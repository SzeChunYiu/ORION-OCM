# AJ9b blind generic-search freeze

This freeze predates the holdout generator implementation, candidate outcome, and post-hoc family adjudication for this tranche.

- AJ9a known-family benchmark Git blob: `6b9ac3095c90d74e2717671a70ad7cc18955310c`.
- Generic search configuration freeze commit: `42fb250c9b139e8fed51c8882cbfc3d9879f6420`.
- The search/evaluator may use only the task observations, generic primitives, exact behavioral requirement, raw resource vector, and registered search budgets in `SEARCH_CONFIG_V1.json`.
- The search/evaluator must not read the benchmark, family IDs/names, post-hoc fingerprints, or any architecture-specific macro/property vector.
- The outcome before adjudication is only generated candidate expressions plus protected I/O and raw resource measurements.
- Post-hoc adjudication may read the frozen AJ9a registry only after the search result is frozen.

This tranche is allowed to earn `RECOVERED` or `NOT_RECOVERED_AT_SCOPE`. It does **not** preregister an architecture-name-free morphology-selection prediction, so it cannot earn `PREDICTED_SELECTED`.

The frozen primitive basis is intentionally weak and generic: two inputs, constants -1/0/1, addition, negation and a positive-value test. No unit, layer, weight-matrix, activation, network, family, or target-morphology macro is supplied.
