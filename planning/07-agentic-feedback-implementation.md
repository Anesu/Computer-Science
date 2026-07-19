# Agentic Feedback System — Implementation Plan

**Date:** 2026-07-18
**Status:** Proposed. Implements `planning/06-agentic-feedback-system.md`.
Work packages WP1–WP6 map to sequencing items A1–A3, B1–B2, C in that document.

Every work package ends with a committed gate artifact and a green
`python3 scripts/validate_pathway.py` run; CI (`.github/workflows/validate.yml`)
already executes the validator on every push touching `curriculum/`,
`resources/`, or `scripts/`, so new validation rules become enforcement the
moment they land.

## 0. Current state (what the code actually does today)

Facts the implementation must respect — verified against the working tree:

- **Course layout is flat**: `curriculum/courses/<ID>.md`, one file per course,
  with the `/teach` mission embedded as a fenced block inside the spec. The
  pilot concept doc lives at `curriculum/CS1101/01-values-types-expressions.md`
  — *outside* `courses/`, deviating from the OKF profile's planned
  `courses/<id>/units/` layout. WP1 reconciles this.
- **`scripts/validate_pathway.py` (572 lines)** — `check_courses()` (DAG,
  semesters, KA coverage), `check_registry()`, `check_documents()` (frontmatter
  of every `curriculum/**/*.md`: churn enum, source refs, prereq refs, staleness),
  plus canvas generation/staleness checks. `check_documents()` is permissive:
  most fields optional.
- **`scripts/build_site_docs.py` (459 lines)** — transforms
  `curriculum/courses/*.md` and `curriculum/<COURSE>/*.md` into
  `site/docs/**/*.mdx`, `site/public/pathway.svg`, `site/lib/pathway-data.json`.
  It rewrites relative links with regexes keyed to the *current* layout
  (`(CS1201.md)` → `/courses/CS1201/`; `(../CS1101/01-x.md)` → concept route)
  and imports layout constants from `validate_pathway`. Any file move must
  update these rewrites in the same commit.
- **`scripts/scaffold_courses.py`** — scaffold-once generator; will not be
  rerun. Migration needs its own one-shot script.
- **`site/islands/Dashboard.tsx`** — progress in localStorage, imports/exports
  `progress.yaml`, computes the frontier from `site/lib/pathway-data.json`.
- **Skills**: none in-repo. `/teach` is external (mattpocock/skills).

## 1. Target repository layout (end state after WP1–WP6)

```
curriculum/courses/<ID>/
  course.md                # spec (moved from courses/<ID>.md; frontmatter unchanged + assessment refs)
  mission.md               # /teach mission (extracted from course.md)
  project.md               # brief + acceptance criteria (frontmatter: ai_mode)
  rubric.yaml              # objectives + evidence + pass_rule (schema §2.1)
  exam.md                  # viva spec (frontmatter: ai_mode, format, retake policy)
  units/<nn>-<slug>.md     # Phase 3 concept docs (CS1101 pilot moves here)
.claude/skills/
  examiner/SKILL.md        # summative viva agent (protocol from 06 §2.2)
  reviewer/SKILL.md        # project review agent
  review/SKILL.md          # spaced-retrieval session agent
  retro/SKILL.md           # weekly retro agent (WP6)
schemas/
  rubric.schema.md         # documented contract (validator is the enforcement)
  learning-record.md       # record v2 schema + examiner-report format
templates/
  progress.yaml            # empty record v2 for the learner's private repo
  examiner-report.md       # report skeleton the examiner skill fills in
scripts/
  migrate_course_layout.py # one-shot WP1 migration (kept, marked run-once)
  validate_pathway.py      # extended (rules §2.4)
  build_site_docs.py       # updated paths/links; emits assessment data to site
```

---

## 2. WP1 — Course directories + assessment schemas + validator (06 §2.1, A1)

The structural foundation; everything else lands on top of it. One PR-sized
change, sequenced so the tree is never half-migrated.

### 2.1 Schema contracts (write first: `schemas/rubric.schema.md`)

`rubric.yaml` (per course):

```yaml
course: CS2201                  # must equal directory name
objectives:
  - id: os.proc.lifecycle       # dot-namespaced, globally unique across all rubrics
    statement: <observable capability>
    evidence: [<what the examiner must see>, ...]   # >=1, phrased observably
    weight: core                # core | supporting
    ai_mode: closed             # closed | open-book | ai-paired (per 06 §2.4)
pass_rule:
  core: all                    # fixed in v1: all core objectives evidenced
  supporting_min: 0.7          # fraction of supporting objectives required
```

