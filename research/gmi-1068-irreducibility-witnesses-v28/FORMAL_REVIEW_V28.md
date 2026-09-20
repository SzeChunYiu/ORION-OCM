# Independent formal review V28

## Observed replay and reviewed bytes

An independent fresh isolated SOURCE/AUDIT replay passed with Lean 4.19.0,
20 sources (9 immutable and 11 new) and 205 exact expected-type registrations.
The checker compiled all staged sources before elaborating the generated audit,
inspected every registered declaration's assumptions and rejected sorryAx.

- Audit SHA256: cc568a9f0cefa73b67881027f091895b2ed23bb83f35bba8db689323a6e7cc9e
- Contract: dd14822ffc555f1346f52d09a7995cafde0ffa0973aa65f76facdd1c410d540f
- Checker: 756d6fab982900990868023b1866a8dd51959e50a11ce5a974aa8378fd4a641d
- Scope: 941b0462362a2db13be1bf651719a9ca91f9e1de55645ec6df815091838fdf66
- Independent receipt: 2cc52d1c262d7cf1305730bc36e49efa7a816bf698223ebd83686a9cccd8e9cb

Receipt location: /tmp/gmi-v28-independent-kernel.json.
This reviewer authored the paper, independently reviewed the other lane's
formal implementation and performed this replay. No mathematical defect remains
in the reviewed scope.

## Literal originals and actual construction bindings

All five original declarations are explicitly registered at their literal types.
OriginalBindings registers the Action cases, unequal generators, processStep,
ctx values, reach predicates, stateValue and both score equations.
The audit therefore does not rely on suggestive theorem names.

ContextBindings registers actual Path Hom, nil identity, append composition,
length/head recursion, generator histories, exact evaluation domain and evaluator,
ordinary Nat order, all-path admission, process value and interpretation equation.
The helper head's nil default is unreachable by an evaluated Context subtype.

The actual source is a complete V11 free-path category. The terminal category has
Unit arrows representing its unique effect; generator_original and interpret_single
bind this to original processStep. This is not a quotient of source histories.
The finite Python interpreter's singleton function tuples are separate
representation-correspondence evidence.

## AB1 review

rankings proves the original strict numeric comparisons on actual singleton values.
contexts_differ evaluates an assumed Context equality at h0 and derives 1=0.
order_differ checks the actual same-history comparison, not model-name inequality.
process_no_context and process_no_order invoke the actual V9 collision theorem
with unchanged complete process and unequal actual targets.

The order relation is defined on the common raw history type with explicit
definedness witnesses. It avoids comparing functions on different dependent
domain types. Generic V15 separation is separately registered with distinct
histories, strict codomain pair and both actual Allowed memberships.

## AB2 review

ThinModels derives reflexivity and transitivity from the original Bool relations.
The constructed Hom is PLift of the relation; category identity/composition
operate on these witnesses, and proof-irrelevance yields the lawful equations.
Hom inhabitation is proved equivalent to admission.

The missing/present false→true arrow proves inequality of actual category records.
stateObservation is exactly original stateValue. The strongest reverse leaf
contains the shared state observer, actual category difference, admission
difference, and both nonrecovery claims.

RawDomains uses actual V16 Admitted on the fixed labelled graph. Its endpoint
Context is shared, but the admitted source, full (P,Context) records and complete
tags differ. This does not silently substitute equal-admission C4/V4.

## AB3 review

not_illegal is proved by cases on actual admission and definedness.
admission_eq follows pointwise and by extensionality.
decode is literally the predicate that the tagged response is not ILLEGAL;
attainedDecoder applies it to the attained observation's stored value.
Its binding, correctness and Recoverable witness are registered separately.

No representative selection or inhabited target premise is introduced.
Underlying proposition decisions remain classical as in V15; “explicit decoder”
does not mean removal of all classical reasoning.

V16 singleton extraction and generated-domain equivalence are freshly registered.
All-undefined active domains coincide while crossing tags remain different.
The actual failure-erasing map merges precisely ILLEGAL and UNDEFINED, producing
equal erased functions. These are all-history proofs, not finite-sample inferences.

## AB4 review

The actual V12 Int instance supplies dot and coordinate order.
Profile/weight definitions, exact dot expansion, positivity, incomparability,
all four values and the original Nat casts are explicitly bound.
Zero/negative/equal-profile controls use actual Int sums.
The kernel's missing-premise controls use the second coordinate; the paper/Python
examples use the first. Both instantiate the same stated failure mechanism.

Generic V12 monotonicity, strictness and incomparable reversal are also replayed.
No Real/Fraction kernel instance or universal linearity theorem is supplied.

## Registration and scope limits

The audit uses static expected types, including actual constructor/application
equations and all three strongest ProofTargets leaves. It does not discover
whatever weakened types a changed source happens to export.
The source-valid mutation guard is separately required by the canonical driver;
this review does not invent its execution outcome.

The final FORMAL_SCOPE accurately separates general kernel bridges and concrete
models from finite Python adapters, exhaustive loops, ledger prose and governance.
The paper locators in THEOREM_LEDGER match actual reviewed declarations.
Only original R2-009's finite-mechanization scope is supported.
Original 003/007 authority and every whole-round status remain unchanged.
