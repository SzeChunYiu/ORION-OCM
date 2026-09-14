# Capability contract V1 — F1 formalization

Issue #602, architecture-independent capability registration. This note extends the merged A4 contract with the exact F1 coordinate vector and the mathematics needed to use it without silently converting a measurement definition into an empirical or predictive theorem.

## 1. Claim boundary

This unit establishes a **G1 measurement specification**. It proves structural properties of the registry and of the stated finite-sample gate. It does **not** prove that a particular machine possesses a capability, that the 17 coordinates form a universal ontology, or that morphology predicts capability (G6).

Every empirical use is relative to a frozen task/ecology family, allowed-information contract, resource envelope, parent envelope, protected remints and judge. Reachability remains separate from admissibility under DU-1.

## 2. Capability vector

For morphology `M`, ecology `E`, resource envelope `R`, and developmental history `H`, define the registered measurement object

```text
Cap(M,E,R,H) = (C_1, ..., C_17)
```

where each coordinate has its own domain, units, ordering and reporting contract in `CAPABILITY_COORDINATES_V1.json`.

There is no architecture-independent scalar "IQ" implied by this definition. A scalarization

```text
J_p(C) = sum_j p_j phi_j(C_j)
```

is admissible only when all `p_j >= 0`, the prices/weights and normalizations `phi_j` are frozen before protected scoring, and the unsummarized vector remains reportable. Otherwise the default comparison is Pareto/componentwise.

## 3. Resource order

Let a charged resource vector be

```text
r = (r_1, ..., r_k) in R_{>=0}^k.
```

Define

```text
r <=_R s  iff  for every j, r_j <= s_j.
```

### Theorem F1-R — componentwise resource order is a partial order [P1]

**Domain.** Any fixed finite registered resource-coordinate set with nonnegative real values.

**Claim.** `<=_R` is reflexive, antisymmetric and transitive.

**Proof.** Reflexivity is coordinatewise `r_j <= r_j`. If `r <=_R s` and `s <=_R r`, then every coordinate satisfies both inequalities and hence `r_j=s_j`, proving antisymmetry. If `r <=_R s` and `s <=_R t`, transitivity of the real order gives `r_j <= t_j` for every coordinate, hence `r <=_R t`. QED.

**Nearest false generalization.** A post-hoc scalar price can reverse an apparent winner by changing weights after outcomes. Therefore no scalar resource ordering is canonical without a prospectively frozen price vector.

## 4. Strongest-parent first refusal

For capability coordinate `c` and budget `B`, let `Pi_c(B)` be the candidate policy class admitted by the information/resource contract and let

```text
Pi_c^P(B) subseteq Pi_c(B)
```

be the preregistered behavioral parent/null envelope. Its theoretical value is

```text
V_c^P(E,B) = sup_{pi in Pi_c^P(B)} E_E[u(pi,w)].
```

If the parent class is finite and enumerable, the maximum can be exact. If it is open, a study may claim separation only from the registered searched envelope and must report search coverage. "Best baseline tried" is not silently promoted to the universal supremum.

This is a decision-value rule: extra state, information, routing, memory, hierarchy, social modeling, tools, or self-model state receives capability credit only when it improves the protected decision outcome after its resource cost and after the strongest registered parent receives first refusal.

## 5. Positive world and minimal negative twin

For each protected positive world `w_i+`, a capability protocol supplies a matched twin `w_i-` satisfying N0:

1. remove exactly one registered capability-requiring conditional dependency;
2. preserve reward/action semantics, scoring, remint family and non-target budgets;
3. make the target capability unnecessary or make the registered parent sufficient.

Let utility be normalized only for the common assay:

```text
u(pi,w) in [0,1]
d_i+ = u(M,w_i+) - u(P,w_i+)
d_i- = u(M,w_i-) - u(P,w_i-).
```

Evidence for the isolated capability requires a positive candidate-parent gap in the positive worlds and collapse of that gap in the negative twins. If the margin survives the twin, the isolated dependency has not been identified: the effect may be a confound, a broader capability, resource mismatch, or an invalid twin.

The registry can verify that every coordinate declares a falsifier and parent. It cannot prove from prose that a future world generator changes exactly one semantic dependency; that requires generator-level invariant tests.

## 6. Finite-sample gate

Because `u in [0,1]`, every paired difference lies in `[-1,1]`, a range of width two. For `n` **independent registered evaluation units**, Hoeffding gives the one-sided statement

```text
P(E[d] < mean(d) - eps) <= gamma
```

with

```text
eps(n,gamma) = sqrt(2 ln(1/gamma) / n).
```

