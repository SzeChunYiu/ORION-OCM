# Slice addendum R3 — the measured-design addendum: corrections to two pre-measurement design statistics of `FREEZE_V1_SLICE_ADDENDUM_R2.md`

`source_main`: `6e116ce5`.
Governs: `FREEZE_V1.md`, `FREEZE_V1_SLICE_ADDENDUM.md`,
`FREEZE_V1_SLICE_ADDENDUM_R2.md` (each committed before this addendum).

**Custody note, registered so the ordering is not misread.** The first three
freeze documents are committed *before* any executor, test, data extraction,
fit or result artifact, and CI asserts that every implementation artifact
postdates them. This addendum is different in kind and its ordering is
therefore registered explicitly: it is an **addendum to a MEASUREMENT**, so it
necessarily postdates the measurement. It states two numbers from
`FREEZE_V1_SLICE_ADDENDUM_R2.md` (sections R2.4 and R2.5) that were recorded
there as *pre-measurement design statistics* and were **wrong**, records the
measured values, and attributes the error to ONE stage. It changes:

- no registered FORM (the source-order presentation control of R2.4 and the
  single-factor ecology control of R2.5 are exactly as registered),
- no count of `FREEZE_V1.md` or of the slice addendum (`T`, `n_fit`,
  `n_held`, `rank_fit`, `rank_score`, `fit_lo`, `fit_hi`, `half`),
- no readout, no winner rule, no charged cost, no ecology, no grammar, no
  scope, no claim ceiling, no falsifier form and no frozen prediction.

## R3.1 What was wrong, and where

Both wrong numbers were design statistics I transcribed from a **scratch
measurement script that scored the control arenas with its own readout
language**, not with the registered language `R` of the slice addendum
section 3. The scratch script was superseded by the executor, which pins the
registered language; the two numbers below were left in the addendum text
unrevised.

Attribution to ONE stage: **the transcription step**, from a scratch
measurement whose control-arena scoring was not the registered one. It is not
a defect of the ecology, of the label, of the readout language, of the winner
rule, or of either control's registered construction. One-stage, and so one
fix: register the measured numbers here and let the receipts carry them.

## R3.2 Correction 1 — `FREEZE_V1_SLICE_ADDENDUM_R2.md` section R2.4 (the source-order presentation control)

**Registered there (pre-measurement, wrong):** "the winning readout is `C0`
at 32,834 errors against the majority's 32,834 — i.e. it is exactly the
majority rule and does NOT clear F1".

**Measured by the executor, pinned by the executor's asserts and re-derived by
route B from the committed receipt:**

| quantity | measured |
|---|---|
| control split | store = descriptor positions `0 .. n_fit-1` (source order), score = positions `n_fit .. T-1` |
| control score set | 97,018 descriptors, of which **32,834 negatives** |
| fit-majority rule | `1`; its control error count **32,834** (F1 half = 16,417) |
| `C1` (always 1) | **32,834** — it IS the majority rule on this arena |
| `C0` (always 0) | **64,184** |
| registered-language winner | **`LEN<=6`, 22,919** — fails F1 (22,919 > 16,417) |
| family readout `R1ASSOC>=1&R2ASSOC>=1` | **64,099** |

**The registered claim of R2.4 is unchanged and holds:** the control FIRES —
the winning readout under source order fails the registered F1 margin
(22,919 > 16,417), and the family readout degenerates to 64,099, far worse
than the majority rule's 32,834. The registered presentation lever is
load-bearing. Only the identity of the constant arm that ties the majority
(`C1`, not `C0`) and the identity of the source-order winner (`LEN<=6`, not
`C0`) were mis-transcribed.

## R3.3 Correction 2 — `FREEZE_V1_SLICE_ADDENDUM_R2.md` section R2.5 (the single-factor ecology control)

**Registered there (pre-measurement, wrong):** the control label's
"fit-majority 44,138".

**Measured:** under the registered control interface `y_sf(q) = 1 iff
|A1(q)| >= 1`, the held slice of 97,018 descriptors contains **77,741
positives and 19,277 negatives**, so the fit-majority rule makes **19,277**
errors. The block's winner and its losing product arm are exactly as
registered:

| quantity | measured |
|---|---|
| control label | `y_sf(q) = 1 iff |A1(q)| >= 1` (the R1 factor alone) |
| winner | **`R1ASSOC>=1`, 899 errors**, class `SINGLE_FACTOR_ASSOCIATION` |
| best factor-product arm | **`R1ASSOC>=1&R2ASSOC>=1`, 12,437 errors** |
| majority rule | 19,277 errors |

**The registered claim of R2.5 is unchanged and holds:** the joint arm LOSES
on a single-factor ecology (12,437 against 899 — it is 13.8x worse), so its
win on the registered ecology is evidence about the JOINT structure and not
about the readout form. That direction is the registered one, and it is the R06
lower-bound control doing its job: a reader who takes `899 < 12,437` for a
failed gate would have the control inverted. Only the majority-rule
denominator was mis-transcribed.

## R3.4 The exact-inference comparison readout (ECM), measured

`FREEZE_V1_SLICE_ADDENDUM_R2.md` R2.7 registers the exact-inference
comparison readout as a boundary datum scored for information only, outside
the readout language `R`. The executor names it `ECM_PRODUCT_FORM_MESSAGE`
(the product form of the two factor-local messages at the query) and the
receipt carries `{"readout": "ECM_PRODUCT_FORM_MESSAGE", "errors_held": 1893,
"agrees_with_winner": true}`: **exact inference over the stored two-factor
model is decision-IDENTICAL to the family-blind winner at the held stage** —
both 1,893 errors on 97,018 held descriptors. That is the point of the datum:
the winner rule recovers, from a closed family-blind language, the readout
that exact inference over the stored factorisation would produce. `ECM` is
not added to `R`; the language stays closed at 54 arms. This is the closest
thing to the row's registered contract, `TRIPLE_PARITY` ("registered
three-variable dependency response", recorded as a steer in `FREEZE_V1.md`
section 2), being EARNED rather than declared: the family-blind recovery lands
on the dependency response the contract names, without the language ever
holding a marginal, a joint table, or any message-passing routine.

## R3.5 Consequences registered here, and only these

- `FREEZE_V1_SLICE_ADDENDUM_R2.md` R2.4 and R2.5 are superseded **in their
  two measured numbers only**, as recorded in R3.2 and R3.3 above. Their
  constructions, their gates and their claims stand.
- Every frozen count, prediction, falsifier, readout, cost and scope is
  unchanged.
- The receipts of the real run carry the measured values and route B
  re-derives them from the committed receipt without reading this file's
  numbers: the corrections are stated for the reader, and are not inputs to
  any re-derivation.
