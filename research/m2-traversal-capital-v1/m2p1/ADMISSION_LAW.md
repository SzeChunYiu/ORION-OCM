# Admission is decided by complete structure recovery

Ten independently seeded E5 worlds, each with its own hidden motif set, run through the
unmodified registered learner. Admission separates **perfectly** on one measurable
property of the mined library.

| world | motifs recovered | ranks in the token ordering | admitted |
|---|---|---|---|
| e5_2002 | **6 / 6** | 1, 2, 4, 6, 9, 15 | **True** |
| e5_2004 | **6 / 6** | 0, 4, 5, 8, 10, 12 | **True** |
| e5_2006 | **6 / 6** | 0, 4, 5, 7, 10, 14 | **True** |
| e5_2007 | **6 / 6** | 4, 5, 6, 7, 11, 13 | **True** |
| e5_2008 | **6 / 6** | 3, 5, 6, 7, 8, 9 | **True** |
| e5_2009 | **6 / 6** | 2, 5, 6, 7, 8, 11 | **True** |
| e5_2001 | 5 / 6 | 0, 6, 7, 12, 13 | False |
| e5_2003 | 5 / 6 | 2, 3, 5, 6, 9 | False |
| e5_2005 | 5 / 6 | 0, 1, 2, 6, 10 | False |
| e5_2010 | 5 / 6 | 0, 6, 7, 9, 14 | False |

```text
recovered == all motifs  <=>  admitted
```

**No exceptions in ten worlds.** Every world mined the full 16 fragments, so library
*size* is not the discriminator — library *completeness* is. A single missing motif is
enough: targets whose canonical program needs it cannot be composed from the library at
all, so the guided stream never reaches them first, they pay the 2× interleave toll, and
the universal non-inferiority rule vetoes the whole generator.

This makes admission **predictable before the gate runs**, from a property of the mined
library rather than from the outcome — which is what turns M2-P1b from "the veto is
unpredictable" into a mechanism.

## A registered prediction that was wrong, and the correction

E6 was predicted to veto **100 %** of its targets. It vetoed **0 %** and admitted from
developmental depth 6 onward. The error was in the estimate of `g`, the guided position
of a target's composition.

I had assumed `g ≈ T^k` — uniform position in the `product(tokens, repeat=k)`
enumeration over `T = |library| + 4` tokens. But `_guided_programs` builds
`tokens = method.fragments + primitives`, and `learn_generator` returns fragments
**sorted by support count descending**. High-support fragments — which under
substring-disjointness are exactly the true motifs — therefore occupy the **earliest**
token positions, and `product` enumerates their combinations **first**.

So `g` is governed by the motifs' **rank** in the token ordering, not by `T^k`. The
observed ranks above (0–15, mostly single digits) put every composition near the front
of its block. The corrected condition is:

```text
admission  <=  motifs are IN the library  AND  ranked early
```

Both follow from the learnability condition: substring-disjointness makes each motif
tie its substrings on count and win the length tiebreak, which puts it in the library
*and* high in the ranking. The `T^k` bound in
[LEARNABILITY.md](LEARNABILITY.md) is superseded as a quantitative estimate; its
qualitative use — that missing motifs raise the effective `k` — was correct and is why
E3 failed.

This also explains E6's length-6 ecology admitting at all, and it is what makes E6 the
answer to the thin-margin limitation recorded in [E5_ADMISSION.md](E5_ADMISSION.md): on
length-6 targets a constant "guess 8" ordering prunes to the wrong length and finds
**nothing**, so the surface baseline is weak by construction rather than by luck.

## Prospective confirmation on a fresh ecology (E7)

The law was fitted on ten E5 worlds. E7 tests it **prospectively**, on a differently
shaped ecology built for a different purpose (a long future horizon: 25 developmental
tasks against 43 future targets).

```text
E7:  5 / 7 motifs recovered  ->  admit = False
```

Incomplete recovery, refusal — as the law requires. Held-out result: 5/10 strictly
better, `never_worse=False`, work reduction **−0.5 %** (no effect). Motif ranks 2, 3, 5,
8, 14: the five recovered motifs *were* ranked early, so ranking was not the failure —
**coverage** was.

This is the law's first out-of-sample test and it holds.

## The constraint E7 exposes

E7 was built to close the amortisation negative by lengthening the horizon. It failed
for a reason that is structural rather than incidental:

> The developmental data needed to **recover** the structure competes with the future
> horizon over which the recovered structure **pays**.

Splitting a fixed-size ecology toward more future targets starves the developmental
phase, and below the recovery threshold the prior is not admitted at all — so the
horizon it would have paid over becomes irrelevant.

| ecology | train | future targets | recovery | admitted | marginal break-even |
|---|---|---|---|---|---|
| E5 | 35 | 21 | 6/6 | ✓ | 23.2 (horizon 10 % short) |
| E7 | 25 | 43 | **5/7** | ✗ | — (no prior to amortise) |

Resolving it requires a **larger ecology**, not a different split — enough members that
both the developmental phase and the future horizon can be large at once. That is E8:
147 members, 66 developmental tasks, 63 future targets.

## Second out-of-sample confirmation (E8)

E8 is a third ecology shape — deliberately larger (147 members) so that the
developmental phase and the future horizon can both be large, which is what E7 showed
was needed.

```text
E8:  7 / 7 motifs recovered  ->  admit = True
```

Held-out: **18/18 strictly better**, `never_worse=True`, work reduction **87.2 %**.
Motif ranks 0, 1, 4, 7, 8, 9, 10 — all in the first eleven token slots.

The law now has two independent out-of-sample confirmations in opposite directions:

| ecology | train | recovery | predicted | observed |
|---|---|---|---|---|
| E7 | 25 | 5/7 | refuse | **refuse** |
| E8 | 66 | 7/7 | admit | **admit** |

```text
recovered == all motifs  <=>  admitted
```

Twelve worlds across four ecology shapes, no exceptions.
