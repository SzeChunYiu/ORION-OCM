# Section D V5 — phase-boundary uncertainty and scale extrapolation freeze

Date frozen: 2026-09-14.
Owner: #602 Section D. Child tracker: #689.
Base: `88b66b1b39940c9f573d0f3525a235e0c88a2cb2`.

This file is the **pre-outcome authority** for V5. It is committed before any V5 witness, result receipt, test, or scored held-out output exists.

## 0. Question

Two Section D obligations remain after the prospective phase-law tranches:

1. quantify uncertainty in a morphology phase boundary;
2. test whether a phase law fitted on tiny exact worlds extrapolates to larger held-out worlds.

A contributed closure bundle supplied two parent-owned mathematical ingredients: a perturbation bound for phase-wall normals and an affine finite-size expansion. Those formulas are theory input only. They do not count as evidence here until a new held-out family is frozen and scored.

## 1. Parent first refusal / claim boundary

Strongest parents own the mathematical and mechanism content:

- convex/polyhedral normal fans, lower hulls and linear-price selection;
- coefficient sensitivity / robust optimization under bounded uncertainty;
- database indexing and bidirectional-index tradeoffs;
- elementary rational finite-size asymptotics.

V5 can therefore claim only a governed, prospective application to morphology selection. It cannot claim a new convex-geometry theorem, a new indexing algorithm, universal scaling, or real-scale calibration.

Claim ceiling if every frozen prediction passes:

```text
FINITE_EXACT_PROSPECTIVE_PHASE_BOUNDARY_UNCERTAINTY_V5
FINITE_EXACT_HELDOUT_SCALE_EXTRAPOLATION_V5
PARENT_OWNED_POLYHEDRAL_ROBUST_INDEXING_ASYMPTOTICS
NO_REAL_SCALE_UNIVERSAL_SCALING_OR_COMPLETE_COORDINATE_SCHEMA_CLAIM
```

## 2. World family

For each integer relation size `n>=2`, freeze an exact bijection between `n` opaque key tokens and `n` opaque value tokens. The obligation supports both directions exactly:

```text
forward(key) -> value
reverse(value) -> key
```

One future ecology block contains exactly:

```text
F = 3 forward queries
R = 5 reverse queries
Q = F+R = 8 total queries.
```

The query multiset is fixed before scoring and uses every direction. Token identities carry no order, distance, or path information.

## 3. Neutral candidate mechanisms

### M0 — `key_index`

Store one value payload per key.

- persistent cells: `n`;
- forward lookup: `1` operation;
- reverse lookup: `n` scan operations;
- exact for every bijection.

One-block serve count:

```text
C_key(n) = 3 + 5n.
```

### M1 — `value_index`

Store one key payload per value.

- persistent cells: `n`;
- forward lookup: `n` scan operations;
- reverse lookup: `1` operation;
- exact for every bijection.

One-block serve count:

```text
C_value(n) = 3n + 5.
```

### M2 — `dual_index`

Store both directions.

- persistent cells: `2n`;
- every lookup: `1` operation;
- exact for every bijection.

One-block serve count:

```text
C_dual(n) = 8.
```

### M3 — `pair_list`

Store explicit pairs without either index.

- persistent cells: `2n`;
- every lookup: `n` scan operations;
- exact for every bijection.

One-block serve count:

```text
C_pair(n) = 8n.
```

No family/architecture label is visible to selection; only exactness and the registered resource vector are visible.

## 4. Registered phase coordinates and exact wall

Use the two-dimensional prospective price comparison

```text
persistent-cell price = x > 0
serve-op price        = 1.
```

The physical vector is therefore

```text
(persistent_cells, serve_ops_per_block).
```

For every `n>1`:

- `key_index` is dominated by `value_index` because they use equal persistent cells and `3+5n > 3n+5`;
- `pair_list` is dominated by `dual_index` because they use equal persistent cells and `8n > 8`.

The only possible winning wall is `value_index` versus `dual_index`:

```text
n*x + (3n+5) = 2n*x + 8
x*(n) = (3n-3)/n = 3 - 3/n.
```

Frozen winner law:

```text
0 < x < x*(n):  dual_index
x = x*(n):      {dual_index, value_index}
x > x*(n):      value_index.
```

If any other candidate is selected at a strictly positive price, the witness is wrong.

## 5. Tiny-scale fit frozen before held-out scoring

