# G4 remaining non-ML decision adequacy

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) remaining
non-ML G4 axes on the exact cache/horizon toy. **G4.4 stays locked (0/9).**
The fourth unlock conjunct is **refuted**. No router is trained.

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

Donor engines are imported, not copied:

- [`research/g4-horizon-exact-v1/`](../g4-horizon-exact-v1/CORE.md) — `H_eff`
  exact cache world, DP, analytic threshold, reset/checkpoint, Pareto
  half-spaces.
- [`research/paid-decision-region-correction-v1/`](../paid-decision-region-correction-v1/CURRENT.md)
  — paid decision-region / early exit (cited).
- [`research/metareasoning-parent-review-v1/`](../metareasoning-parent-review-v1/CORE.md)
  — parent-assumption review of PR #154 (cited).
- [`research/machine-epistemics-lifetime-v1/`](../machine-epistemics-lifetime-v1/README.md)
  — raw vector / no-scalarization contract (cited).

Already earned in `g4-horizon-exact-v1` and **not duplicated**: G4.2 sweeps,
G4.3 parent list, analytic-on-DP-Pareto residual 0, `PRICE_REGIME_ONLY`,
`G4.4_learned_routing = NOT_UNLOCKED`.

## Measurements added here

1. **Legal features.** Full set `(cached, remaining, item, time)` implements
   the analytic/DP parent. Dropping `remaining` or `cached` produces action
   collisions. `item` and `time` are redundant given `remaining`.
2. **Hypothesis class.** Exact finite-state DP contains the analytic parent.
   Myopic 1-step (this-query rent vs build) cannot emit the required long-horizon
   `buy` (`H_eff` 0 vs 7 on the constant family).
3. **Analytic vs DP residual.** Recomputed via import on every frozen family:
   componentwise zero. Box G4.4.4 stays **REFUTED**.
4. **Pareto band.** Cite PR #154 / horizon `H=4..8`. Toy analytic switch is
   `remaining > 4` (constant horizon 5). Does not contradict the cited band.
   Mid-horizon rent vs buy remains incomparable.
5. **Lifecycle.** Reset intervals `{1,2,4,8}` from the horizon toy: post-reset
   service coordinates and `H_eff` match independent empty-cache rebuilds.
   Checkpoint preserves hits. Compose-stage early-exit lifecycle is
   `CANNOT_CHECK` here.
6. **Lifetime, raw vector.** Exact parent vs rent stays price-conditional after
   checkpoint maintenance. A hypothetical learner with positive
   train/infer/update/maintain and zero residual cannot pay back. Not a G4.4
   unlock.

## Not claimed

G4.4. Programme-wide `LEARNED_ROUTER_NOT_NEEDED`. Neural router. Production OCM
lifetime. `STRATEGY_SELECTION_RESIDUAL_CONFIRMED`.
