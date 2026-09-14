# GMI capability interactions v1

This capsule closes the first four rows of issue #602 section F3 at bounded finite scope:

1. memory × planning;
2. memory × abstraction;
3. search × learned heuristic;
4. social modeling × communication.

The registry is `INTERACTIONS_TRANCHE1_V1.json`; proofs are in `FORMALIZATION_V1.md`; executable controls are in `capability_interactions_v1.py` and `test_capability_interactions_v1.py`.

The laws are deliberately architecture-name-free. They state exact resource/distinguishability interactions, include negative twins and nearest assumption failures, and stay at claim ceiling **G2**. They do **not** claim the morphology-to-capability map of G6, empirical universality, or that capability interactions are always beneficial.

Run locally:

```bash
python3 -I -B research/gmi-capability-interactions-v1/test_capability_interactions_v1.py -v
python3 -I -O -B research/gmi-capability-interactions-v1/test_capability_interactions_v1.py -v
```