`exam.md` frontmatter: `{course, type: exam, ai_mode, format: viva,
duration_minutes, retake_cooldown_days: 3}`; body describes scope and question
style. `project.md` frontmatter: `{course, type: project, ai_mode}`; body must
contain an `## Acceptance criteria` section whose items are commands/outcomes.

### 2.2 One-shot migration (`scripts/migrate_course_layout.py`)

For each `curriculum/courses/<ID>.md`:
1. `git mv curriculum/courses/<ID>.md curriculum/courses/<ID>/course.md`.
2. Extract the `## /teach mission` section into `mission.md`; leave a link.
3. Emit stub `project.md`, `exam.md`, and `rubric.yaml` — objectives seeded
   from the course's unit list (one supporting objective per unit, statements
   copied from unit titles, marked `# TODO: refine`), so the tree validates
   immediately and refinement is authoring work, not schema work.
4. `git mv curriculum/CS1101 curriculum/courses/CS1101/units` (pilot doc
   joins the profile layout).

Windows/macOS case-collision note: the earlier `CS1101.mdx` case-only rename
bit us once (commit `1b80d9d`); all moves here change path *shape* not case,
so `git mv` is sufficient.

### 2.3 Same-commit updates in `build_site_docs.py`

- Source globs: `courses/*.md` → `courses/*/course.md`; concept docs from
  `courses/<ID>/units/*.md`.
- Link rewrites: `(CS1201.md)` links inside specs become
  `(../CS1201/course.md)` after migration — the migration script rewrites the
  markdown, and the transform's regexes are updated to map the new relative
  forms to the same site routes as today (`/courses/<ID>/`, concept routes).
  Site route structure does **not** change, so no redirects needed.
- New output: fold `{objectives, ai_modes, has_rubric}` per course into
  `site/lib/pathway-data.json` for WP4's dashboard gate.
- Course pages render two new sections from the bundle: **Assessment** (exam
  format + ai_mode badges, link-style summary of the pass rule) and
  **Project** (acceptance criteria).

### 2.4 Validator extensions (`validate_pathway.py`)

New checks, all errors unless noted:

| # | Rule |
|---|---|
| V8 | Every course directory contains `course.md`, `mission.md`, `project.md`, `rubric.yaml`, `exam.md` |
| V9 | `rubric.yaml` parses; `course` matches directory; every objective has `id`, `statement`, non-empty `evidence`, legal `weight` and `ai_mode`; `pass_rule` well-formed |
| V10 | Objective IDs globally unique across all rubrics |
| V11 | `exam.md`/`project.md` frontmatter present with legal `ai_mode`; `project.md` has an `## Acceptance criteria` section |
| V12 | No stray `curriculum/<X>/` outside `courses/` (layout is now uniform) |
| V13 | *(warning until Phase 3 template lands, then error — WP5)* concept docs contain a `## Common misconceptions` section |

Implementation: a new `check_assessments(courses)` function called from
`main()`; `AI_MODES = {"closed", "open-book", "ai-paired"}` alongside the
existing enums.

### 2.5 Gate

`validate_pathway.py` green on the migrated tree; `build_site_docs.py` output
committed and CI-clean; **CS1101 fully refined** (real objectives, real
evidence lines, real acceptance criteria — not stubs) as the exemplar for all
later refinement; README repo map updated.

**Estimate:** 1–2 sessions. **Risk:** the link-rewrite regexes in
`build_site_docs.py` are the fiddly part — mitigate by diffing `site/docs/`
before/after migration and requiring a byte-identical render for untouched
content.

---

## 3. WP2 — Examiner + reviewer skills, CS1101 pilot exam (06 §2.2–2.3, A2)

### 3.1 Skill implementation

Project-scoped Claude Code skills in `.claude/skills/`, so any session opened
in this repo has them; no external install.

`examiner/SKILL.md` encodes the protocol as hard rules:

- **Inputs:** course ID → loads `rubric.yaml`, `exam.md`, and the course's
  concept docs. Refuses to run if the learner pastes tutoring context.
- **Loop:** for each `core` objective (shuffled), ask; probe every answer with
  ≥1 why/what-if; one transfer question per objective; record verdict
  `evidenced | failed | not-assessed` **with a quoted answer excerpt** as
  evidence. `not-assessed` is not a pass.
