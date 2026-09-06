# Portable mocked assay qualification

**Fixed the N1 hosted-test failure without changing production qualification.**
The shared `prepared()` test helper now accepts pytest's `monkeypatch` and
binds one temporary file labelled `MOCK_UNIT_TEST_ENVIRONMENT_NOT_NATIVE_QUALIFICATION`.
Capture, source, request, command and raw-seal validation still use the existing
production code. The patch changes only two generation-test files.

The failed PR #127 head was `58f80021f7d1704af7da8948a3bece5568dc76be`.
N1 run `34058431895`, job `101554499633`, used hosted Python 3.11.16.
The tests had called the real pinned-generation environment inspector before
substituting their native donors. That inspector correctly refused the host.

## Evidence

- [Red](RED.json): all 13 affected controls reproduced the same interpreter
  refusal on an isolated laptop Python 3.11.14 environment.
- [First green](GREEN.json): 104 generation controls passed after fixture
  isolation; one real-Z3 test was deliberately deselected.
- [Final bound execution](QUALIFIED.json): 104 passed, zero failures/errors/skips,
  with exact test hashes checked before and after execution. This repeats the
  same success to bind final source; it is not another 104 independent cases.
- [Independent review](INDEPENDENT_REVIEW.json): production pin unchanged;
  all 81 historical assay/diagnostic files remain byte-identical.

New controls require changed mock-environment bytes to fail production binding
validation before dispatch, and call the real uncached environment inspector
to confirm that an unpinned interpreter is rejected before dependency lookup.
The existing worker/envelope control verifies the exact sentinel binding.

## Execution scope

The [N1 workflow](../../../.github/workflows/n1-packed-chart.yml) selects both
`research/ocm-n1` and `research/ocm-prototype`. This repair qualified only its
`research/ocm-prototype/generation_tests` subtree, retaining archived-results
and hosted-control exclusions. `test_fixed_z3_equivalence_and_wrong_value`
was explicitly deselected because it invokes real Z3. Full exact-head hosted
CI remains the integration gate; this record does not claim that full run.

The fresh laptop environment contains Python 3.11.14, pytest 8.3.5 and
sexpdata 1.0.2; cvc5 and Z3 are not installed. The recorded import/process guard
logged only 14 Git lineage reads and one phase-log flushing child. There were
zero native synthesis, checker or induction executions and no refused attempts.
No registered assay was prepared, frozen, regraded or rerun.

[Source before repair](SOURCE_BEFORE.json), [final source before execution](QUALIFIED_TEST_SOURCE_BEFORE.json),
[exact cases](QUALIFIED_CASES.json), raw stdout/stderr, JUnit and process logs
are bound by [artifact hashes](ARTIFACTS.json). Production source, frozen
research records and V4 core source ID
`0d114c3087855886242611c623f7ccd60061c140e7b5de4033e6df5644b94948`
remain unchanged. The earlier [integration record](../research_assay_integration_20260906/CORE.md)
retains its original execution identity and scope.
