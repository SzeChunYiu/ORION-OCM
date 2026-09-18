# derive-ag reconciliation (START HERE)

The proposal for four AG/AH comment checkboxes, produced by the `derive-ag` tranche. It writes
nothing to the issue: the orchestrator performs every issue write.

| row | comment | section | closed by |
|---|---|---|---|
| `14` | `5693520829` | AG3 | `gmi-833-ag3-presentation-equivalence-v1` |
| `19` | `5693520829` | AG4 | `gmi-833-ag4-formalism-translations-v1` |
| `41` | `5693520829` | AG7 | `gmi-833-emergence-conditions-v1` |
| `62` | `5693590252` | AH3 | `gmi-833-emergence-conditions-v1` |

One row is left open with its reason: AG0 row `1`.

## Three checks, all run, none assumed

1. **Live fetch.** Every `old` line comes from a fetch of the comment body taken immediately
   before the file was written, and is proved to occur **exactly once** inside its own `###`
   section and exactly once in the whole body. Other lanes are closing rows in these same
   comments while this tranche runs; a row already checked, or duplicated, would be caught here
   rather than reconciled blind.
2. **Custody cross-check.** Every `old` line is also compared against the pinned
   `AGAH_ROWS_V1.json` snapshot, so a row edited since the pin would show up as a mismatch.
3. **RA-1.** The citation admissibility auditor committed by the earlier AG lane is **imported
   and reused**, not reimplemented. It pins every cited receipt by git blob sha, verifies every
   cited field value byte-exactly, requires every cited receipt to be `GREEN`, and refuses a
   citation whose row meaning appears in the cited receipt's own forbidden set.

Result: `4` live-fetch checks clean, `0` RA-1 violations in all thirteen categories.

## Reproduce

```
gh api repos/SzeChunYiu/ORION-OCM/issues/comments/5693520829 --jq .body > /tmp/c_ag.txt
gh api repos/SzeChunYiu/ORION-OCM/issues/comments/5693590252 --jq .body > /tmp/c_ah.txt
python3 -I -B research/gmi-833-derive-ag-reconciliation-v1/build_reconciliation_v1.py \
  /tmp/c_ag.txt /tmp/c_ah.txt
```

## Files

`ISSUE_833_COMMENT_RECONCILIATION_V1.json` (the proposal) ·
`RECONCILIATION_AUDIT_V1.json` (the three checks) · `build_reconciliation_v1.py`.
