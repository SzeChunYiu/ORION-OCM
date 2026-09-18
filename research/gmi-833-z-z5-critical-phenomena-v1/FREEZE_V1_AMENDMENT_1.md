# Z5 freeze amendment 1 — the first null was inert and was replaced before its
# numbers were used

Committed **before** the receipt carrying the corrected numbers. `git log` must
show this file added no later than `RESULT_V1.json`.

## What was wrong

The freeze registered a null of `200` randomized scaling laws
`lambda*_rand(A) = eta * p * f(A)`, each to be **caught by the adjudicating
enumeration over the full ladder `A in {2,3,4}`**.

The first implementation of that null compared each drawn `f(A)` against the
closed-form `1 - 1/A` in Python and never touched the enumerated data at all. It
reported `200/200 caught`. It would have reported `200/200 caught` if the
`A`-ary enumeration had been wrong, or had been deleted, or had never been
written: the null was measuring the author's own algebra against itself.

This is the same failure class as the prior Z lane's calibration instrument,
which was frozen at the wrong record level and made its own hostile
undetectable. A null that cannot fail tests nothing, and its number is not
evidence.

Two further assertions in the same first implementation were hardcoded rather
than computed and are corrected here: `zero_error_one_register_machine_exists`
was the literal `True`, and the boundary tie count was the literal `20`.

## The replacement

The null is now **verdict-level and enumeration-grounded**. A claimed threshold
is caught only when the morphology verdict it implies disagrees with the verdict
computed from

- the **enumerated** minimum stateless delay fraction at that alphabet
  (`16`, `729`, `65536` tables at `A = 2, 3, 4`), and
- an **exhibited and scored** zero-error one-register witness,

probed at four registered `(p, eta)` worlds either side of the claimed threshold.
A guard asserts the probe offset is strictly smaller than the gap between the
claimed and enumerated thresholds, so a catch can never be an artifact of the
offset; `guard_failures` is reported and gated at `0`.

The product form `eta * p * (1 - 1/A)` is now *licensed* rather than assumed: the
receipt records that the delay fraction is constant across the whole stateless
family and that `e_now = 0` is attainable, and the gate fails if either is false.

`zero_error_one_register_machine_exists` is now the conjunction of three scored
witnesses, and the tie count is now `boundary_worlds_checked - tie_violations`.

## What the replacement measures

- full ladder: `200/200` caught, `0/200` surviving;
- an `A = 2`-only adjudicator: `186/200` caught, `14` blind, and the blind set is
  **verified** to consist exactly of laws that agree with the enumerated
  threshold at `A = 2`.

The blindness figure is published rather than the blindness being asserted away.
It is the quantitative reason the alphabet ladder exists: the registered scope
`A = 2` cannot, by itself, distinguish the true scaling law from `14/200` of its
randomized rivals.

## Nothing else in the freeze changes

The claim ceiling, the rows, the hypotheses `S4-naive` and `S4-derived`, the
register, the hostiles and the forbidden promotions are unchanged.
