# Qualified corrections with preserved originals

Control plane: [#1068](https://github.com/SzeChunYiu/ORION-OCM/issues/1068).
Historical evidence: [#833](https://github.com/SzeChunYiu/ORION-OCM/issues/833).

Read the [corrected theory](../gmi-1068-corrected-targets-v16/CORE.md),
[exact preregistered statements](../gmi-1068-corrected-targets-v16/TARGET_CONTRACT_V16.json),
[amendment events](AMENDMENT_LEDGER_V16.json) and [replayed result](RESULT_V16.json).

The [original scope snapshot](../gmi-1068-recursive-audit-v15/SCOPE_SNAPSHOT_V15.json)
remains unchanged:18 fulfilled,204 unresolved. R2-003 and R2-007 remain UNKNOWN.
A qualified replacement is counted separately only while its full statement
bundle and review evidence remain verified. With both replacements supported,
there are2 qualified replacements and202 active unresolved requirements.
No replacement is original fulfillment; overall closure remains OPEN.

The ledger retains exact historical passages and the interpretations corrected.
Revisions form one chain per original. Attestations bind current proof receipts;
retractions preserve history and withdraw authority. A superseded, failed or
retracted revision never silently restores an older successful result.
Semantic dependencies name exact active revisions and must remain qualified.

The gate reads the committed preregistration and checks every pinned source,
freshly replays the scientific package, then derives current accounting.
It rejects changed statements, erased events, forks, stale evidence and
coupled ledger/receipt edits. Structural validity alone establishes no proof.
Missing evidence returns CANNOT_CHECK separately from checked-invalid evidence.
Hash custody does not certify scientific truth; independent semantic review
and the explicit proof/finite-calibration/paper boundaries remain necessary.

This repository gate verifies the initial V16 ledger. Once published, its
bytes are immutable against the PR target base. A future package must pin
this ledger as its independently trusted predecessor before using the tested
append-only successor API; V16 does not authorize an in-place revision.
