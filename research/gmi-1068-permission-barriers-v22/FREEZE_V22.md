# V22 preregistration: permission enabling and target blockers

Control plane #1068; historical programme #833.
Parent: a79d666de82e7fca94249ea318b7eb76a984bc12 (V21, #1117).
This freeze precedes every V22 implementation, experiment and outcome.
Planning counts are algebra, not measured evidence.

## V1 — actual permission-gated finite execution

Fix an actual immutable V8 deterministic partial Machine. A present edge at
(state,action) has a declared set of required optional permissions.
Construct the actual gated Machine: preserve observations, edge payload and
destination; retain a present edge exactly when its requirements are enabled.
Absent physical edges cannot be created by permissions.
Construct finite-word execution returning endpoint and union of encountered
requirements. Requirements depend on the actual traversed state and action.
Prove empty/cons/concatenation equations and the exact success equivalence:
gated endpoint execution succeeds iff the supermachine execution succeeds
and its accumulated requirement set is contained in the enabled set.
Prove equality of complete successful V8 Responses, not just final endpoints.
Missing edges, repeated permissions, loops and empty words retain their meaning.
Arbitrary state/action/permission types are allowed in kernel statements;
finite Python contracts retain actual V8's nonempty machine constructor.

## V2 — actual context target incidence

Use actual V15 partial Context over raw histories (start,finite word).
Change admission only: original P AND declared history selector AND actual
gated physical success. Preserve E, ambient evaluator and value preorder.
Bind all observation outcomes and the actual attained-image membership.
Eligible target witnesses are original P/E selected physically successful
histories whose actual evaluated value lies in the declared target.
Derive capability iff some eligible witness's requirements are enabled,
and impossibility iff no such witness exists. Preserve history identity.
Enabling-set inclusion derives attainable-image inclusion with fixed semantics.
A generic history requirement map obeys the same incidence law only when
the admission equivalence is explicitly given; the edge construction proves it.
Fixed resource restrictions may already be part of P; permissions cannot alter
their costs, interpretation or evaluator inside this specialization.

## V3 — relative enabling and minimal blockers

Fix available permissions U and baseline S0 contained in U. Ignore any target
witness whose requirements are not contained in U before analyzing additions.
An allowed addition D is a subset of U minus S0. Prove it enables the target
iff some eligible available witness's deficit Req(h) minus S0 is contained in D.
An already successful baseline has the empty minimal addition; relief requires
initial impossibility. Under the full powerset, minimal enabling D are exactly
the inclusion-minimal witness deficits, retaining witnessing history IDs.
An arbitrary restricted intervention family needs its own feasibility condition.
The generic history-admission specialization, with freely admitted baseline
histories and one independent permission per absent candidate, recovers the old
one-history relaxation, including distinct histories of equal value. It need
not be realizable by independent edge gating on an arbitrary fixed graph.

For available enabled S, retain precisely witnesses with Req(h) contained in S.
A deletion B contained in S blocks the target iff B meets every retained support.
Derive the hitting-set correspondence from actual capability, not as an axiom.
An inclusion-minimal blocker has a private witness for every b in B:
Req(h) intersects B exactly at b, with h in that retained eligible family.
MinimalBlocker(B,S) iff Blocks(B,S) AND every b has such a private witness.
Private witnesses alone do not establish blocking, including for empty B.
Inclusion-minimal is neither minimum cardinality nor minimum charged cost.
On a finite supplied permission universe, complete subset enumeration finds
all minimal enablers and blockers. Finite descent proves existence beneath
any enabling/blocking set; no output-polynomial complexity claim is made.
Duplicate supports may be grouped only with all history backpointers retained.
Removing strict-superset supports preserves capability and blockers in a finite
roster; it cannot preserve the complete original witness identity catalogue.
Empty witness family and an empty-support target witness have different outcomes.
Infinite incidence laws do not automatically provide minimal blockers or an
algorithm enumerating every target witness. State any kernel/paper boundary.

## Eligible unchanged original record

Only GMI2-R3-007, "derive impossibility and barriers", may close.
Read its original freeze targets7/8, theory and reconciliation at original scope:
target-intersection emptiness plus a declared missing admissible condition/history.
No unique causal explanation, all physical barriers or universal intervention
family was earned by that target. Retain those boundaries in the adjudication.
R3-008/009 and every other original record remain unchanged.
If eligible evidence passes:28 fulfilled/194 unresolved originals;
the same two qualified replacements separately leave192 active unresolved.
R3 remains stale overall; no whole-round promotion or new amendment.

## Independent finite calibration

A: all two-state one-action tables with two permissions, each edge absent or
one of 2 destinations times4 requirement sets. Fixed payload(output0,cost0)
and distinguishable state observations. All starts, enabled subsets and words
lengths0..4: planned81 tables and3240 gated executions.
Independently traverse the gated table, accumulating exact stopped responses.
Check support/endpoint equivalence, every word cut, and successful full traces.
Add explicit two-action branching, nonzero cost/output, repeated permissions
and history-sensitive loop controls. Finite lengths do not prove all-word absence.

B: every family of subsets on labelled permission universes of size0..3.
Planned278 families,2122 family/enabled-subset pairs.
Compare direct support containment with exhaustive intervention evaluation;
all baselines and available subuniverses, additions/deletions, minimal sets,
private witnesses, duplicate supports and finite antichain reduction.
Measure actual loop counts. Do not assume every support fits a smaller universe.

C: actual V15 contexts over n=0..2 unique singleton-action histories.
One-state machine; each action absent or present with one of4 requirement sets;
present payload(output0,cost0). For n=0 use one unused absent action.
m=0..2, all P flags and None-or-value assignments, E exactly defined domain,
and discrete value preorder. Every history selector, enabled subset and target.
Planning1463 machine/context instances,5723 selectors,22892 enabled images.
Compare actual gated Context admission/tags/images with independent traversal;
target-witness IDs, incidence and relative intervention results must agree.
Replay the original R3 one-step-relief helper on its declared real fixture and
an independently derived added-history witness roster; do not rewrite old scope.

## Countermodels and revival

AND path needing a,b has no singleton enabling addition; the pair succeeds.
OR alternatives a versus b give nonunique enablers and a joint blocker.
Equal baseline images can have different missing permissions: retain requirements.
Distinct histories with one target value remain distinct intervention witnesses.
P-illegal, undefined or physically failed histories are not target witnesses.
An endpoint-returning loop can be the only target history; retain history context.
Mandatory activation overhead can remove affordability; charge it in a changed
context instead of asserting the fixed-semantics monotonicity theorem.
Negative permission conditions violate positive incidence; revive with explicitly
intervention-indexed contexts rather than pretending their supports are monotone.
Off-universe supports must be excluded before deletion/addition analysis.
Private witnesses for B={a} against supports {a},{b} do not make B a blocker;
B empty vacuously has private witnesses yet may leave a target reachable.
Different cardinality and priced minima must not be called the same optimum.
Empty universe/family/support, initially enabled target and no physical path
need separate valid outcomes. Infinite-tail supports lack guaranteed minimal
enabling sets/blockers: paper counterexample, not finite extrapolation.

Validate complete inputs before early returns: unused transitions, all words'
suffixes, requirements, history dimensions, targets, additions and deletions.
Reject Bool/integer aliases, duplicate set members, duplicate raw histories,
out-of-domain indices, ragged matrices and mismatched absent-edge annotations.
Valid empty result, invalid input and unavailable verification remain distinct.

## Evidence and custody

Pinned Lean4.19.0, isolated SOURCE builds and exact typed AUDIT with axiom scan.
Register actual recursion, gating constructors and Context fields.
Source-valid mutants compile SOURCE but fail AUDIT, including gating success,
context incidence and private-witness/minimality theorem leaves.
Independent expected results cannot call production. Replay normally and -O;
integrated receipts must match bytes. Real no-alarm, malformed inputs, exact
coverage attacks and coupled receipt/snapshot/accounting mutations are required.
Receipt binds every science source and review. Successor preserves all untargeted
records and immutable V16 qualified authority. Use actual-target-base CI custody.
Every scientific result gets its own verified PR and merge. Modular files<=200lines.
Affine regimes and exact legacy transports remain subsequent registered work.
Classical integration is not a novelty claim or a completed general theory.

## Primary parents and applicability

Eiter/Gottlob, Hypergraph Transversal Computation and Related Problems in Logic
and AI (JELIA2002), introduction, dualization and theory-revision sections:
https://www.kr.tuwien.ac.at/staff/eiter/et-archive/files/jelia02-tr.pdf
This owns minimal hitting-set duality. The actual execution/Context mapping is
an adaptation; finite powerset enumeration imports no advanced complexity result.
Halpern/Pearl, Causes Part I, §§2–3:
https://www.cs.cornell.edu/home/halpern/papers/actcaus.pdf
Structural causal equations and actual-world/contingency conditions are extra
assumptions. Optional edge gating alone does not establish actual causation.
Original R3/AF sources own scope and optionality discipline; V8/V15 own semantics.

## Immutable input SHA256 bindings
- `research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json` `4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574`
- `research/gmi-1068-r3-contextual-attainability-v1/FREEZE_V1.md` `e9f25acb58dc24f2bda8ae6dfeab4e78660f3e1ffc664638b74b76d7f5557209`
- `research/gmi-1068-r3-contextual-attainability-v1/THEORY_V1.md` `6298fda4b6a2f4feb63c98f103c69ffea2602ec86e58fbbfb7dcad06c4aa8c9a`
- `research/gmi-1068-r3-contextual-attainability-v1/RECONCILIATION_V1.json` `8d0243b5ee46ff731b5a52c70d18d573ffe0504b6bd6a5be6f005de31206e925`
- `research/gmi-1068-r3-contextual-attainability-v1/check_r3.py` `7862cbb10877bb80a21182b53fac6253e8707fcf76620552fbe5e9a0d4effcd4`
- `research/gmi-1068-continuation-v8/ContinuationV8.lean` `daca89f4bb32898b285a993ad5de777acbcbcffbf10b0c888b10dfc8accf4da4`
- `research/gmi-1068-continuation-v8/continuation_v8.py` `16f5ba400ea3475b1fc7f58a594ca283aa9d8cf2710095a56a81b9f96c146f02`
- `research/gmi-1068-partial-context-v15/PartialContextV15.lean` `332dcfb63304d5668800ea21f09795c2d92267989291ffe35d9e38ea2db0edf5`
- `research/gmi-1068-partial-context-v15/context_v15.py` `75c62203c8ae61ddce1081f9deaf463dfce6965bb160086a8e21adfe787fcd2f`
- `research/gmi-1068-resource-attainability-v21/core_v21.py` `b82dae0672daf40757c9ec5df52b3ce9cdc78500f81b97250264bcc525040f05`
- `research/gmi-1068-resource-attainability-v21/RESULT_V21.json` `b519fa7752e29d9149c0edc424bb6b8421f48689df1d684a01350ad5f66a10c2`
- `research/gmi-1068-recursive-audit-v21/SCOPE_SNAPSHOT_V21.json` `2ae7e752d97a411a5bbad8cda89c169dfdd109cca99a3f23d48f2b0ab29a068a`
- `research/gmi-1068-recursive-audit-v21/CURRENT_ACCOUNTING_V21.json` `65ee87edaca81ed3cf2ba72ecdc02c66040c29f33be7f7ccf2aee95d1ec8452e`
- `research/gmi-1068-corrected-targets-v16/RESULT_V16.json` `18bea5c6f85b4fcc91c40c53cbf63df59c38d70e9e839efc4585f6640497ad1a`
- `research/gmi-1068-amendment-governance-v16/AMENDMENT_LEDGER_V16.json` `e1cc2d2dbc10171407577889f75ac531c30cf09eab224fc3823f3931c5048618`
- `research/gmi-1068-amendment-governance-v16/RESULT_V16.json` `ed491fab2cd0b69fb4ee845b82e349c79ff0d70f0dbc1d312ee0755645437de4`
- `research/gmi-833-af-barrier-context-v1/FORMALIZATION_V1.md` `edd0ac4551aee307b84b325730cb40a3b946e6f338cebc7573a0b3dc4834c2d9`
- `research/gmi-1068-resource-attainability-v21/OrderedCostsV21.lean` `d74f0c1b61f7f03f0d14826f56214fe83b05bb5371d600454d53c293b217962c`
- `research/gmi-1068-resource-attainability-v21/WeightedExecutionV21.lean` `028bce29bb3446c7213908e07503daf063655150a74340b4ddb33a46c0e48420`
- `research/gmi-1068-resource-attainability-v21/CumulativeV21.lean` `4e02e2d8825d5f9660ee08889c08f5feb83482fd4113386d27799f7a02f959ea`
- `research/gmi-1068-resource-attainability-v21/BudgetResidualV21.lean` `806d15f5c18e0d9a34dec538aa579591baa2c35a5f0236fa4a401e6f8c2cf659`
- `research/gmi-1068-frontier-simulation-v20/FrontierOrderV20.lean` `ec4a10f31365a2e304dd12b599e7c0ac83e3996c31e3a6b6f7307252e8d24bf4`
- `research/gmi-1068-frontier-simulation-v20/GuardedMapsV20.lean` `343d1cdd1897b854c57d6885cdaf46daca70dd405a4248485780d63c3fabf176`
- `research/gmi-1068-frontier-simulation-v20/PartialPostcontextV20.lean` `909ed050209b15d797138a30231eca9b12393618052c73607788725a9bc7e8f8`
