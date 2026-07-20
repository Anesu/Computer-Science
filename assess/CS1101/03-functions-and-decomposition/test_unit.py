"""Checks for CS1101 unit 3 — functions and decomposition."""

from exercises import is_prime, gcd


def test_is_prime():
    assert is_prime(2) is True
    assert is_prime(17) is True
    assert is_prime(1) is False
    assert is_prime(15) is False
    assert is_prime(0) is False


def test_gcd():
    assert gcd(12, 18) == 6
    assert gcd(17, 5) == 1
    assert gcd(100, 10) == 10
