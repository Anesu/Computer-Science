#!/usr/bin/env python3
"""Generate Anki decks (TSV) from OKF concept documents.

Every concept document under curriculum/<COURSE>/**/*.md becomes cards in
cards/<COURSE>.tsv:

  - **Key-term cards**: a paragraph whose first bold span (`**x**`) names a
    term or claim → front "Explain: x", back = the source paragraph.
  - **Check-yourself cards**: numbered items under "## Check yourself" →
    front = the question, back = a pointer to answer from memory and verify
    against the document section.

Deterministic: cards carry a stable GUID (hash of course + document + heading
+ fingerprint) in column 1, so re-importing into Anki updates in place instead
of duplicating. Import via Anki ≥ 23.10 (File → Import); enable FSRS in the
deck options — scheduling is Anki's job, not ours.

Usage:  python3 scripts/cards.py [--course CS1101]
"""

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "curriculum"
OUT = ROOT / "cards"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
SKIP_HEADINGS = {"where to read more", "check yourself"}


def md_to_html(text: str) -> str:
    """Minimal markdown→HTML for card bodies (Anki renders HTML)."""
    s = html.escape(text.strip())
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", s)
    return s.replace("\n", "<br>")


def guid(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:12]


def doc_cards(cid: str, slug: str, title: str, unit: str, body: str) -> list[list[str]]:
    cards: list[list[str]] = []
    heading = title
    para: list[str] = []
    in_fence = False
    in_check = False

    def flush_paragraph():
        if in_check or not para:
            return
        text = " ".join(x.strip() for x in para).strip()
        para.clear()
        if not text or text.startswith("<!--"):
            return
        m = BOLD_RE.search(text)
        if m and len(m.group(1)) <= 80:
            term = m.group(1)
            where = f" — {heading}" if heading != title else ""
            front = md_to_html(f"{title}{where}: explain — {term}")
            cards.append([
                guid(cid, slug, heading, term),
                front,
                md_to_html(text) + f"<br><br><i>{cid} · unit {unit} · {title}</i>",
                f"opencs {cid} unit{unit}",
            ])

    for line in body.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            para.append(line)
            continue
        if in_fence:
            para.append(line)
            continue
        h = re.match(r"^(#{2,3})\s+(.*)", line)
        if h:
            flush_paragraph()
            heading = h.group(2).strip()
            in_check = heading.lower() == "check yourself"
            continue
        if in_check:
            q = re.match(r"^\d+\.\s+(.*)", line.strip())
            if q:
                question = q.group(1).strip()
                cards.append([
                    guid(cid, slug, "check", question[:60]),
                    md_to_html(f"{title}: {question}"),
                    md_to_html(
                        "Answer from memory, then verify against "
                        f"{cid} unit {unit} — {title} (\"Check yourself\")."),
                    f"opencs {cid} unit{unit} check",
                ])
            continue
        if line.strip().startswith(">"):
            continue  # blockquotes are authoring meta, not card material
        if line.strip() == "":
            flush_paragraph()
        else:
            para.append(line)
    flush_paragraph()
    return cards


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", help="only build this course's deck")
    args = ap.parse_args()

    total_docs = total_cards = 0
    for cdir in sorted(p for p in CURRICULUM.iterdir()
                       if p.is_dir() and p.name != "courses"):
        cid = cdir.name
        if args.course and cid != args.course:
            continue
        cards: list[list[str]] = []
        for path in sorted(cdir.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            m = FRONTMATTER_RE.match(text)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1))
            slug = path.relative_to(cdir).with_suffix("").as_posix()
            cards += doc_cards(cid, slug, str(fm.get("title", slug)),
                               str(fm.get("unit", "?")), text[m.end():])
            total_docs += 1
        if not cards:
            print(f"{cid}: no cards (no concept docs yet)")
            continue
        OUT.mkdir(exist_ok=True)
        deck = OUT / f"{cid}.tsv"
        with open(deck, "w", encoding="utf-8", newline="\n") as f:
            f.write("#separator:tab\n#html:true\n#notetype:Basic\n"
                    f"#deck:OpenCS::{cid}\n#guid column:1\n#tags column:4\n")
            for row in cards:
                f.write("\t".join(cell.replace("\t", " ") for cell in row) + "\n")
        print(f"{cid}: {len(cards)} cards -> {deck.relative_to(ROOT)}")
        total_cards += len(cards)

    print(f"cards: {total_cards} cards from {total_docs} concept docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
