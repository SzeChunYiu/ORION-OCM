# V1 pre-outcome protocol failure — #764

The V1 freeze remains preserved and is not repaired in place.

After `FREEZE_V1.md` was committed, the frozen 128-cell outcome-free population was materialized exactly as specified. An outcome-free OS-random 64-id sample was then committed as `AUDIT_SAMPLE_V1.json` at commit `1f1da8f3c14df07736bc2f5053a706b2fb35e192`; its own custody fields state that no oracle outcome had been seen before that commit.

The V1 freeze, however, required **64 distinct determinate cells per coordinate**, not merely 64 arbitrary population ids. Before accepting or scoring that sample, the pinned F4 predictor can be run without any oracle labels to count determinate versus `CANNOT_IDENTIFY` cells. The exact predictor-only census is:

```text
coordinate            determinate   abstain   required determinate sample
memory_exact          10            118       64
planning_exact        10            118       64
coordination_exact    10            118       64
verified_tool_exact   10            118       64
```

Each coordinate has only 10 determinate cells. Therefore no 64-cell determinate sample exists. By pigeonhole alone, **any** 64-id sample from that population contains at least 54 abstentions. The already-committed V1 sample is consequently preserved as outcome-free custody history but rejected as scientifically invalid under the frozen sampling contract.

Terminal:

```text
CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL
```

This is a protocol-design negative, not a statistical result about predictor accuracy. No V1 calibration certificate/result is accepted from the invalid sample; its identities are never resampled or repaired after the fact. The pre-outcome census itself reads no oracle outcome. No threshold, confidence budget, epsilon or error definition is changed because of V1.

The cause is structural. The V1 population selected arbitrary points from `{-3,-2,2,3}^5`. F4's monotone-envelope predictor can determine an out-of-development point only when a development witness is componentwise comparable to that point. Mixed extreme coordinates usually destroy both the positive-lower and negative-upper witness conditions, producing `CANNOT_IDENTIFY`. Thus a nominal 128-cell population did not imply a 128-cell *determinate* population.

V2 therefore freezes a new population-construction rule that guarantees a sufficiently large determinate pool **using predictor-visible geometry only**, before any oracle labels. V1 remains visible and unchanged as the failed preregistration generation.

Reproduction authority: `AUDIT_SAMPLE_V1.json` + `preoutcome_v1_census.py` → `V1_PREOUTCOME_CENSUS.json`.
