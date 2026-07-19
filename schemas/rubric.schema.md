# Rubric & Assessment Bundle Schema v1.0

Contract for the per-course assessment files introduced by
`planning/06-agentic-feedback-system.md` §2.1. Enforcement lives in
`scripts/validate_pathway.py` (rules V8–V13); this document is the
human-readable source of truth. Changing it is a charter-level decision.

## Course directory layout (rule V8)

Every course in `curriculum/pathway.yaml` has a directory
`curriculum/courses/<ID>/` containing exactly these assessment files:

| File | Role |
|---|---|
| `course.md` | Course spec (OKF course document, frontmatter per `planning/01-okf-profile.md`) |
| `mission.md` | `/teach` mission — plain markdown, **no frontmatter** (delivery-time input, not an OKF document) |
| `project.md` | Project brief + machine-verifiable acceptance criteria |
| `rubric.yaml` | Grading rubric as data (schema below) |
| `exam.md` | Summative viva spec for the `/examiner` skill |
| `units/` | Phase 3 concept documents, `<nn>-<slug>.md` (optional until Phase 3 reaches the course) |

No other directories may exist directly under `curriculum/` except `courses/`
(rule V12).

## `rubric.yaml` (rules V9–V10)

```yaml
course: CS2201                  # must equal the directory name
objectives:
  - id: cs2201.proc.lifecycle   # dot-namespaced, lowercase, globally unique
    statement: Explain process states and what triggers each transition
    evidence:                   # >=1 entries — what an examiner must SEE, observably
      - Learner produces the state diagram unprompted and walks a fork/exec/wait trace
    weight: core                # core | supporting
    ai_mode: closed             # closed | open-book | ai-paired
pass_rule:
  core: all                    # fixed in v1 — every core objective must be evidenced
  supporting_min: 0.7          # fraction of supporting objectives required
```

Constraints:

- `course` equals the directory name (V9).
- Objective `id` matches `^[a-z0-9-]+(\.[a-z0-9-]+)+$` and is unique across
  **all** rubrics in the repo (V10) — the misconception log and review queue
  reference these IDs globally.
- Every objective has a non-empty `statement`, a non-empty `evidence` list,
  a legal `weight`, and a legal `ai_mode` (V9).
- At least one objective is `core` — a rubric with only supporting
  objectives would make `pass_rule.core: all` vacuously true (V9).
- `pass_rule.core` is the literal string `all`; `pass_rule.supporting_min`
  is a number in [0, 1] (V9).

## `ai_mode` (rule V11)

Declares the AI-usage tier under which an objective or assessment is
demonstrated (`planning/06` §2.4):

| Mode | Meaning |
|---|---|
| `closed` | No AI, no notes — recall, derivation, mental execution, defenses |
| `open-book` | Docs and references allowed, no generative help |
| `ai-paired` | Full agentic assistance expected; the transcript is part of the graded artifact |

## `exam.md` frontmatter (rule V11)

```yaml
---
course: CS2201
type: exam
ai_mode: closed
format: viva
duration_minutes: 45
retake_cooldown_days: 3
---
```

Body: scope and question style for the viva. The `/examiner` skill loads this
together with `rubric.yaml`.

Keystone courses add `anchors: [<registry-id>, ...]` — each id must exist in
`resources/registry.yaml` with `kind: anchor` (a published exam with
solutions, or a public autograder). Anchor sittings are `closed`-mode,
self-marked against the published scheme, and recorded verbatim in the
learning record's `anchor_results`; they calibrate the learner *and* the
examiner agent against an external standard, and are not a second pass/fail
gate (`planning/06` §2.6).

## `project.md` frontmatter (rule V11)

```yaml
---
course: CS2201
type: project
ai_mode: ai-paired
---
```

Body must contain an `## Acceptance criteria` section whose items are, wherever
the domain allows, *commands with expected outcomes* — the `/reviewer` skill
runs them before reading any code.

## Stub rubrics

Migration seeded scaffold courses with objectives marked `TODO: refine`.
Stubs validate (the schema is satisfied) but are not exam-ready; the count of
TODO-carrying rubrics is surfaced by the validator summary and the `/retro`
skill. A course's rubric must be refined before its first `/examiner` run —
the exemplar is `curriculum/courses/CS1101/rubric.yaml`.
