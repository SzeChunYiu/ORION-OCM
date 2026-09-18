# Prospective freeze — finite Pareto-front density v1

- Parent issue: #833
- Child issue: #994
- Source `main`: `883d13e852fa3904d202b5cae1aee474e0a12dfb`
- Frozen parent result: `research/gmi-833-finite-candidate-space-v1/RESULT_V1.json`
- Frozen parent blob: `4086d6bea440d626e48d92eb35d39267a010589e`
- Claim ceiling: `GMI_833_FINITE_PARETO_DENSITY_AT_REGISTERED_G0_SCOPE`

This package will address exactly the Section-F row “Measure Pareto-front
density.” It will use the complete `G0-fin-v1` spaces at cumulative budgets
`(1,1)`, `(2,1)`, `(1,2)`, and `(2,2)` and the frozen protected interface
`(), (0,), (1,)` with step cap 6.

Morphology identity is the pair of the complete protected observation table and
the raw `(code_cells, register_cells)` resource vector. The preregistered
objective vector maximizes: (1) the count of probes that halt, (2) the count of
nonempty probes whose complete output equals the input word, and (3) the count
of probes with nonempty output. It separately minimizes both raw resource
coordinates. No scalarization is permitted.

The exact frontier cardinalities and densities were not inspected before the
issue freeze. The result is conditional on this finite grammar, budget,
interface, and explicit evaluation prior. It cannot establish universal
Pareto density, objective neutrality, scalable coverage, reachability,
clustering, family recovery, an unbounded result, or complete GMI.
