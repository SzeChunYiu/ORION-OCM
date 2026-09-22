# The `F15` earned boundary — why the original sibling ecology cannot carry this row

This document is the **registered justification** for the amended ecology `F17`
of `FREEZE_V1.md` section 4. It records a measured obstruction and its
one-stage attribution. It closes no checkbox, promotes nothing, and is not a
recovery.

## The ecology it measures

`F15` is the original sibling ecology, registered and built exactly as the
sibling packages register it at `SIGMA_H05R`, `SIGMA_H06R` and `SIGMA_H08R`:
the **descriptor closure** of the sha-bound source (every prefix of length ≥ 2
of every token, 776,142 descriptors), the registered Knuth presentation key
`key(i) = (i * 2654435761) mod 2**32`, the arithmetic 7:1 slice
(`n_fit` 679,124 / `n_held` 97,018, `rank_fit` 475,386 / `rank_score` 203,738,
half 339,562), and — for this row — the hypothesis of a context `q` being the
**continuation descriptors** `p ⊒ q` of the closure, carrying evidence weight
`len(p)`.

## The measurement

Driver `h15_definitive.py` (staging; receipt
`scope_SIGMA_H15R.json`, sha256 `12dc85e2fd531c1a52b6174a8302543970c070b3f4
27f58caf328b10c5a6f410`), host of record billy-old, CPython 3.14.4, exact
integers. A 90-readout language `R` including the weighted-evidence arms
(`WSUM>=T`, `WMAX>=T`, `WAVG>=T`, `WDOM>=m`) **and** every sibling raw arm
(`CNT>=k`, `ASSOC>=k`, `EXT>=k`, `LEN<=L`, the conjunctions, the votes,
`MEM_FALLBACK`) was closed before any outcome.

Four candidate weighted-evidence labels were swept, each at its own registered
threshold: the majority-belief predicate `2*MAX > SUM` on structural weights
(`PEAK_W`), the same on content weights (`PEAK_C`), the quarter-mass predicate
`4*MAX > SUM` on content weights (`Q3_C`), and the accumulated-mass threshold
(`MASSC>=128`). Every one fails at least one registered coordinate:

| label | rank stage | held stage | one-stage attribution of the failure |
|---|---|---|---|
| `MASSC>=128` | winner `WSUM>=64`, 6,909 vs majority 85,281 | winner `WSUM>=128`, **2,366** vs majority 40,461 | **R03** class-sharing fails (rank winner ≠ held winner); **R04/R05** design null fails: the weight reassignment moves the winner only 2,366 → 4,901 (2.07× against a registered 3× bar), and the best reassigned arm (3,614) still beats the majority 40,461 |
| `Q3_C` (`4*MAXc > Wc`) | 23,013 vs majority 41,257 (need 20,628) | 13,413 vs majority 19,686 (need 9,843) | **F1** fails at all four stages. Decisive: with the store extended past the registered slice to **all 776,142 descriptors — 100% coverage** — the arm makes **4,570** errors against an F1 need of **4,041**. F1 is therefore unattainable at 100% coverage, not merely at the registered budget |
| `PEAK_W` (`2*MAXl > Wl`) | winner 5,698 vs majority 5,860 | winner 3,783 vs majority 5,864 | **F1** fails: 3,783 > 5,864 // 2 = 2,932 (and 5,698 > 2,930 at rank). The design null DOES fire here (3,783 → 15,157, 4.0×), so the failure is F1 alone |
| `PEAK_C` (`2*MAXc > Wc`) | constant arm wins (3,578) | constant arm wins (3,504) | **no signal**: the label's base rate is 0.089, the majority rule wins every stage, and every weighted arm is far worse |

The root cause is common to all four and is **one stage**: the registered
evidence weight is a **deterministic function of the descriptor** (`len(p)` is
a function of the closure position's own string; `cnt_full(p)` is a function of
the closure too), so the continuation count `C(q)` is a deterministic function
of the structural weights. Reassigning weights across the continuation entries
therefore cannot destroy the label's alignment — it merely re-thresholds a
count-of-continuations arm. Measured: the raw arms are **bit-identical** under
the registered reassignment (`CNT>=1` 23,471 → 23,471; `EXT>=2` 26,238 →
26,238; `ASSOC>=2` 19,519 → 19,519), and the weighted winner degrades by 2.07×
rather than the registered 3×.

**Consequence, stated exactly.** On the prefix-tree closure the
weighted-evidence-belief class does not separate from its own raw count arm,
and its raw count arm is the sibling's cue-association fan-out
(`CUE_ASSOCIATION_FANOUT` at `SIGMA_H06R`). There is no separate belief
mechanism for a family-blind readout language to distinguish on `F15`. This is
the boundary; the amended ecology `F17` of `FREEZE_V1.md` section 4 exists
because of it, and is registered before any measurement of `F17` exists.

## What this boundary does NOT claim

- It does not claim the row is unrecoverable in general, and it is not a
  recovery. It claims exactly what was measured: `F15` cannot carry the row.
- It does not compose with any parent or sibling certificate; the sibling
  class names are used only as descriptions of the arms measured here.
- It does not retune any registered quantity after the outcome. The four
  labels above are the registered candidate family; their thresholds are
  integers fixed by registration, not fitted.

## Ledgers

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key; the 7:1 slice and its sub-splits; the
continuation-closure hypothesis set with evidence weight `len(p)`; the
90-readout closed language; the registered winner rule; the 100%-coverage
extension reported as a boundary datum (store = all `T` descriptors, used only
to show F1 is unattainable, never as a fitted configuration).

**Dependencies.** The sibling packages' freeze forms
(`gmi-833-h-real-scale-nearest-neighbor-v1`,
`gmi-833-h-real-scale-associative-memory-v1`,
`gmi-833-h-real-scale-decision-trees-v1`) for the ledger shape, the slice
addendum architecture, the null constructions and the presentation lever. No
parent number, gate certificate or scope is imported as evidence.

**Falsifiers.** A store budget at which a weighted-evidence arm clears F1 on
`F15`; a weight reassignment under which the weighted arm degrades by more than
3× while the raw arms stay intact; a label of the registered candidate family
whose base rate exceeds `1/2` without emptying the belief content. Any one
would falsify this boundary.

**Strongest parents.** The sibling real-scale packages above for the ecology
and the ledger form; `gmi-833-h-family-requirement-ledger-v1` `HRL-1` and PR
#997 `FGS-2` for the scope rule; Knuth 1997 for the presentation lever; Salton,
Wong & Yang 1975 for the descriptor-closure vocabulary.
