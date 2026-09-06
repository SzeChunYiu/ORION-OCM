# Opt-in indexed extraction through the runtime

`OCMRuntime.solve` and `runtime.solve.solve` accept the keyword-only
`extraction_index=ExtractionIndex(ks)`. Omitting it retains the incumbent oracle.
This connects the [measured extraction apparatus](INDEXED_EXTRACTION_SERVING_20260906.md)
to the actual runtime; it does not establish end-to-end active-subspace scaling.

## Preserved semantics

A supplied index routes both WARRANTED and EXPLORATORY reaction through the
indexed dense adapter. The exact bounded PCST optimizer remains authoritative;
only its existing greedy fallback uses indexed greedy extraction. Candidate
ordering, warrant checks, revocation, checking, decisions and commitment retain
the incumbent behavior. Fire/enable ordering and their global scans are unchanged.

Snapshot mismatch produces `CANNOT_CHECK` before navigation or backend execution.
The commitment gate refuses. Replaying or structurally replacing a space requires
a new prepared index; evidence revocation alone reuses structural preparation.
The direct extraction-stage API also returns a typed mismatch result.

## Accounting contract

The extraction stage exposes `payload.indexed_extraction` in the solve trace and
persisted EXTRACTION event. It records:

- Separate warranted/exploratory reaction work and greedy work when used.
- Each dense adapter's N seed reads, global prize materialization and optimizer
  seed scan, plus the unchanged exact optimizer's global universe scan/subsets.
- Caller-owned preparation as context, with `charged_in_query: false`.
- Full-field surprise calls, whose internal work is explicitly not instrumented.

The lifetime harness must construct the index once and charge `index.build_work`
once. A repeated query does not re-charge that construction. Build context in
multiple trace rows is not multiple compilation work. Navigation, surprise,
exact bounded optimization, firing and persistent logging still need broader
cost measurement; this integration makes no complete-runtime locality claim.

```python
index = ExtractionIndex(runtime.state.ks)
compile_work = dict(index.build_work)  # charge once in the caller's experiment
outcome = runtime.solve(task, operators, extraction_index=index)
```

## Verification boundary

71 focused tests pass across the new runtime call-path tests and inherited solve,
runtime, lifecycle/replay, event-reducer, surprise and operator-index controls.
The 12 new cases cover both extraction strategies, complete semantic-trace parity,
revocation/reinstatement, persisted accounting, a hostile forbidding incumbent
reaction/greedy execution, stale-snapshot refusal, restart/rebind and direct-stage
refusal. Engineering source-bound qualification follows after integrated source
is frozen; the previous apparatus measurement remains historical evidence.
