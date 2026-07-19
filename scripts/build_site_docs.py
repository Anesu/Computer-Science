#!/usr/bin/env python3
"""Generate the Blume site's data-derived pages from the curriculum.

curriculum/ holds OKF documents (strict frontmatter contract of its own);
Blume validates page frontmatter strictly and rejects OKF keys, so this
transform generates Blume-safe .mdx pages plus the pathway SVG and the
dashboard's data module. Deterministic: CI regenerates and diffs.

Outputs (all overwritten wholesale):
  site/docs/courses/<ID>.mdx     one page per course (from curriculum/courses)
  site/docs/courses/index.mdx    catalog grouped by semester
  site/docs/tracks/<track>.mdx   track overviews (ai, systems, security)
  site/docs/library.mdx          source registry with license status
  site/docs/pathway.mdx          interactive map page (PathwayMap island)
  site/docs/dashboard.mdx        progress dashboard page (Dashboard island)
  site/public/pathway.svg        DAG map (ids + classes for progress tinting)
  site/lib/pathway-data.json     course data for the islands

Curriculum markdown is treated as CommonMark: outside code fences the
transform strips authoring comments and escapes MDX-active characters, so
authored OKF documents cannot break the site build. Blume components belong
in hand-authored site pages, not curriculum sources.

Usage:  python3 scripts/build_site_docs.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

from validate_pathway import (
    BOX_H, BOX_W, COLS, FRAME_GAP, FRAME_W, GAP_X, GAP_Y, PAD_TOP, PAD_X,
    FRONTMATTER_RE, _order_courses,
)

ROOT = Path(__file__).resolve().parent.parent
PATHWAY = ROOT / "curriculum" / "pathway.yaml"
REGISTRY = ROOT / "resources" / "registry.yaml"
COURSES_SRC = ROOT / "curriculum" / "courses"
DOCS = ROOT / "site" / "docs"
PUBLIC = ROOT / "site" / "public"
LIB = ROOT / "site" / "lib"

TRACK_LABEL = {
    "core": "Core", "ai": "AI track", "systems": "Systems track",
    "security": "Security track", "elective": "Elective",
}
TRACK_FILL = {
    "core": ("#dbeafe", "#1e40af"),
    "ai": ("#fce7f3", "#9d174d"),
    "systems": ("#dcfce7", "#166534"),
    "security": ("#fef3c7", "#92400e"),
    "elective": ("#e5e7eb", "#374151"),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


# ── markdown → MDX ─────────────────────────────────────────────────────────

def _route_slug(path: str) -> str:
    # Blume drops NN- ordering prefixes from route slugs.
    return "/".join(re.sub(r"^\d+-", "", part) for part in path.split("/"))


def md_to_mdx_body(body: str, cid: str = "", kind: str = "course") -> str:
    """Transform CommonMark to MDX-safe text, leaving code fences alone.

    Link rewriting is layout-aware (curriculum/courses/<ID>/ bundles):
      (../<ID>/course.md)   -> /courses/<ID>/          (sibling course)
      (units/<doc>.md)      -> /courses/<cid>/<slug>/  (own concept, from course.md)
      (../course.md)        -> /courses/<cid>/         (own course, from a concept doc)
      (<doc>.md)            -> /courses/<cid>/<slug>/  (sibling concept, concept docs only)
    """
    out, in_fence = [], False
    buf: list[str] = []

    def flush():
        seg = "\n".join(buf)
        seg = re.sub(r"<!--.*?-->", "", seg, flags=re.DOTALL)
        seg = seg.replace("{", "\\{").replace("}", "\\}")
        seg = re.sub(r"<(?=[A-Za-z/!])", "\\<", seg)
        seg = re.sub(r"\(\.\./([A-Za-z][\w-]*)/course\.md\)",
                     r"(/courses/\1/)", seg)
        seg = re.sub(r"\(\.\./course\.md\)", f"(/courses/{cid}/)", seg)
        seg = re.sub(r"\(units/([\w./-]+)\.md\)",
                     lambda m: f"(/courses/{cid}/{_route_slug(m.group(1))}/)",
                     seg)
        if kind == "concept":
            seg = re.sub(r"\((?!\.\.|/|https?:)([\w./-]+)\.md\)",
                         lambda m: f"(/courses/{cid}/{_route_slug(m.group(1))}/)",
                         seg)
        seg = re.sub(r"\n{3,}", "\n\n", seg)
        out.append(seg)
        buf.clear()

    for line in body.split("\n"):
        if line.strip().startswith("```"):
            if in_fence:
                buf.append(line)
                out.append("\n".join(buf))
                buf.clear()
            else:
                flush()
                buf.append(line)
            in_fence = not in_fence
        else:
            buf.append(line)
    if buf:
        (out.append("\n".join(buf)) if in_fence else flush())
    return "\n".join(out).strip() + "\n"


POINTER_SECTION_RE = re.compile(
    r"\n## Assessment & delivery\n.*?(?=\n## |\Z)", re.DOTALL)
H1_RE = re.compile(r"\A\s*# .*?\n")


def assessment_section(rubric: dict, exam_fm: dict, stub: bool) -> str:
    objectives = rubric.get("objectives", [])
    core = [o for o in objectives if o.get("weight") == "core"]
    supporting = [o for o in objectives if o.get("weight") == "supporting"]
    sm = rubric.get("pass_rule", {}).get("supporting_min", 0)
    lines = [
        "## Assessment",
        "",
        f"{exam_fm.get('format', 'viva').capitalize()} exam "
        f"(`{exam_fm.get('ai_mode', 'closed')}`, "
        f"{exam_fm.get('duration_minutes', '?')} min) conducted by the "
        f"`/examiner` skill against the course rubric: "
        f"**{len(core)} core** objective{'s' if len(core) != 1 else ''} "
        f"(all required) + {len(supporting)} supporting "
        f"(≥{round(sm * 100)}% required). Retake cooldown: "
        f"{exam_fm.get('retake_cooldown_days', '?')} days.",
        "",
    ]
    if stub:
        lines += ["_Assessment bundle still carries Phase-2 stubs — refined "
                  "alongside unit content._", ""]
    lines += ["| Objective | Weight | AI mode |", "|---|---|---|"]
    for o in objectives:
        lines.append(f"| {o.get('statement', '?')} | {o.get('weight', '?')} "
                     f"| `{o.get('ai_mode', '?')}` |")
    lines.append("")
    return "\n".join(lines)


def course_page(cid: str, fm: dict, body: str, bundle: dict) -> str:
    title = f"{cid} — {fm['title']}"
    desc = (f"Semester {fm['semester']} {TRACK_LABEL[fm['track']]} course, "
            f"{fm['credits']} credits.")
    sources = ", ".join(f"`{s}`" for s in fm.get("sources", []) or [])
    prov = (f"**Provenance:** churn `{fm.get('churn', 'stable')}` · "
            f"verified {fm.get('last_verified', '?')}"
            + (f" · sources: {sources}" if sources else ""))
    body = POINTER_SECTION_RE.sub("\n", body)
    project_body = H1_RE.sub("", bundle["project_body"]).strip()
    mission_body = H1_RE.sub("", bundle["mission_body"]).strip()
    lines = [
        "---",
        f"title: {json.dumps(title)}",
        f"description: {json.dumps(desc)}",
        f"lastModified: {fm.get('last_verified', '2026-07-19')}",
        "search:",
        f"  tags: [{fm['track']}, semester-{fm['semester']}]",
        "---",
        "",
        md_to_mdx_body(body, cid),
        assessment_section(bundle["rubric"], bundle["exam_fm"], bundle["stub"]),
        "## Project",
        "",
        md_to_mdx_body(project_body, cid),
        "## /teach mission",
        "",
        md_to_mdx_body(mission_body, cid),
        "---",
        "",
        prov,
        "",
    ]
    return "\n".join(lines)


def concept_page(cid: str, fm: dict, body: str) -> str:
    title = fm.get("title", "Untitled concept")
    sources = ", ".join(f"`{s}`" for s in fm.get("sources", []) or [])
    prov = (f"**Provenance:** churn `{fm.get('churn', 'stable')}` · "
            f"verified {fm.get('last_verified', '?')}"
            + (f" · sources: {sources}" if sources else ""))
    lines = [
        "---",
        f"title: {json.dumps(str(title))}",
        f"description: {json.dumps(f'{cid} concept document.')}",
        f"lastModified: {fm.get('last_verified', '2026-07-19')}",
        "search:",
        f"  tags: [{cid}, concept]",
        "---",
        "",
        md_to_mdx_body(body, cid, kind="concept"),
        "---",
        "",
        f"{prov} · part of [{cid}](/courses/{cid}/)",
        "",
    ]
    return "\n".join(lines)


# ── generated site pages ───────────────────────────────────────────────────

def catalog_page(courses: dict) -> str:
    by_sem: dict[int, list] = {}
    for c in courses.values():
        by_sem.setdefault(c["semester"], []).append(c)
    lines = [
        "---",
        'title: "Course Catalog"',
        'description: "All 45 courses, grouped by earliest-availability semester."',
        "---",
        "",
        "# Course catalog",
        "",
        "Grouped by earliest availability. See the [pathway map](/pathway/) for",
        "prerequisites and the [dashboard](/dashboard/) for your own frontier.",
        "",
    ]
    for s in sorted(by_sem):
        lines.append(f"## Semester {s}")
        lines.append("")
        lines.append("| Course | Title | Track | Credits |")
        lines.append("|---|---|---|---|")
        for c in sorted(by_sem[s], key=lambda x: (x["track"] != "core", x["id"])):
            lines.append(
                f'| [{c["id"]}](/courses/{c["id"]}/) | {c["title"]} '
                f'| {TRACK_LABEL[c["track"]]} | {c["credits"]} |')
        lines.append("")
    return "\n".join(lines)


def track_page(track: str, courses: dict) -> str:
    tcourses = sorted((c for c in courses.values() if c["track"] == track),
                      key=lambda c: (c["semester"], c["id"]))
    label = TRACK_LABEL[track]
    lines = [
        "---",
        f"title: {json.dumps(label)}",
        f"description: {json.dumps(f'The {label} specialization: {len(tcourses)} courses.')}",
        "---",
        "",
        f"# {label}",
        "",
        f"{len(tcourses)} courses. Track-elective slots sit on top of the core",
        "load in semesters 6–8; see the [catalog](/courses/) for everything.",
        "",
        "| Course | Title | Semester | Credits | Prerequisites |",
        "|---|---|---|---|---|",
    ]
    for c in tcourses:
        prereqs = ", ".join(
            f'[{p}](/courses/{p}/)' for p in c.get("prerequisites", [])) or "—"
        lines.append(
            f'| [{c["id"]}](/courses/{c["id"]}/) | {c["title"]} '
            f'| {c["semester"]} | {c["credits"]} | {prereqs} |')
    lines.append("")
    return "\n".join(lines)


def library_page(registry: list) -> str:
    lines = [
        "---",
        'title: "Library"',
        'description: "Every cited source and its license status — the licensing dashboard."',
        "---",
        "",
        "# Library",
        "",
        "Every source cited anywhere in the curriculum, from",
        "`resources/registry.yaml`. Status meanings: **open** — freely licensed;",
        "**identified** — the programme wants it but it is not yet in the",
        "library; **ingested** — acquired and available locally.",
        "",
        "| Source | Authors | License | Status | Used in |",
        "|---|---|---|---|---|",
    ]
    for e in sorted(registry, key=lambda x: x["id"]):
        authors = ", ".join(e.get("authors", []))
        used = ", ".join(
            f'[{c}](/courses/{c}/)' for c in e.get("used_in", [])) or "—"
        title = (f'[{e["title"]}]({e["url"]})' if e.get("url")
                 else e["title"])
        lines.append(f'| {title} | {authors} | {e.get("license", "?")} '
                     f'| **{e["status"]}** | {used} |')
    lines.append("")
    return "\n".join(lines)


def pathway_page() -> str:
    return "\n".join([
        "---",
        'title: "Pathway Map"',
        'description: "The full prerequisite DAG with your live progress overlaid."',
        "---",
        "",
        "# Pathway map",
        "",
        "The full prerequisite DAG. An arrow A → B means A is a prerequisite",
        "of B. Completion state comes from your [dashboard](/dashboard/)",
        "progress: completed courses are outlined green, available ones amber,",
        "locked ones dimmed. Click a course to open its page.",
        "",
        "<PathwayMap />",
        "",
        "For a hands-on canvas version (click a course to highlight its full",
        "chain), open `planning/pathway.tldraw` in tldraw Desktop.",
        "",
    ])


def dashboard_page() -> str:
    return "\n".join([
        "---",
        'title: "Dashboard"',
        'description: "Your progress: completed courses, the frontier, credits, and coverage."',
        "---",
        "",
        "# Dashboard",
        "",
        "Progress lives in this browser (localStorage) and exports to a",
        "`progress.yaml` you keep in a private repo — see the frontend plan.",
        "Mark courses complete below; the frontier and the",
        "[pathway map](/pathway/) update instantly.",
        "",
        "<Dashboard />",
        "",
    ])


# ── pathway SVG ────────────────────────────────────────────────────────────

def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def wrap_title(title: str, width: int = 26) -> list[str]:
    words, lines, cur = title.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines[:3]


def pathway_svg(courses: dict) -> str:
    by_sem: dict[int, list] = {}
    for c in courses.values():
        by_sem.setdefault(c["semester"], []).append(c)
    ordered = _order_courses(by_sem)

    frames, boxes, centers, frame_top = [], [], {}, {}
    frame_y = 0.0
    for s in sorted(by_sem):
        sem = ordered[s]
        frame_top[s] = frame_y
        rows = (len(sem) + COLS - 1) // COLS
        frame_h = PAD_TOP + rows * BOX_H + (rows - 1) * GAP_Y + 30
        frames.append((s, frame_y, frame_h))
        for i, c in enumerate(sem):
            bx = PAD_X + (i % COLS) * (BOX_W + GAP_X)
            by = frame_y + PAD_TOP + (i // COLS) * (BOX_H + GAP_Y)
            boxes.append((c, bx, by))
            centers[c["id"]] = (bx + BOX_W / 2, by + BOX_H / 2)
        frame_y += frame_h + FRAME_GAP

    parts = []
    for s, fy, fh in frames:
        parts.append(
            f'<rect class="pw-frame" x="0" y="{fy:g}" width="{FRAME_W}" '
            f'height="{fh:g}" rx="10"/>'
            f'<text class="pw-frame-label" x="14" y="{fy + 30:g}">'
            f'Semester {s}</text>')

    for c in sorted(courses.values(), key=lambda x: x["id"]):
        for p in c.get("prerequisites", []):
            (x1, y1), (x2, y2) = centers[p], centers[c["id"]]
            sy, ty = y1 + BOX_H / 2, y2 - BOX_H / 2
            gy = frame_top[c["semester"]] - FRAME_GAP / 2
            d = (f"M {x1:g} {sy:g} V {gy:g} H {x2:g} V {ty:g}"
                 if x1 != x2 else f"M {x1:g} {sy:g} V {ty:g}")
            parts.append(
                f'<path class="pw-edge" data-from="{p}" data-to="{c["id"]}" '
                f'd="{d}" marker-end="url(#pw-arrow)"/>')

    for c, bx, by in boxes:
        fill, stroke = TRACK_FILL[c["track"]]
        tid = esc(c["id"])
        tlines = wrap_title(c["title"])
        text_y = by + 34
        tspans = "".join(
            f'<tspan x="{bx + BOX_W / 2:g}" dy="{16 if i else 22}">{esc(t)}</tspan>'
            for i, t in enumerate(tlines))
        parts.append(
            f'<a href="/courses/{tid}/">'
            f'<g class="pw-course pw-{c["track"]}" id="pw-{tid}" data-course="{tid}">'
            f'<rect x="{bx:g}" y="{by:g}" width="{BOX_W}" height="{BOX_H}" '
            f'rx="8" fill="{fill}" stroke="{stroke}"/>'
            f'<text class="pw-id" x="{bx + BOX_W / 2:g}" y="{text_y:g}">{tid}</text>'
            f'<text class="pw-title" x="{bx + BOX_W / 2:g}" y="{text_y:g}">'
            f'{tspans}</text>'
            f'</g></a>')

    height = frame_y - FRAME_GAP + 20
    style = """
  .pw-frame { fill: rgba(148,163,184,.07); stroke: rgba(148,163,184,.45); }
  .pw-frame-label { font: 600 15px system-ui, sans-serif; fill: #64748b; }
  .pw-edge { fill: none; stroke: #94a3b8; stroke-opacity: .55; stroke-width: 1.6; }
  .pw-course rect { stroke-width: 1.5; }
  .pw-course text { text-anchor: middle; }
  .pw-id { font: 700 14px system-ui, sans-serif; fill: #0f172a; }
  .pw-title { font: 400 12px system-ui, sans-serif; fill: #334155; }
  .pw-done rect { stroke: #16a34a !important; stroke-width: 4 !important; }
  .pw-avail rect { stroke: #d97706 !important; stroke-width: 3.5 !important; stroke-dasharray: 7 4; }
  .pw-locked { opacity: .3; }
"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="-10 -20 {FRAME_W + 20} {height + 30:g}" '
        f'font-family="system-ui, sans-serif">\n'
        f"<style>{style}</style>\n"
        f'<defs><marker id="pw-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker></defs>\n'
        + "\n".join(parts) + "\n</svg>\n")


# ── main ───────────────────────────────────────────────────────────────────

def main() -> int:
    data = load(PATHWAY)
    courses = {c["id"]: c for c in data["courses"]}
    registry = load(REGISTRY) or []

    n = 0
    assessments: dict[str, dict] = {}
    for path in sorted(COURSES_SRC.glob("*/course.md")):
        cdir = path.parent
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            print(f"WARN: {path} has no frontmatter, skipped")
            continue
        fm = yaml.safe_load(m.group(1))
        cid = fm["id"]

        rubric = load(cdir / "rubric.yaml")
        proj_text = (cdir / "project.md").read_text(encoding="utf-8")
        pm = FRONTMATTER_RE.match(proj_text)
        exam_text = (cdir / "exam.md").read_text(encoding="utf-8")
        em = FRONTMATTER_RE.match(exam_text)
        stub = any("TODO" in (cdir / f).read_text(encoding="utf-8")
                   for f in ("rubric.yaml", "exam.md", "project.md"))
        bundle = {
            "rubric": rubric,
            "exam_fm": yaml.safe_load(em.group(1)) if em else {},
            "project_body": proj_text[pm.end():] if pm else proj_text,
            "mission_body": (cdir / "mission.md").read_text(encoding="utf-8"),
            "stub": stub,
        }
        objectives = rubric.get("objectives", [])
        assessments[cid] = {
            "core": sum(1 for o in objectives if o.get("weight") == "core"),
            "supporting": sum(1 for o in objectives
                              if o.get("weight") == "supporting"),
            "aiModes": sorted({o.get("ai_mode") for o in objectives if o.get("ai_mode")}),
            "stub": stub,
        }
        write(DOCS / "courses" / f"{cid}.mdx",
              course_page(cid, fm, text[m.end():], bundle))
        n += 1

    # Phase 3 concept documents: courses/<ID>/units/**/*.md become pages
    # nested under the course (the units/ path segment is dropped, so routes
    # are unchanged from the pre-directory layout).
    nc = 0
    for units in sorted(COURSES_SRC.glob("*/units")):
        cid = units.parent.name
        for path in sorted(units.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            m = FRONTMATTER_RE.match(text)
            if not m:
                print(f"WARN: {path} has no frontmatter, skipped")
                continue
            fm = yaml.safe_load(m.group(1))
            rel = path.relative_to(units).with_suffix("").as_posix()
            write(DOCS / "courses" / cid / f"{rel}.mdx",
                  concept_page(cid, fm, text[m.end():]))
            nc += 1

    write(DOCS / "courses" / "index.mdx", catalog_page(courses))
    for track in ("ai", "systems", "security"):
        write(DOCS / "tracks" / f"{track}.mdx", track_page(track, courses))
    write(DOCS / "library.mdx", library_page(registry))
    write(DOCS / "pathway.mdx", pathway_page())
    write(DOCS / "dashboard.mdx", dashboard_page())
    write(PUBLIC / "pathway.svg", pathway_svg(courses))

    payload = {
        "targetCredits": data["programme"]["target_credits"],
        "kaNames": data["knowledge_areas"],
        "courses": [
            {"id": c["id"], "title": c["title"], "semester": c["semester"],
             "credits": c["credits"], "track": c["track"],
             "kas": c.get("knowledge_areas", []),
             "prereqs": c.get("prerequisites", []),
             "assessment": assessments.get(c["id"])}
            for c in sorted(courses.values(), key=lambda x: x["id"])
        ],
    }
    write(LIB / "pathway-data.json",
          json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(f"site docs: {n} course pages + catalog, 3 tracks, library, "
          f"pathway, dashboard, SVG, data module")
    return 0


if __name__ == "__main__":
    sys.exit(main())
