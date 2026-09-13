# Value of computation: read first

The [corrected VOC-1–6 proof](VALUE_OF_COMPUTATION_THEOREM_V1.md) supplies
finite deterministic stopping values with explicit feasibility and charged
continuation.

- Rank exhaustion is distinct from successfully serving the obligation.
- Positive edge costs give unique finite values on the viable domain;
  other states remain infeasible.
- The certified-cost step bound is deterministic/pathwise. Expected-cost
  stochastic processes require a different statement.
- Full lookahead can improve on myopia; common safety does not settle cost.
- Stop-on-ties is a declared optimal convention; exact argmins use exact signs.

[Model](value_of_computation_model_v1.py) →
[focused tests](test_value_of_computation_v1.py) →
[graph controls](test_value_of_computation_graphs_v1.py) →
[context and receipt](VOC_REPAIR_CONTEXT_V1.md).

Original PR571 source and successful historical controls are retained separately.
This is a corrected finite-model result, not a claim that the parent review's
implementation, general termination, verification or full-cost obligations
have all been discharged. No grand checker or aggregate is changed here.
