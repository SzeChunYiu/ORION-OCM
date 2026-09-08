# What remains UNKNOWN

Unprobed layers stay UNKNOWN. This study does not fill them.

## Preserved by unlabeled diagnosis (exact)

On F1–F6 bound receipts and S11–S28 historical rows, M11 `diagnose()` with
empty ablations returns:

- `weights = {}`
- `minimum_sufficient = None`
- `unknown = {D0,…,D8}`

That is the existing rule in `src/ocm/selfmodel/diagnose.py`: a layer with no
ablation evidence stays UNKNOWN. Escalation is refused until more evidence is
gathered.

Self-evolution cycle files already record the same initial diagnosis before
paid probes. After probes, D0 and D2–D8 remain UNKNOWN; only D1 receives a
weight from catalogue counterfactuals. Cycle 2’s D1 weight is 0 and
`minimum_sufficient` is None.

## Missing traces (not reconstructed)

| Item | Status |
|---|---|
| F1 original A task/certificate/process records | UNKNOWN / absent |
| F1 FACTS.json | absent from this tree |
| F2/F3 individual method/query/re-index events | UNKNOWN |
| F4 individual dependency intervention calls | UNKNOWN |
| F5 per-probe observations and cached-parent row | UNKNOWN |
| F6 instance traces and counterfactual repairs | UNKNOWN |
| Unique root cause of F2 vs F3 | CANNOT_CHECK (shared receipt) |
| Unique historical cause of F3/F4 | not established by C1 sufficiency |
| Self-change κ on a real incident graph | CANNOT_CHECK |
| Ω = H(Z)/B_id(ε) on real probes | CANNOT_CHECK |
| χ = 2^H(R\|e) calibrated posterior | CANNOT_CHECK |

Summary-only observations cannot certify a causal localization. A timeout is
not an obstruction certificate.
