"""CS1101 unit 1 — values, types, and expressions.

Fill in each function. Run the checks:
    python3 scripts/grade.py CS1101 01
"""


def type_name(v):
    """Return the name of v's type as a string: 'int', 'float', 'str',
    or 'bool'. Careful: booleans are a subtype of int in Python."""
    raise NotImplementedError


def to_number(s):
    """Convert a string to a number: '42' -> 42 (int), '3.5' -> 3.5 (float).
    Raise ValueError if the string is neither an int nor a float literal."""
    raise NotImplementedError


def repeat_word(word, n):
    """Return the string `word` repeated `n` times (no separator).
    repeat_word('na', 4) -> 'nananana'"""
    raise NotImplementedError


def division_types(a, b):
    """Return a pair (t1, t2) of type NAMES: t1 is the type of a / b,
    t2 is the type of a // b. Example: (8, 2) -> ('float', 'int')."""
    raise NotImplementedError
