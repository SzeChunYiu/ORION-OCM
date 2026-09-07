# Native proof/runtime lifecycle record audit

Decision: **RECORD_AUDIT_PASS**. No native-result defect found in the audited scope.
This is a read-only audit of retained bytes, source bindings and process receipts.
No OCM restore, tests, worker, Lean command or proof experiment was executed.
The auditor implemented the lifecycle driver; another agent independently reviewed its source.

## Exact receipt

- Raw directory: `/home/billy/orion-director-work/20260907/proof-runtime-commissioning-20260907`.
- Result SHA256: `c1d93fa010515a97f8746bd53252253c8b7d46a95c1c8e78222a023d0ae2f5da`.
- Freeze SHA256: `f71f9053b8dd2270c9a41bcb4e4415f26cc5ee03d1c49b04ae035f5e0f2d5b8f`.
- Runtime manifest SHA256: `93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`.
- All 24 registered phase names, ordering and individual PASS records agree.
- 192 source, 740 host-Python and 195 input/snapshot bindings match actual bytes.
- Snapshot file membership is exact. Parent and recorded phase imports match declared source/stdlib identities.
- Parent executable is CPython 3.11.14; recorded launch uses `-I -S -B` and the exact source entrypoint.

## Actual construction, checking and restart

- Exactly two proposal directories, two checker directories and two authentication directories exist.
- B run: `a6fcc05f50714090ba2014e983a14092`.
- C run: `e8094210b07b4ec988ca79b6dd5f2991`.
- Each actual OCM solve returned ANSWER and admitted its own exact candidate and fresh checker handle.
- Both independently invoked the typed symbolic worker: 24 applications, 37 terms, 33 index probes, 10 introductions, 42 type checks each.
- Candidate JSON SHA256: `17bb3917e2da89db56d1314c2828104e865becbd5a4d7c56a7cdc46fc127dfad` in both runs.
- Both freshly compiled Foundation, fixed Target, and Candidate under Lean 4.33.1 after the version probe.
- Exact target: `F0Target.statement`; Target SHA256 `0694094c1851d5fb72827f4af8a5de0e7d5fd14b646ad9926319f573206273ce`.
- Each candidate's raw axiom report is empty. Foundation has separately reported allowed assumptions; its reports are not mislabelled empty.
- The candidate uses no supplied proof constant in its proof body; Eq occurs in a type annotation.
- The worker guard is sealed, has no prohibited events, and lists only its three registered source modules plus copied Python/built-in/frozen origins.
- Thirteen distinct process receipts: two workers, eight Lean phases, three cold Python children.
- All return zero, have empty stderr and retain matching text/base64 output; native stream hashes and sizes match.
- All thirteen recorded groups are reaped/absent; read-only group probes also found them absent at audit.
- Cold LIVE / OPEN / LIVE children have matching outer/inner PIDs, bound imports, no session and no executable or host operator bindings.

## Support lifecycle

- Discovery A: `ev:ocm:218dbf458738a6c7`.
- Shared checker environment S: `ev:ocm:210d3bd6cb9f235b`.
- B correctness evidence: `ev:ocm:a74ccba238ed3c65`.
- C correctness evidence: `ev:ocm:278ae6a9a35f42cb`.
- Each claim has exact support run-evidence AND S; A does not occur in correctness support.
- A withdrawal retains formal LIVE and makes applicability false. Reinstatement restores applicability.
- B withdrawal before C gives OPEN; after C exists it remains LIVE. Withdrawing both gives OPEN.
- Withdrawing shared S gives OPEN; reinstatement restores LIVE.
- The exact five withdrawals and four reinstatements match the runtime event schedule.
- Ledger hashes/chains verify: 37 OCM rows and 5 issuer rows; exactly two PREPARED/COMMITTED routes.
- Exactly two QUERY_OPENED and CHECKER_RESULT events and six admitted evidence records remain.
- Revision/status receipts assert unchanged dispatch/evidence state; the complete native directory inventory corroborates no additional proposal/check attempts.
- This establishes two independently executed runs, not independent proof systems: both share Lean, sources, target and environment S.

## Costs and retention

- Driver outer wall: `42.449141277` seconds, through final source/input checks.
- GNU time reports 42.54 seconds elapsed, 31.22 user seconds, 6.98 system seconds and 90,676 KiB maximum RSS; exit status zero.
- These are reported process-envelope measurements, not per-phase attribution or simultaneous aggregate system RSS.
- Earlier runtime acquisition/preparation and final result serialization are outside the driver wall; nested phase costs overlap and must not be added to the outer value.
- Complete native tree: **313 files, 14,402,274 bytes**.
- Archive **307 files, 13,754,530 bytes** with original raw source, inputs, ledgers, manifests and receipts unchanged.
- Exclude only the six `.olean` bodies, **647,744 bytes**; retain every relative path, SHA256 and byte size from `RAW_INVENTORY.json`.
- No `__pycache__` files exist in this native tree. If an archive assembler introduces caches, exclude them and record the distinction.
- Include the external stdout log, GNU-time record, this audit/inventory and the qualification/source-review receipts as separately inventoried supporting files.
- Preserve the complete original tree. A metadata-only compiled-artifact archive is an evidence bundle; it cannot directly satisfy the original runtime custody API without the original compiled bytes and paths.

## Audit custody and limits

`AUDIT.json` contains the compact exact findings; `RAW_INVENTORY.json` binds all 313 native files.
`audit_records.py` is the actual standard-library-only inspection script executed on billy-laptop.
Command: stable engineering Python `-B -I /home/billy/orion-director-work/20260907/proof-runtime-native-audit-v2/audit_records.py`.
The earlier audit helper first mishandled a null close-phase value, then excluded a stored `record_path` when comparing handles.
Those helper defects are retained under audit-v1 and explained by `HELPER_CORRECTION.json`; no native record changed.
No broad performance advantage, learned method, cross-task transfer, scaling, FLT, or project completion is established here.
