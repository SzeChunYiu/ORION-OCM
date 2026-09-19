# GMI #833 Section Z / Z6 — theory discrimination against strongest parents

Closes the six rows of `### Z6` in issue comment `5684819296`.

## What it establishes

Thirteen parent selection rules, `404` preregistered worlds in three
declared-accounting families, two readouts, all predictions frozen before the
adjudication, two materially independent routes agreeing exactly:

- **`DS-1`** an executable registry covering every parent family the row names;
- **`DS-2`** disagreement is real: `220` / `220` / `226` `R1` disagreements with
  the registered law for MDL, the folk Occam rule and SRM, with `20` worlds
  excluded because the registered closed form is undefined there and
  abstentions are never counted as agreement;
- **`DS-3`** the wins/losses table, adjudicated by each world's own accounting;
- **`DS-4`** **the registered flagship law is refuted**: `lambda* = eta*p/2` is
  wrong on `108` of the `324` skewed-input worlds, because its derivation
  assumes uniform inputs and the stateless delayed-error floor is `min(q, 1-q)`,
  not `1/2`;
- **`DS-5`** the repair `lambda* = eta*p*R0`, with `R0` the stateless delayed-error
  floor under the environment's own input law, is correct in **all `404`**
  worlds — `60/60`, `324/324`, `20/20` — reduces to `eta*p/2` at `q = 1/2`, and
  unifies Z5's independently found `eta*p*(1 - 1/A)`;
- **`DS-6`** the repaired law is `R1`-identical to Bayesian decision theory,
  bounded rationality, algorithm selection, NAS-with-resource-regulariser,
  active inference, RL/control and program synthesis in all `404` worlds, proved
  by the affine-argmin argument and verified exhaustively; information theory
  and open-ended search abstain in all `404`. For all nine, the row-6 statement
  is made explicitly: **no discriminating experiment exists at this scope**;
- **`DS-7`** `0` of `200` random monotone rules reproduce the equivalence, the
  shifted `2*lambda*` control loses `40`/`60` and `252`/`324`, the always-abstainer
  scores `0`-`0`, and all six hostiles fire.

## What it does not establish

No claim that GMI is truer than MDL; no parent theory is refuted; no universal
observational equivalence; nothing about real or trained systems; and no
validation of the registered law beyond uniform inputs — the opposite is shown
and published in `FAILED_PREDICTION_REGISTER_V1.json`.

Claim ceiling:

```
GMI_833_Z6_PREREGISTERED_PARENT_DISCRIMINATION_AND_PROVED_OBSERVATIONAL_EQUIVALENCE_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z6-discrimination-v1/z6_discrimination_v1.py
python3 -I -B  research/gmi-833-z-z6-discrimination-v1/independent_discrimination_oracle_v1.py
python3 -I -B  research/gmi-833-z-z6-discrimination-v1/test_z6_discrimination_v1.py -v
python3 -I -O -B research/gmi-833-z-z6-discrimination-v1/test_z6_discrimination_v1.py -v
```

Stdlib only, exact arithmetic, no float in any claim. Route A about `22` s,
Route B about `3` min on one core (Route B evaluates every cost as an exact
rational, without Route A's denominator-clearing transform, so that the
transform is checked rather than trusted).

## Four frozen hypotheses were refuted

`D1` and `D2` both said the declared-cost parents would be separable from the
registered law at one readout or the other. They are not separable from each
other at all — they reproduce the declared-cost argmin set in every world — and
they differ from the registered law only where that law is wrong. `D6` said the
registered law would lose somewhere outside its assumption, and it does, on
`108` worlds. The `T12_SRM` rule as first frozen would have been the declared
cost under another name, and was re-registered with its own complexity constant
before any outcome was computed (`FREEZE_V1_AMENDMENT_1.md`).
