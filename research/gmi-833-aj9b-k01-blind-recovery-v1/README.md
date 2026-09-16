# gmi-833-aj9b-k01-blind-recovery-v1

Frozen blind-recovery microscope for the first registered AJ9 known-family holdout.

Reproduce after checkout:

```bash
python3 -I -B research/gmi-833-aj9b-k01-blind-recovery-v1/blind_search_v1.py
python3 -I -B research/gmi-833-aj9b-k01-blind-recovery-v1/posthoc_adjudicate_v1.py
python3 -I -B research/gmi-833-aj9b-k01-blind-recovery-v1/check_aj9b.py
python3 -I -O -B research/gmi-833-aj9b-k01-blind-recovery-v1/check_aj9b.py
```

The blind search source does not read the AJ9 family registry. `BLIND_OUTCOME_V1.json` is frozen before the post-hoc adjudicator is introduced. The post-hoc result is `RECOVERED` at the registered finite structural scope; learning and `PREDICTED_SELECTED` remain explicitly open.
