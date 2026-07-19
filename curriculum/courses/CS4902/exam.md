---
course: CS4902
type: exam
ai_mode: closed
format: panel-defense
duration_minutes: 90
retake_cooldown_days: 14
---

# CS4902 — Capstone defense spec

The capstone defense is the programme's terminal assessment and its single
most important validity check — so it does not rest on one examiner session
(`planning/06` §2.6). Rubric objectives beyond the panel protocol are refined
in Phase 3 alongside CS4901/CS4902 content.

## Panel protocol

1. **Review gate.** `/reviewer` must have returned *qualified for defense*
   on the capstone repository (acceptance criteria in
   [project.md](project.md)) before any panel session is scheduled.
2. **Independent examiner sessions.** Two, preferably three, `/examiner`
   sessions — each a fresh session, run on a **different model** where
   available, none seeing another's transcript or report. Each conducts a
   full defense against [rubric.yaml](rubric.yaml): architecture walk,
   arbitrary-region "why" probes, one component re-derived from a blank
   buffer, and the reviewer's probe targets.
3. **Aggregation.** The course passes only if **every** panel session
   passes under `pass_rule`. Objectives disputed between sessions (one
   `evidenced`, another `failed`) are re-examined in a targeted follow-up
   session restricted to the disputed objectives; its verdicts are final.
4. **Human review attempt.** The learner must *attempt* to recruit one
   human reviewer — a working engineer reading the repo cold and asking
   questions in writing or live. The attempt is the requirement, not the
   acceptance: record who was asked, and the outcome, in the defense
   report. If a human review happens, its findings are appended to the
   examiner reports and count as evidence.
5. **Public artifact.** The defense concludes with publication: a written
   capstone report and a recorded walkthrough (screen capture is fine),
   linked from the capstone repository. "Public defense" means actually
   public — the artifact is the programme's proof-of-graduate-competence to
   anyone who asks.

## Records

Each panel session produces its own examiner report
(`templates/examiner-report.md`); the learner's record links all of them
plus the human-review note in `examiner_report` (a defense index file
listing the panel reports is acceptable). A failed panel retakes after
`retake_cooldown_days` with a fresh panel.
