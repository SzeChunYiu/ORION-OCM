# GMI #833 Section Z / Z13 rows 9-10 and Z16 — a new prediction from the repaired law, frozen before enumeration

Committed **before any executor, oracle, receipt, enumeration or test exists in
this package**. Git order proves it. Nothing about the `L = 5` or `L = 6`
universes declared below has been enumerated by this lane; the numbers in §3 are
hand derivations from the mechanism, shown in full so a reader can check them
without running anything.

- `source_main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`
- branch: `research/833-revive-z17`
- adjudicated parent: `research/gmi-833-z-z13-adjudication-v1` (branch
  `research/833-sec-z4`, PR #1052): `FAILED_PREDICTION_REGISTER_V1.json` blob
  `da6aa281`, `REPAIRED_ECOLOGY_FREEZE_V1.md` blob `5bc0597a`,
  `Z13_THEOREMS_V1.md` blob `0f5fa317`, `RESULT_V1.json` blob `a0c82c07`.
- the retired prediction `Z13-P1`: `research/gmi-833-z-z13-property-prediction-freeze-v1/FREEZE_V1.md`
  blob `25febfa6`, commit `0cc617fc` (branch `research/833-sec-z3`). It is
  **never re-scored here**; it is cited only as the registered expectation that
  the repaired law contradicts.
- the repaired law: `IC-1` (`gmi-833-z-z1-master-principle-v1/Z1_THEOREMS_V1.md`
  blob `11012f8f`) and `DS-5` `lambda* = eta*p*R0` (`gmi-833-z-z6-discrimination-v1`
  blob `35ab5d2b`).

Claim ceiling:

```
GMI_833_Z13_PROSPECTIVE_NICHE_AND_MATCHED_NEGATIVE_ECOLOGY_FROM_THE_MARGINAL_LAW_AT_L5_L6_THREE_MODE_FINITE_STATE_SCOPE__NO_INDEPENDENT_REPLICATION
```

## 0. Disclosure

Before writing this file the author read the Z13 adjudication receipt at `L = 4`
(floors `R0(d2|b=1) = 5/16`, the four floor-attaining next-state functions, the
width `eta*(p1/2 - p2/8)`) and derived §3 by hand from the one-bit Markov
chain. No scratch enumeration at `L = 5` or `L = 6` was run. The predictions
below are therefore prior to every number this package will compute, and the
hand derivation is what the enumeration tests.

## 1. The universe, declared exactly (faithful extension of the adjudicated one)

Identical to `gmi-833-z-z13-adjudication-v1` `FREEZE_V1.md` §1 in every
convention, with the sequence length changed:

- modes `m in {0, 1, 2}`: target at time `t` is `seq[t - m]`; mode-indexed
  output and next-state tables, per-mode address `a = 2*st + cur`;
- canonical initial state `0`; budgets `b in {0, 1, 2}` (`2^b` states);
- uniform independent bits, all `2^L` sequences with exact rational weights;
- **two sequence lengths** `L in {5, 6}`, scored window `t in {2, ..., L-1}`
  (the common window on which all three targets are defined: 3 and 4 scored
  moments per sequence, `96` and `256` scored moments per mode);
- declared cost `C = eta*(p0*r_now + p1*r_delay1 + p2*r_delay2) + lambda*b`,
  `p0 + p1 + p2 = 1`;
- world grids: `eta in {1, 2, 3}` x `(p0, p1, p2)` over eighths (135 worlds
  per `L`), plus the frozen probe worlds of §3.4.

Enumeration at `b = 2` uses the same two lemmas the parent verified
(`MODE-INDEPENDENCE`, `MAJORITY-OPTIMALITY`); Route B must re-verify both by
brute force over the full `(output, next-state)` product at `b <= 1` and at
`L = 5` before they are used at `b = 2`.

## 2. The repaired law this package tests

`IC-1`: a resource level occupies a non-empty niche iff it is a vertex of the
lower convex envelope of the resource-error profile `E(k)`; the niche of level
`1` is exactly `(E(1) - E(2), E(0) - E(1))`; thresholds are marginal error
masses, never levels. The niche of the one-bit class is empty iff
`E(0) - 2*E(1) + E(2) <= 0`.

## 3. The frozen prediction `Z13-P3`

### 3.1 The mechanism, and the closed form it gives (`P3-a`)

Write `g` for a one-bit next-state function and `pi_k = P(s_k = 1)`. For the
**copy-then-reset** function `g(0, c) = c`, `g(1, c) = 0`
(per-mode encoding `(0, 1, 0, 0)`), the state satisfies
`s_t = 1 iff s_{t-1} = 0 and x_{t-1} = 1`, so `pi_k = (1 - pi_{k-1})/2` with
`pi_0 = 0`, i.e. `pi_k = (1/3)*(1 - (-1/2)^k)`.

With per-address majority outputs, the delay-2 error at time `t` is
`1/2 - |P(s_t=1, x_{t-2}=1) - P(s_t=1, x_{t-2}=0)|`. For copy-then-reset the
conditional split is `-(1 - pi_{t-2})/2`, hence

```
e_t = 1/4 + pi_{t-2}/4 = 1/3 - (1/12)*(-1/2)^(t-2)
```

`e_2 = 1/4`, `e_3 = 3/8`, `e_4 = 5/16`, `e_5 = 11/32`, `e_6 = 21/64`. Averaged
over the scored window:

```
R0(d2 | b = 1, L) = 1/3 - (1 - (-1/2)^(L-2)) / (18*(L-2))
```

which gives `5/16` at `L = 4` (the adjudicated value — a consistency check, not
evidence), **`5/16` at `L = 5`** and **`41/128` at `L = 6`**, limit `1/3`.

Exhausting the 16 one-bit next-state functions by the split argument: both
states constant, or both mixed, give split `0`; state `0` constant with `g(0,.) = 0`
never leaves state `0`; state `0` constant with `g(0,.) = 1` and state `1` mixed
gives `e'_t = e_{t-1}` with `e'_2 = 1/2`, strictly worse over every window
`L >= 4`; state `0` mixed with state `1` constant gives the copy-then-reset
family, of which the **set** variants (`g(1, .) = 1`, encodings `(0, 1, 1, 1)`
and `(1, 0, 1, 1)`) have `pi_k = 1 - 2^(-k)` and are strictly worse for
`L >= 5` (`17/48` at `L = 5`). Therefore:

- `P3-a1` `R0(d2 | b=1)` is `5/16` at `L = 5` and `41/128` at `L = 6`, exactly;
- `P3-a2` it is attained by **exactly two** next-state functions at each `L`,
  `(0, 1, 0, 0)` and `(1, 0, 0, 0)`, and by no other — in particular the two set
  variants that tied at `L = 4` drop out;
- `P3-a3` all other floors: `R0(now | b) = 0` for all `b`; `R0(d1 | 0) = 1/2`,
  `R0(d1 | 1) = 0`, `R0(d1 | 2) = 0`; `R0(d2 | 0) = 1/2`, `R0(d2 | 2) = 0`, at
  both `L`.

### 3.2 Thresholds are marginals (`P3-b`)

At every world and both `L`: lower endpoint `lambda_2* = E(1) - E(2) = eta*p2*R`
and upper endpoint `lambda_1* = E(0) - E(1) = eta*(p1/2 + p2*(1/2 - R))`, with
`R = R0(d2 | b=1, L)`. Numerically `lambda_1* = eta*(p1/2 + 3*p2/16)` at `L = 5`
and `eta*(p1/2 + 23*p2/128)` at `L = 6`.

### 3.3 The prospective niche (`P3-c`) — row 9

The one-bit class is the unique cost-minimising budget exactly on
`(lambda_2*, lambda_1*)`, and that interval is non-empty **iff**

```
p1 > p2 * (4*R - 1)        i.e.   4*p1 > p2   at L = 5,   32*p1 > 9*p2   at L = 6.
```

Inside the niche the unique minimisers use `(0, 1, 0, 0)` or `(1, 0, 0, 0)` on
the delay-2 channel and an identity-type next-state on the delay-1 channel; they
are `F_MEALY_PURE` and in no other registered family. On the eighths grid the
niche is non-empty in **`96` of `135`** worlds at `L = 5` and **`96` of `135`**
at `L = 6` (the grid is too coarse to see the boundary move — that is why §3.4
exists).

### 3.4 The matched negative ecology (`P3-d`) — row 10

The advantage disappears exactly on `p1 <= p2*(4*R - 1)`: there the one-bit
class is never a unique minimiser at any `lambda >= 0` (at most a tie at a
single `lambda`). The boundary **moves with `L`**: coefficient `1/4` at
`L in {4, 5}`, `9/32` at `L = 6`, limit `1/3`. Frozen probe worlds, each at
`eta in {1, 2, 3}`:

| world `(p0, p1, p2)` | `L = 5` | `L = 6` | role |
|---|---|---|---|
| `(0, 17/81, 64/81)` | niche **non-empty** (`4*17 = 68 > 64`) | niche **empty** (`32*17 = 544 <= 9*64 = 576`) | the flip world, strict on both sides |
| `(0, 9/41, 32/41)` | non-empty (`36 > 32`) | **empty at exact equality** (`288 = 288`, width `0`) | the boundary world |
| `(0, 1/4, 3/4)` | non-empty | non-empty (`8 > 27/4`) | matched control that must **not** flip |
| `(0, 1/8, 7/8)` | empty | empty | matched control, empty at every `L` |
| `(1/4, 3/4, 0)` | non-empty, width `eta*3/8` | non-empty, width `eta*3/8` | the retired ecology `p2 = 0` is where the niche is widest at fixed `p1` |

`P3-d` is a HIT only if all five rows behave as tabled at all three `eta`.

### 3.5 A negative control on the mechanism (`P3-e`)

The copy-then-**set** function `(0, 1, 1, 1)` attains delay-2 error exactly
`17/48` at `L = 5` and is strictly above the floor; a lane that finds it at the
floor has falsified §3.1's split argument.

### 3.6 What counts as a HIT

`Z13-P3` is HIT only if `P3-a1`, `P3-a2`, `P3-a3`, `P3-b`, `P3-c` (including the
two `96/135` counts) and `P3-d` (all five probe rows) hold exactly, on both
routes. Anything less is a MISS on the named axes, published in
`FAILED_PREDICTION_REGISTER_V1.json` with the exact retired text and never
repaired into a HIT. A partially confirmed prediction closes only the row whose
evidence is fully confirmed.

## 4. Rows, and the pre-declared decision rule

The rows this package may reconcile, and the three that must stay open, are
pinned byte-exact in `FROZEN_ROWS_V1.json` (comment fetch sha256
`5be745ee8ccdf3a96636550ad0782409f83d04fb9c4586b446ff1072bee8bdf9`, 26,485
bytes). In words:

- `Z13` row 9 (prospective demonstration of the niche advantage) closes iff
  `P3-a` .. `P3-c` HIT;
- `Z13` row 10 (matched negative ecology where the advantage disappears)
  closes iff `P3-d` HIT;
- `Z13` row 11 (independent replication) **stays open** with exactly this
  reason: `M5` has zero instances in this corpus and same-author routes never
  license it. Route B here is same-author.
- `Z16` row 1 closes iff `P3-a1` and `P3-d` HIT including the flip world: the
  result is then a model selection boundary law with an `L`-dependent phase
  boundary, not a reconstruction of what a known architecture does; the
  mathematics of the envelope is parent-owned (Everett 1963) and is said so.
- `Z16` row 2 closes iff HIT and git order proves this freeze precedes the
  executor.
- `Z16` row 3 closes iff HIT: the registered expert expectation is `Z13-P1`,
  frozen by a separate lane, which placed the collapse at `p2 = 0` and priced
  the second bit with a level; and `Z5` `CP-4` registered zero finite-size
  drift of the two-level boundary in `L`, whereas the three-level collapse
  boundary is predicted to drift from `1/4` to `9/32`.
- `Z16` row 4 **stays open**: it requires independent replication.
- `Z16` row 5 closes iff the flip world HITs: a change of the selected class
  driven by sequence length alone is a phase transition the retired law cannot
  express.
- `Z16` row 6 **stays open**: a demonstration of design consequence is an
  argument, and an argument authored here is not evidence.

**No neighboring row is earned here.** `Z13` rows 1-8 and 12 belong to the
adjudication lane (PR #1052); nothing in Z1-Z12, Z14, Z15, Z17, Z18.

## 5. Two routes, hostiles, null, vacuity

- Route A: next-state enumeration with per-address majority outputs; envelope
  by differencing `E`.
- Route B: exact Markov computation of the joint law of `(state, x_{t-1}, x_{t-2})`
  with no sequence enumeration; full `(output, next-state)` product at `b = 1`;
  niche located by scanning an exact `lambda` grid over the combined
  three-mode universe rather than by differencing; the `b = 2` floors witnessed
  constructively by a two-bit shift register and matched by a seeded hill-climb.
  Route B imports nothing from Route A.
- Hostiles, each required to move the quantity it perturbs: level-for-marginal
  threshold; window shifted to `t in {1, .., L-1}`; skewed input law
  `q = 1/3`; template injection (identity-next-state family only); set-variant
  substituted for reset-variant; accounting `lambda*(2^b - 1)`; scoring
  `L = 5` floors on the `L = 4` window. Registered no-alarm control: initial
  state `0 -> 1` at `b = 1` (a state-relabelling symmetry; must be silent).
- Null: 200 seeded coefficient pairs `(a, b)`, `a, b in k/128`, for the upper
  endpoint law `eta*(a*p1 + b*p2)` at `L = 6`; the marginal pair
  `(1/2, 23/128)` must be the only perfect scorer over the 135 worlds and `0`
  seeded pairs may reach `135/135`. A second null for the collapse rule:
  200 seeded coefficients `c in k/64` for `p1 <= c*p2` scored on the union of
  the eighths grid and the probe worlds; the predicted `9/32` must be the
  unique perfect scorer at `L = 6`.
- Vacuity: the collapse condition must have worlds on both sides at each `L`
  (it does on the eighths grid, `96` vs `39`); the probe table has both
  outcomes at each `L`. A bound with nothing on one side is retained but not
  counted.

## 6. Forbidden promotions

```
Z13_P1_RESCORED_BY_THIS_LANE
INDEPENDENT_REPLICATION_CLAIMED
W4_STATUS_CLAIMED
NEW_ARCHITECTURE_FAMILY_CLAIMED
Z16_ROW4_OR_ROW6_CLOSED_BY_THIS_PACKAGE
RESULT_EXTENDED_BEYOND_L_IN_5_6_OR_b_GREATER_THAN_2_OR_NON_UNIFORM_INPUTS
ENVELOPE_MATHEMATICS_CLAIMED_AS_NOVEL
PARTIAL_HIT_CLOSING_A_ROW_ITS_EVIDENCE_DOES_NOT_REACH
```

## 7. Falsifiers of this package itself

- any §3 number failing on either route — published as a MISS;
- any hostile that does not move its quantity;
- the no-alarm control firing;
- Route A and Route B disagreeing on any floor, endpoint, probe outcome or count;
- the flip world not flipping while everything else holds — then row 10 closes
  on the eighths grid only if the freeze's own table is honoured, which it is
  not, so row 10 stays open.
