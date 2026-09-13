# Parity-n cost predictions (P1a): read first

Registers numeric predictions for parity-n at n = 4, 5, 6 in the repaired
`(opcodes, unaccounted_calls)` coordinate **before** any n > 3 realization is
compiled or counted.

- [Preregistration](PARITY_N_PREDICTION_PREREGISTRATION_V1.md) — clauses PN-1..PN-5 with falsifiers.
- [Derivation](parity_n_derivation_v1.py) — formulas only; validated against the
  registered n=3 facts (11,0), (39,4), (17,0), (6,1), which it reproduces exactly.

Status: **NOT YET REGISTERED IN THE REPLAY CAPSULE, NOT YET MEASURED.** This unit
is staged so the predictions are durable and timestamped ahead of measurement; it
is deliberately outside `research/gmi-grand-unification-v1/` so it cannot perturb
that sector's registered input set until it is properly registered.

PN-3 contradicts the common expectation that a lookup table is penalised for its
`2^n` entries: a constant table is one `LOAD_CONST`, so this coordinate does not
charge table size at all. That is a declared blind spot, not a result about memory.
