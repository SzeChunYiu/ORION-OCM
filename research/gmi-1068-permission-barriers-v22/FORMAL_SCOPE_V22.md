# V22 formal scope
Read after CORE and the frozen V1–V3 contract. This file states what the
kernel proves; finite Python calibration and scientific adjudication are
separate evidence. Only original R3-007 is eligible. No complete GMI claim.

## Replay and exact inventory
Pinned Lean4.19.0 with Std, warningAsError, fresh isolated source builds,
then explicit typed registration and printed dependency inspection.
21 sources:9 immutable dependencies and12 new proof modules.
145 registered declarations, including actual operation equations.
The contract contains static reviewed signatures; runtime replay does not
discover types from the source it is meant to check.
Fresh SOURCE and AUDIT pass; registered proof dependencies are within
propext, Classical.choice and Quot.sound. No added postulates or gaps.
The checker rejects prohibited proof constructs and unproved dependencies;
an unavailable compiler is distinct from an invalid source or audit failure.

Run on laptop, from this package directory:
```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 -c 'import json, check_lean_v22; print(json.dumps(check_lean_v22.evaluate(), sort_keys=True))'
```
The repository driver supplies its own isolated sibling-module loading.
The checker freshly stages and compiles every listed source in dependency
order, overriding LEAN_PATH with that temporary directory.
The immutable dependency closure is V15 PartialContext, V8 Continuation,
V21 OrderedCosts/WeightedExecution/Cumulative/BudgetResidual and
V20 FrontierOrder/GuardedMaps/PartialPostcontext.
No inherited source is edited. Their exact paths and bytes enter the receipt.

## Actual permission execution
PermissionSetsV22 defines predicate subsets, union, difference, singleton,
and inclusion-minimality, with the elementary transport proofs.
PermissionMachineV22 constructs an actual V8 Machine.
Its edge requirement function takes BOTH current state and action.
A missing physical transition stays missing; a present transition retains
its original payload and destination iff every requirement is enabled.
Observations are unchanged. The output/cost interpretation inside a payload
is inherited, not replaced by a newly invented scalar cost.
The generic gate is classical because arbitrary subset predicates need not
be decidable; the finite implementation uses checked explicit membership.

support recursively traverses the actual base transitions and returns
Option(endpoint, accumulated requirement predicate).
Empty word returns the actual start and empty predicate; a missing physical
edge or failed suffix returns None. A successful step unions its own
state/action requirements with those of the recursively reached suffix.
support_cons, support_endpoint, endpoint_support and support_append bind and
prove this actual recursion, including the real intermediate endpoint.
Finite words need not have finite support when individual edge requirements
are infinite predicates. Finite-support algorithms require the extra premise.

PermissionExecutionV22.gated_success proves, for arbitrary types and EVERY
finite word, gated endpoint success iff the actual accumulated support is
contained in the enabled set. It is proved by transition/word induction.
full_successful_response proves equality of the complete actual V8 Responses
on success: all intermediate observations, edge payloads and terminal obs.
No equality of failed responses is claimed; a gate can reject earlier.
success_mono, all_permissions and successful_base are derived corollaries.
V8 next is a total mathematical Option-valued function; None means a missing
transition, not a theorem about divergence of an arbitrary computation.

## Actual partial-context bridge
PermissionContextsV22 uses raw histories (start,finite action word).
scenario contains a changing admission and the original actual V15 Context.
Admission is original P AND a declared selector AND successful gated execution.
The context's domain, subtype evaluator and preorder are preserved exactly.
fromStart uses the literal first component of a raw history, so a fixed-start
restriction is not represented by a parameter absent from execution.
Image is the actual immutable V20 Attained construction.
image_membership and context_incidence derive the exact support-witness
characterization of that image and its intersection with a declared target.
context_impossible is target-intersection emptiness, with the same P, selector,
domain, evaluator, physical success and target. No supplied oracle stands
in for this bridge.
ILLEGAL, UNDEFINED and VALUE are bound to actual V15 observe outcomes.
image_mono follows from gated success monotonicity with all other data fixed.

WitnessIndex retains the raw history, endpoint and support. Different words
or starts remain different witnesses even when their values/supports coincide.
Value images can identify equal values; this does not identify their witnesses.
A fixed resource restriction may already be encoded in P, or in the fixed
base machine. Permission changes do not automatically preserve a different
model with activation overhead, altered costs or an altered evaluator.

