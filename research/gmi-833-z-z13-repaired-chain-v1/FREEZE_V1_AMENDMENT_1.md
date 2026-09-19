# FREEZE_V1 amendment 1 — the null pools, one vacuous hostile, and nothing in §3

`FREEZE_V1.md` is not edited. This amendment is committed **before** any receipt
of this package is committed, and after the first Route A run on the compute
host (laptop `billy`, `python3 -I -B z13_repaired_chain_v1.py`, wall 1:35)
had reported the numbers quoted below. Nothing in §3 of the freeze — the
prediction `Z13-P3` and every number in it — is touched by this amendment.
The first run's `Z13-P3` verdict was `HIT` on every named axis at both `L`;
that verdict is not what this amendment is about.

## A1.1 What the first run showed about §5 (verbatim numbers)

- Null 1 (upper endpoint law at `L = 6`, 200 seeded pairs in `k/128`):
  `perfect = 0`, best `27/135`, the marginal pair `(1/2, 23/128)` scored
  `135/135`. The null was beaten — but its draw pool contained the true pair,
  which the programme's shared brief forbids ("a null whose draw pool contains
  the true law is not a null").
- Null 2 (collapse coefficient `c` in `k/64` for `p1 <= c*p2` on the union of
  the eighths grid and the probe worlds, 150 worlds): **`perfect = 9` of 200**;
  the predicted `9/32 = 18/64` scored `150/150` but so did `19/64`, `20/64` and
  `21/64`. The frozen clause "the predicted `9/32` must be the unique perfect
  scorer at `L = 6`" **failed**.
- Hostile "scoring `L = 5` floors on the `L = 4` window": Route A's first
  implementation used the window `{3, 4}`, which is not the `L = 4` window
  (`{2, 3}`), and it did not move the floor (`5/16` on both). Implemented as
  frozen, on `{2, 3}`, the delay-2 floor at `L = 5` is
  `(e_2 + e_3)/2 = (1/4 + 3/8)/2 = 5/16` — **equal** to the true
  `L = 5` value `5/16`. The hostile as frozen is **vacuous at `L = 5`**: the
  closed form of §3.1 gives the same average on both windows, which is the
  same coincidence the freeze already notes (`5/16` at `L = 4` and `L = 5`).

## A1.2 One-stage attribution

- Null 2: the world set has no world whose ratio `p1/p2` lies in
  `(9/32, 1/3)`; every coefficient in `[18/64, 21/64]` therefore classifies
  the 150 worlds identically. The failure is in the **null's world grid**, not
  in the prediction, the enumeration or the scoring.
- The hostile: the failure is in the **choice of `L`** at which the hostile is
  applied; at `L = 6` the same hostile scores `(e_2 + e_3)/2 = 5/16` against the
  true `41/128` and must move.

## A1.3 The levers, fixed now, before the re-test

1. Both null pools **exclude the true law**: null 1 draws from the 129 x 129
   grid minus `(64/128, 23/128)`; null 2 draws from `{0, .., 64}/64` minus
   `18/64`. The draw that lands on an excluded point is redrawn; the number of
   redraws is recorded.
2. Null 2 is scored on the frozen union grid **plus two null-discriminating
   worlds** with `p0 = 0`: `(p1, p2) = (18/82, 64/82)` (ratio `18/64`, the
   predicted boundary: empty at equality) and `(19/83, 64/83)` (ratio `19/64`,
   just above: non-empty). With these two worlds the only `k/64` coefficient
   that can score perfectly is `k = 18`, so the frozen uniqueness clause becomes
   decidable. The truth at the two new worlds is computed by the enumeration
   (both routes), not asserted. Predicted outcome, stated before the re-run:
   `18/82` world **empty** at `L = 6` (width `0`), `19/83` world **non-empty**
   at `L = 6`; null 2 `perfect = 0` of 200; the predicted coefficient scores
   `152/152`.
3. The window hostile is run at **both** `L`, on the `L = 4` window `{2, 3}`;
   the cell at `L = 5` carries `applicable: false` with the equality shown;
   the cell at `L = 6` must move (`5/16` vs `41/128`). `hostiles_all_moved`
   is computed over applicable hostiles only, and the vacuous cell is published
   as such.

## A1.4 What this amendment does not do

It does not change the prediction, the universes, the window, the world grids
of §1 or §3.4, the probe table, the decision rule of §4, or the routes of §5.
It does not turn the first run's null-2 outcome into a pass: that outcome is
recorded in `RESULT_V1.json` under `null_collapse_rule_L6_as_first_frozen`
and stays a recorded MISS of the §5 uniqueness clause on the frozen grid.

`s6_instruction_followed: true` (the governing clause — §7, "any hostile that
does not move its quantity" is a falsifier of the package — is what forced
this amendment); `audit_shape_disclosed: AMENDED_BEFORE_RECEIPT_COMMIT`.
