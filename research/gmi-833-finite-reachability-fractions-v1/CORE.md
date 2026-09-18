# GMI #833-F finite reachable quotient fractions v1

This package measures exact protected-semantic reachability mass for every law
in the prospectively frozen four-entry v1 registry. Its universe is the merged
#966 `G0-fin-v1` slice at structural budget `(2,2)`: 576 presentations and 21
classes on protected inputs `(),(0,),(1,)` with step cap 6.

| frozen law | reachable presentations | reachable quotient classes | quotient fraction |
|---|---:|---:|---:|
| `REWRITE_11` | 5 | 4 | `4/21` |
| `CODE_GROWTH_R1` | 126 | 18 | `6/7` |
| `REGISTER_GROWTH_N1` | 14 | 4 | `4/21` |
| `JOINT_GROWTH_22` | 576 | 21 | `1` |

For each law, exhaustive BFS equals an analytic direct characterization and a
source-separated direct-product oracle with its own protected interpreter.
The result also survives all 120 operation-token remints over all 576
presentations and four law-membership predicates (276,480 exact checks).

The allowed terminal is
`GMI_833_FINITE_REACHABLE_QUOTIENT_FRACTIONS_MEASURED_FOR_COMPLETE_DECLARED_LAW_REGISTRY_AT_REGISTERED_SCOPE`.
“Complete” applies only to the four laws frozen before outcomes in commit
`d9ee6f49`; it is not a claim about all possible developmental/search laws.

## Reproduce

```bash
python3 -I -B research/gmi-833-finite-reachability-fractions-v1/test_finite_reachability_fractions_v1.py -v
python3 -I -O -B research/gmi-833-finite-reachability-fractions-v1/test_finite_reachability_fractions_v1.py -v
python3 -I -B research/gmi-833-finite-reachability-fractions-v1/finite_reachability_fractions_v1.py
```
