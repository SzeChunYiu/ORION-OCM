# Issue #602 — capability contract V1

This lane closes the **registration/specification** work in #602 A4 and F1 without claiming empirical capability results.

Files:

- `CAPABILITY_CONTRACT_V1.json` — common information, metric, twin, parent and resource definitions plus shard manifest.
- `CAPABILITIES_01.json` .. `CAPABILITIES_03.json` — the exact 27 A4 capability rows.
- `CAPABILITY_COORDINATES_V1.json` — the exact 17 F1 capability coordinates.
- `FORMALIZATION.md` — mathematical objects, proofs, decision rule and claim boundaries.
- `validate.py` — dependency-free structural verifier.
- `../../tests/test_capability_contract_v1.py` — adversarial mutation tests.

Run from repo root:

```bash
python3 research/capability-contract-v1/validate.py
python3 -m pytest -q tests/test_capability_contract_v1.py
```

The validator must print:

```text
CAPABILITY_CONTRACT_V1: VALID (27 capabilities, 17 coordinates)
```

## Claim ceiling

`G1`. The artifact makes every A4 row and every F1 coordinate machine-readable and falsifiable. It does not establish that any system possesses the capability and does not establish G6 morphology-to-capability prediction.

## Evidence rule

The strongest registered parent gets first refusal under the same declared information/resource envelope. A positive-world advantage must be accompanied by collapse of the candidate-minus-parent margin in a one-dependency negative twin. Information leakage, unmatched resource spending, parent non-separation, failed twin collapse, or protected-remint failure falsifies the corresponding empirical claim.
