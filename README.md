# Open CS Degree 2026

A complete, modern computer-science degree programme built as
*curriculum-as-data*: an ACM/IEEE CS2023-aligned pathway of courses, units, and
concepts stored in the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md),
delivered to learners by [Matt Pocock's `/teach` skill](https://github.com/mattpocock/skills).

## Repository map

| Path | What it is |
|---|---|
| `planning/00-unknowns-and-planning-prompt.md` | Phase 0 charter: decisions, unknowns, master planning prompt |
| `planning/01-okf-profile.md` | OKF pedagogical frontmatter profile + source-registry contract |
| `planning/02-programme-structure.md` | Human-readable programme: 8 semesters, 3 tracks, capstone |
| `planning/03-coverage-matrix.md` | CS2023 knowledge-area coverage proof |
| `planning/04-pathway-graph.md` | Generated Mermaid rendering of the prerequisite DAG + semester load |
| `curriculum/pathway.yaml` | **Single source of truth**: all courses + prerequisite DAG |
| `curriculum/courses/` | Per-course OKF bundles (Phase 2+) |
| `resources/registry.yaml` | Source registry: every book/resource with license status |
| `resources/outreach/` | Generated permission-request letter drafts, one per book |
| `scripts/validate_pathway.py` | CI validator: DAG integrity, KA coverage, registry refs |

## Working with the source registry

Every cited work lives in `resources/registry.yaml` with a license status
(`open`, `purchase_only`, `purchased`, `approval_needed`, `approval_requested`,
`licensed`, `declined`). To see the outreach queue — the books to seek author or
publisher approval for, or to purchase:

```
python3 scripts/validate_pathway.py --outreach          # print the queue
python3 scripts/validate_pathway.py --outreach-drafts   # write letter drafts to resources/outreach/
```

Each draft in `resources/outreach/` is a ready-to-edit permission-request
letter naming the courses that cite the book. After sending one, set the
registry entry's status to `approval_requested`; when answered, to `licensed`
(record the `terms`) or `declined`. When approval is granted or a book is
bought, update that entry's `status`, `status_date`, and `terms` — the change
applies to every document that cites it.

## Pathway graph

`planning/04-pathway-graph.md` renders the full prerequisite DAG (GitHub
displays the Mermaid diagram inline) plus the semester credit-load table. It is
generated — after editing `curriculum/pathway.yaml`, refresh it with:

```
python3 scripts/validate_pathway.py --mermaid > planning/04-pathway-graph.md
```

CI fails if the graph is stale.

## Validation

```
pip install pyyaml
python3 scripts/validate_pathway.py
```

Runs in CI on every push touching `curriculum/`, `resources/`, or `scripts/`.

## Phase status

- [x] Phase 0 — Charter
- [x] Phase 1 — Scaffold (ontology, pathway DAG, OKF profile, validator, coverage matrix, registry)
- [ ] Phase 2 — Course specs (one page per course + `/teach` mission templates)
- [ ] Phase 3 — Knowledge base (OKF concept documents, in prerequisite order)
- [ ] Phase 4 — `/teach` delivery integration, one-course pilot
- [ ] Phase 5 — Sustainment (refresh policy on `churn`/`last_verified`)