- **Verdict:** computed mechanically from `pass_rule` — the skill instructs
  the model to fill the per-objective table first and *derive* pass/fail from
  it, never to state an overall impression first.
- **Output:** writes `examiner-report.md` from `templates/examiner-report.md`
  — frontmatter `{course, date, result, objectives: [{id, verdict, evidence}],
  misconceptions: [...]}` — and tells the learner to commit it to their
  private records repo and to schedule any retake ≥ `retake_cooldown_days` out.
- **Prohibitions stated as rules:** no teaching, no hints, no revealing
  rubric evidence lines mid-exam, no verdict changes on pushback without new
  evidence.

`reviewer/SKILL.md`: given a project repo path + course ID → run every
acceptance-criteria command *first* and paste actual output into the report;
then adversarial read (correctness, tests that don't test, AI-artifact smells
worth probing in the viva); output is a change-request list or a
"qualified for defense" line. Explicitly forbidden from editing the
learner's code.

### 3.2 Pilot (merges into the existing Phase 4 pilot)

Run a real unit exam for CS1101 unit 1 end-to-end: `/examiner CS1101 --unit 1`
against the refined rubric → produce a real examiner report → file a friction
log at `planning/logs/pilot-examiner-CS1101.md` (question quality, sycophancy
observations, protocol gaps) → fold fixes into the skill in the same WP.

### 3.3 Gate

Both skills committed; one genuine examiner report produced under protocol;
friction log committed with every issue either fixed or ticketed in the log.

**Estimate:** 1 session for skills, 1 for pilot+fixes. **Risk:** sycophancy
surviving the protocol — the pilot explicitly tests this by including one
deliberately half-wrong answer and checking the examiner fails it.

---

## 4. WP3 — Learning record v2 + dashboard evidence gate + `/review` skill (06 §2.5, §2.7, A3)

1. **Schema** (`schemas/learning-record.md` + `templates/progress.yaml`):
   record v2 exactly as specified in 06 §2.5 — `courses.<ID>.{status,
   passed_on, examiner_report, project, retakes, misconceptions_resolved}`,
   `review_queue`, `misconception_log`. The record lives in the learner's
   private repo; this repo ships only schema + template.
2. **Validator subcommand**: `validate_pathway.py --record <path>` — course
   IDs resolve, `passed` requires `examiner_report` + all-core-evidenced
   consistency with that report's frontmatter, queue/log entries reference
   real objective IDs from the rubrics. Not run in CI (the record is private);
   it's the learner-side and retro-agent tool.
3. **Dashboard** (`site/islands/Dashboard.tsx`): accept record v2 on import
   (v1 checkbox format still accepted, rendered as `self-reported`); a course
   renders **passed** only when `examiner_report` is set — otherwise
   `in-progress`/`self-reported` styling; show review-queue due count in the
   header. Export writes v2.
4. **`/review` skill**: reads the record's `review_queue`, runs a ~10-minute
   mixed retrieval session over due objectives (question sources: rubric
   statements + misconception catalogue), then outputs the updated queue
   entries (30 → 90 → 250-day intervals; failures shorten to 7 and append to
   `misconception_log`) for the learner to paste/commit back.

**Gate:** dashboard renders correct gated states from a sample v2 record
(fixture committed under `site/islands/` tests or a `samples/` dir);
`--record` subcommand validates the template and rejects three seeded-invalid
fixtures. **Estimate:** 1–2 sessions.

---

## 5. WP4 — Misconception sections in the Phase 3 template (06 §2.7, B1)

Small but it must land **before bulk Phase 3 authoring**:

1. Add `## Common misconceptions` to the Phase 3 concept-doc template
   (documented in the OKF profile `01`, §concept document): 2–5 entries,
   each `**Misconception** — why it's wrong — probe question`, with stable
   anchors (`<a id="mc-...">`)  so rubrics and the misconception log can
   reference them.
2. Update the pilot doc (`.../CS1101/units/01-values-types-expressions.md`)
   as the exemplar; its "Check yourself" section seeds the entries.
3. Flip validator rule V13 from warning to error.
4. Examiner/reviewer/review skills already read concept docs (WP2/WP3);
   confirm they draw probes from these sections — one-line addition to each
   SKILL.md.

**Gate:** validator errors on a misconception-less concept doc; pilot doc
passes. **Estimate:** well under one session; batch with WP3 or WP5.

---

## 6. WP5 — Anchor assessments for keystone courses (06 §2.6, B2)

