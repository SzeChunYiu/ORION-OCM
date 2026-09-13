# Generalization attainment audit V1

Date: 2026-09-13

## Closed at the declared scope

The original GIR-1 proof conflated equality of infimum values with existence of an optimal predictor. The original GIR-6 first bullet then licensed a prediction from `R_gen<=epsilon` without checking attainment. Two worlds with identical observations, targets `-1,+1`, and output space `R` minus `{0}` refute the equality-boundary claim: every legal output has error `1+|y|>1`, although the infimum is `1`.

The corrected identity uses a single positive slack uniformly across observation fibers. The corrected prediction gate uses actual feasible-center sets and a selector in the declared predictor class. Strict radius slack suffices in the unrestricted class; equality requires feasibility evidence. Finite output spaces and compact metric output spaces supply fiberwise attainment. Finite world spaces alone do not. Existence of an adequate output does not certify an arbitrary proposed output, and set-theoretic existence does not establish measurable or physical realization.

The correction retains the full infimum identity instead of imposing unnecessary compactness on it. It also avoids making attainment of every local radius necessary: a globally adequate predictor may use nonoptimal centers on fibers whose radii are smaller than the global radius.

## Verification evidence

The original `grand_gmi_generalization_radius_checks_v1.py` and its frozen receipt are unchanged. Its five tests still cover 1,296 exact predictor problems and 37,422 observation-refinement cases.

The additive `grand_gmi_generalization_attainment_checks_v1.py` checks the analytically solved subclass of finite rational targets in a real output space with finitely many points removed. It records 144 target/tolerance cases, including four false licenses under the old value-only equality gate; 64 strictly positive slack witnesses; and 64 approximating outputs that never attain the boundary. Nine tests cover the equality failure, an extremely small exact rational slack, restored-center attainment, multiple excluded points, global attainment without all local minima, actual-output certification, and basic problem-domain assumptions.

The finite rational checks accompany the analytic counterexample and proof; they do not establish a general measurable-selection theorem. Reproduce with:

```bash
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_generalization*radius_v1.py' -v
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_generalization_attainment_v1.py' -v
python research/gmi-grand-unification-v1/grand_gmi_generalization_attainment_checks_v1.py --out research/gmi-grand-unification-v1/GRAND_GMI_GENERALIZATION_ATTAINMENT_RECEIPT_V1.json
```

## Recursive audit of adjacent claims

`EPISTEMIC_ACQUISITION_THEOREM_V1.md` restricts the experiment problem to finite worlds, finite experiments and finite outcomes. Its minimum over informative experiments therefore has no analogous nonattainment problem. Its continuous extension explicitly requires regularity and measurable selection. This audit does not certify all its other claims.

`CONTINUOUS_REALIZATION_BRIDGE_THEOREM_V1.md`, CRB-2, uses strictly positive approximation tolerance and claims only risk convergence. CRB-5 and CRB-6 separately delimit reachability and exact symbolic guarantees. `MEASURABLE_CONTINUOUS_GMI_THEOREM_V1.md`, GG49–GG51, already separates compact frontier existence and resource-infimum attainment. No matching value-to-attainment error was found in those passages.

One separate issue remains open for a following iteration: `ROBUST_DECISION_PRECISION_THEOREM_V1.md`, sections 0, 1 and 10, permits an arbitrary ecology with real pointwise losses and merely well-defined robust suprema. For `E=N`, any nonempty finite action set, and `L_n(a)=Lhat_n(a)=n`, the uniform error is zero but both robust scores are `+infinity`. The displayed absolute score difference and robust regret then involve undefined `infinity-infinity`. Finiteness of the action set secures a minimizer but does not secure finite scores. A repair must either require finite robust scores, or state an extended-real inequality-only result with additional finite-optimum conditions before subtracting scores. This issue is not closed by the GIR correction.

## Parent theory

The distinction between an optimization value, its attainment and positive-slack solutions is standard; see Boyd and Vandenberghe, [*Convex Optimization*, chapter 4](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf). The separate role of measurable selection in policy construction is documented by Yu and Bertsekas, [*A Mixed Value and Policy Iteration Method for Stochastic Control with Universally Measurable Policies*, sections 2.1 and 3.2](https://arxiv.org/html/1308.3814v3). This audit applies those parent boundaries to Grand GMI and makes no independent novelty claim for them.
