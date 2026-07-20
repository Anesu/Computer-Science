# OSSU Cross-Audit

One-off report, 2026-07-20. Companion to `planning/07-superiority-program.md` (S10).

Method: section-by-section diff of the current
[OSSU computer-science curriculum](https://github.com/ossu/computer-science)
(fetched 2026-07-20) against `curriculum/pathway.yaml` + the CS2023 KA
matrix (`planning/03-coverage-matrix.md`), looking for anything OSSU's decade
of community feedback covers that our design misses.

**Verdict: no structural holes.** Two findings, one fixed in this pass, one
recorded as an advisory. Everything else is a deliberate design choice.

---

## Findings

### F1 — Testing & debugging had no explicit home (FIXED)
A grep of `curriculum/courses/` found zero mentions of "test" or "debug":
44/45 specs are Phase-2 scaffolds, and the one authored course (CS1101) has
no testing unit. OSSU teaches design-for-testing from week 1 (Systematic
Program Design) and has dedicated Software Testing / Software Debugging
courses in Advanced CS.
**Fix applied 2026-07-20:** CS1203 units defined (8 units incl. *Debugging
and profiling* + *Automated testing*); CS2103 units defined (8 units incl.
*Testing strategy: unit, integration, end-to-end*). S6's per-unit pytest
harness (`assess/`) reinforces this mechanically — learners write code
against tests from CS1101 onward.

### F2 — No numerical methods course (ADVISORY)
OSSU Advanced math includes MIT 18.335J Introduction to Numerical Methods.
We have nothing equivalent. Acceptable: it is genuinely elective-level for a
CS degree, and MA1201 + MML touch numerics. Recorded as a candidate future
elective (`EL-NUM`); no pathway change now.

---

## Section-by-section diff

| OSSU block | Ours | Verdict |
|---|---|---|
| Intro CS (MIT 6.00.1x) | CS1101 + CS50P lecture track (S1) | Covered |
| Systematic Program Design (design recipe) | CS1101 units + /teach decomposition emphasis | Covered; keep design-recipe discipline explicit when authoring CS1101 concept docs |
| Class-based / OO design, Software Architecture | CS2103 + APOSD + swe-google + UBC 310 track | Covered |
| Programming Languages (CSE341: SML/Racket/Ruby) | CS3103 + same CSE341 as lecture track | Covered (same source) |
| Calculus 1A/1B/1C (~32 wks) | MA1102 Calculus for Computing (3 cr) | Deliberate: computing-focused, ML-oriented; lighter by design |
| Math for CS (6.042J) | MA1101 + same 6.042J as lecture track + Rosen + MCS | Covered, deeper (two texts) |
| CS Tools (Missing Semester) | CS1203 + Missing Semester as lecture track | Covered (same source) |
| Nand2Tetris I/II | CS1102 + the same book + Coursera track | Covered (same source) |
| OSTEP | CS2201 primary text + MIT 6.1810 lectures | Covered, deeper |
| Networking (Kurose-Ross) | CS3101 + same authors' lectures + Beej | Covered |
| Stanford Algorithms I/II | CS1201 + CS2101 (two courses, CLRS + Erickson + Roughgarden track) | Covered, deeper |
| Core security (3 + 1 courses) | CS3104 + 5-course security track | Stronger |
| Databases (Stanford ×3) | CS2202 + Stanford DB track + SYS-DBI + CMU 15-445 | Stronger |
| Machine Learning (Ng specialization) | CS3102 + same specialization as lecture track + AI track | Stronger |
| Computer Graphics | EL-GRAPH + UCSD edX track | Covered |
| Software Engineering (UBC) | CS2103 + same UBC 310 track | Covered (same source) |
| Ethics ×3 (incl. IP, privacy) | CS4101 + SEC-PRIV + AI-SAFE | Comparable |
| Computation Structures ×3 (digital logic depth) | CS1102 (nand2tetris projects) + CS2102 (P&H + MIT 6.004 track) | Comparable |
| Theory of Computation | CS2203 (Sipser + Barak + Sipser's own OCW lectures) | Covered, deeper |
| Parallel (Scala course) | CS3201 + MIT 6.824 + perfbook | Stronger |
| Compilers | SYS-COMP track + Stanford Compilers + Crafting Interpreters | Stronger (OSSU: elective only) |
| Haskell / Prolog exposure | CS3103 paradigm units via CSE341 | Covered (lighter — acceptable) |
| Computational Geometry / Game Theory | — | Skipped deliberately (tracks instead of survey electives) |
| Linear Algebra / Probability (advanced math) | MA1201 + MA2101 as required core | Stronger (OSSU: advanced electives) |
| Software Testing / Debugging | F1 — fixed (CS1203/CS2103 units + S6 harness) | Fixed |
| Numerical Methods | F2 — advisory, candidate EL-NUM | Open |
| Final project | CS4901 + CS4902 (two-semester capstone, POOS + Full Stack Open) | Stronger |
| Community (Discord, per-course chats) | None — agent + S7 streak/pace instead | Deliberate skip (revisit if published) |

## Follow-ups

- [ ] Bake the SPD "design recipe" (examples before code, tests first) into
      CS1101 concept docs as Phase 3 authors them.
- [ ] Revisit `EL-NUM` if/when a numeric-heavy learner profile appears.
