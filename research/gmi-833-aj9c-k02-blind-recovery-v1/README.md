# gmi-833-aj9c-k02-blind-recovery-v1

Frozen blind-recovery microscope for registered AJ9 family K02.

Reproduce after checkout:

```bash
python3 -I -B research/gmi-833-aj9c-k02-blind-recovery-v1/blind_temporal_search_v1.py
python3 -I -B research/gmi-833-aj9c-k02-blind-recovery-v1/posthoc_adjudicate_v1.py
python3 -I -B research/gmi-833-aj9c-k02-blind-recovery-v1/check_aj9c.py
python3 -I -O -B research/gmi-833-aj9c-k02-blind-recovery-v1/check_aj9c.py
```

The blind search does not read the AJ9 family registry. `BLIND_OUTCOME_V1.json` is frozen before post-hoc adjudication. The scoped terminal is `RECOVERED`; recurrent learning and `PREDICTED_SELECTED` remain open.
