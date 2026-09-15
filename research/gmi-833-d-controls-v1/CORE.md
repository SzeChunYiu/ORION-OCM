# gmi-833-d-controls-v1

Bounded #859 / #833-D execution-control tranche.

This package requires and executes four derivation robustness controls:

- matched mechanism-removal twins with nuisance/search capacity held fixed;
- semantics-preserving alternate encodings;
- distinct certified search procedures;
- raw Pareto analysis plus multiple positive resource scalarizations.

It imports the merged #855 no-smuggling auditor and requires both compared twin arms to be clean/evaluable there.

## Reproduce

```bash
python3 -I -B research/gmi-833-d-controls-v1/test_d_controls_v1.py -v
python3 -I -O -B research/gmi-833-d-controls-v1/test_d_controls_v1.py -v
python3 -I -B research/gmi-833-d-controls-v1/d_controls_v1.py
```

Claim ceiling: `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`.
