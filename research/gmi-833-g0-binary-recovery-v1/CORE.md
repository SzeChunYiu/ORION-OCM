# gmi-833-g0-binary-recovery-v1

First tiny P3-relative mechanism-property recovery tranche for #833.

Two syntactically disjoint functionally complete low-level Boolean grammars (NAND-only and NOR-only) expose only variable wires plus an optional generic one-bit persistent state cell. Exhaustive semantic search recovers the same unique stateful mechanism for one-step delayed copy, while a matched state-removed grammar is impossible and an identity-task control selects the stateless solution despite state being available.

This is architecture-prior-free only relative to the explicit P3 disclosure and finite binary scope. It is not the final universal `G0`, broad grammar neutrality, or known-form closure.

Reproduce:

```bash
python -I -B research/gmi-833-g0-binary-recovery-v1/test_g0_binary_recovery_v1.py -v
python -I -O -B research/gmi-833-g0-binary-recovery-v1/test_g0_binary_recovery_v1.py -v
python -I -B research/gmi-833-g0-binary-recovery-v1/g0_binary_recovery_v1.py
```

Claim ceiling: `GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE`.
