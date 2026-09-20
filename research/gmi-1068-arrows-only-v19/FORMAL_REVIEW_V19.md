# V19 independent formal review

Reviewer authored the paper derivations but did not implement the Lean modules
or typed proof contract. This review inspected their actual definitions and
proofs; it is independent of the mechanizer, not a second paper-author review.

## Fresh kernel evidence

Independently executed check_lean_v19.evaluate() on billy-laptop with the pinned
Lean 4.19.0 toolchain. It freshly compiled all 13 sources in an isolated temporary
directory and accepted all 123 explicit typed registrations. Result: PASS.

- Contract SHA256: b696d032e88e3b48c48f1dc311ef909e769a88f3f5915653bb23466139420bf4.
- Generated audit SHA256: 05a24aca7d0a1bdc21bae626c37519995c6738b15a8502d181ad040c7fb3894f.

The three immutable dependencies are V9 Recoverability, V11 TypedPaths and
V16 GroupLaws. The ten new modules were read directly. The check rejects
unproved source constructs and inspects the axioms of every registered term.
Classical choice, propositional extensionality and quotient principles of the
Lean foundation are not claims of constructive or assumption-free computation.
The root separately reports four source-valid mutations passed source compilation
and were then rejected at AUDIT (37.693 seconds). This is reported root evidence,
not four additional executions by this reviewer. The independent positive replay
above establishes the valid no-alarm case.

## Primitive assumptions and reconstruction

PartialUnitsV19.Algebra contains the actual Option-valued multiplication and
only the declared associativity, local-unit and coherence laws. It does not
contain an assumed category or assume endpoint uniqueness/matching.
IsUnit is explicitly registered as self-product plus both conditional neutralities.
left/right are chosen from actual local-unit witnesses; their uniqueness is
proved from Option associativity and the neutralities. Definedness matching
uses coherence in its reverse direction. Composite endpoint laws are derived.

ReconstructedV19 constructs the Hom subtype, actual identity and composition.
compose_binding ties the returned subtype to the original multiplication.
Category Hom/id/composition equations are registered in addition to the category
return type; replacing the construction by an unrelated category would not
satisfy those equations. Associativity and both identities follow from the
primitive laws. The classical choices are disclosed and empty carriers are valid.

## Converse and both inverse constructions

BundledCategoryV19 retains both object labels in the dependent arrow sum.
Its actual multiplication tests middle equality and transports the second arrow.
The source proof splits endpoint equalities, obtaining none on both sides when
unaligned and actual category composition when aligned. Unit characterization
uses the category identity law and the candidate's conditional neutrality.
The constructed Algebra operation and bundled identity values are registered.

CategoryRoundtripV19 gives a genuine object bijection, then typed Hom forward
and backward maps along it. Source/target equations justify the dependent casts;
both Hom inverse laws and both directions of identity/composition preservation
are proved. No object-fixing isomorphism is substituted for the changed objects.
ArrowRoundtripV19 has actual pack/unpack inverses and preserves the full Option
operation in both directions, including None. It does not rely on a bare
multiplicative-map hypothesis that would permit a nonunital idempotent image.

## Operational interface and recovery

ResponsesV19.Query admits raw nonempty words and every candidate empty anchor.
The run equations implement sequential Option composition. Unit tests for empty
anchors and their illegal None cases are explicitly bound to the actual response.
Length-two evaluation is the original table entry; it is not an assumed observer.
The generic response-transport theorem uses an inverse table isomorphism to
transport the unit predicate and then proves arbitrary-list preservation by induction.

RoundtripResponsesV19 instantiates this transport with the actual pack/unpack
maps. Its categoryForward is explicitly built from the object/Hom maps and
proved equal to the corresponding pack map. All four forward/backward response
preservation equations are registered. Thus the operational claim is not merely
a generic theorem whose required interpretation was left unconstructed.
The response/table equality theorem and attained-image recoverability iff are
proved for any model class on a common carrier, without requiring category laws.
The description as a least information equivalence class is the paper's order
interpretation of those proved mutual recovery maps, not a shortest-code theorem.

## Nonvacuous controls and exact limits

Actual empty, singleton, discrete two-object, nontrivial one-object and C4/V4
partial-algebra constructions are present. C4/V4 uses the immutable actual
operations, with common units/admission and different product values proved.
The coherence and associativity isolation theorems retain their other laws.
The weak-law model proves weak equality, local units and coherence together
with failure of strong associativity; its displayed failure is also registered.
The total-unital size bound includes the generic two-point cover proof, the
Fin n theorem for n≤2, and the explicit lower bound 3≤n for any counterexample.
Projection controls additionally exclude every opposite-unit candidate.

The side-specific local-identity equivalence in paper S1.5 is paper-only.
The fresh tagged-bottom positive contrast in S4.4 is paper plus finite evidence;
the registered kernel statements prove the actual existing-arrow collision,
unit difference and C4/V4 difference. The historical parent wording audit is
source analysis, not a theorem about a formalized version of that entire paper.
No absolute primitive count, physical categoryhood, optional tensor elimination,
prior uniqueness or universal intelligence recovery is established.

The final FORMAL_SCOPE_V19.md was re-read against the sources and ledger; its
paper-only exclusions and 13-source/123-entry inventory agree with this review.

No defect was found in the inspected final constructions, registered equations
or independent fresh replay. This judgment concerns their declared premises
and operational interface, and does not close any original scientific atom.
