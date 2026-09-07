# Resource successor portable guard qualification

`resource_successor_evidence.py` is additive; the original guard, its test file, native helper and 12 original record files are unchanged (15 protected file identities checked).

The real default CLI returned `RESOURCE_SUCCESSOR_CUSTODY_PASS`: 380 historical archive members / 19 historical source snapshots, separately 1,518 successor members / 6,702,958 raw bytes / 22 current sources. Omitted host inputs are explicitly not revalidated. This is archive/source custody, not resource, corpus, proof or neural-absence qualification.

The final guard binds successor seal `3d900f8700445844c1b3c926a1ff150f702c43f841e94a208608ff171645d8c7` and historical seal `2457516e82e1b07062360655dc0dfbce772f3b72aa16379bcfadb23eb6ae00e0`. Source SHA256 is `2d15a21e2c20bfc9063721e94848ab441f12cf8227c45c4ea5d4732eccfc8fec` (151 lines).

## Qualification chain

- `01-red`: 15 authored controls failed against the explicit unimplemented interface, exit 1.
- `02-green`: first 15 controls passed.
- `03-red`: four concrete custody failures reproduced: archive/source mutation during checking, current root alias, historical root alias. Three existing helper/count controls passed.
- `04-green`: all 22 controls passed after those repairs.
- `05-red`: root review's late extra historical file was accepted; its new control failed as intended.
- `06-final`: repaired exact-set check plus final seal binding; 23 controls passed in 0.20 s. Exact subprocess wall and source hashes are in its JSON.
- `07-real`: actual source-only CLI ran once from `/tmp` with empty environment, CPython 3.11.14, `-I -S`; exit 0, empty stderr, 0.155026215 s wall, PID 758813 reaped and process group absent. Selected source hashes match before/after. CPU/RSS are unavailable, not inferred.
- `08-review`: independent source review of the exact final hash, no reviewer execution; no blocker found.

The fixtures include appended extra/duplicate tar members, replaced historical authority, current/historical snapshot divergence, recursive additions, malformed counts, source symlinks, and external paths that must remain unopened. Two matching-header cache controls demonstrate harmless poisoned caches execute through normal import while the qualified helper loader uses only pinned source bytes.

No archived resource source is imported or executed. No resource/native/corpus/old-47 dispatch occurred. No commit was made. The no-alarm record is an independent portable verification of the sealed current records, not a relabeling of earlier test or runtime receipts.

## Files

Production: `resource_successor_evidence.py`.
Controls: `test_resource_successor_evidence.py`, `test_resource_successor_evidence_boundaries.py`.
Data helper: `test_resource_successor_fixture.py`.
Raw commands, JUnit, stdout/stderr, preserved pre-repair guard versions, final source snapshots and protected-file identities remain beside this note. `EVIDENCE_SEAL.json` binds every retained member except itself.
