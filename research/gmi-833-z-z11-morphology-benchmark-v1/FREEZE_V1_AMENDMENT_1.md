# FREEZE_V1 amendment 1 — the scrambled-truth control's cell set

Written **before the first Route A run completes and before any score of any
theory on the scrambled control has been seen**; committed before the executor.
`FREEZE_V1.md` is not edited.

## What the freeze says

§2 `C6(b)`: every theory is additionally scored against the truth of a different
case (a fixed cyclic shift of the case list); a theory scoring above the null
there is a leakage alarm. §5: the scrambled-truth control must put `T_GMI_IC1`
at or below the best null.

## The defect this amendment anticipates

The scrambled truth and the real truth share every class-choice cell whose
argmin set is determined by the universe alone — e.g. every ladder cell at
`λ = 0` (`{2}` whenever `E(2) = 0`) and every cell at a price above both
marginals (`{0}`). On those cells a theory that predicts the *real* truth
perfectly also matches the *scrambled* truth, so an honest theory scores well
above a uniform null on the all-cell control without reading anything. A
control that alarms on `T_GMI_IC1` — a pure function of the public spec, which
cannot leak by construction — has no specificity: it is a false-positive
instrument, and the programme's checker rule (validate the no-alarm case on
known-clean data before reporting) forbids gating on it.

## The governing clause, fixed now

1. The executor computes the literal all-cell control exactly as §2/§5 say and
   reports it in full (`scrambled_truth_control.literal_all_cells`).
2. It also computes the control restricted to the **informative cells**: the
   class-choice cells `(case, λ)` on which the scrambled truth's argmin set
   differs from the real truth's argmin set. On those cells a truth-reading
   theory scores `1`, a theory that predicts the real truth scores `0` wherever
   it does not abstain, and a uniform null scores about `1/(2^K − 1)`.
3. **If the literal control does not alarm on `T_GMI_IC1`, it governs**
   (`governing_form = LITERAL_ALL_CELLS`, `s6_instruction_followed = true`).
4. **If the literal control alarms on `T_GMI_IC1`, the informative-cell control
   governs** (`governing_form = INFORMATIVE_CELLS_AMENDMENT_1`), the receipt
   records `s6_instruction_followed = false` and
   `audit_shape_disclosed = POST_HOC_SUSPECT` for this gate, and the literal
   result stays in the receipt as a recorded false alarm of the frozen
   instrument. The `HZ1` hostile must be applicable and detected under **both**
   forms in either case.

Nothing else in `FREEZE_V1.md` is touched; no frozen prediction `B1`–`B6` is
affected by this amendment.

## Also fixed now: the scramble pairing

The freeze's "fixed cyclic shift of the case list" is realised as a cyclic shift
**within each `(class, universe type)` group**, with the partner's profile
re-priced at the case's own price set. Reason: `C5_HIDDEN` mixes `LADDER` and
`TWO_LEVEL` universes (different level sets) and carries one private price per
case, so a shift across universe types or price sets leaves scored cells with
no truth to score against. A group of size `1` is a hard failure, not a silent
identity pairing.
