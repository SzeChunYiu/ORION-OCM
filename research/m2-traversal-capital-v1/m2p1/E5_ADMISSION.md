# E5 — the unmodified gate admits a history-mined generator

Both predictions registered in [LEARNABILITY.md](LEARNABILITY.md) before the run came
out true.

## Result

```text
admission : True
terminal  : HELD_OUT_SEARCH_IMPROVEMENT
```

| quantity | value |
|---|---|
| true motifs recovered by the learner | **6 / 6** |
| held-out tasks strictly better | **14 / 14** |
| `never_worse` | **True** |
| mean `B` baseline → candidate | **59 287 → 4 111** |
| work reduction | **93.1 %** |

`validate_generator` was **not modified**. Its universal non-inferiority rule, its
thresholds, `learn_generator`, `solve` and the interleaved integration mode are all the
registered units, driven as-is. What changed is the ecology, and it changed in two ways
that were *derived* from measurements rather than tuned:

1. **Learnability** — the 6 motifs are pairwise substring-disjoint, so each motif's
   support count ties its own substrings' and `learn_generator`'s `length DESC`
   tiebreak puts the motif first. Predicted 6/6 recovery; observed 6/6.
2. **Admission** — targets are length-8 normal forms composed of `k ≤ 3` motifs, so the
   guided stream reaches every target's composition within `g ≈ 8 420` steps and returns
   at `2g ≈ 16 840`, below every target's baseline index `b ≥ 21 845`. Predicted zero
   vetoes; observed zero vetoes.

## Why this is the developmental claim and not reuse

- The held-out normal forms are **disjoint from history** (gate G2), so no stored answer
  applies to any of them.
- `LIBRARY_ONLY`, which carries every solved object from history, was byte-identical to
  `RESET` on the earlier ecology — stored solutions are worth zero on new targets.
- What was retained and deployed is a **library of reusable structure**, and it makes
  targets the agent has never seen 93.1 % cheaper to solve and externally verify.

## What it does not establish

This is one ecology, one host, one seed. Fresh-world replication (10 independently
seeded E5 worlds) and the full six-arm comparison are in flight; until they land this
is a single positive, not a replicated one. The claim ceiling from
[../HIDDEN_FAMILY_DESIGN.md](../HIDDEN_FAMILY_DESIGN.md) stands unchanged: an ecology
**we authored**, so replication on someone else's ecology remains **unmet**.

The amortisation question is also still open and is tracked separately: a 93.1 %
per-target saving shortens the break-even horizon substantially, but the ledger must be
recomputed on E5 before any economic claim is made.

## Scored arms on 21 new externally verified targets

`CONTINUED` now serves a real admitted generator, so the G4 surface-ordering null is
checkable for the first time in this programme.

| arm / ordering | ladder | mean `B` |
|---|---|---|
| `ORACLE_FAMILY` (calibration) | 97 | 810.2 |
| **`CONTINUED`** (history admitted and deployed) | **67** | **6 834.6** |
| `ORDINARY_ADAPTIVE_PARENT` | 67 | 6 834.6 |
| best **history-free** surface ordering (`CONST8`/`DESC`) | 65 | 22 892.6 |
| `RESET` = `LIBRARY_ONLY` | 37 | 41 117.8 |
| `SHUFFLED_HISTORY` (hardened control) | 27 | 77 754.1 |

```text
TERMINAL: HISTORY_INDUCED_SEARCH_PRIOR
G1 PASS (parity 0.0) · G2 PASS (0 shared) · G3 PASS · G4 PASS
```

All 21 targets externally verified in every arm; `shared_normal_forms_with_history = 0`.

`CONTINUED` uses **83.4 %** less work than `RESET`, **91.2 %** less than `SHUFFLED_HISTORY`,
and **70.1 %** less than the best history-free surface ordering.

### The ladder margin is thin, and the work metric is what carries the claim

`CONTINUED` beats the best history-free surface ordering by only **2 ladder points**
(67 vs 65). That thinness is not noise — it is **M2-N1 resurfacing inside our own
positive**. E5 targets are *all* canonical length 8, which is exactly the condition
that makes a constant "guess 8" predictor strong: `CONST8_first` and `DESC` both reach
65 by skipping the 21 845 shorter programs, for free, with no history.

The ladder counts successes at five coarse budget rungs and is close to saturation
here, so it cannot separate the arms well. **Mean `B` is the finer measure and it
separates them decisively: 6 834.6 vs 22 892.6, a 70.1 % reduction.** The claim rests
on the work metric, and the ladder margin is reported as thin rather than presented as
the evidence.

A future E-variant should restore length diversity in the target stream so the constant
baseline is weak, as M2-N4 requires. That is registered as the next decisive experiment,
not quietly deferred.

## Amortisation on E5 — improved, still negative

| | E1 (world 1002) | **E5** |
|---|---|---|
| saved slots per target | 16 172 | **34 283** |
| break-even horizon, targets | 311 | **126** |
| targets available at this scope | 79 | 21 |

E5 more than doubles the per-target saving and roughly halves the break-even horizon,
but 126 required against 21 available means the ledger is **still net negative**
(−3 585 969 slots). The mechanism transfers and is now deployable; it does not yet pay
for itself at any horizon this ecology can supply. Reported as an open negative.
