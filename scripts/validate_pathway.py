#!/usr/bin/env python3
"""Validate the curriculum pathway DAG and source registry.

Checks (planning/01-okf-profile.md, "Validation rules"):
  1. all prerequisite IDs resolve
  2. the prerequisite graph is acyclic
  3. a course's prerequisites sit in strictly earlier semesters
  4. every CS2023 knowledge area is claimed by at least one core course
  5. concept-document `sources` resolve to registry IDs (once documents exist)
  6. required fields present, enum values legal
  7. volatile documents unverified for >6 months are flagged (warning only)

Usage:
  python3 scripts/validate_pathway.py                   # validate everything
  python3 scripts/validate_pathway.py --graph           # regenerate planning/pathway.tldr
                                                        # + planning/04-pathway-graph.md
"""

import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATHWAY = ROOT / "curriculum" / "pathway.yaml"
REGISTRY = ROOT / "resources" / "registry.yaml"
CURRICULUM = ROOT / "curriculum"
CANVAS_SCRIPT = ROOT / "planning" / "pathway-canvas-script.js"
TLDRAW_ARCHIVE = ROOT / "planning" / "pathway.tldraw"

TRACKS = {"core", "ai", "systems", "security", "elective"}
STATUSES = {
    "open", "identified", "ingested",
}
CHURN = {"evergreen", "stable", "volatile"}
STALE_AFTER = timedelta(days=183)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


def check_courses(data) -> dict:
    kas = set(data["knowledge_areas"])
    courses = {}
    for c in data["courses"]:
        cid = c.get("id")
        if not cid:
            err(f"course missing id: {c}")
            continue
        if cid in courses:
            err(f"duplicate course id: {cid}")
        courses[cid] = c
        for field in ("title", "semester", "credits", "track", "knowledge_areas", "prerequisites"):
            if field not in c:
                err(f"{cid}: missing field '{field}'")
        if c.get("track") not in TRACKS:
            err(f"{cid}: illegal track '{c.get('track')}'")
        for ka in c.get("knowledge_areas", []):
            if ka not in kas:
                err(f"{cid}: unknown knowledge area '{ka}'")

    for cid, c in courses.items():
        for p in c.get("prerequisites", []):
            if p not in courses:
                err(f"{cid}: dangling prerequisite '{p}'")
            elif courses[p]["semester"] >= c["semester"]:
                err(f"{cid} (sem {c['semester']}): prerequisite {p} "
                    f"is not in an earlier semester (sem {courses[p]['semester']})")

    # cycle check (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {cid: WHITE for cid in courses}

    def dfs(node, stack):
        color[node] = GRAY
        for p in courses[node].get("prerequisites", []):
            if p not in courses:
                continue
            if color[p] == GRAY:
                err(f"prerequisite cycle: {' -> '.join(stack + [node, p])}")
            elif color[p] == WHITE:
                dfs(p, stack + [node])
        color[node] = BLACK

    for cid in courses:
        if color[cid] == WHITE:
            dfs(cid, [])

    covered = {ka for c in courses.values() if c.get("track") == "core"
               for ka in c.get("knowledge_areas", [])}
    for ka in sorted(kas - covered):
        err(f"knowledge area {ka} is not covered by any core course")

    core_credits = sum(c["credits"] for c in courses.values() if c["track"] == "core")
    print(f"  {len(courses)} courses ({sum(1 for c in courses.values() if c['track'] == 'core')} core, "
          f"{core_credits} core credits); {len(covered)}/{len(kas)} KAs covered by core")
    load = semester_load(courses)
    print("  semester load (core credits): "
          + "  ".join(f"S{s}:{cr}" for s, cr in load.items()))
    return courses


def semester_load(courses: dict) -> dict:
    load: dict[int, int] = {}
    for c in courses.values():
        if c.get("track") == "core":
            load[c["semester"]] = load.get(c["semester"], 0) + c["credits"]
    return dict(sorted(load.items()))


