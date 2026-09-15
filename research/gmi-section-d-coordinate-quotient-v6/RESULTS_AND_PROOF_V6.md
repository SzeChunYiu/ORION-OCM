# Section D V6 results and proof — finite decision-sufficient complete coordinates

Authority: issue #693; pre-outcome freeze commit `187afe3744a869fe09b6bf3d71653852cdc4f9f3`.

## Result

All ten frozen V6 assertions pass in normal and optimized Python. The registered atlas contains 14 scored cells: seven base worlds and seven disjoint remint twins. The complete grouped schema

```text
C_D6 = (S,E,R,V,H)
```

induces seven coordinate fibers, and every fiber is exact-frontier constant. The exact decision map has five equivalence classes.

The result is therefore **finite-atlas decision sufficiency**, not a universal coordinate ontology.

## Exact registered frontiers

The seven base cells reproduce the preregistered decisions:

```text
A, cap=8,  Q=16, extensional -> {xor_fold}
B, cap=8,  Q=16, extensional -> {default_exceptions}
A, cap=64, Q=1,  extensional -> {xor_fold}
A, cap=64, Q=16, extensional -> {xor_fold, default_exceptions, full_map}
A, cap=64, Q=16, proof-aware -> {xor_fold}
4-pair 3F:5R, H_key,   m=1 -> {key_index}
4-pair 3F:5R, H_value, m=1 -> {value_index}
```

Every remint twin has the same grouped coordinates, canonical semantic digest and exact frontier as its source cell.

## Why the verifier coordinate is real

The proof-aware world uses the **same Boolean obligation and same exact candidate semantics** as the extensional-verifier world. The verifier changes only registered future verification work.

For the affine XOR realization at `Q=16`:

```text
extensional:  description 4 + verification 32 + serving 16*3 = 84 ops
proof-aware:  description 4 + verification 4  + serving 16*3 = 56 ops
```

The exception and full-map alternatives retain their exhaustive verification costs, yielding `(17,81)` and `(32,80)`. Therefore `(4,56)` strictly dominates both. No inexact candidate is admitted; the verifier collision is cost sensitivity under exact correctness, not relaxed acceptance.

## Group-wise necessity

For each coordinate group, removing only that group creates an actual pair of registered worlds with equal remaining coordinates but unequal exact frontiers:

```text
Drop S:
  A cap8 Q16 extensional vs B cap8 Q16 extensional
  {xor_fold} != {default_exceptions}

Drop E:
  A cap64 Q1 extensional vs A cap64 Q16 extensional
  {xor_fold} != {xor_fold, default_exceptions, full_map}

Drop R:
  A cap8 Q16 extensional vs A cap64 Q16 extensional
  {xor_fold} != {xor_fold, default_exceptions, full_map}

Drop V:
  A cap64 Q16 extensional vs A cap64 Q16 proof-aware
  {xor_fold, default_exceptions, full_map} != {xor_fold}

Drop H:
  same 4-pair 3F:5R present world, inherited key vs inherited value orientation
  {key_index} != {value_index}
```

The witness finds these collisions by coordinate equality after dropping the group; the pairs are not hard-coded as successful merely because their names differ. Remint twins double each collision without changing the conclusion.

This proves **group-wise necessity somewhere on the registered atlas**. It does not prove every field inside every group is individually minimal.

## Decision quotient theorem

Let `P:W -> 2^M` be the exact Pareto decision map on the finite atlas and define

```text
w ~P w'  iff  P(w)=P(w').
```

Let `C` be any decision-sufficient coordinate map, meaning

```text
C(w)=C(w') => P(w)=P(w').
```

Then any two worlds in one fiber of `C` lie in the same `~P` equivalence class. Therefore every `C`-fiber is a subset of one decision class: the partition induced by `C` **refines** `W/~P`. Equivalently, `P` factors through `C`.

The decision quotient itself is thus the coarsest purely extensional sufficient partition. But it is not an explanatory coordinate system: its class labels simply restate the decision. V6 instead verifies that the interpretable architecture-name-free grouping `(S,E,R,V,H)` is a sufficient refinement and that every group is needed somewhere in the atlas.

This theorem is ordinary quotient/partition and decision-sufficiency mathematics; it is parent-owned.

## Leakage and remint controls

The predictor-visible coordinate values contain no specimen/source identity, candidate/family label, token spelling or repository path. The frozen field name `best_count_step_residual_or_null` is a structural statistic label, not a candidate identity value; the hostile checker validates the exact frozen field set separately and searches coordinate **values** for forbidden identities.

Boolean semantics are canonicalized over all five-bit coordinate permutations before hashing. Relation semantics are represented by their typed isomorphism structure. Consequently each disjoint remint twin lands in exactly the same full-schema fiber as its source.

## Parent subtraction

Strongest parents own the mathematical form:

- quotient sets and partition refinement;
- sufficient statistics / decision sufficiency;
- abstraction and bisimulation-style state aggregation;
- the individual Boolean, indexing, verifier-cost, and switching-cost mechanisms established by prior parent literatures and earlier Section D tranches.

The GMI residual is only the governance construction: freeze interpretable architecture-name-free coordinate groups, demand exact fiber constancy, and try to falsify necessity one group at a time by dropping it.

## Box disposition

At the **registered finite atlas and frozen candidate grammar only**, V6 supports:

- [x] Freeze a complete ecology coordinate schema.
- [x] Freeze a complete resource coordinate schema.
- [x] Freeze verifier/feedback coordinates.
- [x] Freeze developmental-history coordinates.

Here “complete” means decision-sufficient for the frozen atlas; it does not mean complete for arbitrary machines, arbitrary ecologies, or unbounded scales.

Claim ceiling:

```text
FINITE_ATLAS_DECISION_SUFFICIENT_COMPLETE_COORDINATE_SCHEMA_D6
GROUPWISE_NECESSARY_S_E_R_V_H_ON_REGISTERED_ATLAS
PARENT_OWNED_QUOTIENT_SUFFICIENCY_AND_PHASE_MECHANISMS
NO_UNIVERSAL_COMPLETE_COORDINATE_ONTOLOGY_OR_FIELD_MINIMALITY_CLAIM
```
