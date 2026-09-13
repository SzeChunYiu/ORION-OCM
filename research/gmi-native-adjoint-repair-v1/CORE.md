# Native gradient parameter attribution — corrected

The parameter marker now belongs to the weight leaf. The existing reverse
multiplication edge scales its adjoint by the input before updating the weight.
At zero input the erroneous8→9 write is removed; the nonzero8→7 control remains.

- [Correction, proof scope and outcomes](PARAMETER_ADJOINT_CORRECTION_V1.md).
- [Primary parents and custody](PARENTS_AND_CUSTODY_V1.md).
- [Full versioned receipt](RECEIPT_V1.json) and [complete manifest](MANIFEST_V1.json).
- [Portable replay and active-runtime checks](REPLAY_V1.md).
- [Historical-runtime selection](HISTORICAL_RUNTIME_CUSTODY_V1.md).
- [Complete original source diagnosis and controls](raw/pr551-grad-audit-20260913/PR551_GRAD_DIAGNOSIS_CORRECTION_7328D5B3_V1.md).

B0/B1 and both bias paths are checked. The unit includes2197 scalar fixed-point
cases,45 exact-polynomial finite differences and shared/tied-weight controls.
Correctness is relative to the registered ordered, rounded/clamped pullback.
The saturation control explicitly rejects literal quantizer differentiation.
The seven affected historical regression fixtures use the frozen old VM; they supply
no corrected-runtime capability result. All historical packets remain exact,
and later experiments must bind the corrected VM source.
