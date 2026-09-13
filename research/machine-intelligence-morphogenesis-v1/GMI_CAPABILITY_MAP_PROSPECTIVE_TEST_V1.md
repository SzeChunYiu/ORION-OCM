# Prospective test of the family capability map

Date: 2026-09-13. **Registered before the ecologies exist.** Every earlier registration in this session
was made against data that already existed somewhere, which is why their prospectivity claims were
retracted. This one fixes the construction rule in advance, so the targets are determined by this
document rather than chosen after seeing anything.

## What is being tested

`GMI_LEARNER_ADMISSIBILITY_MAP_V1.md` measured nine hand-built rows on the six registered ecologies and
found:

| family | mean (min over six interventions) | stdev | admissible on |
|---|---:|---:|---|
| exact search (`program_search`, `compiled_search`) | 0.9653 | 0.0260 | 6 of 6 |
| memory (`hamming_knn_k3`) | 0.8524 | 0.0435 | 3 of 6 |
| learners (`gradient_net_h2`, `_h4`) | 0.6788 / 0.7335 | 0.0406 / 0.0560 | 0 of 6 |

If that map describes the families rather than the six ecologies it was measured on, it should predict
behaviour on ecologies nobody has looked at.

## Construction rule, fixed here

Fresh ecologies are `spec_smooth(coeffs, name)` over coefficient 4-tuples drawn from the grid
`{i/16 : i ∈ [−8, 8]}` by `random.Random(seed)` with

```
seed = int(hashlib.sha256(b"GMI-CAPMAP-PROSPECTIVE-V1").hexdigest()[:8], 16)
```

rejecting any tuple already in `ecology.REGISTRY`, until **five** are accepted, named `E_fresh1…E_fresh5`.
The seed string is frozen by this commit; the tuples are a consequence of it and were not inspected
before writing the predictions below.

## Predictions

| id | prediction | falsifier |
|---|---|---|
| **P1** | both exact-search rows are admissible (min over six ≥ θ = 0.85 **and** ≥ 1 fx over that ecology's best constant) on **≥ 4 of 5** fresh ecologies | admissible on ≤ 3 |
| **P2** | **no** `gradient_net` row is admissible on **any** fresh ecology | any one is |
| **P3** | exact-search min over six stays in **[0.887, 1.0]** on ≥ 4 of 5 — the measured mean less three standard deviations | outside that band on ≥ 2 |
| **P4** | memory (`hamming_knn_k3`) is admissible on **1–4** of 5, i.e. neither everywhere nor nowhere | 0 of 5 or 5 of 5 |

`P3` is the one that tests the map as a *quantitative* claim rather than a ranking. `P4` is deliberately
weak and is included because a map that only ever predicts "search wins" would be worth little.

## What a pass would and would not buy

A pass would show the family ceilings measured on six ecologies transfer to ecologies drawn from the same
construction — evidence that they are properties of the families. It would **not** extend beyond smooth
coefficient targets on this basis at this θ, and it would say nothing about reachability: `DU-1` holds
regardless, and every row here is hand-built rather than searched.

A `P2` failure would be the most interesting outcome available, since it would mean a learner is
admissible somewhere in this construction and the corpus's coefficient-class negative has a live
counterexample to examine.

---

# RESULT — three of four held, including the quantitative one

Seed `753793017` produced the five coefficient tuples below. Receipt:
`STAGE_FRESH_ECOLOGY_CAPABILITY_V1.json`.

| ecology | coefficients | best constant | `program_search` = `compiled_search` (min over six) | margin (fx) |
|---|---|---:|---:|---:|
| `E_fresh1` | (0.1875, 0.0, −0.4375, 0.125) | 0.8542 | 0.9479 | +3.37 |
| `E_fresh2` | (−0.5, −0.0625, 0.375, −0.0625) | 0.8333 | 0.9583 | +4.50 |
| `E_fresh3` | (0.3125, −0.3125, −0.375, −0.125) | 0.8542 | 0.9167 | +1.50 |
| `E_fresh4` | (−0.1875, 0.1875, −0.0625, 0.0) | 0.9271 | 0.9688 | +1.50 |
| `E_fresh5` | (0.5, 0.5, −0.4375, 0.375) | 0.8229 | 0.9583 | +3.25 |

| id | prediction | outcome |
|---|---|---|
| **P1** | exact search admissible on ≥ 4 of 5 | **HELD** — 5 of 5, both rows |
| **P2** | no `gradient_net` admissible anywhere | **HELD** — 0 of 5, best 0.8594 |
| **P3** | exact-search min over six within [0.887, 1.0] on ≥ 4 of 5 | **HELD** — 5 of 5, range 0.9167–0.9688 |
| **P4** | memory admissible on 1–4 of 5 | **FAILED** — 0 of 5 |

`P3` is the one worth dwelling on. It predicted a *numeric band*, derived from a mean and standard
deviation measured on six other ecologies, and every one of five unseen targets landed inside it. The
family ceiling is a property of the family, at least across this construction.

## Why P4 failed, separated from the fact that it failed

**It failed as registered, and that stands.** The account below is post-hoc and is labelled so.

Memory was not weak on these ecologies — it scored 0.8802, 0.8542, 0.8542, 0.9375, 0.8125, clearing
θ = 0.85 on three of five. It failed the **margin**, not the threshold. These five ecologies have unusually
strong constants (mean 0.858 against the registered six's 0.809; `E_fresh4`'s is 0.9271), so memory's
ceiling left it 0.25–0.62 fx of headroom where 1.0 is required.

That is the mechanism proposed in the map itself — admissibility is governed by how much room the constant
leaves — operating harder than I allowed for. But **I did not predict the constants would be strong**, so
this is an explanation after the fact, not a second confirmed prediction. The real error is in my
calibration: I set P4's range assuming fresh ecologies would resemble the registered ones, and a uniform
draw over the coefficient grid does not reproduce a hand-curated registry's distribution of constants.

## What this buys, and what it does not

**Buys:** the capability ceilings of the exact-search and learner families transfer to unseen targets from
this construction, and the search family's transfers *quantitatively*. The map is about the families.

**Does not buy:** anything outside smooth coefficient targets on this basis at this θ; anything about
reachability, since every row here is hand-built and `DU-1` stands; and any claim that memory is
inadmissible in general — on the registered six it is admissible on three, and what changed here is the
baseline it must beat, not the family.

**Recorded as the session's one clean prospective test.** The registration was committed and pushed before
the ecologies existed, so unlike the `X` and `Z` registrations earlier today, there is no question of the
answer having been available beforehand.
