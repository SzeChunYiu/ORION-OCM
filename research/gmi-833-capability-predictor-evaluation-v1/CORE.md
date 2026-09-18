# gmi-833-capability-predictor-evaluation-v1

#833 Section K, second tranche: the rows that **test** the exact capability
predictor `C_hat = F(M,E,R,H,D,U)` built in `gmi-833-capability-predictor-v1`
(#1012). `F` is never modified — only its registered universe is substituted.

Claim ceiling:
`GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE`

## Custody first

Every row here is a custody claim, not only a modelling claim. Predictions were
frozen and pushed **before any outcome oracle, scorer, calibration routine, OOD
probe, real-system runner or test existed**, and `git log` proves the order:

| commit | what |
|---|---|
| `e46003d5` | `FREEZE_V1` — 3 × 51,840 predictions bound by sha256, order classes, curves, real-system protocol |
| `50451f23` | external evaluator, route B, scorer, tests, V1 real outcomes |
| `711903a1` | `FREEZE_V2_AMENDMENT` — revival predictions, before V2 training |
| `accc1aed` | V2 outcomes, `FREEZE_V3_ADDENDUM`, CI |
| `f60377bd` | `FREEZE_V4_POWER_ADDENDUM` — `SIGMA_SYN2` / `SIGMA_ARCH2`, before their outcomes were computed |

CI re-derives this order from the repository, and its gate carries a **negative
control**: it fails if a file known to be present at the freeze is not found, so
a path typo cannot make it vacuously green. That is the #976 `POST_HOC_SUSPECT`
failure class, checked rather than asserted.

## What is closed

| row | result | headline |
|---|---|---|
| held-out synthetic species | KE-1 | `SIGMA_SYN` (64 machines) and, after the power revival, `SIGMA_SYN2` (128 machines): **0 soundness violations** on 45,800 and 25,216 (input, consistent-world) pairs, of which **3,872 point emissions on `SIGMA_SYN2` are non-degenerate** (capability `4/11`, `5/11`, `9/11`); law-vs-simulation 64/64 and 128/128 |
| held-out known architectures | KE-2 | `SIGMA_ARCH` (128 machines) and `SIGMA_ARCH2` (176, adding `FF 3`, `REC 6`, `CTR 3`): **0 violations** on 121,920 and 24,912 pairs, **2,400 non-degenerate points** (`4/13`, `7/13`, `11/13`); law-vs-simulation 128/128 and 176/176; family names blind under all **24** permutations |
| predict qualitative failure | KE-4 | modes frozen per input before outcomes; confusion matrices stratified `ORDER_FREE` / `CONJUNCTIVE` / `NO_CROSSING` (19,880 / 28,304 / 3,656 on `SIGMA_SYN`), never pooled |
| predict quantitative curves | KE-5 | 8 cases × 4 thresholds × 7 universes sweeping `R.budget`; **0 replay mismatches**, per-point exact agreement |
| measure calibration error | KE-6 | exact coverage under the registered 32-pattern fault law: **0 violations** of `913/1000` and `863/1000`, minima `1191567620413/1224000000000` and `2380730729/2448000000`, each reported beside its abstention rate (`121/162`, `439/640`); inflated-fault hostile detected |
| measure OOD failure | KE-7 | OOD defined structurally; 272 out-of-universe worlds; in-universe and out-of-universe strata reported side by side, **0 in-universe violations** |

## What is left OPEN, and why

**`Test predictor on real trained systems` is not closed.** It was genuinely
attempted — 96 real torch-trained systems across three prospectively frozen
populations, 288 trained heads, CPU, one thread, registered seeds, a
sha256-pinned real source, protected splits disjoint by position. The test ran
and produced a result; the result is that the *bridge* fails.

**KE-3 (the positive):** `F` is wrong on **0 of 161,632 (input,
truthfully-registered-world) pairs** across all three real populations. That is
a real fact about `F` on real trained systems.

**KE-3D (the boundary, EARNED BY COUNTEREXAMPLE):** three registration laws were
frozen prospectively, each on a population the previous outcomes did not contain,
and all three were falsified by their own pre-registered falsifiers —
`(GRU,8,w=1)` failing parity; `(GRU,16,w=0)` missing ones-mod-3 by 19/2000 while
`(GRU,16,w=1)` hit parity exactly; `(GRU,12,·)` solving both at widths the
width-16 law forbade. Truthfulness went 19/32 → 28/32 → 26/32 — not monotone,
which is the signature of an optimization threshold rather than a missing clause.
A fourth law fitted to those counterexamples would be tuning to outcomes;
`FREEZE_V3_ADDENDUM.md` section 6 pre-registered this terminal before the V3
outcomes existed. The row stays open and is **not** closed on synthetic data.

## A power defect I found in my own instrument, and fixed

On `SIGMA_SYN` and `SIGMA_ARCH` **every** point `F` emitted was degenerate —
`UNSATISFIED` or `0`. The soundness census over those points was true but weak.
The defect is visible entirely prediction-side (a point-value census consults no
outcome oracle), the failing stage is the observation coordinate rather than `F`
— the abstentions were correct, the instrument was blunt — and the lever is a
finer registered observation `obs = (1+w, ·, h mod 4)`. `FREEZE_V4_POWER_ADDENDUM.md`
registers it on two new machine populations whose capabilities had never been
measured, and the soundness census now rests on **6,272 non-degenerate point
emissions across six distinct nonzero capability values**, not on degenerate ones.
Reporting the original census without this would have been a hollow positive.

## The load-bearing design decisions

1. **Universe injection.** A 23-name `REGISTRATION_SURFACE` is rebound; `F`'s
   code is proved unchanged in-process (sha256 over every `co_code`, before and
   after) and across runs (git blob sha). A surface with a missing or extra name
   is refused.
2. **Seven pairwise-disjoint populations** separated by one coordinate:
   `rho[3] = 0` on `SIGMA_1`, `{1,2}` on `SIGMA_SYN`, `{3,4}` on `SIGMA_ARCH`,
   `{5,6}` / `{7,8}` / `{9,10}` on the three real populations, `{11,12}` on
   `SIGMA_SYN2` and `{13,14}` on `SIGMA_ARCH2` — each backed by an exhaustive
   pairwise descriptor comparison with 0 collisions.
3. **The external evaluator never reads a registered table.** It *runs* each
   machine over the whole protected battery and compares exactly, and it scores
   an over-budget machine `UNSATISFIED` rather than deleting it — the parent's
   load-bearing decision, independently re-derived.
4. **Abstention is never scored as success.** Every hit count is reported with
   its abstention rate and the per-threshold non-degeneracy census.

## Two materially independent routes

`oracle_route_b_v1.py` imports nothing from this package or the parent. It
re-declares the populations as `frozenset`s of realization records, writes its
own simulators and its own longhand mode predicates, and reproduces the frozen
51,840-row × 18-field prediction stream **by sha256 equality on all seven
universes**:

```
SIGMA_SYN   114e2cff47481f5b…   SIGMA_ARCH  ceb9ee6d00ee5818…
SIGMA_SYN2  14b8127f1e242fc2…   SIGMA_ARCH2 e24e90d7849d716e…
SIGMA_REAL  ffeb09a3d7ad6c0e…   SIGMA_REAL2 fd015ae2e8b220f8…
SIGMA_REAL3 92ca4ab905fa73b7…
```

Seven of seven match. Route B also independently reproduces registration
truthfulness (64, 128, 128, 176, 19, 28, 26) and the soundness totals.

## Hostiles, all detected, and a null the result beats

| id | planted defect | detection |
|---|---|---|
| HE1 | complement every measured solved-set (a *scaling* of `mu` would leave a capability of 0 fixed, so the first version of this hostile was undetected and was replaced) | soundness violations appear |
| HE2 | drop the `UNSATISFIED` branch from the external evaluator | soundness violations appear |
| HE3 | prune the survivor set by resource admissibility (the parent's H4, replayed on held-out data) | pruned-predictor points become unsound |
| HE4 | an encoder that reads `ARCH_LABELS[0]` | `ast` reference audit flags it |
| HE5 | inflate every `beta` twenty-fold | calibration violations appear |
| HE6 | truncate the identified set to its first value | coverage failures appear |
| HE7 | mutate the parent blob | blob-sha mismatch |
| HE8 | a path typo in the freeze-order check | the required-file negative control fails |

`NULL_MODAL` (always emit the modal externally-measured capability) is unsound on
every point-emitting input; head to head on the inputs where `F` emits a point,
the null is wrong on all of them and `F` on none.

## Reproduce

```bash
python3 -I -B  research/gmi-833-capability-predictor-evaluation-v1/oracle_route_b_v1.py
python3 -I -B  research/gmi-833-capability-predictor-evaluation-v1/score_heldout_v1.py
python3 -I -O -B research/gmi-833-capability-predictor-evaluation-v1/score_heldout_v1.py
python3 -I -B  research/gmi-833-capability-predictor-evaluation-v1/test_capability_predictor_evaluation_v1.py -v
python3 -I -O -B research/gmi-833-capability-predictor-evaluation-v1/test_capability_predictor_evaluation_v1.py -v
```

Stdlib only, exact `Fraction`/`int` arithmetic, no floats in any claim. The real
systems were trained on laptop-billy with torch 2.4.1+cpu; CI replays only the
deterministic stage from the committed `REAL_RUNS*/` receipts and never trains.

## Not claimed

No universal capability-prediction claim; nothing beyond the registered held-out
universes; no promotion of finite exact coverage to asymptotic calibration; no
rewrite of the parent rows KP-1/KP-2/KP-3; and no claim that a truthful
registration is obtainable for arbitrary trained systems — KE-3D says the
opposite at this scope.
