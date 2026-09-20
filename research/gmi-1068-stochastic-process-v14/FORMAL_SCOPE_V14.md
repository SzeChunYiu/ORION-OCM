# Formal scope — V14 optional stochastic structure

Read [CORE.md](CORE.md), then [THEORY_V14.md](THEORY_V14.md).
The parent constructions are classical finite stochastic matrices and
total relations; source ownership is recorded in PARENTS_V14.json.
Kernel checking does not itself establish novelty or programme completion.

## Module and registration inventory

Use Lean 4.19.0, Std, and the following dependency order:

1. `WeightSumsV14.lean`: primitive weight laws and recursive finite sums.
2. `MatricesV14.lean`: typed finite matrix and normalized-kernel composition.
3. `RelationsV14.lean`: total relations on arbitrary state types.
4. `SupportV14.lean`: support as a composition-preserving map.
5. `RationalModelV14.lean`: the actual seven-arrow rational example.

Matrices imports WeightSums; Support imports Matrices and Relations.
Relations and RationalModel are otherwise self-contained Std modules.
RationalModel additionally imports `Std.Internal.Rat`.
There is no Mathlib dependency or implicit use of the local Lean 4.14 library.

`proof_contract_v14.py` contains this ordered `SOURCE_NAMES` inventory,
37 explicit typed `ENTRIES`, and `audit_source()`.
The audit registers theorem values at their advertised types and prints
their kernel dependencies. It includes the concrete Nat data instance
and actual rational-entry statements, not only generic declarations.

## N1: generic finite weight matrices

`Weight α` supplies primitive scalar operations/laws:
commutative additive monoid, associative unital multiplication,
left/right distributivity, absorbing zero, and `1≠0`.
It also supplies zero-sum freeness
`a+b=0 ↔ a=0 ∧ b=0` and absence of multiplicative zero divisors
`a*b=0 ↔ a=0 ∨ b=0`.
No matrix-category, normalized-composition, finite-sum-support or
deterministic-embedding conclusion is a field of this interface.

The intended probability interpretation takes α to be the **nonnegative**
scalar carrier. Nonnegativity of entries is then represented by their type.
The abstract interface also permits carriers such as Nat and the Boolean
semiring; it is not by itself an ordered-field or probability interface.
In the ordinary nonnegative rational/real interpretation, nonzero support
equals strictly positive support. Those general interpretations are paper
proofs, not installed Lean instances in this package.

`sum` recursively sums over arbitrary `Fin n`, including zero.
Distributivity, sum interchange, selection of a single indexed term,
zero-sum characterization and `sum_support` are proved from scalar laws.
No finite dimension bound or enumerated matrix corpus is assumed.

`mcomp` is the actual first-then-second matrix product.
`mcomp_assoc`, `mid_left` and `mid_right` establish its category laws.
`dirac` maps functions to zero/one matrices;
`dirac_normalized`, `dirac_comp` and `dirac_faithful` prove the
claimed deterministic representation.

`Kernel α n m` contains a matrix and proofs that all row sums equal one.
`comp_normalized` proves closure. Namespace `Kernel` defines actual
`comp`, `ident` and `embed`, and proves associativity, both identity
laws, composition preservation and faithfulness.
Preservation of identity by embed is definitional: `ident n=embed id`.

These Lean signatures use the whole `Weight` interface, including its
support assumptions. The matrix-category/normalization proofs do not use
zero-sum freeness or absence of zero divisors. THEORY's ordinary-semiring
version states that sharper assumption boundary on paper; this package
does not introduce a separate weaker Lean superclass.

The concrete `natWeight` instance proves consistency of the interface.
Normalized natural-number rows provide deterministic examples only.
It is **not** the witness of nontrivial stochasticity.
A normalized zero/one row need not be single-valued over every Weight
carrier, since Boolean addition is idempotent. No such generic
determinism characterization is asserted.

## N1: relations and support

`TotalRel A B` is an actual relation plus
`∀ a, ∃ b, relates a b`.
Its construction and category laws quantify over arbitrary state types,
not just finite fixtures. Composition uses an existential intermediate
state, and its totality proof combines the two given totality witnesses.

`TotalRel.graph` is the singleton embedding. Its identity preservation
is definitional; composition preservation and faithfulness are proved.

`Kernel.support` uses nonzero entries. Totality is derived from
normalization, `1≠0`, and finite-sum support.
`support_comp` proves equality with actual relational composition using
the derived finite-sum and scalar-product support equivalences.
`support_embed` and `support_ident` prove compatibility with functions
and identities.

For both models, empty-domain uniqueness is proved. Existence follows
by embedding the empty function (`Fin.elim0` or `Empty.elim`).
A supplied source element excludes arrows into the empty codomain.
Thus absence of source elements and absence of possible outputs are
not conflated.

## N2: concrete rational probabilities

`RationalModel.Arrow` has identity, flip, zero, third, half, twoThirds
and one. The last five are constant rows with the indicated probability
of true. `matrix` returns actual `Std.Internal.Rat` entries built
with `mkRat`, using ordinary rational arithmetic from that module.

Finite case proofs establish nonnegative entries, row normalization,
the displayed matrix-composition equation, faithful matrix interpretation,
and the category laws of `comp`.
`reduced_entries` checks positive denominators and coprime numerator/
denominator for every actual entry.
`event_probabilities` binds the advertised entries to `mkRat 1 3`,
`mkRat 1 2` and `mkRat 2 3`; `half_nontrivial` proves the half
entry is neither zero nor one.

`encode` takes any function Bool→Bool into the four deterministic arrows.
Its actual Dirac entry equation, identity/composition preservation and
faithfulness are all proved. This is a concrete rational realization,
separate from the abstract scalar-interface embedding.

`support_probability_loss` proves the third and twoThirds kernels
have equal support but unequal probabilities for the same event.
The proofs use kernel `decide` and finite case splits, not a native
execution shortcut, supplied category laws, or the Python oracle.

No `Weight Std.Internal.Rat` instance or general rational algebra-law
development is provided. The concrete checked calculations do not imply
such an instance. General rational/real stochastic categories remain
paper specializations of N1; no real-number implementation is imported.

## Replay and exclusions

The root-owned checker compiles all five modules with
`lean +leanprover/lean4:v4.19.0 -DwarningAsError=true`.
Use a fresh directory for .olean files and set `LEAN_PATH` to it.
Compile in SOURCE_NAMES order, then compile the generated audit.
Dependencies reported by the registrations are drawn from Lean's standard
`propext`, `Quot.sound` and `Classical.choice`; no new axioms or
unfinished proofs are introduced.

The independent Fraction corpus, its malformed-input tests and its
counterexamples are separate executable evidence. No kernel-checked
Python/Lean correspondence or full Markov-category packaging is claimed.
The package supplies ordinary typed sequential process instances.
It does not choose a prior, recover probability from support, derive
physical randomness, or establish universal architecture recovery.
Only the frozen R1-008 atom is eligible for adjudication.
