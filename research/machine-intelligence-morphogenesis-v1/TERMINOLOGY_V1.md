# Track-B Terminology v1

Purpose: prevent concept drift while the theory is still unsettled.

These terms are **provisional scientific vocabulary**, not branding. Replace them if stronger parent terminology exists.

---

## Primitive

A low-level typed operation/state/interface element from which larger systems are composed.

Notation: `p`.

Examples might include a local state read, a typed transform or a restricted update action.

A primitive is not automatically “cognitive.”

---

## Generating basis

A finite/registered set of primitives plus legal composition/update/resource semantics:

\[
B=(Types,Primitives,Composition,Update,ResourceSemantics).
\]

A basis may have multiple equivalent alternatives.

Preferred phrase:

```text
adaptive generating basis
```

Avoid `fundamental cognitive atom` until the hard acceptance gates are earned.

---

## Minimal basis

A basis that is minimal under a **declared criterion and scope**, after compensating compositions are allowed.

Always qualify:

```text
algebraically minimal
resource minimal
learning minimal
epistemically minimal
minimal under registered ecology/resource envelope
```

No absolute metaphysical minimum is assumed.

---

## Basis equivalence class

A set `[B]` of bases that mutually compile under the frozen developmental/resource relation.

This is a plausible end result if no unique basis exists.

---

## Morphology

A complete organization of machine intelligence at a chosen resolution:

\[
M=(structure,state,configuration,control,learning/update,interface).
\]

Examples historically labelled neural, symbolic, probabilistic or programmatic are candidate morphology families.

Morphology is **not** defined by source-code labels or visual topology.

---

## Morphology family

An empirical/formal equivalence class or cluster of morphologies under registered developmental/resource semantics.

Historical names are parent-search aids, not final scientific classes.

---

## Morphogenesis

The process/law that generates or selects morphology from a basis under ecology/resource/verification/history conditions:

\[
\Gamma(B,E,R,V,H)\Rightarrow \mathcal P(\mathcal M).
\]

This is distinct from parameter learning inside a fixed morphology.

---

## Development / within-form learning

Experience-dependent transformation of an instantiated morphology:

\[
M_{t+1}=U(M_t,e_t).
\]

Examples include gradient descent, Bayesian update, rule induction, library learning and local plasticity.

---

## Learning law / update law

The structured rule `U` by which experience changes state/configuration/topology/control.

Do not use an unconstrained `UPDATE(any machine, any experience)` as a primitive; that is vacuous.

---

## Developmental equivalence

Two morphologies are developmentally equivalent at registered scope if a bounded compiler preserves not only current behavior but their response to registered experience/interventions and associated resource behavior within declared tolerance.

Current behavior equivalence alone is weaker; Stage B gives an exact counterexample.

---

## Ecology

The registered problem/environment regime:

```text
task distribution
observation/action structure
feedback/information
verification contract
drift/revision
horizon
resource prices/budgets
```

No morphology-superiority statement is meaningful without an ecology/resource scope.

---

## Developmental frontier

The Pareto set of verified capability outcomes and complete resources reachable by a morphology under an ecology and developmental history.

Notation:

\[
\mathcal F_M(E,H).
\]

This is the preferred primary object rather than a single intelligence score.

---

## Developmental productivity

A secondary scalar quantity such as

\[
\Delta Q/\Delta C
\]

or `dQ/dC`, only after capability utility and resource prices have been frozen prospectively.

This formalizes the intuition “development gained per unit cost.”

---

## Phase law

A prospective relationship between ecology/resource/verification variables and which morphology classes occupy the developmental frontier.

Example form:

\[
\Phi(E,R,V)\to FrontierClasses.
\]

A post-hoc explanation of a winner is not a phase law.

---

## Phase boundary

A region where morphology frontier membership/order changes as ecology/resource coordinates vary.

Under a frozen scalar cost this may appear as a crossover equation; the underlying object should remain the multi-resource frontier.

---

## Phase-diagram hole

A prospectively registered ecology region in which every strong known parent morphology misses a requirement or is dominated, while theory suggests better performance should be possible.

This is the only defensible starting point for a theory-first unknown-morphology search.

---

## Unknown/new morphology candidate

A discovered machine organization that survives simplification and bounded developmental-equivalence reduction against **every applicable registered parent morphology/product**, occupies a reproducible new frontier region, and ideally was predicted before search.

Preferred early term:

```text
NEW_MORPHOLOGY_CANDIDATE_AT_SCOPE
```

Do not say `NEW_FORM_OF_INTELLIGENCE_PROVEN`.

---

## Cognitive Asset Contract

Current role proposed for OCM `u2`: a higher-level interface for a usable cognitive capability/object including applicability, transformation, effects, warrant, cost, lifecycle, scope and acquisition lineage.

It is **not** currently the candidate fundamental primitive.

---

## Meta-morphogenesis

Development of the process that generates/develops morphologies:

\[
(\Gamma_g,U_g)\to(\Gamma_{g+1},U_{g+1}).
\]

This is stronger than ordinary parameter learning, architecture search or one self-edit and is currently gated.

---

# Short hierarchy

```text
primitive p
   ↓ composition
adaptive generating basis B
   ↓ morphogenesis Gamma under E,R,V,H
machine-intelligence morphology M
   ↓ learning/development U
M_0 -> M_1 -> ...
   ↓ measured as
developmental frontier F_M(E,H)
   ↓ across ecologies
morphology phase law Phi
   ↓ unexplained region
phase-diagram hole
   ↓ theory-first search
new morphology candidate
   ↓ much later
meta-morphogenesis
```
