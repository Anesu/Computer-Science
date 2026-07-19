---
course: CS1101
type: exam
ai_mode: closed
format: viva
duration_minutes: 60
retake_cooldown_days: 3
---

# CS1101 — Exam spec

Closed-book oral exam (viva) conducted by the `/examiner` skill against
[rubric.yaml](rubric.yaml). No AI assistance, no notes, no interpreter —
prediction and reasoning happen in the learner's head and on scratch paper;
the point of `closed` mode here is exactly the skill the course trains:
knowing what code does *before* running it.

## Scope

All nine rubric objectives. The two `ai-paired` objectives
(`cs1101.ai-practice.verify-generated`, `cs1101.project.defense`) are examined
in the same sitting but switch mode: the learner presents their transcript and
project, then defends them under closed-book questioning.

## Question style

Per objective, in order:

1. **Do** — a concrete task (reduce this expression, trace this loop, write
   this recursive function in the chat from a blank buffer).
2. **Probe** — at least one why/what-if on the learner's own answer
   ("what if the input list is empty?", "why does this terminate?").
3. **Transfer** — the same concept in a novel dress: a structure-choice
   question wearing a different domain, a trace with an unfamiliar idiom.

Code presented for debugging or critique must be code the learner has not
seen: the examiner writes fresh variants each sitting, seeded from the unit
concept documents' misconception catalogues.

## Defense segment

For `cs1101.project.defense`: the examiner opens the learner's submitted
project, picks two or three arbitrary regions, and asks *why* questions
(design, not syntax). Then one function, chosen by the examiner, is rewritten
from a blank buffer while the learner narrates. Hesitation on one's own
recently-written code is a strong not-yet signal.

## Outcome

The examiner fills the per-objective verdict table first; pass/fail is then
derived mechanically from `pass_rule` (all five core objectives evidenced,
at least 3 of the 4 supporting). Failed objectives are listed with the observed
gap and routed back to tutoring. Retake no earlier than
`retake_cooldown_days` later, with fresh questions throughout.
