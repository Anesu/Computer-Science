---
name: review
description: Run a spaced-retrieval session over the due items in the learner's review queue (learning record v2). Use when the learner asks for their reviews, spaced repetition, or retention practice (e.g. "/review path/to/progress.yaml"). Not for exams or new material — those are /examiner and /teach.
---

# Review

You run a short **spaced-retrieval session** — the memory-decay defense
(`planning/06` §2.7). Ten minutes, mixed retrieval over objectives whose
review is due, then updated queue entries the learner commits back to their
private record.

## Inputs

Argument: path to the learner's `progress.yaml` (schema:
`schemas/learning-record.md`). Read `review_queue` and take every item with
`due` ≤ today (cap at ~8 items; oldest due first — say what you deferred).
For each item's objective, load its rubric entry from
`curriculum/courses/<COURSE>/rubric.yaml` and, when present, the unit concept
docs' "Common misconceptions" sections for that topic.

## Session rules

- **Retrieval, not recognition.** Ask the learner to produce — trace, write,
  derive, explain — never multiple-choice, and never re-teach first. Honor
  the objective's `ai_mode` (`closed` items: no looking things up).
- One question per item, drawn fresh from the objective's statement and the
  misconception catalogue; a shaky answer gets one probe to distinguish
  slipped-recall from lost-understanding.
- Keep pace: this is a 10-minute maintenance ritual, not an exam. No
  verdict theater — per item, just *held* or *slipped*.

## Updating the queue

For each item, output the replacement `review_queue` entry:

- **Held:** next interval in the 30 → 90 → 250 progression (stay at 250
  after that); `due` = today + new interval.
- **Slipped:** interval 7, `due` = today + 7, and append a
  `misconception_log` entry (`<objective.id>:<slug>`, detected today,
  resolved null, course from the objective's rubric) describing what
  actually broke.

Finish with a single fenced YAML block containing the updated
`review_queue` entries and any new `misconception_log` entries, ready to
paste into the record — then remind the learner to commit and to re-validate
with `scripts/validate_pathway.py --record`.
