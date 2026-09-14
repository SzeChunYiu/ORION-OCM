# Prospective held-family capability score v1

## Scope

This capsule scores the immutable freeze committed by PR #682, digest
`cee4b92e9ca524d8d57d6f60c8fe529529216f13602a8a1f1b633a8c8fa3106a`.
The six held families were outside the development cube and frozen before this scoring artifact existed.

The held oracle is independent of the fitted predictor. For signed margins `(m,p,c,r,v)` it evaluates the registered exact obligations directly:

- memory exact iff `m >= 0`;
- planning exact iff `m >= 0` and `p >= 0`;
- coordination exact iff `c >= 0`;
- verified tool use exact iff `r >= 0` and `v >= 0`.

## Exact result

There are `12 members × 4 capability cells = 48` held cells.

The frozen predictor made 20 determinate predictions and 28 `CANNOT_IDENTIFY` predictions. All 20 determinate predictions equal the independent oracle:

- determinate accuracy: `20/20 = 1`;
- coverage: `20/48 = 5/12`;
- abstention: `28/48 = 7/12`;
- determinate errors: `0`.

Abstentions are not counted as successes. Hence this is a selective prediction result, not a claim of 48/48 prediction.

## Family-level signatures

- `HF_UPPER_RAY`: all four registered capabilities are frozen strengths and all are confirmed.
- `HF_STATE_DEFICIT`: frozen memory and planning failures are confirmed.
- `HF_PLAN_DEFICIT`: frozen planning failure is confirmed.
- `HF_COMM_DEFICIT`: frozen coordination failure is confirmed.
- `HF_ROUTE_DEFICIT`: frozen verified-tool failure is confirmed.
- `HF_VERIFY_DEFICIT`: frozen verified-tool failure is confirmed.

No claim is made for cells where the predictor abstained.

## Claim boundary

This supports prospective capability property prediction for the six registered exact structural families at **G3**. It does not establish a general G6 morphology-to-capability map, canonical named-family coverage, transfer across task families, resource-repricing prediction, drift prediction, or real-regime replication.

## Falsification

The result fails if any determinate frozen prediction disagrees with the independent oracle, if the committed freeze content no longer recomputes to its preregistered digest, or if an abstention is silently scored as correct.
