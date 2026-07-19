---
title: "Values, types, and expressions"
course: CS1101
unit: 1
churn: evergreen
last_verified: 2026-07-19
sources: [composing-programs, think-python]
prerequisites: []
---

# Values, types, and expressions

> **Pilot concept document** — the first Phase 3 page, proving the
> curriculum-to-site pipeline end to end. Unit 1 of
> [CS1101 — Programming Fundamentals](../course.md).

Every program, no matter how large, is built from three things you can learn
in an afternoon: **values** (the data), **types** (what kind of data), and
**expressions** (recipes that combine values into new values). Master how
these three interact and the rest of programming becomes arrangement rather
than mystery.

## Values are the nouns

A value is a piece of data the machine can hold: the integer `42`, the text
`"mazvita"`, the truth-value `True`. Values exist independently of any name
you might give them — `42` is `42` whether or not a variable points at it.

## Every value has exactly one type

The type determines what operations make sense. Integers divide; strings
concatenate; booleans negate. Ask Python directly:

```python
>>> type(42)
<class 'int'>
>>> type(3.5)
<class 'float'>
>>> type("mazvita")
<class 'str'>
>>> type(True)
<class 'bool'>
```

Two consequences worth internalizing now:

1. **Operations are type-directed.** `+` on two ints is addition; `+` on two
   strings is concatenation; `+` on an int and a string is an error. The
   operator did not change — the types chose the behavior.
2. **Conversion is explicit.** `int("42")` and `str(42)` cross the boundary
   deliberately. Languages that convert silently for you are making a bet on
   your intent; Python mostly refuses to.

## Expressions are the sentences

An expression is anything that *evaluates to a value*: `2 + 3`, `len("cs")`,
`(1 + 2) * (3 + 4)`. Evaluation is mechanical and inside-out — subexpressions
first, then the operations that combine them. You can always ask "what value
does this stand for?" and reduce step by step:

```python
(2 + 3) * len("abcd")
# → 5 * len("abcd")
# → 5 * 4
# → 20
```

That reduction habit — evaluating in your head, one step at a time — is the
single most useful skill of this unit. It is how you predict what code does
*before* running it, and how you find the exact step where reality diverged
from your prediction when debugging.

## Names are labels, not boxes

An assignment like `x = 2 + 3` first evaluates the right side to a value,
then makes the name `x` refer to it. Names have no type of their own — they
borrow the type of whatever value they currently point at. Reassigning a
name never changes the value it used to point at; it just moves the label.

## Common misconceptions

<a id="mc-names-are-boxes"></a>
**"A variable is a box that contains a value."** — Wrong: a name is a label
*pointing at* a value; assignment moves the label, never mutates the old
value, and two names can label the same value. The box model breaks the
moment aliasing appears (lists, unit 5). *Probe:* after `a = [1]` then
`b = a`, what does `b` see when `a.append(2)` runs — and would your answer
change for `a = 1; b = a; a = 2`?

<a id="mc-plus-means-add"></a>
**"`+` means addition."** — Wrong: the operands' types choose the behavior;
`+` concatenates strings, adds ints, and errors across the boundary. The
operator has no meaning until the types are known. *Probe:* predict `"3" + "4"`,
`3 + 4`, and `"3" + 4` — and say which fact decided each outcome.

<a id="mc-division-keeps-type"></a>
**"Dividing two ints gives an int."** — Wrong in Python: `/` always yields a
`float` (`7 / 2 == 3.5`); floor division `//` is the operation that stays in
int-land. *Probe:* what type is `8 / 2`, and why is the answer not `int`?

<a id="mc-expressions-run-left-to-right"></a>
**"Python evaluates an expression in one go / left to right."** — Evaluation
is mechanical and *inside-out*: subexpressions reduce to values first, then
the combining operation applies. Getting this wrong makes debugging by
prediction impossible. *Probe:* reduce `len("ab") * (2 + 1)` one step per
line, naming the rule used at each step.

## Check yourself

1. Reduce `3 * (2 + len("abc")) - 1` to a value, one step per line.
2. What type is the value of `7 / 2`? Of `7 // 2`? Explain the difference.
3. After `a = "3"` then `b = a * 2`, what is `b` and what is its type? Why
   is it not `6`?
4. Why does `"credits: " + 4` raise an error while `"credits: " + str(4)`
   does not? What decided?

## Where to read more

- *Composing Programs* §1.1–1.2 — expressions and the elements of
  programming.
- *Think Python* (3e) ch. 1–2 — values, types, variables, expressions.
