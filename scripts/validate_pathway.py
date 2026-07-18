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
  python3 scripts/validate_pathway.py             # validate everything
  python3 scripts/validate_pathway.py --outreach  # print the license outreach queue
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
    "open", "purchase_only", "purchased",
    "approval_needed", "approval_requested", "licensed", "declined",
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
    return courses


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


def outreach(registry: dict) -> None:
    prio = {"high": 0, "medium": 1, "low": 2}
    queue = sorted(
        (e for e in registry.values()
         if e.get("status") in ("approval_needed", "approval_requested")),
        key=lambda e: (prio.get(e.get("priority", "low"), 3), e["id"]),
    )
    if not queue:
        print("Outreach queue is empty.")
        return
    print(f"License outreach queue ({len(queue)} entries):\n")
    for e in queue:
        print(f"  [{e.get('priority', '?'):<6}] {e['status']:<19} {e['title']}")
        print(f"           by {', '.join(e.get('authors', []))} — {e.get('publisher', 'n/a')}")
        print(f"           contact: {e.get('contact') or 'TBD'}   since: {e.get('status_date', '?')}\n")


def main() -> int:
    if "--outreach" in sys.argv:
        outreach(check_registry())
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
