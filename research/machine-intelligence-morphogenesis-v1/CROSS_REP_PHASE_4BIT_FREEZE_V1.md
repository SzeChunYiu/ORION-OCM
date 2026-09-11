# Cross-representation 4-bit phase calibration — freeze v1

Status: **FROZEN BEFORE LEARNER OUTCOME ANALYSIS**.

Purpose: first exact finite calibration where the competing organizations are different **representation/hypothesis morphologies**, not merely two serving policies over the same hypothesis language.

This remains classic inductive-bias/version-space parent territory. No GMI novelty is attributed to a positive.

---

# 1. Common task universe

All Boolean functions

```text
f : {0,1}^4 -> {0,1}
```

with the same 16 input rows.

The learner sees exactly four labelled rows and is evaluated on the remaining 12.

Training subsets:

```text
64 subsets from C(16,4)
random.Random(20260911).sample(sorted(all_subsets),64)
```

Same subsets for every target and both morphologies.

---

# 2. Morphology H_T — bounded linear-threshold representation

Hypothesis class consists of every distinct Boolean truth table obtainable from

\[
1[\sum_i w_i x_i+b\ge 0]
\]

under the prospectively fixed parameter grid:

```text
w_i in {-2,-1,0,1,2}
b   in {-4,-3,...,4}
```

Duplicate truth tables are quotient together.

Pre-outcome class census:

```text
|H_T| = 980 distinct functions
```

This is a tiny parametric/threshold morphology analogue, not a trained neural network.

---

# 3. Morphology H_P — bounded program-expression representation

Hypothesis class is every distinct Boolean truth table whose exact minimum expression size is `<=8` under:

```text
leaves: x0,x1,x2,x3,0,1
operators: NOT, AND, XOR
cost: syntax-tree node count
```

Pre-outcome class census:

```text
|H_P| = 882 distinct functions
```

This is a tiny symbolic/program-expression morphology analogue.

The class sizes are intentionally of the same order; they are not forced equal.

---

# 4. Ecology strata — defined before learner outcomes

Using only exact class membership:

```text
E_T_ONLY = H_T \ H_P = 718 targets
E_P_ONLY = H_P \ H_T = 620 targets
E_OVERLAP = H_T ∩ H_P = 262 targets
```

All targets are included; no target sampling or post-outcome exclusion.

---

# 5. Identical learning/serving policy inside each morphology

Given four labels:

1. retain all hypotheses in that morphology consistent with the four observations;
2. on a held-out query:
   - if the consistent version space is non-empty and unanimous, propose the unanimous bit;
   - otherwise abstain;
3. every proposal is checked by an external exact verifier;
4. wrong proposal -> reject + acquire correct label;
5. abstention -> acquire correct label.

No architecture label, target family label, or target identity is passed to the learner.

If the version space becomes empty, the morphology abstains on all remaining queries for that training subset.

---

# 6. Frozen cost coordinate

```text
label acquisition L = 1.0
proposal verification V = 0.25
```

Per held-out query:

```text
correct proposal = 0.25
wrong proposal   = 1.25
abstain          = 1.0
```

This primary calibration does not fold hypothesis-enumeration/training compute into the scalar. Class size and synthesis/evaluation work are reported separately and remain mandatory in any later whole-lifetime claim.

---

# 7. Frozen predictions

## CR-P1 threshold region

On `E_T_ONLY`:

```text
mean_cost(H_T) < mean_cost(H_P)
```

## CR-P2 program region

On `E_P_ONLY`:

```text
mean_cost(H_P) < mean_cost(H_T)
```

## CR-P3 overlap control

On `E_OVERLAP`, both target functions belong to both classes, so every unanimous proposal must be correct. No directional winner is frozen; report raw frontier/costs.

## CR-P4 no universal winner

If CR-P1 and CR-P2 both hold, the same pair of morphologies reverses ordering across ecology strata:

```text
H_T wins E_T_ONLY
H_P wins E_P_ONLY
```

This is the registered phase-region signature.

---

# 8. Strong claim boundary

A positive establishes only:

```text
REPRESENTATION_CLASS_MEMBERSHIP_PREDICTS_PARENT_MORPHOLOGY_REGION_AT_4BIT_SCOPE
```

It does **not** establish:

```text
neural networks beat symbolic systems
symbolic systems beat neural networks
fundamental morphology law
GMI
```

Both hypothesis classes and version-space behavior are mature learning-theory objects. The purpose is to calibrate a cross-representation morphology phase experiment and its controls.

---

# 9. No-rescue rules

After outcomes:

- do not change weight/bias grid;
- do not change expression-size threshold 8;
- do not change V/L;
- do not change training subsets;
- do not drop target functions;
- do not change unanimity policy;
- do not relabel the two morphologies as full neural/symbolic systems;
- if one morphology wins everywhere, report it.
