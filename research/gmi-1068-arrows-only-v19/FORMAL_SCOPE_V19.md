# V19 formal scope — actual reconstruction and observable information

Read [CORE.md](CORE.md) first. This file delimits the kernel result.
The freeze is [FREEZE_V19.md](FREEZE_V19.md); original atom statuses stay unchanged.

## Kernel and dependency boundary

Lean 4.19.0 with Std freshly compiles thirteen sources, then a separate
explicit-type audit with 123 registrations. No previous .olean is reused.
The immutable sources are V9 RecoverabilityV9, V11 TypedPathsV11 and
V16 GroupLawsV16. The ten new modules are listed below in dependency order.
Their exact repository paths and static target types are in
[proof_contract_v19.py](proof_contract_v19.py).
The checker records source hashes and the generated audit hash.

The proofs contain no added axioms, sorry, admit or unsafe definitions.
Classical choice supports abstract local-unit selection; classical decidable
equality supports the bundled operation and anchored-unit test.
These are mathematical constructions, not algorithms for arbitrary infinite
or undecidable presentations. Small types and empty types are covered.

## S1 — partial operation to an actual category

[PartialUnitsV19.lean](PartialUnitsV19.lean) defines:
- IsUnit from self-product and neutrality whenever either product is defined;
- Algebra with actual mul:A→A→Option A, strong bind associativity,
  local left/right units satisfying that predicate, and coherence.

These three laws are premises. No Category, endpoint map, matching theorem
or reconstruction result is a field of Algebra.
unit_definition registers the exact unit predicate.
left_unique/right_unique derive uniqueness.
left/right select units with proved defining equations.
left_unit/right_unit and left_product/right_product derive endpoints.
defined_iff_matched and matching_contract prove
defined mul(x,y) iff right(x)=left(y).

[ReconstructedV19.lean](ReconstructedV19.lean) builds a V11 Category whose
objects are unit subtypes and whose Hom consists of actual arrows with those
endpoints. compose selects the existing partial product; compose_binding
ties the selected value to mul. Associativity and both identity laws are proved.
category_hom, category_identity and category_composition bind the constructor's
types and operations. This is not a finite table or an assumed category.

The equivalence with side-specific local-neutral formulations in THEORY S1.5
is a paper proof, not a separately registered Lean theorem.
The parent-formulation caveat in THEORY remains: do not silently equate these
explicit both-sided premises with weaker displayed domain-only unit clauses.

## S2 — actual converse and changing objects

[BundledCategoryV19.lean](BundledCategoryV19.lean) starts with an arbitrary
lawful V11 Category C. Its category laws are supplied hypotheses.
Arrow C is the dependent sum of all typed arrows.
mul checks middle endpoints, transports the second typed arrow along equality,
and composes using C.comp. Nonmatching endpoints return none.
aligned/not_aligned, defined_iff and algebra_mul bind these operations.
associative/coherent and identity_unit prove the partial-algebra premises.
unit_iff_identity characterizes every unit as a bundled identity.

[ArrowRoundtripV19.lean](ArrowRoundtripV19.lean) gives pack/unpack between
an arbitrary Algebra carrier and all arrows of its reconstructed category.
Both inverse equations are proved. packed_mul and unpacked_mul preserve the
entire Option-valued operation, including undefined products.

[CategoryRoundtripV19.lean](CategoryRoundtripV19.lean) supplies objectForward
and objectBackward between C's objects and the reconstructed unit objects.
Both inverse equations, injectivity and surjectivity are proved.
homForward and homBackward are actual typed maps along that object bijection;
the latter uses proved equality transports, not printed endpoint comparisons.
Both Hom inverse equations and preservation of identities/composition in both
directions are registered. object_value/hom_forward_value bind their values.
This is a changing-object construction; V11's object-fixing CategoryIso is
not used as a substitute. Object labels correspond through the explicit maps.

## S3 — operational responses and relative sufficiency

[TableTransportV19.lean](TableTransportV19.lean) defines TableIso by actual
inverse maps and full partial-multiplication preservation.
It derives reverse preservation and unit preservation/reflection.
This is a bijective translation. Mere multiplicativity is insufficient.

[ResponsesV19.lean](ResponsesV19.lean) defines the common raw Query:
a head plus a finite tail, or an empty history anchored at a candidate arrow.
No validity proof is required to submit a query.
run_nil/run_cons bind sequential execution; word/pair/singleton bindings
identify its responses. Empty responses return the anchor precisely for units,
and none precisely for nonunits. Query-map equations are also registered.
A failed composition returns none; it cannot be confused with a returned arrow.
Here none denotes nonadmission, not divergence of computing an arbitrary function.

run_transport and response_transport prove arbitrary-length preservation,
including failures and anchored empty queries, for actual table isomorphisms.
responses_eq_iff_tables_eq recovers the binary table using length-two queries.
response_recovery_iff_table_recovery proves, for every model-indexed family
of partial tables and every encoding, the equivalence of attained-image
Recoverable for the actual responses and for the actual tables.
This statement even permits unlawful partial tables; reconstruction separately
uses the Algebra premises. V9 supplies the generic recovery/fiber theorem.

[RoundtripResponsesV19.lean](RoundtripResponsesV19.lean) instantiates transport
for pack/unpack and for the actual changing-object/category Hom construction.
categoryForward_eq_pack ties that construction to the proven operation map.
All four response-preservation directions are registered.
The response function includes every finite prefix query. No hidden validity
subtype excludes failed prefixes or invalid empty anchors.

The sufficient-information class is relative to this query interface and arrow
carrier, up to declared bijective translations. This is not a primitive-count
minimum, a physical characterization or a universal intelligence theorem.
Additional external observations must themselves be transported consistently.

## S4 — kernel controls and empirical separation

[CountermodelsV19.lean](CountermodelsV19.lean) registers:
- coherence_isolated: strong associativity and local units without coherence;
- associativity_isolated/nonassoc_witness: both unit laws and coherence retained;
- two_point_unital_associative and fin_small_unital_associative;
- nonassoc_minimum_size: a unital nonassociative Fin n operation requires 3≤n;
- both projection laws and absence of every opposite-identity candidate;
- strong_definedness_isolated: weak equality, local units and coherence hold,
  while strong partial associativity fails in the actual three-arrow table;
- weak_only_witness: the explicit undefined-versus-defined bracketings.

[InformationControlsV19.lean](InformationControlsV19.lean) supplies actual
discrete/join algebras, the untagged-default collision and different unit sets.
It gives the multiplicative nonunital map, empty/singleton algebras, and a
law-preserving lift of the immutable V16 C4/V4 operations. Those operations
have identical full admission and units but different products.
The fresh tagged-bottom contrast in CONTROLS is paper reasoning; no generic
totalization theorem is claimed from the default-collision result.

The separate Python corpus checks finite operational correspondence, malformed
inputs and relabelings. Lean does not certify that Python implementation or
derive its enumeration counts. Conversely, finite enumeration does not prove
the arbitrary-carrier, arbitrary-word or recovery theorems above.

## Replay and scope

Run the package driver on laptop billy, using Python 3.12 and
GMI_LEAN_BIN=/home/billy/.elan/bin/lean. check_lean_v19.evaluate() compiles
fresh sources and the static typed audit in an isolated temporary directory.
Source-valid weakened claims must compile first and fail at the AUDIT stage.

The reconstruction and law-independence mechanisms belong to the cited
category-theory parents. This repair makes the GMI information claim precise.
R1-001/006/007 remain UNKNOWN; no original atom or new amendment is closed.
