"""Checks for CS1101 unit 4 — recursion."""

from exercises import fact, fib


def test_fact():
    assert fact(0) == 1
    assert fact(1) == 1
    assert fact(5) == 120


def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    assert fib(15) == 610
