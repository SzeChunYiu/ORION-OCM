# gmi-833-global-uncertainty-v1

Bounded #851 / #833-C foundation tranche for a typed global uncertainty/confidence interface, dependence-safe composition, and query-relative abstention.

## Scope

- five machine-distinct objects: feasible set, confidence set, predictive law, latent predictive model, selective prediction;
- exact relational images with dependence-safe union-bound confidence composition;
- exact global finite-DAG projection versus sound-but-looser local Cartesian propagation;
- missing relation = full registered target ignorance only for a nonempty upstream set;
- empty relation/upstream empty = inconsistency;
- missing target/query semantics = `CANNOT_CHECK`;
- `UNKNOWN` is maximal registered possibility, not checker failure;
- query identification is image-cardinality based and preserves confidence failure budget;
- marginal-only predictive laws cannot manufacture epistemic/aleatoric decompositions.

## Reproduce

```bash
python3 -I -B research/gmi-833-global-uncertainty-v1/test_global_uncertainty_v1.py -v
python3 -I -O -B research/gmi-833-global-uncertainty-v1/test_global_uncertainty_v1.py -v
python3 -I -B research/gmi-833-global-uncertainty-v1/global_uncertainty_v1.py
```

The canonical executor must byte-match `RESULT_V1.json` in both modes.

Claim ceiling: `GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE`.

This integrates parent-owned mathematics from #757/#759/#748/#750/#766; it does not promote finite registered-scope confidence to universal or real-world calibration.
