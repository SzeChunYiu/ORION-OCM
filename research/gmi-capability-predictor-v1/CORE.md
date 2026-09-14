# Capability predictor (F4) — descriptor frozen before outcomes, held-family prediction

Brand-free morphology descriptor + capability predictor spec for #602 F4. **Spec only, ceiling G1** — no G6 predictor claim.

- Spec: [`CONTRACT_V1.json`](CONTRACT_V1.json) + [`SCHEMA_V1.json`](SCHEMA_V1.json)
- Descriptor: [`DESCRIPTOR_V1.md`](DESCRIPTOR_V1.md) (8 fields: state carrier, operators, control/update, memory org, comm, verification, development law, resource profile)
- Predictor: [`PREDICTOR_INTERFACE_V1.md`](PREDICTOR_INTERFACE_V1.md) — `Cap(D,E,R,H) → 27×Distribution + abstention`
- Math: [`FORMALIZATION_V1.md`](FORMALIZATION_V1.md)
- Falsifiers: [`FALSIFIERS_V1.md`](FALSIFIERS_V1.md) — 3 cheapest single-command checks; which of 11 F4 boxes each closes; which need a frozen campaign
- Executable: [`capability_predictor_v1.py`](capability_predictor_v1.py) → [`test_capability_predictor_v1.py`](test_capability_predictor_v1.py)

No registry row or capsule digest added — Lane A owns registry this turn.
