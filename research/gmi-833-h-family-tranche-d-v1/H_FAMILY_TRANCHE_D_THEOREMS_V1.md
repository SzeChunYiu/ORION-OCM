# H-family tranche D finite derivation theorems

## TD-1 — one target-independent lower grammar

At the registered scopes `SIGMA_TD01` … `SIGMA_TD09`, the shared neutral
grammar `G` of FREEZE_V1.md section 4 has leaves `0,1,x0..x7`, operators
`NOT`, `XOR`, `AND`, node budget `B=5`, and the complete ecology `{0,1}^8`.
Exhaustive generation contains 10,050 syntax trees and exact semantic
quotienting gives 718 classes: `c=1 -> 10`, `c=2 -> 8`, `c=3 -> 56`,
`c=4 -> 112`, `c=5 -> 532`. The grammar digest is
`16289266d044cb1c1e26e48e7df20c71767ee1064d9b19da65dbfa60dbea1b34`, identical
to the census and to tranche A `SIGMA_HA`. The generator executes once, before
any row mapping is consulted; the post-hoc structural classifier reads only a
recovered expression tree.

This is a finite theorem about `G`, the complete cube, and `B=5`; it is not a
claim that the grammar is universal or that a named family is fully recovered.

**Assumptions.** The generator runs exactly once, before any row mapping is
consulted. The ecology is the complete cube `{0,1}^8`; the grammar has leaves
`0,1,x0..x7`, operators `NOT`, `XOR`, `AND`, and node budget `B=5`; semantic
quotienting is exact; every reported quantity is an integer.

**Dependency.** Exhaustive generation, exact semantic quotienting, and the
post-hoc classifier are all implemented in this package at
`SIGMA_TD01`..`SIGMA_TD09`; the frozen specification is `FREEZE_V1.md`. No
Section-H row mapping is consulted during generation.

**Falsifiers.** A syntax tree within node budget `B=5` outside the 718 quotient
classes; a generator whose output changes when row mappings are reordered or
consulted early; a classifier that reads family labels during the search.

**Strongest parents.** The requirement coordinates R01–R10 of the H-family
requirement ledger and the semantic no-smuggling audit; this theorem is the
finite `SIGMA_TD01`..`SIGMA_TD09` instance of those coordinates.

## TD-2 — exact minimum-cost recovery

Complete family-blind search gives the following exact minimum node costs,
post-hoc structural classes and matched-negative-control rejections:

| row | registered scope | contract | cost | class | negative control rejected |
|---|---:|---|---|---|---|
| H35 | `SIGMA_TD01` | `XOR(x0,x5)` | 3 | `STOCHASTIC_SOURCE_CHANNEL` | yes (`XOR(x0,x1)` -> `PARITY_SIEVE`) |
| H36 | `SIGMA_TD02` | `AND(x0,x7)` | 3 | `EXTERNAL_PEER_TOOL_CHANNEL` | yes (`AND(x0,x1)` -> `CONJUNCTIVE_SIEVE`) |
| H37 | `SIGMA_TD03` | `AND(x2,x7)` | 3 | `EXTERNAL_PEER_TOOL_CHANNEL` | yes (`AND(x0,x1)` -> `CONJUNCTIVE_SIEVE`) |
| H38 | `SIGMA_TD04` | `XOR(x1,x7)` | 3 | `EXTERNAL_PEER_TOOL_CHANNEL` | yes (`XOR(x0,x1)` -> `PARITY_SIEVE`) |
| H39 | `SIGMA_TD05` | `XOR(XOR(x0,x1),x2)` | 5 | `TRIPLE_PARITY` | yes (`AND(AND(x0,x1),x2)` -> `CONJUNCTIVE_SIEVE`) |
| H40 | `SIGMA_TD06` | `AND(x0,x6)` | 3 | `UPDATE_FEEDBACK_CHANNEL` | yes (`AND(x0,x1)` -> `CONJUNCTIVE_SIEVE`) |
| H41 | `SIGMA_TD07` | `XOR(x0,x6)` | 3 | `UPDATE_FEEDBACK_CHANNEL` | yes (`XOR(x0,x1)` -> `PARITY_SIEVE`) |
| H42 | `SIGMA_TD08` | `AND(x1,x6)` | 3 | `UPDATE_FEEDBACK_CHANNEL` | yes (`x4` -> `PERSISTENT_STATE_READ`) |
| H43 | `SIGMA_TD09` | `XOR(x0,x7)` | 3 | `EXTERNAL_PEER_TOOL_CHANNEL` | yes (`AND(x0,x1)` -> `CONJUNCTIVE_SIEVE`) |

The lower bound is exhaustive: no tree of strictly lower node cost realizes the
same complete truth table (zero strictly cheaper candidates per row). The
channel labels are the registered contract names of
`gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json`; they are
attached only after recovery.

**Assumptions.** Complete search over every tree in `G` within node budget
`B=5`; cost is the node count; two expressions are equivalent exactly when
their truth tables over the complete cube are identical; the nine contracts are
generic (no family macro embeds a family name).

**Dependency.** The exhaustive enumerator and exact semantic quotienting of
TD-1 at the nine registered scopes; the minimum-cost table is machine-produced
by `tranche_d_v1.py`; the source-separated oracle independently reproduces the
costs and classes.

**Falsifiers.** A tree of strictly lower node cost realizing any listed
contract; a recovered class different from the predicted class on any of the
nine rows; a matched negative control recovered as the predicted class; oracle
disagreement on any cost or class.

