# FREEZE V3 REVIVAL ADDENDUM — three misses attributed to one stage each, three levers registered before their data exist

Freeze V1: commit `dd9b34cef55ef13d144eb5a9258fbd515c55cd06` (blob
`63b98b249ccd736051a262fdd68f81a5ec7a7b80`). Register: `527f326e`.
Producers: `52383a89`, `b3825caa`, `ba494a64`. Amendment V2: `212b989b`.
This addendum is committed **alone**, after the V1 producers had run
(corpus, training, RAPL energy) and their outcomes had been scored by a draft
of route A, and **before** `producers/produce_revival_v1.py` exists and
before any V3 run artifact (`REAL_RUNS/*/train_v3.json`,
`REAL_RUNS/C11..C15/`, `REAL_RUNS/energy_v3/`) exists. `FREEZE_V1.md` and
`FREEZE_V2_AMENDMENT.md` are not edited. Every V1 prediction keeps its V1
outcome; nothing below re-scores a revealing run.

Disclosure: this file was written after the V1 outcomes were seen. Its
diagnostics on the revealing runs are `POST_HOC` and earn nothing. Its
predictions for the V3 data are prospective for that data.

## What the V1 runs showed (recorded, not re-scored)

- **Instrument I.** Every `P-I` prediction held on all nine in-band datasets
  (`C1, C2, C4, C5, C6, C7, C8, C9, C10`; `C3` is `OUT_OF_BAND`); the
  persistent candidate's delayed-mode error `E1` is exactly `0` on every
  run. `NOT_SEPARATING` and `NOT_APPLICABLE` are recorded wherever
  `G < 1/64`. `P-I5f` is `NO_ENERGY_CROSSOVER_DETECTED` (from Instrument
  III). No miss.
- **Instrument II.** `P-II1`, `P-II2`, `P-II4` hold. **`P-II3` missed**: the
  marker `SEP1 <= 3E0/4` crosses on `9` of `9` neural controls against an
  allowance of `2`; it crosses at checkpoint `0` on `8` controls (`C4` at
  `10`) and at checkpoint `0` on `6` of `9` real runs.
- **Instrument III.** The instrument validated (`12` rounds, idle-versus-idle
  null `7/12` inside `[2, 10]`, read paths agree on `107/108` blocks). `D5`
  DETECTED `12/12`. `D1` `4/12`, `D2` `3/12`, `D2'` `1/12`, `D3` `0/12`: NOT
  DETECTED, preserved verbatim as `H_OV` outcomes. `D4` is **not decidable**:
  the median excess energy per step is negative at every GRU rung.
- **Instrument IV.** `P-IV1` `8/8`, `P-IV2` `5/5` with the recall control
  detected. Misses: `P-IV3` on `C7`; `P-IV4` on `C1`, `C2`, `C10` (`full`
  selected already at `m = 64`); `P-IV5` on `C1_SYMCOMP`.

## Revival A — Instrument II, the marker's specificity

**Attribution (one stage: the marker rule).** The rule compares a
single-checkpoint, probe-measured quantity against a train-derived threshold.
A randomly initialised recurrent state already carries `x_{t-1}`: on the
committed controls the single-unit error at checkpoint `0` lies between
`0.209` and `0.475` and is below `3E0/4` on `8` of `9`; the crossing is
architectural, not learned. The training of a control then *erases* that
carry (its state collapses to `2`-`3` cells that track `x_t`, and `SEP1`
rises to about the stateless floor), while a real run drives `SEP1` to
exactly `0`. **Counterexample that maps the boundary:** the `C8` control at
optimizer step `80` has `SEP1 = 0` exactly — one binarised unit equals
`x_{t-1}` on all `2048` probe positions — in a network never given a delayed
target. A level-marker of `x_{t-1}`-separability on a recurrent architecture
therefore cannot, by any causal single-checkpoint rule, distinguish learned
delayed capability from the by-product of tracking `x_t`. This is the
structural reading; it is tested, not assumed, by the lever below.

**Lever: the marker must beat the no-capability null of its own dataset.**
Registered threshold, exact, from the committed V1 control checkpoints
(`min` over all `64` checkpoints of the control's `SEP1`, capped by `3E0/4`;
the cap never binds):

| dataset | `tau_c` | `3E0/4` (for comparison) |
|---|---|---|
| C1 | `521/2048` | `155325/479996` |
| C2 | `423/2048` | `80991/239998` |
| C4 | `417/2048` | `73341/239998` |
| C5 | `103/512` | `79275/239998` |
| C6 | `481/2048` | `58047/191998` |
| C7 | `211/2048` | `60321/239998` |
| C8 | `0` | `65475/239998` |
| C9 | `351/2048` | `75921/239998` |
| C10 | `355/2048` | `83133/239998` |

Marker onset `s_M'` := the first checkpoint with `SEP1 <= tau_c`. The
capability onset `s_cap` and the loss baseline `s_L` are the V1 rules,
unchanged.

