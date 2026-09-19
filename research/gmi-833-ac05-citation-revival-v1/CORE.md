# CORE — `gmi-833-ac05-citation-revival-v1` (issue #833, row AC05)

**Row.** `- [ ] Maintain citation-backed definitions rather than model-generated definitions.`
(comment 5684607872, section AC). Read as: every crosswalk definition row
carries an in-place, verified, supporting citation.

**Result.** 48/48 rows of
`research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` now
carry, in their own citations cell, a primary anchor marked
`VERIFIED-2026-09-19` under the four-clause rule frozen in `FREEZE_V1.md`
§4 (identifier resolves — HTTP status recorded; Crossref/record metadata
matches; the cited text states the definition — ≤15-word passage with
locator; in place). The eight rows the prior proxy found unbacked (16, 19,
21, 23, 34, 41, 47, 48) are backed in place; row 48 cites its programme-
internal primary source (template @ `acb38c8b`, kinds verbatim from issue
row AC07) with Hempel & Oppenheim 1948 retired as non-supporting; row 1's
Harel venue is corrected to *Computer* 25(1), doi:10.1109/2.108047. Named
results: `AC05_THEOREMS_V1.md` (AC05-1 … AC05-4). Register:
`CITATION_VERIFICATION_V1.json` (per anchor: identifier, resolution URL +
HTTP status + date, metadata match, passage, locator, route, role).

**Claim ceiling.** `CITATION_BACKED_DEFINITIONS_IN_PLACE_VERIFIED_V1`. Not
claimed: earliest parents, saturation, definitional correctness, AC02 /
AC07 / AC08 / AC09.

**Gate.** Closure of AC05 is decided by the fresh proxy verdict recorded in
`ISSUE_833_RECONCILIATION_AC05_V1.json` (`HUMAN_GATE_BYPASSED__MODEL_PROXY`)
together with the 48/48 structural check.

## Reproduce (stdlib only, no network; from the repo root)

```
python3 -I -B research/gmi-833-ac05-citation-revival-v1/ac05_citation_check_v1.py      # route A
python3 -I -B research/gmi-833-ac05-citation-revival-v1/independent_ac05_oracle_v1.py  # route B
python3 -I -B research/gmi-833-ac05-citation-revival-v1/test_ac05_citation_check_v1.py
python3 -I -O -B research/gmi-833-ac05-citation-revival-v1/test_ac05_citation_check_v1.py
python3 -I -B research/gmi-833-ac05-citation-revival-v1/build_receipt_v1.py            # receipt matches
```

Expected: `passing_rows: 48`, `failing_rows: []`, 7/7 hostiles applicable
and detected, null 120/120 primary deletions caught over 200 draws, routes
agree on every row, `ALL PASS` (both modes), `receipt matches the live
two-route run`.

## Files

| file | role |
|---|---|
| `FREEZE_V1.md` | pre-implementation freeze: pins, rule, rows, hostiles, forbidden promotions |
| `CITATION_VERIFICATION_V1.json` | the register (48 rows, 90 anchors) |
| `ac05_citation_check_v1.py` / `independent_ac05_oracle_v1.py` | route A / route B |
| `test_ac05_citation_check_v1.py`, `build_receipt_v1.py`, `RESULT_V1.json` | tests and receipt |
| `AC05_THEOREMS_V1.md`, `PARENT_DISCLOSURE_V1.md`, `MANIFEST_V1.json` | named results, parents, pins |
| `ISSUE_833_RECONCILIATION_AC05_V1.json` | reconciliation (schema `GMI_ISSUE_COMMENT_RECONCILIATION_V1`) + proxy verdict verbatim |
| `../gmi-833-ac-lanes-harness-v1/AMENDMENT_01_ADDENDUM_MERGED_V1.md` | addendum merged; harness re-pinned to its frozen blob |

Workflow: `.github/workflows/gmi-833-ac05-citation-revival-v1.yml`
(ubuntu-latest; structural only — resolution is dated, never re-run in CI).
