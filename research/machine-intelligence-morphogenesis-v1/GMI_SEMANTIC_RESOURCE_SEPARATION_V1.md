# GMI semantic-state / resource-realization separation v1

Status: **core theory correction**.

## Problem

An earlier GMI draft defined future developmental equivalence using:

```text
verified future traces
machine changes
resource receipts
```

all at once.

That is too strong for the abstract state.

Suppose two implementations have identical future verified behavior under every legal probe, but one uses 10 FLOPs and another uses 10,000 FLOPs. If raw resource receipts are part of semantic state equivalence, the two situations are forced into different abstract states.

But GMI needs to say:

```text
same abstract cognitive/developmental semantics
+ different computational realization/resource geometry.
```

Likewise, two machines may perform different internal rewrites that are unobservable and irrelevant to every registered future cognitive obligation. Representation-independent state should not distinguish them merely because their private implementation traces differ.

---

# 1. Semantic developmental equivalence

Let `Omega_sem` contain only future quantities declared semantically protected by the cognitive obligation, such as:

```text
external outputs/actions
external verifier/evidence/admissibility receipts
future observable responses to legal teaching/interventions
registered retention/plasticity/generalization observables
registered authority/abstention/refusal outcomes
```

Do **not** automatically include raw internal implementation state or raw resource receipts.

For developmental situations `d,d'`, define

\[
d\sim^{sem}_{O,D,J}d'
\]

iff every admissible future intervention `j in J` induces the same probability law over `Omega_sem`.

The quotient

\[
z^{sem}=[d]_{\sim^{sem}}
\]

is the primary representation-independent developmental sufficient state.

---

# 2. Resource-labelled realization

A concrete morphology realizes semantic transitions with resource-labelled kernels.

Schematically:

\[
K_M:
(z,o,g)
\to
\mathcal D(z',y,e,\mathbf r),
\]

where `r` is a raw resource receipt.

Thus two morphologies may implement the same semantic transition law while differing in:

```text
description size
compute
memory
communication
learning/update work
verification work
maintenance
human input
```

That difference belongs in the GMI developmental frontier, not necessarily in the semantic-state identity.

---

# 3. Current budget/resource availability can still be semantic context

Resource **receipts** and resource **state/constraints** are different concepts.

If the current remaining budget, battery, deadline or memory limit changes which future actions are legal or which verified outcomes can be reached, then that resource state belongs in the developmental situation/context `xi`.

Example:

```text
same beliefs + same policy parameters
but one run has 1 checker call remaining and another has 100
```

They need not be future-equivalent under a budget-constrained obligation.

So:

```text
current resource availability that changes future legal semantics -> situation/context
resource spent by a realization -> transition receipt / frontier coordinate
```

---

# 4. Optional resource-sensitive quotient

Some scientific questions intentionally care about resource behavior as part of the future trace.

Then define a second relation

\[
\sim^{perf}
\]

that preserves both semantic traces and registered resource distributions within exact/bounded tolerance.

This is useful for:

```text
bounded developmental compiler equivalence
morphology equivalence
implementation replacement
resource-aware state abstraction
```

But it is **not** the default representation-independent semantic state.

---

# 5. Internal-development traces are protected only when the obligation says so

Do not include every private topology/weight/rule change in `Omega_sem` by default.

Include a developmental observable only if it affects the scientific obligation, for example:

```text
retained competence after teaching
future plasticity
whether a learned skill is revocable
whether a self-change crossed an authority boundary
future response to a registered probe
```

This prevents GMI from defining two implementations as cognitively different merely because they use different internal bookkeeping.

---

# 6. Morphology equivalence

Morphology equivalence is deliberately stronger than semantic-state equivalence.

Two morphologies may be:

```text
semantically equivalent
but resource-non-equivalent.
```

For `M1 ≈dev M2`, the registered compiler relation may require:

```text
semantic future traces preserved
learning/development responses preserved
resource inflation bounded
verification/authority semantics preserved
```

Therefore:

\[
\text{morphology equivalence}
\Rightarrow
\text{semantic equivalence}
\]

under the registered compiler assumptions, but not conversely.

---

# 7. Consequence for the fundamental-unit question

This gives a cleaner hierarchy:

```text
semantic developmental state
    what future distinctions actually matter

morphology / factorization
    how those distinctions and transitions are represented/computed

resource geometry
    what the realization costs to use/change/maintain
```

Neural and symbolic machines can therefore realize equivalent semantic obligations with very different developmental/resource geometry.

That is exactly the relationship Track B originally wanted to express without forcing “neuron = cognitive unit”.

---

# 8. Required core-file corrections

- `GMI_THEORY_V1.md`: remove raw resource receipts / arbitrary machine changes from default semantic equivalence; keep resource state when it changes future legal semantics.
- `GMI_AXIOMS_AND_THEOREMS_V1.md`: A2 should refer to protected semantic future traces; resource-sensitive equivalence is a separate relation.
- `GMI_STOCHASTIC_APPROXIMATION_V1.md`: distinguish `Omega_sem` from optional performance/resource trace space.
- `GMI_HST_ALIGNMENT_V1.md`: HST Verified Search Burden feeds the frontier, not the default semantic quotient.

Current terminal:

```text
SEMANTIC_DEVELOPMENTAL_STATE_SEPARATED_FROM_RESOURCE_REALIZATION
MORPHOLOGY_EQUIVALENCE_STRONGER_THAN_SEMANTIC_STATE_EQUIVALENCE
CORE_CORRECTIONS_PENDING_PROPAGATION
```