**New data.** For every in-band dataset: one fresh `PERSISTENT-GRU` run
(`H = 16`, seed `seed_c + 13`, registered modes, V1 checkpoints, V1 probe) and
one fresh control (seed `seed_c + 13`, `m_t := 0`), produced by
`producers/produce_revival_v1.py` and recorded as `REAL_RUNS/<C>/train_v3.json`.
No V1 record is touched.

**Predictions (prospective for the V3 data).**
- **P-II1'**: `s_M' <= s_cap` on every fresh run that has an onset.
- **P-II2'**: `s_M' < s_L` strictly on more than half of the fresh runs with
  an onset.
- **P-II3'** is a two-hypothesis test, either outcome recorded: `H_R`
  (specificity recovered): fresh controls cross `tau_c` on at most
  `floor(9/4) = 2` datasets. `H_S` (the structural reading confirmed on new
  data): more than `2` fresh controls cross `tau_c`, i.e. fresh
  initialisations reproduce the carry below the committed control's own
  minimum. Under `H_S` the P-II3 negative is terminal for the neural family
  with the counterexample above, labelled EARNED-BY-COUNTEREXAMPLE, and the
  scoped positive is exactly what P-II1', P-II2' and P-II4 carry.
- The V1 rule is also re-applied to the fresh controls and the count is
  recorded (a replication of the V1 miss, not a claim).

**Diagnostic on the revealing runs (POST_HOC, earns nothing).** With `tau_c`
the marker onset on the nine V1 real runs is `30, 40, 30, 20, 20, 140, 60,
40, 30` steps for `C1, C2, C4, C5, C6, C7, C8, C9, C10` against capability
onsets `60, 60, 80, 60, 60, 180, 60, 60, 40`: lead-or-coincide on `9/9`,
none of them at checkpoint `0`.

## Revival B — Instrument III on an unloaded host

**Attribution (one stage: the measurement).** The V1 run executed with the
host's 1-minute load average between `25.9` and `29.1` (sixteen hardware
threads; other lanes' processes and CI runners resident). The idle package
power was `60.6` to `64.9` W against a single-thread workload; the paired
excess is dominated by background fluctuation and is negative for every GRU
rung (`GRU1024`: about `-520` microjoules per step). Nothing about the
workload is resolvable from package counters on a saturated host.

**Lever.** The identical V1 protocol, same host, same weights, with a
pre-registered admissibility gate: the 1-minute load average read from
`/proc/loadavg` immediately before the resolution probe and immediately after
the last round must both be `< 1.0`, and both readings are recorded in the
record `REAL_RUNS/energy_v3/rapl_rounds.json`. An inadmissible run is
recorded but **not scored**. Predictions `D1`-`D5`, the null band and the
read-path rule are the V1 ones, unchanged.

If no admissible window occurs while this lane is open, Revival B stays
registered and pending; rows 6 and 7 then report the V1 outcome (instrument
validated, `D5` detected, `D1`-`D3` preserved negatives, `D4` undecidable) and
name the unloaded-host re-run as the next step.

## Revival C — Instrument IV on five fresh real datasets

**Attributions (one stage each).**
- `P-IV3` (`C7`): the decision thresholds on `DELTA_4` (`1/128`, `1/512`) do
  not scale with the sample size. With `120000` training windows the
  held-out gain of `full` over `local4` tracks `DELTA_4` itself (`C7`: gain
  `77/39992` against `DELTA_4 = 215/119992`), so any positive locality gap
  above the `256`-cell estimation noise is exploited at `m = ALL`.
- `P-IV4` (`C1`, `C2`, `C10`): the transition budget assumed a `256`-cell
  table needs many more than `64` samples to beat a local table. On ASCII
  text the `8`-bit window fixes the byte phase, and a sparse table with
  prefix-majority fallback already wins at `64` samples (`C1`, `m = 64`:
  `full` `0.394` versus best local `0.414`). The half of `P-IV4` that says
  `full`, once selected, stays selected held on all `10` datasets.
- `P-IV5` (`C1_SYMCOMP`): the freeze specified `shared_comp` as an
  *invariant* table on complement orbits, but the complement symmetry of the
  stream acts on the target too (`y -> 1 - y`). On a stream symmetrised by
  complement every orbit cell receives `y` and `1 - y` in equal counts, the
  cell ties, and the held-out error is `1/2` up to boundary windows
  (observed `39997/79992` at `m = 64`). The specification asked an invariant
  class to exploit an *equivariant* symmetry; that is a proof, not a
  fluctuation, and is labelled EARNED-BY-COUNTEREXAMPLE.

**Levers, registered as revised predictions on fresh data.** New datasets
(`T = 160000`, seeds `1000 + 100 c`, the V1 extractors), produced by
`producers/produce_revival_v1.py` into `REAL_RUNS/C11..C15/corpus.json`,
each with its own `SYMCOMP` companion:

