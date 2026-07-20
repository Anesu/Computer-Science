"""CS1101 unit 7 — a first project: text analyzer.

Integrates everything so far: files, strings, collections, functions.

    python3 scripts/grade.py CS1101 07
"""


def analyze_text(path):
    """Read the file at `path` and return a dict:
        {"lines": <number of lines>,
         "words": <total word count>,
         "unique": <number of distinct lowercased words>}
    Words are split on whitespace; strip .,;:!? from word edges and
    lowercase them before counting distinct ones. Empty lines still
    count as lines but contribute no words."""
    raise NotImplementedError
