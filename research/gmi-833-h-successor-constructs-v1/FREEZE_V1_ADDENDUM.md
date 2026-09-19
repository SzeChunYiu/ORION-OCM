# Freeze v1 addendum: resolutions registered before any executor exists

Committed **before any `.py` file of this package**. `git log --diff-filter=A`
order is the custody record. Nothing here changes a prediction of
`FREEZE_V1.md` section 8; everything here fills a gap that section left, or
states a budget decision, so that the executor has no discretion.

## A1 — Head leaf bindings

`BIAS` binds to the channel value `Q[0]`. There is no fitting at this scope, so
every head leaf must be a channel read or a machine value.

`STATE` is the delay cell. Rows of a slice are processed in ascending row
index; `STATE` is `0` at the first row of a slice, and `OUT` of the previous
row thereafter. Slices are evaluated independently, each starting from `0`.

For `r = 1`, `S2` binds to `0`.

## A2 — Two-stage bindings

For `L = 2`, `ops` is the pair `(stage-1 combining operation, stage-2
combining operation)`. Stage 1 reads the parameter `M[tau_p(i)][j]`; stage 2
reads `Q[j]` and is not tied.

## A3 — Reduction semantics

`ARGMIN` returns the `y` in `Y` itself — not the head value — minimising the
head, ties broken to the smallest `y` in the registered order of `Y`.
`RSUM` returns the exact sum of the head value over all `y` in `Y`.

## A4 — Canonical forms, extending `FREEZE_V1.md` section 4.8

All four are generic, family-blind, and stated before any ecology exists. Each
removes programs that denote a function already denoted by a cheaper program.

1. `r = 2` only when the head depends on `S2`.
2. `L = 2` only when the head depends on `S1`.
3. `tau_p` with `p != 12` only when some `BODY` contains the leaf `PARAM`;
   otherwise the tying map is unobservable and `p = 12` is the representative.
4. `kind != NONE` only when the head depends on `RESP`; otherwise `ARGMIN`
   returns the first element of `Y` regardless of the data and `RSUM` returns
   `|Y|` times the head, both of which a cheaper `kind = NONE` program denotes.

## A5 — The `G_S` stratum, written out

The stratum against which the five non-representability exhaustions of
`FREEZE_V1.md` section 8 `b` are run:

```
r = 1 ;  L = 1 ;  p = 12 ;  kind = NONE ;  combining operation = ADD
BODY  over {ARG, PARAM, C0, C1}          at most 3 nodes
HEAD  over {S1, BIAS, STATE, C0, C1}     at most 4 nodes
```

This is `G_S` exactly, with `S1` playing the role its single fold leaf `S`
played there. It is enumerated to `B_MAX = 10`, which at these leaf sets and
node budgets exhausts the stratum.

## A6 — What `B_MAX` bounds and what it does not

`B_MAX = 10` bounds the `G_S` exhaustion of A5. The `R06` minimality statement
at a scope is bounded by that scope's **recovered cost**: every well-formed
`G_H` program of strictly smaller charged cost is enumerated and tested. Both
are statements about an enumerated set, never about all programs.

## A7 — Ecology construction details

Per row the stream of `FREEZE_V1.md` section 5 is drawn in the fixed order
`A` (12 draws), `P` (12), `M` (48 in row-major order `i` then `j`), `Q` (4);
76 draws per row, rows built in ascending global index `0..47`.

The `sum_i A_i != 0` rebuild guard applies at `SIGMA_D17` only, the one scope
whose response divides by that sum. The rebuild count is reported.

At `SIGMA_D34` the `A` and `P` channels are drawn as `(s mod 3) - 1`, in
`{-1, 0, 1}`, so that the score lies in `[-12, 12]` and `Y` is a coarse
quantisation of its negation. The `M` and `Q` channels are drawn as elsewhere.

The two pinned tie rows of `FREEZE_V1.md` section 5 apply at `SIGMA_D34` only,
at global row indices `0` (the first search-slice row) and `2` (the first
held-out-slice row).

The ecology digest is the sha256 of the canonical serialisation of all 48 rows
of a scope, in ascending row index, channel order `A, P, M, Q`, values
rendered as exact fractions.

## A8 — Tie-break for the recovered program

Ascending charged cost; within a cost, the lexicographically smallest canonical
program rendering. The rendering is a deterministic string built from the
config flags and the `show()` of each tree.

## A9 — The `BODY2` node budget is raised from 3 to 4

`FREEZE_V1.md` section 4.6 set the `BODY2` budget to 3 nodes. The minimal form
of a weighted nonlinear second stage, `MUL(STEP(U), PARAM2)`, has **four**
nodes. At a budget of 3 that form is outside the grammar, so `SIGMA_D20` could
not be tested at all and the `H20` construct could not be built.

The budget is therefore raised to **4**, equal to the `HEAD` budget, here,
before any executor exists.

Disclosed as `BUDGET_RAISED_BEFORE_IMPLEMENTATION`. Two facts bound what the
change can do:

1. It applies to the whole grammar at every scope, not to `SIGMA_D20`. `G_H` is
   one grammar; there is no per-scope budget.
2. A larger budget adds competing programs at every cost level. It can only
   make a recovery harder to win and a minimality statement harder to earn,
   never easier. No prediction of `FREEZE_V1.md` section 8 is weakened,
   and the predicted cost of `SIGMA_D20` remains `9`
   (`3 + 4 + 1 + 1`).

No other budget moves. `BODY` stays at 3, `HEAD` stays at 4, `N = 12`,
`w = 4`, `Y` unchanged, `p` list unchanged.
