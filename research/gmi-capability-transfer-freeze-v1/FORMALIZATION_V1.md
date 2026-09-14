# F4 task-family transfer freeze v1

A task family is represented here only by its registered requirement vector `q` over the five signed capability-margin coordinates. A fixed system has capacity vector `c`. The transfer descriptor for a target task family is therefore

`z_target = c - q_target`.

The already-fitted development-world predictor receives only `z_target`; the opaque task-family identifier is never an input.

## Transfer-sufficiency theorem

At the registered scope, if two task families induce the same requirement vector, they induce the same signed margin vector for a fixed system. Any architecture-name-free predictor that is a function only of those margins must therefore return the same capability vector. `HTF_001` is the preregistered remint negative twin: it changes only opaque task-family identity, not requirements, and must preserve the source prediction exactly.

For a target family whose requirements differ, source success is not copied. The target margins are recomputed first and the frozen predictor is evaluated on that target point. This yields prospective transfer predictions and may legitimately produce `CANNOT_IDENTIFY` when the development corpus does not order-identify the target.

## Holdout design

The freeze contains six opaque target task families. Five have at least one signed margin outside the development cube `{-1,0,1}^5`; the sixth is the exact remint-invariance twin. The mixed family `HTF_006` creates `(memory=2, planning=-2, others=0)` and must preserve the predictor's planning abstention rather than post-hoc forcing a label.

No target outcome is present in this artifact. Each target row and the whole manifest carry SHA-256 receipts. Scoring belongs to a later commit/PR and must reference the committed freeze digest.

## Boundary

This is transfer under a sufficient registered requirement representation for fixed system morphology and development state. It does not cover task identity that carries additional causal information, adaptation during transfer, morphology change, or unregistered task interactions. Claim ceiling: **G2** until the frozen targets are independently scored.
