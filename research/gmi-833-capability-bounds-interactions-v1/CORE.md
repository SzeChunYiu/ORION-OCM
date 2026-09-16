# GMI #906 finite capability bounds and interactions

This package proves three architecture-name-free finite laws under the upgraded
#833 capability/resource foundation:

- `BOUND-1`: uniform capability floors and constructive lower certificates on
  ceilings are distinct; finite extrema and their opposite inclusion
  monotonicities are exact;
- `INT-1`: a frozen four-cell mixed difference defines interaction at a
  registered design, with a product-threshold iff for strict joint-only synergy;
- `BUDGET-1`: mandatory shared-budget interference has an exact iff, while a
  score-preserving free option cannot harm the optimum.

It also retracts the historical rule that coarse resource-channel overlap alone
determines interaction type.

Replay:

```bash
python3 -I -B research/gmi-833-capability-bounds-interactions-v1/test_capability_bounds_interactions_v1.py -v
python3 -I -O -B research/gmi-833-capability-bounds-interactions-v1/test_capability_bounds_interactions_v1.py -v
python3 -I -B research/gmi-833-capability-bounds-interactions-v1/capability_bounds_interactions_v1.py
```

Claim ceiling:
`GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE`.
