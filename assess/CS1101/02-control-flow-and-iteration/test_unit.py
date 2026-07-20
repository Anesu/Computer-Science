"""Checks for CS1101 unit 2 — control flow and iteration."""

from exercises import fizzbuzz, count_vowels


def test_fizzbuzz_fifteen():
    assert fizzbuzz(15) == [
        1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8, "Fizz", "Buzz",
        11, "Fizz", 13, 14, "FizzBuzz",
    ]


def test_fizzbuzz_keeps_ints():
    assert fizzbuzz(2) == [1, 2]
    assert fizzbuzz(5)[4] == "Buzz"


def test_count_vowels():
    assert count_vowels("hello") == 2
    assert count_vowels("MAZVITA") == 3
    assert count_vowels("rhythm") == 0
