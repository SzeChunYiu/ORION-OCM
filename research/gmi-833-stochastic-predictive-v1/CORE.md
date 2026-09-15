# gmi-833-stochastic-predictive-v1

Bounded #836 / #833 stochastic-derivation tranche for exact finite predictive rows, minimum exact linear predictive dimension, and latent-realization non-identifiability.

## Scope

- finite controlled stochastic processes with exact rational kernels;
- positive-probability histories only for conditional predictive rows;
- complete finite controlled-test family through a registered residual horizon;
- predictive-row quotient, with #846 retained as strongest owner of quotient sufficiency/cardinality minimality;
- exact system-dynamics rank lower bound and rank-attaining core-test factorization;
- explicit separation between number of predictive classes and linear predictive dimension;
- observable predictive-law collision showing latent realization/cardinality is not identified without extra assumptions;
- additive gap-graph overlay, validated against the central graph, with explicit OPEN stronger gaps for measurable/infinite, approximate, finite-sample, and causal-latent scope.

## Reproduce

```bash
python3 -I -B research/gmi-833-stochastic-predictive-v1/test_stochastic_predictive_v1.py -v
python3 -I -O -B research/gmi-833-stochastic-predictive-v1/test_stochastic_predictive_v1.py -v
python3 -I -B research/gmi-833-stochastic-predictive-v1/stochastic_predictive_v1.py
```

The canonical executor must byte-match `RESULT_V1.json` in both interpreter modes.

The receipt also records two independently implemented exact rank certificates: rational Gaussian elimination and maximum nonzero determinant/minor.

Claim ceiling: `GMI_FINITE_PREDICTIVE_BLOCK_LINEAR_DIMENSION_AT_REGISTERED_HORIZON`.

This package formalizes/revalidates parent mathematics; it does not claim a novel PSR rank theorem, infinite-horizon/measurable closure, finite-sample identification, causal latent identification, or #833 closure.
