# Packed physical field result

Host: `cursor`, x86_64, Linux 6.12.94+, Python 3.12.3. Worktree `research/g5-packed-field-v1`. Production `src/ocm/kso/space.py`, `warrant.py` and `types.py` were not edited.

**Terminal: `FACTORIZED_KNOWLEDGE_SPACE_SUPPORTED`.**

Twelve unittest cases passed in 0.043 s (`results/unittest_receipt.json`). Round-trip `to_reference()` / `from_reference()` preserves `KnowledgeSpace.digest()` and `as_dict` identity. Liveness under every subset of `{0,1,2}` matches the reference, including join/meet/partial/zero warrants, `edge_enabled_liveness`, and CONSTRAINT nogood filtering (MEG-16). Edits (`with_atoms`, `with_edges`, `replace_atom`, `without`) match the reference digest.

## Scaling (N atoms + N hyperedges)

Raw vectors: [results/scaling_raw.json](results/scaling_raw.json). Slim table: [results/scaling_summary.json](results/scaling_summary.json).

| N | Python host B | packed columns B | packed snapshot B | local delta B | append Python median | append packed median | bitmap units | linear units |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 103,697 | 9,836 | 18,298 | 521 | 62 µs | 414 µs | 8 | 64 |
| 256 | 408,120 | 39,296 | 73,087 | 521 | 227 µs | 1.38 ms | 32 | 256 |
| 1024 | 1,628,330 | 157,140 | 313,052 | 521 | 0.90 ms | 5.96 ms | 128 | 1024 |

N grew 16× from 64 to 1024. Python-object host bytes grew **15.7×**. Packed columns grew **16.0×** (linear in N). At N = 1024 packed columns are **9.7%** of the Python-object field; the full packed snapshot (columns + interned identifier strings + payload blobs + live indexes) is **19.2%**.

A single-atom patch writes a **521-byte** local delta against a **313,083-byte** snapshot (~600×). Intern tables and base packed columns keep the same `id()` across that edit (copy-on-write). Append of one atom+edge clones dirty atom/edge columns and rebuilds version-bound indexes; that packed append is **~6.6×** slower than `KnowledgeSpace.with_atoms` / `with_edges` at N = 1024. Type-bitmap scans touch 8× fewer units than a linear column scan; CPython wall at this N still favours walking the Python tuple (13.6 µs vs 60 µs bitmap). Units, not wall, are the justification recorded for the bitmap.

## G5.2 boxes

| Box | Status |
|---|---|
| stable integer handles | checked (interned atom/edge ids, uint32) |
| dictionary-encoded type/relation/scope/authority identifiers | checked |
| packed atom/edge columns | checked (`array` uint32/int64/uint8) |
| incidence arrays | checked (CSR tails/heads + inverse incident/outgoing) |
| compact bitmap/index structures where justified | checked (type bitmaps; both bitmap and linear costs counted) |
| structural sharing / copy-on-write | checked (shared intern/payloads; dirty columns cloned; replace uses delta overlay) |
| version-bound indexes | checked (rebuild or incremental type-bitmap patch; unusable if version mismatches) |
| local deltas | checked (single-atom overlay smaller than snapshot) |
| immutable payload/archive handles | checked (content-addressed blobs, handle 0 = None) |
| exact semantic parity with reference KSO | checked (digest, liveness, edits, nogoods) |

## Why this terminal

`PHYSICAL_DENOMINATOR_CLEAN` would require the packed field *and* production meters that no longer pay Python-object snapshots or JSONL rewrite. Packed bytes are smaller; packed **update** walls are larger than the incumbent object field, so the production default stays `KnowledgeSpace`. `DATABASE_PARENT_SUFFICIENT` is the G5.1 ledger terminal, not this capsule. `PARENT_SUFFICIENT` would erase the packed parent. The honest G5.2 terminal is `FACTORIZED_KNOWLEDGE_SPACE_SUPPORTED`: the research parent exists, parity holds, economics are reported, production is not switched.

Factored warrant (G5.3) is out of scope. Warrant profiles are interned as handles; lower/upper algebra still runs on the reference `WarrantProfile` objects.

Production adoption remains a separate contract decision. This capsule does not switch `ocm.kso.space.KnowledgeSpace`.
