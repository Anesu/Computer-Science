# Pathway Graph

<!-- GENERATED FILE — do not edit by hand.
     Regenerate: python3 scripts/validate_pathway.py --graph
     CI fails if this file is stale relative to curriculum/pathway.yaml. -->

The prerequisite DAG is rendered as a tldraw canvas. Open
**[`pathway.tldraw`](pathway.tldraw)** with tldraw Desktop — it embeds
[`pathway-canvas-script.js`](pathway-canvas-script.js), so the canvas is
interactive out of the box: click any course to highlight its full
prerequisite ancestry plus everything it unlocks; click empty canvas to
reset. ([`pathway.tldr`](pathway.tldr) is the same canvas as flat portable
JSON, without the script — it also loads on tldraw.com.)

One frame per earliest-availability semester; an arrow A → B means A is a
prerequisite of B. Colors: blue = core, pink = AI track, green = Systems
track, yellow = Security track, gray = general elective.

Everything is generated from `curriculum/pathway.yaml` — edit the YAML, then
regenerate; freehand edits to the canvas will be overwritten.

## Semester load (core credits)

Track-elective slots (3 credits each) sit on top of semesters 6–8; free
elective in semester 8.

| Semester | Core credits |
|---|---|
| 1 | 15 |
| 2 | 15 |
| 3 | 15 |
| 4 | 14 |
| 5 | 14 |
| 6 | 10 |
| 7 | 7 |
| 8 | 5 |
