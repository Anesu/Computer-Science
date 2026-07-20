"""CS1101 unit 5 — collections: lists, dicts, sets.

    python3 scripts/grade.py CS1101 05
"""


def dedupe(xs):
    """Return xs without duplicates, preserving first-seen order.
    dedupe([1, 2, 1, 3, 2]) -> [1, 2, 3]"""
    raise NotImplementedError


def word_counts(text):
    """Return a dict mapping each lowercased word to its count.
    Words are split on whitespace; strip .,;:!? from the edges.
    word_counts('Dog cat, dog.') -> {'dog': 2, 'cat': 1}"""
    raise NotImplementedError


def invert_dict(d):
    """Return a new dict with keys and values swapped.
    Assume values are unique and hashable."""
    raise NotImplementedError
