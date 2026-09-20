# Formal scope — V15 partial contexts and AJ7 separation

Read [CORE.md](CORE.md), then [THEORY_V15.md](THEORY_V15.md).
This document states the kernel boundary for the two frozen original atoms,
R2-001 and R2-004. Primary ownership is recorded in PARENTS_V15.json.
Preorder antisymmetrization and function-factorization are parent mathematics.

## Files and exact reuse

Compile these repository-relative sources in order:

1. `research/gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean`
2. `research/gmi-1068-partial-context-v15/PartialContextV15.lean`
3. `research/gmi-1068-partial-context-v15/QuotientOrderV15.lean`
4. `research/gmi-1068-partial-context-v15/SeparationV15.lean`

The V9 source is reused unchanged, not copied into the new package.
QuotientOrder imports PartialContext. Separation imports PartialContext
and RecoverabilityV9. No Mathlib dependency is introduced.

`proof_contract_v15.py` supplies ordered `SOURCE_NAMES`,
repository-relative `SOURCE_PATHS`, 28 explicit typed `ENTRIES`,
and `audit_source()`. The audit re-elaborates the stated types, including
V9's generic `recoverable_iff_fiber_constant` and
`no_recovery_of_collision`. Replaying only V11's earlier concrete
V9 registrations would not establish this reuse.

## O1: partial evaluation and observation

`Context H W` contains a domain predicate `defined:H→Prop`,
an actual function on the subtype of defined histories, and a
`PreorderSpec W`. The result relation's reflexivity and transitivity
are assumptions of the supplied result space, not derived preferences.

Admission `P:H→Prop` is a separate argument.
`relativeDomain P k` constructs `D={h | P h ∧ k.defined h}`.
Its type `RelativeDomain P` includes the proof that D is contained in P.
`restrictedEval` evaluates on that intersection using its definedness
witness. `restriction_admitted` and `restriction_value` bind the
admission and evaluator projections explicitly.

Thus the original partial evaluator on admitted histories is retained.
An ambient evaluator may additionally be defined on illegal histories;
that does not admit them or cause their values to be returned.

`Outcome W` has three different constructors:
`illegal`, `undefined`, and `value w`.
`observe` first checks admission, then evaluation-domain membership.
Three branch theorems prove its specified behavior.
`observe_has_value` proves that some value is returned exactly when
both admission and definedness hold.
Constructor-disjointness theorems cover all three tag distinctions.
An undefined-like element of W remains a value when wrapped in
`Outcome.value`; it cannot equal the unevaluated constructor.

The arbitrary predicates need not be decidable. The general observation
function uses classical decisions and is declared noncomputable.
This is a semantic construction, not an effective procedure for deciding
physical admission or evaluator termination. The finite implementation
uses explicit supplied tables; it is separate executable evidence.

## O1: induced preorder and an actual quotient poset

`pullback r f` constructs a preorder on f's domain by
comparing its actual image values under r.
`activeOrder P k` applies this to `restrictedEval`.
Its reflexivity/transitivity statements are registered.

`Mutual r a b` means comparison in both directions.
`mutualSetoid` derives its equivalence laws from r;
`mutual_equivalence` exposes those laws as a checked proposition.
`comparison_invariant` proves the comparison is unchanged by replacing
either argument by a mutually comparable representative.

`OrderedQuotient r` is the actual Lean quotient by this setoid.
`quotientLE` lifts the original relation through both quotient arguments,
using the proved representative invariance.
Reflexivity, transitivity and antisymmetry are derived for that lifted
relation; `quotientOrder` packages them in `PosetSpec`.
The construction does not assume a quotient-order conclusion.

`project_eq_iff` states that two quotient classes are equal exactly
when their representatives compare in both directions.
`quotient_comparison` states the exact comparison equation before and
after projection. `contextQuotientOrder` specializes the construction
to the admitted/evaluated domain, and the registered final
`context_quotient_comparison` binds its comparison to actual result values.

Empty domains are permitted; their quotient is empty.
A nonantisymmetric W may have distinct but equivalent values.
The quotient identifies comparison-equivalent histories, not necessarily
equal values, identical process effects, or behaviorally equivalent states.
No comparison outside the evaluated subtype is silently added.
No universal factorization theorem for this quotient is claimed here.

## O2: constructed evaluators and the fixed complete process

`Strict r lo hi` means `r.le lo hi ∧ ¬r.le hi lo`.
The construction requires this strict pair and distinct domain elements a,b.
`preferLow a lo hi` gives a the low value and every other element
the high value; `preferHigh` exchanges those assignments.
Both are actual functions, constructed using classical equality decisions.

`opposite_strict` proves opposite rankings of a,b.
`orders_different` proves inequality of the full induced comparison
functions by evaluating them at that pair.

`Models Allowed` is the subtype of actual evaluator functions satisfying
the explicitly supplied predicate Allowed.
`evaluatorObs` returns that function; `orderingObs` returns its induced
comparison function. `processObs C` always returns the entire supplied
C:Proc, with no changed field or selector used in its place.

`fixed_nonrecovery` requires membership in Allowed of both constructed
indicator functions. It applies V9's collision theorem to the actual
process and comparison maps.
`admitted_nonrecovery` additionally takes
`D:RelativeDomain (admitted C)`, so its witness histories are evaluated
members of the fixed complete process's admitted domain.

Proc is arbitrary in this theorem. The caller supplies C and its admission
map; the theorem does not invent a process model or infer physical laws.
The finite lawful process fixture is independently checked executable
evidence. The general result retains that complete process term unchanged.

V9 recovery is a decoder on the attained image of the process observation.
The proved obstruction is semantic nonrecoverability of comparison on the
declared model class, not probabilistic independence, causal autonomy,
or an algorithmic impossibility theorem under unspecified inputs.

## Conditions, exclusions and replay

`constant_no_strict` and `collapsed_no_strict` prove the no-reversal
boundary for equal values and observation-factorizations identifying a,b.
Empty/singleton domains cannot supply the distinct pair. Equivalent
codomain values do not supply a strict pair. Unadmitted or unevaluated
histories cannot supply members of the required subtype.
The constant-only evaluator class lacks the required indicator memberships.

The alternative assumption of an allowed separating evaluator plus
closure under swapping a,b is proved on paper in THEORY, not mechanized.
The separate evaluator-function nonrecovery corollary is also paper-only;
the required ordering-function obstruction is kernel checked.

Replay all four sources into a fresh .olean directory with that directory
as LEAN_PATH, then compile `audit_source()`, using
`lean +leanprover/lean4:v4.19.0 -DwarningAsError=true`.
The registration report lists only standard `Classical.choice`,
`propext` and `Quot.sound` where used. No new axioms or unfinished
proofs are introduced. Python/table correspondence is not kernel certified.
No reverse-admission recovery closure, canonical objective, complete
context-family characterization or universal intelligence derivation follows.
