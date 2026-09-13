# Direct behavioural receipt — history changes pre-solution search on targets absent from history

#373 §7 asks for a signature recorded *before* the target is solved, with the guard that the
solution itself was never in the developmental history. This lane has both by construction:

- **rank_0(t)** = the enumeration index at which the history-free search proposes the eventual
  verified solution (RESET's charged position; it equals the ecology's recorded
  `baseline_first_index` on every one of 2,741 targets — assay sanity);
- **rank_H(t)** = the charged position at which the integrated controller proposes it — the
  guided-stream position on a probe hit, otherwise the interleaved or baseline position, every
  probe charged;
- **m\* ∉ history**: gate G2 guarantees no protected target's normal form is in the training or
  validation streams, and the runner raises `LEAKAGE_ALARM` if it ever is.

So `rank_H(t) < rank_0(t)` is the required `rank_H(t+1)(m*) < rank_H(t)(m*)` signature: history
moved the solution *earlier in the proposal order* of a target it had never seen, which is a
change to the cognition-generating process, not reuse of a stored answer (LIBRARY_ONLY = RESET
on every world by the same gate). `log2(rank_0 / rank_H)` is the bits of search history saved
before the proposal.

```text
worlds                         : 29   (E5-recipe ×10, lifetimes ×2 at 670 targets, fresh worlds ×8, pure-d=2 seeds ×9)
targets                        : 2,741
rank_H earlier than rank_0     : 2,536  (92.5 %)
rank_H later                   : 202   (the probe's β on a miss)
median bits of search saved    : 1.91
worlds with every target earlier: 18 / 29
```

| world | targets | rank_H earlier | later | median bits saved | min bits | median rank_H | median rank_0 |
|---|---|---|---|---|---|---|---|
| R401 | 60 | 53 | 7 | 0.79 | -0.61 | 25,913 | 52,017 |
| R402 | 60 | 60 | 0 | 1.06 | 0.00 | 29,728 | 64,869 |
| R403 | 60 | 52 | 8 | 1.51 | -0.23 | 21,218 | 57,883 |
| R404 | 60 | 47 | 13 | 1.09 | -0.40 | 21,658 | 48,920 |
| R405 | 60 | 60 | 0 | 1.88 | 0.76 | 14,942 | 58,109 |
| R406 | 60 | 56 | 4 | 1.25 | -0.13 | 21,278 | 71,114 |
| R407 | 60 | 52 | 8 | 1.16 | -0.64 | 20,518 | 58,123 |
| R408 | 60 | 53 | 7 | 1.43 | -0.48 | 19,025 | 53,550 |
| R409 | 60 | 60 | 0 | 1.74 | 1.06 | 16,126 | 64,869 |
| e5_2001 | 17 | 17 | 0 | 6.16 | 5.56 | 481 | 62,213 |
| e5_2002 | 22 | 22 | 0 | 7.10 | 5.82 | 358 | 48,994 |
| e5_2003 | 20 | 20 | 0 | 7.23 | 6.61 | 252 | 54,477 |
| e5_2004 | 20 | 20 | 0 | 7.42 | 6.67 | 334 | 66,281 |
| e5_2005 | 21 | 21 | 0 | 7.18 | 6.70 | 354 | 74,443 |
| e5_2006 | 28 | 28 | 0 | 7.52 | 6.38 | 420 | 58,397 |
| e5_2007 | 21 | 21 | 0 | 7.18 | 6.07 | 361 | 48,893 |
| e5_2008 | 26 | 26 | 0 | 7.22 | 6.54 | 426 | 74,763 |
| e5_2009 | 21 | 21 | 0 | 8.44 | 7.07 | 251 | 75,092 |
| e5_2010 | 16 | 16 | 0 | 7.64 | 6.72 | 382 | 65,288 |
| life_3001 | 670 | 575 | 93 | 0.88 | -0.48 | 1,608 | 3,970 |
| life_3003 | 669 | 615 | 53 | 1.07 | -0.26 | 1,569 | 3,976 |
| world_1001_min6 | 99 | 99 | 0 | 5.18 | 2.92 | 1,657 | 69,941 |
| world_1002_min4 | 82 | 82 | 0 | 4.27 | 0.17 | 1,722 | 48,765 |
| world_1003_min6 | 97 | 97 | 0 | 5.01 | 0.68 | 1,551 | 78,901 |
| world_1004_min4 | 82 | 79 | 3 | 4.39 | -0.98 | 1,470 | 35,545 |
| world_1005_min6 | 61 | 61 | 0 | 4.82 | 1.79 | 1,709 | 25,909 |
| world_1006_min4 | 79 | 79 | 0 | 4.35 | 1.32 | 683 | 32,709 |
| world_1007_min6 | 77 | 74 | 3 | 3.94 | -0.78 | 2,365 | 45,056 |
| world_1008_min4 | 73 | 70 | 3 | 3.24 | -1.15 | 2,263 | 24,920 |

The d = 2 seeds (R401–R409) are the hardest case — every target is ≥ 2 substitutions from every
training arrangement — and still 78–100 % of targets are proposed earlier, median 0.8–1.9 bits.
The "later" targets are the priced cost of asking: a probe miss costs β before the baseline
proposal order resumes. Record: `records/BEHAVIOURAL_RECEIPT.json`; script
`m2_behavioural_receipt.py` over the arm rows (`arm_CONTINUED_OCM.json`, `arm_RESET.json`).

**Rung.** This is the C2 signature (history-induced cognition-generation capital on genuinely
new targets). It says nothing about K2/K3 by itself; see [CLAIM_LADDER.md](CLAIM_LADDER.md).
