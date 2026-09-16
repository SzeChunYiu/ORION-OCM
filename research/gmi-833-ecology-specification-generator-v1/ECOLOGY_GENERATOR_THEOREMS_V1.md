# Registered ecology-product theorems v1

## 1. Definitions

Let `I` be the frozen set of seventeen ecology axes. For each `i in I`, let
`L_i = {ell_i^-, ell_i^+}` be a finite carrier whose token spelling is opaque.
Each level has a canonical external payload `psi_i(ell)` and a total probe
predicate `q_i` satisfying

`q_i(psi_i(ell_i^-)) = 0` and `q_i(psi_i(ell_i^+)) = 1`.

The executable ledger checks these equalities by deriving every predicate from
the payload rather than reading the registered polarity. The seventeen predicates
cover observation partitions, directed cycles, transition support, intervention
access, disjoint factors, locality radius, permutation invariance, graph
reachability, payoff-optimum compatibility, affordable verification, four
resource prices, developmental horizon, cross-epoch stability, and availability
of a required sensor-action pair.

The architecture-neutrality conclusion is not inferred from a word scan alone.
The frozen human semantic audit classifies every load-bearing coordinate:

| Axis | Why it is an external ecology/specification property |
| --- | --- |
| Observability | A partition of environment states into emitted observations is an information contract. |
| Recurrence | Cycle existence belongs to the environment transition graph. |
| Uncertainty/noise | Positive outcome support belongs to the external transition law. |
| Causal ambiguity/intervention access | Observational images and permitted interventions define the experiment interface. |
| Compositional structure | Variable scopes and factorization describe the task relation. |
| Spatial/locality | Sites, influence edges, and radius describe interaction geometry. |
| Symmetry/equivariance | A permutation and outcome table define environmental invariance. |
| Communication topology | Agents and permitted directed links define an external message channel. |
| Competition/cooperation | Payoff tables define incentives and compatible optima. |
| Verification availability/cost | Verifier access, price, and budget define external feedback. |
| Memory price | Required storage units, price, and budget are external resource terms. |
| Compute price | Required operation units, price, and budget are external resource terms. |
| Communication price | Required message units, price, and budget are external resource terms. |
| Energy price | Required energy units, price, and budget are external resource terms. |
| Developmental horizon | Available interaction steps are an external time budget. |
| Nonstationarity/drift | Cross-epoch target variation belongs to the data-generating process. |
| Embodiment constraints | Available sensor-action pairs define the interaction interface. |

Each executable probe receives only its own row's external payload. The separate
vocabulary and function-domain audits then provide corroborating syntactic
evidence that no hidden family coordinate was added.

A syntax is a tuple of one registered token and one same-shaped payload per axis.
It is *semantically well formed* only when every payload is the canonical payload
of the selected token and independently evaluates to that level's registered
probe value. Thus syntactic membership is necessary but not sufficient for
semantic validity.

For a semantically well-formed ecology `e`, define its behavioral specification

`B(e) = (I_probe, {0,1}, R_e, score, resource_terms)`, where

`R_e = {(probe_i, q_i(psi_i(e_i))) : i in I}`

and `score` is the exact fraction of responses equal to `R_e`.

## 2. Total external-specification theorem

**Theorem G17-1.** `B` is a total deterministic function on the registered
semantically well-formed ecologies and depends only on external ecology payloads.

**Proof.** Semantic well-formedness supplies exactly one canonical payload for
each of the seventeen axes. Every `q_i` is total on its registered payload schema,
so its value is a unique bit. Collection in frozen axis order gives a unique
finite relation. The score compares a response map against this relation and is
therefore also unique. Price, horizon, and verification terms are copied from
external payloads. No implementation or family coordinate occurs in the domain,
the construction, or the score. QED.

## 3. Registered-product completeness and uniqueness

Let `E = product_{i in I} L_i`. The iterator nests the carriers in frozen order.

**Theorem G17-2.** The iterator emits every member of `E` exactly once and emits
`product_i |L_i| = 2^17 = 131072` members.

**Proof.** For zero carriers the empty tuple is emitted once. Assume the claim for
the first `k` carriers. For carrier `k+1`, the iterator appends each of its levels
to each prefix. This is surjective onto the `(k+1)`-fold product. Two emitted
tuples are equal only if their prefixes and final coordinates are equal; the
induction hypothesis and no repetition inside a carrier give injectivity. The
cardinality recurrence is `N_(k+1)=N_k |L_(k+1)|`, hence the product formula.
Equivalently, mixed-radix rank is an injection from bounded digit tuples onto the
integer interval `[0, product_i |L_i|)`. The executable census checks iterator,
recurrence, arithmetic product, unique ranks, and interval coverage independently.
QED.

This theorem is complete for the registered carriers only. It says nothing about
the measure, representativeness, or completeness of any larger ecology universe.

## 4. One-coordinate matched twins

Let `e^-` select every negative level. For each axis `j`, let `e^(j,+)` replace
only coordinate `j` by its positive level.

**Theorem G17-3.** `(e^-, e^(j,+))` differs in exactly coordinate `j`, in exactly
semantic payload `j`, and `R_e` differs in exactly probe `j`, changing it from
zero to one. The probe carriers and score rule are identical.

**Proof.** Construction holds all coordinates other than `j` fixed, so their
tokens and payloads are equal. Canonical payloads for the two levels of `j` are
distinct, and the registered nondegeneracy equations give the zero-to-one flip.
Each probe `q_i` reads only payload `i`, so no `i != j` target can change. Input
and response carriers and the exact-match score do not depend on level choice.
QED.

This supplies seventeen matched positive/negative ecology twins rather than one
global pair whose changed cause would be ambiguous.

## 5. Opaque-token remint theorem

For every axis let `rho_i : L_i -> L'_i` be a bijection, and transport the
token-to-payload incidence relation along `rho_i`.

**Theorem G17-4.** The product bijection `rho = product_i rho_i` preserves
token-erased semantics, `B`, exact scores, product cardinality, and twin
isolation.

**Proof.** For each level, transported lookup satisfies
`psi'_i(rho_i(ell)) = psi_i(ell)`. Therefore every probe value is unchanged, so
the required relation, resource terms, and score are unchanged. Bijections
preserve each carrier size, and their product is a bijection on `E`. Coordinate
equality and inequality are also preserved, so one-coordinate twins remain
one-coordinate twins. QED.

The executable control uses a disjoint remint for all 34 tokens and independently
checks three global members and all seventeen twin invariants.

## 6. Architecture-prior noninterference

**Theorem G17-5.** Within the frozen registered scope, changing or supplying an
implementation-family label cannot affect ecology generation, specification
generation, or scoring.

**Proof.** Such a label is absent from the domains of all three functions. Their
outputs are fully determined by coordinate indices, external payload probes, and
external response maps respectively. The operational registry and generated
objects also pass the frozen known-family phrase audit. Hence there is no value to
change and no branch on which such a label could act. QED.

This is a structural noninterference result, not a claim that the chosen ecology
axes are empirically unbiased or exhaustive of nature.

## 7. Claim boundary

The terminal proves a reusable, systematic, architecture-neutral registered
ecology family with explicit semantic axes and exact twins. The following remain
open: sufficient sampling of a broader ecology space, sampling bias and
uncertainty, unregistered/infinite universes, real-world representativeness,
large-scale empirical tests, and recovery or ranking of implementation families.
