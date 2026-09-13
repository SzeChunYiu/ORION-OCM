# Parity-n cost predictions: preregistration

Status: **PREDICTIONS DERIVED AND REGISTERED; NOT YET MEASURED**

This registers numeric predictions for parity-n at n = 4, 5, 6 in the repaired
coordinate `(opcodes, unaccounted_calls)` of
[DIC-1-6](DELEGATION_INVARIANT_COST_PREREGISTRATION_V1.md), **before** any n > 3
realization is compiled or counted. Its purpose is to make the empirical line
falsifiable across a task family instead of resting on the single parity-3 point.

## Derivation, not measurement

Every number below comes from the registered flat opcode contract applied
symbolically to n inputs. No n > 3 candidate was compiled, traced or counted to
produce them. The formulas are validated only against the three registered n = 3
facts, which they reproduce exactly:

| family | formula at n=3 | registered n=3 |
|---|---|---|
| written XOR chain | (11, 0) | (11, 0) |
| written shared-sum threshold net | (39, 4) | (39, 4) |
| written lookup table | (17, 0) | (17, 0) |
| `sum(x) & 1` | (6, 1) | (6, 1) |

## PN-1 .. PN-5, stated so they can fail

- **PN-1** The written XOR chain costs `3n + 2` opcodes per call with zero
  unaccounted calls.
- **PN-2** The written shared-sum threshold net costs `11n + 6` opcodes per call
  with `n + 1` unaccounted calls, and is therefore dominated by the XOR chain at
  every n in {4, 5, 6}.
- **PN-3** The written lookup table costs `5n + 2` opcodes per call, **not**
  `2^n`. A constant table compiles to one `LOAD_CONST`, so this coordinate does
  not charge table size at any n. This contradicts the intuition that a lookup
  table is penalised for its `2^n` entries: in this coordinate it is not.
- **PN-4** No crossover occurs in {4, 5, 6}. The undominated set stays
  `{written XOR chain, sum(x) & 1}` at every n, with `sum(x) & 1` incomparable at
  a constant 6 opcodes per call independent of n.
- **PN-5** The neural family never becomes undominated at any n in {4, 5, 6}.
  A neural win therefore cannot be produced by enlarging n; it requires a task
  whose structure favours a threshold unit, which is separate work.

## Predicted values per full domain sweep (2^n inputs)

| n | XOR chain | shared-sum net | lookup table | `sum(x) & 1` |
|---|---|---|---|---|
| 4 | (224, 0) | (800, 80) | (352, 0) | (96, 16) |
| 5 | (544, 0) | (1952, 192) | (864, 0) | (192, 32) |
| 6 | (1280, 0) | (4608, 448) | (2048, 0) | (384, 64) |

## What a failure would mean

A measured value differing from the formula falsifies that family's clause and is
recorded as a failure, not adjusted away. The registration is frozen before
measurement precisely so that outcome remains available.

## What this does not establish

PN-3 makes explicit that this coordinate omits table size, so none of these
predictions speak to memory, timing or any physical cost. No family verdict
extends beyond the registered straight-line grammar, and no claim here is an
independent replication.
