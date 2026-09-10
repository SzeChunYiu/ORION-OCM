# G5.3 warrant adoption result

**Terminal:** `DATABASE_PARENT_SUFFICIENT`

**Claim ceiling:** Toy/microscope warrant-parent economics on construction, query, revocation, and bytes as separate coordinates. Predecessors' n=3 parity is cited, not overwritten. Production `warrant.py` is unchanged. No production adoption. `PHYSICAL_DENOMINATOR_CLEAN` not claimed. `PARENT_SUFFICIENT` is not programme failure.

Cited, not rewritten:

- v1 `FACTORED_WARRANT_VALUE_SUPPORTED`
- v2 `BDD_PARENT_N3_PARITY_SUPPORTED` (ZDD was OPEN)
- v3 `ZDD_PARENT_N3_PARITY_SUPPORTED` (production unchanged; G5.3/008 `NOT_ADOPTED`)
- G5.1 `DATABASE_PARENT_SUFFICIENT` (ledger parent; not a clean physical denominator)

n=3 four-way expand/liveness parity held (168/168 intervals, 1344/1344 liveness). Construction, query, revocation, and bytes were **not** summed and were not converted to dollars.

## Structural coordinates (decision)

Shared unique tables vs per-interval antichain store. Lower is better.

| n | samples | antichain bytes / units | DAG bytes / units | ROBDD bytes / units | ZDD bytes / units | structural winner |
|---:|---:|---:|---:|---:|---:|---|
| 3 | 168 | 154224 / 540 | 5768 / 20 | 9111 / 20 | 8346 / 20 | DAG/BDD/ZDD (toy sharing) |
| 6 | 40 | 58892 / 217 | 55864 / 183 | 134663 / 335 | 105522 / 264 | DAG only |
| 8 | 40 | 95124 / 374 | 125848 / 415 | 512143 / 1204 | 329490 / 875 | antichain |
| 10 | 40 | 160568 / 638 | 252840 / 833 | 1670143 / 3522 | 844754 / 2136 | antichain |

At the largest measured *n* every research parent is strictly larger on **both** bytes and structural units. Query-expand of a diagram reconstructs the antichain (identity for the production parent). Construction of DAG/BDD/ZDD is a conversion tax from that antichain. Wall times are reported in `RESULT.json` and are not scalarized into the terminal.

G5.3/008 disposition: `ECONOMICS_DO_NOT_SUPPORT_PRODUCTION_SWITCH`. GitHub checkbox stays open. `src/` was not switched.
