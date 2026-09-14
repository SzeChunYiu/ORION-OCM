# Threshold-task frontier: can the neural family ever win?

Status: **DERIVED + EXHAUSTIVELY ENUMERATED AT FINITE SCOPE; ONE NEGATIVE AND ONE
POSITIVE RESULT**
Date: 2026-09-14

Parent machinery: DCR's typed register and typed machine
([TYPED_DELEGATION_COST_THEOREM_V1](../gmi-delegation-cost-repair-v1/TYPED_DELEGATION_COST_THEOREM_V1.md),
`typed_program_v1.py`, `typed_machine_v1.py`, `cost_contracts_v1.py`), and the
interval certificate PNIR-1 of
[INTERVAL_COST_CORRECTION_V1](../gmi-parity-n-prediction-v1/INTERVAL_COST_CORRECTION_V1.md).
Checker: `check_v1.py`. Receipt: `RECEIPT_V1.json`.

## 1. The gap this closes

The parity-n registration ends by naming exactly one thing it cannot do:

> **PN-5** The neural family never becomes undominated at any n in {4, 5, 6}.
> A neural win therefore cannot be produced by enlarging n; it requires a task
> whose structure favours a threshold unit, **which is separate work**.

That separate work is done here. The task whose structure favours a threshold
unit is majority-n, and the question is whether the registered cost coordinate
can ever return a verdict in favour of a structurally neural realization.

The answer has two halves, and they point in opposite directions. Both are
derived rather than sampled, and the negative half quantifies over **every**
task rather than over the one measured here.

## 2. TT-1 — the constant table costs the same on every task

> **TT-1.** For every Boolean task on n binary inputs, the nested
> constant-tuple realization
> `TABLE[v0][v1]...[v(n-1)]` costs exactly `3n + 4` Python opcodes per call with
> zero native obligations, and holds `2**n` integer cells.

Measured on n = 3..8 and exact at every point: 13, 16, 19, 22, 25, 28. The count
is task-independent by construction — only the table's contents change.

**Correction to PN-3.** The parity-n registration costed a lookup table at
`5n + 2` from the flat-index rendering
`i = (v0 << n-1) | ... | v(n-1); return TABLE[i]`. Measured through DCR's own
machine that rendering costs `5n + 4` (19, 24, 29, 34, 39, 44), and the nested
rendering costs `3n + 4`, which is cheaper still. PN-3's **conclusion** —
that this coordinate does not charge table size — survives and is strengthened:
the cheapest table is cheaper than PN-3 reported, and its `2**n` cells remain
free. PN-1, PN-2 and PN-4R are untouched; they do not use the table row.

## 3. TT-2 — the budget floor, and why there is no 3n+3

> **TT-2.** In the typed register, a **written** realization — one that reads its
> n inputs in Python, through one `UNPACK_SEQUENCE` — costs
> `(n + 2) + n + m + c + 1` Python opcodes, where `m` counts binary operations
> and comparisons and `c` counts constant loads. An expression over all n inputs
> needs `m >= n - 1`, and a constant is only ever loaded together with an
> operation that consumes it, so `c >= 1` forces `m >= n`. The reachable budgets
> are therefore `3n + 2` with no constant and `3n + 4` with one; **no written
> realization costs `3n + 3`.**

This is event accounting against the layout contract the checker validates
before reporting anything, not an empirical claim. It says nothing about a
realization that hands the whole read to a native callee, such as
`sum(x) >= k` at 6 opcodes: that form does not unpack in Python at all, and
TT-5 treats it separately because its total cost has no finite upper bound. The registered parity-3
facts are reproduced by the same instrument in the same run: written XOR chain
11 opcodes with no native obligation, shared-sum threshold net 39 with four,
`sum(x) & 1` 6 with one.

## 4. TT-3 — majority needs a constant

> **TT-3.** No `3n + 2` realization of majority-n exists for n = 3 or n = 4.

By exhaustive enumeration over the register's eight binary operations, every
binary tree shape and every assignment of the n inputs to leaves, using each
input exactly once. The enumeration is over reachable **value vectors** rather
than over source texts, so it covers all renderings of each vector at once.
At n = 3 the enumeration finds 235 distinct vectors, at n = 4 it finds 8889, and
majority is not among them at either.

Intermediate magnitudes are capped; the cap is shown not to bind by repeating
the enumeration at caps 32, 64 and 256 (n = 3) and 32 and 64 (n = 4) with
identical results, and at n = 3 by widening the constant range from [-6, 6] to
[-12, 12] with identical results.

