# G5 physical denominator v1 — ledger parent

**Terminal: `DATABASE_PARENT_SUFFICIENT`.**
Mature SQLite/WAL is enough to stop whole-file ledger rewrite, full-history head queries, and hot-path full-state copies on the ledger path. Production `src/ocm/store/ledger.py` is unchanged.

Cognitive-benefit claims remain uninterpretable if Python-object snapshots, whole-file JSONL rewrite, or full-chain hashing dominate later measurements. This capsule measures that denominator on the incumbent ledger and shows a parallel parent that removes it without changing hash-chain, CAS, or transaction-id semantics.

## Question

Can an append-only SQLite/WAL store with application snapshots, suffix restart replay, and incremental authenticated identity match the JSONL ledger exactly, so later lifetime-cost claims are not dominated by storage artifacts?

## What was measured

The incumbent JSONL store still rewrites the entire `ledger.jsonl` on every append (`NamedTemporaryFile` + `os.replace`) and `head()` still replays the full chain. At **N = 2048** small rows on this host that is **529,399,134 bytes written** (about 1022× stored size) and **14.3 ms** per head query.

A research WAL store under this directory, plus the already-present experimental `ocm.store.sqlite_ledger` parent, append incrementally. Head is a meta row plus primary-key lookup. Normal restart verifies only the suffix after the last snapshot. `verify()` remains full-genesis audit.

## What is not claimed

- Production default store was not switched.
- Packed KSO field (atoms, edges, incidence, COW, versioned indexes) is **`CANNOT_CHECK`** except integer **kind handles** on the ledger path.
- Factored warrant (G5.3) and cognitive consolidation (G5.4) were not attempted.
- This is not a scientific efficiency or amortization result. It is an engineering parent for issue #165 P2 / G5.1.

[Result](RESULT.md) · [machine-readable summary](SUMMARY.json) · [raw vectors](results/scaling_raw.json)
