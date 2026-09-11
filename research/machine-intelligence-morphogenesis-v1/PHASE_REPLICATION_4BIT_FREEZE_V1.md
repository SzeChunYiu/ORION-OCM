# 4-bit description-complexity phase replication — freeze v1

Status: **FROZEN BEFORE 4-BIT ACQUISITION OUTCOME ANALYSIS**.

This is the prospective follow-up to the post-outcome 3-bit threshold observation. The 3-bit result itself is not reused as confirmatory evidence for this 4-bit outcome.

## Universe / basis

Target functions:

```text
f : {0,1}^4 -> {0,1}
```

Minimum description size is computed exactly over:

```text
leaves: x0,x1,x2,x3,0,1
operators: NOT, AND, XOR
syntax-tree node count
```

The exact complexity census is allowed as task classification; it is not an acquisition outcome.

## Strata

Frozen from the complexity census before acquisition scoring:

```text
SIMPLE  : minimum expression size <= 4
COMPLEX : minimum expression size >= 15
```

All SIMPLE functions are included.

For computational tractability, select exactly `256` COMPLEX functions with:

```text
random.Random(20260911).sample(sorted(complex_truth_tables), 256)
```

Selection depends only on truth-table identity + complexity threshold, not acquisition outcome.

## Training subsets

Training size:

```text
4 of 16 input rows
```

Use exactly `64` training subsets sampled prospectively from all `C(16,4)` subsets via:

```text
random.Random(20260911).sample(sorted(all_training_subsets), 64)
```

The same subsets are used for every target.

## Morphologies / policies

`M0 DIRECT_LABEL_MEMORY`:

```text
unseen query -> acquire correct label
cost L = 1.0
```

`M1 MDL_RULE_PROPOSER`:

- all 65,536 Boolean functions are the semantic hypothesis universe;
- retain functions consistent with four observed labels;
- restrict to minimum expression-size consistent hypotheses;
- if all minimum-size hypotheses agree on a held-out query, propose;
- otherwise abstain and acquire the label;
- exact verifier checks every proposal;
- wrong proposal is rejected and label is then acquired.

Frozen costs:

```text
L = 1.0
V = 0.5
```

Per held-out query:

```text
correct proposal: 0.5
wrong proposal:   1.5
abstain:          1.0
```

Synthesis/enumeration work remains a separate resource coordinate and is not included in this narrow information/verification price calibration.

## Frozen predictions

### R1 SIMPLE region

```text
mean_cost(M1 | SIMPLE) < 1.0
```

### R2 COMPLEX region

```text
mean_cost(M1 | COMPLEX) >= 1.0
```

### R3 phase separation

```text
mean_cost_COMPLEX > mean_cost_SIMPLE
```

All three must be reported independently.

## Claim boundary

This is still parent-owned MDL/version-space/value-of-verification economics. A positive result supports only:

```text
DESCRIPTION_COMPLEXITY_AND_VERIFIER_PRICE_PREDICT_PARENT_POLICY_REGION_AT_4BIT_SCOPE
```

It is a D3 **calibration of what a morphology phase law should look like**, not evidence for a new GMI mechanism.

## No-rescue rules

After acquisition outcomes are computed, do not change:

- complexity thresholds;
- `V/L=0.5`;
- number or seed of COMPLEX targets;
- training size/subset count/seed;
- hypothesis basis;
- unanimity/abstention rule;
- primary predictions.

If R2 fails because complex targets also favor M1, report it exactly.
