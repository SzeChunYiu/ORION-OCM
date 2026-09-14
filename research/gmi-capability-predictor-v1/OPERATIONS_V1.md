# Capability predictor V1 — operations

Run structural checks (no network, no sampling, CPython 3.8 safe):

```bash
python research/gmi-capability-predictor-v1/capability_predictor_v1.py
python -m pytest research/gmi-capability-predictor-v1/test_capability_predictor_v1.py -v
```

Toy falsifiers:

- Fz1 (remint + brand-free): covered by `capability_predictor_v1.py`'s `check_toy_remints` + brand check.
- Fz2 (price-flip + ablation): `python research/gmi-capability-predictor-v1/scripts/fz2_price_ablation_toy.py` — reference implementation sketched in `FALSIFIERS_V1.md`; not shipped as runnable until next iteration.
- Fz3 (abstention on UNSEEN_SYMBOL): `python research/gmi-capability-predictor-v1/scripts/fz3_abstention_toy.py` — same.

Do NOT add a registry row or capsule digest this turn — Lane A owns registry. This skeleton earns no G6 box.
