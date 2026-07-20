# Superiority Program — closing the gap, then going beyond

Working document, 2026-07-20. Companion to `planning/06-resource-gaps-and-reading-plan.md`.

Mandate: match what the best self-taught CS programs offer, then surpass them
on structure, pedagogy, and UX. Refactors are authorized where they produce a
superior product; the curriculum-as-data architecture stays — it is the
advantage everything else builds on.

The measurable definition of "superior" (the acceptance test for this program):

1. Every one of the 45 courses can be started **tonight** with proven teaching
   material (lecture track or authored concept docs).
2. Every unit ends in **graded proof of work** (autograded exercises or a
   project with tests), not just self-reported completion.
3. Every concept produces **spaced-repetition cards**; retention is
   systematized, not hoped for.
4. The dashboard answers "what do I do **today**?" in one glance, and projects
   a completion date from actual pace.
5. No link rots silently; no license is ambiguous.

---

## 1. What the best already do — and the takeaway for us

| Program | What it does well | Takeaway |
|---|---|---|
| [OSSU/computer-science](https://github.com/ossu/computer-science) | Complete MOOC mapping, battle-tested by thousands, per-course Discord | We need a proven lecture track under every course *now* (S1) |
| [roadmap.sh](https://roadmap.sh/computer-science) | Node-DAG UX with done/in-progress states (6th most-starred repo on GitHub) | We already match this (PathwayMap); next: per-node resource surfacing |
| [The Odin Project](https://www.theodinproject.com/about) | Open-source curriculum, project-first lessons with explicit assignment sections | Concept docs keep "Check yourself", add "Build this" per unit (S6) |
| [CS50 check50](https://cs50.readthedocs.io/projects/check50/en/latest/) | Autograder: checks are plain Python functions, decoupled from the tool, run `--local` | Adapt the model with pytest — no new platform dependency (S6) |
| Duolingo | Streaks, bite-size units, skill-decay → review prompts | Streak + decay-fed review queue on the dashboard (S7) |
| Khan Academy | Mastery levels per skill (unfamiliar → mastered) | Per-unit mastery in progress.yaml v2, fed by /teach quizzes (S4) |
| [FSRS / Anki](https://github.com/open-spaced-repetition/fsrs4anki) | Modern spaced-repetition scheduler, **built into Anki ≥ 23.10** | We generate decks; Anki does scheduling. Do not build our own (S5) |
| Boot.dev / Exercism | Interactive exercises with automated feedback, XP | Out of scope to build; pytest harness + /teach covers the loop (S6) |
| Fullstack Open | Exercise parts submitted to GitHub, free certificate | "Proof of work" public repo per course project (S8) |
| Teach Yourself CS | The "why" per subject + ~100–200 h pacing guidance | Our course specs already carry the "why"; pace projection covers the rest (S7) |

## 2. Decisions

**Adopt**: MOOC bridge; SRS via Anki decks; mastery levels; streak + pace
projection; per-unit graded exercises; proof-of-work repos; link-rot CI.

**Adapt**: check50 → a thin pytest harness (`scripts/grade.py`), same
"checks live next to the curriculum" principle without a new platform.
Odin-style lesson format → extend our concept-doc template with a "Build
this" section (already have "Check yourself" / "Where to read more").

**Skip (with reasons)**: our own SRS scheduler (Anki has FSRS native); gamified
XP/leagues (motivation machinery that serves retention metrics, not learning);
video production (lecture tracks already exist); Obsidian export (concept docs
are local plain markdown — open the repo in Obsidian as-is, zero code);
community infra (revisit if the framework is ever published).

---

## 3. The program (S1–S10, in execution order)

### S1 — MOOC bridge: a proven lecture track under every course
Registry gains `kind:` (`book` | `mooc` | `docs` | `tool` | `standard`).
Add one `kind: mooc` entry per course — the closest flagship lecture series
(CS2101 → Roughgarden *Algorithms*; MA1101 → MIT OCW 6.042J; CS2201 → OSTEP
lectures; CS1102 → nand2tetris Coursera/projects; MA1201 → MIT OCW 18.06 …).
Wire each into the course's `sources:`. Site: course pages get a generated
**Lecture track** section (texts stay in the hand-authored reading lists);
library page gets a kind column. Validator: optional enum-check on `kind`.
**Why first:** kills the "no proven teaching content" gap in one pass, no
architecture change — the `kind` field is additive and backward compatible.

### S2 — P0 open-text ingestion
Doc 06 §2 P0 list, unchanged: Dive into Systems, Open Data Structures,
Missing Semester, Pro Git, Book of Proof, Axler, Data Feminism, Design
Justice, Producing OSS, SWE at Google. Download → `library/books/` (only
license-compatible formats), register `status: open`, extract text where legal.

### S3 — Concept-doc machine (METRIC DONE 2026-07-20; docs author via /teach)
/teach authors concept docs as the learner advances; Semester 1 first.
Build script emits per-course concept counts AND unit titles into
`pathway-data.json`; the dashboard shows coverage live: a "concept docs
authored N/M" tile and per-course "N/M docs" chips on unit rows.

### S4 — Mastery model (DONE 2026-07-20)
Progress v3: per-*unit* mastery levels (`unfamiliar → familiar → proficient
→ mastered`) keyed `"<COURSE>/<unit#>"`, round-tripped through progress.yaml
(import merges, max wins); /teach writes levels after quizzes. Dashboard:
course rows expand to unit lists with cycle-dot controls ○◔◑●, plus a
"units ready — mark complete?" nudge when every unit is ≥ proficient. Unit
titles flow from course specs into `pathway-data.json` (parse_units).
Backward compatible: v1/v2 exports import cleanly.

### S5 — SRS pipeline (DONE 2026-07-20)
`scripts/cards.py`: concept docs → Anki-importable TSV (`cards/<COURSE>.tsv`,
regenerate as docs accrete). Cards: key-term paragraphs (first bold span →
"explain: x") and "Check yourself" items. Anki file headers set deck
`OpenCS::<COURSE>`, `#guid column` (stable hashes → re-import updates in
place), `#tags column`. Import via File → Import in Anki ≥ 23.10; enable
FSRS in deck options — scheduling is Anki's job, not ours.

### S6 — Graded proof of work (PILOT DONE 2026-07-20)
`assess/<COURSE>/<NN-unit>/`: `exercises.py` stubs + `test_unit.py` checks;
runner `scripts/grade.py <course> <unit>` (check50 model, stdlib-only —
checks are plain `test_*` functions with asserts, pytest-compatible if the
bigger tool is ever wanted). CS1101 pilot live: 7 units, 21 checks, verified
both directions (stubs fail cleanly, correct solutions pass 21/21). CS1102
reuses nand2tetris's own project tests. Concept docs gain a "Build this"
section pointing at the harness (unit 01 done; extend as units author).
**Next:** harnesses for MA1101/CS1102/MA1102 as those courses start.

### S7 — Dashboard UX: the daily driver
- **Today widget**: next unit to study (first non-mastered unit on the
  frontier), its lecture-track link, its concept doc if authored, Anki
  reminder if cards exist.
- **Streak heatmap**: GitHub-style study-day grid from localStorage activity.
- **Pace projection**: credits completed vs elapsed → projected completion
  date; "at this pace you finish Semester 1 on …".
All three read the existing localStorage/progress.yaml model — no new backend.

### S8 — Proof of work & portfolio (GENERATOR DONE 2026-07-20)
`scripts/portfolio.py [progress.yaml] [-o out.html]`: one self-contained
HTML page (inline CSS, zero deps) — credits bar, completed courses by track,
mastery summary, and project cards from a `projects:` list in progress.yaml
(Fullstack-Open convention: one public repo per project). Host anywhere or
send as-is. Verified against a sample export incl. the missing-file path.

### S9 — Churn defense CI (DONE 2026-07-20)
`scripts/check_links.py`: every registry URL probed weekly
(`.github/workflows/link-check.yml`, Mondays), browser UA, redirect chains
followed (incl. 308), bot-blocks (401/403/429) not flagged as rot; warns on
`status_date` older than 183 days. First live run: 95 URLs, 92 ok,
3 bot-blocked, 0 rot. OSSU needs 190k stars to catch this; we catch it in CI.

### S10 — Cross-audit (one-off report)
Diff OSSU's topic tags against our CS2023 KA matrix; confirm their decade of
community feedback surfaced nothing our design missed. Output:
`planning/08-ossu-cross-audit.md`.

---

## 4. Refactors this authorizes

- `resources/registry.yaml`: additive `kind:` field (+ entries). No breakage.
- `scripts/validate_pathway.py`: enum-check `kind` when present.
- `scripts/build_site_docs.py`: course page groups sources by `kind`; library
  page kind column; emit concept counts in `pathway-data.json`.
- `scripts/grade.py`, `scripts/cards.py`, `assess/`: new, additive.
- progress model: v2 schema, backward-compatible reads.
- Site islands (Dashboard): Today widget, heatmap, projection — client-side
  only, no backend.

Non-goals: mobile app, own SRS scheduler, video, XP/leagues, community infra.

## 5. Turn plan (goal-mode slices)

1. S1 MOOC bridge (registry + validator + site transform) — verifiable: validator green, course pages show lecture tracks.
2. S10 cross-audit (read-only report) + S2 P0 downloads.
3. S7 dashboard widgets (islands code).
4. S5 cards.py + first deck (CS1101 unit 1).
5. S6 grade.py + CS1101 pilot harness.
6. S4 mastery model + S3 concept-doc coverage metric.
