# KSO general epistemic field N/k indexes v2

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) §8 last four boxes / #93.
G5.2 packed field parent plus two typed domains on production `ocm.kso`.
No `src/` edits. Does not overwrite [`research/kso-general-field-v1/`](../kso-general-field-v1/).

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

## Question

On one packed Knowledge Space Object holding a language view (`lexeme`) and a
mathematics view (`theorem`):

1. Can unrelated cross-domain `N` grow without a second truth store or a domain-core fork?
2. Does relevant `k(q)` stay with the planted domain query while that `N` grows?
3. Are cross-domain indexes charged (construction, update, retrieval, materialization, hidden scans)?
4. Does a parent federation of isolated typed stores already match in-domain `k`, and what does it lose on cross-domain compose?

If those hold, `CURRENT_KSO_ALREADY_GENERAL_ENOUGH` remains the §8 success terminal.
Current KSO plus packed indexes receive first right of refusal.

## World

`N ∈ {64, 256, 1024}` atoms (matching G5.2 / H2 grids). Each scale plants:

- 8 language targets (`lexeme`, `content_ref` `lang-target:*`);
- 8 mathematics targets (`theorem`, `content_ref` `math-target:*`);
- the remainder split as unrelated extra lexemes and extra theorems.

Domain rings use `DEPENDENCE` only inside a domain. Extra types register on a
*local* `TypeRegistry`. `DEFAULT_REGISTRY` stays core.

`N_t` counts identity-bearing atoms and hyperedges. Warrant-set entries are
auxiliary. Relevant `k` is the planted tag posting, not type-index size.

## Arms

| Arm | What it inspects | Language-query work |
|---|---|---|
| Unified packed tag posting | one field, tag index | `2k` (retrieve + materialize) |
| Unified G5.2 type bitmap | type bitmap bytes | tracks `N`, not `k` |
| Unified linear column | every atom | `N + k` |
| Routed isolated stores | language store only | ties unified tag (`2k`) |
| Naive federation | scan both isolated stores | `N` |
| Federation copy-compose | copy `math_t0` into the language store | duplicates identity |

Index construction scans all `N` atoms once. Incremental append of one
unrelated theorem is `1`; a full posting rebuild is `N+1`. Packed CSR/bitmap
rebuild touches are billed on the update ledger. An uninstrumented linear
mutant that reports only hits is `CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN`.

## Parents

G5.2 packed physical field; inverted-file / posting-list retrieval; isolated
typed-store federation with a query router. Production `compose` is the
cross-domain identity parent (correspondence in one store, not a copied atom).

If the gates pass, in-domain `k` is parent-owned by typed indexes. The unified
packed KSO does not require a domain-core fork and does not mint a second truth
store. Isolated federation ties query work and must copy to compose.

## Not claimed

Programme-wide General Epistemic Field close. Language fluency. Prototype #73.
Re-issue of v1 type/warrant boxes (GEF/001–009). Production `space.py` adoption.
Lifetime 1×–30× confirmatory streams. Residual versus HNSW/ANN/RAG.
