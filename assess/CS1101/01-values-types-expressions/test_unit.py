"""Checks for CS1101 unit 1 — values, types, and expressions."""

from exercises import type_name, to_number, repeat_word, division_types


def test_type_name_basics():
    assert type_name(42) == "int", "42 is an int"
    assert type_name(3.5) == "float", "3.5 is a float"
    assert type_name("mazvita") == "str", "'mazvita' is a str"


def test_type_name_bool_is_not_int():
    assert type_name(True) == "bool", "True is a bool, not an int"
    assert type_name(False) == "bool", "False is a bool, not an int"


def test_to_number_int_and_float():
    assert to_number("42") == 42 and isinstance(to_number("42"), int)
    assert to_number("3.5") == 3.5 and isinstance(to_number("3.5"), float)


def test_to_number_rejects_garbage():
    try:
        to_number("abc")
    except ValueError:
        return
    raise AssertionError("expected ValueError for 'abc'")


def test_repeat_word():
    assert repeat_word("ab", 3) == "ababab"
    assert repeat_word("na", 4) == "nananana"
    assert repeat_word("x", 1) == "x"


def test_division_types():
    assert division_types(7, 2) == ("float", "int")
    assert division_types(8, 2) == ("float", "int"), "8 / 2 is 4.0 — still a float"
