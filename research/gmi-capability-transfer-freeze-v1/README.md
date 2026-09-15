# GMI capability task-family transfer freeze v1

This capsule freezes the #602 F4 row **Predict transfer across task families** prospectively.

A fixed system is transferred from one source obligation vector to six opaque held task families. Transfer prediction is computed only by recomputing target signed margins `capacity - requirement` and applying the already-merged development-only capability predictor; task-family identity is unavailable to fitting or prediction.

The freeze includes an exact remint-invariance twin, five targets with at least one margin outside the development cube, explicit `CANNOT_IDENTIFY` abstentions, per-family SHA-256 receipts, and a whole-freeze digest. No held target outcome is present in this PR.

Claim ceiling: **G2** until a later, separate scoring artifact evaluates the committed freeze with an independent oracle.