def check_registry() -> dict:
    if not REGISTRY.exists():
        warn(f"registry not found at {REGISTRY}")
        return {}
    entries = load_yaml(REGISTRY) or []
    registry = {}
    for e in entries:
        rid = e.get("id")
        if not rid:
            err(f"registry entry missing id: {e.get('title')}")
            continue
        if rid in registry:
            err(f"duplicate registry id: {rid}")
        registry[rid] = e
        if e.get("status") not in STATUSES:
            err(f"registry '{rid}': illegal status '{e.get('status')}'")
        for field in ("title", "authors", "license", "status"):
            if not e.get(field):
                err(f"registry '{rid}': missing field '{field}'")
    print(f"  {len(registry)} registry entries")
    return registry


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def check_documents(courses: dict, registry: dict) -> None:
    docs = [p for p in CURRICULUM.rglob("*.md")]
    today = date.today()
    n = 0
    for path in docs:
        m = FRONTMATTER_RE.match(path.read_text())
        if not m:
            warn(f"{path.relative_to(ROOT)}: no frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            err(f"{path.relative_to(ROOT)}: bad frontmatter YAML: {e}")
            continue
        n += 1
        rel = path.relative_to(ROOT)
        if fm.get("churn") and fm["churn"] not in CHURN:
            err(f"{rel}: illegal churn '{fm['churn']}'")
        for src in fm.get("sources", []) or []:
            if src not in registry:
                err(f"{rel}: unknown source id '{src}'")
        for p in fm.get("prerequisites", []) or []:
            if p not in courses and "." not in p:
                err(f"{rel}: dangling prerequisite '{p}'")
        lv = fm.get("last_verified")
        if fm.get("churn") == "volatile" and lv and (today - lv) > STALE_AFTER:
            warn(f"{rel}: volatile document last verified {lv} — refresh due")
    print(f"  {n} curriculum documents checked")


# ---------------------------------------------------------------------------
# Pathway graph generation (tldraw canvas + companion markdown)
#
# Emits a .tldr file (tldraw Desktop's native format): one frame per semester,
# one track-colored box per course, and a bound arrow per prerequisite edge.
# The schema blob below was captured verbatim from tldraw Desktop's own
# editor.store.schema.serialize() so the app migrates/loads the file cleanly.
# ---------------------------------------------------------------------------

TLDRAW_SCHEMA = {
    "schemaVersion": 2,
    "sequences": {
        "com.tldraw.store": 5, "com.tldraw.asset": 1, "com.tldraw.camera": 1,
        "com.tldraw.document": 2, "com.tldraw.instance": 26,
        "com.tldraw.instance_page_state": 5, "com.tldraw.page": 1,
        "com.tldraw.instance_presence": 6, "com.tldraw.pointer": 1,
        "com.tldraw.shape": 4, "com.tldraw.user": 1,
        "com.tldraw.asset.image": 6, "com.tldraw.asset.video": 5,
        "com.tldraw.asset.bookmark": 2, "com.tldraw.shape.group": 0,
        "com.tldraw.shape.text": 4, "com.tldraw.shape.bookmark": 2,
        "com.tldraw.shape.draw": 5, "com.tldraw.shape.geo": 11,
        "com.tldraw.shape.note": 13, "com.tldraw.shape.line": 5,
        "com.tldraw.shape.frame": 1, "com.tldraw.shape.arrow": 8,
        "com.tldraw.shape.highlight": 4, "com.tldraw.shape.embed": 4,
        "com.tldraw.shape.image": 5, "com.tldraw.shape.video": 4,
        "com.tldraw.binding.arrow": 1,
    },
}

TRACK_COLOR = {
    "core": "blue",
    "ai": "light-red",
    "systems": "light-green",
    "security": "yellow",
    "elective": "grey",
}
TRACK_LABEL = {
    "core": "Core", "ai": "AI track", "systems": "Systems track",
    "security": "Security track", "elective": "Elective",
}

BOX_W, BOX_H = 200, 100
GAP_X, GAP_Y = 40, 36
PAD_X, PAD_TOP, PAD_BOT = 30, 60, 30
COLS = 7
FRAME_W = COLS * BOX_W + (COLS - 1) * GAP_X + 2 * PAD_X
FRAME_GAP = 150

# Fractional-index digits (base62 minus '0'; a trailing '0' is illegal).
_IDX_DIGITS = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def frac_indices(n: int) -> list[str]:
    """First n keys of a deterministic, ordered, valid fractional-index chain."""
    out: list[str] = []
    prefix = "a"
    while len(out) < n:
        for d in _IDX_DIGITS:
            out.append(prefix + d)
            if len(out) == n:
                return out
        prefix += "z"
    return out


def _rich_text(*lines: str) -> dict:
    return {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": ln}]}
        for ln in lines
    ]}


def _shape(sid, stype, parent, index, x, y, props, opacity=1):
    # isLocked keeps the generated diagram read-only in the editor: clicks
    # can't select, drag, or text-edit, but the highlight script still sees
    # pointer events (it hit-tests coordinates and writes with ignoreShapeLock).
    return {
        "x": x, "y": y, "rotation": 0, "isLocked": True, "opacity": opacity,
        "meta": {}, "id": sid, "type": stype, "props": props,
        "parentId": parent, "index": index, "typeName": "shape",
    }


