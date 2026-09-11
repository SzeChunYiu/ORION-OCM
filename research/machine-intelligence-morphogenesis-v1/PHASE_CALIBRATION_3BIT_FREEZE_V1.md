# Prospective 3-bit morphology phase calibration — freeze v1

Status: **FROZEN BEFORE OUTCOME ANALYSIS** in this branch.

Purpose: first prospective exact calibration of the Track-B statement

```text
ecology coordinate -> morphology/resource frontier prediction
```

using mature MDL/program-induction parents. No GMI novelty is claimed for the mechanism.

---

# 1. Universe

All `256` Boolean target functions

```text
f : {0,1}^3 -> {0,1}
```

are included. No target exclusion after outcome access.

Target complexity is the exact minimum expression size under the frozen basis:

```text
leaves: x0, x1, x2, constants 0/1
operators: NOT, AND, XOR
cost: syntax-tree node count
```

Enumerate expression semantics exactly until all 256 functions receive a minimum size.

---

# 2. Competing morphologies / policies

## M0 — DIRECT_LABEL_MEMORY parent

For every unseen query, request/acquire its correct label directly and store it.

Registered cost per unseen query:

```text
C_M0 = L = 1.0
```

No generalization claim.

## M1 — MDL_RULE_PROPOSER parent

Given exactly two labelled examples chosen from the eight input rows:

1. retain every target function in the complete 256-function semantic class consistent with the observed examples;
2. find the minimum registered expression size among consistent functions;
3. keep only consistent minimum-size hypotheses;
4. on an unseen query:
   - if all minimum-size hypotheses agree, propose that bit;
   - otherwise abstain and acquire the label;
5. every proposal is checked by an external exact verifier before commitment;
6. if the proposal is wrong, the verifier rejects it and the correct label is then acquired.

The learner receives no architecture/morphology label.

Registered costs:

```text
label acquisition L = 1.0
proposal verification V = 0.25
```

Thus per unseen query:

```text
correct proposal: V
wrong proposal:   V + L
abstain:          L
```

All synthesis/enumeration work is reported separately and is **not** silently omitted from any later whole-lifetime claim. This first phase calibration's primary scalar coordinate is information/verification acquisition cost only.

---

# 3. Exact evaluation

For every target function and every `C(8,2)=28` two-example training subset:

- evaluate all six held-out inputs;
- record correct proposals, wrong proposals and abstentions;
- compute mean registered acquisition cost relative to `M0=1.0` per held-out query.

Independent unit for this finite exact calibration is the target function; all training subsets are exhaustively averaged within target.

---

# 4. Frozen complexity strata

Before outcome analysis:

```text
SIMPLE:  minimum expression size <= 3
COMPLEX: minimum expression size >= 9
```

Middle-complexity functions remain in raw results but are not part of the primary directional prediction.

---

# 5. Frozen predictions

## P1 — simple-ecology advantage

For `SIMPLE` targets:

```text
mean acquisition cost(M1) < 1.0
```

because a simplicity-biased rule morphology should often make verifier-approved predictions from two examples.

## P2 — complexity penalty

For `COMPLEX` targets:

```text
mean acquisition cost(M1) >= mean acquisition cost(M1 | SIMPLE)
```

The stronger exploratory expectation is that M1 may lose or nearly lose its advantage over direct label memory as target structure becomes less aligned with the basis prior. Only the inequality above is frozen as confirmatory for this calibration.

## P3 — phase separation

```text
mean_cost_COMPLEX - mean_cost_SIMPLE > 0
```

with exact exhaustive computation, no asymptotic p-value needed.

---

# 6. Parent / claim boundary

This is a parent calibration for:

```text
MDL / Occam bias
version-space learning
program induction
value of verification
```

A positive result does **not** establish GMI or a new morphology law.

It establishes only that one registered ecology coordinate—description complexity relative to a basis prior—predicts a resource crossover between two parent learning organizations in an exact finite universe.

Allowed positive terminal:

```text
DESCRIPTION_COMPLEXITY_PREDICTS_PARENT_MORPHOLOGY_COST_REGION_AT_3BIT_SCOPE
```

Negative terminals:

```text
NO_REGISTERED_COMPLEXITY_PHASE_SEPARATION
MDL_RULE_PARENT_NOT_ADVANTAGEOUS_EVEN_ON_SIMPLE_STRATUM
ASSAY_DEFECT
```

---

# 7. No rescue rules

After results are computed, do not:

- change `V=0.25`;
- change training size `2`;
- redefine SIMPLE/COMPLEX thresholds;
- remove inconvenient functions;
- switch basis operators;
- change unanimity/abstention policy;
- use a different prediction as if it had been frozen.

A negative result becomes a Track-B calibration constraint.
