# Arithmetic addendum to FREEZE_V1.md — committed before any executor exists

`source_main`: `e4fee27337d898a4483639365590ccebce1b1be6`.
Parent freeze: `FREEZE_V1.md`, committed at
`research/gmi-833-h-real-scale-nearest-neighbor-v1/FREEZE_V1.md`.

This addendum refines **one sentence** of `FREEZE_V1.md` section 6 and nothing
else. It is committed **before any executor, test, data extraction, fit,
search, or result artifact of this package exists**, in the same custody order
the parent freeze is under, and CI asserts that order for it too.

## What changes

Section 6 registered the rationalisation of a fitting routine's output as
`limit_denominator(10**9)`. That is a best-rational-approximation operator: it
returns an arbitrary denominator no larger than `10**9`. Summing tens of
thousands of such values exactly requires their least common multiple, which
for thousands of arbitrary denominators below `10**9` is a number with
hundreds of thousands of digits. The registered arithmetic would be exact and
computationally unusable, and an exact quantity that cannot be computed is not
evidence.

The rationalisation operator is therefore fixed to the **fixed-denominator**
form at the same registered precision:

```
rationalise(x) = Fraction(round(x * 10**9), 10**9)
```

Every rationalised value then carries a denominator dividing `10**9`, every sum
of such values is exact over a common denominator, and every claimed squared
error is an exact rational computed by integer accumulation over one common
denominator, constructed once.

## What does not change

- The registered precision, `10**9`, is unchanged.
- The rule that the operator is applied **identically to every arm** is
  unchanged, and a test asserts that one operator is used everywhere.
- The rule that floats appear only inside fitting routines, and that no float
  enters any comparison, count, loss or claim, is unchanged.
- **No prediction of section 8 changes.** No falsifier changes. No ecology,
  slice, grammar, scope, class, or claim ceiling changes. This addendum cannot
  turn a failed prediction into a held one: it fixes how a real number is
  written down, not what is compared.

## Consequences that are registered here

- `|rationalise(x) - x| <= 1/(2 * 10**9)` for every value, so the
  rationalisation error of any single arm's prediction is bounded by
  `5 * 10**-10` and is identical in form for every arm.
- Every exact squared error reported by this package has a denominator of the
  form `(d * 10**9)**2` where `d` is the design denominator of its scope, and a
  test asserts that shape.
- A hostile is registered for this addendum: replacing the fixed-denominator
  operator by a per-arm operator must be detected. It is `H_MIXED_RATIONALISER`
  in `RESULT_V1.json`, and it carries an `applicable` flag like every other.
