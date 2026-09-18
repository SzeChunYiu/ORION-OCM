# AE1 named results

Every result below is stated at the registered finite scope of `FREEZE_V1.md`.
All quantities are exact rationals; no float appears in any claim. Route A is
`ae1_structure_separation_v1.py`, route B is
`independent_separation_oracle_v1.py`, and the two agree on every value.

## Definition D-AE1 (task-relative exploitable structure)

Let `W = (X, Y, P, A, U)` be a registered world and let `H_R` be the rule class
admitted by a budget `R = (k, d)` of the frozen lattice — functions `X -> Y`
that read at most `k` coordinates of the registered coordinate decomposition of
`X` and are computable by a decision tree of branching depth at most `d` over
those coordinates.

**Exploitable structure of `W` for task `T` under budget `R`** is

    U(W, T, R) = max_{h in H_R} score(h, W, T)  -  best blind score(W, T).

It is task-relative (it moves with `T`), resource-relative (it moves with `R`)
and architecture-independent (`H_R` names coordinates and branching, never
layers, parameters or a network family). It is *not* defined as low entropy,
nonuniform marginals, low intrinsic dimension or compressibility; AE1-1 through
AE1-6 below exhibit exact worlds separating it from each of those.

---

## AE1-1 — marginal nonuniformity is independent of dependence

**Scope.** Registered binary worlds. **Quantifiers.** Exhibits both off-diagonal
truth-value patterns.

`W_IND_SKEW` has a nonuniform `X`-marginal `(3/4, 1/4)` and is *exactly* a
product measure: its L1 dependence is `0`. `W_DEP_UNIFMARG` has uniform
marginals on both coordinates and is maximally dependent. So neither predicate
implies the other.

**Minimality.** Over the frozen grid (all joints with probabilities multiples of
`1/8`, all shapes up to `4x4`, 16 shapes searched exhaustively), the minimal
shape realizing `MARG_NONUNIF and not DEP` is `(2,1)` and the minimal shape
realizing `DEP and not MARG_NONUNIF` is `(2,2)`.

**Falsifier.** A product measure with a nonuniform marginal that the DEP
predicate flags, or a shape smaller than the reported minimum realizing the
pattern on the frozen grid.

**Strongest parents.** Elementary probability; no novelty claimed.

---

## AE1-2 — statistical dependence does not imply predictive dependence

**Scope.** Registered binary worlds, 0-1 loss.

`W_DEP_NOPRED` with `P = [[9/20, 1/20], [7/20, 3/20]]` has L1 dependence
`1/5 > 0`, yet `acc_obs = acc_base = 4/5` exactly, so its Bayes gain is exactly
`0`. Observing `X` buys nothing under 0-1 loss despite genuine dependence.

The converse implication **does** hold and is verified exhaustively: over all
`16` shapes of the frozen grid, the number of shapes admitting `PRED` without
`DEP` is `0`. Predictive dependence therefore strictly refines statistical
dependence.

**Minimality.** Minimal shape `(2,2)`.

**Falsifier.** Any grid world with `acc_obs > acc_base` and vanishing L1
dependence.

**Forbidden extrapolation.** The gain being zero is loss-relative. It does not
say the dependence is useless under every loss; AE1-3 shows the opposite case.

**Strongest parents.** Bayes decision theory; the argmax identity
`acc_obs = sum_x max_y P(x,y)` is standard.

---

## AE1-3 — predictive dependence and control relevance are incomparable

**Scope.** Registered worlds with a finite action set and a rational utility.

*Prediction without control.* `W_PRED_NOCTRL` has `acc_base = 1/2` and
`acc_obs = 1`: `X` determines `Y`. Its utility is **not** constant in `Y`
(`U(a1, 0) = 3/4`, `U(a1, 1) = 7/8`), yet action `a0` dominates pointwise, so
the blind optimum `1` equals the observation-conditioned optimum `1` and the
control gain is exactly `0`.

