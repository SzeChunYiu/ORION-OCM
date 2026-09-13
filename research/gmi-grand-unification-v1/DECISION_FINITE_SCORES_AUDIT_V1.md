# Decision finite-score audit V1

Date: 2026-09-13

## Counterexample and repair

The original RDP setup permitted an arbitrary ecology and real pointwise losses but required only well-defined robust suprema. Let the ecology be the positive integers and let `L_n(a)=Lhat_n(a)=n` for each action. The loss-field error is exactly zero and every supremum is `+infinity`. The absolute score difference and regret relative to the optimal score would both subtract infinities. Finite action cardinality secures a minimizer but does not make its value finite.

The corrected main theorem requires a nonempty ecology, a nonempty finite action set, finite robust scores, and finite nonnegative uniform precision. The uniform loss bound then guarantees finite estimated scores. Neither ecology supremum must be attained. The proof retains the valid extension where some actions have `+infinity` score: finite uniform error preserves those actions' infinite status, and if any action has finite score then both minima are finite and the regret theorem applies. All-infinite problems do not produce finite-regret certificates. The absolute-difference formula is restricted to finite scores throughout.

Unique-action stability now states the singleton convention explicitly: with no competitors, `Delta=+infinity` and regret is zero. A unique finite-score action remains stable when every competitor has infinite score. At `Delta=2 delta`, a tie may be forced and a selected approximate minimizer may incur exactly `2 delta` regret. Thus the regret inequality remains inclusive while unique-action preservation requires the strict margin.

## Recursive selection boundary

The original morphology gate mentioned certified loss representation but did not expressly require the realization to select an estimated minimizer. Exact loss representation alone cannot certify an arbitrary action. The corrected gate requires selection evidence. If the chosen action has estimated suboptimality at most a finite `alpha>=0`, the same proof yields regret at most `2 delta+alpha`. A two-action witness with true scores `(0,3)`, estimated scores `(1,2)`, `delta=1` and `alpha=1` attains regret `3`; omitting selector slack would incorrectly claim the bound `2`.

These are sufficient bounds. Failure to meet them does not establish inadequacy when a sharper direct capability certificate exists. Selection resource cost still needs registered realization evidence; this iteration does not measure it or prove reachability.

## Verification

The original exact loss-field checker and receipt remain unchanged. Its five tests cover 2,985,984 field/perturbation instances. The additive checker covers 225 exact finite perturbation cases, 12 invalid score/precision domains, empty ecology rejection, and a case where equal robust scores hide a violated uniform loss-field bound. Twelve focused tests also cover singleton and infinite-score alternatives, equality ties, exact positive margin slack of `1/10^100`, and selection slack.

The new score-level helper does not infer an infinite-ecology uniform error bound from a finite list. The finite-field helper checks every supplied loss entry before deriving scores. Its rational arithmetic and explicit positive-infinity sentinel prevent undefined arithmetic from becoming a regret certificate. The infinite-ecology counterexample is proved analytically; the executable IEEE-infinity witness only demonstrates why subtracting infinities is invalid.

```bash
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_decision_precision_v1.py' -v
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_decision_finite_scores_v1.py' -v
python research/gmi-grand-unification-v1/grand_gmi_decision_finite_scores_checks_v1.py --out research/gmi-grand-unification-v1/GRAND_GMI_DECISION_FINITE_SCORES_RECEIPT_V1.json
```

The standard parent distinction between optimization values, feasible/optimal points and positive-slack selection is described in Boyd and Vandenberghe, [*Convex Optimization*, section 4.1.1](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf). The finite-error perturbation chain here is elementary and is not claimed as a new parent theorem. This bounded repair does not close arbitrary infinite-action, measurable-selection, statistical-certification or physical-realization problems.
