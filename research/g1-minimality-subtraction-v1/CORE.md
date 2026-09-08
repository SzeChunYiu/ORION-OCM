# G1.2 subtraction / minimality

**Terminal:** `CURRENT_KSO_PARENT_NOT_MINIMAL`

This runs the G1.2 subtraction inventory against the G1.1 freeze
[`research/g1-vessel-freeze-v1`](../g1-vessel-freeze-v1/CORE.md)
(`COMPACT_VESSEL_PARTIAL`). The freeze left two retained schemas:

1. M0 `ocm.runtime.OCMRuntime` (`src/ocm/runtime/state.py`)
2. `work.Operator` (`src/ocm/work/contracts.py`)

Neither is unused by tests. No named leftover core was deleted.
`MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE` is not issued.

[What was measured](RESULT.md) · [Machine-readable summary](SUMMARY.json)

No production code was deleted. Nothing was pushed.

## Scope

Head `d23410aaf084d03e658a020b0ec9c32d66b5d2e8` (`origin/main`).
`src/ocm/` tree `3a4dcbcf3a1875acefcec80cfa8d47330d172655` is unchanged
from the G1.1 freeze (`b35093a`). Later commits on this head are
research-only.

G1.2 asked to remove candidate architecture components one at a time,
permit compensating compositions, and measure capability / resource /
epistemic-invariant change. This capsule does that as **restore-after
probes**. It does not rewrite `work.Operator` into `OperatorSpec`.

## Inventory (what can be removed with tests still passing)

| Candidate | Role | Test-unused? | Hide-probe | Keep? |
|---|---|---|---|---|
| `src/ocm/runtime/state.py` (M0 `OCMRuntime`) | leftover custody core / name collision | no | collection fails | retain |
| `src/ocm/work/contracts.py` (`work.Operator`) | leftover donor operator schema | no | collection fails | retain |
| `src/ocm/store/evidence_identity.py` | unused sibling `EvidenceRecord` + fingerprints | yes on AST + tests | 177/177 pass | retain |

Cheapest proven-unused file is `evidence_identity.py` (46 nloc). Hiding
it did not break the sampled suites. It is **not** a cognitive core.
G1.2/008 forbids calling the machine minimal because unused code could
be deleted. The file stays.

Harness `-m` entrypoints (`evaluation/m*_eval.py`, `cli.py`, `status.py`)
look unused to AST import graphs because they are invoked as modules.
They are not subtraction candidates for `(F,O,Π,C)`.

## Exact blocker

```text
M0_OCMRUNTIME_AND_WORK_OPERATOR_REQUIRED_BY_TESTS
```

**M0 `OCMRuntime`.** Live cognition imports
`ocm.runtime.ocm_runtime.OCMRuntime`. The package export
`ocm.runtime.OCMRuntime` is the M0 Boolean-procedure custody object.
Tests that require it:

- `tests/m0/test_runtime_persistence.py` (3 tests: restart/revoke/reinstate,
  hash-chain tamper, outside-domain `CANNOT_CHECK`)
- CI `m0-canonical.yml` hostile-controls + `python -m ocm.demo --controlled`
  (`src/ocm/demo.py` imports M0 via `from .runtime import OCMRuntime`)

Without a compensating `__init__.py`, hiding `state.py` also breaks
`from ocm.runtime.ocm_runtime import OCMRuntime` because the package
init loads M0 first.

With an empty compensating `__init__.py`, live `tests/m2/test_ocm_runtime.py`
still passed (8/8) and M0 tests plus `ocm.demo` still failed. That is
algebraic non-necessity for the live machine **and** epistemic necessity
for the M0 custody programme. Deletion is not licensed.

**`work.Operator`.** Parallel operator API over dict state with KSO
warrant/authority. Production importers: `work.envs` / `work.methods`,
`lifetime.machine` / `lifetime.phases`, `science.lifecycle` /
`science.transfer`, `selfmodel.benchmark`, `evaluation.m9_transfer_eval`,
`evaluation.m10_science_eval`. Tests that import it:

- `tests/m9/test_work.py`, `tests/m9/test_method_contract_integrity_v3.py`
- `tests/m10/test_proof_lifecycle.py`
- `tests/m12/test_current_comparator_parity.py`

Hiding `contracts.py` fails M9 collection. Unification into
`OperatorSpec` would be a rewrite, not a proven-unused deletion.

## Necessity (G1.2/006)

| Candidate | Algebraic | Resource | Epistemic |
|---|---|---|---|
| M0 `OCMRuntime` | not needed by live `F/O/Π/C` once package init is emptied | 122 nloc custody; CI/demo cost | yes: M0 hash-chain persist/revoke/reinstate |
| `work.Operator` | yes for M9 skill/transfer (dict-state, not `KnowledgeSpace`) | 188 nloc contracts + 318 nloc envs/methods | yes: warrant/authority on procedural skills |
| `evidence_identity.py` | unused sibling of `store.evidence.EvidenceRecord` | 46 nloc, zero callers | spec mentions dual fingerprints; no test enforces them |

## G1.2 checkboxes

| id | status |
|---|---|
| G1.2/001 remove one at a time | `EARNED_AS_PROBES` (restored; no commit) |
| G1.2/002 compensating compositions | `EARNED_AS_PROBES` (empty `runtime/__init__`) |
| G1.2/003 capability loss | `EARNED` (table in RESULT.md) |
| G1.2/004 resource change | `EARNED` (nloc/bytes) |
| G1.2/005 epistemic-invariant failure | `EARNED` (M0 hash-chain tests fail when M0 is hidden) |
| G1.2/006 distinguish algebraic/resource/epistemic | `EARNED` |
| G1.2/007 preserve `PARENT_SUFFICIENT` | already CHECK; not reopened |
| G1.2/008 do not call “minimal” from deletion | CHECK; this capsule obeys it |

**Not earned:** vessel minimality; G1.1.6 as deletion.

## Terminal

`CURRENT_KSO_PARENT_NOT_MINIMAL` is the G1.2 exit.

Not issued: `MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE`,
`CURRENT_KSO_PARENT_SUFFICIENT`, `COMPACT_VESSEL_PARTIAL` (already
issued by the freeze; not re-issued here).
