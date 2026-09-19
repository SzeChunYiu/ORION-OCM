# FREEZE_V2_ADDENDUM — registered corrections before the second checker run

Committed before any change to `family_tranche_a_v1.py` and before the re-run
that follows. `FREEZE_V1.md` stands unchanged. This addendum fixes the exact
definitions of three coordinates whose first implementation was not faithful.
It adds no row, no family, no ecology, and relaxes nothing.

## 1. R03 — semantic no-family-macro audit, made exact

The first run's audit scanned the whole executor source for family-name tokens
and reported hits that come from the **post-hoc row registry** (`ROWS` in the
executor). That registry is the disclosed post-hoc mapping applied only after
selection; it is not causal code. The audit must scan the **causal code** only:

1. the grammar module `grammar_ha_v1.py` in full;
2. the source of the causal functions in the executor —
   `enumerate_candidates`, `select_minimum`, `structural_class`,
   `_class_of_tree`, `_contains`, `cost_regime`, `min_cost_regime`,
   `crossover_block`, `remint_block`, `permute_label` — extracted with
   `inspect.getsource`;

under the zero-hit predicate for every registered family-name token. The
audit's result is a single Boolean (`R03` is true iff all zero-hit predicates
hold); the per-source detail is diagnostic only.

## 2. R07 — charged-cost resource crossover at the serving-allocation level

The first run's crossover priced operator nodes and found the AND3 realisation
unique under both regimes — a genuine structural fact (the registered contract
has a unique minimum-cost tree), but `R07` requires a winner change under two
price regimes. Following the `SIGMA_4F` precedent (STATE-1: persistence vs
replay, with the charged serve vector), the crossover is registered at the
**serving-allocation** level for the addressable-context contract `x3` (the
same serving model applies to `x4`):

A serve plan must provide the value of the registered coordinate at each of
`H` serve positions. Two arms:

- **re-read**: read the coordinate at every serve position:
  `cost = H * leaf_read_price`.
- **stored**: load the coordinate once into one cell, then read the cell per
  position: `cost = cell_write_price + H * cell_read_price`.

Two frozen price regimes, exact integers:

| regime | leaf_read | cell_write | cell_read |
|---|---|---|---|
| `REPLAY_CHEAP` (A) | 1 | 1 | 5 |
| `STORED_CHEAP` (B) | 4 | 1 | 1 |

**Prediction (frozen before this re-run):** under regime A the re-read arm is
the strict winner for every `H >= 1`; under regime B the stored arm is the
strict winner at `H* = 1` and below the crossing `H < 1` the re-read arm wins.
The winners differ between the two regimes at `H = 1`, so `R07` is earned
exactly and the numbers are exact integers. The smallest `H` at which the
stored arm first beats re-read in regime B is reported exactly (`H* = 1`).

## 3. R08 — held-out frozen prediction over a DISJOINT contract set

The first run reused the evaluated contracts for the held-out claim, which is
the parent's `R01`/`R08` shared-key defect. `R08` is re-registered as a
prediction over a contract set disjoint from the evaluated one, frozen here
before any evaluation:

- evaluated contract set `C_eval = {x3, x0 & x1 & x2, x4}`;
- held-out contract set `C_held = {x5, x6, x1 & x2}` — no coordinate and no
  conjunction used in `C_eval` occurs in `C_held`, and vice versa;
- **frozen prediction:** the same family-blind search (same grammar, same
  budget, same classifier) recovers, on `x5` and `x6`, the class
  `COORDINATE_READ` at cost exactly 1; on `x1 & x2`, the class
  `THRESHOLD_CONJUNCTION` at cost exactly 3.

**Post-hoc structural classes, frozen (this addendum), read only from the
expression tree:**

1. depends on the registered state probe `x4` -> `PERSISTENT_STATE_READ`;
2. else depends on the registered context probe `x3` ->
   `ADDRESSABLE_CONTEXT_READ`;
3. else root is `AND` -> `THRESHOLD_CONJUNCTION`;
4. else a leaf over a coordinate not in `{x3, x4}` -> `COORDINATE_READ`;
5. else -> `BOOLEAN_COMPOSITION`.

## 4. The per-row predicted classes, unchanged

`FREEZE_V1.md` predicted `ADDRESSABLE_CONTEXT_READ` for H05/H06/H11,
`THRESHOLD_CONJUNCTION` for H08/H10/H12/H13, and `PERSISTENT_STATE_READ` for
H14. Those predictions stand and are not amended by this addendum.

## 5. Custody

This file is committed before any change to `family_tranche_a_v1.py` and
before any re-run. CI asserts `FREEZE_V1.md` predates `FREEZE_V2_ADDENDUM.md`
predates the executor's second version.
