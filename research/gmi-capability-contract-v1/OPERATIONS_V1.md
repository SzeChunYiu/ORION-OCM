# Capability contract: read first

This unit contains the 27-row A4 architecture-independent capability contract and the 17-coordinate F1 measurement registry. Both are scoped to G1 registration/specification. A4 cites the phenomenology atlas and per-row parents; F1 fixes coordinate semantics, reporting contracts, strongest parents, falsifiers, Pareto/resource rules and the bounded independent-unit assay.

Run from this unit directory:

```sh
python3 -I -B test_capability_contract_v1.py -v
python3 -I -B test_f1_coordinates_v1.py -v
python3 -I -O -B test_capability_contract_v1.py -v
python3 -I -O -B test_f1_coordinates_v1.py -v
```

The test entrypoints compile sibling models from source; no network is required and the code remains CPython 3.8 compatible.

The F1 Hoeffding gate is valid only for bounded independent evaluation units. Repeated/adaptive dependent rows are explicitly outside this unit and remain governed by #602 section M.
