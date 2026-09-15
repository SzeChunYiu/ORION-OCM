# Erratum to immutable FREEZE_V2.md — V1 sample-history sentence

`FREEZE_V2.md` remains immutable as the preregistered V2 authority. One historical sentence in its opening description is inaccurate: it says that no V1 sample occurred.

The repository history shows that an **outcome-free** V1 sample manifest, `AUDIT_SAMPLE_V1.json`, was committed at `1f1da8f3c14df07736bc2f5053a706b2fb35e192` after the V1 population. That sample contains 64 arbitrary population ids per coordinate and its own custody metadata states that no oracle outcomes had been seen before the sample commit.

This does not rescue or contaminate V1. The V1 freeze required a sample of 64 **determinate** cells per coordinate. The predictor-only census, which needs no oracle labels, proves that the entire 128-cell V1 population contains only 10 determinate cells per coordinate. Hence no valid 64-determinate-cell sample exists; any 64-id sample contains at least 54 abstentions. V1 therefore remains:

```text
CANNOT_EXECUTE_FROZEN_SAMPLE_DETERMINATE_POPULATION_TOO_SMALL
```

V2's population rule, sample size, confidence budgets, epsilon, statistical theorem and negative controls are unchanged. No V2 statistical choice depends on the erroneous historical sentence. This erratum is deliberately separate from the immutable freeze so the preregistration history is not rewritten after outcomes.
