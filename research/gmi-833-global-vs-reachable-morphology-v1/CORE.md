# GMI #833 Global-vs-Reachable Architecture Choice V1

This package closes exactly one #833 Section-J row:

> Separate the optimal candidate architecture from the reachable one.

## Authority

- issue: #874
- source main: `367e14e9296cf79924ce56d89fad34b3769acb5d`
- pre-implementation freeze: `e5b0c534e5d316c90e28dff0678ee6038b25e3a5`
- claim ceiling: `GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE`

## Reproduce

```bash
PKG=$(ls -d research/gmi-833-global-vs-reachable-*v1)
python -I -B $PKG/test_global_vs_reachable_v1.py -v
python -I -O -B $PKG/test_global_vs_reachable_v1.py -v
python -I -B $PKG/global_vs_reachable_v1.py > /tmp/result.json
cmp /tmp/result.json $PKG/RESULT_V1.json
```

The exact checker uses rational arithmetic only. The bounded census is an implementation certificate; the analytic proofs are in `GLOBAL_VS_REACHABLE_THEOREMS_V1.md`.

Parent DRS lifecycle evidence remains authoritative for developmental reachability and lifecycle Pareto model selection.
