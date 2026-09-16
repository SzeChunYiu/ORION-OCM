# gmi-833-presentation-equivariance-v1 (internal identifier unchanged; paper-facing title below)

# GMI #833 finite semantic presentation-relabeling equivariance

This tranche formalizes finite semantic presentation relabelings (bijective state-label transports; the historical internal term is retired from paper-facing prose) as bijective state-label transports, proves identity/inverse/composition, proves canonical mechanism fingerprints invariant under valid relabelings, and checks quotient-level directed transform geometry is unchanged when all endpoint presentations are relabeled with burdens fixed.

Neutral-looking semantic mutations are hostile failures. Search/reachability invariance is explicitly not inferred from semantic presentation-relabeling invariance.

Reproduce:

```bash
PKG=$(ls -d research/gmi-833-presentation-equivariance-lane 2>/dev/null || ls -d research/gmi-833-*equivariance*v1)
python -I -B $PKG/test_remint_equivariance_v1.py -v
python -I -O -B $PKG/test_remint_equivariance_v1.py -v
python -I -B $PKG/remint_equivariance_v1.py
```

(The test/executor file names are frozen internal identifiers.)

Claim ceiling: `GMI_FINITE_SEMANTIC_REMINT_EQUIVARIANCE_AT_REGISTERED_SCOPE`.
