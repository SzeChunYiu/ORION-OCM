# Cognitive-unit granularity no-go v1

Status: **formal programme boundary from compositional computation; not claimed as novel mathematics.**

Refs #377, #233, #373.

## Question

Can machine intelligence have one **unique representation-independent minimum cognitive unit** determined from computational behavior alone?

## Result

In general, no.

The granularity of a computational unit is not invariant under ordinary composition/decomposition.

## Proposition 1 — merging

Let a finite deterministic network consist of components with joint state

\[
S=S_1\times\cdots\times S_n
\]

and one synchronous global update induced by their local transitions and wiring:

\[
F:S\times I\to S\times O.
\]

Then the whole network is behaviorally equivalent to a **single transition unit** whose local state is `S` and whose transition is `F`.

Hence a many-unit description does not imply many fundamental units.

This is the same flattening phenomenon already recorded in `FINITE_FLATTENING_THEOREM_V1.md`.

## Proposition 2 — splitting

Suppose a transition/function `f:X->Z` admits a nontrivial factorization

\[
f=g\circ h,
\]

with

\[
h:X\to Y,\qquad g:Y\to Z.
\]

Then the same behavior can be implemented as either:

```text
one unit f
```

or

```text
two units h -> g.
```

More generally, introducing intermediate state, continuation-passing representations, lookup structures, circuits, programs or macro instructions can change the apparent number/type of primitive units without changing the external computation.

## Proposition 3 — recoding

Given a computational basis `B`, an invertible encoding/decoding pair can produce a syntactically different basis `B'` realizing the same transformations. Universal programming formalisms provide many such mutually compilable representations.

Therefore syntax/type names alone cannot establish cognitive atomicity.

## Corollary — no behavior-only unique atom

If the criterion for a "fundamental cognitive unit" uses only extensional input/output behavior or unrestricted computability, then unit boundaries can be merged, split or recoded while preserving the criterion.

So:

```text
UNIQUE_REPRESENTATION_INDEPENDENT_COGNITIVE_ATOM
```

cannot be identified from behavior/universal computation alone.

## What can rescue a meaningful primitive notion?

Primitive status must be relative to additional constraints that are **not invariant under arbitrary merging/splitting**.

Candidates:

### 1. Physical locality

Allowed interactions have bounded spatial/communication structure; merging units incurs communication/storage/energy cost.

### 2. Resource irreducibility

Every legal decomposition/compilation of a candidate transformation incurs a registered asymptotic or finite overhead beyond a frozen bound.

### 3. Developmental locality

A unit boundary isolates updates so learning/revision can occur locally; merging causes harmful interference or expensive update.

### 4. Causal modularity

Interventions on one unit have a bounded causal closure that is not preserved by arbitrary alternative factorizations under the registered intervention language.

### 5. Verification/authority boundary

Some transformations require independently checkable contracts; merging proposal and authority may violate the protected semantics.

### 6. Hardware primitive

At a declared physical substrate, native operations/communication channels may supply a meaningful primitive set. This is substrate-relative, not universal machine intelligence.

## Revised Track-B object

Instead of one metaphysical atom, search for:

\[
\boxed{
\text{resource/causal/developmental equivalence classes of useful factorizations}
}
\]

under a registered ecology and physical/resource semantics.

A candidate `p` is primitive only relative to `(E,R,V,K)` when no allowed replacement/composition preserves the required developmental/epistemic behavior within the registered overhead.

## Connection to neural networks

A neuron is therefore not automatically a fundamental cognitive atom:

- an entire finite network can be flattened into one transition system;
- one neuron's affine/nonlinear calculation can be decomposed into arithmetic primitives;
- several neurons can be compiled into a matrix operation;
- hardware may execute the computation at yet another granularity.

Neural networks are better treated as a **morphology/factorization** whose distributed parameterization and update law create useful resource/developmental geometry.

## Connection to OCM `u2`

Likewise, current `u2` is not fundamental merely because it has a rich contract. Its fields may make it a valuable **mesoscopic cognitive asset** under OCM's verification/revision ecology, but they do not establish minimum irreducibility.

Required evidence remains:

```text
compensation-aware field/unit subtraction
bounded compilation against alternatives
developmental/resource necessity
heterogeneous morphology comparison
```

## Q1 terminal

The strong Q1 question can now receive the scoped answer:

```text
BEHAVIOR_ONLY_UNIQUE_COGNITIVE_ATOM_RULED_OUT_BY_GRANULARITY_NONINVARIANCE
```

The weaker resource-relative question remains open:

```text
RESOURCE_RELATIVE_MINIMAL_ADAPTIVE_FACTORIZATION_OPEN
```

This is a move upward, not a retreat: the object of theory becomes the laws of useful factorization and development rather than a representation-dependent atom.