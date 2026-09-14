# F4 falsifiers — three cheapest single-command checks

**Scope:** G1 spec falsifiers (no held-family campaign). Each is runnable with one `python` invocation on exact toy microscopes. A pass does not earn the corresponding G6 box; a fail voids the predictor claim for that box. Boxes needing a frozen held-family campaign are flagged `needs-campaign`.

| # | Falsifier | What it tests | Command | Boxes closed when it **passes as a toy check** vs **what remains for G6** |
|---|-----------|---------------|---------|------------------------------------------------------------------------------|
| **Fz1** | **Remint-twin invariance + brand-free descriptor** | (a) No brand label survives in any `allowed_values` entry; (b) predictions for two inputs that are bijectively reminted copies of each other (same `D,E,R,H` up to renaming of world/task ids) produce identical distributions; a non-bijective or leaking map is rejected. | `python -m research.gmi-capability-predictor-v1.capability_predictor_v1` (runs `validate_contract` + `check_toy_remints`); plus `python -c "import research.gmi-capability-predictor-v1.capability_predictor_v1 as m; m.run()"` — the toy remint model checks identity/relabel accepted, collapsing rejected. | **Closes at toy level:** box 1 *spec enumerability* (descriptor has no brand strings, all 8 fields have floors, `SCHEMA_V1.json` enforces allowlist) and box 3 *freeze rule well-formedness* (per-family bijective remint is mechanically checkable). **Needs campaign:** true prospective freeze — timestamp < outcome, SHA256 digest, per-family holdout with audit log showing no held data in the derivation commit graph. That requires the held-family campaign. |
| **Fz2** | **Price-flip / ablation twin on exact microscopes** | (a) **Repricing:** flip nonnegative price vector `p` from `p=(0.9,0.1)` on `(exec, store)` to `p'=(0.1,0.9)`; verify the predictor's Pareto ordering of two morphologies that trade `exec` vs `store` inverts (or at minimum moves) — if it does not move, resource profile is decorative. (b) **Ablation:** drop `CONTENT_ROUTED_COMBINATION` from `native_operators` (or halve `|S|` from 8 to 4) while holding other fields fixed; verify predicted success on GG55 conditional-routing world `(x0,x1,q)->x_q` drops from ≈1 toward 3/4 and on GG54 `m=6` delayed-reproduction drops from 1 to provably bounded. The script `scripts/fz2_price_ablation_toy.py` (provided as reference in this doc) does both in <1s with no search. | `python research/gmi-capability-predictor-v1/scripts/fz2_price_ablation_toy.py` — enumerates two descriptors × two price vectors × two microscopes, asserts `predicted_gap > 0` else raises `Falsified`. | **Closes at toy level:** necessity of fields `resource_profile` (box 7) and `native_operators`/`state_carrier` (box 8) — a predictor that ignores them is falsified cheaply. **Needs campaign:** predictive *accuracy* on held resource-repricing families and held ablations at real scale. Toy shows the predictor is *sensitive*; campaign shows it is *correct* prospectively. |
| **Fz3** | **Abstention trigger on out-of-support family** | Construct a held family whose world alphabet contains a symbol `UNSEEN_SYMBOL` absent from every development family (or whose ecology embedding distance from convex hull of `H_dev` exceeds frozen `d_max`), and whose posterior credible interval straddles `tau_parent`/`tau_twin`. Verify the predictor emits `abstain=true` with reason `out-of-support` or `non-identifiability`; if it emits a confident `capable`/`fail` distribution, the abstention gate is falsified. | `python research/gmi-capability-predictor-v1/scripts/fz3_abstention_toy.py` — builds one dev family (delay-4 alphabet `{0..3}`), one held family (`{UNSEEN}`), frozen `d_max=0.1`, asserts `abstain==True`. | **Closes at toy level:** box 10 *spec well-formedness* — the five triggers, thresholds frozen prospectively, abstention rate / selective risk reporting contract, and the `UNSEEN_SYMBOL` falsifier described in `CONTRACT_V1.json:abstention_gate.falsifier`. **Needs campaign:** calibrated abstention at scale — measured coverage vs selective risk on many held families, calibration of the threshold `eta_c/delta_c/d_max` before outcomes, and the efficiency tradeoff. |

