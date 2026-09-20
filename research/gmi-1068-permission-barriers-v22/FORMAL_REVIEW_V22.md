# Independent formal review V22

Read [CORE.md](CORE.md) and [FORMAL_SCOPE_V22.md](FORMAL_SCOPE_V22.md).
The final scope document was read against the inspected sources and inventory.
This reviewer authored the paper and independently inspected the other author's
Lean sources, typed contract and replay checker. It is not a second independent
paper authorship. Python calibration is reviewed separately in REVIEW_V22.

## Independent fresh replay

Ran check_lean_v22.evaluate on laptop billy with the explicit pinned Lean path.
Lean 4.19.0 freshly compiled 21 sources in isolated storage and then compiled the
145-entry exact typed audit. Result PASS. The inventory contains 12 new modules
and 9 immutable dependencies. Entries include definitions/constructor equations;
they are not 145 distinct scientific theorems.

- Scope SHA256: 860962aef8b56f466a90953dc775aec1e9c9f5e9f33e3340e1e06a1229d425ae.
- Contract SHA256: e85def9e00fbfe4ab120559414dad59c6997907e27f1ac8c26eb5f729144f98a.
- Audit SHA256: be0d49a99862b18e5da14f6c0760aa603400559198eb1364a4782632a5119968.

The checker stages every source and compiles it before the separate audit,
fixes the registered types, prints kernel dependencies, rejects forbidden proof
constructs and distinguishes SOURCE/AUDIT failures from unavailable inputs.
The generated audit's local Classical.propDecidable permits the explicitly
classical gate/filter equations; it assumes no target result. Ordinary choice,
propositional extensionality and quotient soundness retain their Lean meanings.

## Actual execution, rather than assumed support semantics

PermissionMachine constructs the actual V8 gate and accumulates requirements
from the traversed state/action cells. The exact observations, next branches,
support nil/cons and actual-endpoint append equation are registered. Equal
payloads do not force equal requirements. A missing physical edge remains absent.
PermissionExecution derives gated_success by induction, then the full successful
Response equality. The converse support condition is proved, not supplied as
an interface axiom. Generic empty state/action/permission types are allowed.

Arbitrary predicate requirements make gating classical, not an effective finite
membership implementation. Finite word length need not make every requirement
set finite. A failed gated trace need not equal a successful physical trace;
the complete-response theorem has the required success premise.

## Contexts and incidence

PermissionContexts preserves the whole actual V15 Context and changes admission.
The registered domain, evaluator, order, image and observation equations bind
those actual constructions. from_start binds the raw history's first component.
Witness includes original P, selector, physical support execution and a defined
evaluation in the declared target. Its identity includes the actual history;
no assumption collapses same-valued or same-endpoint histories.
context_incidence and context_impossible transport the same witness both ways.
The generic Cap abstraction is thus connected to actual machine/context semantics.

HistoryPermissions constructs empty requirements for baseline histories and
singleton requirements otherwise. history_admission gives the exact union,
and one_history_relief retains baseline impossibility. This theorem is a generic
history-admission specialization, not arbitrary whole-history control by graph
edges. Its actual original finite checker replay is separate executable evidence.

## Minimality and finite construction

PermissionMinimality derives available witness deficits and proves each extracted
deficit is an allowed addition. That admissibility step supports the equivalence
of minimal additions and minimal deficits; it is not valid for arbitrary omitted
interventions. Enabling explicitly uses the full allowed subset domain.

blocks_iff_hits restricts the hitting quantifier to eligible supports currently
contained in S. minimal_blocker proves actual blocking AND private witnesses,
including an actual eligible available history for each deleted permission.
Its kernel statement is slightly stronger than the Python deletion contract:
it does not require B subset S. A minimal blocker cannot contain a useless
outside-S element, as its private witness condition itself shows. The paper/API
restriction therefore introduces no soundness gap. Empty private conditions
alone are correctly shown insufficient in named controls.

FinitePermissions constructs the recursive powerset, proves exact predicate
coverage, filters by the actual property, and uses the immutable V20 frontier
under reverse inclusion. minimal_membership and minimal_below then prove the
all-minimal enumeration property and existence beneath an existing successful
set. They do not assume a minimal member as a premise. The property can quantify
over infinite histories, so classical filtering is not automatically executable.

SupportFrontier preserves capability and blocking by actual reverse-inclusion
cofinality. Its list retains equal-support aliases; Python instead groups equal
supports with all their IDs and deduplicates permission sets. Semantic list
membership is proved, not bit-level agreement with that Python output format.
No full provenance or history catalogue is preserved after strict-superset removal.

## Countermodels and registration review

Read exact controls for state-sensitive same-payload gates, both failures of
private-witness-only minimality, baseline nonidentification and already-enabled
empty additions. The two infinite-tail theorems establish no minimal enabling
or blocking set for the actual Nat tails, without finite extrapolation.
Review requested an explicit tail-definition equation; the final contract binds
tail(n,q) iff n<=q as well as exact payload/observation/requirement constructors.
No scientific conclusion is substituted by a mutable model name alone.

ProofTargets contains exact aliases for gated success, Context incidence and
minimal blockers. Root reports all four final source-valid mutation cases passed:
all-empty sources and three weakened leaves compiled SOURCE before AUDIT rejection.
That is root-executed corroboration; the fresh replay above is this reviewer's
execution. Canonical mutation outcomes remain in the integrated receipt.

No outstanding proof, premise, quantifier or constructor-binding defect was found
in the reviewed inventory. The paper's named overhead/negative-permission and
history-sensitive examples also have finite tests; they are not all additional
kernel models. Python executors are independently calibrated, not generated
from these proofs. No causal identification, universal barrier algorithm,
whole-round completion or novel classical theorem is established.
