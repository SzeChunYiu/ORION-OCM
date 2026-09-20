# Existing-round CI baseline repair
The first V10 CI run failed the inherited V9 job with
STATUS_ONLY_PROMOTION:R0. Both V9 snapshot checks passed; the final transition
check incorrectly compared V9 against V8 using only the later V10 PR's paths.

Root cause: an introduction-only baseline was reused for every subsequent PR.
After V9 merges, R0 is already earned on the target branch. Its original
promotion must not be attributed again to an unrelated successor.

select_ci_baseline.py reads the exact target commit. If that commit contains
the current round snapshot, it uses those bytes. Only actual absence selects
the predecessor for first introduction. Missing commit/blob evidence is
CANNOT_CHECK (exit2); malformed input is CHECKED_INVALID (exit1).
No git error silently enables a fallback. Historical snapshot checkers still
validate the original transition, source hashes and complete atom records.

Four regression tests use actual H/I commits and V8/V9/V10 snapshots:
the old call reproduces the failure, the existing-round call passes, first
introduction still rejects unsupported promotion, and the supported original
R0 introduction passes. Missing/malformed evidence controls retain distinct
failure classifications. Both V9 and V10 workflows use this selector.
No frozen evidence or scientific result changes.
