# Decision/lifecycle contract completion, v1

**Terminal: FINITE_TABLE_CONTROLS_PASS.** This is a bounded contribution to #145,
#152 and the existing #165 programme, not completion of ORION-OCM.

## What is added

`FOUNDATION.md` states ten scoped propositions with proofs and limits, connecting
nonempty decision sufficiency, ordered lifecycle bisimulation, finite metareasoning,
self-extension, support semantics, conservative learned macros, lifetime costs,
bounded failure and external admission. P1-P5 have executable finite controls;
P6-P10 are derivations/integration obligations, not new runtime implementations.

`contracts.py` adds a strict finite-table checker, counterexample witnesses,
coarsest-partition refinement, source/model/checker-bound reproducibility receipts,
a nonempty common-action guard and an adapter to the existing exact decision DP.
It preserves STOP, action ordering, exact protected observations, nonnegative
rational additive costs, and successor-block probabilities. No second OCM runtime
or metareasoning solver is introduced.

Three source-bound counterexamples clarify why the stronger contract is needed:
empty version containment returns all region actions in the parent; action-only
bisimulation does not cover differing STOP costs; equal values with reordered tied
actions do not preserve selected action identity. The latter two are limitations
of the parent's explicitly narrower contract, not alleged implementation errors.

## Source custody and validation

Base reviewed: `4c5d3ec35cfa694572b968b4a85bd03321b0cf8d`.
Unchanged parent: `../decision-core-successor-repair-v1/decision_core.py`, Git blob
`4b32940e1a10705001ea0540f20c5067e578a348` (12,540 bytes). Tests verify this identity
before importing it. Earlier capsules and their receipts are not rewritten.

Local Linux CPython 3.13.5: **28/28 authored tests pass normally and with `python -O`,
zero failures, errors or skips**. Each run enumerates **1,728 exposed three-state
models and 8,640 partitions: 2,556 accepted, 6,084 rejected**, agrees with a separate
all-pairs oracle, compares the coarsest relation with bounded deterministic traces,
and checks existing-DP values/policies through horizons 0..4. Additional controls
cover rational stochastic kernels, STOP ties, revocation, modeled restart events,
operator/projection/constitution changes, malformed input and receipt mutation.

Results are in `evidence/normal/validation.json`, `evidence/optimized/validation.json`
and their raw `tests.txt` logs. Source hashes were unchanged across both runs.
The source subset was obtained through the GitHub connector and the parent's Git
blob hash verified locally; this was not a full repository clone or full-suite run.
The initial development run had 26 passing tests; two additional controls and
strict dictionary-key validation were added before the recorded 28-test runs.

From repository root:

```sh
python research/decision-lifecycle-contract-v1/run_validation.py --out /tmp/ocm-contract-normal
python -O research/decision-lifecycle-contract-v1/run_validation.py --out /tmp/ocm-contract-optimized
```

Only Python's standard library is required. A parent source mismatch fails closed.
No hidden benchmark, external service, learned router or foundation model is called.

## What this does not establish

These are self-authored engineering/finite-enumeration results, not independent
review or protected replication. The proofs are not checked by Lean or another
proof kernel. A valid table receipt does not prove model adequacy, extraction
completeness, real restart equivalence, crash safety, runtime cost accuracy, useful
learning, minimal architecture, causal G2 reuse, general intelligence, or physical
speedup. A receipt is not an authority token. Production code is unchanged.

`GAP_MAP.json` keeps the broader gaps open and identifies required evidence and
current ownership. The exposed negatives #189/#191 are preserved. During this review #192 merged
a reported bounded macro-reuse positive, tied by ordinary persistence and without
full-cost payback at its horizon. That result is credited, not duplicated or
promoted to whole-programme closure. This contribution does not unlock #71/#46. M11/M12
protected scientific qualification is not renewed. The next technical step for
this contract is a source-bound production lifecycle extractor and differential
restart/revocation validation, not a claim that writing this theory completes OCM.

Integration base rechecked before publication: `0cd4f4c541491a386677ffd91a97c83d49562dc0`.
The parent decision helper still has exactly the pinned blob above at that commit.
Local validation remains scoped to the recorded source subset, not this entire tree.
