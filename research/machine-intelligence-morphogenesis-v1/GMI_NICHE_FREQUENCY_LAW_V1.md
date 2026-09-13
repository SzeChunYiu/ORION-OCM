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

---

# RESULT — all four predictions held, and the quantitative one to within a point

Seed `902521130`, twelve ecologies, all nine rows, 108 cells. Receipt
`STAGE_NICHE_FREQUENCY_V1.json`. The draw is representative: its mean best constant is 0.8411 against the
space's 0.8363.

| row | admissible | frequency |
|---|---:|---:|
| `program_search` | 11 / 12 | **92 %** |
| `compiled_search` | 11 / 12 | **92 %** |
| `hamming_knn_k3` | 3 / 12 | **25 %** |
| `soft_retrieval` | 0 / 12 | 0 % |
| `gradient_net_h2`, `_h4` | 0 / 12 | **0 %** |
| `exemplar_table`, `constant_emitter`, `particles_p4` | 0 / 12 | 0 % |

| id | predicted | observed | outcome |
|---|---|---|---|
| **N1** | exact search ≥ 85 % | 92 % | **HELD** |
| **N2** | memory 10 – 40 % | **25 %** | **HELD** |
| **N3** | no learner anywhere | 0 of 12 | **HELD** |
| **N4** | search > memory > retrieval > learners | 92 > 25 > 0 = 0 | **HELD** |

**`N2` is the result.** The band came from a derived point estimate: memory's ceiling is 0.8524, the
rule-40 line demands `bc ≤ 0.8524 − 1/24 = 0.8107`, and the constant distribution puts that just under its
p25 — about **24 %**. Measured: **25 %**. A frequency predicted from two independently measured
distributions, landing within a point.

Likewise `N1`: search's ceiling of 0.9653 requires `bc ≤ 0.9236`, which sits above the space's p90;
predicted "very high", measured 92 %.

## What the law now lets the corpus say

For a family with a roughly target-independent ceiling `c ≥ θ`, its **niche frequency** over this
construction is `P(bc ≤ c − 1/24)`. So a capability ceiling converts into *how often that species can
exist at all* — which is a different and more useful quantity than a count over a curated registry, and
one the registry could not have given, since its own constants sit well below the space's.

Read as a statement about the known species:

* **exact search occupies ~92 % of the space** — near-universal, because its ceiling clears almost every
  baseline;
* **memory occupies ~25 %** — a real but minority niche;
* **learners occupy ~0 %** here, and the one registered ecology admitting one is at the **0.2nd
  percentile** of baseline weakness. Their niche is not merely small; it requires an outlier.

## Scope, and one instrument note

Admissibility over one construction, one basis, θ = 0.85, hand-built rows. **Nothing here touches
reachability**: `DU-1` stands, and the gap remains live — exact search is admissible on ~92 % of the space
while the class-rate record recovers the program class on 1 of 3 seeds.

Instrument note: the runner was derived by substitution from the five-ecology script, so its summary lines
print "of 5" while counting twelve. The counts (11, 12, 3) and the receipt are over the full twelve; only
the literal in the printed text is stale.
