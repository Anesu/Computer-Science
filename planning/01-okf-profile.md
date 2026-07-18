# OKF Pedagogical Profile v1.0

This document extends the [Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
with the frontmatter fields this curriculum requires. It is the schema contract
for every document in `curriculum/`. The CI validator enforces the required
fields; changing this profile is a charter-level decision.

## Document types and repository layout

OKF's native units map onto our ontology like this:

| Ontology level | OKF construct | Location |
|---|---|---|
| Programme | the whole repo (bundle of bundles) | `curriculum/` |
| Course | **bundle (forest)** — one directory | `curriculum/courses/<course-id>/` |
| Unit | **tree** — subdirectory with a primary doc | `curriculum/courses/<course-id>/units/<nn>-<slug>/` |
| Concept | **document** — one markdown file | `.../units/<nn>-<slug>/<concept-slug>.md` |

Each course directory also contains:

- `course.md` — the course-level document (spec, Phase 2 deliverable)
- `mission.md` — the `/teach` mission template for this course
- `project.md` — the course project with acceptance criteria

## Frontmatter schema

### Concept document (required fields)

```yaml
---
id: cs2201.processes.context-switching   # globally unique, dot-namespaced
type: concept
title: Context Switching
course: CS2201
unit: 02-processes
learning_objectives:                     # observable, assessable outcomes
  - Explain what state must be saved and restored during a context switch
  - Measure context-switch overhead with a microbenchmark
prerequisites:                           # IDs only — concept, unit, or course IDs
  - CS1202
  - cs2201.processes.process-lifecycle
level: core                              # core | advanced | extension
estimated_hours: 2
assessment: quiz+lab                     # quiz | quiz+lab | project | none
churn: evergreen                         # evergreen | stable | volatile
sources:                                 # registry IDs from resources/registry.yaml
  - ostep
  - csapp
last_verified: 2026-07-18
confidence: high                         # high | medium | low (agent-authored, pending review)
---
```

### Course document (`course.md`)

```yaml
---
id: CS2201
type: course
title: Operating Systems
semester: 4
credits: 4
knowledge_areas: [OS]                    # CS2023 KA codes, primary first
prerequisites: [CS2102, CS1202]
track: core                              # core | ai | systems | security | elective
project: project.md
mission: mission.md
churn: stable
last_verified: 2026-07-18
---
```

### `/teach` mission template (`mission.md`)

Plain markdown consumed at delivery time. Structure:

1. **Mission statement** — what the learner will be able to do (from learning objectives)
2. **Assumed background** — rendered from the prerequisite closure
3. **Resource list** — resolved from the union of unit `sources`, filtered by
   registry license status (see below)
4. **Mastery criteria** — how the learner and `/teach` know the course is done
   (quiz thresholds + project acceptance criteria)

## Source registry contract

All `sources` values are IDs into `resources/registry.yaml`. A concept document
never embeds bibliographic details or license terms — those live only in the
registry, so a status change (e.g. approval granted) applies everywhere at once.

### Registry entry schema

```yaml
- id: ostep
  title: "Operating Systems: Three Easy Pieces"
  authors: [Remzi Arpaci-Dusseau, Andrea Arpaci-Dusseau]
  publisher: Arpaci-Dusseau Books
  year: 2023
  url: https://pages.cs.wisc.edu/~remzi/OSTEP/
  license: free-online                   # free text description of the default terms
  status: open                           # see lifecycle below
  status_date: 2026-07-18
  contact: null                          # author/publisher contact point for outreach
  terms: null                            # recorded terms once licensed/purchased
  used_in: [CS2201]                      # maintained by tooling, not by hand
  priority: high                         # high | medium | low — outreach ordering
```

### License status lifecycle

```
open ────────────────────────────► (usable now, attribution required)
purchase_only ──(book bought)────► purchased
approval_needed ─(outreach sent)─► approval_requested ─┬─► licensed
                                                       └─► declined ─► cite-only
```

| Status | Meaning | What curriculum docs may do |
|---|---|---|
| `open` | Openly licensed or freely published by the author | Link, cite, synthesize; excerpt within the license terms |
| `purchase_only` | Commercial work, no special arrangement | Link and cite; direct the learner to buy it |
| `purchased` | A copy has been bought for the programme | As above, plus the learner-owned copy is a first-class resource in missions |
| `approval_needed` | We want deeper use (excerpts/adaptation); outreach not yet started | Cite-only until resolved |
| `approval_requested` | Outreach sent (`status_date` = when) | Cite-only until resolved |
| `licensed` | Author/publisher granted terms (recorded in `terms`) | Whatever `terms` permits |
| `declined` | Approval refused | Cite-only, permanently |

### Outreach queue

The owner's approval workflow is a registry query, not a separate document:

```
python3 scripts/validate_pathway.py --outreach
```

lists every `approval_needed` / `approval_requested` entry ordered by
`priority`, with contact points — the to-do list for seeking approvals and
logging purchases.

## Validation rules (enforced by `scripts/validate_pathway.py`)

1. Every `prerequisites` entry resolves to an existing course/unit/concept ID.
2. The prerequisite graph is acyclic.
3. A course's prerequisites live in strictly earlier semesters.
4. Every CS2023 knowledge area is claimed by at least one **core** course.
5. Every `sources` entry resolves to a registry ID.
6. Required frontmatter fields are present and enum values are legal.
7. `volatile` documents whose `last_verified` is older than 6 months are flagged
   (warning, not failure) — the Phase 5 refresh queue.
