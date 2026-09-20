# Independent formal implementation review — V17

Verdict: CLEAR at the exact frozen constructor and viability scope.
The reviewer authored the paper theory, but did not author the Lean modules,
proof contract or compiler driver. This review independently checks their
implementation and proof coverage, not a second independent theory authorship.

## Replay actually performed

Read all six new Lean modules and immutable PartialContextV15.lean, final
proof_contract_v17.py, check_lean_v17.py and FORMAL_SCOPE_V17.md.
Independently replayed all seven sources in a fresh isolated temporary directory
with Lean4.19.0 and warningAsError. All97 exact registrations passed.
Generated audit SHA256:
`f126965ec5a7d17593b2743cfad158147a5b6481d79ae0f2a79e6436d9a5c7ea`.
The receipt records the corresponding complete source hash inventory.

Eight extra temporary kernel examples passed in another fresh replay: actual
Bool scores0/1; a viable explicitly looping Unit state; a nonviable safe Unit
deadend; shared empty product retaining False definedness; independent empty
product having True definedness; impossibility of a nonempty Region Empty;
a concrete50-step root countdown prefix; absence of a root identity step.
These are nonvacuity diagnostics, not additional universal theorem coverage.

Independently executed the three source-valid corruption controls. Every source
compiled, and each changed program failed at AUDIT: all seven modules replaced
by import Std; shared_defined weakened to True; trajectory_to_viable and its
dependent viable_iff_trajectory jointly weakened to True. Thus the guard checks
exact domain and infinite-trajectory conclusions beyond source hash matching.
Historical sources were changed only in isolated temporary copies.

## Actual interface and order laws

The package imports the immutable V15 Context and PreorderSpec. It does not
substitute a new shadow interface. Context constructors provide their actual
evaluator, definedness and order. Registrations include equations connecting
those fields to the declared inputs, not merely Context-valued return types.

Generic postcompose accepts any function and target preorder, retains E, and
has the actual composed evaluator. Identity/composition equalities and the
complete observe/Outcome.map equation are proved. OrderMap separately packages
monotonicity; comparison preservation uses that premise. The comparison iff
adds explicit reflection. No theorem treats injectivity as reflection.
Dual retains evaluator/domain, reverses active order and proves double dual
and full observation equality.

Products are dependent finite tuples with pointwise preorder laws.
Shared products use the supplied E for all dimensions. Independent products
use the conjunction of every component domain and evaluate each component with
its actual membership proof. Registered projection and comparison equations
are restricted to the jointly defined domain. Tagged observation, presence,
undefinedness and empty independent-family equations are explicit.
The shared zero-dimensional case remains covered by its generic exact E law.

## Actual specializations and exclusions

utility is an actual Context record. intUtility is explicitly connected to
ordinary Int order and the same evaluator. The generic mathematical Real
specialization is not a new kernel Real instance and is labelled accordingly.
Acceptance converts an actual predicate to Bool. Its truth/comparison equations
are proved; the0/1 Int embedding's application and order iff are registered.
Vector and dual cost constructors have actual value/domain/comparison laws.
No totalization or scalarization is silently assumed.

Region X carries a genuine nonemptiness proof. Its precision order is reverse
inclusion; reflexivity/transitivity and antisymmetry are constructed. Confidence
contexts retain E and their actual Region evaluator. Exact comparison and
nonemptiness are registered. No probabilistic or calibration conclusion occurs.
Classical decidability of arbitrary predicates is a mathematical specialization,
not an effective procedure for every Python callback or physical system.

## Viability: conclusions derived from primitive data

The only dynamical primitives are arbitrary X, K and R. step means safety plus
an existential R-successor in the supplied predicate. Viable is the union of
postfixed predicates. Its safety, greatest-postfixed inclusion and fixedpoint
are derived; no fixedpoint theorem is smuggled in as an assumed interface field.
This part uses ordinary predicate reasoning and allows empty/nonserial models.

Trajectory requires one actual Nat-indexed function, its initial state, safety
and an R-edge at every consecutive pair. The forward proof uses Classical.choose
to select successors in the viable-state subtype, then Nat recursion. It does
not assume an arbitrary inhabitant when that subtype is empty. The reverse
proof uses the range of the given trajectory as a postfixed witness. Both
directions and the iff are individually registered at their actual quantifiers.

viabilityContext evaluates this same Viable predicate at the supplied endpoint
on E. Domain, Boolean value, active comparison and complete tagged observation
are registered. Illegal or undefined histories are not recoded as false.
The semantic interpretation of R as time-advancing is explicitly declared;
category identities do not enter its definition automatically.

CountdownV17 supplies a countably branching root and decreasing natural chains.
The finiteWalk witness satisfies the exact finite-prefix conditions for every
horizon; no continuation outside that horizon is required. Chain impossibility
is proved by induction. Root impossibility examines the actual first successor
and applies the chain theorem. The combined theorem proves all finite horizons
are possible while viability is false, using the previously proved trajectory
connection. No compactness, finite branching or universal-successor premise is
silently inserted.

## Proof boundary and authority

Finite elimination termination and cycle-reachability correctness are paper
arguments with independent finite calibration. They are not kernel proofs of
the Python algorithm or a verified compiler correspondence. Arbitrary-state
fixedpoint, infinite-run equivalence and countdown results are kernel checked.
These distinct layers match the final FORMAL_SCOPE document.

The driver rebuilds all sources with isolated LEAN_PATH, registers fixed exact
types, prints their assumptions and rejects sorryAx/forbidden proof constructs.
Standard Lean foundations remain, including classical choice where stated.
Missing toolchain/source is CANNOT_CHECK; invalid sources and types have distinct
SOURCE/AUDIT stages. No new unproved mathematical axiom was accepted.

This evidence supports only original R2-005 after all successor gates pass.
R2 remains OPEN. Qualified V16 replacements are separate from original closure;
no canonical value, continuous-time result or complete intelligence theory is proved.
