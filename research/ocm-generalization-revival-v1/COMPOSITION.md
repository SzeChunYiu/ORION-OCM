# RV-A adjacent result: the GSA6 lever package traded T3-eligible composition for yield

Parent: [CORE.md](CORE.md). Receipt: `results/RVA_A2_DRAW_INVARIANCE.json`
(`composition` block).

Because `NOT can_check ⟺ FAIL` is exact, the checker-bearing fraction of an
arm's survivor set **is** that arm's T3 hold rate. That makes the R2 arm table
readable as a composition table without any new evaluation.

## Exclusive distinct survivors (phenotypes found by that arm alone)

| arm | novelty gate | dedup promotion | cumulative surrogate | n excl. | can_check | fraction (Wilson 95%) | distinct/seed | morph/cpu-h |
|---|---|---|---|---|---|---|---|---|
| GSA5P_fixed | – | – | – | 12095 | 2114 | 0.1748 [0.1681, 0.1817] | 2251.3 | 71486 |
| GSA6_NG | ✓ | – | – | 11884 | 2372 | 0.1996 [0.1925, 0.2069] | 2202.0 | 58404 |
| GSA6_DP | – | ✓ | – | 32879 | 6768 | 0.2058 [0.2015, 0.2102] | 5802.0 | 190527 |
| GSA6_SC | – | – | ✓ | 8856 | 1456 | 0.1644 [0.1568, 0.1723] | 1723.2 | 42186 |
| GSA6_ALL | ✓ | ✓ | ✓ | 32770 | 1773 | 0.0541 [0.0517, 0.0566] | 5802.0 | 127710 |

Pooled over all arms: 15668 / 100693 = 0.1556 [0.1534, 0.1579].

## The equal-yield comparison

`GSA6_DP` and `GSA6_ALL` report the **same** `mean_distinct_per_seed` (5802.0)
and near-identical exclusive survivor counts (32879 vs 32770). At that matched
yield:

- DP alone: **6768** checker-bearing exclusive survivors.
- Full package: **1773** — a 3.82× shortfall, intervals disjoint by a wide margin.

DP alone is also cheaper (190527 vs 127710 morphologies per CPU-hour, 0.1825 vs
0.2714 CPU-hours). So on the axis the T3 gate reads, the package is strictly
dominated by one of its own components at equal yield and lower cost.

## Bearing on the committed terminal

`GS_R2_AGGREGATE.json` records `terminal_rule_id:
LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY`, selected on distinct-yield. That
rule remains true as stated — the package does beat the surrogate parent on
yield. What the composition table adds is that the package's yield gain is
partly purchased by enriching `hierarchical_fibred` checker-free morphologies,
the exact route the T3 correctness gate rejects. Distinct-yield and
T3-eligible-yield are not the same objective, and on this evidence they point
to different arms.

This is decision support for the next allocation, consistent with the R2
evidence class `EXPLORATORY_ADAPTIVE`. It is not a programme terminal and does
not supersede the committed rule.

## Caveat carried forward

These are counts of distinct **phenotypes** as the R2 arms deduplicated them.
The comparison above is like-for-like (all five arms counted the same way), but
any comparison against a grammar-space enumeration must be re-derived at the
phenotype level before the ratios are quoted together.
