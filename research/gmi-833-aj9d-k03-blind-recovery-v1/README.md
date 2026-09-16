# gmi-833-aj9d-k03-blind-recovery-v1

Frozen blind-recovery microscope for registered AJ9 family K03.

```bash
python3 -I -B research/gmi-833-aj9d-k03-blind-recovery-v1/blind_site_search_v1.py
python3 -I -B research/gmi-833-aj9d-k03-blind-recovery-v1/posthoc_adjudicate_v1.py
python3 -I -B research/gmi-833-aj9d-k03-blind-recovery-v1/check_aj9d.py
python3 -I -O -B research/gmi-833-aj9d-k03-blind-recovery-v1/check_aj9d.py
```

The blind search starts from unrestricted global Boolean output functions; locality/sharing are not supplied. The scoped terminal is `RECOVERED`; training, broad equivariance and `PREDICTED_SELECTED` remain open.
