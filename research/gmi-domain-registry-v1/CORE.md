# GMI domain registry v1

Issue #602 J1 infrastructure for D1–D8.

The formal statement and proof are in
`DOMAIN_REGISTRY_THEOREM_V1.md`. The machine-readable source of truth is
`DOMAIN_REGISTRY_V1.json`; its 64-cell directed reduction matrix is
`REDUCTION_MATRIX_V1.json`. Component, neutral-grammar, and protected-receipt
schemas live beside them.

Run:

```bash
python3 domain_infrastructure_v1.py
python3 -m unittest -v test_domain_infrastructure_v1.py
```

Expected terminal:

```text
GMI_DOMAIN_REGISTRY_V1_VALID
domains=8
matrix_cells=64
burden_classes=4
grammar_symbols=24
```

Claim ceiling: this closes infrastructure only. It does not certify a new
domain, completeness, irreducibility, or any off-diagonal reduction.
