# Section Z, lane `sec-z3` — issue-comment reconciliation

`ISSUE_833_COMMENT_RECONCILIATION_V1.json`, schema
`GMI_ISSUE_COMMENT_RECONCILIATION_V1`, for issue comment `5684819296` of
SzeChunYiu/ORION-OCM#833.

**The issue comment and the issue body are not edited by this lane.** The
orchestrator does all issue writes; this is the machine-readable proposal.

## Accounting

| | rows |
|---|---:|
| already `- [x] ` in the live body at the fetch below | `32` |
| closed by this lane | `14` |
| not closed, with a reason each | `85` |
| **total** | **`131`** |

The `14`: `Z2` rows 1-5, `Z6` rows 1-6, `Z4` rows 2, 3 and 5.

## Custody of the `old` strings

Every `anchor` and every `old` is byte-exact from a fetch taken immediately
before this file was finalized:

```
sha256 5be745ee8ccdf3a96636550ad0782409f83d04fb9c4586b446ff1072bee8bdf9
26485 bytes, 99 unchecked rows, 32 checked rows
```

`COMMENT_5684819296_SNAPSHOT_V1.md` is that fetch, byte for byte.
`check_reconciliation_v1.py` re-verifies offline that the snapshot's sha256
matches, that every `old` occurs **exactly once in the whole body and exactly
once under its own `###` anchor**, that every `old` is an unchecked row and
every `new` is its checked form with an appended evidence clause, that no row
appears in two entries, and that the three counts sum to `131`.

The checker is validated rather than trusted: five planted defects — a
duplicated row, a stripped evidence clause, a missing `comment_id`, a wrong
snapshot digest, and a `new` that was never checked — each make it exit `1`
with a matching message, and the clean file exits `0`.

## The 32 already-checked rows

`Z12` (9) and `Z15` (6) came from PR #1026, which is merged. `Z3` (5), `Z5` (6)
and `Z7` (6) — **17 rows** — are ticked in the live comment while their packages
live on branch `research/833-sec-z2` in **PR #1034, which is open and not merged
at this lane's `source_main`**. This lane neither re-closes nor re-counts them,
and the note is in the JSON so that an auditor does not read the `32` as double
counting.

## Reproduce

```bash
python3 -I -B research/gmi-833-z-sec-z3-reconciliation-v1/check_reconciliation_v1.py
```