With TT-2 and TT-1 this fixes the minimum for majority-n at `3n + 4`, attained.

## 5. TT-4 — the optimum does **not** force the threshold structure

> **TT-4.** At the `3n + 4` budget, majority-3 has exactly **8** comparison-form
> realizations: **2** whose compared value is an affine form of the inputs, and
> **6** whose compared value is not. Majority-4 has **10**: 2 affine and 8
> non-affine.

The affine ones are the threshold renderings

```
(v0 + v1 + v2) >= 2          (v0 + v1 + v2) > 1
```

and the non-affine ones are, for each choice of a distinguished input,

```
((v0 + v1) << v2) > 1        ((v0 + v1) << v2) >= 2        (and the 2 other choices)
```

which computes majority because shifting the count of the other inputs left by
a 0/1 bit doubles it exactly when that bit is set. It is a genuine realization
at the same exact cost, and it is not a linear threshold on the inputs.

There is also one arithmetic-form realization at `3n + 4` at n = 3, with the
constant consumed by an operation rather than a comparison:

```
(v0 + v1 + v2) >> 1
```

which is int-typed rather than Boolean-typed, and which the enumeration finds at
n = 3 only. The same enumeration at n = 4, run in the unit's own test at a
declared cap, finds no arithmetic-form realization there.

**This refutes a claim it would have been easy to make.** Cost minimality on a
threshold task does not single out the threshold structure: a non-threshold
rendering attains the same optimum. Any argument of the form "the cheapest
realization of a threshold task is a threshold unit, therefore the structure is
forced" is false in this register, and nothing below relies on it.

## 6. TT-5 — the negative half: no strict neural win, for any task, at any n

> **TT-5.** In the registered Python-opcode coordinate, under DCR's sound
> reading of an unpriced native obligation, **no realization of any task on n
> binary inputs is certified strictly cheaper than the constant table**, and the
> threshold family therefore can at best tie it. Choosing a different task
> cannot change this.

The argument is short and does not depend on the task:

1. the constant table costs `3n + 4` on every task (TT-1), with no native
   obligation, so its cost interval is the singleton `[3n + 4, 3n + 4]`;
2. among written realizations, none costs less than `3n + 2`, and none that
   needs a constant costs less than `3n + 4` (TT-2);
3. so a written realization that beats the table must compute the task with
   `n - 1` constant-free operations. Such a realization exists for parity —
   the XOR chain at `3n + 2` — and not for majority (TT-3). Either way, whether
   it exists is a property of the task and not of the neural family, and it is
   never a threshold form: a threshold rendering always loads its threshold
   constant, so by TT-2 it never falls below `3n + 4`;
4. the only realization here that is numerically cheaper than the table is the
   delegating one, `sum(x) >= k` at 6 opcodes, and TT-2 does not cover it. It
   carries a native obligation with no supplied upper bound, so under PNIR-1 its
   total cost interval is `[6, +infinity)` and no strict claim in either
   direction is certifiable — in particular it is not certified below the
   threshold form either. Pricing that obligation at zero would certify it below
   everything; the checker records that outcome explicitly as the
   unpriced-resource artifact PN-4 hit, not as a result.

Measured frontiers agree with the derivation. Under the sound reading the
undominated set on majority-n contains `DELEGATING_SUM_COMPARISON`
(unverifiable), `NESTED_CONSTANT_TABLE` and `THRESHOLD_COMPARISON_BOOL` at every
n in 3..8, plus each extra minimal rendering at the n where it is exact: five
members at n = 3, four at n = 4, three from n = 5 on. The gate chain and the
one-hidden-unit net are not on it, because in a scalar coordinate they sit
strictly above `3n + 4` with a finite bound and are therefore certified dearer
than the table. The threshold form is
undominated; it is never certified below the table; the table is never certified
below it. **Exact tie at `3n + 4`, at every n.**

So PN-5's residual question has a negative answer in this coordinate, and the
obstruction is not about neural networks at all: it is that the coordinate
prices `2**n` constant cells at zero.

## 7. TT-6 — the positive half: price the table and the threshold form wins

> **TT-6.** In the two-component coordinate
> `(python_opcodes_per_call, constant_cells)` under the product order, on
> majority-n and for every n in 3..8, the threshold rendering at `(3n + 4, 1)`
> **strictly dominates** the constant table at `(3n + 4, 2**n)`, and is
> undominated. This is the first derived appearance of a structurally neural
> realization strictly beating a registered non-neural realization anywhere in
> this evidence line.

The measured points, n = 8:

