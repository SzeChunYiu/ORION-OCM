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
