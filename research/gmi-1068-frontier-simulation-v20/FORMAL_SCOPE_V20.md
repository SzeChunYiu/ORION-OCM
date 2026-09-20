# Formal scope V20

Read [CORE.md](CORE.md) first. This file delimits the kernel evidence for
[FREEZE_V20.md](FREEZE_V20.md); it does not change original atom authority.
The mathematical parents and general proofs are identified in the theory files.

## Replay and custody

[proof_contract_v20.py](proof_contract_v20.py) registers 100 explicit types,
including constructors, their operational equations, and theorem statements.
[check_lean_v20.py](check_lean_v20.py) freshly compiles ten sources in an isolated
temporary directory using Lean 4.19.0 with warnings treated as errors.
Nine sources are new; the immutable V15 PartialContext source is the tenth.
No previously built project object files supply the replay.

The generated audit binds each declared type to its named source term and prints
its kernel dependencies. These are 100 registrations, not 100 independent
mathematical results. The audit uses fixed reviewed signatures; it does not
discover types dynamically during verification.
The initial fresh replay passed with audit SHA256
`5eecc29b032a58934de79edd0383da1858ddfa09963b69bc31dd4d57660f90fc`.

Run from this package on laptop billy:

```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 -c \
 'import check_lean_v20; print(check_lean_v20.evaluate())'
```

Unavailable source/compiler inputs produce CannotCheck; source or typed-audit
failures produce InvalidProof with a distinct stage. Source-valid hostile
replacements must compile before the independent typed audit rejects them.
ProofTargetsV20 provides three independent exact-statement leaves for this test.

## Finite frontier

[FrontierOrderV20.lean](FrontierOrderV20.lean) uses V15 PreorderSpec directly.
Its actual `extend` list scan keeps a candidate or replaces it by an element
above it. The proved invariant establishes attained membership, domination of
the initial candidate, and maximality among all scanned values.

The actual `frontier` filters the input list by the maximal-element predicate.
`frontier_mem`, `frontier_cofinal`, and `frontier_down` prove its exact
membership, cofinality, and equality of downward closures. No maximal element or
cofinal frontier is supplied as an assumption. Empty input returns empty.

The comparison relation has an explicit DecidableRel argument. Thus this finite
algorithm is effective when that decision procedure and the finite input are
effective. The proof does not provide a comparison algorithm for arbitrary
mathematical preorders.

Theorems use list membership as a finite-set presentation. Repeated occurrences
of exactly the same value may remain in the Lean output; Python deduplicates
them. Distinct mutually equivalent maximal values remain eligible in both
set-level descriptions. No conclusion about cardinality follows from Lean list
length. Selection of one representative per maximal equivalence class and its
minimum cardinality are general paper proofs plus finite calibration, not
kernel claims in this package.

## Arbitrary-carrier extension

[WellFoundedFrontierV20.lean](WellFoundedFrontierV20.lean) constructs a maximal
extension using induction on the attained subtype. Its explicit well-founded
relation is `Ascent y x := x ≤ y ∧ ¬ y ≤ x`: recursive calls move upward.
It proves cofinal maximal elements and equal downward closures.

Well-founded strict ascent is sufficient, not necessary. The theorem neither
asserts a finite frontier nor supplies an effective enumeration for an arbitrary
carrier. Classical case distinction is used. There is no assumption that mere
finite length of each history makes the entire history family finite.

## Guarded partial transformations

[GuardedMapsV20.lean](GuardedMapsV20.lean) works with actual `X → Option Y`
functions. Guarded monotonicity requires every defined source value to have a
defined dominating counterpart at every dominating source.

`image_cofinal` and `image_down` apply to arbitrary cofinal subsets.
`guarded_iff_finite_preserves` proves necessity from the concrete two-element
list `[x,x']` pruned to `[x']`, and sufficiency for every finite cofinal pruning.
Lists present finite subsets extensionally; repetitions do not affect this
equivalence. Composition is actual Option bind, with its guarded law proved.

Downward-closure equality is equivalent to existential attainment of all upward
goals. This is not preservation of arbitrary singleton goals, universal safety,
probability, multiplicity, history identity, or a preferred action witness.

## Actual partial contexts and attained images

[PartialPostcontextV20.lean](PartialPostcontextV20.lean) constructs an actual V15
Context. Its new domain consists of original defined histories whose evaluator
value has a defined image under the partial function. Its order is the supplied
target preorder; its evaluator is the unique returned value.
The proofs bind that value to the actual Option result.

Admission P is retained at restriction and observation. `post_active` exposes
the full conjunction with P; guard failure is UNDEFINED, not ILLEGAL.
`post_observe` preserves all three tagged outcomes through an explicitly
defined outcome map. `post_valueMap` and `post_attained` establish the actual
Option composition and defined attainable-image equations.

The abstract Context contains arbitrary propositions and dependent evaluators.
The construction therefore uses classical choice; this is not a general
executable test for arbitrary domains. Finite table implementations have their
own finite-calibration evidence.

[AttainedFrontierV20.lean](AttainedFrontierV20.lean) obtains the image from an
actual finite history list by filterMap of the P-and-E restricted evaluator.
Membership is exactly `H_x(h) ∧ P(h) ∧ E(h)` with the evaluator value, where
H_x is membership in that list. It then proves the resulting frontier is
cofinal, preserves downward closure, and preserves existential upward goals.
Illegal and undefined histories contribute no value.

## Continuations and endpoint compatibility

[SimulationV20.lean](SimulationV20.lean) defines actual deterministic partial
execution and the union of all simulations contained in the declared base
preorder. The union is proved to be a simulation and a preorder.

`greatest_iff_words` characterizes it by all identical finite action words:
every defined source run has a defined target run with a base-related endpoint.
The empty word enforces the base relation. This is one-sided admission
preservation; the target may admit additional words. Determinism supplies a
single successor for all suffixes. The theorem does not extend unchanged to
nondeterministic transitions or comparisons using different words.

[SimulationPruningV20.lean](SimulationPruningV20.lean) proves every action and
word guarded for the constructed simulation preorder, then transports cofinal
pruning. The endpoint-value bridge uses an actual V15 Context and explicitly
requires its P-and-E restricted `valueMap` to be guarded under the base order.
Because simulation is contained in that order, the bridge proves cofinal
endpoint images and preservation of existential upward value goals.
An arbitrary endpoint context need not satisfy this requirement.

## Explicit limits

The finite synchronous relation-refinement algorithm, its deletion/termination
bound, independent shortest pair-search correspondence, and Python-to-Lean
implementation correspondence are paper proofs and finite tests.
This package does not contain a kernel proof of that Python program.

The V8 budget-lift adapter is independently calibrated as a destination-state
projection into this declared endpoint interface. Its residual budget changes
admission. This package proves no equality of full intermediate EDGE/output/cost
traces, and contains no new kernel extraction of the Python budget adapter.

ConstructorBindingsV20 binds the actual algorithms and observer equations;
ProofTargetsV20 isolates the three source-valid hostile audit targets.
Classical.choice, propext and Quot.sound may occur as ordinary Lean dependencies;
no added unproved scientific assumptions replace the frontier or simulation
constructions. Finite results and these relative theorems confer no
context-independent ranking, prior-free unique scalar score, or universal
machine-intelligence derivation.
