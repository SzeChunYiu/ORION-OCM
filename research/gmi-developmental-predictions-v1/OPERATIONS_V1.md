# Operations — Developmental Predictions V1

## Run controls

```bash
cd research/gmi-developmental-predictions-v1
python3 -I -B test_developmental_predictions_v1.py -v
python3 -I -O -B test_developmental_predictions_v1.py -v
```

Expect **23** tests OK.

## Summary dump

```bash
python3 -I -B developmental_predictions_v1.py
```

## Off-Mac receipt hosts

- `billy-old` (Python 3.14.x) normal + optimized
- `billy-laptop` / `laptop-billy` (Python 3.8.x) normal + optimized

Record results in `PREDICTIONS_RECEIPT_V1.json`.

## Falsify

Edit a gate or the held-out registry and re-run; a mismatch or refused
invariant fails the suite.
