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
| `planning/pathway.tldraw` | Generated interactive tldraw canvas of the prerequisite DAG (open in tldraw Desktop) |
| `planning/pathway.tldr` | Same canvas as flat portable JSON (loads on tldraw.com; no script) |
| `planning/pathway-canvas-script.js` | Document script embedded in the .tldraw: click a course to highlight its prereq chain |
| `planning/04-pathway-graph.md` | Generated companion doc: semester credit-load table + canvas legend |
| `planning/05-frontend-plan.md` | Frontend build plan: Astro static site + Caddy, git-backed progress |
| `curriculum/pathway.yaml` | **Single source of truth**: all courses + prerequisite DAG |
| `curriculum/courses/` | Per-course OKF bundles (Phase 2+) |
| `resources/registry.yaml` | Source registry: every book/resource with license status |
| `site/` | "The University" — Blume docs site (static, offline, serves humans + agents) |
| `scripts/validate_pathway.py` | CI validator: DAG integrity, KA coverage, registry refs |

## Working with the source registry

Every cited work lives in `resources/registry.yaml` with a license status
(`open`, `identified`, `ingested`). 

When a work is `identified`, it means the application has identified it might need it. You can acquire it and change its status to `ingested` when it is in your library. The change applies to every document that cites it.

## Pathway graph

`planning/pathway.tldraw` is the full prerequisite DAG as an interactive
tldraw canvas — one frame per semester, track-colored course boxes, bound
prerequisite arrows, and an embedded document script: click any course to
highlight its prerequisite ancestry plus everything it unlocks; click empty
canvas to reset. Open it with tldraw Desktop (offline).
`planning/pathway.tldr` is the same canvas as flat JSON (loads on tldraw.com,
no script), and `planning/04-pathway-graph.md` is the companion doc with the
semester credit-load table. All three are generated — after editing
`curriculum/pathway.yaml`, refresh them with:

```
python3 scripts/validate_pathway.py --graph
```

CI fails if any of them is stale (the `.tldraw` archive is checked
semantically, since SQLite bytes vary across platforms). The canvas is
regenerated wholesale, so freehand edits to it will be overwritten.

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
