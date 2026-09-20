# H-family tranche A finite derivation theorems

## HA-1 — one target-independent lower grammar

At `SIGMA_HA`, `G_HA` has leaves `0,1,x0..x7`, operators `NOT`, `XOR`, `AND`,
node budget `B=5`, and the complete ecology `{0,1}^8`. Exhaustive generation
contains 10,050 syntax trees and exact semantic quotienting gives 718 classes.
The generator is executed once, before any row mapping is consulted. The
post-hoc classifier reads only a selected expression tree.

This is a finite theorem about `G_HA`, the complete cube, and `B=5`; it is not a
claim that the grammar is universal or that a named family is fully recovered.

## HA-2 — exact minimum-cost recovery

Complete search gives the following exact minimum costs and structural classes:

| generic contract | minimum | selected expression | class |
|---|---:|---|---|
| `x3` | 1 | `x3` | `ADDRESSABLE_CONTEXT_READ` |
| `x0 AND x1 AND x2` | 5 | `AND(AND(x0,x1),x2)` | `THRESHOLD_CONJUNCTION` |
| `x4` | 1 | `x4` | `PERSISTENT_STATE_READ` |
| `0` | 1 | `0` | `BOOLEAN_COMPOSITION` |
| `x0 XOR x1 XOR x2` | 5 | `XOR(XOR(x0,x1),x2)` | `BOOLEAN_COMPOSITION` |

The lower bound is exhaustive: no tree of strictly lower node cost realizes the
same complete truth table. The eight registered rows reuse these contracts by
design, and family labels are attached only after this generic recovery.

## HA-3 — serving resource crossover

Tree-level operator repricing does not change the AND3 winner: its minimum
spelling is structurally unique. The registered resource coordinate is instead
the generic serving allocation for an addressable coordinate. At horizon `H`,
replay costs `H * leaf_read_price`; stored serving costs
`cell_write_price + H * cell_read_price`.

- `REPLAY_CHEAP`: `(leaf_read, cell_write, cell_read) = (1,5,1)`, so at `H=1`
  replay costs 1 and stored costs 6; replay remains cheaper.
- `STORED_CHEAP`: `(4,1,1)`, so at `H=1` replay costs 4 and stored costs 2;
  stored is cheaper (first stored-win horizon 1).

Thus the winner changes under two exact integer regimes. This is a serving
allocation theorem, not a claim that operator-tree spelling changes.

## HA-4 — alternate encoding and independent search

Reversing candidate presentation order leaves the selected minimum and class
unchanged. Coordinate-label transport over cyclic permutations of `x0,x1,x2`
preserves the AND3 semantics and the post-hoc class. The source-separated
oracle independently enumerates/evaluates the same frozen specification and
reproduces all eight selected classes and costs.

## HA-5 — scope and open gate

Rows H05, H06, H08, H10, H11, H12, H13, and H14 each have ten finite
coordinates in this package at `SIGMA_HA`: R01-R10. R11 is explicitly open.
The complete binary cube is finite and has no sha256-bound external data source,
so it cannot satisfy the registered real-scale definition. No row is closed and
no issue checkbox is changed. The R11 residual is operational/deferred, not
proved structural; it requires a separately frozen real-scale ecology and
laptop/remote execution.

Forbidden promotions: cross-scope gate composition, finite evidence implying
real scale, named-family closure, Section-H completion, universal grammar
neutrality, and independent-team replication.
