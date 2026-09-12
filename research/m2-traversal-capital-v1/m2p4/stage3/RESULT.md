# M2-P4 stage 3 — the scored result

**`C2_NOT_REPLICATED_IN_SECOND_GRAMMAR`.** k = **2 / 8** worlds clear the registered 50 %
effect-size bar; median ratio−1 = **−0.4446**.

This is a real negative on target (1)'s *grammar* axis. Nothing was re-run, no parameter was
touched, and the registration was frozen before the run
([`M2P4_STAGE3_FREEZE_V1.json`](M2P4_STAGE3_FREEZE_V1.json), #436) with the scorer validated
against a known answer before use ([`VALIDATION.md`](VALIDATION.md), job 3602070).

## Per world, by effect

| world | n | PARENT_GF_D4 | RESET | ratio−1 | Holm | passes |
|---|---|---|---|---|---|---|
| leaky_seam | 36 | 2 821.1 | 22 403.8 | −0.8741 | 0.00080 | **yes** |
| twin_roots | 50 | 4 015.8 | 28 276.0 | −0.8580 | 0.00080 | **yes** |
| tin_orchard | 38 | 8 612.1 | 23 245.0 | −0.6295 | 0.84352 | no |
| brass_lantern | 38 | 10 094.9 | 19 273.1 | −0.4762 | 1.00000 | no |
| deep_well | 37 | 37 324.6 | 63 591.4 | −0.4131 | 1.00000 | no |
| long_and_short | 49 | 28 536.8 | 36 315.4 | −0.2142 | 1.00000 | no |
| shallow_shelf | 33 | 21 611.0 | 21 089.6 | **+0.0247** | 1.00000 | no |
| narrow_gauge | 84 | 7 762.4 | 4 066.6 | **+0.9088** | 1.00000 | no |

## It is not a uniform collapse

The **precondition** — `PARENT_GF_D4 < RESET` at all — still holds on **6 / 8** worlds
(p ≤ 0.036). On those, history is still helping; what fails is the *magnitude* against the 50 %
bar. Two worlds reverse outright: `shallow_shelf` (p_precondition 0.547) and `narrow_gauge`
(+0.9088, p_precondition 0.999), where the registered arm costs nearly **twice** RESET.

## Attribution: selection, not history — ledger row 56, in a second grammar

The registered primary fixes one library and one depth (MDL, depth 4) for every world. Across
the seven arms, that is the wrong choice on exactly the worlds where the study fails:

| world | best history arm | best / RESET | **GF_D4 / RESET** (registered) |
|---|---|---|---|
| brass_lantern | CONTINUED_OCM | 0.077 | 0.524 |
| deep_well | PARENT_GF_D4 | 0.587 | 0.587 |
| leaky_seam | PARENT_GF_D4 | 0.126 | 0.126 |
| long_and_short | PARENT_GFQ_D3 | 0.719 | 0.786 |
| narrow_gauge | PARENT_GFQ_D3 | 0.783 | **1.909** |
| shallow_shelf | CONTINUED_OCM | 0.375 | **1.025** |
| tin_orchard | PARENT_GFQ_D4 | 0.090 | 0.370 |
| twin_roots | PARENT_GF_D4 | 0.142 | 0.142 |

`PARENT_GF_D4` is the best available arm on only **3 / 8** worlds. This is precisely ledger
row 56's mechanism — *"selection must be costed the way the arm is deployed"*, whose verdict was
**STRUCTURAL at this authoring's tuning stream** (formula argmax right on 5/8 in M2-P2). The same
selection defect reappears in a second grammar. What replicates here is the **failure mode**, not
the benefit.

## A structural hypothesis the shapes suggest

| world | k | chunk lengths | mbl | members | protected | best arm | GF_D4/RESET |
|---|---|---|---|---|---|---|---|
| brass_lantern | 12 | 6x3, 6x4 | 4 | 135 | 38 | CONTINUED_OCM | 0.524 |
| deep_well | 10 | **10x4 (all 4)** | 8 | 100 | 37 | PARENT_GF_D4 | 0.587 |
| leaky_seam | 13 | 7x3, 6x4 | 4 | 130 | 36 | PARENT_GF_D4 | 0.126 |
| long_and_short | 14 | 4x3, 10x4 | 7 | 158 | 49 | PARENT_GFQ_D3 | 0.786 |
| narrow_gauge | 16 | **16x3 (all 3)** | 6 | 224 | 84 | PARENT_GFQ_D3 | **1.909** |
| shallow_shelf | 11 | 6x3, 5x4 | 4 | 105 | 33 | CONTINUED_OCM | **1.025** |
| tin_orchard | 12 | 6x3, 6x4 | 4 | 135 | 38 | PARENT_GFQ_D4 | 0.370 |
| twin_roots | 12 | 5x3, 7x4 | 6 | 144 | 50 | PARENT_GF_D4 | 0.142 |

`narrow_gauge` is the package's only **all-length-3** world, its largest (k=16, 224 members, 84
protected), and the only outright reversal. Its mirror `deep_well` is the only **all-length-4**
world — and there the registered MDL-D4 arm *is* the best available. A depth-4 probe rebuilds
length-4 motifs directly but must compose length-3 motifs to reach the same builders, so a
homogeneous 3-chunk world is exactly where a fixed D4 library should misprice.

**This is a hypothesis, not a finding.** It is read off eight worlds after seeing their scores,
the two extremes are one world each, and nothing here was registered in advance. It is recorded
because it makes the row-56 attribution *testable*: it predicts which library and depth should
pay per world, and that prediction can be registered before the next run rather than fitted
after it.

## The post-hoc figure is NOT a claim

Some history-bearing arm beats RESET on **8 / 8** worlds (0.077 … 0.783). That number is
**descriptive only** and is reported here so the diagnosis is legible. It is chosen *after*
seeing the scores, with no held-out selection rule, so it establishes nothing: picking the
per-world winner post hoc is exactly the move this lane polices. **The terminal is
`C2_NOT_REPLICATED_IN_SECOND_GRAMMAR` and it stands.**

The legitimate revival is a **prospective** per-world selection rule, costed the way the arm is
deployed, registered before it is scored, and tested against the strongest parent. That has not
been done and is not claimed.

## Provenance

Array **3602080**, all eight tasks `COMPLETED` at exit `0:0` — including the two still running
when LUNARC access was lost (`deep_well` 22m57s, `long_and_short` 15m04s). Access was restored
through the billy-laptop hop; the registered resume precondition (#438) ran **first** and
returned `COMPLETE` 8/8, both primary arms present, `all_targets_verified` true, row counts
matching the registration.

Instruments re-verified *after* the outage: scorer `e09c02d4…`, `methods.py` `e0a05654…`, runner
`7d790905…` — all matching the registration.

The scored tree was confirmed to be M2-P4's own worlds and **not** the M2-P2 validation fixture,
which carries identical `m2p4_*_scored` directory names: world ids `brass_lantern`…`twin_roots`
and row counts 38/37/36/49/84/33/38/50, against the fixture's `hc01`…`hc10` and
46/447/303/55/146/55/58/163. Result transferred and sha-verified `f191490f…` at both ends.
