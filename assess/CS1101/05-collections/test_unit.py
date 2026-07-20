"""Checks for CS1101 unit 5 — collections."""

from exercises import dedupe, word_counts, invert_dict


def test_dedupe():
    assert dedupe([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert dedupe([]) == []
    assert dedupe(["a", "a", "b"]) == ["a", "b"]


def test_word_counts():
    assert word_counts("Dog cat, dog.") == {"dog": 2, "cat": 1}
    assert word_counts("one") == {"one": 1}
    assert word_counts("a a! a? a") == {"a": 4}


def test_invert_dict():
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert_dict({}) == {}
