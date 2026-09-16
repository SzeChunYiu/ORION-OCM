# gmi-833-update-law-nfl-v1

Finite, architecture-neutral no-free-lunch boundary for #870 / #833 Section I.

The package proves analytically that under a **uniform distribution over finite target completions consistent with a fixed observed history**, every normalized deterministic or randomized update law has expected held-out accuracy exactly `1/k` for a `k`-label alphabet. It separately constructs nonuniform ecologies that prefer opposite update laws.

This is not a claim that algorithms are equal in real-world structured/nonuniform ecologies.

Reproduce:

```bash
python3 -I -B research/gmi-833-update-law-nfl-v1/test_update_law_nfl_v1.py -v
python3 -I -O -B research/gmi-833-update-law-nfl-v1/test_update_law_nfl_v1.py -v
python3 -I -B research/gmi-833-update-law-nfl-v1/update_law_nfl_v1.py
```

Claim ceiling: `GMI_FINITE_UPDATE_LAW_NO_FREE_LUNCH_BOUNDARY_AT_UNIFORM_COMPLETION_SCOPE`.