def _order_courses(by_sem: dict[int, list]) -> dict[int, list]:
    """Order courses within each semester to minimize arrow crossings.

    Sugiyama-style barycenter sweeps: repeatedly place each course near the
    mean column of its prerequisites (downward pass) and of its dependents
    (upward pass). Stable sorts + id tiebreaks keep the result deterministic.
    """
    order = {s: sorted(cs, key=lambda x: (x["track"] != "core", x["id"]))
             for s, cs in by_sem.items()}
    sems = sorted(order)
    deps: dict[str, list[str]] = {}
    for s in sems:
        for c in order[s]:
            for p in c.get("prerequisites", []):
                deps.setdefault(p, []).append(c["id"])

    def columns():
        return {c["id"]: i % COLS for s in sems for i, c in enumerate(order[s])}

    for _ in range(4):
        pos = columns()
        for s in sems[1:]:
            def down(ic):
                i, c = ic
                ps = [pos[p] for p in c.get("prerequisites", []) if p in pos]
                return (sum(ps) / len(ps) if ps else float(i % COLS), c["id"])
            order[s] = [c for _, c in sorted(enumerate(order[s]), key=down)]
        pos = columns()
        for s in reversed(sems[:-1]):
            def up(ic):
                i, c = ic
                ds = [pos[d] for d in deps.get(c["id"], []) if d in pos]
                return (sum(ds) / len(ds) if ds else float(i % COLS), c["id"])
            order[s] = [c for _, c in sorted(enumerate(order[s]), key=up)]
    return order


