# Blind recovery prefix-code calibration — frozen protocol v1

Status: **method calibration / parent-owned coding theory.** Frozen before executing the enumeration script in this branch.

## Question

Can the Track-B pipeline:

```text
shared low-level morphology space
-> pre-outcome phase prediction
-> blind exhaustive search
-> post-hoc morphology classification
```

recover the expected phase transition without supplying labels such as `BALANCED` or `BIASED` to the search procedure?

This is intentionally a source-coding calibration, not an intelligence claim.

## Shared morphology space

Candidate morphology is only a 4-symbol binary prefix-code length vector

```text
d=(d1,d2,d3,d4)
```

with:

```text
di in {1,2,3}
Kraft sum_i 2^(-di) = 1
```

The search program receives no architecture/morphology class labels.

## Ecology

\[
P_p=[p/2,p/2,(1-p)/2,(1-p)/2].
\]

Evaluate:

```text
p = 0.10, 0.25, 0.50, 0.75, 0.90
```

Primary cost is exact expected code/proposal depth:

\[
C(d,p)=\sum_i P_p(i)d_i.
\]

Ties are retained; no post-hoc tie-breaker selects the desired class.

## Frozen prediction

From the analytic structure-to-geometry calculation, predict:

```text
p < 1/3:
  an asymmetric/bias code favoring the second pair should beat the balanced depth-(2,2,2,2) form.

1/3 <= p <= 2/3:
  balanced depth-(2,2,2,2) should be Pareto/expected-depth optimal (with equality possible at boundaries).

p > 2/3:
  an asymmetric/bias code favoring the first pair should beat balanced.
```

For the registered points:

```text
0.10 -> BIASED_TO_SECOND_PAIR
0.25 -> BIASED_TO_SECOND_PAIR
0.50 -> BALANCED
0.75 -> BIASED_TO_FIRST_PAIR
0.90 -> BIASED_TO_FIRST_PAIR
```

## Classifier defined before search

After enumeration only, classify a winning vector:

```text
BALANCED:
  sorted depths == [2,2,2,2]

BIASED_TO_FIRST_PAIR:
  sorted depths == [1,2,3,3]
  AND the two shortest depths are assigned to indices {0,1}

BIASED_TO_SECOND_PAIR:
  sorted depths == [1,2,3,3]
  AND the two shortest depths are assigned to indices {2,3}

OTHER:
  anything else
```

Because equal-probability members of a pair may swap depth 1/2, both permutations remain the same post-hoc class.

## Parent / claim boundary

This is exactly the kind of result expected from Huffman/source coding and Kraft inequality. A positive is **not GMI evidence**.

It only validates that the Track-B methodology can make a morphology-region prediction, search a label-free structural space, and recover the predicted region exactly.

## Terminals

```text
BLIND_RECOVERY_CALIBRATED_ON_PREFIX_CODE_PARENT
PREDICTED_PREFIX_PHASE_NOT_RECOVERED
ASSAY_DEFECT
```

A positive calibration does not authorize #221/#220 morphology search.