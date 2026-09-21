# Reproduction

Stdlib only. No third-party imports, no network, no real source required; all
claimed quantities are exact integers and are produced by the committed
checker.

```
python3 -I -B independent_oracle_v1.py     # route B, source-separated oracle
python3 -I -B tranche_d_v1.py              # route A, eleven-coordinate ledger
python3 -I -B test_tranche_d_v1.py -v
python3 -I -O -B test_tranche_d_v1.py -v
```

## What the receipts say

- `RESULT_V1.json` — the nine-row gate ledger. Each row carries ten finite-scope
  coordinates (`R01`–`R10`) supported at one `sigma` and `R11` open
  (`OPEN_REAL_SCALE_PENDING`), so no row is closed and the issue checkboxes stay
  unchecked.
- `ORACLE_RESULT_V1.json` — the source-separated oracle reproduces all nine
  recovered classes and costs (`all_classes_match = true`, all twins rejected).
- `ISSUE_833_RECONCILIATION_H_TRANCHE_D_V1.json` — schema
  `GMI_ISSUE_RECONCILIATION_V2`, `replacements: []`, the nine rows recorded open
  with per-row attribution (`supported_gates: 10`, open gate `R11`).
