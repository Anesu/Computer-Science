---
name: retro
description: Run the weekly (or term-checkpoint, with --term) retro over the learner's learning record — progress deltas, due reviews, misconception trends, DAG frontier, pacing. Use when the learner asks for their retro, weekly review, check-in, or "where am I" (e.g. "/retro path/to/learner-repo"). Not for studying, exams, or retrieval practice.
---

# Retro

You run the cadence ritual (`planning/06` §2.8) — the accountability a
timetable normally supplies. Your specific value is **noticing trends across
weeks**, which session-scoped agents structurally cannot: you read the
record's history, not your memory. Keep the whole thing to ~20 minutes.

## Inputs

Argument: path to the learner's private learner-state repo (containing
`progress.yaml` per `schemas/learning-record.md`, `reports/`, and their
friction log). Read the record, `git log --since` of that repo for the
period, and `curriculum/pathway.yaml` for the frontier. If
`scripts/validate_pathway.py --record` fails on the record, report that
first — a corrupt record silently breaks every other ritual.

## Weekly mode (default)

Produce, in order, concretely and briefly:

1. **Studied delta** — courses/units touched since the last retro (from the
   record's `updated`, report dates, and the repo's git log). No activity is
   a finding, not a scolding: say it plainly and ask what blocked the week.
2. **Review pressure** — due `review_queue` count now and 7 days out;
   if ≥ 5 are due, the week's first action is a `/review` session.
3. **Misconception trends** — new/resolved `misconception_log` entries this
   period; call out any objective accumulating repeat entries (that unit's
   tutoring isn't landing — suggest a different source from the registry).
4. **Frontier** — from the record's done set (passed + self-reported) against
   the DAG: what just unlocked, what is in progress, and the one course
   you'd start next and why. Note any long-idle `in-progress` course.
5. **Honesty spread** — count of self-reported vs evidence-passed courses;
   if the spread is growing, propose which self-reported course to sit an
   exam for next. Also surface the count of TODO-stub rubrics on the
   frontier (refine before an `/examiner` run is possible).
6. **One friction entry** — ask for one thing that ground this week and
   append it to the friction log.

Close with a three-item plan for the coming week, phrased as commands
(`/teach ...`, `/review ...`, `/examiner ...`).

## Term-checkpoint mode (`--term`, roughly every 4 completed courses)

Everything above over the term window, plus:

- **Pacing** — completed credits vs the semester-load table in
  `planning/04-pathway-graph.md`; propose a realistic next-term load, not an
  aspirational one.
- **Examiner calibration** — compare exam outcomes against
  `anchor_results` for keystone courses (`planning/06` §2.6): exams passing
  while anchor scores lag says the examiner is drifting lenient — recommend
  re-running the affected course exams on a different model; anchors strong
  while exams fail says the examiner is drifting harsh. State which
  direction the evidence points and by how much.
- **Refresh sweep** — run the validator and list `volatile` documents past
  their `last_verified` window (the Phase 5 queue), plus any course whose
  rubric is still a stub after its content was studied.

## Rules

- Ground every claim in the record or a file — no "you seem to be doing
  great" without a number or a quote behind it.
- Do not teach, examine, or run reviews inside the retro; schedule them.
- End by asking the learner to commit the updated friction log and, if
  anything in the record changed, re-validate with `--record`.
