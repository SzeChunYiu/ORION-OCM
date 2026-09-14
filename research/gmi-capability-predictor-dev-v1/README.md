# GMI capability predictor — development-only v1

This capsule closes one bounded prerequisite in #602 F4: **fit/derive the capability predictor only from development worlds**.

It depends on the architecture-name-free morphology descriptor in `research/gmi-morphology-descriptor-v1/`. The fit corpus is generated deterministically from the finite five-margin cube `{-1,0,1}^5` and contains 243 development worlds. The fitter rejects family names, specimen/source identifiers, held-family flags, held-out outcomes and test outcomes.

The predictor is deliberately conservative. It uses monotone lower/upper witnesses and returns `CANNOT_IDENTIFY` when the development corpus does not order-identify the requested capability. On the registered development cube it exactly replays all four registered capability targets.

Files:

- `DEV_PREDICTOR_PROTOCOL_V1.json` — scope, fit boundary, targets, strongest parent and falsifier.
- `FORMALIZATION_V1.md` — soundness and exact-replay proofs.
- `dev_predictor_v1.py` — deterministic development-world generator and monotone-envelope predictor.
- `test_dev_predictor_v1.py` — exhaustive replay, anti-leakage, monotonicity mutation and abstention controls.

Claim ceiling: **G2**. This is not a held-family test and does not establish the G6 morphology-to-capability map.
