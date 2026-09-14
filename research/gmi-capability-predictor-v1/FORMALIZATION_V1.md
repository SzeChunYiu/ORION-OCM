# Capability predictor V1 — formalization (F4 skeleton)

**Issue:** #602 F4. **Status:** G1 spec. This note gives the mathematics that the validator checks structurally; it does **not** prove that morphology predicts capability or that the predictor achieves any calibration target.

## 1. Objects

- `D ∈ Desc_8` — 8-field descriptor value per `DESCRIPTOR_V1.md`. Each `D` is a syntactic tuple with finite enumerable coordinates; `Desc_8` has no brand labels.
- `E ∈ Eco_15` — extended ecology per `ECOLOGY_EXTENSION_CONTRACT_V1.json` (15 coords + bijective remint guard).
- `R = (b, p, ρ)` with `b ∈ R_{≥0}^k` hard caps, `p ∈ R_{≥0}^k` nonnegative price, `ρ : r ↦ (time, energy, area)`.
- `H = (H_dev, H_held, lineage)` — family partition for prospective evaluation.
- `C = (C_1,...,C_27)` — capability vector where each `C_c` is measured per `CONTRACT_V1.json` row `cap-*` and `F1_ASSAY_V1.json` gate `S0`.

Define the predictor as the map

```text
Cap : Desc_8 × Eco_15 × R × Hist  →  ∏_{c=1}^{27} Dist_c × {abstain_c}
```

where `Dist_c` is either `Δ_3 = {(p0,p1,p2): p_i ≥ 0, Σp_i=1}` (categorical grade) or `Beta(a,b)` on `[0,1]` (continuous success probability). The categorical vs Beta choice is frozen per `c` before `H_held` outcomes.

## 2. Resource order (inherited from F1)

`r ≤_R s` iff every registered nonneg coordinate of `r` ≤ that of `s`. This is a partial order (F1-R). A scalar `p^T r` comparison is canonical only with `p ≥ 0` frozen before protected scoring.

## 3. Proper loss and held-only scoring

For held family `f ∈ H_held` with realized label `y_{c,f}` per row `c`'s `success_metric`:

- categorical: Brier `BS = (1/|H_held|) Σ_f ||p_{c,f} - onehot(y_{c,f})||^2` or log score `- (1/|H_held|) Σ_f log p_{c,f}[y_{c,f}]`.
- continuous: log score `-(1/|H_held|) Σ_f log Beta_pdf(y_{c,f}; a_{c,f}, b_{c,f})` or CRPS.

Both are **strictly proper**: for any fixed held distribution, the expected loss is minimized uniquely by reporting the true distribution. This is Gneiting & Raftery (2007) and holds only on `H_held`; development data `H_dev` never enters the average.

## 4. Abstention as selective prediction

Let frozen thresholds `η_c, δ_c, d_max` and remint-invariant ecology embedding `φ(E)`. For row `c` and held family `f`, define binary decision `A_{c,f} ∈ {predict, abstain}`:

```
abstain_{c,f}  iff  (underspec)  D or E has NONE/UNDECLARED on a required coordinate
                or (support)     dist(φ(E_f), conv{φ(E): E∈H_dev}) > d_max
                or (uncertainty) H(posterior_{c,f}) > η_c  or  width(CI_{c,f}) > δ_c
                                 or CI_{c,f} overlaps both τ_parent and τ_twin intervals
                or (parent)      V_c^P(E_f,B) unenumerated beyond precision ε_c
                or (remint)      proposed remint for f is not bijective or leaks label.
```

Tightening a threshold is allowed; relaxing post-freeze is forbidden. Report `coverage = E[1 - abstain]` and `selective risk = E[loss | predict]`. Abstained rows are unscored and earn no credit.

This is Chow's reject option / selective prediction with a prospectively frozen reject rule; the falsifier is a high-entropy / out-of-support family that is not rejected.

## 5. Freeze and remint

For each `f ∈ H_held`, serialize `Cap(D, E_f, R_f, H)` to `PREDICTION_{f}_V1.json` with SHA256 `h_f` and timestamp `t_f`. Require `t_f < t^{outcome}_f` (outcome timestamp from a monotonic clock or commit graph). Verify by checking `h_f == sha256(file)`, `t_f < t^{outcome}_f`, bijections via `ecology_extension_v1.is_bijection`, and that the derivation commit DAG contains no node that reads `f`'s labels. Per-family versioning is append-only; a later write for `f` supersedes only if its own `t_f'` still precedes `t^{outcome}_f`.

## 6. Boundaries

- Independent units `n_c` for the F1 assay satisfy Hoeffding; repeated / adaptive dependent rows need a separately registered simultaneous-validity construction (#602 M).
- DU-1: `Cap` predicts *admissible* success (what could be achieved with the declared information, if reached), not *reachability* (whether development law `D_dev` will find `D`). Crossing the two is a claim error.
- No cross-row scalar `J_p` without a frozen nonnegative `p`; otherwise default is Pareto / componentwise dominance.

## 7. Theorem (spec-level, P1)

*Descriptor enumerability.* If `capability_predictor_v1.run()` returns `PASS`, then within this registry: every descriptor field is from the frozen allowlist with no brand label, predictor signature mentions `Cap(D,E,R,H)`, loss is strictly proper on `H_held` only, abstention gate has ≥3 triggers pre-frozen, and the freeze rule requires per-family digest and bijective remint before held outcomes. This is a **syntactic** guarantee; it does not imply predictive accuracy.
