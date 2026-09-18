# AE2 named results

Registered scope is `FREEZE_V1.md`. All arithmetic is exact rational; no float
appears in any claim. Route A is `ae2_predictive_boundary_v1.py`, route B is
`independent_boundary_oracle_v1.py`, and the two agree on every value.

---

## PIB-1 — the no-predictive-information boundary

**Statement.** Let `X` be the entire allowed observation/history variable and
`Y` the registered future target on finite alphabets, and suppose `Y` is
independent of `X`. Then for every loss `L : Y x Y -> Q` and every rule
`h : X -> Delta(Y)`, deterministic or randomized,

    E[L(h(X), Y)]  >=  min_a  E[L(a, Y)],

with equality attained by the constant base-rate rule. Under 0-1 loss this is
exactly: no learner beats the base-rate optimum.

**Proof.** By independence `P(x,y) = P_X(x) P_Y(y)`, so for a randomized rule
with conditional `h(a|x)`,
`E[L] = sum_x P_X(x) sum_a h(a|x) sum_y P_Y(y) L(a,y)
      >= sum_x P_X(x) min_a sum_y P_Y(y) L(a,y) = min_a E[L(a,Y)]`,
since a convex combination is at least the minimum. The constant rule attains
it. The argument never uses the loss's shape, so it is not special to 0-1 loss.

**Verification.** Registered i.i.d. Bernoulli(3/10) sources with the observation
being the whole history of length 1 and length 2 (observation alphabets 2 and 4;
4 and 16 deterministic rules, all enumerated by route B). Under all three
registered losses — `zero_one`, an `asymmetric` loss charging 3 for a missed
positive, and a `squared` loss — the improvement from observing the history is
exactly `0`. A grid of randomized rules is additionally enumerated and never
beats the best deterministic rule.

**Falsifier.** Any rule over these worlds with strictly smaller risk than the
constant rule under any registered loss.

**Forbidden extrapolation.** This is a statement about *exact* independence. The
quantitative version is PIB-2 and is strictly weaker than "small MI implies
small gain by continuity", which is not asserted.

**Strongest parents.** Wald/Berger statistical decision theory; the convexity
reduction of randomized to deterministic rules. Parent-owned.

---

## PIB-2 — bounded predictive information gives a performance bound

**Statement.** With `gain = sum_x max_y P(x,y) - max_y P_Y(y)` and
`D = sum_{x,y} |P(x,y) - P_X(x) P_Y(y)|`,

    gain  <=  D / 2,

and the bound is tight. Combining with the parent-owned
Csiszar-Kullback-Pinsker inequality `I(X;Y) >= D^2 / 2` (nats) gives

    2 * gain^2  <=  I(X;Y).

**Proof.** Write `Delta(x,y) = P(x,y) - P_X(x) P_Y(y)` and let `y*` maximize
`P_Y`. For any `x` let `yhat(x)` maximize `P(x, .)`. Since
`P_X(x) P_Y(yhat) <= P_X(x) P_Y(y*)`,

    max_y P(x,y) - P(x,y*)  <=  Delta(x, yhat(x)) - Delta(x, y*).

Summing over `x` and using `sum_x Delta(x,y) = 0` for every fixed `y` — so the
`Delta(x,y*)` terms cancel exactly — gives
`gain <= sum_x Delta(x, yhat(x)) <= sum_x sum_y (Delta(x,y))_+ = D/2`, the last
equality because the positive and negative parts of `Delta` each total `D/2`.

**Verification.** Exhaustive over the frozen integer grid: every joint on every
shape up to `4x4` with probabilities multiples of `1/8` — **670,396** cases,
**0** violations, and **15,328** cases attain equality with strictly positive
gain. Route B verifies the two steps of the proof *separately* (0 violations
each) and also confirms the cancellation identity `sum_x Delta(x,y) = 0` on
every case (0 violations); route A checks only the composed inequality, so the
argument itself, not only its conclusion, is independently verified.

**Tightness witness.** `W_TIGHT` (`P(0,0) = P(1,1) = 1/2`) has `gain = 1/2` and
`D = 1`, so `gain = D/2` exactly.

**Registered roster.** For each world the receipt records `gain`, `D`, the
chi-squared divergence, and an exact rational bracket for `I(X;Y)` in nats, and
asserts `2*gain <= D`, `D^2/2 <= I_lower`, `I_upper <= chi^2` and
`2*gain^2 <= I_lower`. For example `W_DEP_NOPRED` has `gain = 0`, `D = 1/5`,
`chi^2 = 1/16`; `W_MILD` has `gain = 1/4`, `D = 1/2`, `chi^2 = 1/4`; `W_TIGHT`
has `gain = 1/2`, `D = 1`, `chi^2 = 1`.

**Falsifier.** A joint with `2*gain > D`, or a roster world whose exact
mutual-information bracket falls below `D^2/2`.

**Forbidden extrapolation.** The bound is one-sided. Small `gain` does not imply
small `I(X;Y)` — `W_DEP_NOPRED` has `gain = 0` with `chi^2 = 1/16 > 0`.

**Strongest parents.** Csiszar-Kullback-Pinsker; the argmax identity for Bayes
accuracy. The `gain <= D/2` step with its cancellation argument is elementary
and is not claimed as a new theorem.

---

## PIB-3 — certified rational enclosure of mutual information

`ln(t)` for rational `t > 0` is bracketed by exact rationals using
`ln t = 2 atanh((t-1)/(t+1))` truncated at 48 terms with the exact remainder
bound `|z|^(2K+1) / ((2K+1)(1 - z^2))`, whose sign matches `z`. All registered
probe brackets have width below `1e-9`, and `ln(2) + ln(3)` is consistent with
`ln(6)` within the brackets.

