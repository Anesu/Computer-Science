#!/usr/bin/env python3
"""Generate a shareable portfolio page from progress.yaml (planning/07, S8).

Reads the learner's exported progress (dashboard → Export progress.yaml)
plus the curriculum data, and emits one self-contained HTML file (inline
CSS, no dependencies) — host it anywhere or send it as-is.

progress.yaml may additionally carry a projects list (the proof-of-work
convention, Fullstack-Open style — one public repo per project):

    projects:
      - name: nand2tetris CPU
        url: https://github.com/you/nand2tetris
        course: CS1102
        blurb: Built a working CPU from NAND gates.

Usage:  python3 scripts/portfolio.py [progress.yaml] [-o portfolio/index.html]
"""

import argparse
import html
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATHWAY = ROOT / "curriculum" / "pathway.yaml"

CSS = """
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; background: #0b1220; color: #e2e8f0;
         margin: 0; padding: 40px 20px; }
  main { max-width: 860px; margin: 0 auto; }
  h1 { margin: 0 0 4px; font-size: 28px; }
  h2 { margin: 28px 0 10px; font-size: 18px; color: #93c5fd; }
  .sub { opacity: .7; margin: 0 0 18px; }
  .bar { height: 10px; border-radius: 5px; background: #1e293b; overflow: hidden;
         margin: 8px 0 4px; }
  .bar i { display: block; height: 100%; background: #3b82f6; }
  .stats { display: flex; gap: 24px; flex-wrap: wrap; margin: 12px 0 4px; }
  .stats b { font-size: 22px; }
  .stats span { display: block; font-size: 12.5px; opacity: .7; }
  table { width: 100%; border-collapse: collapse; font-size: 14.5px; }
  td, th { text-align: left; padding: 6px 8px; border-bottom: 1px solid #1e293b; }
  th { font-size: 12px; text-transform: uppercase; letter-spacing: .05em;
       opacity: .6; }
  .proj { border: 1px solid #1e293b; border-radius: 10px; padding: 12px 16px;
          margin: 10px 0; background: #0f172a; }
  .proj a { color: #93c5fd; text-decoration: none; font-weight: 600; }
  .proj small { display: block; opacity: .75; margin-top: 4px; }
  footer { margin-top: 36px; font-size: 12.5px; opacity: .55; }
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("progress", nargs="?", default="progress.yaml")
    ap.add_argument("-o", "--out", default="portfolio/index.html")
    args = ap.parse_args()

    pfile = Path(args.progress)
    if not pfile.exists():
        print(f"{pfile} not found - export it from the dashboard first "
              f"(Sync -> Export progress.yaml).")
        return 2
    prog = yaml.safe_load(open(pfile, encoding="utf-8")) or {}
    pathway = yaml.safe_load(open(PATHWAY, encoding="utf-8"))
    courses = {c["id"]: c for c in pathway["courses"]}
    target = pathway["programme"]["target_credits"]

    done_ids = sorted(prog.get("completed_courses", []) or [])
    done = [courses[i] for i in done_ids if i in courses]
    credits = sum(c["credits"] for c in done)
    mastery = prog.get("mastery", {}) or {}
    levels = [0, 0, 0, 0]
    for v in mastery.values():
        if isinstance(v, int) and 0 <= v <= 3:
            levels[v] += 1
    projects = prog.get("projects", []) or []
    learner = prog.get("learner") or "anonymous"
    esc = html.escape

    rows = []
    for track, label in (("core", "Core"), ("ai", "AI track"),
                         ("systems", "Systems track"),
                         ("security", "Security track"),
                         ("elective", "Electives")):
        group = [c for c in done if c["track"] == track]
        if not group:
            continue
        rows.append(f'<tr><th colspan="3">{label}</th></tr>')
        for c in group:
            rows.append(f'<tr><td>{c["id"]}</td><td>{esc(c["title"])}</td>'
                        f'<td>{c["credits"]} cr</td></tr>')

    proj_html = "\n".join(
        f'<div class="proj"><a href="{esc(p.get("url", "#"))}">'
        f'{esc(p.get("name", "project"))}</a> · {esc(p.get("course", ""))}'
        f'<small>{esc(p.get("blurb", ""))}</small></div>'
        for p in projects)

    pct = min(100, round(credits / target * 100))
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(learner)} — Open CS Degree 2026</title>
<style>{CSS}</style></head><body><main>
<h1>{esc(learner)}</h1>
<p class="sub">Open CS Degree 2026 — self-taught computer-science degree</p>
<div class="bar"><i style="width:{pct}%"></i></div>
<div class="stats">
  <div><b>{credits} / {target}</b><span>credits</span></div>
  <div><b>{len(done)}</b><span>courses completed</span></div>
  <div><b>{levels[2] + levels[3]}</b><span>units ≥ proficient</span></div>
  <div><b>{levels[3]}</b><span>units mastered</span></div>
</div>
<h2>Projects</h2>
{proj_html or '<p class="sub">Projects land here — add them under <code>projects:</code> in progress.yaml.</p>'}
<h2>Completed courses</h2>
<table>{''.join(rows) or '<tr><td>No courses completed yet.</td></tr>'}</table>
<footer>Generated {date.today().isoformat()} by scripts/portfolio.py ·
Open CS Degree 2026</footer>
</main></body></html>
"""

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"portfolio: {len(done)} courses, {len(projects)} projects, "
          f"{credits}/{target} credits -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
