# E6 — the positive against a baseline that is weak by construction

E5 left one honest weakness: `CONTINUED` beat the best history-free surface ordering by
only **+2 ladder points**, because every E5 target sat at canonical length 8 — exactly
the condition that makes a constant "guess 8" ordering strong (M2-N1). E6 removes that
condition by construction: **all targets are length 6**, so an ordering that prunes to
length 8 finds *nothing*.

## Result

```text
TERMINAL: HISTORY_INDUCED_SEARCH_PRIOR
G1 PASS (parity 0.0) · G2 PASS (0 shared) · G3 PASS · G4 PASS
```

| arm / ordering | ladder | mean `B` |
|---|---|---|
| `ORACLE_FAMILY` (calibration) | 80 | 357.0 |
| **`CONTINUED`** | **70** | **2 018.8** |
| `ORDINARY_ADAPTIVE_PARENT` | 70 | 2 018.8 |
| `ASC_baseline` (history-free) | 54 | 4 187.2 |
| `RESET` = `LIBRARY_ONLY` | 54 | 4 034.4 |
| `SHUFFLED_HISTORY` (hardened) | 48 | 8 168.8 |
| `CONST8_first` (history-free) | **16** | 69 723.2 |
| `DESC_history_free` | **16** | 84 742.2 |

The constant and descending orderings **collapse from 65 to 16**, precisely as the
design predicted. So the margin that mattered:

| | E5 | **E6** |
|---|---|---|
| `CONTINUED` − best history-free surface | +2 | **+16** |

`CONTINUED` uses **50 %** less work than `RESET` and **75 %** less than
`SHUFFLED_HISTORY`, on 16 targets with **zero** normal forms shared with history, every
one externally verified.

**The thin-margin limitation recorded in [E5_ADMISSION.md](E5_ADMISSION.md) is closed.**
The positive no longer depends on a metric where a trivial constant nearly matches it.

## The cost of closing it

E6's targets are cheap to solve (`RESET` mean `B` 4 034 against E5's 41 118), so the
absolute saving per target is small and the break-even horizon **worsens**: 1 286
targets against E5's 126.

That is a genuine trade-off, not an artifact:

| | E5 | E6 |
|---|---|---|
| surface baseline | strong (all length 8) | **weak** (all length 6) |
| saving per target | **34 283** | 2 016 |
| break-even horizon | **126** | 1 286 |

An ecology whose targets are expensive enough to make the prior economically valuable is
also, in this grammar, an ecology whose targets sit near the maximum length — where a
constant ordering is a strong baseline. Scientific control and economic value pull in
opposite directions here. Both ecologies are reported; neither is presented alone.

## Depth is the economic lever

The E6 depth sweep shows admission from depth 6 and a break-even that is itself
depth-dependent:

| depth | admitted | work reduction | break-even (marginal) |
|---|---|---|---|
| 3–4 | ✗ | 31.7 % | 695 |
| **6** | ✓ | **78.5 %** | **280** |
| 8 | ✓ | 75.4 % | 292 |
| 12 | ✓ | 64.0 % | 344 |
| 16 | ✓ | 61.8 % | 356 |
| 28 | ✓ | 74.3 % | 296 |

Full depth is **not** the economic optimum — depth 6 is, at 9 mined fragments. This is
the dose-response non-monotonicity (#323 HC-7) showing up in the ledger: accumulating
more history past the peak buys a worse prior *and* a longer payback.