Route B computes the same quantity from the **Mercator** series
`ln t = sum_k u^k / k` with `u = (t-1)/t` (and `ln t = -ln(1/t)` for `t < 1`),
a different expansion with a different remainder bound, and additionally checks
that both brackets sit inside the parent-owned crude bracket
`1 - 1/t <= ln t <= t - 1`. The two brackets overlap for every probe and for
every roster world's mutual information.

**Falsifier.** A bracket that fails to contain the other route's bracket, or
that escapes the crude bracket.

---

## PIB-4 — Shannon information is not accessible information

**Scope.** `X` uniform on `{0,1}^3`, `Y = x_0 xor x_1 xor x_2`. The learner sees
**all** of `x`; the budget is the decoder's branching depth, not its visibility.

`Y` is a function of `X` and the `Y`-marginal is uniform, so
`I(X;Y) = H(Y) - H(Y|X) = 1 - 0 = 1` bit exactly — the maximum possible for a
binary target — established by a counting argument with no logarithm evaluated.

Best attainable accuracy by decision-tree depth:

| depth | parity | dictator `Y = x_0` |
|---|---|---|
| 0 | `1/2` | `1/2` |
| 1 | `1/2` | `1` |
| 2 | `1/2` | `1` |
| 3 | `1` | `1` |

So at every depth below 3 the best decoder attains exactly the base rate `1/2`,
despite one full bit of mutual information. The dictator, with the *same* one
bit of mutual information, is decoded perfectly at depth 1.

**Unconditionality.** The separation invokes no cryptographic hardness
assumption. It rests on an exactly verified combinatorial fact: for every one of
the `7` proper subsets `S` of the coordinates, the pair `(x_S, y)` is exactly
uniform on `{0,1}^(|S|+1)` — `0` violations. Any decoder that effectively
consults only a proper subset therefore has exactly zero correlation with `Y`.

Route A computes the depth-bounded optimum by a subcube dynamic program; route B
constructs every decision tree bottom-up and evaluates it. They agree at every
depth for secrets `0b111`, `0b001` and `0b011`.

**Falsifier.** Any depth-2 tree over `{0,1}^3` with accuracy above `1/2` on
3-parity.

**Forbidden extrapolation.** This is an unconditional statement about
depth-bounded decision trees on three variables. It is **not** a complexity-class
separation and does not assume or imply any hardness conjecture.

**Strongest parents.** Classical decision-tree lower bounds for parity and the
`k`-wise independence of parity restricted to proper coordinate subsets
(O'Donnell, *Analysis of Boolean Functions*, 2014).

---

## PIB-5 — the registered fixture roster

Each fixture's defining property is machine-checked, not asserted in prose.

**`LOWENT_IID`** — i.i.d. Bernoulli(1/10). Marginal `(9/10, 1/10)` is nonuniform;
the pair `(X_{t-1}, X_t)` is *exactly* a product measure, so L1 dependence and
mutual information are exactly `0` and the predictive gain from history is
exactly `0`. Low entropy, zero temporal dependence.

**`HIGHENT_CYCLIC`** — `X_t = X_{t-1} + 1 (mod 4)`, `X` uniform on `Z_4`. The
marginal is uniform, so its entropy is `2` bits exactly — the maximum on a
four-letter alphabet — yet `acc_base = 1/4`, `acc_obs = 1` and the predictive
gain is `3/4`; `I(X_{t-1}; X_t) = 2` bits exactly. Maximal entropy, perfect
predictability.

**`DRIFT_INVERT`** — phase 1 has `Y = X`, phase 2 has `Y = 1 - X`, equiprobable.
Each phase carries `1` bit of mutual information, but the pooled joint is
*exactly* independent (L1 dependence `0`), so a learner that pools the phases
sees no structure whatsoever. The rule fitted on phase 1 scores `1` in phase 1
and exactly `0` in phase 2 — strictly below that phase's base rate `1/2`.
Historical dependence does not merely stop helping; it becomes harmful.

**`CHAOS_DOUBLING`** — `x_{t+1} = 2 x_t (mod 1)` on `8`-bit dyadic states with
the top `4` bits observed, verified by enumerating all `256` states. The next
symbol is determined with certainty for exactly `4` steps (Bayes accuracy `1`),
and from step `4` onward the Bayes accuracy is exactly `1/2`. Deterministic
dynamics, exactly bounded predictability horizon.

---

## Null and detector validation

Detector: `Y` determined by `X` with a uniform `Y`-marginal — so `I(X;Y)` is
exactly one bit — while no depth-2 decision tree beats the base rate.

- recall: fires on the planted positive, 3-parity;
- no-alarm on known-clean: does **not** fire on the dictator `Y = x_0` or on the
  two-bit xor `Y = x_0 xor x_1`;
- null: `0` of `200` random deterministic worlds drawn from a deterministic
  integer LCG are flagged.

## Forbidden extrapolations for the whole note

Nothing here licenses `INTELLIGENCE_EQUALS_COMPRESSION`,
`ALL_LEARNING_IS_COMPRESSION`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`GENERAL_REASONING_REDUCED_TO_PREDICTION`, `CRYPTOGRAPHIC_HARDNESS_ASSUMED`,
`INFINITE_HORIZON_EXTENSION`, `CONTINUOUS_STATE_EXTENSION`,
`UNIVERSAL_LEARNER_IMPOSSIBILITY`, `GMI_MORPHOLOGY_PREDICTION` or
`COMPLETE_GMI`. Every statement is finite-alphabet, finite-horizon and
registered-scope; the finite tags are carried in `MANIFEST_V1.json`.
