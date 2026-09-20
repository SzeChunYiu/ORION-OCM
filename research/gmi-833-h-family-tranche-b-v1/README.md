# Reproduction

Stdlib only. No third-party imports, no network, no real source required; all
claimed quantities are exact and are produced by the committed checker.

```
python3 tranche_b_v1.py               # route A, writes RESULT_V1.json
python3 independent_oracle_v1.py      # route B, source-separated oracle
python3 -m unittest test_tranche_b_v1.py -v
python3 -O -m unittest test_tranche_b_v1.py -v
```

## What the receipts say

- RESULT_V1.json — the nine-row gate ledger. Each row carries 10 finite-scope
  coordinates supported at one `sigma` and `R11` open, so `complete: false`
  and the row stays open with its single-stage attribution.
- The oracle reproduces the ledger's `independent_route_agrees = true`.
