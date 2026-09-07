# Checked unary method persistence and actual OCM invocation

> **For Codex:** use the executing-plans skill to execute this bounded plan.

**Goal:** make mechanically acquired checked rule data survive a real process restart
and construct an independently verified answer inside `OCMRuntime.solve`.
**Architecture:** existing learner and exact prepared parent; strict rule envelope in
KSO; one generic registered dispatcher and an explicit solve adapter; a small process
entry point. Discovery, utility selection and correctness retain separate identities.
**Tech stack:** existing Python 3.11 standard library and OCM, pytest on billy-laptop.

This is an engineering qualification with authored controls. The registered four-arm
scientific assay, dataset generation, performance conclusions and paper writing follow
only after this seam works. No new ontology, core runtime rewrite or neural component.

## Ownership and starting state

One code writer owns new `research/math-language-learning-v1/unary_method_*.py`,
their authored tests and this tranche's contract/qualification note. Another reviewer
reads the frozen implementation. Evidence/CI packaging is a separate file owner.
Do not change prepared solver/miner/matcher without a reproduced defect and notice.
Start a new laptop worktree at the reviewed learning-tranche commit. Record its exact
parent and use `git rebase --onto` after its parent release, never replay merged ancestry.
Do not edit the live ORION checkout or run tests/worktrees on the Mac.

Read the accepted first-tranche API and the read-only runtime map at
`/home/billy/orion-director-work/20260907/math-language-runtime-seam-v1/MAP.md`.
The two OperatorSpec types have different callback signatures. A registered method
alone is not evidence that `runtime.solve` invoked it.

## 1. Strict persisted data and actual checking

Create `unary_method_store.py` and focused `test_unary_method_store.py`.
Expose small functions for checked admission, exact-ID lookup and cold index build;
define the exact payload schema before implementing them. Use canonical JSON text
in Atom.meta and hash the entire envelope into content_ref. Persist only plain rule
data, schema certificate and explicit source/evidence identities, never callbacks.

Run the independent rule checker before proof admission and after restore. A proof
channel label or matching digest is not a mathematical checker. Bind the supplied
schema/semantic assumptions and actual checker source identity, with a derived proof
warrant obtained from the evidence record. Admit a quarantined proof anchor plus
connected procedure through the existing ordered atomic batch.

Keep discovery and utility receipts out of the rule's mathematical warrant. Record
selected-policy eligibility separately: withdrawing discovery preserves independently
proved correctness; withdrawing selected utility disables that selection policy.
Revoking correctness assumptions disables method use. Reinstatement permits a fresh
check and match; it does not make an old answer current.

Author controls for valid admit/restore, malformed envelope, wrong content hash,
invalid schema proof, changed source identity and each separate revocation route.
An unavailable check must produce an explicit refusal, not successful empty retrieval.

## 2. Exact rule retrieval and selection

Use an index built from the selected admitted rule IDs, with conclusion quantifier
kind as the first exact key. Stable rule-ID ordering suffices; no learned ranker yet.
Record cold entries visited, decoded/checked rules, bytes, postings, probes, candidate
attempts and every refusal. Any cached index binds the current immutable field and
revocation/selection state. Rebuild or refuse stale indexes; do not trust stale liveness.
Lookup current atoms through atom_view. A miss only selects exact fallback.

Do not hide existing whole-field replay/admission/revision/navigation cost. This tiny
index is a method-data index inside one dispatcher, not core million-operator scaling.

## 3. The real solve bridge

Create `unary_method_runtime.py` and `test_unary_method_runtime.py`.
Admit a strict request atom containing task AST/digest and conditional premise support.
Register one fixed programmatic backend; bridge it to the solve OperatorSpec with the
current input atoms and exact scope/context. Use actual `runtime.solve` and require
`SV.committed`. Reuse the core callback purity guard; do not duplicate full-state hashes.

Inside that invoked backend: prepare premises once, retrieve live candidate rules,
try the existing matcher/recipe, and independently verify a proposal. If no usable
rule exists, complete the same prepared parent. Do not solve the query beforehand.
Record the original request digest, actual rule ID, actual support indices/bindings,
replaced branch, candidate attempts, proposal result and final verifier decision.
Preparation is charged once; complete returns invocation deltas; inspection binding
work remains cumulative and still traverses full prepared data.

The checker closes over the original admitted request. Check current rule eligibility
and claimed support binding as well as `verify_result(expected_task, result)`.
Malformed or unavailable checking returns an explicit refusal mapped to CANNOT_CHECK.
UNKNOWN and INCONSISTENT are semantic statuses that may have valid checked results.
Never turn a correct fallback or a reported method ID into a method-use claim.

## 4. Durable use record and real A/B process boundary

Create `unary_method_episode.py` and `test_unary_method_restart.py`.
Process A accepts authored training episodes, invokes the actual miner, independently
checks/admit selected acquired rules, and persists. The parent waits for A to exit.
Process B cold-starts, restores the actual ledger and builds its index, then calls
the real runtime adapter on fresh authored tasks. Use new PID and empty interpreter
state; reconstruct no learned rule from fixture code in B. Only sealed plain data and
the generic implementation may cross the boundary. An empty learned set stays empty.

Journal the checked answer/use packet explicitly after committed solve; the runtime
stage trace alone does not retain it. Use an existing public ledger/event API or a
small explicit append-only sidecar, without reaching into private state unsafely.
Record process exit, runtime trace and packet linkage; persist/fsync work is charged.
Keep launch environment/source/import observations for later closure qualification.
Engineering subprocess tests are not evidence of no-network host containment.

## 5. Causal and semantic authored controls

Use authored training fixtures only for software qualification; label their origin.
Require a mechanically acquired rule to be invoked after restart on a fresh Boolean
substitution and a fresh context. Verify both results independently. Then use the
same stored data with invocation disabled: all answers remain checked, recipe count0.
Make parent completion raise in the positive recipe control to detect hidden solves.

Remove an actually used premise, re-admit the changed request and require that exact
old support binding to disappear. Allow and record valid alternate matches. Restore
the premise and require fresh binding/checking. Test rule-data tamper, wrong request,
stale index, checker/utility/discovery revocation and an inconsistent premise set.
Include a no-match fallback and a valid UNKNOWN two-model response.

## 6. Qualification and bounded handoff

Record targeted failing cases, their repairs, exact before/after source bytes,
commands, raw output, XML and outer process cost. Use a new external --basetemp each
invocation. Once fixes pass, run one combined unary/learning/runtime test scope.
Run existing relevant runtime checks only if core behavior is changed or a concrete
unresolved concern requires them. No broad unrelated corpus reruns.

Keep source files and docs modular. Review the actual frozen files; fix verified
defects, retain raw failures, commit owned files. Report only authored capability and
limitations. The next separate task is the equally adaptive conventional store and
frozen scientific generator, followed by actual closure qualification and the assay.

## Approved interpreter-profile successor

The runtime review required an explicit launcher-only Python profile for portable
engineering tests. Keep the previous exact laptop identity as default; validate
resolved executable, SHA256 and Python 3.11.14 independently in parent and child.
Tests supply an observation of their actual interpreter, not a task/method field.
Do not accept entrypoint, import-root, callback or arbitrary environment overrides.
Preserve the completed 206-control generation; use a separate profile evidence root
for targeted RED/GREEN and the final combined suite. Set PYTHONDONTWRITEBYTECODE=1
in the enclosing test command on a clean checkout. No host containment or scientific
qualification follows from this profile observation.
