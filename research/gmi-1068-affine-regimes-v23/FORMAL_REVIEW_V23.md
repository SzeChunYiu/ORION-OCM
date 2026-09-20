# V23 independent formal review

The reviewer authored the paper proofs and independently read all eleven new Lean
modules, the static typed contract and checker. No Lean source was edited by this
reviewer. This is independent proof-implementation review, not independent paper authorship.

## Observed fresh replay

On billy-laptop, ran check_lean_v23.evaluate() using the pinned Lean4.19.0 toolchain.
It freshly copied and compiled all18 sources into an isolated temporary directory,
then compiled122 explicit typed registrations and inspected their printed axioms.
The actual observed result was PASS. No pre-existing package oleans were reused.
All11 new source hashes matched those saved at the independent static read.
The replay record is /tmp/gmi-v23-independent-kernel.json; canonical result belongs
in RESULT_V23.json. This review did not repeat the exhaustive primary Python corpus.

Exact audit SHA256:
0b71961a6c39f735a8ca6bcb4c294428e49021f05bcd02529e980a56b4fd62ed
Exact proof_contract_v23.py SHA256:
7dd44e1e03e5f815d16152a597ca62a66d89df5f66093c4be29e60462b1c79dc
Exact check_lean_v23.py SHA256:
9376b2f266b22695c4f4f932c3e13b1907eb94e476ede178fa71c3add6d6496b

## Primitive assumptions and nonvacuity

The generic interface is the immutable V12 Scalar ordered commutative ring, including
nontriviality and primitive order/product laws. The complete actual Int instance is
freshly compiled. No endpoint/envelope/root-existence conclusion is an interface axiom.
The ordinary affine operations and actual Int arithmetic are explicitly bound.
No generic Real/Rat implementation is kernel-claimed. Their ordinary mathematical
interpretation and exact Fraction calibration are separate evidence scopes.
Classical decisions support predicate/list filtering; the checker does not portray
arbitrary predicates as an effective universally decidable machine.

## Endpoint proof strength and quantifiers

AffineArithmetic derives product signs and affine monotonicity/antitonicity.
AffineIntervals splits the sign of the difference slope and compares each arbitrary
t in [lo,hi] directly to the appropriate endpoint. Both weak and strict iff results
include endpoint necessity. They do not assume a normalized interpolation parameter
exists for every interval point. Separate interpolation identities follow ring laws.

AffineWinners retains active P/E membership and quantifies every distinct active
competitor for uniqueness. Total scalar order justifies unique iff strict; ties
are not broken. Universal weak winners and universal unique winners are separate
registered propositions, including zero-width, empty and singleton controls.

FiniteWinners constructs an actual filtered list and reuses immutable V20 frontier.
Its complete-roster hypothesis covers every active identity, not merely the listed
winner. Membership is proved equivalent to the global winner predicate, and actual
frontier cofinality earns existence for nonempty active families. List semantics do
not assert canonical deduplicated cardinality or a runtime bound.
PossibleWinners uses this existence theorem in singleton_possible. A singleton possible
set supplies an active witness; the reverse direction uses lo<=hi to exhibit an
interval point. This is not a vacuous infinite-family unique-winner inference.
Equality of that logical set with a Python rational sample union remains paper/finite.

## Actual contexts and decoding

AffineContexts constructs E-defined evaluators and score-reversed preorders, keeping
admission P separate through actual V15 observations and V20 Attained.
The full maximal predicate is related to all active scalar minima. Equivalent scores
retain distinct typed identities; no quotient or selector is substituted.
AffineDecoders proves injectivity AND order reflection, actual V17 postcomposition
equality, decoded attained/maximal-image equivalence and decoded observation tags.
ConstructorBindings registers the actual field/evaluator/order equations and the
active/list/winner predicates, so matching theorem names alone cannot supply this bridge.

## Existing roots, field boundary and nontrivial controls

RootCertificates derives difference factorization from actual affine equality,
strict orientation on either side under ordered slopes, parallel-line identity,
and uniqueness of an already-present root under strictly ordered slopes.
It assumes no desired sign-constancy theorem and proves no general division-based
root existence. General rational root enumeration, density, midpoint completeness,
interval-update invariants and certificate acceptance remain paper plus finite evidence.

Actual Int controls exhibit an interval point absent from integral interpolation,
a sign reversal with no integer equality root, singleton universal weak intersection
with an endpoint tie, changing decoded values, and a nonlinear endpoint failure.
Their definitions are themselves registered. The Int nonlinear witness is equivalent
in purpose to, but numerically different from, the fractional executable control.

## Registration and review outcome

The audit assigns each named declaration to a static explicit expected type, with
actual constructor bindings in addition to broad structure types. All imported
source bytes are bound; printed axiom reports exclude sorryAx. Missing tool/source
input is CANNOT_CHECK, distinct from SOURCE/AUDIT proof invalidity.
Read the root-owned source-valid guard: it stages source copies, requires compilation
before rejection at AUDIT, and weakens all-source/endpoint/decoder/universal leaves.
Its observed integrated outcomes belong to the canonical receipt; this review does
not substitute hash matching for that semantic mutation test.
No formal defect was found in the reviewed scope. Scope does not close R3-009,
mechanize the full rational diagram algorithm or establish a complete intelligence theory.

## Final scope read

Read FORMAL_SCOPE_V23.md in full after its finalization (164 lines), SHA256
5b5ec966ba1275d0462a34dea32a7928d544a013a961f4af618f2183bc87a606.
It agrees with the inspected proof signatures, explicitly separates index/external-label
Python refinement and logical possible winners from computed rational samples, and
keeps all field/algorithm completeness at paper plus exact finite scope. Review clear.
