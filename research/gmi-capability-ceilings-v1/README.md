# GMI capability ceilings V1 — #602 F2 tranche 1

This unit binds three classical lower-bound families into the architecture-independent GMI capability contract at a deliberately bounded scope:

1. state capacity -> zero-error memory distinction ceiling;
2. complete observation quotient -> zero-error task distinguishability ceiling;
3. fixed-bit one-way communication -> zero-error coordination ceiling.

Artifacts:

- `F2_CEILINGS_V1.json` — machine-readable theorem registry with scope, assumptions, parents, twins and falsifiers.
- `FORMALIZATION_V1.md` — parent subtraction and formal proofs.
- `capability_ceilings_v1.py` — registry validator plus exact finite witnesses.
- `test_capability_ceilings_v1.py` — exact and hostile scope controls.
- `STATUS.md` — claim boundary.

Run from repository root:

```bash
python3 -I -B research/gmi-capability-ceilings-v1/test_capability_ceilings_v1.py -v
python3 -I -O -B research/gmi-capability-ceilings-v1/test_capability_ceilings_v1.py -v
```

Claim ceiling: **G2**. These are bounded theorem-level capability ceilings, not a G6 morphology-to-capability predictor.
