# GMI #833 Section Z / Z13 rows 9-10 and Z16 — a prediction from the repaired law, made and then tested

Closes `Z13` rows 9 and 10 and `Z16` rows 1, 2, 3 and 5 of issue comment
`5684819296`. Leaves `Z13` row 11 and `Z16` rows 4 and 6 open by design
(independent replication is not self-suppliable; an authored argument is not
evidence).

## What it establishes

The marginal law (`IC-1`, `DS-5`) was used to write down, before any
enumeration at `L = 5` or `L = 6` existed, the prediction `Z13-P3`
(`FREEZE_V1.md` §3, commit `f9301396`): a closed form for the one-bit delay-2
floor `R0(d2|b=1, L) = 1/3 - (1 - (-1/2)^(L-2))/(18(L-2))`, its exact attaining
pair, both niche endpoints as marginals, the niche rule
`p1 > p2*(4R - 1)` with `96/135` worlds at each `L`, and a five-world probe table
containing one world that must flip from niche to no-niche between `L = 5` and
`L = 6`. Two materially independent routes then enumerated both universes:

- **`ZP-1`** `R0(d2|b=1) = 5/16` at `L = 5` and `41/128` at `L = 6`, attained by
  exactly `(0,1,0,0)` and `(1,0,0,0)`; per-t errors `1/4, 3/8, 5/16, 11/32`;
- **`ZP-2`** both thresholds are marginals in `135/135` worlds at both `L`
  (Route B by scanning an exact `lambda` grid, not by differencing); `0/200`
  seeded pairs reproduce the upper endpoint, the marginal pair `135/135`;
- **`ZP-3`** the one-bit niche is non-empty in `96/135` worlds at both `L`; the
  rule matches the enumeration `135/135`; minimisers are copy-then-reset x
  identity-type (`F_MEALY_PURE`);
- **`ZP-4`** the collapse coefficient moves from `1/4` (`L = 5`) to `9/32`
  (`L = 6`); the flip world `(0, 17/81, 64/81)` has niche width `+eta/162` at
  `L = 5` and `-eta/162` at `L = 6`; the boundary world `(0, 9/41, 32/41)` has
  width exactly `0` at `L = 6`; both controls and the retired `p2 = 0` ecology
  (width `eta*3/8`) behave as tabled at all three `eta`; `0/200` seeded collapse
  coefficients classify all `156` worlds of the amended grid, the predicted
  `9/32` does;
- **`ZP-5`** seven applicable hostiles move their quantity, the no-alarm
  control is silent, one vacuous hostile is published as vacuous;
- **`ZP-6`** `Z13-P3` is a **HIT** on every named axis at both `L` on both routes.

## What it does not establish

No independent replication (Route B is same-author); no W4 or new-domain
status; no new architecture family (the minimisers are Mealy machines); nothing
beyond `L in {5, 6}`, `b <= 2`, uniform binary inputs; the envelope mathematics
is Everett's, not ours; `Z13-P1` is not re-scored. One frozen null clause failed
on the frozen grid and is published, attributed and repaired by a pre-committed
amendment (`FAILED_PREDICTION_REGISTER_V1.json`).

Claim ceiling:

```
GMI_833_Z13_PROSPECTIVE_NICHE_AND_MATCHED_NEGATIVE_ECOLOGY_FROM_THE_MARGINAL_LAW_AT_L5_L6_THREE_MODE_FINITE_STATE_SCOPE__NO_INDEPENDENT_REPLICATION
```

## Custody

`FREEZE_V1.md` at `f9301396` (with §3 in full) precedes every executor;
`FREEZE_V1_AMENDMENT_1.md` at `465f096a` precedes the receipt commit; the
enumeration commit follows both. The test checks the chain by git ancestry and
degrades to `UNREACHABLE`, never to a pass, without history.

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z13-repaired-chain-v1/z13_repaired_chain_v1.py
python3 -I -B  research/gmi-833-z-z13-repaired-chain-v1/independent_z13_oracle_v1.py
python3 -I -B  research/gmi-833-z-z13-repaired-chain-v1/test_z13_repaired_chain_v1.py -v
python3 -I -O -B research/gmi-833-z-z13-repaired-chain-v1/test_z13_repaired_chain_v1.py -v
```

Stdlib only, exact arithmetic, no float in any claim. Route A about `95` s wall
on the compute host (python 3.8.10), Route B about `6` s.
