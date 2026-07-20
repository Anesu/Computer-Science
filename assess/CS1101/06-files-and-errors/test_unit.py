"""Checks for CS1101 unit 6 — files and errors."""

import tempfile
from pathlib import Path

from exercises import safe_divide, read_numbers


def test_safe_divide_normal():
    assert safe_divide(7, 2) == 3.5
    assert safe_divide(8, 2) == 4.0


def test_safe_divide_never_raises():
    assert safe_divide(1, 0) is None
    assert safe_divide("a", 2) is None


def test_read_numbers_skips_bad_lines():
    with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False) as f:
        f.write("1.5\nhello\n2\n\n-3.5\n")
        path = f.name
    try:
        assert read_numbers(path) == [1.5, 2.0, -3.5]
    finally:
        Path(path).unlink()
