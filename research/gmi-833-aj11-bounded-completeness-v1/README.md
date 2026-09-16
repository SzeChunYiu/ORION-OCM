# gmi-833-aj11-bounded-completeness-v1

Reproduce the complete finite atlas:

```bash
python3 -I -B research/gmi-833-aj11-bounded-completeness-v1/check_aj11.py
python3 -I -O -B research/gmi-833-aj11-bounded-completeness-v1/check_aj11.py
```

The checker regenerates `ATLAS_V1.json` with all 260 presentation rows and verifies canonical compact SHA-256 `09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed`.

`COMPLETE_GMI_ATLAS_AT_BOUND_B` is permitted only for this frozen finite scope. The package explicitly forbids unbounded complete semantic classification.