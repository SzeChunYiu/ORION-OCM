# G6.1 remaining parent comparison v3

**Frozen v1:** `research/g6-intervention-lab-v1/` (`SELF_EVOLUTION_SUPPORTED_BOUNDED`).
**Frozen v2:** `research/g6-intervention-parents-v2/` (`PARENT_SUFFICIENT`; ATMS/change-impact
cheapest; AutoML/BO `CANNOT_CHECK_NO_BO_LIBRARY`; human-designed `NOT_THIS_CAPSULE`).
Those capsules are not retuned or overwritten.

**This successor** adds the G6.1 *compare against* remainder that is stdlib-tiny
and was still missing after v2, on the same synthetic plant (imported, not copied):

| Bullet | This capsule |
|---|---|
| system-identification | **cited v2** (`s = A f` GF(2)); not rerun |
| structured surrogate | **1-parameter** main-effect surrogate: one integer θ (top-k) on a fixed first-order design. Distinct from v2's 2-factor ANOVA. θ-grid is labeled **not-BO** |
| ATMS/change-impact | **cited v2** and **rerun** as the standing cheapest parent |
| evolutionary search | **random** (1+λ) swap-mutation ES; no crossover. Distinct from v2's permutation GA |
| program repair | **generate-and-test** over the finite power-set patch catalogue. Distinct from v2's GenProg mutate |
| AutoML/BO | `CANNOT_CHECK_NO_BO_LIBRARY` — no package, none invented, no GP/EI stand-in |
| learned selector | **cited v2**; this capsule does **not** train an ML selector |
| human-designed repair | the **authored plant** XOR windows, charged as prior |

`recover source-bound real failure/probe incidents` is a separate G3 worker
(`research/g3-real-failure-v1/`); this capsule does not close that checkbox.

If ATMS remains cheapest on this split (human cost includes prior), the terminal
stays `PARENT_SUFFICIENT`.

Claim ceiling: bounded synthetic plant; not production self-evolution.
No root-cause labels enter parent fit functions.
