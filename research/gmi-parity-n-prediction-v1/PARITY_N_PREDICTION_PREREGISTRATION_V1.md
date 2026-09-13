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

## Correction 2026-09-13: PN-3's scope, after the DIC coordinate was superseded

The coordinate these predictions were written against (DIC, PR563) was corrected by
DCR-1-4 (PR565). Two confirmed defects in DIC, both reproduced independently:

- a `functools.partial` wrapping a Python callee scored `(32, 8)` against `(344, 32)`
  for the same callee invoked directly, because DIC recursed only into callees carrying
  `__code__` and never followed `partial.func`, which does carry one. That is a
  counterexample to DIC-5: the wrapped form dominates its parent in **both** components.
- a user-defined `__getitem__` scored `(136, 0)` with no callee recorded, so descendant
  Python work was charged to neither component.

**Effect on PN-1..PN-5:** the per-call formulas are unchanged, because every registered
parity-n realization here uses only exact constant tuples, exact int/bool arithmetic and
named calls to `int`/`sum` - all inside the typed register DCR admits. **PN-3 must be read
with that restriction made explicit:** a lookup table costs `5n+2` rather than `2^n`
*only when the table is an exact constant tuple*. An arbitrary object with a Python
`__getitem__` is not cheap; under DCR it is refused before its method is invoked, and
under DIC it was silently scored as free. The blind spot PN-3 declares is therefore about
constant-table **size**, not about subscription in general.

These predictions must be re-validated against DCR's trace semantics before registration.

## OUTCOME 2026-09-13, measured against DCR on main@d61a2ec6

Executed with DCR's own typed machine (`Program` + `typed_machine_v1.execute`) on
CPython 3.12.14, over all 2^n inputs, n = 3,4,5,6. The PN clauses above are left
**verbatim**: a failed prediction is a result, not something to edit away.

### PN-1, PN-2, PN-3 — CONFIRMED, 16 of 16 exact

Python opcodes per sweep, predicted vs measured, all MATCH:

| n | XOR chain | shared-sum net | lookup table | `sum(x)&1` |
|---|---|---|---|---|
| 3 | 88 | 312 | 136 | 48 |
| 4 | 224 | 800 | 352 | 96 |
| 5 | 544 | 1952 | 864 | 192 |
| 6 | 1280 | 4608 | 2048 | 384 |

Native obligations: XOR 0, lookup 0, shared-sum net `(n+1)*2^n` (32/80/192/448),
delegating `2^n` (8/16/32/64). PN-3 holds: the lookup table is `5n+2`, not `2^n`,
because an exact constant tuple is one `LOAD_CONST`.

### PN-4 and PN-5 — FALSIFIED

Both clauses asserted an ordering (XOR stays undominated; the neural family never
wins; `sum(x)&1` stays incomparable). Both depended on treating native obligations as
a second **minimised** component. DCR does not do that, and the ordering fails on both
available readings:

- Under DCR-3's **implemented** contract (py events cost 1, native and adapter
  obligations cost 0 Python opcodes), `separation(delegating, XOR)` =
  **`CERTIFIED_STRICTLY_LOWER`** at n=3 (48 vs 88) and n=6 (384 vs 1280). The
  delegating form certifiably **wins**.
- Under the honest-unknown reading (DCR-3: an absent bound is `[0, infinity)`), the
  delegating bounds are `(48, None)` and `(384, None)`, so `separation` returns
  **`UNVERIFIABLE`** at both n. No ordering claim is certifiable in either direction.

So PN-4/PN-5 are neither true in the certifying coordinate nor rescuable by appealing
to unbounded native work. The transportable content of this registration is the count
formulas, not any family verdict.

### Why this happened

The formulas were derived against DIC, whose second component was minimised alongside
opcodes. DCR replaced DIC precisely because that second component was unsound (a
`functools.partial` scored `(32,8)` against `(344,32)` for the same callee called
directly). Removing the unsound component removed the basis for the ordering claims,
while leaving the counts untouched.

## REVIVAL 2026-09-13: PN-4 recovered as an n-dependent positive, PN-5 restored

The earlier outcome recorded PN-4 and PN-5 as falsified. That was attributed to one
stage and re-tested rather than filed: the failure was in the **cost contract**, not
in the formulas. DCR-3 charges native obligations **zero** Python opcodes and treats a
missing bound as `[0, infinity)`, so `sum(x)&1` appeared cheaper than written XOR only
because its native work was priced at nothing - an unpriced-resource artifact.

**Lever applied:** a sound *lower* bound `l` on native work per call, in the same
Python-opcode units, which `separation` can use. Certification of XOR over `sum(x)&1`
requires `2^n * (3n+2) < 2^n * (6 + l)`, i.e. `l > 3n - 4`.

**PN-5 was never falsified.** `separation(XOR, shared-sum net)` returns
`CERTIFIED_STRICTLY_LOWER` at **every** nonnegative `l`, including `l = 0`, at n = 3
and n = 6. The neural form never wins, unconditionally. The earlier blanket statement
was too broad.

**PN-4 recovers under a faithful charge, with an exact crossover.** A faithful native
charge for `sum` over an n-tuple is `l(n) = 2n + 1` (n loads, n-1 additions, one
return). Measured with DCR's own machine:

| n | faithful `l` | threshold `l > 3n-4` | XOR | delegating lower | verdict |
|---|---|---|---|---|---|
| 3 | 7 | 5 | 88 | 104 | CERTIFIED_STRICTLY_LOWER |
| 4 | 9 | 8 | 224 | 240 | CERTIFIED_STRICTLY_LOWER |
| 5 | 11 | 11 | 544 | 544 | UNVERIFIABLE (exact tie) |
| 6 | 13 | 14 | 1280 | 1216 | delegation strictly cheaper |
| 7 | 15 | 17 | 2944 | 2688 | delegation strictly cheaper |
| 8 | 17 | 20 | 6656 | 5888 | delegation strictly cheaper |

**Revived claim (PN-4R).** Under a faithful per-element native charge, written XOR is
certifiably cheaper than `sum(x)&1` exactly for `n <= 4`; at `n = 5` the bounds coincide
exactly at 544; for `n >= 6` the delegating form is strictly cheaper.

**Structural boundary.** `2n + 1 > 3n - 4` iff `n < 5`, so **no fixed constant charge
rescues the original ordering at all n**. The delegating form's per-call cost is constant
in n while the XOR chain's grows as `3n + 2`, so delegation must eventually win. The
original PN-4 was wrong because it asserted a uniform ordering where the true statement
is a crossover.

**Falsifier for PN-4R.** Exhibit a faithful native charge and an `n <= 4` at which XOR is
not certified, or an `n >= 6` at which it is.

## What this does not establish

PN-3 makes explicit that this coordinate omits table size, so none of these
predictions speak to memory, timing or any physical cost. No family verdict
extends beyond the registered straight-line grammar, and no claim here is an
independent replication.
