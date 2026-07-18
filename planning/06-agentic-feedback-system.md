# Self-Directed Learning under AI-Only Feedback — System Improvements Plan

**Date:** 2026-07-18
**Status:** Proposed. Supersedes nothing; extends the charter (`00`) and OKF
profile (`01`) with an assessment-and-feedback layer.

## 1. The problem this plan solves

The programme will be completed by one self-directed learner whose *only*
feedback mechanism is LLMs and agentic AI: no instructor, no graders, no
peers, no deadlines. That changes which failure modes matter most. The current
system (course specs, `/teach` missions, a progress dashboard) is strong on
*sequencing* and *content*, and weak on exactly the things a university
otherwise provides:

| # | Failure mode | Why it is acute here |
|---|---|---|
| F1 | **Sycophantic grading.** LLMs default to encouragement and pass borderline work. | The grader is also the tutor with a rapport-shaped context; a lenient examiner silently converts the degree into a reading list. |
| F2 | **The AI does the work.** AI-assisted practice is (rightly) woven into every course — but the same assistant that helps can complete the assignment, and no human ever notices. | Quiz-passing plus AI-completed projects certifies nothing. This is the single biggest validity threat. |
| F3 | **Self-referential assessment.** The AI writes the content, teaches it, writes the quiz, and grades it. Model blind spots become invisible curriculum-wide gaps. | Nothing anchors "mastery" to any external standard once scraping/mapping is done. |
| F4 | **Unknown unknowns stay unknown.** An LLM answers what it is asked; it does not spontaneously probe for the misconception you don't know you have. | A human TA notices confusion across weeks; a fresh chat session notices nothing. |
| F5 | **Drift and abandonment.** No external cadence, no cohort, no cost of quitting. | Structure must supply the accountability a timetable normally does. |
| F6 | **Memory decay.** `/teach` quizzes are formative and immediate; nothing revisits material weeks later. | Without spaced retrieval, semester-1 math is gone by semester 4 when ML needs it. |

The unifying design principle for every improvement below:

> **Separate the roles, and prefer verification over judgment.**
> The agent that teaches must not be the agent that certifies; and wherever
> possible, "did I master this?" should be answered by *running something*
> (tests, benchmarks, proofs checked line-by-line) rather than by an LLM's
> impression.

## 2. Improvements

### 2.1 Per-course assessment bundle (structure change)

Phase 2 delivered flat `curriculum/courses/<ID>.md` files. The OKF profile
(§ document types) already plans per-course directories — adopt them now,
*before* Phase 3 authoring, and give assessment first-class files:

```
curriculum/courses/CS2201/
  course.md        # existing spec (moved)
  mission.md       # /teach mission (extracted from course.md)
  project.md       # project brief + machine-verifiable acceptance criteria
  rubric.yaml      # grading rubric as data (schema below)
  exam.md          # summative oral-exam ("viva") spec: scope, question style, pass bar
  units/...        # Phase 3 concept documents
```

`rubric.yaml` schema (validated in CI):

```yaml
course: CS2201
objectives:
  - id: os.proc.lifecycle
    statement: Explain process states and what triggers each transition
    evidence:            # what an examiner must SEE to award it — observable, not vibes
      - Learner produces the state diagram unprompted and walks a fork/exec/wait trace
    weight: core         # core | supporting  — all core objectives required to pass
  - id: os.sched.impl
    statement: Implement and benchmark a scheduling policy
    evidence:
      - Project scheduler passes the provided test suite
      - Learner explains one design tradeoff they made and its measured effect
    weight: core
pass_rule: all core objectives evidenced; >=70% of supporting
```

Rationale: rubrics-as-data is what makes every downstream anti-sycophancy
measure possible — an examiner agent can be *required* to cite evidence per
objective instead of emitting a holistic "great job, pass!"

### 2.2 Role-separated agents: tutor / examiner / reviewer (the core move)

Three distinct, versioned skills live in this repo (e.g. `skills/`), each with
a deliberately different contract:

| Skill | Session rules | May | Must not |
|---|---|---|---|
| **/tutor** (today: `/teach`) | Long-running, warm, learner-adaptive | Explain, hint, pair-program, answer anything | Award course completion |
| **/examiner** | **Fresh session**, no tutoring transcript in context, rubric + exam spec loaded | Probe, ask follow-ups, drill into weak answers, fail the learner | Teach, hint, reveal rubric evidence lines mid-exam, or pass without cited evidence |
| **/reviewer** | Fresh session per project submission | Run the acceptance tests, read the code adversarially, demand changes | Fix the code itself; accept "tests pass" as sufficient without reading |

