# Threshold-task frontier: the answer to PN-5's residual question

The parity-n registration closed by saying a neural win "requires a task whose
structure favours a threshold unit, which is separate work". That work is here,
on majority-n, in DCR's typed register and with DCR's own instrument.

Two results, in opposite directions, both derived rather than sampled:

- **No strict neural win is available in the opcode-only coordinate, on any
  task, at any n.** The cheapest constant table costs `3n + 4` whatever the task
  computes, nothing in the register costs less than `3n + 2`, and nothing that
  needs a constant costs less than `3n + 4`. The threshold form can tie the
  table and never beat it. The obstruction is the coordinate, not the family.
- **Charge a constant cell at any positive rate and the threshold form strictly
  dominates the table** at `(3n + 4, 1)` against `(3n + 4, 2**n)`, for every n
  in 3..8. That is the first structurally neural realization to strictly beat a
  registered non-neural one anywhere in this evidence line.

Supporting facts, all exhaustive at their declared scope:

- majority-n has no constant-free realization at n = 3, 4 at any budget below
  the one-constant `3n + 4` shape — `3n + 2`, `3n + 3` and the two-unary
  `3n + 4` are all empty — so its minimum is `3n + 4`, attained;
- the `3n + 4` optimum is attained by a threshold rendering **and** by a
  non-affine one, `((v0 + v1) << v2) > 1`, so minimal cost does **not** force
  the threshold structure. That claim is refuted here, not assumed;
- the parity-n figure for a lookup table, `5n + 2`, is corrected: the flat-index
  rendering costs `5n + 4` and the nested rendering `3n + 4`. PN-3's conclusion
  survives and is strengthened.

- [Theorem, scope and residue](THRESHOLD_TASK_FRONTIER_THEOREM_V1.md): TT-1..TT-7.
- [Measured constant footprint](MEASURED_CONSTANT_FOOTPRINT_V1.md): TB-1..TB-6,
  which discharges TT-6's pricing premise with two exact measured sizes. The
  domination survives both; from n = 5 the in-memory measure makes the threshold
  rendering the **unique** undominated realization, because its single constant
  is an interned integer costing no incremental memory. It also withdraws the
  nested-versus-flat table ranking the count coordinate produced: measured, the
  two are incomparable.
- [Complete payload](RECEIPT_V1.json) from `check_frontier_v1.py`.
- [Portable replay](REPLAY_V1.md) and [complete bindings](MANIFEST_V1.json).

These are finite source-and-coordinate results. No timing, no physical memory,
no coverage of unwritten realizations, and nothing about learning.

One correction is recorded in §10 of the theorem rather than quietly fixed: the
first version of TT-2 claimed no written realization costs `3n + 3`, which is
false because each admitted unary operation costs one opcode, and the
enumeration behind TT-3 searched binary operations only. Cursor Bugbot raised it
in review on PR #619. The search now spends a unary budget and the conclusions
are unchanged.
