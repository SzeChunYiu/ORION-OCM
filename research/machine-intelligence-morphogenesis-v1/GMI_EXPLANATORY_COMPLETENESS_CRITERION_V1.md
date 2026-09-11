# GMI Explanatory Completeness Criterion v1

Status: **FORMAL META-THEORY / NON-VACUITY CONTRACT**

Status date: 2026-09-12.

Refs:

- `GMI_THEORY_V1.md`
- `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`
- `GMI_PREDICTIVE_SUFFICIENCY_NO_GO_V1.md`
- `GMI_MACHINE_LEARNING_PHENOMENA_ATLAS_V1.md`
- `GMI_ML_THEORY_EXPERIMENT_MATRIX_V1.md`

Purpose:

> Define what it could scientifically mean for GMI to “contain everything” in machine learning without winning by putting an arbitrary learner inside a black-box transition function.

---

# 1. Five different notions of completeness

Do not conflate:

```text
C0 representational completeness
C1 semantic completeness
C2 mechanistic coverage
C3 predictive explanatory completeness
C4 morphogenetic completeness
```

They are successively stronger.

---

# 2. C0 — representational completeness

Consider any discrete-time adaptive computational system with legal external input `i_t`, internal state `x_t`, externally visible output `y_t`, and state transition

\[
(x_{t+1},y_t)\sim T(\cdot\mid x_t,i_t).
\]

If the system can also alter a declared structural descriptor `a_t`, include that in `x_t` or split it as morphology state.

## GMI-EC1 — normal-form embedding

Such a system can be embedded in the GMI realization normal form

\[
\mathfrak M=(Z,\kappa,Q,U,\Gamma,\rho)
\]

by taking, at minimum,

```text
Z      = complete legally relevant internal machine state x
Q/U    = a decomposition of T into execution/output and developmental state transition
Gamma  = identity unless structural changes are represented separately
kappa  = any registered semantic interpretation when one exists
rho    = registered resource receipts
```

If no useful Q/U split exists, a degenerate embedding can put the whole transition in one kernel and define the other as identity.

Therefore GMI is representationally broad enough to *describe* ordinary neural, symbolic, Bayesian, programmatic, evolutionary, retrieval, RL, ensemble and hybrid learning systems.

### Proof sketch

Choose `Z=X`. Define the GMI transition to reproduce `T` exactly; assign external outputs identically. Any state component whose change is called structural can be moved into `Gamma`; otherwise keep it in `Z/U`. The construction is immediate.

This is a **coding theorem**, not an intelligence theorem.

---

# 3. Why C0 has almost no explanatory power

A theory that says

```text
K = the entire unknown behavior of the machine
```

can fit every observation and predict nothing.

Likewise a one-dimensional real number can encode arbitrary world identity, and an unconstrained response map can memorize a protected outcome table.

Therefore:

\[
\text{representational completeness}
\not\Rightarrow
\text{explanatory completeness}.
\]

Any “GMI explains X” claim must pass the non-vacuity gates below.

---

# 4. C1 — semantic completeness at a registered obligation

For fixed obligation `O`, legal development protocol `D` and intervention class `J`, define the semantic developmental quotient `S_O`.

A realization is semantically complete at scope if its reachable state plus legal side information preserves every quotient distinction required for future protected consequences.

This is obligation-relative, not universal.

Failures include:

```text
current behavior matches but future learning differs;
content matches but provenance obligation differs;
ordinary prediction matches but interventions differ;
present state matches but historical/as-of query differs.
```

C1 is tested by semantic collision/continuation hostiles.

---

# 5. C2 — mechanistic coverage

A theory has mechanistic coverage of a phenomenon class if every registered phenomenon is assigned to typed objects and mechanisms such that the assignment is implementation-invariant.

For modern ML, the current atlas requires coverage over at least:

```text
representation/capacity
optimization/credit
implicit selection/generalization
self-supervision/transfer
fast adaptation/in-context learning
memory/retrieval/provenance
continual learning/plasticity
verification/authority
compression/serving
scaling/saturation/emergence
robustness/causality/OOD
reinforcement/planning
architecture search/morphogenesis
distributed/multi-agent realization
data/feedback quality
interpretability/causal mechanism measurement
```

A source-code label is not mechanistic coverage.

Example:

```text
“Transformer”
```

must be decomposed into properties such as content-dependent routing, shared parameterized functions, positional/state encoding, residual computation, gradient development and hardware/resource context.

---

# 6. C3 — predictive explanatory completeness

This is the scientifically important target.

Let a theory descriptor be

\[
D_T = (\Psi(O),\Phi(M,h),P)
\]

where:

- `Psi(O)` is bounded-information pre-outcome obligation structure;
- `Phi(M,h)` is a bounded, implementation-invariant response/mechanism descriptor;
- `P` is exogenous resource/substrate context.

Let protected outcome/frontier response be `Y`.

A strong predictive theory seeks a law/class `f` such that

\[
\hat Y=f(D_T)
\]

transfers to protected ecologies, remints and held-out realization families within registered uncertainty.

Ideal exact sufficiency would require

\[
Y\perp\!\!\!\perp W
\mid
D_T
\]

with respect to unregistered world identity `W`, but empirical science should normally test residual prediction rather than assert exact conditional independence.

## Non-vacuity requirements

`D_T` and `f` must be bounded in:

```text
description length
precision
structured object size
query access to the obligation/world
search/tuning burden
```

and invariant to irrelevant semantic remints.

Protected outcomes cannot define their own predictors.

---

# 7. GMI-EC2 — collision refutation rule

