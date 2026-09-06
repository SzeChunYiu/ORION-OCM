# Executed engineering successor — 2026-09-06

Owner: #72 / #38 / #49. INFRASTRUCTURE; no paper claim is established.

The source-addressed successor passed its actual fixed replay and all twelve milestone wrappers.
The earlier V1–V4 generations and protected V5 receipt remain unchanged.

## Selected result

- Source inventory: 307 files; SHA256 `33e7bb0a24b773b6c5261183dc37efba312418625eafffbbf67b0b6812c51b83`.
- Receipt SHA256: `bb75eb4674c19a30ada1f21186288854785f3673ae339c5d7bbd9e98cb13edce`.
- [Raw selected receipt](runs/33e7bb0a24b773b6c5261183dc37efba312418625eafffbbf67b0b6812c51b83/e0243cbe76924c90/RECEIPT.json) binds each command, log, JUnit, source archive and execution cost.
- [Twelve-wrapper verification](EXECUTED_VERIFICATION_V1.json) records each executed command and returned result.

| Fixed replay | Passed | Failed / errors / skipped | Wall seconds |
|---|---:|---:|---:|
| focused_suite | 133 | 0 / 0 / 0 | 34.440 |
| full_suite | 979 | 0 / 0 / 0 | 228.520 |

All 18 new selector/recorder controls also passed in the final full suite. They cover source and
artifact drift, unauthorized authority, missing/failed/skipped gates, predecessor binding, atomic
selection, exact interpreter execution, and exit-zero invalid-JUnit failure custody.

## Retained failures and stage-specific correction

Both earlier attempts remain immutable under source `9c4278649aef8e6ac633f7bf6d2c14b2433c9646a01e54fe03522e777f9c78e0`.

- Run `897c425465014059`: focused 127 passed / 6 errors because the initial environment lacked
  setuptools for the wheel fixture. The dedicated receipt environment supplied existing project pins.
- Run `3775d5e1bc294a3b`: focused 133 passed; full 973 passed / 2 failed. The failures were legacy
  V2/V3 wrapper-dispatch assertions. Only those assertions were updated to the new shared selector.

The reviewed recorder fixes bind both executable and Python argv[0] to the selected interpreter,
and retain FAILED.json for exit-zero skipped/missing/malformed JUnit without replacing the pointer.
The corrected source received its own complete replay; no prior result was rebound.

## Environment and historical custody

[Actual environment](ENVIRONMENT_V1.json): laptop Python 3.13.12, pytest 8.3.5, setuptools 75.8.0,
wheel 0.45.1, editable OCM 0.1.0 imported from this support checkout. Both suites used its absolute
Python executable with this checkout src on PYTHONPATH; ambient PYTEST_ADDOPTS was removed.

Predecessor verification passed for the original 302-file source inventory and bound V4/V5 records.
All 167 previously tracked provenance files were independently compared with committed HEAD and
were byte-identical. Production src bytes were unchanged by this receipt implementation.

Protected reevaluation: NOT_RUN. Scientific promotion: NOT_ESTABLISHED. Independent replication:
NOT_RUN. The ordinary inherited temporary-state unit tests are engineering tests; the recorder did
not invoke the protected M12 evaluator or rewrite a historical result. Energy and environment setup
and development costs remain unmeasured; measured child CPU and wall time are in the raw receipt.
