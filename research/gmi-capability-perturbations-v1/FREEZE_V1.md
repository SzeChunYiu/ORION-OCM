# T602-V4 prospective capability perturbations — freeze V1

Issue: #784  
Parent ledger: #602 V4  
Claim ceiling: `PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE`

## Frozen predictor authority

Pinned file:

`research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py`

Pinned Git blob:

`937b91f6a3787ff04c2b5209c81d249518406859`

Registered input axis order:

`(memory_margin, planning_margin, communication_margin, routing_margin, verification_margin)`

Registered output order:

`(memory_exact, planning_exact, coordination_exact, verified_tool_exact)`

The predictor is fit only on the full development grid `{-1,0,1}^5` and uses monotone envelopes. Held points below are frozen before any held scorer or result artifact exists. `C` means the exact string `CANNOT_IDENTIFY`; abstentions are reported separately and never counted as successes.

## Frozen independent capability oracle

For any integer-margin point:

- `memory_exact = 1[memory_margin >= 0]`
- `planning_exact = 1[memory_margin >= 0 and planning_margin >= 0]`
- `coordination_exact = 1[communication_margin >= 0]`
- `verified_tool_exact = 1[routing_margin >= 0 and verification_margin >= 0]`

The held scorer must implement this oracle independently rather than calling the predictor's oracle helper.

## P1 — component ablation

Main pair changes only memory margin:

- `A_pre  = (+2,0,0,0,0)`
- `A_post = (-2,0,0,0,0)`

Frozen oracle:

- `A_pre  -> (1,1,1,1)`
- `A_post -> (0,0,1,1)`

Frozen predictor:

- `A_pre  -> (1,1,1,1)`
- `A_post -> (0,0,C,C)`

The exact intervention-relevant deficit set is `{memory_exact, planning_exact}`.

Safe control:

- `A_safe_pre  = (+3,0,0,0,0)`
- `A_safe_post = (+2,0,0,0,0)`

Both oracle and predictor remain `(1,1,1,1)`.

## P2 — routing-resource repricing

Freeze routing budget `B=5`, routing demand `d=1`, and

`routing_margin = B - price*d`.

Main repricing `price: 3 -> 7` gives:

- `R_pre  = (0,0,0,+2,0)`
- `R_post = (0,0,0,-2,0)`

Frozen oracle:

- `R_pre  -> (1,1,1,1)`
- `R_post -> (1,1,1,0)`

Frozen predictor:

- `R_pre  -> (1,1,1,1)`
- `R_post -> (C,C,C,0)`

The exact direct deficit set is `{verified_tool_exact}`.

Safe repricing `price: 2 -> 3` gives routing margin `+3 -> +2`; both oracle and predictor stay `(1,1,1,1)`.

## P3 — environmental drift

Freeze

`communication_margin_after = communication_margin_before - drift_shock`.

Main pair:

- `D_pre  = (0,0,+2,0,0)`
- `shock = 4`
- `D_post = (0,0,-2,0,0)`

Frozen oracle:

- `D_pre  -> (1,1,1,1)`
- `D_post -> (1,1,0,1)`

Frozen predictor:

- `D_pre  -> (1,1,1,1)`
- `D_post -> (C,C,0,C)`

The exact direct deficit set is `{coordination_exact}`.

Safe drift starts at communication margin `+3`, shock `1`, and ends at `+2`; both oracle and predictor stay `(1,1,1,1)`.

## Required controls and falsifiers

The successor must fail closed if:

1. the pinned predictor blob changes;
2. any frozen held point or transformation law changes after activation;
3. a supposedly held main post point is substituted back inside the development grid;
4. an expected vector is edited after scorer/result authority exists;
5. a determinate predictor cell disagrees with the independent oracle;
6. a frozen abstention does not occur exactly where preregistered;
7. an abstention is counted as a success;
8. main deficit sets differ from the frozen sets;
9. safe controls change capability or abstain;
10. normal and `python -O` receipts differ.

Forbidden promotions:

- `UNIVERSAL_CAPABILITY_PREDICTOR`
- `REAL_WORLD_PERTURBATION_CALIBRATION`
- `CAUSAL_EFFECT_IDENTIFIED_OUTSIDE_REGISTERED_ORACLE`
- `G6_UNIVERSAL`
- `COMPLETE_GMI`

This lane is a bounded synthetic held-perturbation assay only.