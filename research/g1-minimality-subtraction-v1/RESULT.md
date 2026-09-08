# What G1.2 subtraction measured

Worktree `research/issue-165-g1-minimality` at
`d23410aaf084d03e658a020b0ec9c32d66b5d2e8`. Interpreter: CPython 3.14 +
`pytest==8.3.5`, `PYTHONPATH=src`. Production files were hidden only
inside restore-after probes.

Baseline (files present):

| suite | result |
|---|---|
| `tests/m0/test_runtime_persistence.py` | 3 passed in 0.02s |
| `tests/m9/test_work.py` + `test_method_contract_integrity_v3.py` | 8 passed in 0.05s |
| `tests/m1` + `tests/m2/test_ocm_runtime.py` + `test_sqlite_ledger_parent.py` | 166 passed in 33.86s |

## Probe 1 — hide `src/ocm/store/evidence_identity.py`

Cheapest AST-unused file (46 nloc / 2185 bytes). No `tests/` or `src/`
importer. Duplicate `EvidenceRecord` lives beside
`store.evidence.EvidenceRecord`.

Same suites as the 3+8+166 slice: **177 passed in 32.59s**.

Not kept. Unused helper deletion is not core elimination (G1.2/008).

## Probe 2 — hide `src/ocm/runtime/state.py` (no `__init__` change)

Collection errors:

```text
src/ocm/runtime/__init__.py:3
ModuleNotFoundError: No module named 'ocm.runtime.state'
```

`tests/m0/test_runtime_persistence.py` and
`tests/m2/test_ocm_runtime.py` both fail at collection.
`from ocm.runtime.ocm_runtime import OCMRuntime` also fails: package
init loads M0 first.

Resource delta if committed: −122 nloc / −8329 bytes, plus a broken
live import graph.

## Probe 3 — hide `state.py` + empty compensating `__init__.py`

| arm | result |
|---|---|
| `tests/m0/test_runtime_persistence.py` | collection `ImportError: cannot import name 'OCMRuntime' from 'ocm.runtime'` |
| `tests/m2/test_ocm_runtime.py` | 8 passed in 0.11s |
| `from ocm.demo import OCMRuntime` | `ImportError` (`demo.py:5 from .runtime import OCMRuntime`) |

Capability: live M2 executive survives; M0 persist/revoke/reinstate and
the controlled demo do not. Epistemic invariant that fails is the M0
hash-chain (`test_event_hash_chain_rejects_tamper`).

CI that would go red: `.github/workflows/m0-canonical.yml`
`hostile-controls` and `controlled-demo`.

## Probe 4 — hide `src/ocm/work/contracts.py`

```text
tests/m9/test_method_contract_integrity_v3.py:6
ModuleNotFoundError: No module named 'ocm.work.contracts'
```

Both M9 files fail at collection (8 tests uncollected). Resource delta
if committed: −188 nloc / −10760 bytes, plus broken lifetime / science /
M10 / M12 importers.

## What was not attempted

- Rewriting `work.Operator` into `operators.registry.OperatorSpec`
- Repointing `ocm.runtime` to export the live `ocm_runtime.OCMRuntime`
- Deleting M0 tests or the controlled demo to make a hide “pass”
- Full `tests/` after every hide (probes used the suites that import
  the candidate)

## Disposition

```text
CURRENT_KSO_PARENT_NOT_MINIMAL
blocker = M0_OCMRUNTIME_AND_WORK_OPERATOR_REQUIRED_BY_TESTS
```

Tree restored. `git status` on `src/` was clean after the probes.
