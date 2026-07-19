---
course: CS1101
type: project
ai_mode: ai-paired
---

# CS1101 — Course project: `wordstats`

Build a command-line text-analysis tool, `wordstats`, in Python with no
third-party dependencies. It reads one or more text files and reports word
frequencies, vocabulary richness, and per-file comparisons. The project is
`ai-paired`: work with an AI assistant as you will professionally — but the
transcript is part of the submission, and the defense (see
[exam.md](exam.md)) assumes every line is yours to explain.

## Functional requirements

1. `wordstats count FILE...` — total words, unique words, and the top-10
   most frequent words with counts, case-insensitive, punctuation stripped.
2. `wordstats compare FILE1 FILE2` — words unique to each file and the ten
   most frequent shared words.
3. `wordstats stopwords FILE --stopwords LIST` — as `count`, excluding the
   stopwords in `LIST` (one word per line).
4. Malformed input never crashes the tool: unreadable files produce a
   one-line error on stderr and a non-zero exit code; undecodable lines are
   skipped and counted, with the skip count reported.
5. Code is decomposed into tested functions — tokenization, counting,
   reporting are separate and importable (`from wordstats import tokenize,
   count_words, ...`); the CLI layer contains no logic.

## Submission

A repository (or directory in your workspace) containing `wordstats.py` (or a
small package), `tests/` with your own pytest suite, a `README.md` with usage
examples, and `transcript.md` — the AI-pairing transcript with a short note on
one place you rejected or fixed the assistant's output.

## Acceptance criteria

Run by the `/reviewer` skill, in order, before any code reading. Every
command must behave as stated:

- `python -m pytest tests/ -q` — the learner's own suite: **≥ 10 tests, all
  passing**, covering tokenization edge cases (empty file, punctuation-only,
  unicode) and at least one error path.
- `python wordstats.py count sample.txt` — exits 0; output lists total,
  unique, and exactly 10 ranked `word count` lines for a known sample, with
  deterministic tie-breaking (alphabetical) so output is reproducible.
- `python wordstats.py count missing.txt` — exits non-zero; exactly one
  error line on stderr; nothing on stdout.
- `python wordstats.py compare a.txt b.txt` — sections for unique-to-A,
  unique-to-B, and shared top-10, verified against a hand-computable fixture
  pair provided by the reviewer at review time.
- `python -c "from wordstats import tokenize, count_words"` — exits 0: logic
  is importable, not trapped in the CLI.
- Reviewer runs their own adversarial fixture (crafted at review time — mixed
  case, hyphens, apostrophes, an undecodable byte sequence) through `count`;
  documented behavior, no traceback.
- `transcript.md` exists and contains at least one identified-and-corrected
  assistant defect (the `cs1101.ai-practice.verify-generated` evidence).
