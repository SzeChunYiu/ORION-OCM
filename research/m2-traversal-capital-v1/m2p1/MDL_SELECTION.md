# Compression beats frequency — the root-cause fix, predicted then confirmed

[ARRANGEMENT_OBSTRUCTION.md](ARRANGEMENT_OBSTRUCTION.md) traced two separate failures to
one line of the registered learner: `learn_generator` ranks candidate fragments by
`(support count DESC, length DESC)`. A substring shared by two motifs occurs in every
occurrence of both, so its count strictly exceeds either motif's and it displaces them
from the fixed top-16.

The parent is corpus-guided library learning (**Stitch / DreamCoder**): choose the library
that best **compresses** the corpus of solutions rather than the one whose parts recur
most. Compression prices length, so a long fragment used twice can beat a short one used
five times — the distinction frequency ranking structurally cannot make.

```text
gain(f) = occurrences(f) · (len(f) − 1)      then RE-PARSE and repeat
```

Re-parsing is the part that matters: once a motif is taken, its substrings stop earning
credit for the occurrences it covers, so they no longer displace their own parents.

## Motif recovery, frequency vs MDL

| ecology | hidden motifs | frequency | **MDL** | Δ |
|---|---|---|---|---|
| E3 (16 motifs, lengths 3–4, sharing substrings) | 16 | 1/16 | **2/16** | +1 |
| **E7** (long-horizon) | 7 | 5/7 | **7/7** | **+2** |
| E5 | 6 | 6/6 | 6/6 | 0 (ceiling) |
| E8 | 7 | 7/7 | 7/7 | 0 (ceiling) |
| E6 | 4 | 4/4 | 4/4 | 0 (ceiling) |

**MDL is never worse, and improves both cases where frequency ranking actually failed.**
Three ecologies were already at ceiling, so the headline "better on 2 of 5" understates
the result — the correct denominator is the two with headroom, where MDL went 2/2.

## The registered prediction, and its confirmation

E7 is the ecology built for the long horizon (43 future targets) that **refused** under
frequency ranking, starved at 5/7 recovery. The admission law
(`recovered == all motifs ⟺ admitted`) predicted that fixing recovery would flip it.
Registered before the run, then executed:

| selection rule | library size | admission | held-out strictly better |
|---|---|---|---|
| frequency (registered learner) | 16 | **False** | 5/10 |
| **MDL (successor)** | **7** | **True** — `HELD_OUT_SEARCH_IMPROVEMENT` | **10/10** |

A **smaller** library — 7 fragments rather than 16 — admits where the larger one refused,
which is the dilution mechanism of the non-monotone dose-response seen from the other
side.

## Why this matters beyond one ecology

The same root cause was producing three separate symptoms:

1. **Non-monotone dose-response** — deeper history fills the fixed capacity with generic
   high-support fragments and the prior degrades (E8: −82.8 % at depth 20).
2. **E7's refusal** — recovery starved at 5/7 because shared substrings displaced motifs.
3. **d ≥ 2 untestable** — frequency ranking forces substring-disjointness, which caps the
   motif alphabet at `m(ℓ−1) ≤ P²`, which starves the arrangement space to zero feasible
   configurations.

Compression-based selection addresses the cause of all three. It is a **research-layer
successor rule**, reported only under the `CONTINUED_MDL` label;
`src/ocm/learning/methods.py` is not modified and the registered admission rule is not
loosened.

## Claim ceiling

Motif recovery and a single admission flip are demonstrated. **Not** yet demonstrated: the
scored arm comparison on protected targets (running), replication across seeds, or that
MDL selection actually moves `ALL_THREE` off zero in the feasibility map — that last is a
prediction, not a result.
