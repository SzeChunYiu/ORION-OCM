# Exact sparse donor API

Use the existing pinned environment; this change adds no dependency installation:
`/home/billy/orion-director-work/20260906/g1-env/bin/python`.
SymPy 1.14.0 and the actual QQ backend are bound in BINDINGS.json.

## Numerical API

```python
from exact_sparse_donor import fixed_point, solve_checked
values = fixed_point(ks, seed, alpha, revoked=revoked, relevance=None, mode=mode)
values, receipt = solve_checked(ks, seed, alpha, revoked=revoked, mode=mode)
```

Both retain the existing fixed_point keyword contract, including optional matrix.
The full dict retains KS ID order and Fraction values, including zero coordinates.
Unsupported optional routes delegate to the captured original function.
Supported calls return EXACT_ZERO only after the independent original residual passes.
Failures are exceptions; a missing/failed check is never a zero residual.
The candidate does not truncate outputs, infer positivity or clip coefficients.

## Consumer API and untimed native control

```python
from exact_sparse_donor_consumer import evaluate
record = evaluate(ks, task, operators, arm="reference", revoked=revoked,
                  config=config, commit_authority=authority)
```

Use arm="sympy" for the candidate. The exact same SV.solve and full operator
catalogue remain responsible for selection, execution, checking and commitment.
The caller supplies trusted live bindings; this module introduces no checker loader.

Result keys: arm, consumer, vectors, surprise, checks, stage_counts,
logical_fixed_point_calls, performance_authority, runtime_work_proxy.
consumer includes status/decision/answer/committed/trace/witness/gap_hook.
Each vector includes mode/seed/alpha/revoked/full values.
Candidate navigation checks include route, donor_solve_calls, coefficient_nnz,
rhs_nnz, checker_dense_cells, full_output_entries and independent_residual.
Original traces/resources are retained without pretending their work proxy measures
the adopted solver. There are no comparative timers in these modules.

```sh
PYTHONPATH=src:research/ocm-prototype /home/billy/orion-director-work/20260906/g1-env/bin/python -m exact_sparse_donor_consumer --arm sympy --fixture base
```

Named fixtures are base/incoming/mixed_warrant/alternative. This is a tiny development
control, not the actual G1 trial. The frozen G1 supervisor can call evaluate using
the separately bound fixed context loader. Do not dynamically load arbitrary code.

## Semantics and resource boundaries

Temporary module patching follows the existing research adapter and is restricted
to one isolated, single-threaded call. It is restored on exceptions.
SymPy has no subprocess here; full process/cold/warm/resource boundaries belong to
the separately registered supervisor. Do not import unused candidate dependencies
in the reference arm. Independent parity grading is external to both measured arms.

The real CLIA callable emits consumer.answer.application_wall_s.
Its separate fixed checker receipt emits check_wall_s; trusted binding emits
bind_wall_s outside evaluate. Preserve these raw fields. Any parity exclusion must
name their exact worker JSON paths prospectively. No recursive clock stripping,
clock-derived identity rewriting or expected-answer injection is implemented.

Official adopted API:
- https://docs.sympy.org/latest/modules/polys/domainmatrix.html#sympy.polys.matrices.domainmatrix.DomainMatrix.from_dod
- https://docs.sympy.org/latest/modules/polys/domainmatrix.html#sympy.polys.matrices.domainmatrix.DomainMatrix.solve_den
RREF may use dense internal operations; sparse storage does not certify transient
sparsity. The original dense residual remains part of candidate deployment cost.
