# CORE — `gmi-833-mtg-naturality-tiers-v1` (issue #833, programme comment 5687604615)

**Rows.** Four MTG-3 rows (indices 11, 12, 15, 16 of `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json`):
exact and approximate commuting squares; the static / learning-compatible / full-equivalence
distinction; tracking path dependence instead of erasing it through final-output equivalence; and the
extension to stochastic update kernels with an exact defect interval.

**Claim ceiling.** `GMI_833_MTG_APPROXIMATE_AND_STOCHASTIC_NATURALITY_TIERS_AT_REGISTERED_FINITE_SCOPE`

| result | statement | numbers |
|---|---|---|
| NAT-1 | `eps` exact; `eps(U∘T) ≤ eps(T)+eps(U)` (discrete metric); Lipschitz-weighted bound under the registered metric; `eps=0` recovers the parent | 19,683/19,683 pairs; 2,457 + 10,395 trajectory checks |
| NAT-2 | tiers `FULL ⊂ EXACT ⊂ LC(1/2) ⊂ STATIC`, every inclusion strict by a recorded witness | census 36/24/9/5 of 243; differences 4/15/12 |
| NAT-3 | final outputs agree on every word yet the trajectory tracker reports mismatches; hysteresis witness `ab` vs `ba` | 45 rows, 0 final-output mismatches, 34 tracker mismatches |
| NAT-4 | `tv` exact; subadditive; deterministic lift gives `tv = eps`; interval `[0, tv]`; deterministic-overclaim hostile | 19,683/19,683; 243/243; overclaim `eps=0` vs `tv=1/4`; null 0/200 |

**Two routes.** `naturality_tiers_v1.py` (direct definitions, dictionary push-forward) and
`independent_oracle_v1.py` (integer-indexed trajectory enumeration, vector–matrix kernel products; imports
nothing from route A). 86 shared quantities agree. Eight hostiles, each applicable and detected.

**Reproduce (laptop or CI, never the Mac mini).**

```
python3 -I -B  research/gmi-833-mtg-naturality-tiers-v1/naturality_tiers_v1.py
python3 -I -B  research/gmi-833-mtg-naturality-tiers-v1/independent_oracle_v1.py
python3 -I -B  research/gmi-833-mtg-naturality-tiers-v1/test_naturality_tiers_v1.py
python3 -I -O -B research/gmi-833-mtg-naturality-tiers-v1/test_naturality_tiers_v1.py
```

Receipts are byte-identical between the two modes.

**Not claimed.** Optimizer equivalence, real learning dynamics, Bayesian or latent uncertainty,
universal hysteresis, continuous-state naturality, complete GMI.
