# RSI-7 — a zero-cost probe under the active policy: 0.818 at 2.93 per verified improvement

The RSI-6 residual was C2 → C1 on the LUNARC lifetime worlds. The mechanism says C1 is
*displacement* — compression selects different fragments than frequency — while complete
recovery means both selections agree. So the probe is **library stability under
reselection**: the Jaccard overlap of the frequency and MDL libraries. Both are already
computed in the dev phase; the probe costs nothing.

It varies as the mechanism predicts: lifetime worlds (full recovery) **0.75**; D1/D2
0.59; the displaced C1 worlds 0.28–0.45.

## Result — 33-case packet

| policy | gen | cost | accuracy | cost / verified improvement |
|---|---|---|---|---|
| exhaustive | G6 | 1 023 | 0.758 | 40.92 |
| exhaustive | G7 | 1 023 | 0.758 | 40.92 (unchanged — outvoted) |
| **active** | G6 | 260 | 0.576 | 13.68 |
| **active** | **G7** | **79** | **0.818** | **2.93** |

Under the active policy the two zero-cost probes (`admitted`, `lib_overlap`) run first and
settle most cases before any paid probe fires — 79 slots across 33 cases. Confusion at
active G7: C0 9/9, C1 11/13, **C2 6/9** (from 2/9), C5 1/1; C3 still called C1.

Under exhaustive probing the same probe changes nothing: every paid probe runs and the
stronger paid likelihoods outvote it. **The gain is an interaction between the probe set
and the policy**, not a property of the probe alone — which is itself an L6-relevant
finding: the improvement process has two coupled parts.

## Slope status, stated exactly

```text
active, G4 → G7:  accuracy 0.455 → 0.455 → 0.576 → 0.818   (monotone non-decreasing)
                  cost/verified 14.13 → 10.73 → 13.68 → 2.93   (G6 rose; G7 the largest fall)
full G0 → G7:     TERMINAL NO_IMPROVING_SLOPE                 (G0–G2 rose)
```

The strict terminal requires monotone non-increasing cost over *every* generation; it is
not met. What is established: three consecutive probe additions, each localised by the
previous generation's confusion, each derived from the mechanism, took the active
diagnoser from 0.455 to 0.818 and its cost per verified improvement from 14.13 to 2.93.

## Repair catalogue made honest

`C2 → REDUCE_K_OR_RAISE_P` was stale: what actually fixed the depth-limited worlds in this
lane was depth-aware per-target deployment (the probe gate with cost-depth). The catalogue
now says `C2 → DEPTH_AWARE_DEPLOYMENT`, and D1/D2's validated repair is recorded as that.
