# First-tranche API and claim boundary

## Modules

| Module | Public entry | Contract |
|---|---|---|
| Parent unary_solver | RegionSolver.prepare(task) | Immutable issuer-bound Prepared; premises only |
| Parent unary_solver | inspect_prepared(prepared, task=None) | Validate exact active object/content/task binding |
| Parent unary_solver | complete(prepared) | Exact result using the compiled aggregate |
| Parent unary_solver | result_from_certificates(prepared, yes, no) | Proposal assembly; requires independent verification |
| unary_rule_contract | seal_rule(parameters, premises, conclusion) | Detached versioned data and content ID |
| unary_rule_check | check_rule(rule) | Independent pointwise validity and premise-essentiality check |
| unary_rule_identity | semantic_key(training_task, work) | Complete finite-world semantics modulo renaming |
| unary_rule_identity | canonical_rule(fragment, work) | Structural alpha normalization and content identity |
| unary_rule_acquire | acquire(episodes) | Mine repeated essential proper subcovers |
| unary_rule_apply | apply_rule(rule, task, engine, prepared) | Structural substitution and certificate proposal |

The parent solve(task) API and unary-result.v1 certificate/counter keys remain intact.
Malformed or unsupported direct learning inputs raise InputRefused. A logical invalid
schema returns accepted=false with its counterassignment; redundant valid schemas return
NON_ESSENTIAL_PREMISE. Unmatched application returns NO_MATCH. An inconsistent base returns
INCONSISTENT_BASE without applying a recipe. A matching application returns PROPOSED.

## Registered fragment

Rule data contains exactly schema, parameters, premises, conclusion, recipe and rule_id.
The schema is ocm.unary-rule.v1; recipe is universal-cover.v1. One to three sequential
parameters P0... occur in two or three universal every/no premises and one universal
conclusion. Boolean expression nodes use the unchanged unary AST. The SHA256 rule ID
binds canonical JSON content; content identity itself is no admission authority.

The checker enumerates all 2^n point assignments directly from the AST. Their conjunction
proves the universal implication for arbitrary Boolean-expression substitution, including
overlapping or equal parameter extensions. A separate deleted-premise counterassignment
for every premise proves that this is an essential composite within this fragment.
Discovery evidence and the current mathematical warrant are distinct.

The miner accepts at most 32 checked training episodes, each with at most three predicates.
It considers a checked query-branch unsat certificate only when the unsatisfied obligation
is that branch's added existential. It enumerates size-two/three subsets of the recorded
universal cover, strictly smaller than the full premise context. All attempted subsets
and their rejection reasons remain in the returned record. It does not inject a target
rule, choose held-out tasks or expose evaluator fingerprints.

Each support fingerprint comprises the premise-model set and premise-plus-query model
set, minimized over all predicate renamings within its complete registered vocabulary.
For three predicates there are eight point regions and **255 nonempty occupied-region
worlds**. All are included, including the all-true region. Predicate emptiness is allowed.
This training-only construction is charged equally to both prospective adaptive arms.
Equivalent contexts and pure renamings count once; at least two distinct groups are required.

## Prepared state and application

Prepared stores immutable tuples and task bytes, premise masks, allowed regions,
universal indices, existential obligations, a base certificate and premise-work counters.
The query's syntax is bound in the task bytes, but no query mask or answer is prepared.
Only the engine's most recently issued object can be reused. Copy, foreign engine,
stale issuance, changed task and content mutation refuse. This is a trusted in-process
object/data boundary; it is not containment against arbitrary Python code.

Completion does not aggregate the premises again. A universal query can invalidate
existing witnesses, so its branch checks the prepared existential obligations.
An existential query adds one witness to the consistent prepared model; different
existentials need not share a witness. Both adaptive arms must receive this exact parent.

The application matcher indexes task premises by quantifier kind, then enumerates
injective mappings for one supplied rule. Predicate parameters match entire Boolean
expressions; repeated parameters require exact structural equality. The returned cover
contains actual task premise indices. Removing a used premise invalidates the old task
binding; a fresh legitimate alternate mapping may still apply.

A proposal must pass unary_verify.verify_result against the original task before admission.
No parent complete/solve call supplies a hidden query answer during recipe application.
The matcher is not yet a registry or OCM operator selector.

## Work accounting

The existing parent's logical counter names retain their meaning. Each prepare starts
one accounting scope. Engine counters accumulate the actual semantic operations within
that scope; complete returns only its call's deltas. Certificate assembly reports zero
parent-semantic work. solve explicitly reports its one preparation plus completion.
Reading or reusing Prepared never resets counters to its historical snapshot.

Binding work is cumulative within the same preparation scope: checked nodes, prepared
hash bytes, bytes submitted to decoding, JSON parse/encode calls, task-validation calls
and task-digest calls are explicit. Each inspect still traverses and hashes the full
prepared payload, decodes the task and validates the full task. Avoiding repeated
semantic aggregation is not avoiding full-state work. Callers must retain these
cumulative counters or compute before/after deltas without charging earlier work again.
The stateless module solve also performs its existing initial validation outside the
engine scope; full-call costs remain necessary. Learning records actual
key traversal/encoded bytes, hashing bytes, schema point/AST/statement visits, deletion
index tests, all finite-world visits/lookups, canonicalization visits, subset enumeration,
matching visits, kind-index reads/probes, binding attempts and applied recipes.
Schema check receipts report that call's deltas while a supplied work dictionary
accumulates all calls. The independent result verifier is counted as calls during mining;
its internal operations are not relabeled as pointwise schema work.

These logical counts and binding call/input counts do not measure Python allocation, sorting/comparison internals, tuple
hash/equality internals, task validation/serialization or whole process costs. Full wall,
CPU, storage, retrieval, verification and revision accounting belongs in the subsequent
source-bound assay. No sparse-execution or end-to-end savings inference follows from
cache hits, short covers, matching counters or the authored qualification.

## Next seam

Persist only checked data with an explicit issuer journal and separate support kinds;
restore in a fresh OS process; register one generic OCM method dispatcher with actual
internal rule-selection telemetry; run the same adaptive learning/persistence/revision
mechanism in the conventional parent. Then register paired fresh tasks and used-support
interventions before any causal-use evaluation. None of these steps is implemented here.
