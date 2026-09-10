# M2 traversal-capital probes — CORE (read first)

Lane `LANE_M2_TRAVERSAL_CAPITAL_OPUS`. Owner #165, hardening parent #323.
Status: **PRE-FREEZE PROBES, NOT SCORED RUNS.** Pre-registration input for the
`DEV-CAL-1` / M1 successor. Nothing here promotes a claim.

## One-line result

The `KNOWN_STRUCTURE_ORACLE` calibration arm does **not** measure transferable
structural headroom. At the M1 acquisition scope its entire advantage is a
**constant 21 845-slot offset**, recoverable with zero history and zero features.

## The four findings

| # | terminal | where |
|---|---|---|
| M2-N1 | `ORACLE_ADVANTAGE_IS_A_CONSTANT_OFFSET` | [RESULT.md](RESULT.md#m2-n1) |
| M2-N2 | `STRUCTURE_PREDICTABLE_WITHOUT_HISTORY` | [RESULT.md](RESULT.md#m2-n2) |
| M2-N3 | `HEADROOM_NOT_SURFACE_IDENTIFIABLE` | [RESULT.md](RESULT.md#m2-n3) |
| M2-N4 | `BASELINE_ENUMERATION_ORDER_IS_MISCALIBRATED` | [RESULT.md](RESULT.md#m2-n4) |

## Why this is checkable

The declared grammar is 4 primitives at max length 8, so the whole space is
`sum(4^L, L=0..8) = 87 381` programs and every `B_slots` is a closed-form lookup,
not an estimate. The probes reproduce the **committed M1 scored endpoints exactly**
— baseline `0+0+1+3+8 = 12/40`, oracle `0+1+1+8+8 = 18/40` — and independently
reproduce the frozen `min_primitive_length` for all 288 partition rows
(`min_length_crosscheck: PASS`, zero mismatches).

## Raw records

`records/M2_PROBE_V1.json` (identifiability) · `records/M2_PROBE_V2.json`
(residual headroom) · `records/M2_PROBE_V3.json` (feature sufficiency).
Emitters: `m2_probe_v1_identifiability.py`, `m2_probe_v2_residual_headroom.py`,
`m2_probe_v3_feature_sufficiency.py`. `src/ocm/learning/methods.py` and
`research/m1-native-acquisition/m1_partitions.py` are imported **AS-IS**.
Executed on laptop `billy-laptop-old` (python 3.14.4), never the Mac.
