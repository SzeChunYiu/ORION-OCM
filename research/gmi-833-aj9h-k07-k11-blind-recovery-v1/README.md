# gmi-833-aj9h-k07-k11-blind-recovery-v1

Reproduce from repository root:

```bash
python3 -I -B research/gmi-833-aj9h-k07-k11-blind-recovery-v1/check_aj9h.py
python3 -I -O -B research/gmi-833-aj9h-k07-k11-blind-recovery-v1/check_aj9h.py
```

The freeze/config/bias ledger predate `blind_recovery_v1.py`. Generation/search/evaluation cannot read the AJ9a family registry. `posthoc_adjudicate_v1.py` reads the registry only after the blind outcome is fixed.

This closes the registered AJ9 family-recovery checklist only at the declared finite task/basis scopes. It does not assert historical-ignorance inevitability or universal family optimality.