Examiner protocol (encoded in the skill, not left to chance):

1. Load `rubric.yaml` + `exam.md`. For each **core** objective, ask until it
   has affirmative evidence or a recorded failure — *absence of failure is not
   evidence*. Default verdict is **not yet**.
2. Follow-up rule: every substantive answer gets at least one "why" or
   "what-if" probe; a memorized definition must survive one transfer question
   (novel scenario using the same concept).
3. Output is a structured **examiner report** (see §2.5): per-objective
   verdict + quoted evidence + identified misconceptions. The pass/fail falls
   out of `pass_rule` mechanically — the model doesn't get to feel generous.
4. Fail is a normal, expected outcome: report routes misconceptions back to
   the tutor as the next mission's focus, and the exam can be retaken after a
   cooling-off period (e.g. 3 days) with fresh questions.

Additional de-biasing, cheap to adopt where available: run the examiner on a
**different model** than the tutor, and for capstone/course finals run **two
independent examiner sessions** and require both to pass (disagreement =
retest on the disputed objectives).

### 2.3 Verification-first projects (attack on F1 and F2)

Every `project.md` acceptance criterion must be phrased as a *command with an
expected outcome* wherever the domain allows: a pytest suite, a benchmark
threshold, a fuzzer that finds no crashes, a proof checked step-by-step. The
reviewer agent's first act is to **run** the criteria, not read the prose.

The AI-did-the-work problem is then handled by the **defense**, not by
surveillance: passing tests qualifies the project for a viva in which the
examiner picks arbitrary parts of *the learner's own submission* and asks:
why this data structure, what breaks if this line changes, rewrite this
function's core loop from a blank buffer while talking through it. Code you
didn't write — or wrote without understanding — does not survive ten minutes
of this. This mirrors the degree's stated philosophy: using AI is a
professional skill, but the *understanding* must live in the learner.

### 2.4 Explicit AI-usage tiers per assessment

Add one frontmatter field to every assessment artifact:

```yaml
ai_mode: closed | open-book | ai-paired
```

- `closed` — recall/derivation exams and defenses: no AI, no notes. What must
  be demonstrable unaided: core vocabulary, mental execution of code, big-O
  reasoning, proof sketches.
- `open-book` — docs and references allowed, no generative help. Typical for
  timed labs.
- `ai-paired` — full agentic assistance expected; the graded artifact includes
  the *prompt/agent transcript*, and the rubric grades the direction-giving,
  review, and verification the learner did. This is where "engineering with AI
  teammates" is actually assessed rather than merely permitted.

This resolves the tension between "AI woven into every course" and assessment
validity: each objective declares which tier proves it.

### 2.5 Evidence-linked learning record (structure change)

Progress today is a checkbox (`progress.yaml`, localStorage). Extend the
schema — still living in the learner's private repo, per charter §10 — so a
course is *complete* only with evidence attached:

```yaml
courses:
  CS2201:
    status: passed
    passed_on: 2027-02-11
    examiner_report: reports/CS2201-exam-2027-02-11.md   # structured report from §2.2
    project: https://github.com/Anesu/os-labs            # repo whose CI is green
    retakes: 1
    misconceptions_resolved: [os.sched.priority-inversion]
review_queue:            # spaced repetition, see §2.7
  - {objective: ma1201.svd.geometry, due: 2027-03-01, interval: 30}
misconception_log:       # every misconception any agent ever detects, append-only
  - {id: os.sched.priority-inversion, detected: 2027-01-20, resolved: 2027-02-11, course: CS2201}
```

The dashboard (FE-2) gains a soft gate: a course renders "passed" only when
`examiner_report` is present. It's an honor system — everything here is — but
the structure makes the honest path the default path, and the record becomes
the portfolio: examiner reports + green project repos are the closest thing
this degree has to a transcript worth showing anyone.

### 2.6 External anchors (attack on F3)

Break the self-referential loop by pinning assessment difficulty to the
outside world at a few load-bearing points:

