# Parity V5 custody repair

This directory repairs two demonstrated execution/evidence defects while
preserving the frozen V5 instrument, registration, runners and raw results.

- [Protocol and proof obligations](PROTOCOL_V1.md): authority, canonical first
  attempt, full evidence reconstruction, cost boundary and limitations.
- [Validation readout](VALIDATION_READOUT_V1.md): exact controls and existing
  empirical packets; these are distinct sources of evidence.
- [Original defect controls](raw/SYNTHETIC_COUNTERCONTROLS_V1.json):
  source-bound synthetic witnesses, with no measurement execution.
- [Imported packet bindings](raw/IMPORTED_V5_PACKET_BINDINGS_V1.json):
  three byte-preserved records from main commit 2ea3a617.

The operational entry point is attempt_custody_v1.py. It requires Linux,
an explicit CPython interpreter, a persistent registry and the explicit
--execute-first-attempt argument. Its output directory remains reserved after
failure or interruption. No measurement has been executed through this repair.

cross_envelope_v6.py reconstructs results through static audits under supplied
matching interpreters. Missing interpreters yield UNVERIFIABLE, not success.
It can also audit the three commit-bound historical packets; this does not
retroactively certify their first-attempt execution.

The frozen V5 uncertainty remains the finite observed envelope. Its development
cost exclusion, four-candidate scope and outcome-informed expectation remain.
No method here proves independent host provenance or global family preference.
