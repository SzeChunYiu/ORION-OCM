# Countable-row confidence corrigendum (ARC-6)

Corrects #655 / #602 M / #592 item 32. Read [the quantified theorem, retractions,
parents and boundaries](FORMALIZATION_V1.md) before using the numerical API.

```bash
python3 -I -B research/gmi-countable-row-corrigendum-v1/test_countable_rows_v1.py -v
python3 -I -O -B research/gmi-countable-row-corrigendum-v1/test_countable_rows_v1.py -v
```

General probability argument: written P1/P3, not proof-assistant checked.
24 exact/adversarial P2 controls. Local execution evidence is recorded separately
in `LOCAL_RECEIPT_V1.json`; the old ARC-5 multi-host receipt is historical and
is not reused as evidence for new code. No physical conditional-law validation,
empirical capability prediction or unbounded deployment guarantee is claimed.