- **Anchor exams:** for ~8 keystone courses (DS&A, OS, architecture, ML,
  networks, theory, linear algebra, probability), the registry gains
  published past exams with solutions — MIT OCW finals, Berkeley CS188/CS162
  exams, past papers with mark schemes. Sitting one under `closed` conditions
  and self-marking against the *published* scheme calibrates both the learner
  and the examiner agent ("my examiner passes me, and I score ~70% on the MIT
  final" is a real signal; either alone is not).
- **Competitive/automated externals** where they exist: LeetCode/Codeforces
  bands for DS&A, Kaggle leaderboard position for ML, CTF challenges
  (picoCTF/OverTheWire tiers) for security, SQL/OS lab suites with public
  autograders. Record the objective external result in the learning record.
- **Capstone defense** (CS4902) is examined by a *panel*: two or three
  independent examiner sessions on different models, plus at least one
  attempt to recruit a human reviewer (a working engineer reviewing the repo
  cold). The charter's "public defense" should mean *actually public*: a
  written report and recorded walkthrough published with the capstone.

### 2.7 Spaced retrieval + misconception loop (attack on F4, F6)

- Every objective evidenced in an exam enters `review_queue` with an expanding
  interval (30 → 90 → 250 days). A lightweight **/review** skill runs a
  10-minute mixed retrieval session from due items and re-queues them;
  failures route back into `misconception_log` and shorten the interval.
- Phase 3 authoring gains a requirement: every concept document includes a
  **"Common misconceptions"** section (the pilot's "Check yourself" section is
  the seed of this). These are gold for LLM feedback quality — a tutor that
  knows the misconception catalogue probes for the *specific* wrong models a
  learner is likely to hold, which is what a fresh chat session otherwise
  cannot do. The examiner draws distractors and what-if probes from the same
  catalogue.

### 2.8 Cadence and sustainment (attack on F5)

- **Weekly retro ritual** (~20 min, agent-driven, one prompt in the repo):
  what was studied, what's due in the review queue, misconception log deltas,
  frontier check ("what does the DAG say you could start next"), and one
  friction-log entry. The agent's job is to *notice trends across weeks* —
  the thing session-scoped LLMs are worst at — by reading the learning record,
  not by remembering.
- **Term boundaries:** every ~4 courses, a checkpoint retro decides
  pace changes and reviews whether examiner strictness feels calibrated
  against the anchors (§2.6).
- The existing Phase 5 refresh policy (`churn`/`last_verified`) stays; the
  weekly ritual is its trigger surface.

## 3. What changes where (delta summary)

| Artifact | Change |
|---|---|
| `curriculum/courses/` | Flat files → per-course directories with `project.md`, `rubric.yaml`, `exam.md` (schema in §2.1) |
| `skills/` (new) | `/examiner`, `/reviewer`, `/review` skill definitions; `/tutor` = existing `/teach` mission flow |
| OKF profile (`01`) | Add `ai_mode` to assessment artifacts; add "Common misconceptions" as a required concept-doc section for Phase 3 |
| `scripts/validate_pathway.py` | Validate rubric schema, objective-ID uniqueness, every course has project/rubric/exam, misconception section present in concept docs |
| `resources/registry.yaml` | Anchor-exam and external-autograder entries for keystone courses |
| Learning record schema (private repo) | Evidence-linked completion, `review_queue`, `misconception_log` (§2.5) |
| Site dashboard (FE-2) | Soft evidence gate on "passed"; review-queue count surfaced |

## 4. Sequencing

Ordered so that Phase 3 content authoring lands into the improved structure
rather than being migrated afterward:

1. **A1 — Adopt per-course directories + rubric/exam/project schemas; extend
   validator.** (Gate: CI validates the new layout; CS1101 fully converted as
   the exemplar.)
2. **A2 — Write `/examiner` and `/reviewer` skills; pilot a real CS1101 unit
   exam end-to-end.** (Gate: one examiner report produced under the protocol,
   friction log filed. This piggybacks on the existing Phase 4 pilot.)
3. **A3 — Learning-record schema v2 + dashboard evidence gate + `/review`
   skill.** (Gate: dashboard renders evidence-gated state from a sample
   record.)
4. **B1 — Misconception sections become part of the Phase 3 authoring
   template** (applies to all concept docs from here on; pilot doc updated).
5. **B2 — Anchor assessments registered for the 8 keystone courses.**
6. **C — Weekly retro prompt + term-checkpoint protocol committed;
   capstone panel-defense spec added to CS4902.**

A1–A3 are small and structural — days, not weeks — and everything else in the
programme gets more trustworthy the moment they exist.

## 5. Explicitly rejected alternatives

- **Surveillance-style anti-cheating** (lockdown modes, keystroke proof).
  Pointless when the learner owns the whole system; the defense viva (§2.3)
  achieves validity through *understanding checks* instead.
- **A single "super-tutor" agent that also grades.** Rejected as the root
  cause of F1/F3; role separation is the entire point.
- **Hard gating in the dashboard** (blocking course pages until prerequisites
  are evidenced). The DAG is advice, not law, for an adult learner; soft
  gates + honest records preserve agency without lying to the record.
- **Human-free capstone.** One human review attempt is required at the
  capstone; it is the single highest-value external calibration point in the
  whole degree, worth the awkwardness of asking.
