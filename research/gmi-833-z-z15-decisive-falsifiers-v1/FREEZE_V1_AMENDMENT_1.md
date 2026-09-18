# Z15 freeze v1 — amendment 1: `F1` is blind inside a factor-two window, and the revival that closes it

Committed **before** the revived falsifier's numbers are used in any receipt or
reconciliation. The frozen `F1` was run against its registered null, the null
found a real blindness, and the response is diagnosis plus a mechanic
improvement — not a weaker null.

## What the null found

`FREEZE_V1.md` registered a null of 200 randomized boundary laws
`lambda*_rand = r·eta·p/2`, `r != 1`, each of which `F1` must catch. `F1` as
frozen examines the **40 endpoint worlds**. Result: **143/200 caught, 57/200
survived undetected**, all survivors with `r` in `{3/5, 5/7, 6/7, 5/6, ...}`.

## Diagnosis — one stage

The failing stage is the **registered world ladder**, not the checker and not the
theory. The registered design places the endpoints at `lambda_low = lambda*/2`
and `lambda_high = 3·lambda*/2`. A shifted boundary `r·lambda*` reproduces the
true endpoint classification for every world exactly when

```
lambda*/2 < r·lambda* < 3·lambda*/2   i.e.   1/2 < r < 3/2 .
```

So `F1` restricted to endpoints is **provably** blind on `(1/2, 3/2) \ {1}` and
**provably** decisive outside `[1/2, 3/2]`. That is a boundary of the frozen
instrument, not a defect in it, and it is recorded as
**EARNED-BY-COUNTEREXAMPLE** with the counterexample `r = 6/7`.

Endpoint evidence alone cannot localize the boundary better than a factor of
two, because two points at `lambda*/2` and `3·lambda*/2` carry exactly that much
information. No amount of re-running endpoints repairs this.

## The revival: `F1+`

The registered design already contains the information the endpoints lack — the
**20 boundary worlds** at `lambda = lambda*` exactly. The true law predicts a
**tie** there; any shifted law with `r != 1` predicts a strict winner:

- if `r > 1` then `lambda* < r·lambda*`, so the shifted law predicts
  `{PERSISTENT_STATE}`;
- if `r < 1` then `lambda* > r·lambda*`, so the shifted law predicts
  `{STATELESS}`;
- the exhaustive argmin at `lambda = lambda*` is the two-element tie, because the
  two class optima are `eta·p/2` and `lambda`, which coincide there.

Hence a predicted singleton never equals the actual tie, and `F1+` — `F1`
evaluated over **all 60 registered worlds**, endpoints and boundaries — fires for
**every** `r != 1`.

**Theorem `F1PLUS-DEC` (decisiveness).** For every rational `r != 1`, `F1+`
fires on the registered world set. *Proof:* as above; the boundary worlds alone
suffice, and they are part of the frozen design. QED

`F1+` is a strictly stronger instrument obtained by using evidence the frozen
design already contained. Nothing was tuned: the world ladder is unchanged, the
threshold is unchanged (`fires iff count > 0`), the theory is unchanged.

## Registered change

1. `F1` is **retained** with its frozen endpoint scope and its measured null
   result `143/200`, together with the analytic blindness interval
   `(1/2, 3/2)` and the counterexample `r = 6/7`, labelled
   EARNED-BY-COUNTEREXAMPLE.
2. `F1+` is registered as the decisive falsifier for row 2, evaluated over all
   60 registered worlds. Its null target is `200/200` caught, `0/200` surviving.
3. Both routes must agree on both, and the empirical survivor set of `F1` must
   lie **exactly** inside the analytically predicted interval `(1/2, 3/2)` —
   a characterization check, not merely a count, so that "blind" is verified
   rather than asserted.

## Register correction

The `SU-TRANS` success anchor registered in `FREEZE_V1.md` assumed indented JSON.
The pinned receipt is minified, so the anchor is corrected to the byte-exact
`"forty_endpoint_predictions_correct":true`. This is a transcription fix to a
pinned quotation, not a change of evidence; the register checker requires the
anchor to occur exactly once, so a wrong anchor fails loudly rather than
silently.

Everything else in `FREEZE_V1.md` is unchanged.
