# FREEZE V2 AMENDMENT — the licensed band applied to the quantity its parent defines it on

Freeze V1: commit `dd9b34cef55ef13d144eb5a9258fbd515c55cd06` (blob
`63b98b249ccd736051a262fdd68f81a5ec7a7b80`). Register: commit
`527f326ec342a3d3041880c63edc84a2cc46984f`. Producers: commit
`52383a89`. This amendment is committed alone, after the corpus producer
has run and before any training or energy producer has run. `FREEZE_V1.md`
is not edited.

## What was observed (structure measures only; no prediction outcome)

The corpus producer computed the frozen structure measures on the train
splits. The delayed-mode stateless floor `E0` came out at `51775/119999`
(C1), `53994/119999` (C2), `14338/119999` (C3), `48894/119999` (C4),
`52850/119999` (C5), `38698/95999` (C6), `40214/119999` (C7),
`43650/119999` (C8), `50614/119999` (C9), `55422/119999` (C10). Under the
V1 sentence `the law is tested on a dataset only if 1/8 < E0 < 3/8`, eight
of ten datasets are `OUT_OF_BAND`, the two in-band datasets are both audio,
the Instrument I terminal is `INSUFFICIENT_IN_BAND_CORPUS`, and the
pre-registered ladder rule finds no in-band dataset at all, so Instrument
III has no registered workload either.

No `P-I`, `P-II`, `D` or `P-IV` prediction outcome had been consulted when
this amendment was written; the Instrument IV outcomes exist in
`REAL_RUNS/*/corpus.json` but are not touched by this amendment, which
changes nothing in Instrument IV.

## Attribution to one stage: the freeze specification

V1's band clause is headed `Licensed band (parent-owned, #903 amendment A4)`
and claims to be the parent's rule. The parent
(`gmi-833-real-transition-receipts-v1/FREEZE_V2_AMENDMENT.md`, section A4)
defines the band on `E0 := stateless candidate median overall eval error`
— the error over the WHOLE evaluation stream, immediate and delayed
positions together — and derives `1/8 < E0 < 3/8` from the priced
objective on that quantity. V1 wrote the same numbers against the
delayed-mode floor, a quantity roughly twice as large (the immediate-mode
floor is `0`, so the whole-stream floor is the delayed floor times the
delayed fraction). The clause therefore contradicts its own governing
attribution: as written it is not the parent's band.

The failure is in one stage — the freeze specification transplanted a
parent constant onto a different quantity — not in the corpus, the task
family, the candidates, the prices, the predictions or the decision rules,
all of which are unchanged.

## Repair under the governing clause

The governing clause is the parent's A4. It is applied as the parent
defines it, in exact form:

`E0_all := eta_train * E0`, where `eta_train` is the realized delayed
fraction of the train split (recorded in `corpus.json`) and `E0` is the
exact delayed-mode floor; the immediate-mode floor is exactly `0`.

A dataset is in band iff `1/8 < E0_all < 3/8`. Every other sentence of V1
stands: `lambda* = p * E0 / B` still uses the delayed-mode floor (that is
the quantity the priced delayed-mode objective is written on), the
predictions P-I1 to P-I5f, the controls, the recodings, the ladder rule
with its fallback order, the Instrument II onset rules, the Instrument III
protocol and the Instrument IV parts are unchanged.

Under the repaired clause the in-band verdicts are forced by the recorded
numbers, not chosen: `E0_all` is `0.2158`-ish for C1 and lies inside the
band for C1, C2, C4, C5, C6, C7, C8, C9, C10, and outside it for C3
(`E0_all` near `0.06`: the pixel bytes are mostly zero, so the stateless
floor is small and the parent's band excludes it exactly as it excluded
the parent's near-silent audio source). The exact rationals are emitted by
the executor.

## Disclosure

- `s6_instruction_followed: false` — the V1 band sentence is not followed
  as written; the governing parent clause is followed instead.
- `audit_shape_disclosed: POST_HOC_SUSPECT` for the band, because this
  amendment was written after the structure measures had been seen.
  Nothing else in the package carries that flag on this account.
- The V1 verdict is preserved: the executor reports BOTH terminals for
  Instrument I — `terminal_v1_rule` (which is `INSUFFICIENT_IN_BAND_CORPUS`
  by the recorded numbers) and `terminal_v2_rule` — and the reconciliation
  quotes the V2 terminal only together with this disclosure.
- The training and energy producers are updated in the commit following
  this one to compute the in-band verdict by the repaired clause; the
  corpus producer and its committed outputs are not touched.

## Custody

This file is committed alone. The custody checker pins its blob and
asserts that no `train.json`, no checkpoint record and no
`REAL_RUNS/energy/` artifact existed at this commit.
