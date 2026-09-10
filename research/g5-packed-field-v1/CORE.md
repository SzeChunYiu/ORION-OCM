# G5 packed physical field v1 — KSO parent

**Terminal: `FACTORIZED_KNOWLEDGE_SPACE_SUPPORTED`.**
A research packed `KnowledgeSpace` parent matches reference KSO semantics (digest, liveness, join/meet warrants, CONSTRAINT nogoods, edits). Production `src/ocm/kso/space.py` is unchanged. Packed columns and interned identifiers cut host bytes; append/replace walls are higher than the Python-object field, so the default stays objects.

Cognitive-benefit claims remain uninterpretable if Python-object snapshots dominate later measurements. This capsule is the G5.2 packed-field parent, parallel to `research/g5-physical-denominator-v1/` for the ledger.

## Question

Can interned identifiers, packed atom/edge columns, CSR incidence, version-bound indexes, copy-on-write / local deltas and immutable payload handles represent the reference KSO with exact semantic parity, and what are the byte and update costs versus Python objects?

## What was measured

At **N = 1024** atoms and 1024 hyperedges on this host, the Python-object field is **1,628,330 host bytes**. Packed columns are **157,140 bytes** (~9.7%). A full packed snapshot (columns + interned identifier strings + payload blobs + live indexes) is **313,052 bytes** (~19%). A single-atom local delta is **521 bytes**.

Type bitmaps touch **128 bytes** versus **1024** linear column reads (8×). Packed append of one atom+edge is slower than `dataclasses.replace` on the Python field (**5.96 ms** vs **0.90 ms** median): column copy plus index rebuild is charged. Production adoption is not supported by those update costs.

## What is not claimed

- Production default field was not switched.
- `PHYSICAL_DENOMINATOR_CLEAN` is not issued (JSONL ledger default remains; packed updates are not cheaper).
- Factored warrant (G5.3) and cognitive consolidation (G5.4) were not attempted.
- This is not a scientific efficiency or amortization result. It is an engineering parent for issue #165 G5.2.

[Result](RESULT.md) · [machine-readable summary](SUMMARY.json) · [raw vectors](results/scaling_raw.json)
