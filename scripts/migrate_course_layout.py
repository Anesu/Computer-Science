#!/usr/bin/env python3
"""One-shot WP1 migration (planning/07 §2.2): flat course files to directories.

curriculum/courses/<ID>.md            -> curriculum/courses/<ID>/course.md
  '## /teach mission' section         -> curriculum/courses/<ID>/mission.md
  (stubs seeded)                      -> project.md, exam.md, rubric.yaml
curriculum/CS1101/*.md                -> curriculum/courses/CS1101/units/

Sibling links are rewritten for the new layout. Idempotent: skips courses
already in directory form. Kept for the record; not expected to run again.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "curriculum" / "courses"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
MISSION_RE = re.compile(r"\n## /teach mission\n(.*)\Z", re.DOTALL)
UNIT_LINE_RE = re.compile(r"^\d+\.\s+(?:\[([^\]]+)\]\([^)]*\)|([^—\n]+?))\s*(?:—.*)?$")


def slugify(text: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def unit_titles(body: str) -> list[str]:
    m = re.search(r"\n## Units\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if not m:
        return []
    titles = []
    for line in m.group(1).splitlines():
        lm = UNIT_LINE_RE.match(line.strip())
        if not lm:
            continue
        title = (lm.group(1) or lm.group(2) or "").strip().strip("_").strip()
        if title and title.lower() not in ("to be specified.", "to be specified"):
            titles.append(title)
    return titles


def rubric_stub(cid: str, units: list[str]) -> str:
    ns = cid.lower()
    lines = [
        "# Grading rubric — seeded by scripts/migrate_course_layout.py.",
        "# Schema: schemas/rubric.schema.md. Refine before the first /examiner run.",
        f"course: {cid}",
        "objectives:",
    ]
    for i, title in enumerate(units, 1):
        lines += [
            f"  - id: {ns}.u{i:02d}.{slugify(title)}",
            f"    statement: \"TODO: refine — demonstrate mastery of: {title}\"",
            "    evidence:",
            f"      - \"TODO: refine — observable evidence for: {title}\"",
            "    weight: supporting",
            "    ai_mode: open-book",
        ]
    lines += [
        f"  - id: {ns}.project.defense",
        "    statement: Complete the course project and defend it in the viva",
        "    evidence:",
        "      - Project passes every acceptance criterion in project.md",
        "      - Learner explains design decisions and modifies their own code live",
        "    weight: core",
        "    ai_mode: ai-paired",
        "pass_rule:",
        "  core: all",
        "  supporting_min: 0.7",
        "",
    ]
    return "\n".join(lines)


def exam_stub(cid: str, title: str) -> str:
    return f"""---
course: {cid}
type: exam
ai_mode: closed
format: viva
duration_minutes: 45
retake_cooldown_days: 3
---

# {cid} — Exam spec

<!-- TODO: refine — course-specific scope and question style. -->

Closed-book oral exam (viva) for **{title}**, conducted by the `/examiner`
skill against [rubric.yaml](rubric.yaml). Scope: all units in
[course.md](course.md). Question style per objective: recall, then at least
one why/what-if probe, then a transfer question in a novel scenario. Failed
objectives route back to tutoring; retake after the cooling-off period with
fresh questions.
"""


def project_stub(cid: str, title: str) -> str:
    return f"""---
course: {cid}
type: project
ai_mode: ai-paired
---

# {cid} — Course project

<!-- TODO: refine — replace with a real brief when Phase 3 reaches this course. -->

_Project brief for **{title}** to be authored alongside unit content._

## Acceptance criteria

<!-- TODO: refine — each criterion must be a command with an expected outcome. -->

- To be defined: machine-verifiable criteria (test suite, benchmark, or
  checkable artifact) that the `/reviewer` skill runs before reading any code.
"""


def pointer_section() -> str:
    return (
        "## Assessment & delivery\n\n"
        "Assessment lives beside this spec: [rubric.yaml](rubric.yaml)\n"
        "(objectives and pass rule), [exam.md](exam.md) (viva spec), and\n"
        "[project.md](project.md) (project + acceptance criteria). The `/teach`\n"
        "mission is in [mission.md](mission.md). The site renders all of them\n"
        "on this course's page.\n"
    )


def migrate_course(path: Path) -> None:
    cid = path.stem
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    fm = yaml.safe_load(m.group(1))
    body = text[m.end():]

    mm = MISSION_RE.search(body)
    mission_body = mm.group(1).strip() if mm else ""
    body = body[:mm.start()] if mm else body

    # sibling course links: (CS2102.md) -> (../CS2102/course.md)
    body = re.sub(r"\(([A-Z][\w-]*)\.md\)", r"(../\1/course.md)", body)
    # own concept docs: (../CS1101/01-x.md) -> (units/01-x.md)
    body = re.sub(rf"\(\.\./{cid}/([\w./-]+\.md)\)", r"(units/\1)", body)
    body = body.rstrip() + "\n\n" + pointer_section()

    mission_body = mission_body.replace(
        f"curriculum/courses/{cid}.md", f"curriculum/courses/{cid}/course.md")

    cdir = COURSES / cid
    cdir.mkdir()
    (cdir / "course.md").write_text(text[:m.end()] + body, encoding="utf-8")
    (cdir / "mission.md").write_text(
        f"# /teach mission — {cid}\n\n{mission_body}\n", encoding="utf-8")
    (cdir / "rubric.yaml").write_text(
        rubric_stub(cid, unit_titles(body)), encoding="utf-8")
    (cdir / "exam.md").write_text(exam_stub(cid, fm["title"]), encoding="utf-8")
    (cdir / "project.md").write_text(project_stub(cid, fm["title"]), encoding="utf-8")
    path.unlink()
    print(f"  {cid}: migrated")


def migrate_stray_concept_dirs() -> None:
    for cdir in sorted(p for p in (ROOT / "curriculum").iterdir()
                       if p.is_dir() and p.name != "courses"):
        target = COURSES / cdir.name / "units"
        target.mkdir(parents=True, exist_ok=True)
        for f in sorted(cdir.rglob("*.md")):
            text = f.read_text(encoding="utf-8")
            # link to own course page: (CS1101.md) -> (../course.md)
            text = re.sub(rf"\({cdir.name}\.md\)", "(../course.md)", text)
            dest = target / f.relative_to(cdir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            f.unlink()
        for d in sorted(cdir.rglob("*"), reverse=True):
            d.rmdir()
        cdir.rmdir()
        print(f"  {cdir.name}: concept docs -> courses/{cdir.name}/units/")


def main() -> int:
    flat = sorted(COURSES.glob("*.md"))
    if not flat:
        print("nothing to migrate — courses/ already in directory form")
    for path in flat:
        migrate_course(path)
    migrate_stray_concept_dirs()
    print(f"migrated {len(flat)} courses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
