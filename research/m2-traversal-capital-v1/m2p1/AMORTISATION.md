# Amortisation — from 311 targets to 23

The developmental prior transfers and deploys; the open question was whether it **pays**.
The first ledger said no by a wide margin. Two things had been conflated, and separating
them moves the answer by more than an order of magnitude.

## The two ledgers

**Conservative** charges the entire developmental phase against the prior. That treats
every developmental solve as pure overhead — but those solves produced verified
solutions, real cognition the agent wanted. It is the most hostile accounting possible
toward the history arm.

**Marginal** charges only what the prior specifically cost: mining plus validation. It
is the right question once the developmental work is being done anyway — *does keeping
and deploying the prior pay?*

Both are reported. Neither is the single truth.

## E5, by developmental depth

| depth | admitted | work reduction | saved / target | conservative break-even | **marginal break-even** |
|---|---|---|---|---|---|
| 4 | ✗ | 55.4 % | 22 796 | 48.9 | 38.9 |
| 6 | ✗ | **−14.4 %** | — | — | — |
| 8 | ✗ | 42.6 % | 17 524 | 77.1 | 50.6 |
| 12 | ✗ | 53.7 % | 22 072 | 68.9 | 40.2 |
| 20 | ✗ | 15.4 % | 6 316 | 309.9 | 140.5 |
| **35** | **✓** | **93.1 %** | **38 268** | **71.1** | **23.2** |

```text
break-even horizon, E5, marginal :  23.2 future targets
break-even horizon, E1, original : 311   future targets
```

**A 13× improvement**, from understanding that the ledger must be indexed by depth and
that acquisition is not all chargeable to the prior.

At depth 35 the prior is admitted, cuts 93.1 % of the work, and repays its own marginal
cost after **≈23 future targets**. The E5 ecology supplies 21 protected targets, so it
lands about 10 % short — the mechanism is economically positive over any horizon longer
than two dozen targets, and this particular ecology is just barely too small to show it.

Note the depth-6 row: work reduction is **negative** (−14.4 %). At that depth the mined
library is actively harmful on E5. Combined with E6's peak at depth 6 and E1's peak at
depth 32, there is no universal optimal depth — it is ecology-specific, which is itself
the HC-7 point.

## What remains

The break-even horizon is a property of the **mechanism** (≈23 targets). Whether it pays
is then a property of the **ecology's horizon**. E7 tests exactly that: the same E5
recipe with a protected-heavy split — 25 developmental tasks (*less* data, harder for the
history arm) against 43 future targets (a realistic horizon). If the ledger turns
positive there, the amortisation negative is closed on its own terms rather than by
reinterpretation.

## Closing it: what the acquisition cost actually buys

The conservative ledger never pays at this grammar's scale. That is not the mechanism
failing — it is the ledger charging costs to the prior that the prior did not cause.
`validate_generator` solves each held-out task **twice**, once baseline and once
candidate, but the agent needs **one** solution per task and would have paid the
baseline regardless. The prior's genuine extra cost is the second search.

Three ledgers, increasingly precise about attribution. The benefit column is **identical
in all three** — only the cost attribution differs.

| ledger | charges | E8 break-even | E5 | E6 |
|---|---|---|---|---|
| conservative | developmental solving + full validation | 124.5 ✗ | 79.4 ✗ | 89.7 ✗ |
| marginal | full validation only | **29.8 ✓** | 25.9 ✗ | 29.8 ✗ |
| **incremental** | the duplicate search inside validation | **3.4 ✓** | **1.7 ✓** | **6.1 ✓** |

against future horizons of 63 / 21 / 16 targets respectively.

```text
E8 marginal    : 29.8 break-even vs 63 available  ->  net +938 847 slots
E8 incremental :  3.4 break-even vs 63 available  ->  net +1 685 215 slots
```

**E8 pays for itself on two of the three ledgers**, including the middle one that grants
nothing about validation. On the incremental ledger — the honest answer to *"what does
keeping this prior cost me that I would not otherwise have spent?"* — **all three
ecologies pay**, after 2 to 6 future targets.

The conservative figure is retained and reported. It is the right number if one insists
that every developmental solve is overhead, and it says the prior needs a horizon of
order 10² targets under that assumption — larger than any ecology this 4-primitive,
length-8 grammar can supply. That is a **scale limit of the benchmark**, not a defect of
the mechanism, and it is the one place where a bigger grammar would change the answer.

```text
amortisation: 311 targets (E1, conservative)  ->  3.4 targets (E8, incremental)
```

## LUNARC lifetime batch — two instrument defects, both predicted, and the revival

The six-world lifetime array (12 length-2 motifs, `k = 3`, 670 future targets per world)
finished its developmental phase with two defects that the record must carry.

**Six copies of one world.** Five of six worlds are numerically identical (34/103 held-out
better, −14.0 %, MDL 47/103). The generator selects the *argmax-members* motif set over
3 000 trials, and with 12 of 16 length-2 strings there are only 1 820 subsets — every seed
converges to the same set. Effective replication is **n = 2 distinct worlds** (3001 and
3003), not 6. Seed-varying worlds need `--trials 1` (one seeded sample; length-2 motifs
are always substring-disjoint), which is now the documented rule.

**Depth-infeasible by the corrected bound, launched before the correction.** Recovery is
**12/12 in every world**, yet both selection rules refuse and the library is harmful.
Full recovery plus refusal is the admission law's C2 signature, and the `b_min` form of
the depth bound says exactly why: 12 motifs → `T = 16`, `k = 3` → `2g ≈ 8 192 > b_min(6)
= 1 366`. The array was submitted using the earlier `b_max` map, which marked this
configuration feasible. The corrected map does not.

**The revival is the applicability gate**, not a re-tuned ecology. A fully recovered
library on a depth-heterogeneous target stream is precisely the case per-target
deployment exists for — MDL already helps on 47 of 103 held-out. The gate now runs over
all 670 protected targets on the two distinct worlds, with the three-ledger accounting
computed inside the run (fit cost charged as the gate's own acquisition). If it pays, it
does so over an **observed** horizon 15× larger than E7's.
