# A niche-frequency law, registered before measurement

Date: 2026-09-13. Registered **before the test ecologies exist**, like
`GMI_CAPABILITY_MAP_PROSPECTIVE_TEST_V1.md` and unlike the `X`/`Z` registrations earlier today.

## The law

Two things are now measured independently:

* **family ceilings** — each family's minimum over the six interventions, roughly stable across ecologies
  for the flat families (`GMI_LEARNER_ADMISSIBILITY_MAP_V1.md`);
* **the distribution of best constants** over the construction space — mean 0.8363, stdev 0.0439, with
  p10/p25/p75/p90 at 0.7812 / 0.8125 / 0.8646 / 0.8958 (`GMI_ECOLOGY_REGISTRY_SAMPLING_BIAS_V1.md`).

Admissibility requires `min6 ≥ θ = 0.85` **and** `min6 − bc ≥ 1 fx = 1/24`. If a family's ceiling `c` is
roughly ecology-independent, its **niche frequency** — the fraction of the space where it is admissible —
is predicted by

> **`P(admissible) ≈ P(bc ≤ c − 1/24)`**, provided `c ≥ θ`.

This converts a capability ceiling into *how often that species can exist at all*, which is the question
the registry's "n of 6" counts cannot answer.

## Predictions

From the measured ceilings and the measured constant distribution:

| family | ceiling `c` | requires `bc ≤` | predicted niche frequency | registered band |
|---|---:|---:|---|---|
| exact search (`program_search`, `compiled_search`) | 0.9653 | 0.9236 | above p90 → very high | **≥ 85 %** |
| memory (`hamming_knn_k3`) | 0.8524 | 0.8107 | just under p25 | **10 – 40 %** |
| retrieval (`soft_retrieval`) | 0.8142 | — (`c < θ`) | ceiling below θ | **≤ 10 %** |
| learners (`gradient_net_h2`, `_h4`) | 0.6788 / 0.7335 | 0.637 / 0.692 | far below p10 | **0 %** |

| id | prediction | falsifier |
|---|---|---|
| **N1** | exact search admissible on **≥ 85 %** of a uniform draw | below 85 % |
| **N2** | memory admissible on **10–40 %** | outside that band |
| **N3** | no `gradient_net` admissible on **any** ecology of the draw | any one is |
| **N4** | the ordering search > memory > retrieval > learners holds on the draw | any inversion |

## Test

12 ecologies drawn by `random.Random(int(sha256(b"GMI-NICHE-FREQ-V1")[:8],16))` from the same grid,
rejecting registry duplicates. **All nine rows measured, including the expensive search rows** — excluding
rows by cost is the error corrected in `GMI_LEARNER_ADMISSIBILITY_MAP_V1.md`, and cost correlates with
capability here.

## Scope

`N1`–`N4` are about *admissibility over a construction*, not about reachability: every row is hand-built,
and `DU-1` says the reachable frontier does not follow from the admissible one. A pass would mean the
corpus can state where each known species can live as a frequency rather than a count over a curated
registry. It would not extend beyond smooth coefficient targets on this basis at this θ.
