# SUPPLEMENT 2 — correction to FREEZE_V4_POWER_ADDENDUM section 3

`FREEZE_V4_POWER_ADDENDUM.md` is left exactly as committed. This supplement
records an arithmetic error in its prose.

**The error.** Section 3 says `SIGMA_ARCH2` has "160 machines". It has **176**.
The registered parameter sets are `FF (1,2,3)`, `REC (2,3,6)`, `CTR (2,3,4)` and
`STK (1,2)` — eleven mechanism/parameter combinations, each crossed with two
register settings and eight head wirings: `11 × 2 × 8 = 176`.

**What is unaffected.** The binding artifact is the sha256 of the frozen
prediction stream, `e24e90d7849d716e…`, which was computed over the actual 176
realizations and is reproduced byte-exactly by route B. The frozen prediction
counts in section 5 (9,488 point emissions, 2,400 non-degenerate, 6,640
abstentions, 35,712 inconsistent) are likewise the true figures for the real
population. `RESULT_V1.json` and `ROUTE_B_RESULT_V1.json` both report
`population = 176`, and the closed-form capability law agrees with brute-force
simulation on **176/176** machines.

Only the prose count in section 3 was wrong. `SIGMA_SYN2`'s stated count of 128
is correct (`4 × 2 × 8 × 2`).
