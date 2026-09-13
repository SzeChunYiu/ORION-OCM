# Stochastic proper stopping

For a supplied finite rational MDP with nonnegative scalar costs, construct
one deterministic stationary policy that minimizes expected cost and then
expected actions among proper policies, simultaneously on every viable state.

- [Proof](STOCHASTIC_PROPER_STOPPING_THEOREM_V1.md): viable-domain extraction,
  SSP perturbation reduction, joint attainment and a finite J/L progress certificate.
- [Parent subtraction and full-cost scope](PARENTS_AND_SCOPE_V1.md):
  inherited SSP theory, not a new optimality law or free model acquisition.
- [Exact constructor and independent flow oracle](ALGORITHM_AND_ORACLE_V1.md).
- [Complete finite receipt](RECEIPT_V1.json) binds the source, parent files,
  exact witnesses, full checker output and normal/optimized test results.

Zero-cost loops remain legal, but a scalar Bellman tie is insufficient:
the returned certificate establishes finite expected termination. A geometric
policy can be proper while its possible execution lengths remain unbounded.
No campaign, native capability or universal physical optimum is asserted.

Run the focused tests with explicit CPython3.12 and isolated imports:
`python3 -I -B test_stochastic_stopping_v1.py` (also `-O`).
The standalone checker is `python3 -I -B stopping_checks_v1.py`.