*Control without prediction.* `W_CTRL_NOPRED` has `acc_obs = acc_base = 1/2`,
so its Bayes gain under 0-1 loss is exactly `0`; but the blind utility optimum
is `1/4` and the observation-conditioned optimum is `1/2`, a control gain of
`1/4`. The observation resolves exactly the distinction the utility cares about
while leaving the modal label untouched.

**Falsifier.** A policy over `W_CTRL_NOPRED` beating `1/2`, or a policy over
`W_PRED_NOCTRL` beating `1`; both spaces are enumerated exhaustively by route B.

**Strongest parents.** Statistical decision theory; value of information
(Howard 1966). No novelty claimed in the underlying inequality.

---

## AE1-4 — observational prediction does not imply causal relevance

**Scope.** The registered structural causal model `Z -> X`, `Z -> Y` with no
edge `X -> Y`, `P(Z) = (1/2, 1/2)`, `P(X = z | Z = z) = 4/5`,
`P(Y = z | Z = z) = 3/4`.

The induced joint is `P(0,0) = P(1,1) = 13/40`, `P(0,1) = P(1,0) = 7/40`.
Observationally `P(Y=1 | X=0) = 7/20` and `P(Y=1 | X=1) = 13/20`, an
observational Bayes gain of `3/20 > 0`. Interventionally
`P(Y=1 | do(X=0)) = P(Y=1 | do(X=1)) = 1/2`: the interventional gain is exactly
`0`, because severing `Z -> X` leaves `Y` on its `Z`-driven marginal.

**Falsifier.** Any `x, x'` with `P(y | do(x)) != P(y | do(x'))` in this model.

**Forbidden extrapolation.** This is a single confounded triple. It does not
establish that observational prediction is *never* causally informative, and it
does not identify causal structure from data.

**Strongest parents.** Pearl's do-calculus and the back-door criterion
(Pearl 2009, *Causality*, 2nd ed.). Entirely parent-owned; the residual here is
only the exact rational instance.

---

## AE1-5 — existence of structure does not imply accessibility, and no
## budget-independent scalar can repair this

**Scope.** `X` uniform on `{0,1}^3`, the frozen budget lattice of 16 cells.

`W_PARITY3` (`Y = x_0 xor x_1 xor x_2`) has `acc_base = 1/2` and full-information
accuracy exactly `1`. Yet every rule admissible at `(k,d) = (2,2)` attains
exactly `1/2`, and so does every rule admissible at `(k,d) = (3,2)` — reading
all three coordinates is not enough if the branching depth is two. Only the
single top cell `(3,3)` attains `1`. The structure exists and is maximal; below
the top budget it is entirely inaccessible.

**Scalar impossibility (row 7, negative disjunct).** Let `sigma : W -> Q` be any
**budget-independent** scalar claimed to determine available structure, in the
sense `sigma(W) >= sigma(W') => U(W,R) >= U(W',R)` for every `R` in the frozen
lattice. Taking `W = W_PARITY3` and `W' = W_NOISY_DICT` (`Y = x_0` with
probability `3/4`):

| budget | `U(W_PARITY3, R)` | `U(W_NOISY_DICT, R)` |
|---|---|---|
| `k1_d1` | `1/2` | `3/4` |
| `k3_d3` | `1` | `3/4` |

The order reverses, so no such `sigma` exists. The quantifier matters: a scalar
indexed by the *pair* `(W, R)` is **not** refuted by this, and the positive
disjunct below supplies exactly such an object. Three named candidate scalars
are refuted explicitly and individually — full-information gain
(`1/2` vs `1/4`), L1 dependence (`1` vs `1/2`) and chi-squared divergence
(`1` vs `1/4`) — each ranking `W_PARITY3` above `W_NOISY_DICT` while
`W_NOISY_DICT` strictly outperforms it at `k1_d1`.

