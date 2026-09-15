# gmi-833-remint-equivariance-v1

This tranche formalizes finite semantic presentation remints as bijective state-label transports, proves identity/inverse/composition, proves canonical mechanism fingerprints invariant under valid remints, and checks quotient-level directed transform geometry is unchanged when all endpoint presentations are reminted with burdens fixed.

Neutral-looking semantic mutations are hostile failures. Search/reachability invariance is explicitly not inferred from semantic remint invariance.

Reproduce:

```bash
python -I -B research/gmi-833-remint-equivariance-v1/test_remint_equivariance_v1.py -v
python -I -O -B research/gmi-833-remint-equivariance-v1/test_remint_equivariance_v1.py -v
python -I -B research/gmi-833-remint-equivariance-v1/remint_equivariance_v1.py
```

Claim ceiling: `GMI_FINITE_SEMANTIC_REMINT_EQUIVARIANCE_AT_REGISTERED_SCOPE`.
