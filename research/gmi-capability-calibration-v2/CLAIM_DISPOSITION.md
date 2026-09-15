# Claim disposition — #766 / #602 Section M

## Scientific question

Can the frozen F4 capability predictor receive a genuine probabilistic error certificate on a prospectively frozen finite audit population without treating abstentions as successes or assuming iid/replacement sampling?

## V1 negative

#764 terminated `ASSAY_DEFECT_NONDETERMINATE_SAMPLING_FRAME`: its sample was frozen before the determinate frame was checked, and the predictor abstained on most sampled population cells. No redraw or #602 credit occurred.

## V2 result

At the registered selective finite-population scope:

- each coordinate has a predictor-only determinate frame of 64 cells from the fresh 1024-cell out-of-development candidate grid;
- 48/64 cells per coordinate were sampled uniformly without replacement after the frame commit and before scorer/oracle-result artifacts;
- all four frozen samples contain zero prediction errors;
- exact hypergeometric inversion at `delta_j=1/80` gives `U_j=3`, hence error-rate upper bound `3/64 < 1/20` for every coordinate;
- by union bound the simultaneous four-coordinate confidence level is at least `19/20`, with no independence premise;
- the post-certificate full-frame census has zero errors for all four coordinates and therefore lies within every realized bound;
- a complemented-predictor hostile has 48/48 sampled errors and fails the frozen gate on all four coordinates;
- an abstention hostile reduces determinate coverage to `27/32` and never counts abstentions as correct.

The most important limitation is selective coverage: the determinate frame is only `64/1024 = 1/16` of the registered candidate grid. The calibration claim concerns error conditional on this frame, not all candidate cells.

## Formal result

For fixed finite error population size `K`, `X~Hypergeometric(N,K,n)` under uniform sampling without replacement, and

`U_delta(x)=max{K : P_K(X<=x)>delta}`,

CAL-1 proves `P_K(K<=U_delta(X))>=1-delta`. The implementation independently verifies all finite cases through `N=20` using subset-count dynamic programming: 10,395 PMF cells and 12,320 coverage cases over four exact deltas.

## Evidence classes

- P1: exact finite-population inversion theorem; four-coordinate union-bound theorem; selective-risk accounting contract.
- P2: exhaustive finite checker, sample/frame custody hostiles, complement and abstention controls, normal/optimized receipt reproduction.
- P3 consequence: the frozen random-without-replacement sample produces the registered one-sided finite-population error certificates.
- no P4 real-world capability calibration claim.

## Strongest parents

Exact hypergeometric/finite-population confidence bounds and sampling without replacement; modern without-replacement confidence sequences; selective classification/risk-control and conformal risk-control methods. No statistical novelty is claimed.

## Claim ceiling

`EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME`

Not earned here: per-example probability calibration, iid/superpopulation validity, calibration on abstained cells, future-domain/real-world calibration, universal G6, or complete GMI.

## #602 consequence if merged and CI-green

Check only:

- `Calibrate capability-prediction uncertainty.`

Do not infer any broader V4, real-scale, or complete-GMI terminal from this certificate alone.