**Positive disjunct (row 7).** The object `S(W) : R -> max_{h in H_R} acc(h, W)`
on the 16-cell lattice is well defined, **monotone** (0 violations over all
ordered budget pairs and all registered worlds) and **bounded above** by the
full-information optimum (0 violations). It is architecture-independent by
construction.

**Measured auxiliary.** Order reversals are generic, not contrived: `114` of
`200` random world pairs from the registered family exhibit one. A single
reversal already suffices for the refutation; the high rate strengthens it.

**Falsifier.** A rule inside `H_{2,2}` or `H_{3,2}` beating `1/2` on
`W_PARITY3` — route B enumerates every decision tree of the relevant depth and
finds none.

**Strongest parents.** The parity lower bound for bounded-depth decision trees
and for juntas is classical and entirely parent-owned.

---

## AE1-6 — finite-sample discoverability is not asymptotic learnability

**Scope.** Hypothesis family: all `8` secrets `s` in `GF(2)^3` with a uniform
prior; `X` uniform; `Y = <s, X>`.

The secret-marginalised world has `acc_base = acc_obs = 9/16` exactly, so it has
no predictive structure at all once `s` is integrated out. The Bayes-optimal
learner given `m` i.i.d. labelled pairs from a single fixed `s` attains expected
test accuracy

| `m` | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| expected accuracy | `9/16` | `79/128` | `723/1024` | `6715/8192` |

At `m = 0` this is exactly the base rate `9/16`; the asymptotic optimum is `1`;
and even at `m = 3` the learner is at `6715/8192 < 1`, because three uniform
draws span `GF(2)^3` only with probability `21/64`.

Route A derives these from the span argument (inside the span of the training
points every consistent secret agrees, outside it they split exactly evenly).
Route B enumerates every `(secret, training tuple, test point)` and never uses
a span, rank or subspace argument. The two agree exactly at every `m`.

**Falsifier.** Any learner over this family with expected accuracy above the
tabulated value at some `m`.

**Forbidden extrapolation.** The `m = 0` equality is with respect to the
*marginalised* world's base rate, which is the stated comparison; it is not a
claim that no learner ever helps at zero samples in any other world.

**Strongest parents.** PAC/statistical learning theory and the classical sample
complexity of learning parities; parent-owned.

---

## AE1-7 — the separations are simultaneous, not sequential

The receipt's `distributional_separation` table gives all three distributional
predicates for all four registered worlds at once, so the separations are read
off a single consistent roster rather than assembled from incompatible setups.

## Null and detector validation

The package's detector is the **accessibility gap**: full-information Bayes gain
strictly positive while every rule admissible at junta arity `k <= 2` attains
exactly the base rate. Validation on real (not fixture) data:

- recall on the planted positive: fires on `W_PARITY3`, gap magnitude `1/2`;
- no-alarm on known-clean worlds: `W_DICT` and `W_NOISY_DICT` are **not**
  flagged;
- null: over `200` random worlds from the registered family the detector fires
  `7` times. Those seven are **not** false positives — each is a genuine but
  small accessibility gap, and all seven magnitudes are reported individually
  (`1/32` x3, `1/16` x2, `3/32`, `3/16`). The largest is `3/16`; the frozen
  magnitude threshold is `1/4`, at or above which **0 of 200** random worlds
  fire, against the witness's `1/2`.

The detector was not narrowed to force a zero count: the unthresholded rate is
published in the receipt alongside the thresholded one.

## Forbidden extrapolations for the whole note

Nothing here licenses `INTELLIGENCE_EQUALS_COMPRESSION`,
`MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`UNIVERSAL_STRUCTURE_MEASURE`, `ARCHITECTURE_SELECTION_LAW`,
`GMI_MORPHOLOGY_PREDICTION`, `MINIMALITY_OVER_ALL_REAL_VALUED_JOINTS`, or
`COMPLETE_GMI`. Minimality is claimed only over the frozen denominator-8 grid
and shapes up to `4x4`. The budget lattice is the frozen two-dimensional one;
memory, precision, communication, time and energy budgets are **not**
instantiated here.
