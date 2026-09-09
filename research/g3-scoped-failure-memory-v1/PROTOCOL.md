# G3.2 checked failure-point memory — prospective authored development v1

## Registered question and parent boundary

Do counterexamples actually encountered by the existing polynomial synthesizer
produce reusable, scoped failure-point records that save repeated interpreter
work on later mathematical tasks, survive a real process restart, and lose exactly
that effect after production evidence withdrawal? This is **ordinary checked
memoization / counterexample reuse**, not a novel OCM algorithm, general failure
learning, or the complete G3.2 gate. The equally equipped conventional parent gets
identical records, checking, lookup, and solver. A tie is PARENT_SUFFICIENT for the
mechanism. No weaker-parent victory becomes architectural superiority.

The unchanged source-pinned `ocm.learning.methods.solve` remains the search and
verification implementation. A single-threaded research adapter temporarily
replaces only its point interpreter call within a `try/finally`, restoring it on
all exits. It either returns the unchanged interpreter result or a previously
independently checked identical result. No task blacklist, search reorder, new
cognitive core, model, ranker, learned policy, or altered native source.

Review roles applied by one author: formal-semantics review of pruning soundness;
implementation review of source/data/liveness boundaries; causal-design review of
matched parents and withdrawals; resource review of cold costs and nested timers.
These are not independent experts or protected replication.

## Allocation frozen before new study outcomes

Canonical mathematical identities are enumerated from the existing four-primitive
language up to length 5; minimum length defines the strata. Sort each stratum by
SHA-256(salt + NUL + task fingerprint), with fingerprint tie-break. Training: eight
minimum-length-4 tasks, salt `ocm-g3-failure-training-v1-20260909`. Test: sixteen
minimum-length-5 tasks, salt `ocm-g3-failure-test-v1-20260909`. All tasks have budget
2,000 search slots and maximum program length 5. No overlap or task-label novelty;
no replacement on failure. Population construction is prior computation and its
cost is reported separately. This is a small authored polynomial distribution,
not independent semantic families or language/formal-proof transfer.

Training calls the actual interpreter. Retain every mismatch observed at a queried
integer x, with exact program, mathematical task fingerprint and coefficients,
point, computed value, target value, declared budget, domain, environment version,
interpreter source identity, and outcome. Also retain each final search outcome.
BUDGET_EXHAUSTED and other incomplete outcomes cannot create failure certificates.

The reusable subset is the **first 64 distinct (program, x) mismatches**, in the
frozen training/search order. No utility tournament, test-aware selection, or
post-exposure cap change. A record is accepted only after the separate symbolic
coefficient evaluator independently proves p(x)=v and target(x)!=v. Raw failed
attempts are retained even when no new record is selected. Final training answers
are not supplied to the test worker. Existing domain primitives are prior inputs.

## Scope, reopening, and constitutional binding

The learned record says only `this exact program evaluated to v at x under the
registered engine/domain/environment`. It does NOT say the program always fails,
that a task has no solution, or that a larger budget is useless. New tasks use the
record only at that same program/point and only with exact context/budget identity.
A changed environment, domain, source or budget makes the index inapplicable and
falls back to actual execution. A matching target value does not blacklist a
candidate; it proceeds through the original exact checker and can succeed.

All failures are retained outside the solver in an immutable acquisition archive.
The selected records are admitted as one warranted, content-bound procedure/data
object under the existing OCM evidence registry and support edge. An ordinary
parent stores the identical records atomically. Fresh OS processes reconstruct
each consumer; neither gets training answers or the allocation oracle. The OCM
root is the same root across live, evidence-revoked, and reinstated stages. Actual
`OCMRuntime.revoke` and `reinstate` change support, not a renamed eligibility flag.
A new stage must reconstruct from its persisted ledger. This is one within-study
lineage; it does not retroactively join missing historical #192/#193 ledgers or
discharge programme-wide H / G6 generations.

## Arms and measurement

Fixed order: primitive/no-memory; ordinary checked memory; OCM live memory;
OCM evidence-revoked; OCM reinstated. No online test updates in any arm. Every row
retains exact original result fields, point-call count, actual interpreter calls
and primitive steps, cache lookups and hits, accepted certificate IDs, index
construction/rechecking counts, solve wall, and solve CPU. Each worker separately
reports load/build/verification wall and CPU, worker-body wall/CPU (excluding startup/imports), peak RSS and input
bytes. The parent separately observes the entire child wall and user/system CPU,
including startup and imports. Producer/controller reports allocation, acquisition, certificate checking,
admission, withdrawal/restoration, persistence, bytes and process launch costs.
Nested phases are never summed into their enclosing physical measurement. RSS is
not additive. Fixed arm order and one run do not establish unbiased wall speedup,
energy benefit or protected statistics. A lower logical step count is not physical
or lifetime payback. Engineering/test attempts are not amortized away.

Required controls before study: exact result parity with the unchanged solver over
small finite task/budget grids; mismatching records rejected; UNKNOWN cannot prune;
source/environment/domain/budget mismatch falls back; task relabeling does not alter
lookup; prior failure cannot suppress a correct candidate for another task;
revocation and restoration survive fresh-process reload; ordinary and OCM records
and selected results match; missing/duplicate/truncated arms fail reconciliation.

## Interpretation (no retuning exposed v1)

All exact results must equal primitive and ordinary task-by-task. Actual-use and
strict repeated-execution savings in live/restored arms with revoked=primitive
supports `FAILURE_POINT_MEMORY_USEFUL_AT_SCOPE`. No saving is
`FAILURE_MEMORY_NOT_USEFUL_AT_SCOPE`; source or result disagreement is
`CANNOT_CHECK_REFINEMENT_OR_LIFECYCLE`. Ordinary parity is explicitly
`PARENT_SUFFICIENT_FOR_FAILURE_POINT_MECHANISM`. Even a positive does not close the
broader G3.2 requirement to compare richer TMS/nogood/CEGAR/CBR mechanisms or prove
whole-lifetime benefit. Negative results, failures and harmful physical outcomes
are retained. Code/control fixes before study are engineering, not new research
replicates; after exposure the source/results stay frozen.

## Conditional argument

For deterministic total interpreter E in context c, validation establishes
E(p,x,c)=v. Substituting v for a later identical call is extensionally identical.
The unchanged solver therefore sees the same point values in the same order;
induction over its iterations preserves first solution, status, counterexamples
and slot counts. This depends on complete context/source binding, immutable checked
values and exact lookup equality. It does not preserve execution costs: it trades
interpretation for validation, lookup, storage and lifecycle work. Revoking the
only support disables the substitution and reverts the exact baseline call path.
No inference about impossibility follows from resource exhaustion.

Parents: de Kleer, An Assumption-based TMS (1986),
https://doi.org/10.1016/0004-3702(86)90080-9 ; Clarke et al., Counterexample-Guided
Abstraction Refinement, https://doi.org/10.1184/R1/6604547 . This experiment uses
checked point memoization, not a faithful implementation of all those algorithms.
Strong acquisition parents for the later economics lane: Stitch,
https://arxiv.org/abs/2211.16605 ; DreamCoder,
https://arxiv.org/abs/2006.08381 . Their reported compression/learning results do not
supply OCM-specific causal, physical, or lifetime evidence.
