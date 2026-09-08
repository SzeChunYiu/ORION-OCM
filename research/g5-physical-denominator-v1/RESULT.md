# Ledger physical-denominator result

Host: `BillydeMac-mini.local`, Apple M4, Darwin 25.4.0, Python 3.13.12. Worktree `research/issue-165-p2-physical`. Production JSONL and `sqlite_ledger` sources were not edited.

**Terminal: `DATABASE_PARENT_SUFFICIENT`.**

Fourteen parity/restart tests passed in 0.34 s (`results/pytest_receipt.json`). Semantic identity with the JSONL ledger holds for sequence, `entry_hash` / `prev_hash`, compare-and-swap (`expected_head=None` means genesis), and identified transaction ids (idempotent same content; `TransactionIdConflict` otherwise; idempotency before CAS).

## Scaling (N sequential CAS appends, 32-character pad)

Raw per-append wall and rewrite vectors: [results/scaling_raw.json](results/scaling_raw.json). Slim table: [results/scaling_summary.json](results/scaling_summary.json).

| N | JSONL total s | SQLite parent s | WAL+snapshot s | JSONL bytes written | WAL+snapshot net bytes | JSONL head s | SQLite head µs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 0.0213 | 0.0180 | 0.0569 | 0.52 MiB | 28 KiB | 0.42 ms | 105 |
| 256 | 0.0753 | 0.0688 | 0.1706 | 7.86 MiB | 92 KiB | 2.36 ms | 90 |
| 512 | 0.2668 | 0.1165 | 0.5819 | 31.5 MiB | 180 KiB | 6.13 ms | 66 |
| 1024 | 0.7178 | 0.2104 | 1.1343 | 126 MiB | 368 KiB | 7.45 ms | 76 |
| 2048 | 3.0367 | 1.3648 | 2.8778 | 505 MiB | 736 KiB | 14.33 ms | 66 |

N grew 32× from 64 to 2048. JSONL total wall grew **143×** (superlinear). The JSONL rewrite volume is the whole new file on every append: **529,399,134 bytes** at N = 2048 against **517,972 stored bytes** (~1022× amplification). SQLite/WAL net directory growth stays near stored size.

JSONL `head()` remains a full replay (**14.3 ms** at N = 2048). SQLite parent head stays **~66 µs**. The checkpointed research store head stays **0.33–0.50 ms** (meta + primary key + kind join). After N divisible by the snapshot interval, restart verified **0 suffix rows**.

Per-append wall on the research WAL store is higher than the existing `SQLiteLedgerStore` because each append opens a connection, interns a kind handle, and folds authenticated identity. That cost does **not** grow with history. Snapshot insert plus `PRAGMA wal_checkpoint(FULL)` at N = 2048 is **< 1 ms** total. Index/checkpoint maintenance does not dominate.

The existing experimental `src/ocm/store/sqlite_ledger.py` already removes whole-file rewrite and full-history head queries. It does not snapshot, suffix-replay, or maintain incremental identity. This capsule adds those G5.1 mechanisms in `wal_ledger.py` without replacing the production JSONL default.

## G5.1 boxes

| Box | Status |
|---|---|
| stop whole-file ledger rewrite on every append | checked on the research/SQLite parents; JSONL default still rewrites |
| evaluate SQLite/WAL or equivalent mature append store | checked (`journal_mode=wal`) |
| implement real snapshots/checkpoints | checked (application `snapshots` table + WAL checkpoint) |
| replay only suffix during normal restart | checked |
| retain full-genesis replay as audit | checked (`verify()` / `verify_from_genesis()`) |
| incremental authenticated state identity | checked (rolling fold of prev identity, sequence, entry hash) |
| remove hot-path detached full-state copies | checked (no JSONL `_validated_snapshot` byte copy) |
| avoid linear scans of full history for normal head queries | checked |
| count all build/update costs | checked (append, snapshot, WAL checkpoint, rewrite bytes, dir bytes) |

## G5.2 packed field

Integer **kind handles** and a `kind_dict` are implemented on the ledger path. Packed atoms/edges, incidence arrays, bitmaps, structural sharing, version-bound indexes, local deltas, and payload archive handles are **`CANNOT_CHECK`**. Exact KSO field parity is therefore not claimed.

## Why this terminal

`PHYSICAL_DENOMINATOR_CLEAN` would require the packed field and remaining P2 local-structure work. `INDEX_MAINTENANCE_DOMINATES` is rejected: checkpoint/index walls stay sub-millisecond while JSONL rewrite bytes grow as Θ(N²). The mature database parent already removes the ledger artifact that would otherwise dominate later cognitive-benefit measurements, provided future meters use the parent (or an adopted successor) rather than JSONL `head()` / whole-file append.

Production adoption remains a separate contract decision. This capsule does not switch `LedgerStore`.
