# RV-377-118 Lane C — instrument note, recorded before the lane's adjudication

Date: 2026-09-12. Applies to the 99 CP1 ablation units U-C001…U-C099 (33 kinds × `E_smooth1`,
`E_smooth3`, `E_sym5`). Predictions C1 and C2 of `GMI_DISTRIBUTED_BATCH_RV_377_118_FREEZE.md`
are **unchanged**.

## What the first execution found

On both laptops the units for 18 of the 33 kinds returned in under a second with
`KeyError('<kind>')`. The traceback ends in `morphgen.op_insert_verifier → _sources_of_type →
morph.KINDS[k]`: the mutation grammar constructs certain kinds **by name** (`ABSTAIN`, `VERIFY`,
`LOOKUP`, `LINEAR`, `PROGEXEC`, and the kinds those operators wire to), so deleting such a kind
from the alphabet is not a leave-one-out test of derivability — the generator crashes on its
own hard-coded reference before any search happens.

This is the same defect that left **18 of 33 kinds without a receipt** on `E_wit1` in
`RV-377-110`/`RV-377-113` (`microscopes/results/STAGE_B1_ABL_*_E_wit1_S0.json` exists for 15
kinds only). Those absences were never classified; they are classified now.

## Instrument repair (additive; no prediction touched)

`gmi_microscope.primitive_ablation.run_one` now catches a `KeyError` whose argument is the
dropped kind and writes a receipt with `status = STRUCTURAL_TO_GENERATOR` at the unit's
registered receipt path, so the unit is EXECUTED and its outcome is visible. Every other
exception is still reported as `ERROR`, and a genuine search still produces the ordinary
receipt through `b1.main`.

## How the adjudication of C1/C2 must read these kinds

A kind with `STRUCTURAL_TO_GENERATOR` is neither REDUCIBLE nor IRREDUCIBLE at this scope: it is
`NOT_TESTABLE_BY_LEAVE_ONE_OUT__GENERATOR_HARD_CODES_IT`, exactly as `INPUT`/`OUTPUT`/`TARGET`
were classed STRUCTURAL in `RV-377-110`. C1 and C2 are adjudicated over the kinds that ARE
testable, and the count of untestable kinds is reported alongside. A generator that references
kinds by class/type instead of by name (so that an absent kind is skipped rather than crashed on)
is the minimal justified change and is owed as a separate frozen revival record; it is not made
here.
