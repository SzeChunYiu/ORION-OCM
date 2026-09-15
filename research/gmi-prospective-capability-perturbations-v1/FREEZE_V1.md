# #784 freeze — prospective held capability perturbations V1

Date: 2026-09-15. Parent ledger: #602 V4. Child issue: #784.

This is the pre-scoring authority. No held scorer, scored receipt, test, or dedicated workflow for this lane exists on this branch before this commit.

## Claim boundary

Target only:

```text
PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE
```

This lane may establish that the pinned F4 architecture-name-free monotone predictor prospectively gets the registered **direct perturbation deficits** right on held out-of-development margin points for one component ablation, one exact resource repricing map, and one exact environmental-drift map, while preregistered unrelated cells may fail closed with `CANNOT_IDENTIFY` and do not count as successes.

It may not claim universal perturbation prediction, real-world causal effects, universal G6, or complete GMI.

## Pinned predictor and oracle authority

Pinned source:

```text
research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py
Git blob: 937b91f6a3787ff04c2b5209c81d249518406859
```

Registered axis order:

```text
(memory_margin, planning_margin, communication_margin, routing_margin, verification_margin)
```

Capability-vector order:

```text
(memory_exact, planning_exact, coordination_exact, verified_tool_exact)
```

Independent oracle semantics:

```text
memory_exact        = int(memory_margin >= 0)
planning_exact      = int(memory_margin >= 0 and planning_margin >= 0)
coordination_exact  = int(communication_margin >= 0)
verified_tool_exact = int(routing_margin >= 0 and verification_margin >= 0)
```

Development fitting points use only `{-1,0,1}^5`. Every decisive main post point below contains a `-2`; safe-control points contain `+2` or `+3` and are also outside the development grid.

`C` below is literal predictor terminal `CANNOT_IDENTIFY`. It is not correctness and must be reported separately.

## Frozen opaque cases and predictions

Case IDs are non-semantic; scorer behavior must depend on points/transform contracts only.

### A — component ablation

Transformation:

```text
memory_margin_after = -2
all other margins unchanged.
```

Main pair:

```text
A0_pre  = (+2,0,0,0,0)
A0_post = (-2,0,0,0,0)
```

Frozen independent oracle:

```text
A0_pre  = (1,1,1,1)
A0_post = (0,0,1,1)
```

Frozen predictor result:

```text
A0_pre  = (1,1,1,1)
A0_post = (0,0,C,C)
```

Frozen determinate direct-deficit set:

```text
{memory_exact, planning_exact}.
```

Frozen post-ablation abstention set:

```text
{coordination_exact, verified_tool_exact}.
```

Safe capacity reduction:

```text
A1_pre  = (+3,0,0,0,0)
A1_post = (+2,0,0,0,0)
```

Both oracle and predictor are frozen as `(1,1,1,1)`.

### R — resource repricing

Exact registered map:

```text
routing_budget B = 5
routing_demand d = 1
routing_margin = B - price*d
```

Main prices:

```text
price_before = 3 -> routing_margin +2
price_after  = 7 -> routing_margin -2
```

Main pair:

```text
R0_pre  = (0,0,0,+2,0)
R0_post = (0,0,0,-2,0)
```

Frozen oracle:

```text
R0_pre  = (1,1,1,1)
R0_post = (1,1,1,0)
```

Frozen predictor:

```text
R0_pre  = (1,1,1,1)
R0_post = (C,C,C,0)
```

Frozen determinate direct-deficit set:

```text
{verified_tool_exact}.
```

Frozen post-repricing abstention set:

```text
{memory_exact, planning_exact, coordination_exact}.
```

Safe repricing:

```text
price 2 -> margin +3
price 3 -> margin +2
R1_pre  = (0,0,0,+3,0)
R1_post = (0,0,0,+2,0)
```

Both oracle and predictor are frozen `(1,1,1,1)`.

### D — environmental drift

Exact map:

```text
communication_margin_after = communication_margin_before - drift_shock.
```

Main pair:

```text
D0_pre  = (0,0,+2,0,0)
shock   = 4
D0_post = (0,0,-2,0,0)
```

Frozen oracle:

```text
D0_pre  = (1,1,1,1)
D0_post = (1,1,0,1)
```

Frozen predictor:

```text
D0_pre  = (1,1,1,1)
D0_post = (C,C,0,C)
```

Frozen determinate direct-deficit set:

```text
{coordination_exact}.
```

Frozen post-drift abstention set:

```text
{memory_exact, planning_exact, verified_tool_exact}.
```

Safe drift:

```text
D1_pre  = (0,0,+3,0,0)
shock   = 1
D1_post = (0,0,+2,0,0)
```

Both oracle and predictor are frozen `(1,1,1,1)`.

## P4-1 — prospective scoring contract [P2 protocol]

The held scorer must:

1. verify the pinned predictor Git blob before importing it;
2. reconstruct every post point from its frozen transformation metadata and pre point rather than trusting a duplicated post vector;
3. independently compute the oracle vector from the frozen threshold definitions;
4. run the pinned predictor without target/family labels;
5. compare the full predictor vector to the frozen predictor vector, including every expected `CANNOT_IDENTIFY`;
6. require every determinate predictor cell to equal the independent oracle cell;
7. report abstentions separately and never include them in an accuracy numerator;
8. require the main determinate deficit sets and safe-control no-change results exactly as frozen.

No post-outcome point, price, shock, expected vector or abstention set mutation is permitted.

## Frozen hostile controls

- **predictor source drift:** any Git-blob mismatch fails before scoring;
- **repricing arithmetic mutation:** change B, d, or either price and require reconstructed margin mismatch to fail;
- **drift arithmetic mutation:** change shock or post point and fail;
- **hidden development-grid substitution:** replacing a decisive ±2/±3 held point by an all-`{-1,0,1}` point fails the held-domain gate;
- **outcome-aware expected vector mutation:** changing any frozen expected oracle/predictor cell causes receipt/test failure;
- **abstention laundering:** replacing `CANNOT_IDENTIFY` with the correct oracle value must fail rather than improve reported success;
- **safe-control sensitivity:** A1/R1/D1 must remain fully determinate all-ones vectors; otherwise the lane fails.

## Frozen receipt requirements

Receipt must contain:

- issue/parent/freeze/predictor-blob/claim ceiling;
- development-grid definition;
- every opaque case with pre point, exact transform metadata, reconstructed post point, independent oracle vectors, predictor vectors;
- per-case determinate-cell count, determinate-correct count, abstention count;
- direct-deficit and abstention sets;
- aggregate determinate accuracy with abstentions excluded from denominator;
- safe-control all-ones assertions;
- hostile-control dispositions;
- explicit forbidden claims.

Normal Python and `python -O` must emit byte-identical receipts.

## Falsifiers

This lane is falsified if the pinned source blob differs; transformation reconstruction differs from a frozen post point; any determinate cell disagrees with its oracle; any expected abstention becomes a determinate prediction or any expected determinate cell abstains; main direct-deficit sets differ; safe controls change; held points silently fall into the development grid; an abstention is counted as success; normal and optimized output differ; or wording exceeds the registered synthetic prospective-perturbation scope.
