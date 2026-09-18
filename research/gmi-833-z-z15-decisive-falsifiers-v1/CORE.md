# gmi-833-z-z15-decisive-falsifiers-v1

Section Z (issue comment `5684819296`), subsection **Z15 — Decisive
falsifiability**: all six rows.

Claim ceiling:
`GMI_833_Z15_FOUR_EXECUTABLE_DECISIVE_FALSIFIERS_FOR_THE_FLAGSHIP_MORPHOLOGY_SELECTION_THEORY_AT_REGISTERED_FINITE_SCOPE`

## The flagship theory, without the repository

> A machine's *morphology* is whether it carries persistent internal state.
> Given a task in which some outputs must depend on an earlier input, and a price
> `lambda` charged per bit of persistent state, the theory predicts which
> morphology a resource-bounded search will select: stateless when
> `lambda > eta·p/2`, persistent when `lambda < eta·p/2`, and a tie exactly at
> `lambda = eta·p/2`, where `p` is the probability that a scored moment requires
> the earlier input and `eta` weights that requirement. The prediction is made
> from the task's parameters alone, before any search is run, and the search
> itself never sees an architecture name.

## Four falsifiers — clean vs planted

| id | what it detects | clean (no alarm) | planted positive (fires) |
|---|---|---|---|
| `F1` | systematic morphology-selection failure, endpoint scope | `0/40` | `20/40` under boundary `2·lambda*` |
| `F1+` | same, revived over all 60 worlds | `0/60` | `20/60` under boundary `6/7·lambda*` |
| `F2` | recovery outside the predicted set | `0/60` | `20/60` with the prediction narrowed to `{STATELESS}` |
| `F3` | capability miscalibration beyond registered uncertainty | `0/480` | `1/480` with one truth element removed |
| `F4a` | invariance failure under candidate-identifier remint | `0` changes in `12,000` world-checks over 200 remints, `1` distinct multiset | semantics-permuting pseudo-remint: `200` distinct multisets, thousands of changes |
| `F4b` | invariance failure under common unit rescaling | `0/360` | rescaling `eta` alone: `240/360` |

`F4a`/`F4b` are registered as a **pair** on purpose: an invariance checker that
returned `0` for everything would be a constant `False`. It must stay silent on
the transformation claimed irrelevant and fire on the one that is not.

## The scientific core: a blind falsifier, diagnosed and revived

The registered 200-seed null of randomized boundary laws `r·lambda*` caught only
**143/200**. That is a real result, not a bug, and it was neither hidden nor
tuned away.

- **Diagnosis, one stage — the world ladder.** Endpoints at `lambda*/2` and
  `3·lambda*/2` reproduce the true classification for every `r` in `(1/2, 3/2)`.
  `F1` restricted to endpoints is therefore **provably** blind there.
  Counterexample `r = 6/7`. Labelled **EARNED-BY-COUNTEREXAMPLE**.
- **Verified, not asserted.** The 57 survivors realize exactly 12 distinct
  multipliers — `2/3, 3/4, 3/5, 4/3, 4/5, 4/7, 5/4, 5/6, 5/7, 6/5, 6/7, 7/6` —
  **all** inside `(1/2, 3/2)`, with `0` survivors outside and `0` catches inside.
  The blind set is exactly the predicted interval.
- **Revival `F1+`, unconditional.** The registered design already contains the
  20 boundary worlds at `lambda = lambda*`, where the true law predicts a tie and
  any `r != 1` predicts a strict winner. Theorem `F1PLUS-DEC` proves `F1+` fires
  for **every** `r != 1`; measurement confirms **200/200** caught, `0/200`
  surviving, and `F1+` stays silent on the true law (`0/60`).

No world, threshold or theory was changed. The frozen `F1` and its `143/200` are
retained beside the revival.

## Failed preregistered predictions, published beside the successes

`FAILED_PREDICTION_REGISTER_V1.json`: **6** failed/falsified/open entries and
**2** successes, each pinned by path, git blob sha and a verbatim anchor required
to occur exactly once; all 8 resolve. The deliberately shifted boundary is
labelled `REGISTERED_NEGATIVE_CONTROL` — a designed control, not a discovered
failure. One entry is this session's own Z12 calibration-instrument defect.

The register checker is itself validated: the test plants a non-occurring anchor
and a missing file and requires both to be rejected.

## Two materially independent routes

- **A** `z15_decisive_falsifiers_v1.py` — per-candidate `Fraction` scan over all
  65,552 candidates; the summary reduction it uses for repeated sweeps is
  verified against the full scan on every registered world (`0` mismatches).
- **B** `independent_falsifier_oracle_v1.py` — semantics rewritten as explicit
  truth-table lists, reduced to a multiplicity histogram, decided with **integer**
  objective coefficients after clearing denominators. Imports nothing from route A
  and nothing from the Z12 package.

Both reproduce `65,552` candidates, `146` distinct risk summaries, and the
parent-recorded `shifted_threshold_failures = 20` and
`endpoint_predictions = 40`. Contract: all clean counts and all verdicts agree
exactly; deterministic planted counts agree exactly; the randomized `F4a` plant
is contracted on verdict only.

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z15-decisive-falsifiers-v1/independent_falsifier_oracle_v1.py
python3 -I -B  research/gmi-833-z-z15-decisive-falsifiers-v1/z15_decisive_falsifiers_v1.py
python3 -I -B  research/gmi-833-z-z15-decisive-falsifiers-v1/test_z15_decisive_falsifiers_v1.py -v
python3 -I -O -B research/gmi-833-z-z15-decisive-falsifiers-v1/test_z15_decisive_falsifiers_v1.py -v
```

19 tests, stdlib only, roughly 50 s.

## What this package does NOT claim

Surviving four falsifiers does not verify the theory. The set of four is not
claimed complete. `architecture-uncommitted` here means the search sees only
opaque summaries — it does **not** mean prior-free. No real-system or universal
morphology claim is licensed.