**Strongest parents.** TD-1 (the searched grammar); requirement coordinates
R01 (property prediction from the ecology) and R04 (family-blind recovery).

## TD-3 — serving resource crossover

The registered resource coordinate is the generic serving allocation for each
golden's protected channel. At horizon `H` and `r` channel read-sites per serve
position (`r = 2` for eight rows, `r = 3` for `SIGMA_TD05`):

- replay: every read-site re-reads the channel at every serve position:
  `cost = H * r * leaf_read_price`;
- stored: every read-site loads its own cell once up front, and each serve
  position reads the loaded cells in one pass:
  `cost = r * cell_write_price + H * cell_read_price`.

Two frozen exact integer regimes:

| regime | leaf_read | cell_write | cell_read |
|---|---|---|---|
| `REPLAY_CHEAP` (A) | 1 | 5 | 1 |
| `STORED_CHEAP` (B) | 4 | 1 | 1 |

Under regime A the replay plan wins at `H = 1` (`2` vs `11` for `r = 2`; `3` vs
`16` for `r = 3`) and the stored plan strictly overtakes at the registered
horizon `H = 11` (`r = 2`) and `H = 8` (`r = 3`). Under regime B the stored
plan wins at every `H >= 1` (`8` vs `3` for `r = 2`; `12` vs `4` for `r = 3`).
The winners differ between the regimes in all nine rows, so the crossover is
exact, integer, and reported per row. This is a serving-allocation theorem, not
a claim that operator-tree spelling changes.

**Assumptions.** Exact integer prices and horizon `H`; each golden composite
reads its protected channel `r` times per serve position; the two cost
equations for replay and stored serving; the two frozen integer regimes.

**Dependency.** The frozen cost law of FREEZE_V1.md section 8; the generic
serving-allocation model of the tranche A and classical `A5` precedents.

**Falsifiers.** A price regime under which the recorded winners do not reverse;
a horizon other than the registered crossing at which the stored plan first
wins under regime A; a cheaper serving allocation within the two cost models.

**Strongest parents.** TD-2; requirement coordinate R07 (resource crossover).

## TD-4 — independent regeneration and independent search

Reversing candidate presentation order leaves the recovered minimum and its
post-hoc class unchanged in all nine rows (order-reversal regeneration).
Coordinate-label transport over all non-identity permutations of the golden's
own coordinates preserves both the golden's truth table and its post-hoc class
in all nine rows (`1/1` transports for the two-coordinate rows, `5/5` for
`SIGMA_TD05`). The source-separated oracle independently enumerates and
evaluates the same frozen specification and reproduces all nine recovered
classes and costs (`R10` holds when the oracle agrees on every scope's
minimal-cost class and cost).

**Assumptions.** Reversing candidate presentation order does not change the
recovered minimum or class; permuting the golden's coordinate labels preserves
semantics and class; the oracle enumerates the same frozen specification from
source-separated code that imports nothing from this package.

**Dependency.** `tranche_d_v1.py` and the source-separated
`independent_oracle_v1.py`; the frozen specification `FREEZE_V1.md`; the
coordinate-label transport implementation.

**Falsifiers.** An order reversal that changes the recovered minimum or class;
a coordinate permutation of a golden that changes its class; any oracle
disagreement on the nine registered classes or costs.

**Strongest parents.** TD-2; requirement coordinates R09 (independent
regeneration) and R10 (independent search).

## TD-5 — scope and open gate

Rows H35–H43 each earn ten finite coordinates in this package at one registered
scope (`R01`–`R10` at `SIGMA_TD01`..`SIGMA_TD09`). `R11` is explicitly open on
every row with reason `OPEN_REAL_SCALE_PENDING`: the complete binary cube is a
finite point set with no sha256-bound external byte-source analogue for the
frozen contracts, so it cannot satisfy the registered real-scale definition
(`n_fit >= 100000`, `n_held >= 20000`, sha256-bound real source, exact held-out
arithmetic, laptop/remote execution). The `R11` residual is operational and
deferred, not proved structural; it requires a separately frozen real-scale
ecology, which is the coordinator's next unit after this package merges. No row
is closed and no issue checkbox is changed.

Forbidden promotions: cross-scope gate composition, registered control
substitution, post-hoc falsifier replacement, ecology iteration until positive,
independent-team replication, real-scale validation complete, finite evidence
implying real scale, Section-H completion, all-known-form recovery, universal
grammar neutrality, frontier-scale validation, named-family row closed at real
scale, and complete GMI.

**Assumptions.** Each of rows H35–H43 earns ten finite coordinates `R01`–`R10`
at its own `SIGMA_TD01`..`SIGMA_TD09`; `R11` is open with the registered
attribution; the complete binary cube is finite and has no sha256-bound
external data source, so it cannot satisfy the registered real-scale
definition; the `R11` residual is operational and deferred, not proved
structural.

**Dependency.** The ten-gate finite ledger and reconciliation artifact in this
package; the H-family requirement ledger; the real-scale definition of record
(`gmi-833-h-real-scale-revival-v1`).

**Falsifiers.** A row where `R01`–`R10` is not earned at its own registered
scope; an sha256-bound real-scale ecology that satisfies `R11` for these rows;
a forbidden promotion (cross-scope gate composition, finite evidence implying
real scale, named-family row closed) occurring.

**Strongest parents.** The H-family requirement ledger's eleven coordinates;
the real-scale definition of record.
