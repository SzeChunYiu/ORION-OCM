# Section D Phase Winners V2 — Frozen-Prediction Failure Record

Pre-outcome authority: `FREEZE_V2.md` at commit `b8c407428cfb76dda736d9867e50c1c8a365eabb`.

## Failure

The first scored exhaustive check after the freeze falsified frozen prediction **N3**.

The freeze predicted that the best `one Hamming-weight cutoff + exceptions` approximation to

```text
y(x) = 1 iff HammingWeight(x) = 4,  x in {0,1}^8
```

would require 56 correction keys, for total persistent description `2 + 56 = 58`.

Exhaustive enumeration over every integer cutoff and both polarities gives instead:

```text
minimum corrections = 70
```

The reason is simple and important: the frozen reasoning forgot the legal constant-zero member of the cutoff family. A cutoff above the maximum Hamming weight (equivalently the all-zero base) makes errors only on the 70 positive shell points. No nonconstant cutoff does better.

So the correct observed description size for that candidate is:

```text
2 + 70 = 72 cells.
```

## Consequence

`FREEZE_V2.md` explicitly says that any mismatch is a failed frozen prediction and must not be repaired after outcomes. Therefore **V2 as a whole is failed**. The freeze is intentionally left unchanged.

This failure does **not** reverse the qualitative memory-cap prediction for the N held-out point: 72 is still above the frozen 32-cell cap, while the registered weighted-local-composition construction uses 21 cells. But that qualitative survival is not used to declare the neural-like box closed from V2, because the quantitative preregistration failed.

## Scientific disposition

The correction will be tested only on a new held-out shell with a fresh pre-outcome freeze. The new test must derive the best cutoff residual analytically including constant functions before any exhaustive result is generated.

The P (probabilistic) and S (online-planning) subtests remain separately preregistered by the same immutable V2 freeze. Their outcomes may be reported as their own prospective subtests, but no document may call the full V2 suite a pass.

## Claim ceiling

```text
FAILED_PREREGISTRATION_V2
NO_NEURAL_PHASE_CLOSURE_FROM_V2
P_AND_S_SUBTESTS_REMAIN_SEPARATELY_TESTABLE
```