1. Registry schema gains an optional `kind: anchor` field plus
   `anchor_for: [<course-ID>]` (validator: IDs must resolve; `kind` enum
   `{resource (default), anchor}`).
2. Register anchors for the 8 keystones — CS1201/CS2101 (DS&A: MIT 6.006
   finals + Codeforces band), CS2201 (OS: OSTEP homework + a public xv6 lab
   autograder), CS2102 (arch), CS3102 (ML: Kaggle competition band +
   Berkeley CS188 exams), CS3101 (networks), CS2203 (theory), MA1201/MA2101
   (math: OCW finals with solutions). Each entry status starts `identified`
   per the existing license lifecycle; `exam.md` for those courses gains an
   `anchors:` frontmatter list referencing the registry IDs.
3. Record v2 addition (schema already shipped in WP3 — extend now):
   `courses.<ID>.anchor_results: [{registry_id, score, date}]`.
4. `exam.md` template text: anchor sitting is `closed`-mode, self-marked
   against the published scheme, recorded verbatim — the point is calibration
   of the examiner agent, not a second pass/fail gate.

**Gate:** validator resolves all anchor refs; the 8 keystone `exam.md` files
reference at least one anchor each. **Estimate:** 1 session (mostly curation).

---

## 7. WP6 — Cadence: retro skill, term checkpoints, capstone panel (06 §2.8, C)

1. **`retro/SKILL.md`**: reads the learner's record (path passed in) +
   `git log` of the private repo; outputs the weekly retro — studied delta,
   due review count, misconception-log deltas, DAG frontier ("you could start
   X"), one friction-log prompt. Term checkpoint mode (`/retro --term`) adds:
   pace vs. the semester-load table, and examiner-calibration review comparing
   examiner pass/fail history against anchor scores (06 §2.6).
2. **Capstone panel spec**: extend `curriculum/courses/CS4902/exam.md` —
   defense is 2–3 independent examiner sessions (different models where
   available), all must pass; disputed objectives → targeted retest; plus one
   required *attempt* at human review (the attempt, not the acceptance, is the
   requirement) and a published written report + recorded walkthrough.
3. Cadence is pull-based by design (the learner runs `/retro`); optionally, a
   scheduled reminder can be layered on later — deliberately out of scope
   here, since it depends on the learner's runtime environment, not the repo.

**Gate:** both artifacts committed; `/retro` produces a correct retro from the
sample record fixture. **Estimate:** 1 session.

---

## 8. Sequencing and dependency graph

```
WP1 (layout+schemas+validator) ──► WP2 (skills+pilot) ──► WP3 (record+dashboard+/review)
        │                                                        │
        └──────────► WP4 (misconception template) ◄──────────────┘   (needs WP1 layout; feeds skills)
                                    │
                                    ▼
                          WP5 (anchors)  ──►  WP6 (retro+capstone)
```

Order of execution: **WP1 → WP2 → WP3 → WP4 → WP5 → WP6**, one branch/PR
each, gates as defined above. WP4 may batch with WP3. Total: ~6–8 working
sessions. Phase 3 bulk authoring stays blocked until WP1 + WP4 are merged
(so every concept doc is written into the final layout with the misconception
section from day one); WP5/WP6 can proceed in parallel with early Phase 3.

## 9. Verification (run at every WP gate)

```bash
pip install pyyaml
python3 scripts/validate_pathway.py            # all rules incl. V8–V13
python3 scripts/validate_pathway.py --graph    # canvas/doc staleness
python3 scripts/build_site_docs.py             # deterministic; CI diffs output
python3 scripts/validate_pathway.py --record templates/progress.yaml   # WP3+
cd site && npm install && npx blume build --strict                     # site still builds
```

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| WP1 link-rewrite breakage in the site transform | Byte-diff `site/docs/` pre/post migration for untouched content; CI already fails on stale generated output |
| Rubric stubs fossilize (never refined past unit-title objectives) | CS1101 refined fully in WP1 as the bar; stub rubrics carry `# TODO: refine` and the retro skill surfaces the count of TODO rubrics on the frontier |
| Examiner sycophancy survives the protocol | WP2 pilot includes a planted half-wrong answer that must fail; term checkpoints re-test calibration against anchors |
| Record schema churn after WP3 ships | Dashboard accepts v1 and v2 from day one; any v3 must ship with an import path, rule stated in `schemas/learning-record.md` |
| Skills rot as Claude Code evolves | Skills are plain markdown in-repo, versioned with everything else; friction logs are the refresh trigger |
