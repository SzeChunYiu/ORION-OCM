# H-family tranche A finite derivation theorems

## HA-1 — one target-independent lower grammar

At `SIGMA_HA`, `G_HA` has leaves `0,1,x0..x7`, operators `NOT`, `XOR`, `AND`,
node budget `B=5`, and the complete ecology `{0,1}^8`. Exhaustive generation
contains 10,050 syntax trees and exact semantic quotienting gives 718 classes.
The generator is executed once, before any row mapping is consulted. The
post-hoc classifier reads only a selected expression tree.

This is a finite theorem about `G_HA`, the complete cube, and `B=5`; it is not a
claim that the grammar is universal or that a named family is fully recovered.

**Assumptions.** The generator runs exactly once, before any row mapping is
consulted. The ecology is the complete cube `{0,1}^8`; the grammar has leaves
`0,1,x0..x7`, operators `NOT`, `XOR`, `AND`, and node budget `B=5`; semantic
quotienting is exact.

**Dependency.** Exhaustive generation, exact semantic quotienting, and the
post-hoc classifier are all implemented in this package at `SIGMA_HA`; the
frozen specification is `FREEZE_V1.md`. No H-family row mapping is consulted
during generation.

**Falsifiers.** A syntax tree within node budget `B=5` outside the 718 quotient
classes; a generator whose output changes when row mappings are reordered or
consulted early; a classifier that reads family labels during search.

**Strongest parents.** The requirement coordinates R01–R10 of the H-family
requirement ledger and the semantic no-smuggling audit; this theorem is the
finite `SIGMA_HA` instance of those coordinates.

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

**Assumptions.** Complete search over every tree in `G_HA` within node budget
`B=5`; cost is the node count; two expressions are equivalent exactly when
their truth tables are identical; the five contracts are generic (no family
macro embeds a family name).

**Dependency.** The exhaustive enumerator and exact semantic quotienting of
HA-1 at `SIGMA_HA`; the minimum-cost table is machine-produced by the package
checker; the source-separated oracle independently reproduces the costs.

**Falsifiers.** A tree of strictly lower node cost realizing any listed
contract; a different selected minimum or class on any of the eight registered
rows; oracle disagreement on any cost or class.

**Strongest parents.** HA-1 (the searched grammar); requirement coordinates
R01 (property prediction from ecology) and R04 (family-blind recovery).

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

**Assumptions.** Exact integer prices and horizon `H`; the AND3 minimum
spelling is structurally unique (exhaustive, from HA-2), so operator-tree
repricing cannot change the winner; the registered coordinate is the generic
serving allocation, not tree spelling.

**Dependency.** Structural uniqueness of the AND3 minimum spelling (HA-2
machinery); the two cost equations for replay and stored serving; the two exact
integer regimes `REPLAY_CHEAP` and `STORED_CHEAP`.

**Falsifiers.** A price regime under which the AND3 minimum spelling changes; a
horizon other than 1 at which stored serving first wins under the given prices;
a cheaper serving allocation within the two cost models.

**Strongest parents.** HA-2; requirement coordinate R07 (resource crossover).

## HA-4 — alternate encoding and independent search

Reversing candidate presentation order leaves the selected minimum and class
unchanged. Coordinate-label transport over cyclic permutations of `x0,x1,x2`
preserves the AND3 semantics and the post-hoc class. The source-separated
oracle independently enumerates/evaluates the same frozen specification and
reproduces all eight selected classes and costs.

**Assumptions.** Reversing candidate presentation order does not change the
selected minimum or class; cyclic permutations of the coordinate labels
`x0,x1,x2` preserve AND3 semantics and class; the oracle enumerates the same
frozen specification from source-separated code.

**Dependency.** The package checker and the source-separated
`independent_oracle_v1.py`; the frozen specification `FREEZE_V1.md`; the
coordinate-label transport implementation.

**Falsifiers.** An order reversal that changes the selected minimum or class; a
cyclic permutation of `x0,x1,x2` that changes the class; any oracle
disagreement on the eight registered classes or costs.

**Strongest parents.** HA-2; requirement coordinates R04 (family-blind
recovery) and R10 (independent search).

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

**Assumptions.** Each of rows H05, H06, H08, H10, H11, H12, H13, H14 earns ten
finite coordinates R01–R10 at `SIGMA_HA`; R11 is open; the complete binary cube
is finite and has no sha256-bound external data source, so it cannot satisfy
the registered real-scale definition; the R11 residual is operational/deferred,
not proved structural.

**Dependency.** The ten-gate finite ledger and reconciliation artifact in this
package; the H-family requirement ledger; the real-scale definition of record
(`gmi-833-h-real-scale-revival-v1`).

**Falsifiers.** A row where R01–R10 is not earned at `SIGMA_HA`; an
sha256-bound real-scale ecology that satisfies R11 for these rows; a forbidden
promotion (cross-scope gate composition, finite evidence implying real scale,
named-family closure) occurring.

**Strongest parents.** The H-family requirement ledger's eleven coordinates;
the real-scale definition of record.
