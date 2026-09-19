# Z6 freeze amendment 1 — `T12_SRM` gets its own complexity constant

Committed **before** any executor, oracle, receipt or result file of this
package exists, and therefore before any outcome it adjudicates has been
computed. `source_main`, the claim ceiling and the six reconcilable rows are
unchanged; no neighboring row is earned here.

## Why

`FREEZE_V1.md` §3 registered `T12_SRM` as "argmin of `declared error + kappa *
sqrt-surrogate`, with the registered exact surrogate `kappa * bits`". Read
literally with `kappa` set to the world's declared state price, `T12_SRM`
becomes the declared cost itself and is equivalent to `T02_BAYES` by
construction. That is not structural risk minimization; it is the declared cost
wearing a different name, and registering it that way would manufacture an
observational equivalence instead of measuring one.

Structural risk minimization (Vapnik 1998) sets the complexity penalty from the
hypothesis class and the sample size, **not** from the environment's price
list. On this universe the two complexity levels are `bits in {0, 1}` and the
sample is `32` scored moments, so the penalty is a single constant per state
bit, fixed by the learner rather than by the world.

## Amendment

`T12_SRM` is registered as

```
argmin over candidates of   declared_error(c) + kappa_SRM * bits(c)
kappa_SRM = 1/4          (exact; the registered rational stand-in for the
                          two-level complexity surrogate at n = 32)
```

where `declared_error` is the world's error term **without** its state price.
`kappa_SRM` does not depend on the world. `T12_SRM` therefore joins `T09_MDL`
and `T10_OCCAM_HARD` in the group of parents that impose their own accounting,
and it can disagree with the registered law.

Added hypothesis:

| id | statement | falsifier |
|---|---|---|
| `D11` | `T12_SRM` disagrees with `T01_GMI` on `R1` in at least one `E-LIN` world, and the world's declared accounting adjudicates against `T12_SRM` there | no disagreement, or `T12_SRM` is right wherever they differ |

## Performance note (no scientific content)

The executor converts each world's rational coefficients to integers by clearing
denominators before the argmin scan, and memoises the exception-code table. This
changes no value: comparisons of `A*rn + B*rd + C*bits` with integer `A, B, C`
obtained by multiplying the exact rational cost by a positive common denominator
have the same order as the rational cost. The oracle route recomputes the same
quantities without that transformation, so the transformation is checked rather
than trusted.
