# Acquisition freshness repair

The exact frozen v1 capture stopped before OCM acquisition: OCMRuntime creates its empty ledger.jsonl during construction, then the runner falsely classified that file as pre-existing study state.
This is an operational capture failure. No mechanism comparison or negative is established.

The only runtime change checks freshness before Actor construction.
A real fresh OCM constructor reaches the pre-acquisition fixture halt; genuinely persisted OCM state is refused before constructor execution.
Both controls first failed and then passed. The current N1/G1 scoped suite passed192 tests with unchanged source/test hashes.

The failed v1 remains immutable: native completed2 acquisitions and2 universal checks; OCM performed none. F1 was never created, and no mathematical application or syntax inference ran.
The exact external grader ran once: CANNOT_CHECK_STUDY, parent NOT_ESTABLISHED, and CANNOT_CHECK_COST. All36 math and5 syntax assignments per arm remain unchecked.
All7 recorded actor/native process IDs were absent after completion.

Raw v1 F0, receipt, seal, independent grade, launch/exit records and the failing stderr are copied unchanged under raw/.
The full original sealed capture and model remain in the separate release-only asset described by raw/clia-reuse-capture-v1-asset.json. No model binary enters git.
To replay a relocated asset, unpack its capture/ tree intact and use the unchanged external grader; do not edit manifests.
All original attempt costs remain charged alongside any separately frozen successor.

Protocol, tasks, argument tuples, model, checkers and resource settings are unchanged. A new committed-source F0 and fresh state are required for v2.
