# GMI ecology contract V2 — issue #602 A2

This research unit closes the **registration/specification** part of #602 A2 at claim ceiling **G1**. It refines the earlier Track-B ecology contracts by making all A2 coordinates explicit and machine-checkable, including adaptive agents, social topology, embodiment, verifier economics, information-acquisition cost, protected splits, and remint equivalence.

Artifacts:

- `ECOLOGY_CONTRACT_V2.json` — exact 16-coordinate machine-readable registry.
- `FORMALIZATION_V2.md` — parent subtraction, formal ecology object, resource theorem, remint-equivalence theorem, leakage lemma, and structural-closure theorem.
- `ecology_contract_v2.py` — dependency-free validator plus finite remint witness.
- `test_ecology_contract_v2.py` — exact/adversarial controls.

Run from repository root:

```bash
python3 -I -B research/gmi-ecology-contract-v2/test_ecology_contract_v2.py -v
python3 -I -O -B research/gmi-ecology-contract-v2/test_ecology_contract_v2.py -v
```

Claim boundary: this establishes the registered environment object needed by later G5/G6/G7 work. It does **not** establish a morphology phase law, reachability, natural-cognition validity, or a universal environment ontology.