## Incidence, relative additions and blockers
PermissionIncidenceV22 defines capability as an eligible witness whose
requirement predicate is contained in the enabled set.
The partial-context bridge above supplies the actual instance of this abstraction.
available_restrict proves the legitimate restriction to supports contained
in the available universe.
blocks_iff_hits derives the hitting condition from absence of a surviving
witness. Only supports contained in currently available S are relevant.
Off-universe paths do not create an extra deletion requirement.

PermissionMinimalityV22.enabling_deficits proves the relative addition law:
baseline S0 lies in U; additions D lie in U minus S0; eligible available
witnesses have support in U; their deficits are support minus S0.
minimal_enabling proves the exact equality between minimal enabling sets
and inclusion-minimal members of that deficit family.
The allowed family is the FULL powerset, not an arbitrary restricted list.
Baseline impossibility is unnecessary for this equivalence. The separate
admitted_baseline theorem proves empty addition is minimal if baseline
already succeeds. A claim of relief additionally needs initial impossibility.

minimal_blocker proves:
Minimal(Blocks at S,B) iff Blocks at S,B AND PrivateWitnesses at S,B.
Every b in B has an eligible currently available support intersecting B
exactly at b. Private witnesses alone are insufficient.
The kernel equivalence holds even without separately assuming B is contained
in S: its minimality/private clauses already exclude ineffective outside
elements. The relative finite API still requires deletions contained in S.
These are inclusion-minimal sets, not minimum cardinality or charged cost.

HistoryPermissionsV22 constructs freely admitted baseline histories plus
one independent permission per absent candidate history.
history_admission and one_history_relief recover the old one-history
relaxation at its generic history-admission scope, retaining history IDs.
It need not be realizable as independent edge permissions on a fixed graph.

## Finite existence and support reduction
FinitePermissionsV22 constructs an actual recursive powerset roster.
choices_sound/complete prove exact coverage of all predicate subsets of
the supplied finite permission list.
candidates filters that roster by the actual property; minimalMembers
applies immutable V20 frontier under reverse inclusion.
minimal_membership proves the roster represents exactly ALL inclusion-minimal
solutions. minimal_below constructs a minimal solution beneath any supplied
solution; finite_enabler and finite_blocker instantiate this result.
The property may quantify over an infinite history family, so its classical
filter is not automatically an effective evaluator or enumeration algorithm.
No finite word cutoff certifies complete enumeration of all target histories.

Lean lists may repeat extensionally equal subset predicates, especially when
the universe list has duplicates. The theorems are membership/set semantics,
not cardinalities of list entries. Python canonical sorting/deduplication
has independent finite evidence, not a claimed general kernel refinement.
SupportFrontierV22 removes strictly dominated supports from a finite history
roster and proves capability/blocker preservation. Equal-support history
aliases are retained in its full frontier. Grouping supports in Python must
retain their original backpointers; it is not preservation of the raw list.

## Controls and explicit boundaries
PermissionControlsV22 binds the concrete same-payload machine and source-state
requirements, then proves different enabled behavior for equal payloads.
It proves nonblocking private-witness examples, the vacuous empty certificate
failure, equal-baseline/different-permission ambiguity, and the admitted baseline.
Actual tail(n)={q:Nat | n≤q} is bound explicitly. General kernel theorems show
no minimal enabling predicate and no minimal blocker for this infinite family.
Thus the infinite-tail counterexample is stronger than paper/finite evidence.
Other named finite controls, including charged-cost versus cardinality and
history-sensitive cycles, remain independent executable/paper evidence.

ConstructorBindingsV22 registers actual sets, gates, context fields, witnesses,
capability, blockers, deficits, powerset recursion and frontier construction.
ProofTargetsV22 supplies three exact independent leaf contracts for source-valid
mutants: gated_success_contract, context_incidence_contract,
minimal_blocker_contract. Replacing them with True must fail typed AUDIT.

Python traversal, strict parsers, canonical outputs and exhaustive-corpus
coverage are not proved correct by Lean; independent tests assess them.
No implication from bounded calibration to unbounded-history completeness,
no advanced enumeration efficiency, no unique causal explanation and no
physical causal identification is asserted. The hypergraph mechanism is
classical; the earned result is its exact machine/partial-context mapping.
R3-008 affine regimes and R3-009 legacy transports are outside this round.
