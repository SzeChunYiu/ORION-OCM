# FREEZE_V2_ADDENDUM — registered corrections before the checker re-run

Committed before any change to `family_tranche_a_v1.py` or
`independent_oracle_v1.py`, and before any re-run. `FREEZE_V1.md` stands
unchanged. This addendum fixes the exact definitions of three coordinates whose
first implementation was not faithful to the closed precedent, and it
re-registers `R01` and `R08` on non-shared evidence keys. It adds no row, no
family, no ecology, and relaxes nothing.

## 1. R01 — property prediction from the ecology, on a DISTINCT evidence key

The first run discharged `R01` with the same equality as `R04`
(`recovered == predicted`). The ledger precedent names `R01`/`R08` sharing one
evidence key as a defect, and the classical packages discharge `R01` by
predictions about the ecology that are NOT the recovery class.

`R01` is therefore discharged by phenomena predicted from the **ecology
specification alone** (complete cube, all eight coordinates excited, budget
`B = 5`, the registered cost model), frozen here before any checker change:

- `P-A01`: on the complete cube ecology the context contract `x3` realises at
  exact minimum node cost 1 (a single coordinate leaf), and this minimum is
  attained by reading the coordinate — a leaf read, not composition.
- `P-A02`: on the complete cube ecology the threshold contract
  `x0 AND x1 AND x2` realises at exact minimum node cost 5, with the unique
  minimum-cost spelling a `AND`-rooted chain (three distinguishes reads, two
  composition operators).
- `P-A03`: on the complete cube ecology the history/state contract `x4`
  realises at exact minimum node cost 1.
- `P-A04`: on the complete cube ecology the constant-zero twin realises at
  cost 1 and the parity twin `x0 XOR x1 XOR x2` at cost 5.

These are exact counting statements about the ecology that the search then
confirms; `R04` (recovered class equals predicted class) remains a separate
key. `R01` is true iff `P-A01`–`P-A04` hold under the family-blind search.

## 2. R07 — resource crossover, made exact, with a winner flip

The first run priced operator nodes for the AND3 contract and found the same
`AND`-chain unique under both regimes — a genuine structural fact (AND3 has a
unique minimum-cost realisation over this grammar) that does not, by itself,
satisfy `R07`. Following the `SIGMA_4F` STATE-1 and the classical A5
precedents, `R07` is registered at the **serving-allocation** level for a
single registered coordinate (the context contract `x3`, and identically the
state contract `x4`):

A serve plan must provide the value of the registered coordinate at each of
`H` serve positions. Two plans:

- **replay**: read the coordinate at every serve position:
  `cost = H * leaf_read_price`.
- **stored**: load the coordinate once into one cell, then read the cell per
  position: `cost = cell_write_price + H * cell_read_price`.

Two frozen exact integer price regimes:

| regime | leaf_read | cell_write | cell_read |
|---|---|---|---|
| `REPLAY_CHEAP` (A) | 1 | 5 | 1 |
| `STORED_CHEAP` (B) | 4 | 1 | 1 |

**Prediction (frozen before this re-run):** under regime A the replay plan is
the strict charged winner for every horizon `H >= 1` (`1 + 5H > H` for the
stored plan); under regime B the stored plan is the strict winner at every
`H >= 1` (`1 + H < 4H`). The winners differ between the two regimes at every
horizon, so the crossover is exact, integer, and reported per contract. The
first-run operator-node comparison stands as a labelled diagnostic showing a
tree-level uniqueness that does not flip (`R07` is earned at the allocation
level, exactly as in the parents).

## 3. R08 — held-out frozen prediction over a DISJOINT contract set

The first run's `held_out` claim compared `sclass == predicted_class` on the
same evaluated ecology — the parent's `R01`/`R08` shared-key defect.
`R08` is re-registered as a prediction over a contract set **disjoint** from
the evaluated one, frozen here before any evaluation:

- evaluated contract set `C_eval = {x3, x4, x0 AND x1 AND x2}`;
- held-out contract set `C_held = {x5, x0 AND x1}` — every truth table in
  `C_held` differs from every truth table in `C_eval`;
- **frozen prediction**: the same family-blind search (same grammar, same
  budget, same classifier) recovers, on `x5`, cost exactly 1 and class
  `ADDRESSABLE_CONTEXT_READ`; on `x0 AND x1`, cost exactly 3 and class
  `THRESHOLD_CONJUNCTION`.

The held-out evaluation is then a single, pre-frozen read of those two
contracts under the unchanged search; `R08` is true iff both predictions hold.

## 4. R03 — semantic no-family-macro audit, causal-code scope

The first run scanned the entire executor source and reported hits coming from
the disclosed post-hoc `ROWS` registry and the audit's own name list — the
same names the classical and revival executors carry in their `ROW`/`ROWS`
dictionaries. Those registries apply names only after recovery and are not
causal code. The audit therefore scans the **causal code only**:

1. the grammar module `grammar_ha_v1.py` in full;
2. the source of the causal functions in the executor —
   `enumerate_candidates`, `select_minimum`, `structural_class`,
   `_class_of_tree`, `_contains`, `cost_regime`, `min_cost_regime`,
   `crossover_block`, `remint_block`, `permute_label`, and the additive
   served-plan accounting — extracted with `inspect.getsource`;

under the zero-hit predicate for every registered row/family-name token. The
audit result is the single Boolean conjunction of all zero-hit predicates;
`R03` is false if any causal source contains a family-name token. The audit
also asserts the grammar digest is identical before and after every search
(`R02`'s shared-grammar key).

## 5. Per-row predicted classes, unchanged

`FREEZE_V1.md` predicted `ADDRESSABLE_CONTEXT_READ` for H05/H06/H11,
`THRESHOLD_CONJUNCTION` for H08/H10/H12/H13, and `PERSISTENT_STATE_READ` for
H14. Those predictions stand.

## 6. R11 — registered, deferred, with reason

`R11` (real-scale, `n_fit >= 100,000`, `n_held >= 20,000`, sha256-bound SOURCE
data, exact arithmetic, laptop/remote host) is not run in this tranche. The
reason is registered: every ecology here is the complete 256-point truth-table
cube — a finite point set with no external byte-source analogue for the frozen
contracts, and building a real-scale ecology whose protected behavior IS one of
the registered contracts is a separate construction that FREEZE_V1.md does not
register. Per the caller's rule, a row with 10/11 closes only if the missing
gate is proved structural; `R11` is a runnable test, so it stays open with this
attribution on every row. Deferred, not claimed.

## 7. Custody

This file is committed before any change to the checker or the oracle and
before any re-run. CI asserts `FREEZE_V1.md` predates `FREEZE_V2_ADDENDUM.md`
predates the executor's second version.
