# GMI capability ceilings V1 — #602 F2 tranches 1–2

This unit binds six classical lower-bound families into the architecture-independent GMI capability contract at deliberately bounded exact scope:

1. state capacity -> zero-error memory distinction ceiling;
2. complete observation quotient -> zero-error task distinguishability ceiling;
3. fixed-bit one-way communication -> zero-error coordination ceiling;
4. fixed-architecture finite precision -> representable threshold-boundary ceiling;
5. finite persistent-update alphabet -> target-state plasticity/reachability ceiling;
6. protected-output rank -> exact retention/plasticity null-space frontier.

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

The precision theorem intentionally freezes architecture and its boundary decoder. Low per-parameter precision is **not** claimed to impose a universal architecture-independent expressivity ceiling when width/depth or other parameter channels may change.

Claim ceiling: **G2**. These are bounded theorem-level capability ceilings, not a G6 morphology-to-capability predictor.
