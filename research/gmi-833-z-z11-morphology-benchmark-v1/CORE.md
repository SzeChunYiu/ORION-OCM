# gmi-833-z-z11-morphology-benchmark-v1 — IMB-v1

Section Z (issue comment `5684819296`), subsection
`### Z11 — Intelligence Morphology Benchmark`: all nine rows.

Claim ceiling:
`GMI_833_Z11_EXACT_THEORY_PREDICTION_BENCHMARK_WITH_HIDDEN_SEEDED_ECOLOGIES_EMPIRICAL_STREAM_WORKLOADS_AND_SCORED_COMPETITOR_THEORIES_AT_REGISTERED_FINITE_TRANSDUCER_SCOPE`

## The benchmark

`519` cases in six classes, generation rules published in `FREEZE_V1.md` before
any outcome existed: `C1_LADDER` `135` (exact three-mode worlds), `C2_TWO_LEVEL_IID`
`189`, `C3_ALPHABET` `81`, `C4_EMPIRICAL_STREAM` `45` (input law = the empirical
4-bit-window law of three pinned real files), `C5_HIDDEN` `60` (drawn from a seed
whose `sha256` was committed in the freeze; preimage revealed in the executor
commit), `C6_NEGATIVE_CONTROL` `9` flat ecologies + a scrambled-truth pass;
`C7_DISCRIMINATION` derived (`517/519` cases). Every case's hidden truth —
profile, thresholds, resource frontier, class choice per price, failure modes —
is enumerated exactly; every theory is a pure function of the public
specification and must emit all five fields. Case-set `sha256`
`c8de5c75e4786e4731c19b6aad29eb282eddea8b0b6c95f1b842a57ec723619f`.

## Headline scores (exact rationals; both routes agree on every score)

| theory | class choice | thresholds | frontier | failure modes | calibration |
|---|---|---|---|---|---|
| `T_GMI_IC1` | `1` (`11380` hits, `0` misses, `155` abstains) | `1` | `1` | `1` | `CALIBRATED` |
| `T_DECLARED` | identical records, `0` disagreements | | | | `NON_DISCRIMINATING` |
| `T_HALF` (retired `ηp/2`) | `2111/2307` | `418/731` | `511/519` | `618/625` | `MISCALIBRATED` |
| `T_LEVEL` (`Z13-P1`) | `11311/11535` | `513/731` | `1` | `1` | `MISCALIBRATED` |
| `T_MDL` | `3471/11535` | abstain | abstain | `1` | |
| `T_OCCAM_HARD` | `8341/11535` | abstain | abstain | `1` | |
| `T_SRM` | `7819/11535` | abstain | `1` | `1` | |
| `T_SATISFICE` | `7320/11535` | abstain | `1` | `1` | |
| `T_ABSTAIN` | `0` hits, `0` misses | | | | |
| best of `200` nulls | `3071/11535` | `20/731` | `157/519` | `27/125` | |

Frozen predictions: `B1`, `B2`, `B4`, `B5`, `B6` HIT; `B3` MISS at the `p = 0`
boundary (`144/162`, `48/54`), published in `FAILED_PREDICTION_REGISTER_V1.json`.

Scrambled-truth control: the frozen all-cell form alarms on `8/9` clean
theories (no specificity); `FREEZE_V1_AMENDMENT_1.md` (committed before the
first run) makes the informative-cell form govern — `1536` cells, `T_GMI_IC1`
`0`, best null `9/32`, planted truth reader `1`; `T_MDL`/`T_OCCAM_HARD` false
alarms recorded and diagnosed (price-blind). `s6_instruction_followed = false`,
`audit_shape_disclosed = POST_HOC_SUSPECT` for that gate.

Named results `IMB-1`..`IMB-7` in `Z11_THEOREMS_V1.md`.

## Two materially independent routes

- **A** `imb_benchmark_v1.py` — address-signature enumeration (`2910` distinct
  signatures at `b = 2`), tally scorer, nulls seeded `1000+k`. Emits
  `CASES_V1.json`, `PREDICTIONS_V1.json`, `RESULT_V1.json`.
- **B** `independent_imb_oracle_v1.py` — rebuilds all `519` cases from the
  rules, full explicit machine enumeration at `b ≤ 1` and witness-proved `b = 2`
  floors, half-line frontier, its own scorer over `PREDICTIONS_V1.json`, its own
  `200`-null family (`500000+k`). Imports nothing from A. Emits
  `ORACLE_RESULT_V1.json`.

## Hostiles (all applicable, all detected)

`HZ1` truth reader, `HZ2` missing field, `HZ3` abstain-as-hit, `HZ4` vacuous
interval, `HZ5` tampered rule, `HZ6` wrong preimage, `HZ7` drifted blob,
`HZ8` miscalibration.

## Reproduce (from the repository root; route A takes ~10 min)

```bash
python3 -I -B research/gmi-833-z-z11-morphology-benchmark-v1/imb_benchmark_v1.py
python3 -I -B research/gmi-833-z-z11-morphology-benchmark-v1/independent_imb_oracle_v1.py
python3 -I -B research/gmi-833-z-z11-morphology-benchmark-v1/test_imb_benchmark_v1.py
python3 -I -O -B research/gmi-833-z-z11-morphology-benchmark-v1/test_imb_benchmark_v1.py
```

Workflow: `.github/workflows/gmi-833-z-z11-morphology-benchmark.yml`.
