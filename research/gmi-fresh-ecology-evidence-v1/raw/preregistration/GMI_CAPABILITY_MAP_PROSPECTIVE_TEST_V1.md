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
