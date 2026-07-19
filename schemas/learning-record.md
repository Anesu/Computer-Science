# Learning Record Schema v2

The learner's evidence-linked record (`planning/06` §2.5). It lives in the
learner's **private repo** — never in this one; this repo ships only the
schema, the empty template (`templates/progress.yaml`), and the validator
(`scripts/validate_pathway.py --record <path>`). The dashboard imports and
exports this format but the private repo stays authoritative.

## `progress.yaml`

```yaml
version: 2
learner: <name>
updated: 2027-02-11
courses:
  CS2201:
    status: passed             # passed | self-reported | in-progress
    passed_on: 2027-02-11      # required when passed
    examiner_report: reports/CS2201-exam-2027-02-11.md   # required when passed;
                               # path relative to this file
    project: https://github.com/you/os-labs              # optional
    retakes: 1                 # optional, non-negative
    misconceptions_resolved:   # optional — ids from misconception_log
      - cs2201.sched.priority-inversion:starvation
    anchor_results:            # optional — external calibration sittings
      - {registry_id: anchor-mit-6006, score: "71%", date: 2027-02-01}
review_queue:                  # spaced retrieval (managed by /review)
  - {objective: ma1201.svd.geometry, due: 2027-03-01, interval: 30}
misconception_log:             # append-only; resolved stays in the log
  - {id: cs2201.sched.priority-inversion:starvation,
     detected: 2027-01-20, resolved: 2027-02-11, course: CS2201}
```

## Semantics

- **`status: passed` requires evidence.** `examiner_report` + `passed_on`
  are mandatory; the report is the examiner's structured output
  (`templates/examiner-report.md`). The validator cross-checks the report
  when it can reach the file: `course` matches, `result: pass`, and every
  `core` objective in the course rubric has verdict `evidenced`.
- **`self-reported`** is a checkbox with no evidence — legitimate (prior
  knowledge, external courses) but rendered distinctly everywhere.
- **Objective and misconception IDs** are global: objective IDs come from
  the course rubrics (`rubric.yaml`); misconception IDs are
  `<objective.id>:<short-slug>`.
- **`review_queue` intervals** are days; `/review` expands them
  30 → 90 → 250 on success and shortens to 7 on failure (which also appends
  to `misconception_log`).
- **`misconception_log` is append-only.** Resolution sets `resolved`; entries
  are never deleted — trends across entries are what `/retro` reads.

## Compatibility

- **v1** (flat `completed_courses` / `in_progress` lists) remains importable
  by the dashboard; v1 completions render as `self-reported`.
- Any future **v3** must ship with an import path for v2 before the dashboard
  or skills may require it.
