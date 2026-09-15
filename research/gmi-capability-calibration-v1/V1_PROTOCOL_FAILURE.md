# V1 pre-outcome protocol failure — #764

The V1 freeze remains preserved and is not repaired in place.

After `FREEZE_V1.md` was committed, the frozen 128-cell outcome-free population was materialized exactly as specified. Before any audit sample was drawn and before any held oracle outcome/correctness/error bit was computed, the pinned F4 predictor was run only to determine whether each frozen cell was determinate or `CANNOT_IDENTIFY`.

The exact pre-outcome census is:

```text
coordinate            determinate   abstain   required sample
memory_exact          10            118       64
planning_exact        10            118       64
coordination_exact    10            118       64
verified_tool_exact   10            118       64
```

Each coordinate has only 10 determinate cells, so the frozen requirement to draw 64 distinct determinate cells without replacement is impossible.

Terminal:

```text
CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL
```

This is a protocol-design negative, not a statistical result about predictor accuracy. No sample manifest exists for V1; no oracle outcome was inspected; no threshold, confidence budget, or error count was changed after outcomes.

The cause is structural. The V1 population selected arbitrary points from `{-3,-2,2,3}^5`. F4's monotone-envelope predictor can determine an out-of-development point only when a development witness is componentwise comparable to that point. Mixed extreme coordinates usually destroy both the positive-lower and negative-upper witness conditions, producing `CANNOT_IDENTIFY`. Thus a nominal 128-cell population did not imply a 128-cell *determinate* population.

A scientifically valid successor must freeze a new V2 population rule that guarantees at least 128 determinate points **by predictor-visible geometry alone**, without consulting oracle outcomes. It may not resample V1 or alter V1 after this failure was observed.

Reproduction authority: `preoutcome_v1_census.py` → `V1_PREOUTCOME_CENSUS.json`.