| id | name | domain | source (registered host) | sha256 |
|---|---|---|---|---|
| C11 `LANG_2701` | language | `https://www.gutenberg.org/cache/epub/2701/pg2701.txt` | `907420db6c4b68c70e2988cd2ad9c8cf79138667a01b63376d18dd17fef1a18b` |
| C12 `VISION_RIVER` | vision | `/usr/share/backgrounds/ryan-stone-skykomish-river.jpg` (JPEG, greyscale raster) | `0902c595631088127f1fe314f055ea9b91dc7ff3c22b24986313a4d69e66f0e5` |
| C13 `AUDIO_RL` | audio | `/usr/share/sounds/alsa/Rear_Left.wav` (payload from offset 44) | `1679e0557701864d55b742a0abd3fe5f50d95b1bfcb55ffad4b597dcc7e3c7b8` |
| C14 `CODE_STDLIB2` | code | concatenation of `/usr/lib/python3.8/typing.py`, `re.py`, `collections/__init__.py`, `argparse.py`, `inspect.py` | member digests `d05cefb32dc9b6da9a82986af83b5818ff811ed416aeebb9948d38d8dabffce5`, `4326ef93e3cf336c06523426187dce705c12f9fdc0a562a7cd00ab1739b14c2d`, `386526d59e0c4fb3198bfa17ba3dc66684f6a9b45d0a679d0bc55448cd8550e1`, `cc1e3c3a7cb538c32270a77b6f62ac7e91ff5b5a9261607ccbb3e6afe57c44f7`, `6018c433712f5906a6ba19ce9debdf48d3c0174ed2449b82e007cf466182fb40` |
| C15 `LEX_BRITISH` | lexicon | `/usr/share/dict/british-english` | `3462bd63f3a692ca0fd3c6251e2052ccda094a6a06263d84f591b1c96952d204` |

The new class `shared_comp_eq` (equivariant sharing): cell `min(w, ~w)`; the
table stores the majority of `y` for windows with `w < ~w` and of `1 - y` for
windows with `w > ~w`; the prediction is read back through the same flip.
Ties predict `0` before the flip; unseen cells predict the train-prefix
majority (unflipped), as in V1. It is computed from the committed bits by
both routes; no producer computes it.

- **P-IV1'**: `DIM_AFF(ALL) = 8` for `C11`, `C12`, `C14`, `C15`; `C13`
  registered unknown.
- **P-IV2'**: `INVARIANT(comp)` false at `m = ALL` for `C11`, `C14`, `C15`;
  true on `C11_SYMCOMP` (recall control).
- **P-IV3'** (the locality gap transfers to held-out): at `m = ALL`,
  `|gain(full over local4) - DELTA_4| <= 1/32`, and the selected class is
  `full` iff `DELTA_4 > 1/1024`, for every fresh dataset. (On the ten V1
  datasets this revised rule is consistent with every recorded outcome — the
  largest `|gain - DELTA_4|` is `C9` at about `0.025`, which is why the
  tolerance is `1/32` and not tighter; that consistency is POST_HOC and is
  reported as such.)
- **P-IV4'** (budget monotone in the locality gap): on every fresh dataset,
  once `full` is selected it stays selected; and over the fifteen datasets
  pooled, for every pair whose `DELTA_4` ratio is at least `4`, the dataset
  with the larger `DELTA_4` has `m_cross` no larger than the other's
  (`m_cross` := the first `m` on the ladder at which `full` is selected,
  `ALL` counting as the largest). (The V1 pairs satisfy this; POST_HOC.)
- **P-IV5'**: on every fresh `SYMCOMP` stream, the invariant `shared_comp`
  has held-out error within `1/1000` of `1/2` at `m = ALL` (the counterexample
  generalises), and `shared_comp_eq` has held-out error no larger than `full`
  at `m = 64` and at `m = 256`; on every fresh plain stream `shared_comp_eq`
  has error no smaller than `full` at `m = ALL` (no free lunch without the
  symmetry). (On the committed `C1_SYMCOMP` the same three inequalities are
  reported POST_HOC.)

## Instrument I — a reading of the freeze, not a change

`P-I2` says the `lambda_low` cell is *equivalent to* `P-I1` and the
`lambda_high` cell *holds whenever `E1 >= 0`*. Both sentences are true only
when the stateless candidate is priced at its exact floor `E0`
(`J_STATELESS = p E0`), which is also what "the measured delayed-mode error
of `STATELESS-MLP` ... is not a claim input" says. Route A prices the
stateless candidate at `E0` in every cell, and records the measured MLP
error and the winners it would give as data. A draft of route A that priced
the MLP at its measured error produced one `B1_NOT_PERFECT` ledger line
(`C7`, probe cell); the draft was corrected to the frozen reading before any
receipt was written, and the measured-error winners remain in the receipt.

## Terminals and rows

The V1 terminals stand as computed. Revivals A and C add `P-II1'`, `P-II2'`,
`P-II3'`, `P-IV1'` to `P-IV5'` to the receipt with their own outcomes; they
change no V1 outcome and are quoted in the reconciliation only next to the
V1 outcome they revive. Revival B is scored only if admissible.

## Custody

Committed alone; the custody checker pins this blob and asserts that no
`train_v3.json`, no `C11`-`C15` directory and no `energy_v3` directory existed
at this commit, and that `producers/produce_revival_v1.py` is first added
after it.
