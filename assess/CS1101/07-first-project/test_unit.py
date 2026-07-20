"""Checks for CS1101 unit 7 — a first project."""

import tempfile
from pathlib import Path

from exercises import analyze_text


def _write(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(text)
        return f.name


def test_analyze_text_basic():
    path = _write("Dog cat, dog.\nThe cat sat.\n")
    try:
        assert analyze_text(path) == {"lines": 2, "words": 6, "unique": 4}
    finally:
        Path(path).unlink()


def test_analyze_text_empty_lines():
    path = _write("one two\n\nthree\n")
    try:
        assert analyze_text(path) == {"lines": 3, "words": 3, "unique": 3}
    finally:
        Path(path).unlink()
