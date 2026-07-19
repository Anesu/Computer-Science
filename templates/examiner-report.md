---
course: __COURSE_ID__
type: examiner-report
date: __YYYY-MM-DD__
sitting: exam            # exam | unit-N | retake
result: __pass|fail__    # derived from pass_rule AFTER the table is complete
examiner_model: __model identifier__
objectives:
  # one entry per rubric objective — every objective, no omissions
  - id: __objective.id__
    verdict: __evidenced|failed|not-assessed__
    evidence: >-
      __short quote or concrete description of what the learner actually
      did in this session that satisfies (or fails) the rubric evidence__
misconceptions:
  # anything surfaced, even on passed objectives — feeds the learner's
  # misconception_log and the next tutoring mission
  - id: __objective.id:short-slug__
    note: __what the learner believes that is wrong, in one sentence__
retake_allowed_from: __YYYY-MM-DD__   # date + retake_cooldown_days, if failed
---

# Examiner report — __COURSE_ID__, __YYYY-MM-DD__

## Summary

__Two or three sentences: overall result, which core objectives carried it
or sank it, and the single most important thing to practice next.__

## Verdict detail

__Per objective, one short paragraph: the task given, what the learner did,
why that does or does not satisfy the rubric's evidence line. Quote the
learner where the quote is the evidence.__

## Routed to tutoring

__Bulleted list of failed/shaky objectives with a concrete practice
suggestion each — this section becomes the next /teach mission's focus.__