Calibration scales:

```text
n = 2, 3, 4.
```

Fit family frozen in advance:

```text
x_fit(n) = alpha + beta/n.
```

The fitting rule uses **only** the exact phase walls at `n=2` and `n=3`; `n=4` is a calibration check, not a fit datum.

Frozen predicted fitted parameters:

```text
alpha = 3
beta  = -3.
```

Frozen calibration check:

```text
x_fit(4) = 9/4.
```

Any other fitted coefficients or calibration mismatch is a failed preregistration.

## 6. Held-out extrapolation scales and predictions

Held-out scales:

```text
n = 7
n = 8.
```

Neither held-out wall may be used by the fitting routine.

Frozen prospective predictions:

```text
x*(7) = 18/7
x*(8) = 21/8.
```

For every calibration and held-out `n`, exactness must be checked on **every forward and reverse query for every bijection**. This requires exhaustive enumeration of all `n!` bijections. In particular `n=8` contains `40,320` bijections and `645,120` directional query obligations.

The extrapolation box is earned at this registered finite scope only if the tiny-scale fit predicts both held-out walls exactly and the exact phase winner on both sides of each wall agrees with the frozen law.

## 7. Frozen bounded-counter uncertainty model

Persistent-cell counts are exact by construction.

The instrument measuring each candidate's one-block serve count is guaranteed only within

```text
±1 operation
```

of the exact total, independently for `value_index` and `dual_index`.

Let

```text
e_value, e_dual in {-1,0,1}.
```

Then the measured op-difference is

```text
(3n-3) + e_value - e_dual.
```

The candidate phase wall under an admissible measurement error is

```text
x_e(n) = ((3n-3) + e_value - e_dual) / n.
```

Frozen robust uncertainty interval:

```text
I_n = [ (3n-5)/n, (3n-1)/n ].
```

The witness must enumerate all 9 error pairs in `{-1,0,1}^2` and prove by exact rational comparison that their minimum/maximum walls equal the two endpoints above.

The unperturbed exact wall must lie inside `I_n`.

## 8. Frozen robust decisions / abstention

For both held-out scales `n=7` and `n=8`, freeze three price probes:

```text
x_low  = 2
x_mid  = 5/2
x_high = 3.
```

Predictions:

```text
x=2:
  dual_index wins for all 9 admissible error pairs.

x=5/2:
  at least one admissible error pair selects dual_index and at least one selects value_index;
  robust output must therefore be CANNOT_IDENTIFY.

x=3:
  value_index wins for all 9 admissible error pairs.
```

A method that emits one morphology at `x=5/2` despite the registered uncertainty fails the uncertainty test.

## 9. Scope-failure / non-universality twin

Change one primitive law only: a scan operation may inspect two records at once. The scan cost becomes

```text
scan2(n) = ceil(n/2).
```

Keep the same 3-forward/5-reverse ecology and candidate storage sizes. The batched `value_index` serve count is

```text
C_value_batch(n) = 3*ceil(n/2) + 5.
```

The dual count remains 8, so the batched wall is

```text
x_batch*(n) = (3*ceil(n/2)-3)/n.
```

Frozen control: the original fitted law `3-3/n` must fail on at least one held-out scale `n in {7,8}`. This is required evidence that the extrapolation is conditional on the primitive cost law and is not universal.

## 10. Remint and independent selection implementations

Freeze an opaque token remint for each scored scale by reversing key labels and applying a distinct cyclic permutation to value labels. The remint must preserve:

- exactness;
- resource vectors;
- fitted `alpha,beta`;
- exact held-out walls;
- uncertainty intervals;
- robust decisions.

Two independently coded selectors are required:

1. direct all-pairs dominance plus exact price-cost argmin;
2. a lower-envelope selector that sorts candidate lines by memory coordinate and constructs/queries the exact lower hull without calling the first selector.

They must agree on every registered scale and price probe.

## 11. Box disposition if all predictions pass

At the declared finite exact scope, passing V5 would support exactly:

- [x] Quantify uncertainty in phase-boundary location.
- [x] Test phase-law extrapolation beyond fitted tiny worlds.

It would **not** close:

- real-scale empirical phase uncertainty;
- complete/unbounded ecology, resource, verifier, or history coordinate schemas;
- arbitrary nonlinear cost laws;
- universal scale extrapolation;
- any claim that every intelligence morphology is captured by this candidate family.
