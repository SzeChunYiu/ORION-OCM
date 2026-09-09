# H2 sparse relevant cognition v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) H2 boxes, planted
packed-field / posting-index world only.

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

## Question

On a finite authored knowledge space, using the G5.2 packed physical field
parent at `research/g5-packed-field-v1/` (no `src/` edits, production
`ocm.kso.space` unchanged):

```text
k(q, K_t) << N_t
```

and query cost tracks `k` materially better than `N`.

Charge:

1. index construction;
2. index update;
3. retrieval;
4. materialization;
5. hidden scans.

## World

`N ∈ {64, 256, 1024}` atoms and matching hyperedges (same N grid as G5.2).
Exactly `k = 8` planted `goal` atoms; the rest are distractors
(`claim` / `procedure` / `observation`). Query `q` retrieves every `goal`.

`N_t` counts identity-bearing atoms and hyperedges. Warrant-set entries are
auxiliary and do not pad `N`. `k(q)` is identity-bearing objects **actually
touched** during `q`, not result size, not estimated relevance.

## Arms (exact work units, not wall)

| Arm | What it inspects | Query work |
|---|---|---|
| G5.2 linear column | every atom type cell | `N` (G5.2 `linear_units_touched`) |
| G5.2 type bitmap | every bitmap byte | `⌈N/8⌉` (G5.2 `bitmap_units_touched`) |
| inverted posting list | the `goal` posting | `k` retrieval + `k` materialization |
| `live_atoms` | every atom warrant | hidden full scan = `N` |

G5.2 already counted bitmap vs linear. Bitmap is 8× cheaper than linear and
**still tracks `N`**, not `k`. Posting-list retrieval stays with `k` while
`N` grows 16×. Construction of the posting index scans all `N` atoms once and
is billed separately. A packed `with_atoms` rebuild of G5 indexes is billed as
update (`build_touches ~ N`); an incremental posting append is billed as `1`.

A mutant that walks every atom and reports only the hits, without charging the
scan, is `CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN`. Hidden full scans that
**are** instrumented appear in `k` and in `hidden_scan_units`.

## Parents

Inverted-file / posting-list retrieval (IR, database secondary indexes) on the
G5.2 packed field (interned identifiers, type bitmaps, version-bound indexes).
If the gates pass here, the mechanism is `PARENT_SUFFICIENT` at this scope —
not an OCM residual over indexes.

## Not claimed

Programme-wide H2 close. Lifetime 1×/3×/10×/30× confirmatory streams. Residual
vs HNSW/ANN/RAG/MoE. Production `space.py` adoption. H3–H5. M11/M12 scientific
inheritance. Wall-time as a primary coordinate (units are).
