# GMI capability real-regime v1

Bounded executable replication for #602 F4 across four task regimes:

- factual/science retrieval -> `memory_exact`
- math/proof chain -> `planning_exact`
- code patch verification -> `verified_tool_exact`
- sensor/actuator control -> `coordination_exact`

Each domain has a frozen positive case at threshold and a matched negative twin with exactly one load-bearing signed margin reduced by one. `test_real_regime_v1.py` requires the already-merged development-only predictor to agree with an independent executable verifier on all eight cases.

Claim ceiling: **G3**. This is not general G6 closure and does not claim open-ended benchmark or physical-world transfer.
