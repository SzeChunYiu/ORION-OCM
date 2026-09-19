# GMI #833 Section AE2 — predictive-information learnability boundary: prospective freeze v1

Source `main`: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`.

Committed **before** any executor, oracle, test, fixture, receipt or
reconciliation file of this package exists in the tree.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE2 — Information-theoretic learnability boundary`

1. `- [ ] Prove a no-predictive-information boundary: if the registered future target is independent of all allowed history/observations, no learner can improve prediction beyond the Bayes/base-rate optimum.`
2. `- [ ] Generalize from exact independence to bounded predictive information and derive performance bounds where possible.`
3. `- [ ] Distinguish mutual information from usable/accessible information under computational/resource constraints.`
4. `- [ ] Construct a source with high mutual information but computationally inaccessible dependence and show why Shannon information alone does not guarantee practical intelligence.`
5. `- [ ] Construct low-entropy/nonuniform but temporally independent controls.`
6. `- [ ] Construct high-entropy but strongly predictable structured controls.`
7. `- [ ] Add nonstationary/drifting sources where historical dependence ceases to be useful.`
8. `- [ ] Add chaotic deterministic systems where microscopic predictability is horizon-limited.`

**No neighboring row is earned here.** No AE1, AE3, AE10 or other row, and no
row of the #833 issue body, is earned by this tranche.

## Frozen statements to be proved or refuted

- `PIB-1` (no-predictive-information boundary). For any finite registered world
  in which the target `Y` is independent of the entire allowed observation/history
  variable `X`, every rule `h : X -> Delta(Y)`, deterministic or randomized, has
  expected 0-1 accuracy at most `max_y P_Y(y)`, with equality attained by the
  constant base-rate rule. The statement is to be proved for arbitrary bounded
  loss, not only 0-1 loss, or the generalization is to be reported as OPEN.
- `PIB-2` (bounded-predictive-information performance bound). With
  `gain = sum_x max_y P(x,y) - max_y P_Y(y)` and
  `D = sum_{x,y} |P(x,y) - P_X(x) P_Y(y)|`, prove `gain <= D/2` and exhibit a
  witness attaining equality. Combined with the parent-owned
  Csiszar-Kullback-Pinsker inequality `I(X;Y) >= D^2 / 2` (nats), this yields
  `2 * gain^2 <= I(X;Y)`. Only the rational forms `4 * gain^2 <= D^2` and
  `D^2 / 2 <= I_lower` may appear as verified assertions.
- `PIB-3` (exact rational enclosure of mutual information). Mutual information in
  nats must be bracketed by exact rationals `[I_lo, I_hi]` with
  `I_hi <= chi2 = sum_{x,y} P(x,y)^2 / (P_X(x) P_Y(y)) - 1`, using a certified
  rational truncation of the `atanh` series for the natural logarithm with an
  explicit rational remainder bound. No float may enter the bracket.
- `PIB-4` (Shannon information vs decoder-complexity accessible information). A
  registered world with `I(X;Y)` exactly one bit in which every rule computable
  by a decision tree of depth strictly less than the registered arity attains
  expected accuracy exactly equal to the base rate. The budget is computational
  (branching depth over the observed coordinates), and the observation is *not*
  restricted: the learner sees all of `x`.
- `PIB-5` (fixture roster). Four registered generator families, each with an
  exactly asserted defining property:
  `LOWENT_IID` (nonuniform marginal, exactly zero temporal dependence),
  `HIGHENT_CYCLIC` (uniform maximal-entropy marginal, deterministic one-step
  predictability), `DRIFT_INVERT` (a nonstationary source whose phase-1-fitted
  rule scores strictly below base rate in phase 2, and whose pooled joint has
  exactly zero mutual information while each phase has one bit),
  `CHAOS_DOUBLING` (deterministic doubling map on `b`-bit dyadic states observed
  to `c` bits, with certainty prediction for exactly `c` steps and exactly
  base-rate accuracy thereafter).

## Required evidence and falsifiers

- Route A: closed-form/analytic computation of every quantity.
- Route B: an independently written oracle, importing nothing from route A,
  that recomputes every accuracy by exhaustive enumeration of the full
  deterministic rule space (and of all depth-bounded decision trees for
  `PIB-4`), and recomputes `D`, `chi2` and the logarithm bracket by a separate
  series implementation.
- Randomized rules must be reduced to deterministic rules by a proved convexity
  argument, and the reduction must additionally be checked empirically on a
  registered grid of randomized rules.
- Hostiles: for each, first assert that the perturbation actually changes the
  quantity it targets, then assert the checker flags it. Registered hostile
  targets include a false independence claim, a `gain > D/2` violation, a
  corrupted logarithm bracket, a decision tree exceeding the depth budget, a
  fixture whose asserted property is silently broken, and a pooled-joint
  dependence claim.
- Null: randomized exact-rational worlds must fail `PIB-4`'s separation at a
  reported rate, and the no-alarm case must be asserted on the true fixtures.
- Byte-identical `RESULT_V1.json` under `python3 -I -B` and `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE2_PREDICTIVE_INFORMATION_LEARNABILITY_BOUNDARY_PROVED_AND_EXACTLY_WITNESSED_AT_REGISTERED_FINITE_SCOPE`

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`,
`MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`GENERAL_REASONING_REDUCED_TO_PREDICTION`, `COMPLETE_GMI`,
`CRYPTOGRAPHIC_HARDNESS_ASSUMED`, `INFINITE_HORIZON_EXTENSION`,
`CONTINUOUS_STATE_EXTENSION`, `UNIVERSAL_LEARNER_IMPOSSIBILITY`,
`GMI_MORPHOLOGY_PREDICTION`, `ARCHITECTURE_SELECTION_LAW`.

Parent-owned and not claimed novel: Shannon mutual information and its
independence characterization; Bayes decision theory; the
Csiszar-Kullback-Pinsker inequality; decision-tree and junta lower bounds for
parity; the doubling map's symbolic dynamics. The residual contribution is the
exact finite float-free instantiation, the `gain <= D/2` tightness witness, the
certified rational mutual-information bracket, and the registered fixture
roster with machine-checked defining properties.
