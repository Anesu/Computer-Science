# CS Curriculum Project — Pre-Planning Analysis

**Purpose of this document:** before writing the master planning prompt, surface the
known unknowns (decisions we know we haven't made) and the unknown unknowns
(constraints and facts the original plan didn't account for). The improved planning
prompt at the bottom incorporates all of them.

**Date:** 2026-07-18
**Status:** Awaiting decisions on the items in §1 before Phase 1 begins.

---

## 0. Grounding: what the two named dependencies actually are

These matter because both are more opinionated than the plan assumed.

### Matt Pocock's `/teach` skill ([mattpocock/skills](https://github.com/mattpocock/skills))

- It is **mission-driven and learner-adaptive**: it captures a learning "mission,"
  finds high-quality resources, generates interactive HTML lessons (audio + quizzes),
  and keeps a **learning record** of one learner's progress.
- It **generates its own lessons** from resources; it is not a player for
  pre-authored courseware. Since v1.0.1 it is "reuse-first" (reads existing
  components before authoring), but the unit of input is *resources + mission*,
  not finished lesson files.
- **Implication:** our scaffold should not produce finished lessons. It should
  produce what `/teach` consumes: per-subject **mission templates**, **curated
  resource lists**, **prerequisite context**, and **mastery criteria**. `/teach`
  does the last-mile lesson generation, personalized to the learner.

### Open Knowledge Format ([OKF spec, Google Cloud 2026](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md))

- Markdown files + YAML frontmatter. One **concept per document**; a directory of
  a primary markdown file plus assets is a **tree**; related trees form a
  **bundle ("forest")**. Designed so any AI agent can consume organizational
  knowledge without custom integration.
- It is a **knowledge-context format, not a courseware format**. v0.1 has no
  native fields for learning objectives, prerequisites, difficulty, assessment,
  or estimated hours.
- **Implication:** we must define an **OKF profile** (a documented frontmatter
  extension) for pedagogical metadata *before* scraping begins — otherwise every
  document written early gets re-migrated later.

---

## 1. Known unknowns — decisions the plan needs but hasn't made

| # | Decision | Why it changes everything downstream | Recommended default |
|---|----------|--------------------------------------|---------------------|
| 1 | **Who is the learner?** You personally, a public audience, or a cohort? | `/teach` is single-learner and keeps a personal learning record. Public/cohort use needs a separation between shared curriculum (this repo) and per-learner state (outside it). | Design curriculum as learner-agnostic; treat learner state as external to the repo. |
| 2 | **Benchmark standard.** "Top universities" is not a spec. | Without a canonical spine, coverage arguments are unfalsifiable. | Use **ACM/IEEE CS2023** curriculum guidelines as the spine; cross-map against MIT, CMU, Stanford, Berkeley, Cambridge, ETH published curricula as a validation layer. |
| 3 | **Scope.** Full BSc-equivalent (incl. mathematics, writing, ethics) or CS-core only? | Mathematics (discrete math, linear algebra, probability, calculus) is ~25–30% of a real CS degree and is the most common omission in self-taught pathways. | Full BSc-equivalent minus general-education filler; mathematics fully in scope. |
| 4 | **Terminology ontology.** "Courses, units, subjects" mean *opposite* things in US vs UK/AU/ZW usage. | Every file path, frontmatter field, and prompt will encode this hierarchy. Must be fixed once, first. | Define explicitly: **Programme → Course (≈ semester course, e.g. "Operating Systems") → Unit (≈ 1–2 week module) → Subject/Concept (one OKF document)**. |
| 5 | **Depth / time budget.** Credit-hour equivalence? Total hours? | Determines how many units per course and how aggressively to prune. | Target ~120 US credit hours equivalent (~3,600 learning hours), explicitly tagged per course so it can be scaled down. |
| 6 | **Assessment model.** Quizzes only, or projects/capstones with acceptance criteria? | `/teach` quizzes are formative (recall). Graduate-level competence is demonstrated through projects. | Every course gets a project spine with machine-verifiable acceptance criteria (test suites, benchmarks) where possible; programme ends in a capstone. |
| 7 | **Specialization tracks.** Pure generalist degree, or elective tracks (AI/ML, systems, security, data)? | Affects the shape of years 3–4 of the pathway DAG. | Common core (years 1–2) + 2–3 defined tracks + free electives, mirroring CS2023's core/elective split. |
| 8 | **"Modern 2026" delta.** Which contemporary topics are *core* vs *elective*? AI-assisted software engineering, LLM application development, MLOps, Rust/memory safety, distributed systems, privacy engineering, quantum basics… | This is the project's headline value ("what a 2026 graduate needs") and also its highest-churn content. | AI-assisted engineering practice woven into *every* programming course (not siloed); LLM app dev + applied security promoted to core; quantum/blockchain elective. |
| 9 | **Definition of done for the scaffold phase.** | "Phased approach" without phase gates drifts. | Scaffold is done when: ontology fixed, full pathway DAG with prerequisites exists, every course has a one-page spec, and the OKF profile is documented — before any content scraping starts. |

---

## 2. Unknown unknowns — things the original plan didn't account for

1. **You don't need to reverse-engineer top universities — a canonical body of
   knowledge already exists.** ACM/IEEE **CS2023** defines the discipline in
   knowledge areas with explicit core-hour allocations, and it's what the top
   departments themselves benchmark against. This *flips the scraping phase*:
   instead of "discover the structure by scraping universities," the structure
   comes from CS2023, and scraping becomes *mapping curated resources onto a
   known skeleton* — a much more tractable, verifiable task.

2. **`/teach` and "university-standard fixed curriculum" are in tension.**
   `/teach` adapts to one learner and authors its own lessons. If we pre-author
   rigid lesson content, we fight the tool. The resolution (see §0) is that the
   repo's deliverable is *curriculum-as-data* — mission templates, resource
   lists, prerequisite graph, mastery criteria — and `/teach` is the delivery
   runtime. This changes what "content" means in every later phase.

3. **OKF needs a pedagogical profile defined up front.** (See §0.) Fields we'll
   need that OKF v0.1 doesn't specify: `learning_objectives`, `prerequisites`
   (IDs, not prose), `level`, `estimated_hours`, `assessment`, `sources`,
   `last_verified`, `confidence`. Deciding this schema is a Phase-1 gate, not a
   detail.

4. **The pathway is a DAG, not a list.** "Graduated pathway" implies linear
   ordering, but real prerequisites form a directed acyclic graph (e.g. Operating
   Systems needs Architecture *and* C-level programming; ML needs Linear Algebra
   *and* Probability *and* Python). If prerequisite edges aren't first-class data
   in the OKF frontmatter, `/teach` cannot sequence correctly and electives can't
   branch. The scaffold must model edges explicitly and machine-checkably
   (no cycles, no dangling references — CI-verifiable).

5. **Licensing and copyright constrain the scraping phase.** MIT OCW is
   CC BY-NC-SA; many top resources (CLRS, SICP editions, commercial courses) are
   copyrighted. A public GitHub repo cannot hold copies of scraped content.
   Policy: OKF documents contain **original synthesis + links/citations to
   resources**, never copied content. This also happens to be what `/teach`
   wants (resource lists, not mirrored text).

6. **Scale forces a quality-control harness.** ~40 courses × ~10 units × several
   concepts each ≈ **thousands of OKF documents**. No human reviews that by
   hand, and agent-generated content at that scale *will* contain confident
   errors. The plan needs a review loop as a first-class phase: rubric-based
   adversarial verification agents, coverage checks against the CS2023 spine,
   and spot-check sampling — not "generate and trust."

7. **2026 content rots in months.** The most valuable material (AI tooling,
   frameworks, security practice) has the shortest half-life. Every document
   needs `last_verified` + `sources` frontmatter and a scheduled refresh policy;
   evergreen theory (algorithms, math) should be explicitly tagged as
   low-churn so refresh effort targets the volatile 20%.

8. **Assessment validity gap.** Quiz-passing ≠ graduate competence. Without a
   project/capstone spine with real acceptance criteria, the programme certifies
   recall, not ability. (Promoted to decision #6 above.)

9. **The phases themselves were undefined.** "Scraping phase" was named but its
   inputs, outputs, and gate were not, and the phases before/after it were
   implicit. Proposed phase plan is in the prompt below.

10. **State separation.** `/teach`'s learning record lives in the learner's
    Claude environment, not in this repo. Conflating curriculum (shared,
    versioned) with learner progress (personal, mutable) would break both.

---

## 3. The improved planning prompt

> Use this (edited to taste) as the master prompt for the next session/phase.
> Bracketed items are the §1 decisions — fill or accept the defaults.

---

**PROJECT: Open CS Degree 2026 — curriculum-as-data for agent-delivered learning**

Build a complete, modern computer-science degree programme in this repository as
structured data, delivered to learners at runtime by Matt Pocock's `/teach`
skill. The repo is the *curriculum*; `/teach` is the *classroom*; learner state
stays outside the repo.

**Fixed decisions (do not re-litigate):**
- Ontology: Programme → Course (semester-scale, e.g. "Operating Systems") →
  Unit (1–2 week module) → Concept (one OKF document). [confirm]
- Spine: ACM/IEEE CS2023 knowledge areas, validated by cross-mapping against
  [MIT, CMU, Stanford, Berkeley, Cambridge, ETH] published curricula.
- Scope: full BSc-equivalent including mathematics (discrete math, linear
  algebra, probability/statistics, calculus); ~[120] credit-hours equivalent;
  common core (years 1–2) + tracks [AI/ML, Systems, Security] (years 3–4)
  + capstone.
- 2026 delta: AI-assisted software engineering woven into every programming
  course; LLM application development and applied security in core;
  [quantum, blockchain] as electives.
- Content policy: OKF documents contain original synthesis and *citations/links*
  to external resources — never copied copyrighted text. Prefer open resources
  (OCW, open textbooks, official docs) in resource lists.
- Storage format: OKF v0.1 (markdown + YAML frontmatter, concept-per-document,
  bundle-per-course) extended by our documented pedagogical profile with
  required fields: `id`, `title`, `learning_objectives`, `prerequisites`
  (list of concept/course IDs), `level`, `estimated_hours`, `assessment`,
  `churn` (evergreen|stable|volatile), `sources`, `last_verified`.
- Prerequisites are a DAG with machine-checkable integrity (no cycles, no
  dangling IDs); a CI script validates this on every commit.
- Assessment: every course defines a project with verifiable acceptance
  criteria (auto-gradable where possible); programme ends in a capstone.
  `/teach` quizzes are formative only.

**Phases (each ends with a committed, reviewable gate artifact):**

- **Phase 0 — Charter (this document).** Decisions locked. *Gate: this file merged.*
- **Phase 1 — Scaffold.** Define the OKF pedagogical profile
  (`planning/okf-profile.md`); enumerate all courses mapped to CS2023 knowledge
  areas; build the full prerequisite DAG; write the DAG validator (CI). *Gate:
  a rendered pathway graph + course list that passes validation, plus a coverage
  matrix showing every CS2023 core hour is assigned to exactly one course.*
- **Phase 2 — Course specs.** One-page spec per course: description, learning
  objectives, unit breakdown, project definition with acceptance criteria,
  `/teach` mission template. *Gate: all specs pass a rubric review by an
  independent verification pass (adversarial agent review, not self-review).*
- **Phase 3 — Knowledge base ("scraping").** For each unit, populate OKF concept
  documents: original synthesis + curated resource list (open-licensed
  preferred), full frontmatter. Work course-by-course in prerequisite order so
  early courses are usable while later ones are in progress. *Gate per course:
  coverage check against its spec + adversarial fact-verification sampling.*
- **Phase 4 — Delivery integration.** Wire `/teach`: mission templates that
  point at the course's OKF bundle, prerequisite context injection, mastery
  criteria. Pilot one full course end-to-end as a learner before scaling.
  *Gate: one course completed via `/teach` with the pilot's friction log
  addressed.*
- **Phase 5 — Sustainment.** Refresh policy keyed on `churn` + `last_verified`
  (scheduled sweep of volatile documents); contribution guide; versioned
  releases of the curriculum.

**Working rules:**
- Never start phase N+1 before phase N's gate artifact is committed.
- All generated content at scale gets an independent verification pass; report
  what was sampled and what failed, not just successes.
- When a decision arises that isn't covered above, add it to the charter with
  rationale rather than deciding silently inline.

---

## Sources

- [mattpocock/skills — Skills for Real Engineers](https://github.com/mattpocock/skills)
- [Learn Anything With My /teach Skill — aihero.dev](https://www.aihero.dev/learn-anything-with-my-teach-skill)
- [OKF specification — GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [How the Open Knowledge Format can improve data sharing — Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)
