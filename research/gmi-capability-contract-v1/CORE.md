# Capability contract

Architecture-independent capability registration for #602 at claim ceiling **G1**.

The merged A4 contract contains 27 rows with
`inputs -> allowed_info -> required_behaviour -> success_metric -> resource_metric -> twin -> parent -> falsifier`.
The F1 extension registers the exact 17-coordinate capability vector, per-coordinate reporting contracts, strongest parents and falsifiers, plus a common bounded independent-unit assay.

This unit proves specification/measurement structure only. It does not prove empirical capability possession, reachability, universal ontology completeness, F2 capability ceilings, or a G6 morphology-to-capability predictor.

- A4: [contract](CONTRACT_V1.json) + [schema](SCHEMA_V1.json)
- A4 executable controls: [model](capability_contract_v1.py) -> [tests](test_capability_contract_v1.py) -> [receipt](CONTRACT_RECEIPT_V1.json)
- F1: [coordinates](CAPABILITY_COORDINATES_V1.json) + [assay](F1_ASSAY_V1.json)
- F1 mathematics: [formalization](FORMALIZATION_V1.md)
- F1 executable controls: [model](f1_coordinates_v1.py) -> [tests](test_f1_coordinates_v1.py)
