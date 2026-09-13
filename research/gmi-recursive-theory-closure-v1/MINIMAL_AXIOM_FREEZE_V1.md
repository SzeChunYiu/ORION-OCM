# Minimal GMI axiom freeze V1

Status: **FOUNDATIONAL FACTORIZATION / CONDITIONAL AXIOM FREEZE**  
Date: 2026-09-13

This document freezes the smallest core currently needed to state learning, realization, agency and resource theorems without inserting a preferred architecture or learning rule. It factors, rather than supersedes, `GRAND_GMI_MASTER_THEORY_V1.md`.

## 1. Five primitives

A GMI problem is declared by

\[
\boxed{\mathcal G=(\mathcal I,\mathcal E,\mathcal O,\mathcal R,\mathcal D)}.
\]

### P1. Causal interface `I`

`I` supplies histories, the filtration `(F_t)`, legal observations/interventions/computations, the system boundary and continuation semantics. At step `t`, the selected operation is measurable with respect to the pre-outcome information `F_{t-1}` unless the theorem explicitly uses a different timing convention.

This primitive contains no neural layer, symbol table, program counter, prior, loss optimizer or architecture grammar.

### P2. Environment class `E`

`E` is the declared set of admissible causal laws/kernels for the environment and any unresolved machine components. It may be singleton, Bayesian, adversarial, partially identified or nonstationary, but the theorem must say which.

An environment class is not automatically a probability prior.

### P3. Obligation `O`

`O` specifies what outcomes count and at what tolerance: a relation, vector loss/risk, utility after sign reversal, safety constraint, prediction target or other declared task criterion. The tolerance formerly written `epsilon` is part of this contract.

Without `O`, there is no architecture-independent meaning of intelligence, learning improvement or successful planning.

### P4. Resource ledger `R`

`R` maps admitted traces, states and development operations to a declared partially ordered resource space. Coordinates may include samples, time, compute, communication, storage, energy, development work and lifetime work.

Resources that are declared additive use a nonnegative commutative monoid; nonadditive coordinates must carry their own composition rule. Unmeasured work is `unknown`, not zero.

### P5. Development law `D`

`D` is the admitted family of state/model/architecture update processes, including learning, search, synthesis, self-modification and evolutionary updates. Updates may create new internal objects or modules when that creation is a legal `I` operation and its state/resource effects are retained.

A static realization theorem does not determine `D`.

## 2. Six axioms / scope rules

### A1. Causal nonanticipation

Every selected observation, intervention, computation, bet or update uses only information available at its declared decision time. For the standard sequential convention, the choice at step `t` is `F_{t-1}`-measurable and the new outcome is revealed afterwards.

This is the timing hypothesis that later permits optional-stopping/e-process arguments. If an outcome leaks before selection, the corresponding validity theorem does not apply.

### A2. Scoped quantification

Every theorem quantifies only over the explicitly declared `E`, legal `I` operations, obligation `O`, resource coordinates `R` and development laws `D`.

Extending the ecology, intervention set, support, horizon, resource vector or development class creates a new claim unless a transport theorem is proved.

### A3. Trace composability

Two admitted components may be wired only when their declared interfaces match. Wiring defines one joint history/filtration and one joint trace semantics. Local states may be hidden, shared or dependent; composition itself does **not** grant statistical independence or correctness.

This axiom gives a system semantics. The later composition theorem must still prove when local validity survives the wiring.

### A4. Resource conservation / monotonicity

Admitted composition cannot erase a declared nonnegative cost. For additive coordinates, the total ledger is the sum of charged component, interface and coordination costs, minus only explicitly modelled reusable/shared work. For nonadditive coordinates, the registered aggregation law is used.

This rule blocks “free wrapper”, “free delegation” and “free controller” derivations.

### A5. Representation neutrality

Two implementations that induce the same protected causal response under the same boundary are equivalent for semantic claims at that declared resolution, while their resource and developmental profiles may differ.

Therefore a representation theorem proves only that a family lies inside the realization set. Architecture selection requires an additional feasible-set and preference/resource theorem.

### A6. Developmental causality

At every development step, the update is an admitted causal transformation of the available state/evidence under `I`; its cost is charged by `R`, and its future behavior remains inside the declared `D`/`E` scope. Dynamic module creation is state extension, not a reset of earlier evidence, error budget or cost.

## 3. Scientific metarules (not architectural primitives)

These rules govern what this repository may call established.

**M1 — Witness discipline.** Existential claims require a construction/witness. Universal claims require a proof, a complete finite cover, or a sound certificate for the declared infinite class.

**M2 — Statistical discipline.** A data-dependent claim must carry a sampling/filtration contract and a finite-sample, asymptotic or anytime-valid guarantee appropriate to its use. Reusing a fixed-look guarantee after adaptive monitoring is invalid without a repair.

**M3 — Negative discipline.** Failure to find or learn an object is not nonexistence unless search/coverage is complete. A failed sufficient certificate is not an impossibility theorem.

**M4 — Prediction discipline.** A “GMI prediction” must be recorded before the decisive result and must exclude at least one matched alternative/parent account. Post-hoc redescription is not a novel prediction.

## 4. Minimality tests

The freeze is intentionally small. Removing each primitive destroys a distinct requested layer:

| Removed item | What becomes undefined or unjustified |
|---|---|
| `I` | causal order, interventions, memory updates, sequential validity |
| `E` | the worlds/laws over which correctness or generalization is claimed |
| `O` | success, loss, improvement, planning objective |
| `R` | bounded intelligence, computation choice, architecture efficiency |
| `D` | learning, adaptation, architecture search, convergence |

The axioms are not claimed logically independent in a model-theoretic sense. “Minimal” here means no listed primitive can be deleted while retaining definitions for all fifteen requested GMI layers without smuggling an equivalent object back under another name.

## 5. Compatibility map to Grand GMI V1

The detailed current declaration

\[
(\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D,\varepsilon)
\]

maps to the freeze as

\[
\mathcal I=(\mathbf P,\mathcal B,\Theta),\quad
\mathcal E=\mathcal E,\quad
\mathcal O=(\Omega,\varepsilon),\quad
\mathcal R=\rho,\quad
\mathcal D=\mathcal D.
\]

Thus existing exact semantic state, cut spectrum, transformation spectrum, developmental reachability and morphology-frontier results remain in force. The freeze merely exposes which ingredients later theorems are allowed to use.

## 6. What is deliberately *not* an axiom

The following are not primitive assumptions:

- iid data or independence between rows;
- Bayesian priors;
- differentiability;
- gradient descent or backpropagation;
- neural/symbolic/tree architecture classes;
- a scalar utility rather than a vector obligation/resource order;
- stationarity;
- causal identifiability from observational data;
- unlimited memory, compute, samples or time;
- a universal architecture-selection rule;
- convergence of learning;
- correctness of a self-modification;
- novelty of any candidate learner.

Each may appear only as a theorem-specific premise or derived specialization.

## 7. Falsifier for the freeze’s intended role

This freeze fails its design goal if a requested downstream concept—learning, realization, optimization, memory, causality, agency, bounded metareasoning or architecture selection—cannot be stated without adding an architecture-specific primitive **and** the added primitive cannot be represented as a theorem-specific restriction of `I`, `E`, `O`, `R` or `D`.

Conversely, the ability to restate an existing theory in this vocabulary is not evidence that GMI improves that theory; comparison requires a separate theorem or experiment.
