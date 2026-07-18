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
  python3 scripts/validate_pathway.py --mermaid         # print pathway graph doc (planning/04)
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATHWAY = ROOT / "curriculum" / "pathway.yaml"
REGISTRY = ROOT / "resources" / "registry.yaml"
CURRICULUM = ROOT / "curriculum"

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


TRACK_STYLE = {
    "core": "fill:#dbeafe,stroke:#1e40af,color:#1e3a8a",
    "ai": "fill:#fce7f3,stroke:#9d174d,color:#831843",
    "systems": "fill:#dcfce7,stroke:#166534,color:#14532d",
    "security": "fill:#fef3c7,stroke:#92400e,color:#78350f",
    "elective": "fill:#e5e7eb,stroke:#374151,color:#1f2937",
}


def _nid(cid: str) -> str:
    return cid.replace("-", "_")


def mermaid_doc(courses: dict) -> str:
    lines = ["flowchart TD"]
    by_sem: dict[int, list] = {}
    for c in courses.values():
        by_sem.setdefault(c["semester"], []).append(c)
    for s in sorted(by_sem):
        lines.append(f'  subgraph S{s}["Semester {s}"]')
        for c in sorted(by_sem[s], key=lambda x: (x["track"] != "core", x["id"])):
            lines.append(f'    {_nid(c["id"])}["{c["id"]}<br/>{c["title"]}"]:::{c["track"]}')
        lines.append("  end")
    for c in sorted(courses.values(), key=lambda x: x["id"]):
        for p in c.get("prerequisites", []):
            lines.append(f'  {_nid(p)} --> {_nid(c["id"])}')
    for t, style in TRACK_STYLE.items():
        lines.append(f"  classDef {t} {style}")
    graph = "\n".join(lines)

    load = semester_load(courses)
    load_rows = "\n".join(f"| {s} | {cr} |" for s, cr in load.items())
    return f"""# Pathway Graph

<!-- GENERATED FILE — do not edit by hand.
     Regenerate: python3 scripts/validate_pathway.py --mermaid > planning/04-pathway-graph.md
     CI fails if this file is stale relative to curriculum/pathway.yaml. -->

Prerequisite DAG for the full programme, grouped by earliest-availability
semester. An arrow A → B means A is a prerequisite of B. Colors: blue = core,
pink = AI track, green = Systems track, amber = Security track, gray = general
elective.

```mermaid
{graph}
```

## Semester load (core credits)

Track-elective slots (3 credits each) sit on top of semesters 6–8; free
elective in semester 8.

| Semester | Core credits |
|---|---|
{load_rows}
"""


def main() -> int:
    if "--mermaid" in sys.argv:
        courses = {c["id"]: c for c in load_yaml(PATHWAY)["courses"]}
        sys.stdout.write(mermaid_doc(courses))
        return 0
    print("Validating pathway...")
    courses = check_courses(load_yaml(PATHWAY))
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
