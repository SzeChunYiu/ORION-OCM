# Registered K4 campaign under repaired pricing (items 22 / 23 / 35 clause c)

Date: 2026-09-15. Lane: machine-intelligence-morphogenesis-v1.
Package: `gmi_k4_repaired_campaign_v1/`.
Protocol: `PROTOCOL_FREEZE_V1.json`.
Runner: `repaired_campaign_v1.py`.

## What was still open

Items **22**, **23** and **35** share one standing negative: 0/264 K4 cells green,
blind recovery `NOT_EARNED`. Root cause (#622) and instrument repair (#626) are
already on the record:

- frozen pricing contains **no substitutions**;
- overlay R1+R2+R3 restores a storage↔serve trade and recovers retention by
  label-free search under reuse;
- **the frozen model was deliberately left untouched**, so no registered
  verdict moved.

The checklist names the remaining act as clause **(c)**:

> a registered campaign under the repaired pricing — a protocol decision, not
> something to do silently.

This package is that decision.

## Protocol decision (the content of (c))

1. **Adopt** the repaired overlay (`gmi_k4_substitution_repair_v1.py`, R1+R2+R3)
   as the pricing arm of a **new** campaign id
   `GMI_K4_REPAIRED_PRICING_CAMPAIGN_V1`.
2. **Do not** mutate `gmi_k4_resource_native_v4.py`, `gmi_k4_search_v4.py`, or
   any V4/V7 freeze / beacon / aggregate. Pins in `PROTOCOL_FREEZE_V1.json`
   fail CI if those bytes move under the false flag of this campaign.
3. **Do not** rewrite frozen cell verdicts. The 0/264 property-vector result
   remains the authority for the frozen protocol.
4. **Predict a different object** under the repair: PVR-3 retention recovery as
   a function of reuse — not the original 22 property vectors. A probe under
   repaired pricing still finds cheaper admissible non-targets than several
   frozen target witnesses; pretending those vectors go green would be the
   silent mutation clause (c) forbids.

## Campaign cells and green rule

Grid: grammar `G2_SYMBOLIC_PROGRAM` × scale 4 × registered reuse schedule
`(1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096)`, 4000 label-free draws,
seed `0xA11CE`.

A repaired cell at reuse `r` is **`K4_REPAIRED_CAMPAIGN_GREEN`** iff:

- `r < 128` and the winner does **not** retain, or
- `r ≥ 128` and the winner **does** retain (retrieval ≠ `none` and store
  coverage ≥ 0.5).

The matched **frozen-v4 control** at the same `r` must never retain. If it
does, the campaign is `INVALID_INSTRUMENT`, not green.

Campaign-level invariants (also asserted): repaired winners vary with reuse;
frozen winners do not; repaired retained state is monotone in reuse; reuse 1
declines retention; reuse ≥ 256 reaches full coverage.

## What this establishes for #592 / #602

| claim | status |
|---|---|
| Clause (c) is a **registered** protocol, not a silent reprice of V4 | established by `PROTOCOL_FREEZE_V1.json` |
| Green cells are **earnable** under repaired pricing | established by the executable campaign (multiple greens on the schedule) |
| Frozen model / frozen verdicts are **untouched** | established by sha256 pins + frozen control arm |
| Original 22 property vectors are **not** quietly reclassified | established by predicted-object clause |

Admissible vs reachable: this campaign claims **reachability of retention under
the repaired instrument**, not that every frozen `THEORY_RED` cell was
misclassified. Worker-1's per-cell substitution audit (clause a) remains the
path for reclassifying individual property-vector cells.

## Falsifiers

- Frozen pin bytes change while this campaign claims "untouched".
- Frozen control arm retains at any scheduled reuse.
- Repaired arm retains at reuse 1, or fails to retain at reuse ≥ 128, or loses
  monotone state growth / full coverage by 256.
- Any write path that patches `rn.lifecycle` in place rather than overlaying
  costs through `gmi_k4_substitution_repair_v1.lifecycle`.
