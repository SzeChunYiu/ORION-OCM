# GMI #913 capability abstention

This package binds external capability queries to the merged typed-uncertainty
contract. A unique point is emitted exactly for a singleton capability image;
multi-valued images carry their complete identified set and must abstain.
Inconsistency and missing query semantics remain distinct terminals, confidence
budgets remain explicit, and feasible sets cannot fabricate calibration.

Replay:

```bash
python3 -I -B research/gmi-833-capability-abstention-v1/test_capability_abstention_v1.py -v
python3 -I -O -B research/gmi-833-capability-abstention-v1/test_capability_abstention_v1.py -v
python3 -I -B research/gmi-833-capability-abstention-v1/capability_abstention_v1.py
```

Claim ceiling: `GMI_833_CAPABILITY_IDENTIFICATION_ABSTENTION_AT_REGISTERED_FINITE_SCOPE`.
