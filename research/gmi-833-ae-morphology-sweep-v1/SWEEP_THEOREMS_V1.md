# SWEEP theorems v1

Claim ceiling
`GMI_833_AE_MORPHOLOGY_SELECTION_PREDICTOR_COMPARISON_AT_REGISTERED_FINITE_SCOPE`.
Freeze `a9b5de6154fb4758523133b6e07255adc4dababc`, source main
`349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

## 0. Registered objects

`X = {0,1}^3` under the uniform measure unless a fixture says otherwise; `Y`
binary. A **world** `W` is a pair of exact rational vectors `(P(x))_x`,
`(P(Y=1|x))_x`. A **morphology** `m` is a pair (hypothesis class `H_m`,
resource vector `r(m) in Z^3_{>=0}` with coordinates
`(fan_in, depth, memory_cells)`). The registered set is

| `m` | class | `r(m)` |
|---|---|---|
| `m0_constant` | constants | `(0,0,1)` |
| `m1_arity1_junta` | functions of at most one coordinate | `(1,1,2)` |
| `m2_arity2_junta` | functions of at most two coordinates | `(2,2,4)` |
| `m4_gf2_affine` | `a·x XOR b` over GF(2) | `(3,1,4)` |
| `m3_arity3_table` | all functions | `(3,3,8)` |

`acc(m, W) = max_{h in H_m} Pr_W[h(X) = Y]`, an exact `Fraction`. The
**achievability profile** is `p(W) = (acc(m,W))_{m in M}`.

**Viability bridge (the residual of this tranche).**
`active(W, tau) = { m in M : acc(m, W) >= tau }`.

**Selection** is the parent choice correspondence applied to `active(W, tau)`:
`NO_VIABLE_MORPHOLOGY` if empty; otherwise the full scalar argmin set under a
strictly positive price `w`, together with the raw Pareto frontier. No tie is
broken. Frozen `w_A = (1,1,1)`, `w_B = (1,3,1)`, `tau = 3/4`.

## 1. SWEEP-1 — raw Shannon information does not determine the selection

**Scope.** The 256 deterministic worlds `Y = f(X)` on `{0,1}^3` under uniform
`X`, at `tau = 3/4` and price `w_A`.

**Statement.** There exist worlds `W, W'` with `I(X;Y) = I(X;Y')` and
`sel(W) != sel(W')`. Exhaustively, `4,348` of the `10,292` equal-information
world pairs conflict.

**Exactness of the equality test.** For uniform `X` and deterministic `Y`,
`I(X;Y) = H(Y) = h(k/8)` with `k = |f^{-1}(1)|`. `h` is strictly concave on
`[0,1]` and symmetric about `1/2`, so `h(k/8) = h(j/8)` iff
`min(k, 8-k) = min(j, 8-j)`. Equality of mutual information is therefore decided
by an integer invariant and **no logarithm is evaluated anywhere**.

**Witness.** `f = 11100000` and `f' = 01101000` (truth tables indexed by
`x = x0 + 2·x1 + 4·x2`) both have invariant `3`; the first selects
`m1_arity1_junta`, the second `m4_gf2_affine`.

**Assumptions.** Uniform `X`; deterministic `Y`; the registered `M`, `r`, `w`,
`tau`. **Falsifier.** A price/threshold pair at which the conflict count is `0`.
**Forbidden extrapolation.** That raw information is uninformative about
morphology in general, or on non-uniform or continuous domains.

## 2. SWEEP-2 — single-budget usable information does not determine it either

`U(W, T, R0) = acc(m2, W) - acc(m0, W)`, AE10's achievability gap at the single
reference budget `R0` = arity 2 / depth 2. `9,576` of `17,744` equal-`U` pairs
conflict. Witness: `f = 11000000` and `f' = 11100000`, both with `U = 1/4`,
selecting `m0_constant` and `m1_arity1_junta` respectively.

This is the sharp form of the row's question: usable information is the *right
kind* of quantity, but **one scalar of it is not enough**.

## 3. SWEEP-3 — the resource-conditioned vector does determine it

**Sufficiency.** If `p(W) = p(W')` then `active(W,tau) = active(W',tau)` for
every `tau`, hence `sel(W) = sel(W')` for every `(tau, w)`. Immediate from the
definitions — the content of the result is not this implication but the three
facts that make it non-vacuous:

1. `0` conflicts over the census (the implication is not vacuously about a
   partition into singletons);
2. **strictly coarser than the world** — `256` worlds collapse to `11` distinct
   profiles, so the profile is a genuine statistic, not a re-encoding of `f`;
3. **strictly finer than either scalar** — `5` distinct values of the raw
   invariant and `3` of `U(·,R0)` versus `11` profiles.

**Minimal sufficient subvector.** All `31` nonempty subvectors were tested. At
`tau = 3/4`, `w_A`, exactly one minimal sufficient subvector exists:
`{m0_constant, m1_arity1_junta, m2_arity2_junta}`. The two most expensive
coordinates are redundant *for the selection decision at this threshold and
price* — they are not redundant for the profile.

**Price robustness.** At `w_B = (1,3,1)` the three counts are `3,568`, `9,576`
and `0`.

**Forbidden extrapolation.** That the achievability profile is a sufficient
statistic for anything other than this selection rule, or that the minimal
subvector is price- or threshold-independent.

## 4. SWEEP-4 — exact locality phase boundary (AE6)

**Locality predicate.** `W` is *locality-exploitable at order k* iff some
`k`-subset `S` of coordinates satisfies `max` accuracy `= 1` for predictors
measurable with respect to `x_S`. This is the coordinate-junta special case of
the manifold/low-intrinsic-dimension hierarchy and is labelled as such.

**Derivation.** `m_k` is active at `tau` iff the best arity-`k` junta attains
accuracy `>= tau`; `acc` for a class measurable w.r.t. `S` equals
`sum over cells of max(cell mass on Y=0, cell mass on Y=1)`.

**Witnesses.** `Y = x0 XOR x1 XOR x2` is locality-exploitable only at order `3`
and pins every class of arity `<= 2` at accuracy exactly `1/2`. `Y = x0 AND x1`
is locality-exploitable at order `2`.

**Exact phase maps** (price `w_A`, half-open intervals `(lo, hi]`):

- parity: `tau in (0, 1/2]` → `{m0_constant}`; `tau in (1/2, 1]` →
  `{m4_gf2_affine}`.
- AND: `tau in (0, 3/4]` → `{m0_constant}`; `tau in (3/4, 1]` →
  `{m2_arity2_junta}`.

So **`tau = 1/2` is the exact boundary at which failure of locality displaces
every local morphology** and the non-local GF(2)-affine morphology is selected
instead, at cost `8` under `w_A`. At the registered `tau* = 7/8` the two worlds
select different morphologies and the local classes are inactive for parity.

**Falsifier.** A world that is not locality-exploitable at order `<= 2` yet has
a local class active above `tau = 1/2`. **Forbidden extrapolation.**
`REAL_DATASET_INTRINSIC_STRUCTURE_TEST` — nothing here is a claim about real
data, and AE6's prospective row stays OPEN.

## 5. SWEEP-5 — causal structure changes the selected morphology (AE13)

Observables `x = (A, B, D)` with `B, D` independent fair coins; target `Y = C`.

- World `L`: `A ~ Bern(1/2)`, `P(C=1|A=1) = 3/4`, `P(C=1|A=0) = 1/4`.
- World `R`: `C ~ Bern(1/2)`, `P(A=1|C=1) = 3/4`, `P(A=1|C=0) = 1/4`.

`L` and `R` are Markov-equivalent; their observational joints agree **cell by
cell as exact rationals** (machine-checked, not asserted), so
`p(L) = p(R)` and the observational selection is `{m1_arity1_junta}` in both.

Under `do(A)`: in `L` the `A -> C` edge survives and `acc(m1) = 3/4`; in `R` the
`C -> A` edge is severed, `C` becomes independent of `A`, and every class is
pinned at `acc = 1/2`. At `tau = 3/4` the selections are
`{m1_arity1_junta}` and `NO_VIABLE_MORPHOLOGY`, and they differ for every
`tau in (1/2, 3/4]`.

**Verdict.** `CAUSAL_STRUCTURE_CHANGES_SELECTED_MORPHOLOGY`. The observational
distribution alone does not determine the morphology selected for an
interventional task. **Forbidden extrapolation.**
`CAUSAL_DISCOVERY_FROM_OBSERVATION_ALONE` — this result says the opposite.

## 6. SWEEP-6 — no AE5 scalar predicts (AE5)

Same census, same test, four scalars from AE5's own row list:

| scalar | distinct values | equal-value pairs | conflicting pairs |
|---|---:|---:|---:|
| predictive-state cardinality `\|S\|` | 6 | 13,196 | **8,712** |
| GF(2) predictive rank | 4 | 18,468 | **10,172** |
| causal-state entropy (certified lower bound) | 13 | 5,996 | **2,968** |
| registered description length | 4 | 18,643 | **12,818** |

Causal states are computed by the Crutchfield–Young definition on the process
`x0, x1, x2, y`. **Entropy is never evaluated.** Two worlds are keyed together
only when their exact causal-state probability *multisets* coincide, which
implies equal entropy in any base; the converse is not used, so `2,968` is a
certified **lower bound** on the true number of equal-entropy conflicts — the
direction that makes the "does not predict" verdict sound.

Description length is the minimum code length in the registered finite language
`L1` (rule 6 bits, negated rule 7, XOR of two rules 11, literal table 9). `K`
itself is never computed; `KOLMOGOROV_COMPLEXITY_COMPUTED` is a registered
forbidden promotion and the receipt records
`kolmogorov_complexity_not_computed: true`.

**Answer to the row.** No single scalar of the AE5 family predicts the selected
morphology; the resource-conditioned achievability vector does.

## 7. Two routes

Route A (`morphology_sweep_v1.py`) is analytic: partition-cell maxima over
coordinate subsets for the junta classes, and the Walsh closed form
`1/2 + max_a |W(a)|/2` for the affine class. Route B
(`independent_sweep_oracle_v1.py`) materialises every member of every class as
an explicit 8-entry truth table, scores it by direct summation, re-implements
the selection rule from the parent's written definition, and rebuilds the causal
fixtures from their structural equations. It imports nothing from Route A. The
two agree on all `256` profiles, on all `256` selections under both prices, and
on all four causal fixtures.

## 8. Hostiles and nulls

| id | perturbation | moves its quantity | detected |
|---|---|---|---|
| `H1_resource_vector_tamper` | reprice `m4` to `(3,9,9)` | selection moves `m4 → m3` | yes |
| `H2_zero_price_coordinate` | `w = (1,0,1)` | the Pareto-dominated `(1,5,1)` ties with `(1,1,1)` | yes, positivity guard raises |
| `H3_fabricated_tie_break` | return one winner from a two-element argmin | argmin really has 2 members on `Y = x0 XOR x1` | yes |
| `H4_observational_only_intervention` | read the interventional profile off the observational joint | returns the same answer for `L` and `R` | yes |
| `H5_parent_blob_tamper` | corrupt a pinned parent blob sha | audit flips | yes |

**Null.** `200` shuffled selection maps over the true profiles: zero trials
reached `0` conflicts (range `3,533`–`3,685`), while the true profile has `0` —
so the sufficiency result is not attainable by chance. `200` random strictly
positive prices: `0` violations of the parent's `SEL-1` (scalar argmin is Pareto
efficient) and raw information still fails in `200/200`, so the `SWEEP-1`
verdict is not an artifact of the frozen price. The no-alarm case is asserted
directly: the conflict detector reports `0` on the true result.
