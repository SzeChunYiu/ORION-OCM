# Testing arrangement generalisation is itself constrained — and the constraint is computable

The hostile review left one question outstanding: does the developmental benefit survive
at generalisation distance `d ≥ 2` (a novel *arrangement* of known parts), or is it
interpolation at `d = 1`? Three attempts failed for reasons that turned out to be
structural rather than incidental, so the constraint was derived instead of guessed.

## Two constraints that pull opposite ways

**Novelty must exist.** Each training arrangement of `k` tokens over `m` motifs covers
`k(m−1)+1` arrangements within distance 1, so distance-2 targets exist only if

```text
train_n · (k(m−1) + 1)  <  A(m, k)
```

with `A(m,k)` the number of **canonical** k-token arrangements (measured, not assumed —
only ~5 % of combinations are the first-in-enumeration program for their normal form).

**The mechanism must work.** A k-token word over the top-ranked motifs sits at guided
position `g ≈ Σ m^i`, and the interleave returns at `≈ 2g`, so the mechanism needs
`2g ≤ b`.

Raising `k` creates arrangement room and simultaneously deepens the guided search. The
two windows need not overlap.

## The measured map

| motifs | k | target len | canonical arrangements | max train_n leaving d2 room | 2g | b_max | both |
|---|---|---|---|---|---|---|---|
| 8 | 3 | 6 | 139 | 6 | 1 168 | 5 461 | ✗ |
| 10 | 3 | 6 | 186 | 6 | 2 220 | 5 461 | ✗ |
| **12** | **3** | **6** | **635** | **18** | **3 768** | **5 461** | **✓** |
| 14 | 3 | 6 | 845 | 21 | 5 908 | 5 461 | ✗ |
| 6 | 4 | 8 | 293 | 13 | 3 108 | 87 381 | ✓ |
| 8 | 4 | 8 | 635 | 21 | 9 360 | 87 381 | ✓ |
| 12 | 4 | 8 | 4 642 | 103 | 45 240 | 87 381 | ✓ |

```text
VERDICT: ARRANGEMENT_GENERALISATION_TESTABLE — 6 feasible configurations
```

## Why the first three attempts failed, and it was not the distance

| attempt | config | outcome | cause |
|---|---|---|---|
| D1/D2 | m=12, k=4, train=120 | both refused, library harmful | train_n 120 ≫ 103; and `ORACLE_FAMILY` **also failed** (103 vs RESET 104) — depth, not library |
| M8D1/M8D2 | m=8, k=4, train=30 | one favourable draw (47 %, EU-admitted) | **not replicated** — 4 seeds show −30 to +19 %, mostly harmful |
| k=3, train=120 | m=12, k=3 | 4 targets at d≥2 | train_n 120 ≫ 18 — space saturated by counting |

The single favourable M8D2 draw would have made an attractive headline. Replication
killed it, which is the correct outcome of insisting on replication before claiming.

Note also that the `k = 4` rows are marked feasible by the estimate but **failed
empirically**, so the `g ≈ Σ m^i` estimate is optimistic at `k = 4`. The trustworthy
region is `k = 3`, where the E-series mechanism is independently known to work.

## The registered test

`m = 12, k = 3, train_n = 18` — the only configuration that is both feasible *and* in the
regime where the mechanism is known to work. Matched `d = 1` and `d = 2` at identical
`(m, k, train_n)`, six seeds, so **distance is the only variable**.

## What this bounds, either way

If benefit survives at `d = 2`, U2 is development over arrangements, not interpolation.
If it collapses, U2 is bounded at `d = 1` and the hostile review's reading stands. Either
result is decisive, and the feasibility map is what makes the test interpretable at all —
without it, a null would have been indistinguishable from an infeasible configuration,
which is exactly what the first three attempts were.
