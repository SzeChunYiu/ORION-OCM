# PR80 engineering receipt drift diagnostic

Classification: INFRASTRUCTURE. Owner: scientific acceptance/custody #38; PR80 integration.
Source inspected: 1de53bc88d461a71b6408007dfed2765aa6c17db.
This note changes no receipt, source, test or scientific terminal.

## Executed finding

M1 and M10 current verification both returned exit 1:
CURRENT RECEIPT REFUSED: engineering replay source inventory DRIFT.

The recorded and actual inventories each contain 299 files. No path was added or removed.
Only these three bindings differ:
- src/ocm/evaluation/scaling.py
- src/ocm/kso/admission.py
- tests/test_kso_optimization.py

The current revision config, replay, two JUnit reports and twelve successor receipts retained
identical before/after hashes during this read-only diagnostic.
No engineering rebuild or protected/scientific evaluation ran.

## Exact protocol boundary

[Rebuild tool](../../tools/rebuild_engineering_replay_v4.py) expressly regenerates the current
engineering replay after executing the two fixed validation gates. Its declared outputs are:
- docs/provenance/runtime_revision_20260905_v4/ENGINEERING_REPLAY_V4.json
- docs/provenance/runtime_revision_20260905_v4/FOCUSED_SUITE.xml
- docs/provenance/runtime_revision_20260905_v4/FULL_SUITE.xml

That tool does not update the successor receipts which bind the replay.
[CurrentReceipts.write](../../tools/runtime_revision_receipts_v4.py) verifies an existing
successor and only creates a missing target with exclusive creation. Existing drift is refused.
[The custody protocol](runtime_revision_20260905_v2/README.md) explicitly states:
“A later source change requires another revision, not overwriting either earlier generation.”
[The V4 regression](../../tests/test_runtime_revision_receipts_v4.py),
test_no_recipe_execution_and_exclusive_idempotent_creation, requires the same refusal and
unchanged existing receipt bytes after a source change.

Consequently, rebuilding the replay alone cannot restore M1–M10 verification. Deleting or
overwriting their existing V4 successors would bypass the enforced current protocol.
Neither the no-run option nor a fresh digest proves that the required validation actually ran.

## Declared validation, if a successor revision is authorized

REVISION_V4.json declares an exact focused pytest command with eight test files (minimum 125),
and an exact full pytest tests command (minimum 861), each writing its named JUnit report.
Both must actually pass with no skips/failures/errors and bind the current source inventory.

The full suite includes tests/m12/test_paired.py, which uses temporary unit-test states and
V3/V4 stream checks. The inspected tests contain no --v5 invocation or protected V5 terminal.
The m12_paired_eval.py --v5 path is outside this task and was not executed or relabelled.
No M12 protected claim is needed to diagnose this engineering binding failure.

## Resolution boundary

No artifact was regenerated because the existing protocol does not authorize the successor
replacement needed to make the CI gate green. A reviewed current engineering revision or
explicit protocol amendment is required before changing that binding. It must preserve the
existing V4 receipts and their history, execute the required gates against the intended runtime,
and keep protected reevaluation, scientific promotion and independent replication unclaimed.

Raw diagnostic and all exact hashes:
billy:/home/billy/orion-director-work/20260906/pr80-engineering-receipt-diagnostic/diagnostic.json.
The first metadata attempt used an older system Python missing Path.is_relative_to; the diagnostic
was rerun successfully with the existing Python 3.13.12 environment. No runtime/test was executed
through another checkout's editable installation.
