# gmi-833-robustness-controls-v1

Bounded #863 / #833-D governance-and-evidence tranche for four required derivation robustness controls:

- matched mechanism-removal grammar twins;
- semantics-preserving alternate encodings/remints;
- materially distinct alternate search algorithms;
- raw Pareto analysis plus distinct positive resource scalarizations.

The package deliberately separates **control compliance** from **scientific robustness**. A valid control may reveal sensitivity and still satisfy the protocol requirement.

Reproduce:

```bash
python3 -I -B research/gmi-833-robustness-controls-v1/test_robustness_controls_v1.py -v
python3 -I -O -B research/gmi-833-robustness-controls-v1/test_robustness_controls_v1.py -v
python3 -I -B research/gmi-833-robustness-controls-v1/robustness_controls_v1.py
```

Claim ceiling: `GMI_DERIVATION_ROBUSTNESS_CONTROL_REQUIREMENTS_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`.
