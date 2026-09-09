# G3 remaining — source-bound real failure/probe incidents v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165).

**Claim authority:** recover a planted source-bound probe incident from the
production ledger after OS-process restart or a new solve episode. Not a G3
programme-wide close.

This capsule may support:

```text
PARENT_SUFFICIENT_AT_SCOPE
SOURCE_BOUND_FAILURE_RECOVERY_SUPPORTED_AT_SCOPE
SOURCE_BOUND_FAILURE_NOT_RECOVERED
CANNOT_CHECK_<reason>
```

`PARENT_SUFFICIENT` is not programme failure. If the production evidence
registry + hash-chained ledger already stores and replays incidents keyed by
`evidence_id` / `source`, the honest terminal is `PARENT_SUFFICIENT_AT_SCOPE`.

Timeout / resource-wall is `RESOURCE_BOUND`. Timeout does **not** license
`JUMP`.

## What is being asked

G3.2 retained failed continuations keyed by **remaining residual state**, not
task ids (`FAILURE_MEMORY_USEFUL_AT_SCOPE` on remaining-gates). G3.3 selected a
representation language (`PARENT_SUFFICIENT` then v2
`REPRESENTATION_CHANGE_CAUSALLY_USEFUL`). G3.4 diagnosed representation
insufficiency (`REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE`).

A remaining G3/G6.1 obligation is different:

```text
recover source-bound real failure/probe incidents
```

The incident must be a **specific evidence/source identity** whose failure is
recoverable from the ledger, not from a task-id cache.

## Frozen predecessors (do not overwrite)

| Capsule | Terminal on this head | Role here |
|---|---|---|
| `research/g3-failure-memory-v1/` | `FAILURE_MEMORY_USEFUL_AT_SCOPE` | remaining-state skip keys |
| `research/g3-representation-v1/` | v1 `PARENT_SUFFICIENT`; v2 `REPRESENTATION_CHANGE_CAUSALLY_USEFUL` | representation, not source incidents |
| `research/g3-representation-diagnosis-v1/` | `REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE` | timeout ≠ JUMP |

A competing ecology `research/g3-scoped-failure-memory-v1` may exist on other
branches with `FAILURE_MEMORY_NOT_USEFUL`. This capsule must not create or
overwrite that directory, and must not retune remaining-gates G3.2.

## Planted probe

Registered grammar `{inc, dec, double, square}` from production
`src/ocm/learning/methods.py` (blob `50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`).

Independent checker fact, not a timeout:

```text
remaining polynomial 1+x  (coefficients 1,1)
invert last operator = square
degree 1 is odd ⇒ not a polynomial square
METHOD_FAILURE / INVERT_IMPOSSIBLE
```

Two sources admit the same remaining-polynomial failure under **different**
source URIs. Task ids are lineage only.

| Incident | Source | Task lineage | Remaining | Method |
|---|---|---|---|---|
| A | `probe://source-A` | `task-alpha` | `1,1` | square |
| B | `probe://source-B` | `task-alpha` | `1,1` | square |

Episode 2 after restart uses a **new** task id `task-beta` against source A.

A separate timeout-only probe is classified `RESOURCE_BOUND`. A planted mutant
that maps timeout → `JUMP` is recorded as an overclaim, not adopted.

## Required demonstrations

1. The incident skip/lookup key is `source` + `evidence_id`, not `task_id`.
2. After a **separate OS process** reloads the persisted ledger, the same
   source-bound failure is recovered. A new solve episode with a different
   task id still uses the live incident (skips repeating that source's probe).
   After revocation of source A's evidence, the recovered record is dead and
   must **not** be used.
3. Parent comparison:

| Parent | Predicted behaviour |
|---|---|
| task-id memory | known-negative from G3.2: lookup(`task-beta`) misses; lookup(`task-alpha`) conflates A and B |
| remaining-state memory (G3.2 v1) | useful at remaining-state scope; lookup(`1,1`) returns both sources and cannot answer by source identity |
| representation-change v1/v2 | frozen terminals; no source-bound incident store |

Ordinary JSON with the same source keys is expected to **tie** the production
ledger on source lookup. That is additional parent sufficiency, not an OCM
residual.

## Valid terminals

```text
PARENT_SUFFICIENT_AT_SCOPE
SOURCE_BOUND_FAILURE_RECOVERY_SUPPORTED_AT_SCOPE
SOURCE_BOUND_FAILURE_NOT_RECOVERED
CANNOT_CHECK_<reason>
```

Do not emit `FAILURE_MEMORY_USEFUL_AT_SCOPE` (that is G3.2 remaining-state).
Do not emit `JUMP`. Do not claim G3 programme-wide close.

## Run

```sh
python3 -B -m unittest discover -s research/g3-real-failure-v1 -p 'test_*.py' -v
python3 -B research/g3-real-failure-v1/experiment.py --out research/g3-real-failure-v1/RESULT.json
```
