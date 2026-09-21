# gmi-833-h-family-tranche-d-v1 — CORE

**What this is.** A registered-scope evidence package for the nine remaining
Section-H rows of issue #833 (the exotic family rows that were unclaimed after
tranches A, B and C). Every row is reported **open with an attribution**; no
row is closed, because the real-scale coordinate (`R11`) is registered
`OPEN_REAL_SCALE_PENDING` and a closed row requires all eleven coordinates at
one scope.

## The nine rows and their registered protected contracts

| row | registered scope | protected channel | contract | cost |
|---|---|---|---|---|
| Evolutionary/population search. | `SIGMA_TD01` | `STOCHASTIC_SOURCE_CHANNEL` | `XOR(x0,x5)` | 3 |
| Cellular/local-field computation. | `SIGMA_TD02` | `EXTERNAL_PEER_TOOL_CHANNEL` | `AND(x0,x7)` | 3 |
| Distributed/collective intelligence. | `SIGMA_TD03` | `EXTERNAL_PEER_TOOL_CHANNEL` | `AND(x2,x7)` | 3 |
| Tool-using/solver-routing intelligence. | `SIGMA_TD04` | `EXTERNAL_PEER_TOOL_CHANNEL` | `XOR(x1,x7)` | 3 |
| Neuro-symbolic/statistical-symbolic hybrids. | `SIGMA_TD05` | `TRIPLE_PARITY` | `XOR(XOR(x0,x1),x2)` | 5 |
| Continual-learning systems. | `SIGMA_TD06` | `UPDATE_FEEDBACK_CHANNEL` | `AND(x0,x6)` | 3 |
| Meta-learning systems. | `SIGMA_TD07` | `UPDATE_FEEDBACK_CHANNEL` | `XOR(x0,x6)` | 3 |
| Self-modifying/morphogenetic systems. | `SIGMA_TD08` | `UPDATE_FEEDBACK_CHANNEL` | `AND(x1,x6)` | 3 |
| Multi-agent emergent communication systems. | `SIGMA_TD09` | `EXTERNAL_PEER_TOOL_CHANNEL` | `XOR(x0,x7)` | 3 |

## What is earned at each registered scope

- One shared neutral grammar `G` (leaves `0,1,x0..x7`; operators `NOT`, `XOR`,
  `AND`; node budget `B=5`; complete ecology `{0,1}^8`; digest
  `16289266d044cb1c1e26e48e7df20c71767ee1064d9b19da65dbfa60dbea1b34`), the same
  grammar as the census and tranche A. Family names never reach the grammar,
  the search or the post-hoc classifier; they are attached only after recovery
  by the mapping in `POSTHOC_MAPPING_V1.json`.
- Per row: exact minimum-cost recovery at the predicted class (9/9), matched
  negative control rejected (9/9), exhaustive lower bound (zero strictly
  cheaper candidates), held-out frozen predictions over a disjoint contract set
  (6/6), deterministic null batteries recovering 0/N (0/200, `SIGMA_TD05`
  0/182), serving-resource crossover crossing in all nine rows, independent
  regeneration (order reversal + coordinate transport) preserved in all nine
  rows, and a source-separated oracle that agrees on all nine rows.
- Every reported quantity is an integer; no float enters any comparison, count
  or claim.

## Status

- 9 of 9 rows: 10 of 11 coordinates at one registered scope each, with the
  source-separated oracle agreeing in normal and optimized Python.
- 0 of 9 rows closed. `R11` is open on every row with reason
  `OPEN_REAL_SCALE_PENDING` and the registered attribution.
- The claim ceiling is
  `TRANCHE_D_NAMED_FAMILY_CONTRACT_DERIVED_AT_REGISTERED_FINITE_SCOPE__REAL_SCALE_OPEN_PENDING`.

## Reproduction

```
cd research/gmi-833-h-family-tranche-d-v1
python3 -I -B independent_oracle_v1.py     # route B, writes ORACLE_RESULT_V1.json
python3 -I -B tranche_d_v1.py              # route A, writes RESULT_V1.json
python3 -I -B test_tranche_d_v1.py -v
python3 -I -O -B test_tranche_d_v1.py -v
```
