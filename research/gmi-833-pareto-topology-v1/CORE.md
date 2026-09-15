# gmi-833-pareto-topology-v1

This tranche lifts morphology transform burden from one scalar back to the primary Pareto frontier of nonnegative semantic/resource vectors. Finite Pareto choice and sequential Minkowski composition form the exact path algebra used for multiobjective transform closure. Frozen positive scalarizations recover directed Lawvere-style pseudometrics but are information-losing projections.

Strict positive vector-budget balls satisfy the forward-basis refinement theorem and generate a topology. A one-way zero-burden transform demonstrates that the topology need not be symmetric, T1, Hausdorff, or manifold-like.

Reproduce:

```bash
python -I -B research/gmi-833-pareto-topology-v1/test_pareto_topology_v1.py -v
python -I -O -B research/gmi-833-pareto-topology-v1/test_pareto_topology_v1.py -v
python -I -B research/gmi-833-pareto-topology-v1/pareto_topology_v1.py
```

Claim ceiling: `GMI_PARETO_TRANSFORM_ALGEBRA_AND_FORWARD_TOPOLOGY_AT_REGISTERED_FINITE_SCOPE`.
