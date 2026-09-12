# GMI descriptor interval calibration v2

Status: **EXECUTED SYNTHETIC ESTIMATOR PILOT / B4 PARTIAL CLOSURE**

Date: 2026-09-12.

Purpose: move assumption-indexed descriptor bounds from theorem statements into a preregistered finite-sample coverage check.

## Registered simple descriptor regime

Three latent quantities are treated as iid Bernoulli rates in this pilot:

```text
required dependency-event frequency
predictive-target residual-event frequency
mode/context-event frequency
```

This is deliberately simpler than real high-dimensional structure. The point is to calibrate the uncertainty contract that later phase predictors must consume.

For `n` development observations and empirical rate `p_hat`, use

\[
r=\sqrt{\frac{\log(2/\delta_i)}{2n}},
\qquad
I=[\max(0,\hat p-r),\min(1,\hat p+r)].
\]

For three descriptors in one world, register `delta_i=0.05/3` so a union bound gives at least 95% simultaneous coverage under the iid assumption.

## Executed pilot

`run_gmi_descriptor_interval_calibration_v2.py` freezes:

```text
32 deterministic parameter cells
3 latent rates per cell
512 development observations per rate
seed = 20260912
```

The latent rates vary widely, including rare and common events. Protected/held-family outcomes are not used to repair intervals.

Result:

```text
96 intervals checked
96 true rates covered
0 misses
interval half-width = 0.06837605505628847
```

Receipt: `GMI_DESCRIPTOR_INTERVAL_CALIBRATION_RECEIPT_V2.json`.

## What this closes

At this simple iid rate scope, B4 now has an executed pre-outcome uncertainty mechanism rather than a point estimator.

## What remains open

```text
non-iid / correlated events
unseen structural categories
high-dimensional dependency sets
nonlinear residual rank/locality
mode-function geometry rather than mode frequency
phase-boundary regret and abstention on held families
charged extractor cost
```

A real descriptor is admitted only with its identifiability assumptions, interval and abstention rule.

## Claim ceiling

Synthetic iid Bernoulli coverage calibration only. It does not satisfy the full B4 C3/C5 target or establish useful real-world dependency/residual/specialization estimators.