The common assay needs three one-sided concentration events: one lower-tail event for the positive-world mean and two tails to bound the absolute negative-twin mean. Allocate `gamma=alpha/3`, so

```text
eps(n,alpha) = sqrt(2 ln(3/alpha) / n).
```

The registered gates are

```text
mean(d+) - eps(n+,alpha) > tau_parent
abs(mean(d-)) + eps(n-,alpha) <= tau_twin.
```

`alpha`, `tau_parent`, `tau_twin`, the independence unit and sample-size plan must be frozen before protected scoring.

### Theorem F1-S — simultaneous coverage of the common assay [P3 bound]

**Assumptions.** Bounded paired differences in `[-1,1]`; independent registered evaluation units within each reported mean; thresholds and analysis fixed before protected scoring.

Let `E+` be failure of the positive lower confidence statement and `E-_upper`, `E-_lower` the two failures needed to control the twin mean in both directions. Hoeffding gives each probability at most `alpha/3`. By the union bound,

```text
P(E+ union E-_upper union E-_lower) <= alpha.
```

Thus the two displayed gates hold simultaneously with probability at least `1-alpha` under the stated assumptions. No Gaussian or asymptotic approximation is used.

**Boundary.** This theorem does not cover repeated dependent rows, adaptive row creation, adaptive reuse, or unlimited horizons. Those remain in #602 section M and require a separately registered simultaneous-validity construction.

## 7. Registry completeness theorem

Let `Q` be the exact 17 F1 IDs frozen in `f1_coordinates_v1.py`.

### Theorem F1-C — structural omission freedom [P1/executable]

If `f1_coordinates_v1.run()` returns `PASS`, then within this registry:

- every member of `Q` occurs exactly once and no extra coordinate is present;
- every row has a definition, reporting contract, scope, assumptions, strongest parent, falsifier, evidence class and claim ceiling;
- no row raises its claim ceiling above G1;
- the common assay states A0/S0/N0/P0, the three-event bound, the independent-unit boundary and frozen-price scalarization rule.

**Proof.** The verifier tests exact set equality, uniqueness, required-field inclusion, nonempty metadata, claim-ceiling order and the common-assay predicates before returning success. Therefore zero error implies precisely those structural predicates. QED.

**Non-claim.** Structural omission freedom is not semantic truth, construct validity, empirical capability possession, or completeness of all possible notions of intelligence.

## 8. Coordinate semantics

The registered F1 vector contains:

1. memory capacity/retention;
2. retrieval efficiency;
3. abstraction/compression ability;
4. transfer/generalization;
5. compositional depth;
6. planning horizon;
7. exploration/information-gain efficiency;
8. causal identifiability/intervention capability;
9. robustness/invariance;
10. continual-learning plasticity;
11. catastrophic-forgetting susceptibility;
12. tool-use/solver-routing capability;
13. social-model depth;
14. communication capacity;
15. verification/reliability;
16. self-model accuracy;
17. meta-learning/evolvability.

The machine-readable file is authoritative for formulas and reporting contracts. Several are intentionally multi-part frontiers rather than one number: memory capacity must not erase retention, planning horizon must report branching and simulator budget, plasticity must state a retention floor, communication must report the utility-vs-bit frontier, and reliability must expose asymmetric false-adoption cost where relevant.

## 9. Literature anchors and parent subtraction

Methodological anchors, not novelty claims:

- Blackwell (1953), *Equivalent Comparisons of Experiments*: information structures are compared by decision value, motivating parent first refusal rather than implementation labels.
- Hoeffding (1963), *Probability Inequalities for Sums of Bounded Random Variables*: finite bounded concentration used by F1-S under its explicit independence assumption.
- Gneiting & Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*: proper-score discipline for prediction, verification and self-forecast coordinates.
- Lieder & Griffiths (2020), *Resource-Rational Analysis*: resource-conditioned behavioral comparison as a parent perspective, not a GMI-specific novelty claim.

Capability-specific parent families remain listed per row and continue to receive first refusal.

## 10. Claim ceiling

This artifact earns only:

```text
F1_CAPABILITY_COORDINATES_REGISTERED_AT_G1
```

It does not earn:

```text
MORPHOLOGY_TO_CAPABILITY_MAP_SUPPORTED_AT_REGISTERED_SCOPE
```

To advance toward G6, the next work must freeze an architecture-name-free morphology descriptor, a development-only fitting/derivation protocol, held-family predictions, failure predictions, resource-repricing/ablation/drift predictions, uncertainty/abstention rules, and protected real-regime tests.
