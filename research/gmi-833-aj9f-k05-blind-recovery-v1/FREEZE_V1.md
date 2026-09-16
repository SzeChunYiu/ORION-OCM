# AJ9f blind compositional-state freeze

This freeze predates solver implementation, outcome, and post-hoc K05 adjudication.

- AJ9a benchmark Git blob: `6b9ac3095c90d74e2717671a70ad7cc18955310c`.
- Generic environment/search config commit: `d2bf5139499e84856ed8e7219d3bb2dea23d8a5b`.
- The task exposes a finite compositional data type, two legal local environment transformations, a start and a goal. Those are task laws, not a supplied solver architecture.
- Search/evaluation receives no family label/fingerprint, symbolic-solver/theorem-prover/rewrite-engine macro, or family score.
- Two generic graph/path procedures and two data presentations are registered before outcomes.
- Blind outcome is frozen before benchmark-family access.

No pre-search morphology-selection prediction is registered; `PREDICTED_SELECTED` is unavailable in this tranche.
