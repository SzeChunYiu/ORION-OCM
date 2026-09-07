# Adaptive unary parent implementation plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** add a matched adaptive conventional parent and the minimal shared selection/cache seams.
**Architecture:** shared mechanical computation; separate conventional versus OCM admission and dispatch.
**Tech Stack:** existing Python 3.11.14, stdlib, LedgerStore, pytest; no new runtime dependency.

All paths below are relative to the inspected assay worktree. Keep each authored module at most 200 lines.
Implement only after root assigns ownership. No source change or test execution belongs to this plan.

## 1. Share proposal computation and independent use checking

Create `research/math-language-learning-v1/unary_method_execution.py`.
Extract runtime.py:40–73 proposal work into:
`propose(task, *, lookup, index, engine, invoke, observation)`.
The caller authenticates request bytes and binds its issued packet; the shared routine performs
one prepare, actual indexed candidate visits, structural matching, and complete only on fallback.
Extract check.py:43–74 into `verify_use(task, use, lookup, *, current, work)`.
Keep independent `unary_verify.verify_result`; the verifier never calls RegionSolver.solve/complete.
Retain OCM request/warrant checks in `unary_method_check.py`; conventional code checks its own
exact request, library/source revisions, dependency roles, and issued packet before the shared checks.
Extract the small pure kind-postings builder from `unary_method_index.py`; retain each adapter's
own staleness token and explicit actual lookup/posting/match counters.

Modify `unary_method_runtime.py` to keep engines keyed by exact ordered predicate registry.
A new conventional runtime uses the same engine cache policy and proposal function.
prepare() already preserves mask cache (solver.py:125–136); do not change unary_solver.py.
Re-prepare each exact task; prepared identity remains engine-local/latest/task-bound.
Capture query counter deltas before the next prepare resets counters; do not re-charge historical work.
Cache immutable kind-posting contents under the same library/eligibility revision policy in both arms.
Per-request index guards still bind the current state after USE_PREPARE; a new use-log head alone
need not rebuild unchanged posting contents. Record actual builds, validations, hits and candidates.
Invalidate on source/library/correctness/selection revision; no stale eligibility reuse.
Conventional custody need not scan unrelated KSO state merely to emulate OCM overhead.

## 2. Replace authored selection in the assay path

Create `research/math-language-learning-v1/unary_method_selection.py`:
`acquire_selected(training, development, selection_contract, *, work)`.
It physically solves/checks all training tasks in arm A, then invokes existing acquire() once
on the ordered strict {task,result} list; do not accept a successful subset of 32 assay rows.
It implements the observed prospective v2 selection contract, with its exact version/hash bound.
It never accepts manually injected rule data, a final-task oracle key, or a fabricated selected list.
Verify training results, distinct semantic supports, rule certificates, and development results.
For each of 16 development ASTs, measure a fresh baseline engine: prepare, snapshot, complete,
snapshot, independently verify. Score only the complete delta of constraints_checked.
For each candidate in rule_id order and each row, use a fresh engine: prepare, snapshot,
apply_rule, complete only on no-match/inconsistent base, then independently verify.
Benefit is the sum of baseline minus candidate post-prepare constraints_checked deltas.
Tie work is the sum of matching_nodes + mapping_attempts + premise_index_reads + index_probes.
Rank positive rules by (-benefit, tie work, canonical inner bytes, rule_id); select at most eight.
Route selected rules by rule_id; library digest hashes their canonical inner-rule array in that order.
Retain all preparation/schema/binding/wall/verification work and candidate failures outside that score.
An invalid/refused candidate trial invalidates selection; do not delete it and continue to promotion.
Empty pool is NO_METHOD_ACQUIRED; no positive rule is NO_DEVELOPMENT_BENEFIT.
This is the specified independent-ranking parent, not an unimplemented greedy optimizer.
Output discovery receipt, candidate-pool digest, development receipt, selected ordered rules,
routing-policy digest, selected-library digest, and measured work. Strictly refuse absent/unknown policy.
An empty selected library is valid when the frozen selector yields none; exact fallback remains usable.

Add `MethodStore.acquire_selected(training, development, selection_contract)` and the same parent API.
Both call that adapter internally, then admit only its selected checked rules.
Refactor the current store admission loop; preserve legacy acquire() solely for historical authored use.
The new selection evidence body binds actual development contract/input/receipt/library identities;
it cannot use authored-selected.v1. Admission and restore validate that body separately from correctness.
Compare arm A pool/library/decision digests, not timing/path fields in physically different receipts.
A disagreement is an assay integrity failure; do not substitute one arm's output into the other.

## 3. Conventional persistence and direct dispatch

Create `unary_parent_store.py`, `unary_parent_journal.py`, and `unary_parent_runtime.py`
under the learning package. The store exposes method_ids, read(mid), acquire_selected(), and revise().
Use canonical content-addressed payloads and one existing LedgerStore log with checked batch admission.
Require existing storage on restore; LedgerStore's constructor must not silently create missing history.
Validate chain/CAS, exact sources, inner schema proof, selected membership, and role dependencies.
Use plain dependency states for this fixed conjunctive fragment; do not implement a second general warrant algebra.
Discovery, development selection, schema correctness, and answer checking are separate role records.
Discovery withdrawal preserves independently checked validity; selection withdrawal disables selection.
Schema UNKNOWN/revoked disables rule reuse; semantics/answer-checker unavailable refuses checked answers.
Exact fallback survives method-only withdrawal while its own required roles remain LIVE.
Reinstatement changes an explicit recorded role revision and revalidates dependencies.

ParentRuntime.solve(task, invoke=True) uses the shared proposal/check routine directly.
EXACT_PARENT instead runs the same warm engine prepare/complete plus independent verify_result,
without a learned store/index/acquisition. OCM_KNOCKOUT retains OCM infrastructure with recipes disabled.
Record USE_PREPARE before lookup/work and USE or USE_REFUSED afterward, with exact request/result binding.
Pending admission/use on restart refuses explicitly; do not infer no work or reacquire missing state.
The conventional log may admit one batch atomically; do not impose OCM's two-ledger failure surface.
Historical checked uses remain historical after revision; current eligibility is recomputed separately.

## 4. Fixed portable A/B/C process entry

Extend `unary_method_process.py` and `unary_method_episode.py` with a strict trusted launcher arm enum
and a bounded batch mode; keep task/method data unable to select entrypoints, imports, or callbacks.
Use branch-local runtime imports so the parent does not instantiate OCMRuntime.
Reuse `unary_method_profile.py` exact executable/hash/version/flags validation at parent and child.
A acquires/selects/persists; B cold-restores then holds one runtime for its ordered query batch;
C starts from a copy of A for task interventions; separately audit cold recovery of B's use history.
Role withdrawal/reinstatement use separate A copies and fresh mutation/solve process lifetimes,
as fixed by EXECUTION.md. Authored controls demonstrate these operations without scientific rows.
No B/C training payload or implicit mining, solving during restore, or inherited Python cache.
Extend `unary_method_data.py` source enumeration to all new actual dependencies; report imported origins.
A shared outer source envelope may bind both arms; distinguish actual loaded closure and hashing work.
Keep fixed bootstrap roots and launcher failure/raw/cleanup custody; -I/-S is not host containment.

Implement new `test_unary_parent_{selection,store,runtime,process}.py` and
`test_unary_method_shared_execution.py`; detailed required controls and commands are in [CONTROLS.md](plan-CONTROLS.md).
No core runtime, semantic solver, old sealed archive, CI, generator, or scientific schedule changes are required.