If two registered worlds/realizations have identical theory descriptor

\[
D_T(w_1)=D_T(w_2)
\]

but deterministically require different protected outcome/frontier prediction

\[
Y(w_1)\ne Y(w_2),
\]

then no exact deterministic predictive theory using only `D_T` can be sufficient at that scope.

Therefore every discovered collision forces one of:

```text
refine the descriptor using a pre-outcome distinction;
narrow the claim;
move to a stochastic/uncertainty-aware prediction;
accept irreducible residual error.
```

It must not be patched with world identity.

---

# 8. GMI-EC3 — explanation burden principle

The cost of obtaining the theory descriptor is part of the developmental burden whenever a machine is supposed to *use* the theory online.

If estimating

```text
Xi_obl
residual quotient burden
mechanism witnesses
hardware response
```

requires more experimentation/search than direct adaptation, then a meta-intelligence implementation based on the theory may be dominated even if the theory is descriptively correct.

Thus explanatory compression and measurement cost are themselves resource-sensitive.

---

# 9. C4 — morphogenetic completeness

A theory reaches morphogenetic completeness at a registered scope only if it can do more than predict performance of supplied architectures.

It must prospectively predict which **implementation-invariant property/mechanism vector** should become frontier-useful, and a neutral search should recover that vector without the name being encoded as a macro.

Required chain:

```text
obligation/context
   -> bounded theory descriptor
   -> predicted mechanism/property vector
   -> neutral search over low-level primitives
   -> recovered frontier form
   -> disjoint replication
   -> parent-reduction attack
```

This is the strongest Track-B target.

---

# 10. Completeness scorecard

For each theory atom/phenomenon `i`, maintain:

```text
MAP_i       typed home exists?
MECH_i      implementation-invariant mechanism exists?
PRED_i      directional pre-outcome prediction frozen?
X0_i        exact/formal microscope where applicable?
X1_i        controlled intervention survived?
X2_i        held-family prediction survived?
X3_i        neutral recovery survived?
X4_i        real transfer survived?
X5_i        parent reduction survived?
OPEN_i      remaining assumptions/gaps
```

Do not collapse this vector to one scalar unless a prospectively registered aggregation is needed for a specific experiment.

---

# 11. How “all of machine learning” enters the framework

The intended closure is not a finite list of algorithms.

Any new ML method can change only some combination of:

```text
what information is legally available (D/J/O)
what state is preserved (Z/Theta)
how state is factorized (F)
how outputs/candidates are produced (K)
how experience changes state (U)
how structure changes (Gamma)
how internal state maps to protected semantics (kappa)
how resources are consumed (rho/P)
what protected consequences are demanded (O/V/C/H)
```

This gives a complete **type system** for registered adaptive computational systems.

But the theory earns explanatory content only when it compresses those objects into reusable invariant laws that survive collisions and interventions.

---

# 12. Explanation targets for unresolved deep-learning theory

Rather than leave “deep learning theory is incomplete” as one vague gap, split it into response-law targets.

## EC-T1 optimization accessibility

Predict

\[
P(T_A\le B\mid F,U,D,P,O)
\]

or equivalent burden distribution for reaching an admissible solution.

## EC-T2 function selection / implicit bias

Given many low-training-loss states, predict which semantic/function classes the update law selects.

## EC-T3 generalization

Predict protected risk from bounded descriptors of data/ecology, selected function/representation, update history and obligation.

## EC-T4 feature-learning transition

Predict when the learned representation materially moves beyond a fixed-kernel/lazy approximation.

## EC-T5 scaling/saturation

Predict marginal capability/loss gain from extra model/data/compute and which bottleneck causes crossover/saturation.

## EC-T6 fast adaptation

Predict when task structure is encoded as an in-context/meta-learned update procedure rather than persistent parameter change.

## EC-T7 continual plasticity

Predict future learning response from developmental history/state, not present behavior alone.

## EC-T8 causal/interventional sufficiency

Predict how much extra state/evidence beyond observational prediction is needed for registered interventions.

Each is a separate scientific programme and receives experiment IDs in `GMI_ML_THEORY_EXPERIMENT_MATRIX_V1.md`.

---

# 13. Strong completeness terminals

Allowed future terminals are graded.

```text
GMI_C0_REPRESENTATIONAL_CLOSURE
GMI_C1_SEMANTIC_CLOSURE_AT_REGISTERED_SCOPE
GMI_C2_MECHANISTIC_ATLAS_COVERAGE
GMI_C3_HELD_OUT_PREDICTIVE_CLOSURE_AT_REGISTERED_SCOPE
GMI_C4_NEUTRAL_MORPHOGENETIC_RECOVERY_AT_REGISTERED_SCOPE
```

Never emit

```text
GMI_EXPLAINS_EVERYTHING
```

without a registered scope, because new ecologies, physical substrates and protected obligations can introduce new distinctions.

---

# 14. Current status

Current strongest honest summary:

```text
C0: essentially closed for ordinary computable adaptive machines by normal-form embedding.
C1: exact finite quotient theory exists; real/stochastic approximation remains partly open.
C2: broad ML atlas coverage now exists; future unmapped phenomena must enter the gap ledger.
C3: open and central — response laws require controlled/held-out validation.
C4: open — VLC has an exact/E1 programme; RQM/VRQM/VGSC/IQL/LMHM/SCDI are prospective candidates.
```

This is a stronger scientific position than either extreme:

```text
“the framework contains everything, therefore it is true”
```

or

```text
“because deep learning has open problems, a general theory is impossible.”
```

The goal is to turn open phenomena into typed, falsifiable response laws one by one.