## Reference sketches for Fz2/Fz3 toys (normative for campaign, informative for skeleton)

**Fz2 — price-flip + ablation (informative pseudo-code, matches `FILTERED` descriptor):**

```python
# Two morphologies trading exec vs store; two price vectors
D_exec_cheap = {"state_carrier": "FINITE_ALPHABET(8)", "native_operators": {"CONTENT_ROUTED_COMBINATION"}, ...}
D_store_cheap = {"state_carrier": "EXTERNAL_ADDRESSABLE(64, latency=10)", ...}
p_exec = {"exec": 0.9, "store": 0.1}
p_store = {"exec": 0.1, "store": 0.9}
# GG55 world: predictor must assign higher prob(capable) to routed variant
assert E_predict(D_routed, gg55) - E_predict(D_fixed, gg55) > 0.15  # falsified if not
# GG54 m=6: |S|=4 variant must be predicted below |S|=8 variant
assert E_predict(D_S8, gg54_m6) - E_predict(D_S4, gg54_m6) > 0.20
# Price flip must move Pareto ordering
assert rank(p_exec, D_exec_cheap, D_store_cheap) != rank(p_store, D_exec_cheap, D_store_cheap)
```

**Fz3 — abstention:**

```python
dev_support = embed_families(["delay4:{0..3}"])
held = embed_one("UNSEEN_SYMBOL:{*}")
assert distance(held, convex_hull(dev_support)) > d_max  # out-of-support by construction
pred = Cap(D, held.ecology, R, H={"dev_families": ["delay4"], "held_families": ["unseen"]})
assert pred.per_row["cap-working-memory"].abstain is True
assert pred.per_row["cap-working-memory"].reason in ("out-of-support", "non-identifiability")
```

## Which of the 11 F4 boxes need a frozen campaign (do not claim on skeleton)

| Box | Needs frozen campaign? | Why |
|-----|------------------------|-----|
| 1 Build descriptor | **No** — spec check suffices (enumerability + no-brand). The *use* of the descriptor needs a campaign, the *definition* does not. |
| 2 Fit/derive only from development worlds | **Yes** — requires audit log + git history showing no held data in derivation commits + timestamp check. |
| 3 Freeze held-family predictions | **Yes** — requires per-family SHA256 + timestamp < outcome; toy only checks the rule is well-formed and remint is bijective. |
| 4 Predict known family strengths/weaknesses | **Yes** — held families only (e.g., retrieval-family vs planning-family strengths). |
| 5 Predict failure modes before testing | **Yes** — pre-registered failure predictions vs realized failures. |
| 6 Predict transfer across task families | **Yes** — cross-family held transfer. |
| 7 Predict after resource repricing | **Partial** — Fz2 toy closes *necessity*; G6 needs held repricing families. |
| 8 Predict after ablation | **Partial** — Fz2 toy closes *sensitivity*; G6 needs held ablation twins. |
| 9 Predict after environmental drift | **Yes** — held drift families varying `drift_regime_change` coord; toy has no real drift. |
| 10 Calibrate uncertainty / abstention | **Partial** — Fz3 toy closes *gate well-formedness*; G6 needs selective risk / coverage on many held families. |
| 11 Real-regime replication (code, math/proof, factual/science, multimodal/control) | **Yes** — full-scale tasks; clocked separately from GMI toy measurement. |

**Box closure at skeleton:** none of the 11 boxes are claimed closed by this skeleton. Fz1–Fz3 are *spec falsifiers* shipped as executable toys; they make the predictor falsifiable before any campaign but do not earn empirical credit.
