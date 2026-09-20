# FREEZE_V1 — gmi-833-k-real-trained-v1 (#833 Section K row: real trained systems)

**This document and the vendored evidence it pins are committed BEFORE any
scorer, oracle, null, hostile, test or reconciliation artifact of this package
exists.** `git log --reverse` over this directory must return this commit first.

## 1. The exact row this tranche may reconcile

Section anchor: `# K. Capability theory upgrade`

```
- [ ] Test predictor on real trained systems.
```

No neighboring row is earned here (the neighbouring held-out/qualitative/
quantitative/calibration/OOD rows are already closed by
`gmi-833-capability-predictor-evaluation-v1`; the predictor build/abstention
rows by `gmi-833-capability-predictor-v1`).

## 2. Evidence chain this package completes (freeze-first, already on record)

`research/gmi-833-kl-revival-v1` (branch `research/833-revive-kl`, not merged)
executed the freeze-first real-training chain for this row:

- freeze commit `233bb38a504f7ba10a1a75578840c0416b2e5c0d` (`FREEZE_V1.md` +
  `FREEZE_ROWS_V1.json`) — before any implementation;
- commit `2f7a191e` — `SIGMA_REAL4` population + `SB-L*` set-valued bridge +
  `FROZEN_PREDICTIONS_REAL4_V1.json`: the complete 51,840-input set-valued
  emission stream bound by sha256 `0c81049d6c75062bc9a6438f0bda57558743bec53e76e0c3c3f5677e12b6a854`
  (`ND-2 = 2100` non-degenerate points, `ND-1 = 7976`, 32 machines, 22
  resolved), computed with the UNMODIFIED parent `F` at git blob
  `7f1bb6808901be2291bf575ee3178247d14d01d4`;
- commit `59f69dad` — `REAL_RUNS_V4/REAL_MEASURED_V4.json`: 32 real trained
  systems (torch 2.4.1+cpu, MLP/GRU x widths {6,48} x register {0,1} x trained
  heads {1,3,5,7}, 400 epochs, batch 256, lr 1/1000, one thread, band
  >= 99/100 on the 2000-item protected split) — **trained strictly after the
  frozen prediction stream existed**.

The branch stopped there; this package supplies the missing scoring layer:
route-A scorer, independent route-B oracle, the `NULL_RANDOM_COMMIT` null, the
`HK1..HK7` hostiles, the receipt, and the reconciliation. It trains nothing; it
re-derives, verifies and scores.

## 3. Vendored evidence (byte-exact copies, blob-pinned at source_branch)

| file in this package | source blob sha (recorded at `research/833-revive-kl`) |
|---|---|
| `heldout_universes_real4_v1.py` | `d7b821441b1d64c49ddea67474f444d2de180618` |
| `FROZEN_PREDICTIONS_REAL4_V1.json` | `41661ff7bc63bad218679110de0bc713570ea6d1` |
| `REAL_MEASURED_V4.json` | `96457f37c5a67d6c8aab1fbb8cf7a740218f839a` |

The executor verifies each vendored file's git blob sha at run time and refuses
to proceed on drift. The parent predictor is pinned at blob
`7f1bb6808901be2291bf575ee3178247d14d01d4` (re-verified in-process by
`install_universe`'s code fingerprint).

## 4. Frozen decision rule (the row closes iff ALL of these)

1. `ND-2 >= 1` on `SIGMA_REAL4` (frozen stream re-derived and sha256-matched);
2. **0 soundness violations** over every input with a nonempty survivor set,
   both contracts, where soundness is `extcap(x, b_real) in I(x)` with `b_real`
   the measured solved bits and `extcap` the parent's external definition
   (a system over budget is `UNSATISFIED`, never deleted);
3. `SB-L*` truthful on **32 of 32** machines (`b_real(i) in Adm(i)`);
4. routes A and B agree on `ND-1`, `ND-2`, the violation count and the
   truthfulness count;
5. `NULL_RANDOM_COMMIT` beaten: `SB-L*` truthful on 32/32 while **at most 2 of
   200** seeded random bridges with the same committed-cell set are truthful on
   32/32.

Any failure leaves the row OPEN with the failing clause named and the failing
stage attributed to ONE of: the commitment rule, the population design, or the
counter.

## 5. Frozen route-B protocol (independent, black-box)

Route B installs concrete worlds on the registration surface through the
parent's `install_universe` and runs the parent's `predict` end to end. For
every input with a nonempty survivor set it builds the **value-index worlds**
(world `t` gives machine `i` its `(t + idx) mod |Adm(i)|`-th admissible bit
vector, so each admissible vector of each machine appears in some world), takes
the union of the emitted identified sets, and additionally installs `3` seeded
random product worlds per input on which every emitted identified set must lie
inside route A's `I(x)`. Route B imports nothing from the route-A scorer and
recomputes `extcap`, violations and truthfulness from the receipt with its own
code.

## 6. Frozen hostiles

| id | planted defect | must be |
|---|---|---|
| `HK1` | drop the protocol clause (untrained heads free) | `ND-1` and `ND-2` must fall |
| `HK2` | count `{0}` and `{UNSATISFIED}` as `ND-2` | `ND-2` must rise |
| `HK3` | flip `MLP T1` commitment to `{SOLVED}` | truthfulness must flag `>= 1` machine |
| `HK4` | complement one machine's measured bits in the receipt | violations must appear |
| `HK5` | drop one value from route A's `I(x)` at one input | route B must report a disagreement |
| `HK7` | mutate the parent `F` blob | blob-sha mismatch refused |

## 7. Claim ceiling

```text
CAPABILITY_PREDICTOR_VALIDATED_ON_REAL_TRAINED_SYSTEMS_AT_REGISTERED_SCOPE
```

Forbidden promotions: `REAL_SCALE_FRONTIER_GENERALIZATION`,
`FULL_CAPABILITY_COVERAGE`, `M5`, `PREDICTOR_RETRAINED_OR_FITTED`,
`REAL_TRAINING_OUTCOMES_GENERALISE_BEYOND_THE_PINNED_SOURCE`, `COMPLETE_GMI`.
The scope is the 32-machine `SIGMA_REAL4` population, the pinned `argparse.py`
byte source, and the registered 99/100 exact-accuracy band.
