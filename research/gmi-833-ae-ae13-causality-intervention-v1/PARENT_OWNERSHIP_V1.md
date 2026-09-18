# AE13 parent-ownership disclosure v1

## What is parent-owned and is NOT claimed novel

| result | parent | citation |
|---|---|---|
| the `do` operator, truncated factorisation, identifiability | Pearl | doi:10.1093/biomet/82.4.669; doi:10.1017/CBO9780511803161 |
| Markov equivalence: same skeleton, same v-structures; the CI-set characterisation | Verma & Pearl 1990; Andersson, Madigan & Perlman 1997 | doi:10.1214/aos/1031833662 |
| causal discovery from observational data and its limits | Spirtes, Glymour & Scheines 2000 | doi:10.7551/mitpress/1754.001.0001 |
| bounds on causal effects under non-identification | Manski 1990; Balke & Pearl 1997 | doi:10.1080/01621459.1997.10474074 |
| optimal experimental design for causal discovery | Eberhardt, Glymour & Scheines 2005; Hauser & Bühlmann 2014 | doi:10.1111/rssb.12071 |
| causal representation learning as a programme | Schölkopf et al. 2021 | doi:10.1109/JPROC.2021.3058954 |
| the computational-mechanics `causal state` | Shalizi & Crutchfield 2001 | doi:10.1023/A:1010388907793 |

That observational data underdetermines causal structure is **entirely
parent-owned**. Three of the six crosswalk entries terminate
`PARENT_SUFFICIENT`, which under the #833 doctrine is a success terminal.

## The named residual of this tranche

1. **The census, not the example.** The parents give the impossibility in
   general. What is not in them is the exhaustive count over a completely
   enumerated model space: which of the eleven classes actually realise a
   disagreement over a frozen rational grid, how many joints are shared, how
   many pairs disagree, and — the part usually left out — how many classes and
   groups are **identified**. Both quantifiers are counted.

2. **The exact price of an experiment, with its zero.** The break-even
   tolerance is computed as an exact rational and the verdict is shown to flip
   at it, above it and below it. A named specification with value of
   intervention exactly `0` is exhibited, which is what forbids the promotion
   *intervention is always worth its cost*.

3. **A proved zero.** `CAUSAL_STRICTLY_REFINES = 0` is accompanied by a
   structural argument, so it is a theorem at this scope rather than the
   absence of a search result. Distinguishing those two is the point of the
   row.

4. **The conflation guard.** The two senses of `causal state` — computational
   mechanics' predictive equivalence class and Pearl's interventional structure
   — are separated in the machine-readable crosswalk and the conflation is a
   registered forbidden promotion, so a later tranche cannot quietly merge them.

## What is explicitly NOT claimed

No latent-confounder result. No multi-variable interventions. No continuous
variables. No impossibility of causal discovery. No morphology or architecture
selection law — the Tier-2 morphology row of AE13 is already earned by
`gmi-833-ae-morphology-sweep-v1` and is explicitly not re-closed here.
