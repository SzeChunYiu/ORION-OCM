# gmi-833-z-z8-hostile-ingredients-v1

Section Z (issue comment `5684819296`), subsection **Z8 — Hostile
out-of-distribution science**: rows 2–10 (the nine ingredients). Row 1
(*commission independent hostile benchmark construction*) is declared out of
scope: it names an independent party as the instrument and this lane built the
ingredients.

Claim ceiling:
`GMI_833_Z8_NINE_HOSTILE_INGREDIENTS_EACH_SHOWN_TO_MOVE_A_REGISTERED_VERDICT_OR_PROVED_UNABLE_AT_REGISTERED_THREE_MODE_FINITE_STATE_SCOPE`

## What is shown (exact rationals, both routes agreeing on every count)

The base universe is the Z13 three-mode ladder (`L = 4`, `b ∈ {0,1,2}`, window
`{2,3}`), the `135`-world grid `η ∈ {1,2,3} × p over eighths`, prices
`{j/16 : j = 0..24}`. Four registered verdicts: `V_SEL` (argmin set),
`V_NICHE` (level 1 an envelope vertex), `V_THR` (marginal pair), `V_FAIL`
(failure-mode set). Every ingredient's ground truth is re-enumerated under the
modified universe.

| ingredient | headline |
|---|---|
| `I1` near-ties | `V_SEL` moves in `132/135` worlds; `6` triple-tie worlds (`3` degenerate) |
| `I2` verifier noise/failure | uniform flip noise cannot move `V_NICHE` (`135/135` at `ε ∈ {1/16,1/8,1/4}`, affine theorem `ZH-2`); delay-2-only noise moves it in `3/6/12`; dropping `t = 2` sets `R0(1,2) = 1/4` and moves `V_THR` in `108` |
| `I3` causal aliasing | period-2 law: `V_NICHE` `12/135`, `V_THR` `108/135`, `V_SEL` `108/135` |
| `I4` shift/nonstationarity | `2612/33075` shift cells move `V_SEL`; the frozen nonstationary floor is exact on `31/49` pairs (same side of `1/2`) and fails on all `18` opposite-side pairs (`ZH-4`, earned by counterexample) |
| `I5` accounting | affine `ρ = 2b+1`: `0` moves with the matching price (theorem); state-count `ρ ∈ {0,1,3}`: `V_NICHE` `36/135`; concave `ρ ∈ {0,2,3}`: `24/135` |
| `I6` history/current optimum | mixture moves `V_SEL` in `11264/151875` cells and never drops a shared level (`134907/134907`); hysteresis moves `2003 / 5069` of `50625` cells at `κ = 1/32, 1/8` |
| `I7` grammar/encoding | Moore: cannot move `V_SEL`/`V_NICHE`/`V_THR`, moves `V_FAIL` in `108`; input-only: `V_NICHE` `12`, `V_THR` `108`; relabelling with the task: `0` (bijection, no-alarm) |
| `I8` search law | single-start descent attains `1/8` where exhaustive is `0` and moves `V_NICHE` in `12`, `V_SEL` in `86` worlds; seeded hill-climb attains `9/9` floors and moves nothing |
| `I9` freeze before scoring | freeze commit `f7e1e7b1` precedes every executor; hostile world set `1399` entries, one `sha256`; `4` of `11` frozen sub-predictions missed and are published, not repaired |

Named results: `ZH-1` (the matrix), `ZH-2` (affine maps cannot move the niche),
`ZH-3` (why five ingredients hit the same twelve worlds), `ZH-4`
(nonstationary floor boundary), `ZH-5` (published tie-cell misses), `ZH-6`
(instruments). See `Z8_THEOREMS_V1.md`.

## Two materially independent routes

- **A** `z8_hostile_ingredients_v1.py` — next-state tables with per-address
  majority outputs; the price grid scanned cell by cell.
- **B** `independent_z8_oracle_v1.py` — full `(output, next-state)` pairs at
  `b ≤ 1`, constructive witness + closed-form bound at `b = 2`; argmin sets as a
  piecewise-constant function of the price from supporting slopes. Imports
  nothing from A. `test_z8_hostile_ingredients_v1.py` compares the receipts
  field by field.

## Hostiles (all applicable, all detected) and null

`HX1` corrupted floor, `HX2` identity ingredient claimed earned, `HX3` null
pool containing the true law, `HX4` non-affine noise model, `HX5` vacuous
bound, `HX7` low-bit LCG null. Null: `200` seeded marginal laws (`148`
distinct, `IC-1`'s pair excluded) score at best `48/249` where `IC-1` reads
`249/249`. No-alarm: relabelling moves `0` verdicts without alarm.

## Reproduce

```bash
python3 -I -B research/gmi-833-z-z8-hostile-ingredients-v1/z8_hostile_ingredients_v1.py
python3 -I -B research/gmi-833-z-z8-hostile-ingredients-v1/independent_z8_oracle_v1.py
python3 -I -B research/gmi-833-z-z8-hostile-ingredients-v1/test_z8_hostile_ingredients_v1.py
python3 -I -O -B research/gmi-833-z-z8-hostile-ingredients-v1/test_z8_hostile_ingredients_v1.py
```

Receipts: `RESULT_V1.json`, `ORACLE_RESULT_V1.json`,
`FAILED_PREDICTION_REGISTER_V1.json`, `MANIFEST_V1.json`. Workflow:
`.github/workflows/gmi-833-z-z8-hostile-ingredients.yml`.
