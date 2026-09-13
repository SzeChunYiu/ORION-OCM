# Structural threshold correction and analytic revival

The former full-class proof had three gaps: its four-input output grid omits
legal thresholds; fixed variable order need not minimize opcodes; four
delegation witnesses do not exclude a delegated class.

The repaired theorem proves r>=3 active hidden predicates and at least six
raw-input incidences. With the explicit flat-opcode contract these give
39 instructions per call for both registered source shapes, attained by the
existing shared-sum parity network. Arbitrary coefficient magnitudes and unit
counts are covered analytically. Delegated implementations remain outside
that exclusion.

Read STRUCTURAL_THRESHOLD_ANALYTIC_CORRECTION_V1.md, then PARENTS_AND_COSTS_V1.md.
The full portable receipt is STRUCTURAL_THRESHOLD_REPAIR_RECEIPT_V1.json.
Native interpreter identity and executions are retained separately in
VALIDATION_V1.json. Original #557 sources and receipt remain unchanged in raw/.

structural_threshold_analytic_v1.run() is independent of repository layout.
Its four helper modules can be copied byte-exact into grand for a thin adapter.
No generic threshold solver, timing experiment or physical family verdict
is claimed.