| realization | opcodes | cells |
|---|---:|---:|
| `THRESHOLD_COMPARISON_BOOL` | 28 | 1 |
| `NESTED_CONSTANT_TABLE` | 28 | 256 |
| `HIDDEN_UNIT_NET_BOOL` | 34 | 2 |
| `THRESHOLD_COMPARISON_INT` | 30 | 2 |
| `FLAT_INDEX_TABLE` | 44 | 263 |
| `MONOTONE_DNF_CHAIN` | 570 | 0 |

The domination is not an artifact of a particular price for a cell: the product
order is implied by **every** coordinate that charges a cell at any positive
rate and charges opcodes monotonically, because the threshold rendering is no
worse in both components and strictly better in one.

Three qualifications, all of which the checker enforces:

- **The win is not unique.** `MONOTONE_DNF_CHAIN` uses no constant cells at all
  and is also undominated, at `570` opcodes against `28` at n = 8. The frontier
  on majority-n is `{MONOTONE_DNF_CHAIN, THRESHOLD_COMPARISON_BOOL}` for
  n >= 5. At n = 3 and n = 4 the non-affine rendering joins it, and at n = 3 the
  shift rendering joins as well, since those are the n at which each is exact.
  The content is that the threshold family is *on* the frontier and the `2**n`
  table is *off* it — not that the threshold family is uniquely optimal.
- **It depends on the return type.** The threshold comparison is Boolean-valued.
  Under an obligation demanding an `int`, the cheapest threshold rendering costs
  `3n + 6` (or `3n + 4` at n = 3 via the shift rendering), and the table at
  `3n + 4` stays undominated for n >= 4. Python's `True == 1` makes the Boolean
  rendering satisfy the obligation under value equality, which is the reading
  used for TT-6; the int-typed frontier is computed and reported separately
  rather than folded in.
- **`constant_cells` is a count, not a measurement.** It counts integer cells in
  the code object's constants and in the registered data bindings. It is not
  bytes, not resident memory, and not a physical cost. TT-6 says what follows
  from charging that count; it does not claim a machine charges it.

## 8. TT-7 — what this does and does not change

> **TT-7.** The parity-3 verdict and the majority-n verdict are opposite, in the
> same register, with the same instrument, and both are point verdicts over
> registered candidates.

On parity-3 the threshold net costs 39 against the XOR chain's 11 and is
strictly dominated. On majority-n the threshold rendering ties the cheapest
non-neural realization in the opcode coordinate and strictly dominates the table
once cells are charged. So the framework is not rigged against neural forms: it
returns the verdict the task and the coordinate imply. That was the open
question PN-5 named, and the answer is that both verdicts are reachable.

What is **not** established:

- **coverage.** By CU-1 and CU-3b these remain point verdicts over registered
  candidates. No proof is offered that the register covers the realizations
  nobody has written, and adding candidates cannot upgrade a point verdict to a
  family statement.
- **the arithmetic shape above n = 3 inside the capsule.** The checker
  enumerates the `3n + 4` arithmetic shape exhaustively at n = 3 only; the unit
  test enumerates n = 4 at a declared cap. n >= 5 is open, and only affects
  whether a cheaper int-typed rendering exists, not TT-5 or TT-6.
- **more than one hidden layer, non-threshold activations, vectorized or array
  realizations, and any substrate other than the validated CPython opcode
  layout.** The layout is validated at run time and the checker refuses rather
  than restating different numbers under the same theorem name.
- **timing and physical memory.** Neither appears anywhere in this derivation.
  No CL-2 or CL-3 window is involved.
- **anything about learning.** Every realization here is written, not trained.
  Nothing follows about developmental reachability.

Terminal: `GRAND_GMI_THRESHOLD_TASK_FRONTIER_GREEN_AT_FINITE_SCOPE`.

## 9. Parent mathematics and contribution boundary

The parent facts are elementary: monotonicity of a minimum under set inclusion,
exhaustive finite enumeration, the product order on a two-component cost, and
PNIR-1's interval certificate. Majority's monotone formula size and the
classical threshold lower bound for parity are not used. No novelty is claimed
for any of them.

The contribution is: the task-independent cost of the cheapest constant table
and the correction it implies for PN-3's figure; the budget floor that rules out
`3n + 3`; the exhaustive enumeration that fixes majority-n's minimum and
**refutes** the claim that the minimum forces a threshold structure; the
task-independent negative answer to PN-5's residual question in the opcode
coordinate; and the identification of the exact premise — charging constant
cells at any positive rate — under which a structurally neural realization
strictly dominates a registered non-neural one.
