# Computable machine-intelligence reduction v1

Status: **parent-owned computability reduction used to delimit Track-B claims.**

## 1. Scope

Consider a machine-intelligence system whose execution and developmental dynamics are computable.

Let its complete internal state at time `t` be `s_t`, including whatever the system needs:

```text
weights
program/rules
memory
optimizer state
library
belief state
topology
indexes
self-model
```

Let observation/feedback be `z_t`. Let the machine's computable transition be

\[
(a_t,s_{t+1})=F_M(s_t,z_t).
\]

Any distinction between `inference` and `learning` can be represented inside `s_t/F_M`; learning simply changes parts of the future machine state.

## 2. Universal-program reduction

For any such computable `F_M`, a universal machine `U` can execute an encoding/program `p_M` implementing `F_M`.

Thus, at the level of computable input/state/output behavior:

\[
M \equiv U(p_M,\cdot).
\]

This applies equally to computable:

```text
neural-network execution + optimizer updates
symbolic production systems
program synthesis/library systems
probabilistic inference implemented by exact/approximate algorithms
reservoir/readout learners
VSA/HDC algorithms
OCM-like explicit developmental systems
hybrid agents
```

The reduction is ordinary universal computation, not a new GMI theorem.

## 3. Scientific consequence

A universal computational substrate is a valid **expression substrate** but an insufficient theory of practical intelligence.

It does not explain:

```text
why p_M is found rather than another program
why useful representations are close/far in search
what experience changes
which updates are cheap
what generalizes
how much data/search is required
which hardware/resource regime favors the program
which verifier/feedback structure makes learning possible
```

Therefore the fundamental scientific object must live above bare computability.

## 4. The irreducible practical differences become bias/resource differences

For practical developmental behavior, extract from morphology `M` a tuple such as

\[
\mathcal G_M=(\mathcal H_M,\pi_M,K_M,c_M,V_M),
\]

where:

- `H_M`: accessible hypothesis/configuration space/factorization;
- `pi_M`: prior/proposal/search distribution or order;
- `K_M`: experience-conditioned update/proposal kernel;
- `c_M`: resource vector for transitions/execution/maintenance;
- `V_M`: feedback/verification interface.

Two universal programs can therefore be equivalent in computability but radically different in developmental geometry.

## 5. Morphology is a structured bias over computation

A useful working interpretation is:

> A machine-intelligence morphology is a structured, resource-embedded inductive/developmental bias over computable processes.

Examples:

```text
neural:
  continuous parameterization + architecture prior + optimizer geometry

program synthesis:
  grammar/library/prefix prior + edit/synthesis/search geometry

probabilistic:
  model class + prior/likelihood + inference geometry

production system:
  symbolic ontology/rule language + match/chunk/rewrite geometry

OCM-like:
  explicit warranted asset space + retrieval/applicability/search + verified update geometry
```

This is a synthesis, not a novelty claim: inductive bias, meta-learning, universal search and resource-rational parents already own the constituent ideas.

## 6. Stronger meaning of generality

A machine is not more general merely because its instruction set is universal.

A stronger developmental notion of generality is the ability to **adapt its effective inductive/developmental geometry** across structured ecologies at acceptable meta-cost.

That may involve changing:

```text
representation / hypothesis class
prior/proposal distribution
optimizer/update rule
library/abstractions
topology
memory organization
verification/search allocation
```

This immediately connects to mature parents:

```text
meta-learning
AutoML/NAS
algorithm selection
PowerPlay/OOPS
evolutionary search
learned optimizers
resource rationality
```

so the idea itself is not ORION novelty.

## 7. Track-B residual after the reduction

Track B can still contribute only if it establishes something stronger, for example:

1. a cross-paradigm developmental-geometry formalism with useful measurable invariants;
2. quantitative ecology -> geometry/frontier predictions made before outcomes;
3. endogenous acquisition of the predicted geometry from a neutral/frozen generator;
4. phase-diagram regions not already explained by strongest algorithm-selection/meta-learning parents;
5. a predicted missing geometry/morphology that is subsequently discovered and survives reduction.

## 8. Current no-go terminal

```text
BARE_COMPUTATIONAL_SUBSTRATE_IS_UNIVERSAL_COMPUTATION_PARENT
PRACTICAL_INTELLIGENCE_DIFFERENCES_REQUIRE_BIAS_RESOURCE_DEVELOPMENTAL_STRUCTURE
```

This is the current strongest answer to the question “what is below neural/symbolic/OCM?” at the computability level.

It does **not** prove that physical implementation has no deeper universal laws; it states that computational expressivity alone cannot select a unique cognitive atom or explain practical machine-intelligence forms.