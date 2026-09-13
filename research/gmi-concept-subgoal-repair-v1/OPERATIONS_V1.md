# Replay

Use laptop CPython3.12. Keep all generated output outside the frozen unit.

```sh
python3 -I -B -m unittest discover -s research/gmi-concept-subgoal-repair-v1 -p 'test_*v1.py'
python3 -I -B -O -m unittest discover -s research/gmi-concept-subgoal-repair-v1 -p 'test_*v1.py'
python3 -I -B research/gmi-concept-subgoal-repair-v1/replay_v1.py > /tmp/gmi-concept-subgoal-replay.json
```

The replay compares the complete original-and-repaired payload and anchors full
unit membership and receipt bytes before/after. Git/source bindings preserve
origin, not external experiment authenticity. No historical or native campaign
is called. The two small supplied table/string source scripts are reproduced.
