# GMI corpus census v1 — audit semantics

This package implements child #842 under the pre-implementation authority in `FREEZE_V1.md`.

## What the census proves

At the exact frozen source SHA, the scanner establishes a reproducible **syntactic/provenance census** for the registered path universe. It can prove that every tracked file selected by the frozen discovery rule appears exactly once in the file census and that every textual scientific marker recognized by the frozen grammar is retained as an object or explicit gap.

It does **not** prove that every scientific idea is expressible by the parser grammar, that every theorem is true, or that the repository is ontologically complete. A marker that the grammar cannot type remains an `UNKNOWN`/gap and is evidence against stronger census claims.

## Graph theorem

Let `V` be the set of discovered scientific-object IDs and let `E_c` contain only explicitly registered claim/theorem-dependency edges. The audit requires:

1. every internal edge target is unique in `V`;
2. no self-edge;
3. depth-first color/stack traversal finds no directed cycle.

If these conditions hold, the registered claim-dependency relation is a DAG. Citation, provenance, parent-comparison and evidence-production links are not silently reinterpreted as logical implication edges.

This is a standard finite graph property, not novel GMI mathematics.

## Completeness invariant

For frozen tracked candidate path set `F` and emitted file rows `R`, the census requires exact set equality

`{r.path : r in R} = F`.

Any omitted or extra path fails closed. This establishes file-level completeness relative to the frozen discovery predicate, not semantic completeness of science.

## Finite-computation / proof boundary

A complete enumeration over a registered finite universe may be a computer-assisted exhaustive certificate for that finite statement. It is not automatically an analytic proof of an unrestricted universal statement. The audit therefore keeps `UNIVERSAL` separate from `FINITE_EXACT` and flags universal wording whose only registered evidence mode is bounded executable enumeration/certification.

## Provenance boundary

The file/object records follow the W3C-PROV idea that entities and derivations/provenance must remain explicit enough to assess reliability. Here, source path, exact Git blob and frozen commit identify the source entity; generated audit artifacts record the derivation activity. This is a local adaptation, not a claim of full PROV conformance.

## Replication vocabulary

Same-team deterministic replay is recorded as repeat/reproduction evidence only at its declared scope. `INDEPENDENT_REPLICATION` requires an independently responsible team/implementation according to the #833 constitution; the census may report its absence but cannot manufacture it from CI repetition.

## Algorithm-selection parent boundary

When later GMI morphology-selection objects are audited, Rice-style problem/feature/algorithm/performance spaces are treated as a strongest-parent comparison. A GMI object is not novel merely because it renames those components ecology/morphology/performance.

## RED / AMBER / GREEN

`GREEN` means the row's **registered structural audit obligations** are discharged. `AMBER` means an explicit unresolved classification/semantic review remains. `RED` means a material integrity/proof/scope/dependency failure. An aggregate may not become GREEN while a critical RED descendant remains open.

## Strong non-claims

No output of this package alone licenses `ALL_GMI_THEOREMS_TRUE`, `ONTOLOGICAL_COMPLETENESS`, `ALL_PARENTS_EXHAUSTED`, `ALL_OVERCLAIMS_REPAIRED`, `KNOWN_FAMILY_DERIVATION_COMPLETE`, `REAL_SCALE_VALIDATION_COMPLETE`, or `COMPLETE_GMI`.
