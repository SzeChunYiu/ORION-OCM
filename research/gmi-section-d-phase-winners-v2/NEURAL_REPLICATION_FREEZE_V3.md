# Section D Neural-like Phase Replication V3 — Pre-outcome Freeze

This is a **new held-out replication** created only after the V2 quantitative cutoff-residual prediction failed. It does not edit or rescue `FREEZE_V2.md`.

No exhaustive V3 truth-table result, result JSON, or scored witness output may be generated before this file exists in Git history.

## Target

Input:

```text
x in {0,1}^9
```

Obligation:

```text
y(x) = 1 iff HammingWeight(x) = 4.
```

Hard persistent-memory cap:

```text
persistent_cells <= 32.
```

Remint permutation:

```text
pi_V3 = (8, 3, 0, 6, 1, 7, 4, 2, 5).
```

The candidate grammar is the same architecture-name-free mechanism set as the N world in `FREEZE_V2.md`: full map, default+exceptions, GF(2)-affine fold, one Hamming-weight cutoff (either polarity), one cutoff+exceptions, and generic weighted-local-composition from weighted sums plus scalar thresholds. No named exact-count/shell macro is legal.

## Analytic predictions frozen before exhaustive evaluation

### Full map

```text
2^9 = 512 persistent cells.
```

Over cap.

### Default + exceptions

The positive shell has

```text
C(9,4) = 126
```

points, fewer than the 386 negatives, so default zero plus positive exceptions requires:

```text
1 + 126 = 127 persistent cells.
```

Over cap.

### GF(2)-affine fold

Predicted inexact. A single exact Hamming shell of weight 4 is not an affine Boolean function.

### One cutoff

Predicted inexact. A single monotone cutoff or its complement cannot isolate one interior shell.

### One cutoff + exceptions

This prediction explicitly includes constant cutoff functions, the omission that broke V2.

For positive-polarity `1[weight >= t]`:

- if `t >= 5`, the base is disjoint from the target shell, so error is `126 + tail(t) >= 126`, with equality at the constant-zero cutoff `t=10`;
- if `t <= 4`, the base contains the shell and at least every point of weights 5..9, whose count is 256, so error is at least 256.

For complement polarity `1[weight < t]`:

- if `t <= 4`, the base is disjoint from the target shell, so error is `126 + lower(t) >= 126`, with equality at the constant-zero complement `t=0`;
- if `t >= 5`, the base contains the shell plus at least weights 0..3, whose total is `1+9+36+84 = 130`, so error is at least 130.

Therefore the frozen exact minimum correction count is:

```text
126
```

and cutoff+exceptions requires:

```text
2 + 126 = 128 persistent cells.
```

Over cap.

The exhaustive witness must enumerate every cutoff and both polarities and fail this V3 prediction if it finds anything below 126.

### Weighted local composition

Construct:

```text
h4 = 1[sum_i x_i >= 4]
h5 = 1[sum_i x_i >= 5]
y  = h4 AND (NOT h5)
```

with generic threshold units only.

Parameter-cell accounting:

```text
h4: 9 weights + 1 threshold = 10
h5: 9 weights + 1 threshold = 10
out: 2 weights + 1 threshold = 3
total = 23 persistent cells.
```

Predicted exact on all 512 inputs and under the 32-cell cap.

Frozen held-out prediction:

```text
weighted_local_composition is the unique valid frozen candidate under cap 32,
therefore the unique exact Pareto winner.
```

## Negative twin

For

```text
y_twin(x) = 1[HammingWeight(x) >= 4]
```

a single cutoff is exact with two description cells. The deeper weighted composition must not be selected as a universal winner.

## Stochastic-search replication

Use the same Search B algorithm frozen in `FREEZE_V2.md`, seeds 0..99, 64 proposals, over the six V3 candidates. At least 95/100 seeds must retain the exact V3 winner. Candidate family names remain hidden until selection.

## Parent boundary

Any passing result remains parent-owned by classical threshold logic / threshold circuits. The only GMI residual is prospective cross-morphology phase selection under the common resource protocol.

## Claim ceiling

```text
FINITE_EXACT_PROSPECTIVE_NEURAL_LIKE_PHASE_REPLICATION_V3
PARENT_OWNED_THRESHOLD_LOGIC
NO_NEURAL_EXCLUSIVITY_OR_REAL_SCALE_CLAIM
```