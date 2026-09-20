# Independent formal review — V15

Verdict: all reviewed general statements and their exact scope are sound.
Independent fresh replay passed all four sources and all 28 typed registrations.
No remaining mathematical defect was found.

The reviewer authored THEORY/ADJUDICATION but did not author the Lean modules,
proof contract or statement-corruption guard. This is an independent review
of those implementations and their claim boundary. Read REVIEW_V15 for the
separate executable construction defect and its completed repair.

## General source and exact-type review

Read all three new Lean modules, the actual reused RecoverabilityV9 source,
the 28 explicit registration types, FORMAL_SCOPE and the root-owned checker.
The original V9 file is compiled from its repository path, not replaced with
a copied or rephrased proof. Its source SHA256 remains
`164768fbda9a973001312c04e8ad07626de64b3fa0ec44fbd45391d7a0a704bd`.
Both recoverable_iff_fiber_constant and no_recovery_of_collision are freshly
registered at their general types. Earlier V11 finite registrations are not
used as authority for this new generic application.

PreorderSpec assumes precisely the supplied value relation's reflexivity and
transitivity. The constructed pullback relation compares actual evaluator
values; its laws follow by substitution, rather than assuming a contextual
preorder as a field. The codomain need not be antisymmetric or inhabited.

RelativeDomain records a domain contained in admission. relativeDomain P k
constructs the intersection P∩E and restrictedEval uses the definedness proof.
This retains the original partial evaluator on admitted histories. The ambient
Context structure alone is not silently substituted for that original context.

Outcome has three distinct constructors. Branch theorems prove illegal,
undefined and evaluated behavior, and observe_has_value characterizes the
intersection exactly. Constructor-disjointness keeps a value named undefined
separate from an undefined result. observe uses classical decisions for
arbitrary predicates; no executable admission/termination decision procedure
is derived. The finite tables are separate computation evidence.

## Quotient construction

Mutual is the conjunction of both comparison directions. mutualSetoid and
mutual_equivalence derive reflexivity, symmetry and transitivity. The proof of
comparison_invariant composes the correct directional inequalities on both
sides. quotientLE is an actual binary Quotient lift using that invariance.

The quotient relation's reflexivity and transitivity follow by quotient
induction; antisymmetry follows from Quotient.sound on the two comparisons.
No partial-order law on the quotient is an assumption. project_eq_iff and
context_quotient_comparison bind equality and ordering to the actual underlying
relation and restricted evaluator. Empty domains are permitted; no default
representative or value is introduced. Contextual ties are not behaviorally
interchangeable histories, and no such process claim appears in these types.

## Separation and complete-process observation

preferLow/High are actual indicator functions, with the same three-or-more
history formula now used by corrected Python. opposite_strict evaluates at
a,b under a≠b and an actual strict codomain pair. orders_different evaluates
the resulting binary comparison functions at that pair. Distinct codomain
values alone would not suffice; the strict reverse inequality is explicit.

Models Allowed contains the actual functions and their membership proofs.
processObs returns all of the supplied C:Proc unchanged. The nonrecovery proof
constructs two members of Models Allowed, uses definitional equality of their
full-process observations and the proved inequality of their actual ordering
functions, then applies the freshly replayed V9 collision theorem.
admitted_nonrecovery requires the history subtype of a domain included in
admitted(C), excluding witnesses outside the permitted evaluated domain.

Proc and its admission interpretation are supplied by the caller. No new
lawful-process existence is assumed to follow from an arbitrary data type;
the actual lawful C3 witness is independently checked executable evidence.
The polymorphic theorem retains any such complete term unchanged and needs
no deletion of process fields to establish the collision.

constant_no_strict and collapsed_no_strict prove the equal-value and
observation-factorization controls. Allowed membership of both indicators is
an explicit premise; no universal indicator or transposition closure is hidden.
Semantic nonrecoverability is not a statistical independence statement.

## Statement-corruption audit

Independently executed test_kernel_guard_v15 on billy-laptop: all three
mutants were rejected at AUDIT after source compilation succeeded. Mutations
were import-only replacement of all four modules, weakening the actual final
context quotient comparison to True, and weakening admitted_nonrecovery to
True. No original research source was edited. These tests verify exact-type
registration failures, not mere manifest-hash or source-syntax rejection.

The checker uses pinned Lean4.19.0, fresh .olean output and warningAsError,
then inspects the generated audit's printed axioms. Missing input/tool errors
must retain the separate CANNOT_CHECK pipeline status. The guard is one layer;
it does not replace reading definitions or the independent Python oracle.

## Scope retained

The separate evaluator-function nonrecovery corollary and the alternative
swap-closure sufficient condition are paper-only. The required ordering
nonrecovery and actual contextual quotient are kernel checked. The stronger
claim that every original partial context has an ambient representation is a
set-theoretic paper construction; the implemented restriction direction is
explicitly registered. No full context-family classification follows.

No certified extraction connects the Python code to Lean. No preferred value
scale, reverse-admission theorem, universal weighting claim or complete GMI
result is established. Only the two frozen original requirements may change.

## Independent replay and specialization evidence

Copied the four actual sources into a fresh temporary directory on
billy-laptop, compiled in contract order with a fresh LEAN_PATH and
Lean4.19.0 warningAsError, then compiled the generated exact-type audit.
All 28 registrations passed; dependencies were confined to propext,
Quot.sound and Classical.choice. No sorryAx or new axiom was accepted.
The generated audit SHA256 is
`f00d0ce7682107423295dea0364591b4919d48b2c2bf2d9321da3ca73c3f2380`.

| New source | SHA256 |
| --- | --- |
| PartialContextV15.lean | 332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5 |
| QuotientOrderV15.lean | cbc87018840c5622e3b7311d46c85f6dcaff4a0a448211e2830cf31c3eda91b7 |
| SeparationV15.lean | 2a043db0cb0adb1143120106403395317cbec0520ef4c147d5632c77960c346b |

Five additional temporary specialization theorems passed:

1. Universal comparison on Bool identifies false and true in the quotient.
2. A defined ambient value on an illegal Bool history still observes ILLEGAL.
3. VALUE("UNDEFINED") differs from the UNDEFINED constructor.
4. Three admitted/evaluated histories with Nat order and exactly the two
   permitted indicators instantiate admitted_nonrecovery for an unchanged
   compound process-observation term. This probe checks general type use;
   the lawful C3 process example is separately tested in Python.
5. Equal observed values cannot form a strict comparison.

Probe elaboration was corrected before acceptance; failed drafts were not
counted as evidence. These five diagnostics do not add receipt coverage or
new original closures. The stored source bindings identify the reviewed
proofs; the integrated driver supplies the final production receipt.
