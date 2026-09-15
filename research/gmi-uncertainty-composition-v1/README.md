# GMI uncertainty composition V1

Child issue: #759. Parent ledger: #602 Section M.

This capsule handles uncertainty propagation through a finite acyclic composition graph while preserving dependence when it is registered.

Core distinction:

- **global feasible projection** retains one joint assignment relation across the graph and is exact for the registered finite contract;
- **local Cartesian propagation** keeps only one uncertainty set per node and is proved sound, but may widen when branches share ancestors.

The frozen dependency hostile is `a=x`, `b=x`, `y=a-b` with `x in {-1,+1}`: global output `{0}`, local output `{-2,0,+2}`.

Artifacts:

- `FREEZE_V1.md` — pre-implementation authority;
- `FORMALIZATION_V1.md` — UC-1..UC-5 proofs, counterexamples and scope;
- `uncertainty_composition_v1.py` — exact finite/rational executor;
- `test_uncertainty_composition_v1.py` — exact/adversarial controls;
- `RESULT_V1.json` — deterministic receipt.

Claim ceiling: `DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE`.

No probabilistic capability calibration or real-scale uncertainty claim is made here.
