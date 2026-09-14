# Developmental History Phase Law V1: read first

Given a morphology M and ecology E, the developmental trajectory (infant to
child to adult) is predicted by the same PVR-3 pressure that determines the
adult morphology. Trajectory length is proportional to
log(running_need / initial_capacity).

| Files | What |
|-------|------|
| [DEV_HISTORY_PHASE_THEOREM_V1.md](DEV_HISTORY_PHASE_THEOREM_V1.md) | Formal theorem: trajectory length formula, three theorems, corollaries |
| [dev_history_witness.py](dev_history_witness.py) | Exact computation: 3 morphologies x 3 ecology types, trajectory lengths |
| [test_dev_history.py](test_dev_history.py) | 10 unittest controls: monotonicity, negative twin, separation, burden |

Run tests: `python3 -I -B test_dev_history.py -v`
