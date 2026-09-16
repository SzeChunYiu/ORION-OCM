# AJ9e blind Boolean-control freeze

This freeze predates search implementation, outcome, and post-hoc K04 adjudication.

- AJ9a benchmark Git blob: `6b9ac3095c90d74e2717671a70ad7cc18955310c`.
- Generic search config commit: `21e9976ab4c14bc1f9189ab391b7b99bc6ab62b5`.
- Search/evaluation sees only all eight `(c,a,b)` Boolean inputs, the exact required output `a if c=0 else b`, generic NOT/AND/OR, raw complexity coordinates, and two generic synthesis procedures.
- No family label/fingerprint, attention/routing/selector/multiplexer macro, family-specific score, or post-outcome classifier feedback is available.
- Blind outcome is frozen before any benchmark-family access.

No pre-search morphology-selection prediction is registered, so this tranche cannot earn `PREDICTED_SELECTED`.
