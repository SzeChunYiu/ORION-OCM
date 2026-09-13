# Grand GMI Phenomenology-to-Morphology Selection Bridge V1

Status: **SYNTHESIS WITH MORPHOLOGY_SELECTION_THEOREM_V1**  
Date: 2026-09-12

This note binds `PHENOMENOLOGY_REDUCTION_ATLAS_V1.md` to the independently merged `MORPHOLOGY_SELECTION_THEOREM_V1.md`.

## 1. Reduction is not architecture derivation

The phenomenology atlas shows that attention, memory, retrieval, prompting, planning, tools, continual learning, multi-agent communication, scaling and the other frozen phenomena can be represented through existing Grand-GMI master objects. This establishes ontology/reduction coverage.

It does **not** imply that a named architecture implementing one of those phenomena has been derived.

The morphology-selection theorem supplies the missing quantifier. Let `A` be the admissible/reachable morphology set after obligation, semantic-cut, transformation, process, physical and developmental constraints. Let `F` be its registered reachable Pareto/selected set. An operational property `P` is derived only if

\[
\forall m\in F,\quad P(m),
\]

or an explicitly declared selection rule uniquely selects one morphology-equivalence class possessing `P`.

## 2. Combined derivation chain

The complete claim chain is therefore

\[
\boxed{
\text{phenomenon}
\to
(Q,S^*,\kappa,\tau,\rho,Reach,G,\text{composition})
\to
\text{necessity / feasibility constraints}
\to
\mathcal A
\to
\operatorname{Pareto}(\mathcal A)
\to
\text{properties common to selected morphologies}.
}
\]

A property may be **explained** before it is **selected**. For example:

- dynamic routing can be proved useful on selector-dependent tasks without proving that every frontier realization is a Transformer;
- temporal memory can be necessary without proving the memory must be recurrent neural state rather than an external store;
- equivariance can be derived without proving the implementation must be a historical CNN;
- exact finite intelligence can compile to a neural realization while neurality itself remains underdetermined if a non-neural frontier realization survives.

## 3. Architecture-derivation falsifier

A statement `GMI derives family/property P at scope S` is false whenever one admissible selected/frontier morphology at the same registered scope lacks `P`.

An empty selected set supplies no positive architecture derivation (MSC-1);
proof of feasible selection is distinct from excluding counterproperties.
Candidate omission is not a proof of derivation. Competing families must be excluded by proved response, physical, resource, developmental or selection constraints.

This criterion is deliberately stronger than architecture compatibility.

## 4. Consequence for the phenomenology atlas

Every architecture-named row in the atlas must be read as follows:

1. the named mechanism is one realization of an architecture-neutral operational role;
2. the operational role can be necessary/advantageous under stated GMI conditions;
3. the named family is derived only if morphology selection subsequently excludes all selected alternatives lacking that family/property.

Thus the atlas plus morphology-selection theorem gives Grand GMI a disciplined route from observed phenomena to predicted form without reintroducing architecture names as priors.

## 5. Status

`PHENOMENOLOGY_REDUCTION_COVERAGE != NAMED_ARCHITECTURE_DERIVATION`.

`NAMED_OR_OPERATIONAL_MORPHOLOGY_PROPERTY_DERIVED` requires the morphology-selection criterion.

This bridge preserves the earlier protected failure of exact architecture-name recovery and turns it into a typed boundary rather than ignoring it.