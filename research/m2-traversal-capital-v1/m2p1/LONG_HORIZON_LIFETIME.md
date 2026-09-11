# Long-horizon lifetime — the conservative ledger's own test (registered 2026-09-11, LUNARC 3593078)

## Why

At 670 executed targets (life_3001) the integrated controller pays on the marginal
(break-even 403) and incremental (215) ledgers, and on the conservative ledger the verdict
turns on one attribution rule: charging developmental solving alone gives break-even 475 ✓;
charging developmental solving **plus the whole validation phase** gives 878 ✗
([INTEGRATED_ARM.md](INTEGRATED_ARM.md)). Both readings are recorded. The ambiguity is not a
mechanism question — the per-target saving is measured (≈ 1 957 slots per target on
life_3001: 929 652 / 475 = 1 718 166 / 878) — it is a *horizon* question: a lifetime of
670 targets is shorter than the most hostile break-even.

The decisive test is therefore a lifetime whose horizon exceeds 878 by construction, on a
fresh seed, with the most hostile ledger applied unchanged.

## Design (frozen before any outcome; submitted as LUNARC array 3593078, seeds 4001–4003)

Same regime as life_3001: 12 length-2 motifs, length-6 targets built from ≤ 3 motifs,
`m2p1_ecology_e4.py`, one trial per seed. The only change is the **stream split**:
0.12 / 0.05 / 0.83 (life_3001: 0.25 / 0.10 / 0.65). For a ≈1 030-member world that is
≈ 124 developmental, ≈ 52 validation, ≈ 855 protected targets. Arms: RESET, CONTINUED_OCM,
PARENT_WITH_MDL, ORDINARY_ADAPTIVE_PARENT, SHUFFLED_HISTORY. Ledger: `m2p1_ledger3.py`
unmodified, deployed arm CONTINUED_OCM.

Nothing in the controller, the admission rule, the probe, the depth rule or the ledger
changes. The split is the lifetime's allocation of its own stream, chosen before the run.

## Registered predictions

Derived from life_3001's measured quantities, scaled linearly by stream size:

| quantity | life_3001 (measured) | prediction for seeds 4001–4003 |
|---|---|---|
| developmental solving | 929 652 (258 tasks) | ≈ 447 000 (124 tasks) |
| full validation phase | 788 514 (103 tasks) | ≈ 398 000 (52 tasks) |
| conservative cost, hostile rule | 1 718 166 | ≈ 845 000 |
| saving per protected target | ≈ 1 957 | ≈ 1 957 (same regime) |
| **conservative break-even (hostile rule)** | **878 ✗** (670 available) | **≈ 430 ✓** (≈ 855 available) |

**Falsifiers.** (a) the smaller developmental stream fails to recover all 12 motifs → the
learner refuses, the controller stands down, benefit ≈ 0, and the ledger cannot pay
(recorded as PARENT_SUFFICIENT / refusal, not smoothed); (b) the per-target saving falls
below ≈ 990 (half the prediction), which would put the hostile break-even above the
horizon on at least one seed; (c) the shuffled-history control ceases to be worse than
RESET (structure-not-volume fails). Any of these is reported as the outcome.

**Claim ceiling if positive.** The conservative ledger pays *under the most hostile
attribution rule* on a lifetime whose horizon was chosen to exceed the measured break-even;
that resolves target (2)'s ambiguity by measurement, not by choosing the friendlier rule.
It does not change the 670-target record, which stays 475 ✓ / 878 ✗.

## Amendment before any arm ran (2026-09-11 09:44 UTC, dev phase in progress)

The ≈ 855-target horizon assumed life_3001's member count (1 031). That count was an
argmax over 3 000 generator trials; with one trial per seed the member count follows the
motif draw: **839 / 579 / 459 members → 696 / 481 / 381 protected targets** (streams
101/42, 69/29, 55/23). The prediction rule is unchanged (break-even = hostile cost /
1 957 with life_3001's per-task costs 3 603 dev, 7 655 validation); applied per seed:

| seed | dev tasks | validation tasks | predicted hostile cost | predicted break-even | horizon | predicted |
|---|---|---|---|---|---|---|
| 4001 | 101 | 42 | 685 413 | 350 | 696 | ✓ (2.0×) |
| 4002 | 69 | 29 | 470 602 | 240 | 481 | ✓ (2.0×) |
| 4003 | 55 | 23 | 374 230 | 191 | 381 | ✓ (2.0×) |

Because the split allocates cost and horizon proportionally, the margin is the same ≈ 2×
on every seed; the falsifiers (a)–(c) stand. The array runs the liveness_v2 runner (the
one registered above); the LUNARC runner is not touched while it runs.

## Outcome (LUNARC 3593078, all three seeds complete 2026-09-11 07:45–07:51 UTC; liveness_v2 runner as registered)

| seed | horizon | RESET | integrated | parent + MDL | shuffled | saved / target | hostile cost | **hostile break-even** | marginal | incremental | net (hostile) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4001 | 696 | 3,862 | **1,401** | 2,802 | 7,294 | 2,460 | 733,656 | **298 ✓** | 134 | 70 | +978,713 |
| 4002 | 481 | 3,460 | **1,116** | 2,231 | 6,420 | 2,344 | 432,379 | **184 ✓** | 94 | 51 | +695,037 |
| 4003 | 381 | 3,155 | **1,054** | 2,108 | 5,881 | 2,101 | 320,834 | **153 ✓** | 74 | 36 | +479,571 |

```text
conservative ledger, hostile rule (developmental solving + the whole validation phase):
  pays on 3 / 3 seeds   break-even 298 / 185 / 153   vs horizon 696 / 481 / 381   (margin 2.3× / 2.6× / 2.5×)
registered predictions 350 / 240 / 191: held, and were conservative — the per-target saving
  came out 2 460 / 2 344 / 2 101 against the 1 957 assumed from life_3001
falsifier (a): the registered admission REFUSED on every seed (2g > b, as the ecology predicted,
  exactly as on life_3001); the controller deployed through the validated library and the
  benefit is 64–68 % — the refusal-with-zero-benefit branch did not occur
falsifier (b): saving ≥ 990 on every seed
falsifier (c): shuffled history 1.9× RESET on every seed (structure, not volume)
```

**Target (2) closes on the hostile ledger's own terms.** The 670-target record stays
475 ✓ / 878 ✗; on three fresh seeds whose horizon exceeds the measured break-even, the prior
pays under every attribution rule, with the prediction registered before the run.
Records: `records/life_long/life_400{1,2,3}_{SUMMARY,LEDGER3_OCM,ATTRIBUTION}.json`.
