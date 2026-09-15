# D1–D8 domain-registry and reduction-infrastructure theorem v1

## Status and claim boundary

This bundle closes the eleven **infrastructure** obligations in Issue #602 J1. It
does not claim that D1–D8 are complete, mutually irreducible, new, or a minimal
basis. An open matrix cell is an abstention. A protected receipt proves ordering
and integrity only when its custody and commit time are externally inspectable.

## Definitions

Fix a registered ecology set \(\mathcal E\), intervention set \(\mathcal I\),
resource coordinates \(R\), and protected execution-and-development response
\(\llbracket x\rrbracket_{E,I}\).

A domain entry is the tuple

\[
D=(S,O,U,\sim,|\cdot|,P,F,C),
\]

where \(S\) is a typed state carrier, \(O\) its native operators, \(U\) its
development law, \(\sim\) protected-response equivalence, \(|\cdot|\) the
registered lifecycle burden vector, \(P\) the strongest-parent list, \(F\) a
falsifier, and \(C\) a claim ceiling. The exact JSON schemas for \(S,O,U\)
and burden equivalence are in `DOMAIN_COMPONENT_SCHEMA_V1.json`.

For domains \(A,B\), write \(A\preceq_E B\) only if total typed state and
operator compilers preserve every protected execution and development response,
and their full lifecycle burden is bounded in class \(E\). The relation is
directional. Define \(A\equiv_E B\) only when both \(A\preceq_E B\) and
\(B\preceq_E A\) hold under one frozen scope. E0 exact isometry, E1 frozen
constant-factor overhead, and E2 explicit polynomial overhead are accepted.
E3 approximate or empirical agreement is evidence but cannot establish exact
domain equivalence.

## Theorem

The artifacts in this directory form a finite, mechanically auditable J1
registry infrastructure:

1. `DOMAIN_REGISTRY_V1.json` contains exactly D1–D8 in order. Every row has a
   nonempty state carrier, native operator inventory, development law, strongest
   parents, evidence, falsifier, and claim ceiling.
2. `REDUCTION_MATRIX_V1.json` contains each of the \(8^2=64\) ordered pairs
   exactly once. Only the eight reflexive cells are identities. Every off-diagonal
   cell records missing state compilation, operator/update commutation, and
   bidirectional lifecycle bounds, so no absent proof is converted into a result.
3. `NEUTRAL_DOMAIN_GRAMMAR_V1.json` supplies 12 carrier and 12 operator
   constructors. Its symbols contain no D1–D8 label or forbidden family macro.
4. `collision_pairs` enumerates all \({n\choose2}\) pairs and returns exactly
   the pairs equal on frozen present coordinates but unequal on the future
   response. `negative_twin` rejects a no-op and certifies exactly one changed
   leaf.
5. `parent_reduction_tournament` sorts parents prospectively by priority. An
   absorber returns `PARENT_SUFFICIENT`; any unresolved parent forces
   `CANNOT_IDENTIFY`; a residual survives only after all registered parents are
   refuted.
6. The protected freeze is a SHA-256 commitment to canonical outcome bytes and a
   nonempty salt. The freeze exposes neither. Reveal rejects any changed outcome
   or salt.

### Proof

Items 1–3 are finite set and schema checks in `validate_registry`: ordered
domain identifiers equal \((D1,\ldots,D8)\), matrix keys equal the Cartesian
square without duplicates, diagonal status is equivalent to identity, accepted
burden classes are exact, and all 24 neutral symbols pass the macro exclusion.

For item 4, the collision generator traverses `combinations(range(n), 2)`,
which contains every unordered pair exactly once. Its predicate is precisely
equality on each frozen present key and inequality on the future key. The twin
generator compares the complete before/after leaf maps and accepts exactly the
requested singleton difference.

For item 5, finite sorting defines one order. The first absorber witnesses a
registered reduction; without one, an open parent prevents universal
refutation; otherwise every status is `REFUTES`, yielding the residual
terminal. These cases are exhaustive and disjoint.

For item 6, reveal recomputes
\(\mathrm{SHA256}(salt\|0x00\|canonical(outcome))\) and requires equality
with the frozen commitment. Therefore a nonmatching reveal is rejected under the
collision resistance assumption of SHA-256. The executable hostile controls
exercise the positive and negative branches. ∎

## Scientific disposition

This is a registry-and-test-harness result. The 56 off-diagonal reductions remain
open until domain-specific compiler, semantic-commutation, and burden proofs are
registered. Consequently this work enables future novelty tests without itself
asserting novelty or completeness.
