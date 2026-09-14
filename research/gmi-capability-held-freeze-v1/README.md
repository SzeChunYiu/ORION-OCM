# GMI capability held-family freeze v1

This capsule addresses only the #602 F4 row **“Freeze held-family predictions.”**

Six opaque held morphology families are generated outside the development cube used to fit `research/gmi-capability-predictor-dev-v1/`. The family IDs contain no architecture semantics, and no observed held outcome is present in the freeze artifact.

`HELD_FAMILY_PREDICTIONS_V1.json` stores the descriptor margins, the already-fitted predictor's frozen output, per-family digests, and a whole-freeze digest. `freeze_held_predictions_v1.py` recomputes the freeze from the merged development-only predictor and rejects outcome leakage, development overlap, prediction edits, and digest edits. `CANNOT_IDENTIFY` is frozen as a legitimate prediction wherever the development corpus does not identify a held value.

This is prospective registration, not scoring. The claim ceiling remains **G2** until held outcomes are computed in a later round and compared against the frozen receipt.
