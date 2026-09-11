# M2-P2 stage 3 — preview on 7 / 8 scored worlds (not the terminal of record)

The frozen arm set (CONTINUED, RESET, LIBRARY_ONLY, SHUFFLED_HISTORY, ORACLE_FAMILY,
ORDINARY_ADAPTIVE_PARENT) ran on the authored worlds with the m2p1 scripts at the freeze-bound
head `3184131` (LUNARC 3593104). `stage3_preview/m2p2_stage3.py` applies the frozen terminal
precedence, the admission-law check and the frozen statistics to the records; it never re-scores.
hc02-square-shift (1 194 members, 447 future targets) is still running, so this is a **preview**;
the terminal of record is computed once all eight are scored.

```text
preview terminal : CANNOT_CHECK_NO_ADMITTING_WORLD
admission law    : VIOLATED   (per world below)
worlds scored    : 7 / 8     admitting: 0
LIBRARY_ONLY == RESET on every scored world : True   (stored answers worthless, gate G2)
SHUFFLED_HISTORY worse than RESET everywhere : True
```

| world | chunks recovered | admitted | law | held-out strictly better | no-gate parent vs RESET (descriptive) | shuffled > RESET |
|---|---|---|---|---|---|---|
| hc01-binary-ladder | 5 / 6 | no | HOLDS | 43 / 49 | −90.1 % (Holm p 0.0003) | yes |
| hc02-square-shift | — | — | — | — | not yet scored | — |
| hc03-shift-runs | 6 / 8 | no | HOLDS | 163 / 203 | −67.9 % (Holm p 0.0003) | yes |
| hc05-long-form | 5 / 7 | no | HOLDS | 17 / 22 | −72.5 % (Holm p 0.0005) | yes |
| hc06-decoy-pair | 5 / 7 | no | HOLDS | 48 / 63 | −65.7 % (Holm p 0.0003) | yes |
| hc08-drawn-lot-b | 5 / 8 | no | HOLDS | 36 / 46 | −55.2 % (Holm p 0.0143) | yes |
| hc09-negative-ladder | 6 / 6 | no | VIOLATED | 58 / 59 | −86.4 % (Holm p 0.0003) | yes |
| hc10-quartic-climb | 5 / 6 | no | HOLDS | 86 / 108 | −76.7 % (Holm p 0.0003) | yes |

**Reading, per the freeze.** The registered admission rule (universal non-inferiority on the
tuning stream) refuses on every scored authored world, so no world reaches the positive-terminal
test and the frozen terminal is `CANNOT_CHECK_NO_ADMITTING_WORLD` if hc02 also refuses. This is
the same refusal the lane recorded on its own worlds (E5_ADMISSION.md) and is not an assay defect.
The admission law `recovered == all ⟺ admitted` holds on 6 / 7 and is **violated on hc09** (all
six chunks recovered, 58 / 59 held-out tasks strictly better, refused on the one task where the
guided stream proposed the solution later than the baseline) — a boundary of the law, preserved.
The no-gate parent serving the same mined library is 55–90 % cheaper than RESET on every world
(descriptive: the freeze names it as the counterfactual, never deployment), and shuffled
fragments are worse than RESET everywhere, so the structure the author hid was learned.

**Beyond the frozen family (exploratory, labelled as such):** the lane's deployable controller,
which is not in the frozen arm set, beats the strongest parent on all eight authored worlds —
see ../m2p1/INTEGRATED_ARM.md (authored-world table).
