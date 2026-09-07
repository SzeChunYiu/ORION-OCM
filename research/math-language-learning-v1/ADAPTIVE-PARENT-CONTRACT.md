# Adaptive parent contract

This implements the observed prospective v2.1 selection/cache/parent policies on authored fixtures.
It supplies no task generator, scientific continuation controller, resource enforcement or analysis.

## Public APIs

- `unary_method_selection.contract(32,16)` returns the fixed ASSAY selection contract.
  Smaller counts require explicit `authored=True`; they are labelled AUTHORED, not scientific rows.
- `acquire_selected(training_tasks, development_tasks, contract, observation=...)` physically
  solves/checks every training task, invokes the existing proper-subcover miner once, and measures
  every candidate against fresh development baselines. An exception leaves reached observations
  in the caller-owned observation dictionary. Successful subsets are never silently mined.
- `ParentStore(root, create=True)` creates one conventional library. Existing storage uses
  `ParentStore(root)`; missing initialization or pending admission/use refuses.
- Both ParentStore and MethodStore expose `acquire_selected(...)`. They call the selector internally;
  neither public path accepts a caller-selected rule list or forged utility receipt.
  MethodStore.acquire() remains the older authored route, separate from real selection.
- `ParentRuntime(store).solve(task, invoke=True)` directly dispatches; MethodRuntime uses real OCM.
  invoke=False disables recipes. The exact RegionSolver can bypass all rule/admission machinery.
- `ParentStore.revise(role, state, mid=...)` records LIVE/REVOKED/UNKNOWN role revisions.
  OCM's fixed arm adapter uses existing revoke/reinstate for the declared LIVE/REVOKED interventions.
- `unary_method_process.launch(..., arm="conventional"|"ocm", profile=...)` admits only fixed code modes:
  acquire (legacy OCM), acquire_selected, solve, batch, revise, status.
  The interpreter profile stays launcher configuration, independent of task/rule data.

## Selection and authority

Training engines stay warm per exact ordered predicate registry. Development has fresh engines for
every baseline and candidate/row trial. Ranking uses summed query constraints saved; ties use actual
matching work, inner-rule bytes, then rule_id. Select at most eight positive rules and route by rule_id.
NO_METHOD_ACQUIRED and NO_DEVELOPMENT_BENEFIT record empty selected libraries and permit exact fallback.
This independent-ranking policy is a narrow logical-work heuristic, not a total-cost optimization claim.

The rule's mathematical certificate retains exact type/shape, truth table and essentiality countermodels.
The miner may return additional zero-delta instrumentation keys inherited from its surrounding work
dictionary. Those keys are retained and validated as nonnegative integer counts, independently of
the exact mathematical certificate. Missing partial observations are never manufactured as zero.
Receipt checking validates actual support episode/task identities, semantic grouping, proper cover
and canonical rule correspondence without running mining or an optimized query solve.

Training discovery, measured development eligibility, universal schema correctness, and current answer
checking remain separate. Discovery withdrawal changes attribution. Utility withdrawal disables
selection without falsifying the rule. Schema withdrawal disables dependent recipes while a live,
independent answer checker can accept exact fallback. UNKNOWN liveness is never LIVE.
Reinstatement requires fresh matching/checking; historical accepted uses never become current warrants.

## Conventional custody and shared computation

Parent admission records ADMIT_PREPARE, writes/fsyncs immutable content-addressed payloads, then ADMIT.
One log supplies WAL intent/completion; it is not a second OCM implementation or cross-ledger transaction.
USE_PREPARE precedes lookup/work; USE or USE_REFUSED follows actual independent checking.
A durable-use failure preserves pending state. Cold restore refuses incomplete work instead of
reporting zero prior use. Unreferenced, missing, altered or aliased payload files refuse.

Each conventional public acquire/solve/revise/persist checks its current journal head, every referenced
payload's consumed bytes/hash, and its 34-file declared source/policy closure.
This excludes unrelated OCM/ORION sources and copied plan notes. The broader outer experiment inventory
is separately observed by the launcher. Actual source checking is once per conventional public entry.
Checked method bodies are frozen once, then copied from immutable decoded data for callers; reads do
not parse JSON again. Posting contents survive use-log growth and invalidate on eligibility revision.
The OCM adapter keeps its own stronger field/evidence checks; that extra work remains measurable.

The unchanged generic ledger.py/canonical.py are loaded from fixed repository paths under
_unary_conventional_ledger. Their actual loaded-byte digests are checked against declared inputs.
No caller can change those paths or pass a code body, callback, import root or entrypoint.
The shared computation uses the existing RegionSolver/apply_rule and independent AST/model verifier.

## Observation boundaries

Logical counters retain real key traversal, preparation, binding, indexing, matching, schema checks,
support revalidation, source/payload reads and durable-write bytes at their stated call boundaries.
They do not exhaust Python allocation, hashing/equality, JSON internals, interpreter or kernel work.
Every instrumented internal use/selection validator requires an explicit work accumulator.
The counted answer wrapper increments before the actual independent checker, including failed calls.
Selection revalidation retains actual binding-expression visits; use admission and each cold restore
retain their own answer/binding revalidation work. Packet check work and store/replay work are separate
observations of separate calls, not interchangeable totals or additions to encompassing CPU/wall time.
Legacy public pure validation wrappers may allocate a local dictionary; arm operations call the
required-work internal boundary. The pure semantic verifier API and mathematical fields are unchanged.

solve_wall_s ends before the use journal. return_observation covers the journal and returned call.
A failed use write leaves pre_journal_observation in the arm failure record, explicitly provisional:
it can describe an already checked recipe while the overall operation is unavailable.
It is never a completed durable issuance/use receipt. Reached/unreached batch rows remain distinct.

The subprocess outer_wall_s is its dispatch/wait span, excluding initial/final recorder inventory
and output writing. Nested timings explain encompassing physical costs; they must not be summed.
The external engineering-test process span includes the test suite and its waited children.
The later scientific controller must measure/enforce the full registered process tree and deadline.
-I/-S/-B and imported-origin observations do not establish host containment or a whole-host no-neural claim.
