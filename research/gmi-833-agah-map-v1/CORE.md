# AG/AH structural map + citation auditor (START HERE)

Issue #833 sections **AG** (comment `5693520829`, 55 rows) and **AH** (comment `5693590252`,
20 rows) were entirely unstarted — 75 open rows, zero packages on `main`. Most of the substance,
it turns out, is already discharged by the merged AJ stream under different section labels. The
risk in a tranche like that is **misreporting a parent**, so the first instrument built here is the
one that decides whether a citation is allowed.

## Where the 75 rows stand

| disposition | rows |
|---|---|
| closed by **verified parent reconciliation** | `40` |
| closed by **new work in this tranche** (`gmi-833-ag1-descent-stack-v1`, `gmi-833-ag2-signature-free-syntax-v1`) | `15` |
| **open**, each with a reason and a named next tranche | `20` |

| bucket | rows |
|---|---|
| `EXACT-FORMAL` — provable now over an existing finite universe | `32` |
| `DISCIPLINE-CONTRACT` — a prohibition; closes only when some configuration trips it | `16` |
| `HARNESS` — an exact instrument over a result already frozen on `main` | `15` |
| `NEW-SCIENCE` — genuine derivation required | `11` |
| `EXTERNAL-GATE` — no model-only route exists | `1` |

## RA-1 — the citation auditor

`40` citations, `185` receipt fields across `20` merged parent packages, every receipt pinned by
git blob sha. Thirteen violation counters, **all zero**. A citation is admissible only if the
package exists at its pinned sha, every cited field resolves and matches byte-exactly, the parent's
status is `GREEN`, **and the row's plain meaning is not something the cited parent forbids**.

That last criterion is not decorative. Closing AG3's *"flagship 'fundamental primitive' claims must
survive replacement of the chosen generating presentation"* as a clean positive citing AJ5 would
assert `COMPILER_MAKES_SEARCH_BIAS_INVARIANT` — which AJ5 lists as forbidden. The auditor refuses
it (hostile `HA4`), and the row instead closes `EARNED_BY_COUNTEREXAMPLE` naming the four
quantities AJ5 records as non-invariant without the resource map.

## Evidence

- 2 materially independent routes (dot-path resolution + fixed forbidden-key list, vs exhaustive
  receipt flattening + forbidden-set harvest by key-name prefix). All shared quantities agree.
- 11 hostiles, each paired with the clean counter so the check is shown to **move** the quantity it
  perturbs. The row-text-drift hostile is additionally shown to be isolated.
- Null: 200 misdirected citations (real replacement, real but wrong parent) → `0/200` admissible.
- No-alarm case asserted on the real table.
- Every `old` and `anchor` re-verified byte-exact against a fresh fetch of both live comments;
  75 live open rows, 75 accounted for, 0 missing, 0 extra, every anchor unique.

## What this does not claim

`AG_AH_SECTIONS_DISCHARGED` (20 rows remain open), `PARENT_CITATION_PROVES_ROW_CONTENT`
(admissibility is not proof of content — the cited parent still owns it),
`BUCKET_CLASSIFICATION_IS_A_THEOREM`.

## Reproduce

```
python3 -I -B  research/gmi-833-agah-map-v1/citation_audit_v1.py
python3 -I -B  research/gmi-833-agah-map-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-agah-map-v1/test_agah_map_v1.py
```

## Files

`FREEZE_V1.md` (committed before any code) · `AGAH_ROWS_V1.json` (75 rows, byte-exact) ·
`AGAH_STRUCTURAL_MAP_V1.json` (bucket + disposition + reason per row) ·
`STRUCTURAL_MAP.md` (the same, readable) · `CITATION_TABLE_V1.json` ·
`ISSUE_833_COMMENT_RECONCILIATION_V1.json` (55 replacements, 20 not_closed) ·
`AGAH_MAP_THEOREMS_V1.md` (RA-1, RA-2) · `PARENT_LEDGER.md` · `RESULT_V1.json` ·
`ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` · `MANIFEST_V1.json`
