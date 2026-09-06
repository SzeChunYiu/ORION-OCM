# Decoder presentation successor

Integrated commit `b95b2329d59b0b29a94a312366eb710fcbc91e60` changes only
`later_consumption_capture.decode_result` and adds its mocked regression file.
After the worker payload has passed the existing completion checks, a
`PASS`, `FAIL` or `SOLUTION` clears the initialized unavailable-return reason
before applying the payload. An explicit native reason is still preserved.
`CANNOT_CHECK`, malformed output and failed/timeout processes remain refusals.
No status, candidate, solver return, warrant or historical verdict is promoted.

## Source succession

| Source | SHA-256 of `later_consumption_capture.py` |
|---|---|
| Original captured decoder, retained | `5c86f5d8f01f2899b6abec1f2aa7bd7c78ea5e689548bebf8b69aff3f4fdb6a9` |
| Integrated corrected successor | `c60e215f5f0d1839b5686ddfb752a5dffb743cb5ca7bf1669e9a4e40e8fb340e` |

The [original result](../../../research/ocm-prototype/results/later-consumption-20260906/RESULT.md)
records the stale reason alongside the raw C-spec `UNSAT`/`PASS` evidence.
The [original assessment](../../../research/ocm-prototype/results/later-consumption-20260906/run-v1/assessment/receipt.json)
is retained exactly; it is not rewritten or reinterpreted as a successor run.
Both original study worktrees, manifests, raw captures and seals remain bound
to their historical source. The integrated fix does not qualify a native run
of new bytes under an old manifest.

## Regression evidence

The [red run](decoder-red.json) failed exactly the omitted-reason cases for
`PASS`, `FAIL` and `SOLUTION`; the other nine controls passed. The
[green run](decoder-green.json) passed all 12. Controls preserve explicit
reasons and exercise invalid JSON, invalid result shape/status, Boolean worker
identity, invalid candidate, incomplete results and timeout refusal. All 12
also passed within the final 57-test mocked integration run.

No native synthesis or checker was invoked for the fix. The
[qualification](CORE.md) binds its final bytes separately from historical
research evidence.
