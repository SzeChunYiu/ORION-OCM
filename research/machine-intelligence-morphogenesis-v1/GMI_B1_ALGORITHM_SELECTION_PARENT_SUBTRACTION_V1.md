# B1 algorithm-selection parent subtraction v1

Status: **PARENT-FIRST THEORY AUDIT — NO GMI POSITIVE**

Date: 2026-09-12. Fresh-main base: `b7316ad210eb1649cb07bf62e59c044c7ca2e520`.

Refs: #377, #233, #373; `GMI_PARENT_PREDICTION_DISCRIMINATION_V1.md`; `GMI_QUANTITATIVE_PREDICTIVE_CLOSURE_V1.md`; `GMI_E1_E3_THEORY_VALIDATION_GATE_V2.md`.

## 1. Why this parent matters to B1

After subtracting the A2-A5 atomic mechanism rules, an obvious successor is:

> measure ecology/obligation/resource features, then predict which morphology or mechanism combination will perform best.

That generic schema is not new. It is a direct instance of the classical **algorithm selection problem** when the candidate morphologies are treated as algorithms/solvers and the ecology description is treated as the problem-instance feature vector.

Primary parents:

- John R. Rice (1976), *The Algorithm Selection Problem*, Advances in Computers 15, 65-118, DOI `10.1016/S0065-2458(08)60520-3`: formalizes selection among algorithms using problem features and performance criteria.
- Xu, Hutter, Hoos & Leyton-Brown (2008), *SATzilla: Portfolio-based Algorithm Selection for SAT*, JAIR 32, DOI `10.1613/jair.2490`: learns feature-based per-instance performance models and selects a solver from a portfolio.
- Kerschke, Hoos, Neumann & Trautmann (2019), *Automated Algorithm Selection: Survey and Perspectives*, Evolutionary Computation 27(1), DOI `10.1162/evco_a_00242`: surveys feature-based per-instance algorithm selection, configuration, scheduling and portfolios across domains.

Therefore B1 must not count a generic learned mapping

`ecology/features -> best known morphology`

as a GMI-specific predictive law.

## 2. AS-1 — selection-schema containment [P1]

Let:

```text
X    registered pre-outcome ecology/obligation/resource features
M    a finite portfolio of already supplied candidate morphologies
Y    registered performance/resource outcome
s    a predictor/selector mapping X to a member or distribution over M
```

If a claimed GMI predictor only chooses among the supplied `M` using `X` in order to optimize a registered criterion over `Y`, then it is an instance of the algorithm-selection schema.

This is a classification by mathematical object, not by implementation name. A neural selector, rule-based selector, regression model, Bayesian selector or hand-derived lookup table can all instantiate the same parent problem.

Consequently, empirical success of `s` over one fixed default morphology establishes at most a successful algorithm-selection system unless an additional GMI residual is prospectively identified.

## 3. What can remain genuinely Track-B-relevant

The parent subtraction does **not** make Track B empty. It sharpens the residual into stronger objects that algorithm selection does not supply merely by definition.

### R1 — theory-derived structural prediction

GMI may earn a residual if it freezes a restricted functional/causal law before protected outcomes and that law transfers where a generic feature-to-performance learner does not have enough family-specific data to fit the mapping.

Examples of admissible targets:

```text
same intervention direction across excluded morphology families;
quantitative crossover from independently measured semantic/resource terms;
mechanism-core necessity derived from future distinguishability;
calibrated prediction for a held-out structural family with no family identity/proxy.
```

The comparator must still include a strong algorithm selector using the same legal development data and feature-extraction budget.

### R2 — generation rather than portfolio choice

Selecting from a supplied morphology portfolio is weaker than generating a morphology from a neutral primitive basis.

Track B can therefore exceed algorithm selection only if the candidate is not merely handed to the selector: the registered basis/search must construct it under a charged resource bound, and alternate encodings/search priors must survive.

This residual is central to C4/E3 and remains entirely OPEN.

### R3 — prospective non-parent-equivalent form

A new-form claim requires the predicted property complex to be frozen before a neutral search and then recovered through multiple low-level implementations, followed by bounded reduction attacks against the strongest parents.

A selector choosing a pre-named RQM/VLC/VRQM arm from a portfolio cannot satisfy that requirement.

### R4 — developmental acquisition law

Track B may also exceed static algorithm selection if it predicts how inherited developmental history changes the **process that generates future morphologies** under fresh tasks, rather than merely choosing among a fixed portfolio. This connects to #233 HST and #373's higher claim rungs, but is not established by the present tranche.

## 4. Comparator requirement for B1/C5

Any future B1 held-family tournament that predicts frontier morphology/mechanism membership from pre-outcome features should include at least:

```text
P0 constant/best-global morphology parent
P1 family-native strongest analytic predictors
P2 generic feature-based algorithm selector trained on the same D/V worlds
P3 resource-rational/full-cost selector using the same legal cost terms
P4 GMI restricted law under test
```

Rules:

```text
same legal pre-outcome information for P2-P4;
feature extraction/search/tuning costs charged;
no protected family identity or outcomes;
P2 model class and tuning budget frozen before P;
P4 must declare its structural restriction/prediction difference before P;
if P4 reduces to an unrestricted feature learner, classify it under P2 rather than as GMI novelty.
```

A strong GMI result is not `P4 beats P0`. It requires a residual against P1-P3 under the frozen held-family/intervention contract.

## 5. Kill / narrowing terminals

```text
ALGORITHM_SELECTION_PARENT_SUFFICIENT
STATIC_FEATURE_SELECTOR_ONLY
NO_HELD_FAMILY_STRUCTURAL_RESIDUAL
GENERATION_NOT_TESTED__PORTFOLIO_ONLY
FAMILY_IDENTITY_REQUIRED_FOR_PREDICTION
PARENT_SELECTOR_UNDERBUDGETED
```

These are valid scientific results and must be preserved.

## 6. Consequence for the current B1 next step

The next B1 artifact should **not** be an arbitrary regression/classifier from `Xi_obl,P` to morphology labels. That would test the algorithm-selection parent problem again.

The next admissible candidate should instead freeze a small, theory-derived relation whose variables and coefficient/sign/threshold structure are justified independently of the held-family outcomes. It must then be compared to a strong feature-based algorithm selector and native/resource parents using the same legal information.

If no such restricted relation can be justified without reading the protected outcomes, then B1 should remain `OPEN` or terminate `ALGORITHM_SELECTION_PARENT_SUFFICIENT` at that scope.

## 7. Claim ceiling

This parent audit establishes no empirical phase law and no generating basis. It only removes another broad source of false novelty:

> predicting the best member of a known morphology portfolio from ecology features is, by itself, algorithm selection.

Track B still has to earn a residual through theory-derived transfer, resource-bounded generation, developmental acquisition, or prospectively recovered non-parent-equivalent morphology.
