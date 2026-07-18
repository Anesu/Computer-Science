#!/usr/bin/env python3
"""Scaffold Phase 2 course specs: one OKF bundle per course.

Generates curriculum/courses/<ID>.md from pathway.yaml + registry.yaml with
everything derivable from the data — semester, credits, track, knowledge
areas, prerequisites, unlocks, reading list, and a /teach mission template.
Unit outlines are scaffolded for Phase 2 authoring.

Scaffold-once: existing files are never overwritten, so authored edits are
safe. Delete a file and rerun to regenerate it.

Usage:
  python3 scripts/scaffold_courses.py
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATHWAY = ROOT / "curriculum" / "pathway.yaml"
REGISTRY = ROOT / "resources" / "registry.yaml"
OUT = ROOT / "curriculum" / "courses"

SCAFFOLD_DATE = "2026-07-19"

TRACK_LABEL = {
    "core": "Core", "ai": "AI track", "systems": "Systems track",
    "security": "Security track", "elective": "Elective",
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def course_doc(c, courses, ka_names, readings, unlocks) -> str:
    cid = c["id"]
    prereqs = c.get("prerequisites", [])
    kas = c.get("knowledge_areas", [])
    sources = [r["id"] for r in readings]

    fm = ["---"]
    fm.append(f"id: {cid}")
    fm.append(f'title: "{c["title"]}"')
    fm.append(f'semester: {c["semester"]}')
    fm.append(f'credits: {c["credits"]}')
    fm.append(f'track: {c["track"]}')
    fm.append(f"knowledge_areas: [{', '.join(kas)}]")
    fm.append(f"prerequisites: [{', '.join(prereqs)}]")
    fm.append("churn: stable")
    fm.append(f"last_verified: {SCAFFOLD_DATE}")
    fm.append(f"sources: [{', '.join(sources)}]")
    fm.append("---")

    lines = fm + [""]
    lines.append(f'# {cid} — {c["title"]}')
    lines.append("")
    lines.append(f'Semester {c["semester"]} · {TRACK_LABEL[c["track"]]} · '
                 f'{c["credits"]} credits')
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    ka_list = ", ".join(f"{k} ({ka_names[k]})" for k in kas)
    lines.append(f"Covers CS2023 knowledge areas: {ka_list}.")
    lines.append("")
    lines.append("<!-- PHASE-2 AUTHORING: replace this scaffold overview with "
                 "2-3 paragraphs on what the course is about and why it sits "
                 "here in the pathway. -->")
    lines.append("")

    lines.append("## Prerequisites")
    lines.append("")
    if prereqs:
        for p in prereqs:
            lines.append(f'- [{p} — {courses[p]["title"]}]({p}.md)')
    else:
        lines.append("None — this course starts the pathway.")
    lines.append("")

    lines.append("## Unlocks")
    lines.append("")
    if unlocks:
        for u in unlocks:
            lines.append(f'- [{u} — {courses[u]["title"]}]({u}.md)')
    else:
        lines.append("Terminal course — nothing depends on it.")
    lines.append("")

    lines.append("## Units")
    lines.append("")
    lines.append("<!-- PHASE-2 AUTHORING: define 6-9 units, each mapping to "
                 "concept documents (Phase 3) under curriculum/" + cid + "/. -->")
    lines.append("")
    lines.append("1. _To be specified._")
    lines.append("")

    lines.append("## Reading list")
    lines.append("")
    if readings:
        for r in readings:
            authors = ", ".join(r.get("authors", []))
            lines.append(f'- **{r["title"]}** — {authors} '
                         f'(`{r["id"]}`, status: {r["status"]})')
    else:
        lines.append("_No registry sources assigned yet — add `used_in: "
                     f"[{cid}]` entries to resources/registry.yaml._")
    lines.append("")

    lines.append("## /teach mission")
    lines.append("")
    lines.append("Paste into a Claude Code session with the `/teach` skill:")
    lines.append("")
    lines.append("```text")
    lines.append(f'/teach Teach me {cid} "{c["title"]}" from the Open CS '
                 "Degree (curriculum/courses/" + cid + ".md).")
    if prereqs:
        lines.append(f"Assume I have completed: {', '.join(prereqs)}.")
    if readings:
        lines.append("Primary sources: "
                     + "; ".join(r["title"] for r in readings) + ".")
    lines.append(f"Target knowledge areas: {', '.join(kas)}.")
    lines.append("Work unit by unit. Quiz me before advancing. Record what "
                 "I have mastered so my progress file can be updated.")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = load(PATHWAY)
    courses = {c["id"]: c for c in data["courses"]}
    ka_names = data["knowledge_areas"]
    registry = load(REGISTRY) or []

    readings_by_course: dict[str, list] = {}
    for entry in registry:
        for cid in entry.get("used_in", []):
            readings_by_course.setdefault(cid, []).append(entry)
    unlocks_by_course: dict[str, list] = {}
    for c in courses.values():
        for p in c.get("prerequisites", []):
            unlocks_by_course.setdefault(p, []).append(c["id"])

    OUT.mkdir(parents=True, exist_ok=True)
    created = skipped = 0
    for cid in sorted(courses):
        path = OUT / f"{cid}.md"
        if path.exists():
            skipped += 1
            continue
        doc = course_doc(
            courses[cid], courses, ka_names,
            sorted(readings_by_course.get(cid, []), key=lambda r: r["id"]),
            sorted(unlocks_by_course.get(cid, [])),
        )
        path.write_text(doc, encoding="utf-8", newline="\n")
        created += 1
    print(f"course specs: {created} created, {skipped} existing (untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
