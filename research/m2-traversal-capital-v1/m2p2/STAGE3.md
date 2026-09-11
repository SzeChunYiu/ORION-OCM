# M2-P2 stage 3 — terminal of record (2026-09-11)

Freeze: [M2P2_FREEZE_V1.json](M2P2_FREEZE_V1.json); stage 2: [STAGE2.md](STAGE2.md). The frozen arm set
(CONTINUED, RESET, LIBRARY_ONLY, SHUFFLED_HISTORY, ORACLE_FAMILY, ORDINARY_ADAPTIVE_PARENT) ran on all eight
viable authored worlds with the m2p1 scripts at the freeze-bound head `3184131` and `methods.py`
byte-identical to main (LUNARC 3593104). `stage3/m2p2_stage3.py` applies the frozen terminal precedence,
the admission-law check and the frozen statistics to the records; it never re-scores. This supersedes
[STAGE3_PREVIEW.md](STAGE3_PREVIEW.md) (7 / 8).

```text
TERMINAL          : CANNOT_CHECK_NO_ADMITTING_WORLD
worlds scored     : 8 / 8        admitting: 0
admission law     : VIOLATED on 2 / 8 (hc02-square-shift, hc09-negative-ladder); holds on 6 / 8
LIBRARY_ONLY == RESET on every world    : True   (stored answers worthless: gate G2)
SHUFFLED_HISTORY worse than RESET everywhere : True
no-gate parent vs RESET (descriptive)   : −14.6 … −90.1 %
```

| world | chunks recovered | admitted | admission law | held-out strictly better | no-gate parent vs RESET (descriptive) | shuffled > RESET |
|---|---|---|---|---|---|---|
| hc01-binary-ladder | 5 / 6 | no | HOLDS | 43 / 49 | −90.1 % (Holm p 0.0004) | yes |
| hc02-square-shift | 6 / 6 | no | VIOLATED | 160 / 224 | −14.6 % (Holm p 0.0004) | yes |
| hc03-shift-runs | 6 / 8 | no | HOLDS | 163 / 203 | −67.9 % (Holm p 0.0004) | yes |
| hc05-long-form | 5 / 7 | no | HOLDS | 17 / 22 | −72.5 % (Holm p 0.0005) | yes |
| hc06-decoy-pair | 5 / 7 | no | HOLDS | 48 / 63 | −65.7 % (Holm p 0.0004) | yes |
| hc08-drawn-lot-b | 5 / 8 | no | HOLDS | 36 / 46 | −55.2 % (Holm p 0.0143) | yes |
| hc09-negative-ladder | 6 / 6 | no | VIOLATED | 58 / 59 | −86.4 % (Holm p 0.0004) | yes |
| hc10-quartic-climb | 5 / 6 | no | HOLDS | 86 / 108 | −76.7 % (Holm p 0.0004) | yes |

**Reading, as the freeze prescribes.** The registered admission rule (universal non-inferiority on the
tuning stream) refused on every authored world, so no world reached the positive-terminal test:
**replication of the positive terminal is not measurable on this authoring** (`CANNOT_CHECK_NO_ADMITTING_WORLD`).
It is not `AUTHORSHIP_CONTAMINATED` (hostile clean with controls), not `SURFACE_DERIVABLE` (G-SURF PASS 8 / 8),
and not an assay defect (every target verified; LIBRARY_ONLY = RESET by construction everywhere). The
admission law `recovered == all chunks ⟺ admitted` is **violated on hc02-square-shift, hc09-negative-ladder** — every hidden
chunk recovered, refused on a single held-out task where the guided stream proposed the solution later
than the baseline — a boundary of the law found on independently authored worlds and preserved.

What the frozen family does show, descriptively: the structure the author hid was learned (the mined
library served without the gate beats RESET on 8 / 8, Holm-significant; shuffled fragments are worse
than RESET on 8 / 8). What the frozen family cannot show — deployment under the registered rule — is
exactly the gap the lane's deployable controller was built for; it is not in this frozen family and is
reported only as a labelled exploratory arm (m2p1/INTEGRATED_ARM.md: it beats the strongest parent on
8 / 8 authored worlds).

Secondary (per the freeze): the dose ladder and E8-horizon ledger for hc02 were still running when the
terminal was computed; they cannot change the primary terminal and are appended when they land.
#323, #277 and #165 stay open regardless of outcome, as the freeze requires.
