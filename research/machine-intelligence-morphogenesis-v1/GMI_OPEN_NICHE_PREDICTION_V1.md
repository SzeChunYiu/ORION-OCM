# An undiscovered niche, and a provably empty region — predicted before measurement

Date: 2026-09-13. Follows `GMI_NICHE_FREQUENCY_LAW_V1.md`, whose four predictions held. That law is here
**inverted**: instead of asking how much space a known family occupies, it asks what space is left over,
and what a machine would have to be to occupy it.

## The two regions, derived

Admissibility requires `min6 ≥ θ` and `min6 − bc ≥ 1 fx = 1/24 ≈ 0.04167`. Two thresholds follow from
quantities already measured:

| threshold | derivation | meaning |
|---|---|---|
| `bc > 0.9236` | exact search's ceiling 0.9653 − 1/24 | **the best known family fails** |
| `bc > 0.9583` | the capability cap 1.0 − 1/24 | **no machine can clear the margin, however good** |

Measured against the constant distribution (3 000 uniform draws):

| region | size |
|---|---:|
| exact search fails (`bc > 0.9236`) | **2.6 %** |
| **open niche** (`0.9236 < bc ≤ 0.9583`) | **≈ 2.5 %** |
| **provably unoccupiable** (`bc > 0.9583`) | **0.1 %** |

## What each region is

**The provably unoccupiable region is a derived boundary, not an observation.** Where the best constant
already sits within 1 fx of the maximum attainable capability, *no* machine can satisfy rule 40 — a
perfect machine at 1.0 still fails to beat the baseline by the required margin. This is the first region
in this corpus that is empty by derivation rather than by failure to find anything. It is small (0.1 %)
but it is exactly the kind of statement the programme's ceiling half is supposed to produce: a limit on
how far capability can go that does not depend on any development law.

**The open niche is the interesting one.** Across ≈ 2.5 % of the construction space, the strongest known
family cannot clear the margin, yet the cap leaves room: a family with ceiling in `(bc + 1/24, 1.0]` would
be admissible there. **No known species occupies it, and it is not empty by necessity.** That is a
predicted undiscovered domain with its required capability stated: to occupy it a machine needs
`min over six ≥ bc + 1/24`, i.e. **above 0.9653 and up to 1.0** — better than exact search, on targets
whose constant baseline is already very strong.

## Registered prediction

Twelve ecologies are drawn by rejection sampling from the same grid, keeping only those with
`0.9236 < bc ≤ 0.9583`, seeded by `sha256(b"GMI-OPEN-NICHE-V1")`. All nine hand-built rows measured under
the six interventions.

| id | prediction | falsifier |
|---|---|---|
| **O1** | **no** row is admissible on **any** of the twelve | any row admissible anywhere |
| **O2** | exact search still scores highest of the nine on ≥ 10 of 12, i.e. it fails on margin rather than collapsing | some other row scores higher on ≥ 3 |
| **O3** | exact search's min over six stays ≥ 0.887 — its ceiling is target-independent even where it is not enough | below 0.887 on ≥ 3 |

`O1` is the substantive claim: the niche is open *and unoccupied by anything the corpus knows*. `O2` and
`O3` guard the interpretation — if search collapsed on these targets the region would be uninteresting for
a different reason, namely that these targets are simply hard, rather than that their baseline is strong.

## Scope

Admissibility over one construction at one θ with hand-built rows; nothing about reachability. A confirmed
`O1` would not prove no machine can occupy the niche — only that none of the nine registered families does,
which is the same presence/absence asymmetry the `M′` rule imposes everywhere else. The *unoccupiable*
region is different: that one is derived, and no search could overturn it.

---

# RESULT — O1 and O2 FAILED, O3 held, and both failures share one root cause

Seed `236716253`, twelve ecologies rejection-sampled into `0.9236 < bc ≤ 0.9583`, all nine rows.
Receipt `STAGE_OPEN_NICHE_V1.json`.

| id | prediction | outcome |
|---|---|---|
| **O1** | no row admissible on any of the twelve | **FAILED** — `E_open4` admits both search rows |
| **O2** | exact search scores highest on ≥ 10 of 12 | **FAILED** — 8 of 12; memory tops the other four |
| **O3** | exact search min over six ≥ 0.887 throughout | **HELD** — 12 of 12 |

## The root cause, one error behind both failures

**I used point estimates of family ceilings to define a boundary, and then conditioned on the tail.**

The band's lower edge, 0.9236, came from exact search's *mean* ceiling 0.9653 minus the margin. But that
ceiling is a distribution with stdev 0.026. On `E_open4` (`bc = 0.9271`, requiring 0.9688) search attained
**exactly 0.9688** and cleared by precisely 1.0 fx. A boundary drawn from a mean cannot bound a
distribution's reach.

The same error explains O2. The ordering search > memory was measured as an average over a
*representative* draw. This band is a **selected subpopulation** — conditioned on high baseline — and the
ordering inverts there: `hamming_knn_k3` tops `E_open3`, `E_open5`, `E_open8` and `E_open9`. A law
calibrated on marginal statistics does not transfer to a conditioned tail, and I applied it as if it did.

That the niche-frequency law's own predictions held on a representative draw and fail here is not a
contradiction — it is the distinction between a marginal and a conditional claim, which I collapsed.

## What survives, corrected

**O3 is the durable part.** Exact search held ≥ 0.887 on all twelve of the hardest targets in the space.
Its ceiling is genuinely robust; what varies is whether that ceiling clears the *local* margin.

**The open niche is mostly real, but it is not a band.** Eleven of twelve band ecologies are occupied by
nothing. But unoccupancy cannot be defined by a fixed `bc` threshold derived from mean ceilings. The
correct test is per-ecology: **an ecology is unoccupied iff every family's attainable ceiling there falls
below `bc + 1/24`.** That is a measurement, not a boundary formula.

**Corrected registration for any successor test:** compute the band from the *maximum attained* ceiling
rather than the mean, and state family-ordering claims as marginal unless re-measured on the conditioned
subpopulation.

The **provably unoccupiable** region is untouched by all of this: where `bc > 1 − 1/24 = 0.9583`, no
machine clears the margin whatever its ceiling, because capability is capped at 1.0. That derivation uses
no ceiling estimate at all, which is exactly why it survives.