def tldr_doc(courses: dict) -> dict:
    by_sem: dict[int, list] = {}
    for c in courses.values():
        by_sem.setdefault(c["semester"], []).append(c)

    frames, boxes, arrows, bindings = [], [], [], []
    centers: dict[str, tuple[float, float]] = {}

    # Legend row above the first frame.
    for i, t in enumerate(TRACK_COLOR):
        boxes.append(_shape(
            f"shape:legend-{t}", "geo", "page:page", None,
            i * (150 + 20), -120,
            {"w": 150, "h": 50, "geo": "rectangle", "dash": "draw", "growY": 0,
             "url": "", "scale": 1, "color": TRACK_COLOR[t],
             "labelColor": "black", "fill": "semi", "size": "s", "font": "draw",
             "align": "middle", "verticalAlign": "middle",
             "richText": _rich_text(TRACK_LABEL[t])}))

    ordered = _order_courses(by_sem)
    frame_top: dict[int, float] = {}
    frame_y = 0.0
    for s in sorted(by_sem):
        sem = ordered[s]
        frame_top[s] = frame_y
        rows = (len(sem) + COLS - 1) // COLS
        frame_h = PAD_TOP + rows * BOX_H + (rows - 1) * GAP_Y + PAD_BOT
        fid = f"shape:S{s}"
        frames.append(_shape(
            fid, "frame", "page:page", None, 0, frame_y,
            {"w": FRAME_W, "h": frame_h, "name": f"Semester {s}", "color": "black"}))
        child_idx = frac_indices(len(sem))
        for i, c in enumerate(sem):
            bx = PAD_X + (i % COLS) * (BOX_W + GAP_X)
            by = PAD_TOP + (i // COLS) * (BOX_H + GAP_Y)
            boxes.append(_shape(
                f'shape:{c["id"]}', "geo", fid, child_idx[i], bx, by,
                {"w": BOX_W, "h": BOX_H, "geo": "rectangle", "dash": "draw",
                 "growY": 0, "url": "", "scale": 1,
                 "color": TRACK_COLOR[c["track"]], "labelColor": "black",
                 "fill": "semi", "size": "s", "font": "draw", "align": "middle",
                 "verticalAlign": "middle",
                 "richText": _rich_text(c["id"], c["title"])}))
            centers[c["id"]] = (bx + BOX_W / 2, frame_y + by + BOX_H / 2)
        frame_y += frame_h + FRAME_GAP

    for c in sorted(courses.values(), key=lambda x: x["id"]):
        for p in c.get("prerequisites", []):
            aid = f'shape:arrow-{p}-{c["id"]}'
            (cx1, cy1), (cx2, cy2) = centers[p], centers[c["id"]]
            # leave the prerequisite's bottom edge, enter the dependent's top
            x1, y1 = cx1, cy1 + BOX_H / 2
            x2, y2 = cx2, cy2 - BOX_H / 2
            # bend in the gutter just above the destination semester, so the
            # horizontal segment never cuts through a frame
            gutter_y = frame_top[c["semester"]] - FRAME_GAP / 2
            mid = max(0.05, min(0.95, (gutter_y - y1) / (y2 - y1)))
            arrows.append(_shape(
                aid, "arrow", "page:page", None, x1, y1,
                {"kind": "elbow", "elbowMidPoint": round(mid, 4), "dash": "draw",
                 "size": "s", "fill": "none", "color": "grey",
                 "labelColor": "black", "bend": 0,
                 "start": {"x": 0, "y": 0}, "end": {"x": x2 - x1, "y": y2 - y1},
                 "arrowheadStart": "none", "arrowheadEnd": "arrow",
                 "richText": {"type": "doc", "content": [{"type": "paragraph"}]},
                 "labelPosition": 0.5, "font": "draw", "scale": 1},
                opacity=0.6))
            anchors = {"start": (f"shape:{p}", {"x": 0.5, "y": 1}),
                       "end": (f'shape:{c["id"]}', {"x": 0.5, "y": 0})}
            for term, (target, anchor) in anchors.items():
                bindings.append({
                    "meta": {}, "id": f"binding:{aid[6:]}-{term}", "fromId": aid,
                    "toId": target, "type": "arrow",
                    "props": {"isPrecise": True, "isExact": False,
                              "normalizedAnchor": anchor,
                              "snap": "none", "terminal": term},
                    "typeName": "binding"})

    # Page-level siblings (legend + frames + arrows) share one index chain.
    page_children = [b for b in boxes if b["parentId"] == "page:page"] + frames + arrows
    for idx, rec in zip(frac_indices(len(page_children)), page_children):
        rec["index"] = idx

    records = [
        {"gridSize": 10, "name": "", "meta": {},
         "id": "document:document", "typeName": "document"},
        {"meta": {}, "id": "page:page", "name": "Pathway",
         "index": "a1", "typeName": "page"},
        *frames, *boxes, *arrows, *bindings,
    ]
    return {"tldrawFileFormatVersion": 1, "schema": TLDRAW_SCHEMA,
            "records": records}


def graph_md(courses: dict) -> str:
    load = semester_load(courses)
    load_rows = "\n".join(f"| {s} | {cr} |" for s, cr in load.items())
    return f"""# Pathway Graph

<!-- GENERATED FILE — do not edit by hand.
     Regenerate: python3 scripts/validate_pathway.py --graph
     CI fails if this file is stale relative to curriculum/pathway.yaml. -->

The prerequisite DAG is rendered as a tldraw canvas. Open
**[`pathway.tldraw`](pathway.tldraw)** with tldraw Desktop — it embeds
[`pathway-canvas-script.js`](pathway-canvas-script.js), so the canvas is
interactive out of the box: click any course to highlight its full
prerequisite ancestry plus everything it unlocks; click empty canvas to
reset. ([`pathway.tldr`](pathway.tldr) is the same canvas as flat portable
JSON, without the script — it also loads on tldraw.com.)

One frame per earliest-availability semester; an arrow A → B means A is a
prerequisite of B. Colors: blue = core, pink = AI track, green = Systems
track, yellow = Security track, gray = general elective.

Everything is generated from `curriculum/pathway.yaml` — edit the YAML, then
regenerate; freehand edits to the canvas will be overwritten.

## Semester load (core credits)

Track-elective slots (3 credits each) sit on top of semesters 6–8; free
elective in semester 8.

| Semester | Core credits |
|---|---|
{load_rows}
"""


# The .tldraw desktop archive: a stored zip of db.sqlite (one JSON blob per
# record), metadata.json, the embedded document script, and session.json.
# Unlike the flat .tldr, this format carries the click-to-highlight script,
# so the canvas is interactive the moment it is opened.

def _sqlite_bytes(records: list[dict]) -> bytes:
    fd, tmp = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    os.unlink(tmp)
    con = sqlite3.connect(tmp)
    con.executescript("""
        CREATE TABLE documents (id TEXT PRIMARY KEY, state BLOB NOT NULL,
                                lastChangedClock INTEGER NOT NULL);
        CREATE INDEX idx_documents_lastChangedClock ON documents(lastChangedClock);
        CREATE TABLE tombstones (id TEXT PRIMARY KEY, clock INTEGER NOT NULL);
        CREATE INDEX idx_tombstones_clock ON tombstones(clock);
        CREATE TABLE metadata (migrationVersion INTEGER NOT NULL,
                               documentClock INTEGER NOT NULL,
                               tombstoneHistoryStartsAtClock INTEGER NOT NULL,
                               schema TEXT NOT NULL);
    """)
    for r in records:
        con.execute("INSERT INTO documents VALUES (?,?,?)",
                    (r["id"], json.dumps(r, separators=(",", ":")).encode(), 1))
    con.execute("INSERT INTO metadata VALUES (?,?,?,?)",
                (2, 1, 0, json.dumps(TLDRAW_SCHEMA, separators=(",", ":"))))
    con.commit()
    con.close()
    data = Path(tmp).read_bytes()
    os.unlink(tmp)
    return data


def write_tldraw_archive(records: list[dict]) -> None:
    script = CANVAS_SCRIPT.read_bytes()
    meta = {
        "formatVersion": 1,
        "displayName": "Pathway",
        "createdWith": "tldraw-desktop (legacy import)",
        "documentClock": 1,
        "script": {"sha256": hashlib.sha256(script).hexdigest(), "author": "agent"},
    }
    session = {
        "version": 0, "currentPageId": "page:page", "exportBackground": True,
        "isFocusMode": False, "isDebugMode": False, "isToolLocked": False,
        "isGridMode": False,
        "pageStates": [{"pageId": "page:page", "camera": {"x": 100, "y": 500, "z": 1},
                        "selectedShapeIds": [], "focusedGroupId": None}],
    }
    epoch = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(TLDRAW_ARCHIVE, "w", zipfile.ZIP_STORED) as z:
        for name, data in (
            ("db.sqlite", _sqlite_bytes(records)),
            ("metadata.json", json.dumps(meta, indent="\t").encode()),
            ("script/main.js", script),
            ("session.json", json.dumps(session, separators=(",", ":")).encode()),
        ):
            z.writestr(zipfile.ZipInfo(name, date_time=epoch), data)
        z.writestr(zipfile.ZipInfo("assets/", date_time=epoch), b"")


def check_canvas_archive(courses: dict) -> None:
    """Semantic staleness check for pathway.tldraw.

    SQLite bytes differ across library versions, so CI cannot diff the archive
    byte-for-byte like the .tldr; instead compare the extracted records and
    embedded script against what the current pathway.yaml generates.
    """
    if not TLDRAW_ARCHIVE.exists():
        err("planning/pathway.tldraw missing — run scripts/validate_pathway.py --graph")
        return
    if not CANVAS_SCRIPT.exists():
        err("planning/pathway-canvas-script.js missing")
        return
    expected = {r["id"]: r for r in tldr_doc(courses)["records"]}
    with zipfile.ZipFile(TLDRAW_ARCHIVE) as z:
        script = z.read("script/main.js")
        if script != CANVAS_SCRIPT.read_bytes():
            err("pathway.tldraw: embedded script differs from "
                "planning/pathway-canvas-script.js — rerun --graph")
        meta = json.loads(z.read("metadata.json"))
        if meta.get("script", {}).get("sha256") != hashlib.sha256(script).hexdigest():
            err("pathway.tldraw: metadata script sha256 mismatch — rerun --graph")
        fd, tmp = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        Path(tmp).write_bytes(z.read("db.sqlite"))
    con = sqlite3.connect(tmp)
    got = {rid: json.loads(state) for rid, state
           in con.execute("SELECT id, state FROM documents")
           if rid.split(":")[0] in ("document", "page", "shape", "binding")}
    con.close()
    os.unlink(tmp)
    if got != expected:
        stale = [rid for rid in expected if got.get(rid) != expected.get(rid)]
        extra = [rid for rid in got if rid not in expected]
        err(f"pathway.tldraw is stale relative to pathway.yaml "
            f"({len(stale)} changed/missing, {len(extra)} extra records) — rerun --graph")
    print(f"  pathway.tldraw: {len(got)} records match pathway.yaml; script embedded")


def main() -> int:
    if "--graph" in sys.argv:
        courses = {c["id"]: c for c in load_yaml(PATHWAY)["courses"]}
        doc = tldr_doc(courses)
        tldr_path = ROOT / "planning" / "pathway.tldr"
        md_path = ROOT / "planning" / "04-pathway-graph.md"
        with open(tldr_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")
        with open(md_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(graph_md(courses))
        write_tldraw_archive(doc["records"])
        print(f"wrote {tldr_path.relative_to(ROOT)}, "
              f"{TLDRAW_ARCHIVE.relative_to(ROOT)}, and {md_path.relative_to(ROOT)}")
        return 0
    print("Validating pathway...")
    courses = check_courses(load_yaml(PATHWAY))
    print("Validating canvas archive...")
    check_canvas_archive(courses)
    print("Validating registry...")
    registry = check_registry()
    print("Validating curriculum documents...")
    check_documents(courses, registry)
    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"\nOK: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
