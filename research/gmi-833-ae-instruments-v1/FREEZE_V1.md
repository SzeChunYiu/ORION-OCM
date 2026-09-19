# GMI #833 Section AE instruments — four-domain real corpus, training-time measurement, hardware energy, real-dataset structure test: prospective freeze v1

Source `main`: `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`.

This freeze is committed **before** any producer, executor, oracle, test,
fixture, run artifact, receipt, theorem note or reconciliation file of this
package exists in the tree. The add-order of the blobs is the custody
evidence; this commit touches exactly one file. The prospective register
(`PROSPECTIVE_REGISTER_V1.json`) is committed second and alone; the
producers (measurement code) are committed third; every run artifact under
`REAL_RUNS/` is committed only after the producers. CI asserts this order
and runs a negative control in which a post-dated freeze must be flagged.

**Claim ceiling:**
`GMI_833_AE_INSTRUMENTS_BUILT_AND_RUN_ON_REGISTERED_REAL_CORPUS_AND_HOST`.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

The four anchor headings (verbatim, three hashes) and the sixteen rows that
the reconciliation of pull request #1054 left open as `INSTRUMENT_REQUIRED`:

> `### AE6 — Manifold hypothesis and geometric structure`

1. `- [ ] Prospectively test intrinsic-structure -> morphology transitions on synthetic and real datasets.`

> `### AE9 — Learning as representation restructuring`

2. `- [ ] For neural systems, measure representational geometry, effective rank/dimension, clustering, linear separability, invariances, circuit/path usage and information flow across training.`
3. `- [ ] Freeze prospective markers of a representation transition before observing the capability transition.`
4. `- [ ] Test whether internal transition markers predict new capability onset better than parameter count/training loss alone.`
5. `- [ ] Compare neural transition results with non-neural systems to test whether the law is architecture-general.`

> `### AE11 — Thermodynamics and physical information processing`

6. `- [ ] Measure actual energy on real hardware for selected GMI morphology transitions.`
7. `- [ ] Test whether information-theoretic savings predict physical energy savings; preserve negative results if hardware overhead dominates.`
8. `- [ ] For biological claims, separate energetic maintenance of life from cognitive information processing.`

> `### AE16 — Real-world empirical programme`

9. `- [ ] Choose real datasets/tasks spanning vision, language, sequential control and one scientific/biological domain.`
10. `- [ ] Estimate relevant structure measures without using protected outcomes to choose them.`
11. `- [ ] Freeze GMI predictions linking structure/resource regime to representation/morphology/capability.`
12. `- [ ] Compare against strong architecture-selection and information-theoretic baselines.`
13. `- [ ] Include deliberately structure-destroyed controls preserving marginal statistics where possible.`
14. `- [ ] Include structure-preserving recodings/remints.`
15. `- [ ] Test predicted crossovers as data, compute, memory, precision and energy budgets vary.`
16. `- [ ] Report failures and non-identifiability rather than post-hoc redefining `structure`.`

**No neighboring row is earned here.** In particular this tranche does not
earn any AE1, AE2, AE3, AE4, AE5, AE7, AE8, AE10, AE12, AE13, AE14, AE15 or
AE17 row of issue comment 5692689542, does not earn any other AE6, AE9,
AE11 or AE16 row than the sixteen quoted above, and does not earn any row of
the #833 issue body.

Row 8 (biological energetics) is declared **not buildable by this lane**
before any work starts: it needs indirect calorimetry or doubly labelled
water paired with a neural-activity measure on a living system. No such
instrument exists on the registered host. The row stays open with that
instrument named; nothing in this package is offered against it.

## Registered host and instrument inventory (pre-outcome)

- Host `billy` (laptop), Ubuntu 20.04, Linux `5.15.0-139-generic`, one
  socket `11th Gen Intel(R) Core(TM) i7-11800H`, 8 cores / 16 threads.
- `python3` = 3.8.10; `torch` = 2.4.1+cpu; `numpy` = 1.24.3;
  `scikit-learn` = 1.3.2 (used ONLY as the carrier of two bundled real data
  files, never for any computation); `Pillow` = 10.4.0 (used ONLY as a JPEG
  decoder).
- Energy counters: `/sys/class/powercap/intel-rapl:0/energy_uj` (domain
  `package-0`, MSR read path), `/sys/class/powercap/intel-rapl-mmio:0/energy_uj`
  (domain `package-0`, MMIO read path), `/sys/class/powercap/intel-rapl:0:0/energy_uj`
  (domain `core`). All three are root-readable only and are read with
  `sudo -n cat`; the counter range is `max_energy_range_uj = 262143328850`
  and wrap-around is handled by adding the range to a negative difference.
  No external power analyser and no NVML device exist on the host; this is
  disclosed as the instrument's limitation and is carried into every
  closing line that rests on it.
- Every producer sets `torch.set_num_threads(1)` and `torch.manual_seed`
  from the registered seeds; wall-clock and step counts are recorded as
  data, never as claims.

## Registered corpus (real, externally originated, checksum pre-registered)

Every source below is a real file that this lane did not generate. Its
sha256 was computed on the host before this freeze was written and is
pinned here; every producer re-verifies the digest at run time and refuses
to run on a mismatch. The Gutenberg texts and the UCI archive are fetched
at run time from the URLs given and must reproduce the pinned digest.

| id | domain | source | sha256 (pre-registered) |
|----|--------|--------|-------------------------|
| C1 `LANG_1342` | language | `https://www.gutenberg.org/cache/epub/1342/pg1342.txt` | `3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75` |
| C2 `LANG_84` | language | `https://www.gutenberg.org/cache/epub/84/pg84.txt` | `7810cd483cffcf2cc8a1d8f0d5807931e69d4f48cd14149b8c76f88af82fead3` |
| C3 `VISION_DIGITS` | vision | `sklearn/datasets/data/digits.csv.gz` (UCI optical recognition of handwritten digits, 1797 images of 8x8 pixels) | `09f66e6debdee2cd2b5ae59e0d6abbb73fc2b0e0185d2e1957e9ebb51e23aa22` |
| C4 `VISION_PHOTO` | vision | `/usr/share/backgrounds/brad-huchteman-stone-mountain.jpg` (a photograph shipped with Ubuntu, 3840x2560 RGB) | `a50d1261984aba099d011202a696ce641dda3120b33e5fff40036c54484335cc` |
| C5 `CONTROL_ROBOT` | sequential control | `https://archive.ics.uci.edu/static/public/194/wall+following+robot+navigation+data.zip`, member `sensor_readings_24.data` (SCITOS G5 robot, 24 ultrasound readings and the executed movement command per time step, 5456 steps in temporal order) | zip `7c1a3838be678585570fa7fa675217ee626b3aa277bb187dde627418b5e95ed2`; member `6e9728dedef8b35e31ba0be11aea85aa53bd248ab33652777df81b95a4cc8c00` |
| C6 `BIO_CANCER` | scientific/biological | `sklearn/datasets/data/breast_cancer.csv` (Wisconsin diagnostic breast cancer, 569 cases, 30 measured features) | `fed3eb72d0575ef6192293f5093c6e801b1476b577d0386bf4455504522172ed` |
| C7 `AUDIO_FC` | audio | `/usr/share/sounds/alsa/Front_Center.wav` | `0d61518bcd3f13b0c709a5298e939caf698b80d31d71d50475365ee0e5536cc9` |
| C8 `AUDIO_NOISE` | audio (low-structure real control) | `/usr/share/sounds/alsa/Noise.wav` | `0d897df3862192ea078efc1dd8fdc4f51fae9e93d3ed4c15e049829b0386729e` |
| C9 `CODE_STDLIB` | code | concatenation, in this order, of `/usr/lib/python3.8/json/__init__.py`, `decoder.py`, `encoder.py`, `scanner.py`, `/usr/lib/python3.8/ast.py`, `/usr/lib/python3.8/os.py` | member digests `41c4abb6840b6eeca85e7ea5e9b08bba71dc529725a415cc826ca940be4c79b2`, `079f7a25863c18fc9a9abc59735d684535b9deaafc08acda416997784b78e9c5`, `cdb1eb54c453f672c56caf00c02ace80c97fb48121c4af734b7c4123ceb1fb3d`, `8604d9d03786d0d509abb49e9f069337278ea988c244069ae8ca2c89acc2cb08`, `5c63117dfa24cb8df9409e82d9ce062e2b09f6198f7954b8a5ef6ca180f0cd5c`, `11a7c4ff0b2a7cfd3cf19ac7ef786b4e1bc2138ccf21afd734d4bda5352157b8` |
| C10 `LEX_WORDS` | lexicon | `/usr/share/dict/words` -> `/usr/share/dict/american-english` | `f6c94d35691b9c356f7e5072f94d23f127b168cf9b04f0f5b26e0cb1f6ef4414` |

The four domains named by row 9 are covered by real sources: vision (C3,
C4), language (C1, C2), sequential control (C5), scientific/biological (C6).
Audio, code and lexicon are additional real domains. Ubuntu's stock sound
files, Ubuntu's stock wallpaper, CPython's standard library and the system
dictionary are externally originated artifacts installed by the operating
system; the two Gutenberg texts, the UCI robot archive and the two
scikit-learn data files are externally originated public datasets.

### Registered extractors (byte stream, then bits MSB-first)

- C1, C2, C9, C10: the raw file bytes.
- C3: gunzip; drop the first line (header); for every remaining line take the
  first 64 comma-separated integers (pixel values `0..16`, raster order) as
  one byte each; the label column is dropped.
- C4: decode the JPEG with Pillow, convert to 8-bit greyscale (`"L"`), take
  the raster bytes row-major from the top-left.
- C5: for every line of `sensor_readings_24.data`, 24 comma-separated readings
  `v` in metres and a command name; emit 25 bytes per step: `min(255, floor(51 * v))`
  for each reading (a reading of exactly `5.000` maps to `255`) followed by the
  command byte `Move-Forward=0`, `Slight-Right-Turn=1`, `Sharp-Right-Turn=2`,
  `Slight-Left-Turn=3`.
- C6: drop the header line; for every case, 30 features and the label; emit
  31 bytes per case: `floor(255 * (v - min_col) / (max_col - min_col))` with the
  per-column extremes taken over the whole file (an extractor statistic that
  uses no outcome), then the label byte `0/1`.
- C7, C8: the file bytes from offset 44 onward (the PCM payload).

Bits are taken MSB-first from the byte stream. The registered stream length
is `T = 160000` bits for every dataset except C6, whose stream is shorter and
is registered at `T = 128000`. The first `3T/4` bits are the train split and
the last `T/4` bits are the protected evaluation split. No evaluation
position is used for training, for any structure measure, or for any
estimator. The sha256 of every extracted byte stream is recorded at run
time.

## Registered PRNG discipline (stdlib only)

Every random object is produced by Python's `random.Random(seed)` so that
the stdlib verifier can regenerate it exactly. Per dataset with index `c`
(C1 -> 1, ..., C10 -> 10): `seed_c = 1000 + 100 * c`.

- Mode stream: `m_t = random.Random(seed_c).getrandbits(1)` for `t = 0..T-1`
  in order; `m_t = 1` means DELAYED, `m_t = 0` means IMMEDIATE. The realized
  delayed fraction is recorded.
- Torch seeds for the two training seeds: `seed_c` and `seed_c + 7`.
- Bit-shuffle control: `random.Random(seed_c + 3).shuffle` applied to the
  list of train bits, then (same generator, continuing) to the list of
  evaluation bits.
- Byte-shuffle control: `random.Random(seed_c + 5).shuffle` applied to the
  list of train bytes, then to the list of evaluation bytes.
- Energy-ladder random weights: `torch.manual_seed(4242)`.

## Instrument I — the corpus programme (rows 9-16)

### Task family (parent-owned)

The frozen #901 delayed/immediate bit-prediction frame, carried to real
data by `gmi-833-real-transition-receipts-v1` (#903): at position `t` the
candidate sees `(x_t, m_t)`; the target is `y_t = x_t` when IMMEDIATE and
`y_t = x_{t-1}` when DELAYED (`x_{-1} = 0`). A stateless candidate cannot see
`x_{t-1}` except through what `x_t` reveals about it; a persistent candidate
can carry it.

### Structure measures (row 10) — computed on the train split only, all exact

With `c_ab = #{t in train, t >= 1 : x_{t-1} = a, x_t = b}` and `N = sum c_ab`:

- `p1 = #{t in train : x_t = 1} / |train|`.
- `E0 = 1 - (sum_b max_a c_ab) / N`: the exact delayed-mode error floor of
  the best stateless predictor (it reads `x_t`, predicts `x_{t-1}`).
- `E00 = 1 - (max_a sum_b c_ab) / N`: the same floor when only the marginal
  of `x_{t-1}` is used.
- `G = E00 - E0 >= 0`: the structure gap.
- `E_k` for `k in {1, 2, 4, 8}`: the exact next-bit error floor of the best
  predictor that reads the last `k` bits, from the `(k+1)`-gram counts on the
  train split; `DELTA_k = E_k - E_8 >= 0` for `k in {1, 2, 4}` (the locality
  gap, consumed by Instrument IV).

These are functions of the train bits alone. They are computed and
committed before any training outcome exists, and this list is not extended
after outcomes are seen.

### Candidates and training (parent-owned protocol, fixed here)

- `STATELESS-MLP`: inputs `(x_t, m_t)`, one hidden layer of width `W = 16`,
  ReLU, one logit; carried-state bytes `B = 0`.
- `PERSISTENT-GRU`: `nn.GRU(2, H)` with `H = 16` unless a ladder rung says
  otherwise, linear readout, state carried across the whole stream; carried
  state bytes `B = 4 H` (float32) or `2 H` (float16 rung).
- `CONST-0` floor witness: predicts `0` always; never eligible as winner.
- Training: Adam, learning rate `0.01`, the stream processed in chunks of
  `64` positions, `3` passes over the train split, binary cross-entropy on
  the logit, float32, one thread; two seeds per candidate; the scored error
  is the seed-pooled count `err = (wrong_seed1 + wrong_seed2) / (2 N_eval_mode)`
  as an exact rational; the seed spread is recorded.
- Evaluation errors are recorded as integer counts `(N_imm, wrong_imm,
  N_delay, wrong_delay)` per seed, and the per-position prediction bits are
  committed so that the independent route can recount them.

Let `E1` be the scored delayed-mode error of `PERSISTENT-GRU` and `E0` the
exact stateless floor above. The measured delayed-mode error of
`STATELESS-MLP` is recorded and reported against `E0` but is not a claim
input: `E0` is the exact floor and the MLP can only be worse.

### Licensed band (parent-owned, #903 amendment A4)

The law is tested on a dataset only if `1/8 < E0 < 3/8`. A dataset outside
the band is reported `OUT_OF_BAND` and counts neither for nor against any
prediction. The terminal below requires at least three in-band datasets
covering at least three of the four named domains; fewer gives
`INSUFFICIENT_IN_BAND_CORPUS` and rows 11-15 stay open.

### Prices and the frozen law (row 11)

Error price `p = 8`. Priced objective `J_c(lambda) = p * err_c + lambda * B_c`
with `lambda` per carried-state byte. Because the persistent candidate can
in principle carry `x_{t-1}` exactly, the frozen boundary uses `E1 := 0`:

`lambda* = p * E0 / B`, `lambda_low = lambda* / 2`, `lambda_high = 3 lambda* / 2`.

**P-I1 (structure -> capability).** For every in-band dataset, `E1 <= E0 / 2`:
the carried state recovers at least half of the structure-limited stateless
deficit. Falsifier: any in-band dataset with `E1 > E0 / 2`.

**P-I2 (regime transition).** For every in-band dataset the priced winner is
`PERSISTENT-GRU` at `lambda_low` and `STATELESS-MLP` at `lambda_high`, i.e. the
transition `PERSISTENT -> STATELESS` as `lambda` crosses `lambda*`. At
`lambda_low` this is equivalent to P-I1; at `lambda_high` it holds whenever
`E1 >= 0`, and that is disclosed: the empirical content of P-I2 lives in
P-I1 and in the shifted-law control. Winner ties keep both and fail the cell
closed.

**Shifted-law control.** The wrong boundary `lambda** = 2 lambda*` predicts
`PERSISTENT-GRU` at `lambda_high`; that prediction must be observed to FAIL on
every in-band dataset (the frame can be falsified on real data).

### Baselines (row 12)

Three predictors of the winner in each priced cell, scored against the
observed winner:

- `B1_GMI`: the law above (`PERSISTENT` iff `lambda < lambda*`).
- `B2_PRICE_BLIND`: standard held-out model selection that ignores the
  resource price: predicts the lower-error candidate in every cell
  (`PERSISTENT` whenever `E1 < E0`).
- `B3_MARGINAL`: the law with the structure-blind floor `E00` in place of
  `E0` (`PERSISTENT` iff `lambda < p * E00 / B`).

Cells: `lambda_low`, `lambda_high`, and, when `G >= 1/64`, the separating
price `lambda_probe = (lambda* + p * E00 / B) / 2` at which `B1_GMI` and
`B3_MARGINAL` disagree; when `G < 1/64` the probe cell is `NOT_SEPARATING`
and is not scored. Predicted scoreboard: `B1_GMI` correct in every cell of
every in-band dataset; `B2_PRICE_BLIND` wrong at `lambda_high` and at
`lambda_probe`; `B3_MARGINAL` wrong at `lambda_probe`. The scoreboard is an
exact count decided by the measured `E1`.

### Structure-destroyed controls (row 13)

- `BITSHUF`: every train bit and every evaluation bit is permuted by the
  registered shuffle; `p1` per split is preserved exactly and every temporal
  relation is destroyed. Predictions, for each in-band dataset with
  `G >= 1/64` (below that the control is `NOT_APPLICABLE` and is so
  reported): **P-I3a** `E0_shuf > E0` (the stateless floor rises toward the
  marginal floor); **P-I3b** the persistent candidate still attains
  `E1_shuf <= E0_shuf / 2` (the copy capability does not depend on the
  destroyed structure); so the stateless candidate's capability is
  structure-borne and the persistent candidate's is not.
- `BYTESHUF`: bytes are permuted, bits inside a byte keep their order.
  **P-I3c** (exact, no training): `E0 <= E0_byteshuf <= E0_bitshuf` for every
  dataset with `G >= 1/64`, ties allowed.

### Structure-preserving recodings (row 14)

- `COMPLEMENT`: every bit flipped. **P-I4a** (exact): `p1 -> 1 - p1`, and `E0`,
  `E00`, `G`, every `E_k` are exactly unchanged. **P-I4b**: for every in-band
  dataset the winner in every priced cell is unchanged and
  `E1_comp <= E0 / 2`.
- `REVERSAL`: the train split and the evaluation split are each reversed in
  time. **P-I4c** (exact, predicted from the original counts before the
  recoded stream is built): `E0_rev = 1 - (sum_a max_b c_ab) / N` (the
  transposed table), `E00_rev = 1 - (max_b sum_a c_ab) / N`. **P-I4d**: for
  every in-band dataset whose reversed stream is also in band,
  `E1_rev <= E0_rev / 2` and the winner cells match the law computed from
  `E0_rev`.

### Budget ladder (row 15)

The ladder runs on two registered datasets, `C1` and `C5`; if either is out
of band the pre-registered fallback order is `C2, C9, C10, C3, C4, C6`, taken
in that order until two in-band datasets are found.

- Memory: `H in {8, 16, 32, 64}`, `B = 4 H`. **P-I5a**: P-I1 holds at every `H`,
  and the predicted boundary scales exactly as `lambda*_H = p E0 / (4 H)`.
  **P-I5b** (cross-budget cell): at the single price `lambda_X = lambda_high(H=64)
  = 3 p E0 / 512`, the priced winner among `{STATELESS-MLP, GRU-8, GRU-16,
  GRU-32, GRU-64}` is `GRU-8`.
- Precision: the `H = 16` state is cast to float16 between chunks (`B = 32`),
  compute stays float32. **P-I5c**: `E1_fp16 <= E0 / 2`, and at the price
  `lambda_high(fp32, H=16)` the winner between `GRU-16-fp16` and
  `STATELESS-MLP` is `GRU-16-fp16` (this needs `E1_fp16 < E0 / 4`; a miss is
  reported as such).
- Data: `T_small = 40000` (train `30000`, evaluation `10000`), `H = 16`.
  **P-I5d**: P-I1 holds at `T_small`.
- Compute: one pass instead of three, `H = 16`. **P-I5e**: P-I1 holds after
  one pass.
- Energy: consumed from Instrument III — with measured per-step inference
  energies `eps_c` (excess over the idle baseline, in microjoules), the
  energy-priced objective `J_E = p * err + lambda_E * eps_c` has a crossover
  `lambda_E* = p (E0 - E1) / (eps_GRU16 - eps_MLPSEQ)` iff
  `eps_GRU16 > eps_MLPSEQ` is DETECTED by the Instrument III sign test;
  otherwise the energy budget cannot select the stateless candidate and the
  cell is reported `NO_ENERGY_CROSSOVER_DETECTED`. **P-I5f**: the crossover
  exists (this is the information-theoretic hypothesis of Instrument III at
  rung `H = 16`; its failure is a preserved negative, not an error).

### Failure reporting (row 16)

The executor emits a `failure_ledger` listing every prediction miss, every
`OUT_OF_BAND` dataset, every `NOT_APPLICABLE` control, every
`NOT_SEPARATING` cell and every `NO_ENERGY_CROSSOVER_DETECTED` cell. The
terminal is computed by the rules above regardless of how many predictions
miss; no definition in this freeze is revised after outcomes. The test
plants a miss into a copy of the artifacts and asserts that it appears in
the ledger and that the terminal is recomputed, and asserts the no-alarm
case on the committed artifacts.

Terminal for Instrument I:
`AE16_CORPUS_PROGRAMME_EXECUTED_AT_REGISTERED_SCOPE` iff at least three
in-band datasets across at least three named domains exist and every step
above ran and was scored; otherwise `INSUFFICIENT_IN_BAND_CORPUS`.

## Instrument II — training-time measurement on real neural runs (rows 2-5)

### Runs

For every in-band dataset, the `PERSISTENT-GRU` (`H = 16`, first seed) is
trained exactly as in Instrument I but with checkpoints at optimizer steps
`S = {0, 10, 20, ..., 300} U {350, 400, ..., 1000} U {1250, 1500, ..., 5500} U {last}`.
The neural control is the same training with `m_t := 0` for every position
(IMMEDIATE only, no delayed capability required), same checkpoints. The
probe is the first `2048` positions of the protected evaluation split; the
probe's `x_{t-1}`, `x_t` and `m_t` bits are committed once per dataset.

### Markers, all computed from the binarized state `b_t = [h_t > 0] in {0,1}^H` on the probe

- `CELLS`: number of distinct codes (clustering, integer).
- `LARGEST_CELL`: fraction of probe positions in the most populated code
  (exact rational).
- `CARRY`: with delayed probe positions only, `err_carry = (1/N_d) sum_codes
  min(n_code,0, n_code,1)` where `n_code,v` counts positions with that code
  and `x_{t-1} = v` (information flow from `x_{t-1}` into the state, exact
  rational; the cell-optimal decision).
- `SEP1`: `min` over units `i` and polarities of the error of predicting
  `x_{t-1}` from `b_t[i]` alone on delayed probe positions (single-unit
  linear separability, exact rational).
- `ACTIVE_UNITS`: units whose bit is not constant over the probe
  (circuit/path usage, integer).
- `GF2_RANK`: rank over GF(2) of the `N x H` code matrix (integer effective
  dimension).
- `PR_RANK`: participation ratio of the covariance eigenvalues of the real
  `h_t` over the probe (float, recorded as data; no claim reads it).
- `GEOMETRY`: mean Hamming distance between codes of delayed positions with
  `x_{t-1} = 0` and those with `x_{t-1} = 1`, minus the mean within-group
  Hamming distance (exact rational).
- `INVARIANCE`: fraction of probe positions where recomputing the cell with
  the mode input flipped (`1 - m_t`, same `h_{t-1}`) leaves `b_t` unchanged
  (exact rational).

Capability `CAP(s)` is the delayed-mode error on the probe at checkpoint `s`
(exact rational). Committed per checkpoint: the packed code matrix
(zlib-compressed, base64) so that the independent route recomputes every
marker from raw codes.

### Frozen onset rules (row 3)

- Capability onset `s_cap`: the first checkpoint `s` with `CAP(s) <= E0 / 2`
  and `CAP(s') <= E0 / 2` at the next checkpoint `s'` (two consecutive
  checkpoints, so a single fluctuation is not an onset). A run with no
  onset is `NO_ONSET`.
- Marker onset `s_M`: the first checkpoint with `SEP1 <= 3 E0 / 4`. A single
  binarized unit alone must beat three quarters of the stateless floor. The
  cell-optimal `CARRY` is NOT the marker, because `err_carry <= CAP` holds by
  construction on delayed positions and its lead would be a theorem, not a
  prediction; `CARRY` is recorded for row 2 only.
- Training-loss baseline `s_L`: the first checkpoint at which the running
  mean training loss over the last `10` optimizer steps is below `L0`, the
  loss of the optimal stateless predictor computed exactly-in-form from the
  train counts: `L0 = (1/N_train) sum_{t delayed} h(q_{x_t})` with
  `q_b = c_1b / (c_0b + c_1b)` and `h` the binary entropy in nats (a float
  threshold; the comparison yields an integer checkpoint index).
- Parameter-count baseline: constant along training, so it fires at `s = 0`
  on every run.

**P-II1 (lead-or-coincide).** On every in-band run with an onset,
`s_M <= s_cap`. Falsifier: a run with `s_M > s_cap` or with an onset but no
marker crossing.

**P-II2 (better than training loss).** `s_M < s_L` strictly on more than
half of the in-band runs that have an onset.

**P-II3 (specificity, better than parameter count).** On the neural
controls (no delayed capability required), the marker crosses `3 E0 / 4` on at
most `floor(n_ctrl / 4)` runs; the parameter-count baseline fires on every
control by construction and the loss baseline never fires on a control
because `L0 = 0` there (both facts disclosed as the baselines' own
structure). A marker crossing on a control is a false alarm and is reported.

### Non-neural comparison (row 5)

`TABULAR-PERSISTENT`: an online majority table indexed by
`(x_{t-1}, x_t, m_t)`; `TABULAR-STATELESS`: indexed by `(x_t, m_t)`. Both are
updated one chunk of `64` positions per step on the same stream in the same
order, with the same checkpoints; their representation is the context
partition, on which every marker above is computed identically (a unit is
one context bit). **P-II4**: the persistent table satisfies lead-or-coincide
(its state is `x_{t-1}` by construction, so this direction is trivial and is
disclosed as such) and reaches an onset; the stateless table has no onset
and no marker crossing; together with P-II1 and P-II3 on the neural runs the
lead-or-coincide law and the no-alarm law hold across the two registered
architecture families. The scope is exactly those two families on the
registered corpus; nothing is claimed beyond it.

Terminal for Instrument II:
`AE9_TRAINING_TIME_MARKERS_MEASURED_AT_REGISTERED_SCOPE` iff at least three
in-band neural runs exist with checkpoints, markers and controls; otherwise
`INSUFFICIENT_RUNS`.

## Instrument III — hardware energy with RAPL (rows 6-7)

### Protocol

`R = 12` rounds. In each round nine blocks run in the registered order
rotated left by the round index (round `r` starts at block `r mod 9`):

`IDLE_A` (sleep `2.0` s), `MLP_BATCH` (`2000` passes), `MLP_SEQ` (`8` passes),
`GRU8` (`4`), `GRU16` (`4`), `GRU64` (`2`), `GRU256` (`1`), `GRU1024` (`1`),
`IDLE_B` (sleep `2.0` s).

A pass is one inference over the `N = 40000` evaluation positions of the
ladder's first dataset (C1, fallback rule as in Instrument I). `MLP_BATCH`
evaluates the stateless candidate as one batched call; `MLP_SEQ` evaluates
it in chunks of `64` positions like the GRU (the overhead-matched stateless
comparator); `GRU-H` evaluates a GRU with hidden size `H` in chunks of `64`.
`MLP_*` and `GRU16` use the trained first-seed weights of the ladder dataset
(the endpoints of its real transition receipt); the other rungs use random
weights from the registered seed, since the energy of the computation does
not depend on the weight values (disclosed).

Around every block: `energy_uj` of the three registered domains before and
after, `time.perf_counter_ns()` before and after, the coretemp reading, and
the block's step count. All integers. Per round,
`P_idle = (E_A + E_B) / (t_A + t_B)` (package domain, microjoules per
nanosecond, rational) and for each workload block
`eps_c = (E_c - P_idle * t_c) / (passes_c * N)`: the excess energy per
evaluation step, an exact rational in microjoules.

### Pre-freeze instrument calibration (disclosed)

Before this freeze, eight `2.0` s idle readings of the package domain on the
loaded host gave energies between `83540863` and `123641896` microjoules
(`42` to `62` W), with the MSR and MMIO paths equal in seven readings and
differing by `57801` microjoules in one; a timing-only pilot of GRU
inference at `H in {8, 16, 32, 64}` took `0.51` to `0.64` s per `500` chunks
with no monotone trend in `H`. The host is shared with continuous-integration
runners, so background power is large and variable; that is why every
comparison below is a paired, within-round sign test and why the idle-versus-
idle null is asserted. No energy comparison between architectures was made
before this freeze.

### Predictions and decision rules

Two pre-registered hypotheses: `H_IT` (per-step energy is ordered by the
carried-state bytes `B`, so information-theoretic state savings predict
physical savings in direction) and `H_OV` (below some scale the fixed
per-step hardware overhead dominates and no ordering is detectable). Each
comparison is decided by a paired sign test over the `12` rounds; `DETECTED`
means at least `10` of `12` rounds agree (binomial tail `19/1024`... exactly
`P(X >= 10 | n = 12, 1/2) = 79/4096`).

- **D1**: `eps_GRU1024 > eps_MLP_SEQ`. Predicted DETECTED under both hypotheses.
- **D2**: `eps_GRU8 > eps_MLP_SEQ`. `H_IT` predicts DETECTED; `H_OV` predicts
  NOT DETECTED. Either outcome is recorded; a NOT DETECTED is the preserved
  negative `OVERHEAD_DOMINATED_AT_H8`.
- **D2'**: `eps_GRU16 > eps_MLP_SEQ` (the rung consumed by Instrument I's
  energy cell).
- **D3**: the full chain `eps_GRU8 < eps_GRU16 < eps_GRU64 < eps_GRU256 <
  eps_GRU1024` within a round; `H_IT` predicts DETECTED.
- **D4** (magnitude, the Landauer comparison): the carried state of `GRU-H`
  is `32 H` bits overwritten per step, so the Landauer floor per step is
  `32 H * k_B * T_nom * ln 2` with `T_nom = 300 K`, i.e. `32 H * 2.8706e-15`
  microjoules. Predicted under both hypotheses: `eps_GRU-H` exceeds the
  floor by a factor of at least `10^9` at every `H` (decided exactly as
  `10^10 * eps >= 32 * H * 28706` with `eps` in microjoules). The die
  temperature is recorded as data; the nominal `300 K` is the registered
  reference and is disclosed.
- **D5** (overhead made visible): `eps_MLP_BATCH < eps_MLP_SEQ` DETECTED and
  `eps_MLP_SEQ >= 10 * eps_MLP_BATCH` in at least `10` rounds.
- **Null**: `E_B / t_B > E_A / t_A` in `k` of `12` rounds with `2 <= k <= 10`
  (two-sided binomial band); the run fails if the null leaves the band
  (an idle-versus-idle asymmetry would mean the protocol itself is biased).
- **Read-path agreement**: `100 * |dE_msr - dE_mmio| <= dE_msr` in at least
  `103` of the `108` blocks.
- **Uncertainty statement** (row 6): the receipt carries the idle power
  range, the read-path skew range, the counter resolution observed as the
  smallest non-zero difference between consecutive reads, and the sign-test
  outcome for every comparison; a closing line for row 6 must quote them.

Row 7 closes on the *recorded* answer to D2/D2'/D3/D4 whichever way they
fall: if `H_OV` wins any rung, that negative is preserved verbatim.

Terminal for Instrument III:
`AE11_HARDWARE_ENERGY_MEASURED_AT_REGISTERED_SCOPE` iff all `12` rounds ran,
the null is in band and the read paths agree; otherwise
`ENERGY_INSTRUMENT_NOT_VALIDATED` and rows 6-7 stay open.

## Instrument IV — real-dataset intrinsic-structure test (row 1), four parts

- **Part (i)** versioned corpus checksums: the corpus table above.
- **Part (ii)** estimators. Windows `w_t = (x_{t-7}, ..., x_t)` over the
  train split, next bit `y_t = x_{t+1}`. `DIM_AFF(m)`: GF(2) affine dimension
  of the distinct windows among the first `m` windows,
  `m in {16, 64, 256, 1024, 4096, ALL}`; stated finite-sample behaviour:
  non-decreasing in `m` (asserted), `m_sat` = the first `m` at which the
  final value is reached is reported; stated failure modes: `F1` it saturates
  at `8` for any stream whose window support is affinely full, so it
  certifies low intrinsic dimension only when the support is small; `F2` it
  underestimates below `m_sat`. `SUPPORT(m) = |distinct windows| / 256`
  (graded, exact). Orbit estimator: registered group
  `G = {id, rev, comp, rev*comp}` acting on `{0,1}^8` (time reversal of the
  window, complement, both); `TV(g) = (1/2) sum_w |P(w) - P(g w)|` over the
  train windows (exact rational) against the split-half noise floor
  `TV_split` (first half of the train windows versus the second half);
  `INVARIANT(g)` iff `TV(g) <= TV_split`; failure modes: `F3` low power at
  small `m` (everything looks invariant), `F4` blindness to structure beyond
  the window. The verdict is taken at `m = ALL`.
- **Part (iii)** held-out split, budget ladder and decision rule. Classes
  (exact tables, no torch): `local1`, `local2`, `local4` (majority table on
  the last `k` bits), `shared_comp` (majority table on complement orbits,
  `128` cells), `full` (`256` cells). Training on the first `m` train windows,
  `m in {64, 256, 1024, 4096, 16384, 65536, ALL}`; per-cell ties predict `0`;
  an unseen cell predicts the train-prefix majority. Held-out accuracy is the
  exact fraction correct over every window of the protected evaluation
  split. Decision rule: at each `m` the selected class is the one with the
  lowest held-out error; ties go to the smaller class in the order
  `local1 < local2 < local4 < shared_comp < full`.
- **Part (iv)** predictions, recorded under this register:
  - **P-IV1**: `DIM_AFF(ALL) = 8` for C1, C2, C3, C4, C5, C6, C9, C10. The audio
    streams C7, C8 are registered as unknown (either value acceptable, reported).
  - **P-IV2**: `INVARIANT(comp)` is false at `m = ALL` for C1, C2, C3, C9, C10
    (their byte formats fix the top bits). Recall control: the symmetrized
    stream `C1_SYMCOMP` (train = C1 train bits followed by their complement;
    evaluation = C1 evaluation bits followed by their complement) must be
    reported `INVARIANT(comp)` true.
  - **P-IV3** (locality -> local operators, the real form of AE6-5): with
    `DELTA_4` from Instrument I, the class selected at `m = ALL` is `full` for
    every dataset with `DELTA_4 > 1/128` and is one of the local classes for
    every dataset with `DELTA_4 < 1/512`; datasets in between are `ABSTAIN`.
  - **P-IV4** (transition budget): for every dataset the class selected at
    `m = 64` is local, and along the ladder once `full` is selected it stays
    selected (at most one crossover, reported as `m_cross`).
  - **P-IV5** (symmetry -> sharing, the real form of AE6-6): on `C1_SYMCOMP`,
    `shared_comp` has held-out error no larger than `full` at `m = 64` and at
    `m = 256`; on C1 itself `shared_comp` has strictly larger held-out error
    than `full` at `m = ALL` (the matched failure on real data).

Terminal for Instrument IV:
`AE6_REAL_DATASET_TEST_EXECUTED_AT_REGISTERED_SCOPE` iff all four parts ran
on every registered dataset; row 1 closes on this terminal together with the
synthetic side already carried by `gmi-833-ae-ae6-geometric-structure-v1`,
whichever way the predictions fall, with every miss named.

## Exact-arithmetic discipline

Every quantity entering a claim is an exact `fractions.Fraction` or a Python
`int`: error counts, floors, prices, sign-test counts, checkpoint indices,
ranks, total-variation distances, held-out accuracies. Wall-clock, energy
counters and temperatures are integers read from the hardware; loss values
and `PR_RANK` are floats recorded as data and never enter a claim except
through an integer comparison index. No float appears in any claim, receipt
assertion, test assertion or hostile.

## Two materially independent routes

Route A is `ae_instruments_v1.py`; route B is
`independent_instruments_oracle_v1.py`. Route B contains no executable
import of route A (asserted by AST in the test) and recomputes every claimed
quantity from the committed raw artifacts by a different algorithm:
error counts by recounting the committed per-position prediction bits
against the regenerated evaluation targets; floors by direct enumeration of
positions instead of the count table; markers from the unpacked raw code
matrices instead of the producer's summaries; GF(2) rank by row reduction
instead of the basis-insertion method; total variation by sorting joint
keys instead of dictionary accumulation; the sign tests by explicit
cross-multiplied rational comparison; the Landauer inequality by integer
arithmetic on scaled values.

## Hostiles (pre-declared; each carries an `applicable` flag that fails the run if vacuous)

- `H_FLOOR_INFLATE`: perturbs a committed count table so `E0` rises by one
  count; the recount from raw bits must disagree.
- `H_PREDICTION_BITS`: flips committed prediction bits of one seed; the
  recount must disagree with the committed error count.
- `H_ONSET_SHIFT`: moves one checkpoint's `CAP` below `E0/2` in isolation; the
  two-consecutive rule must not move `s_cap`; moving two must.
- `H_MARKER_LAUNDER`: replaces `SEP1` by `CARRY` in a copy of the marker
  table; the lead-or-coincide check must be flagged as trivially true.
- `H_ENERGY_WRAP`: subtracts the counter range from one reading; the wrap
  handler must restore the difference.
- `H_ENERGY_NULL_BIAS`: sets every `IDLE_B` energy above `IDLE_A`; the null
  band check must fail.
- `H_SIGN_COUNT`: replaces a `10/12` outcome by `9/12`; `DETECTED` must flip.
- `H_LANDAUER_SCALE`: multiplies the Landauer floor by `10^9`; D4 must flip.
- `H_DIGEST`: alters one pinned corpus digest; the run-time binding check
  must refuse.
- `H_DIM_SATURATE`: drops one window pattern so the affine dimension falls;
  the oracle's rank must disagree with the tampered value.
- `H_SPLIT_LEAK`: computes a structure measure with one evaluation position
  included; the leakage check must fire.
- `H_POSTDATED_FREEZE` (custody negative control): a fixture repository in
  which the freeze blob postdates a result blob; the custody checker must
  report `POST_HOC_SUSPECT`.

## Nulls the true results must beat, with the no-alarm case asserted

- Instrument I: on `BITSHUF` the structure gap `G_shuf` must be strictly
  below `G` for every applicable dataset (the structure measure is not an
  artifact of the marginals); no in-band dataset may be scored a P-I1 pass
  from the `CONST-0` witness.
- Instrument II: the marker must not fire on the stateless table
  (structural null) and on at most `floor(n_ctrl / 4)` neural controls.
- Instrument III: the idle-versus-idle sign count must lie in `[2, 10]`.
- Instrument IV: `TV_split` is the noise floor; the recall control must be
  detected and the real ASCII-format streams must not be called invariant.

## Custody and misses

Predictions and decision rules are frozen here, before any producer exists.
If a measured outcome misses a frozen prediction, the miss is reported,
attributed to one stage, and a revival is frozen on new data in a
descendant package; the revealing run is never re-scored and this file is
never edited. The reconciliation states each row's outcome with its exact
numbers, including every miss.

## Parent ownership (summary; the full disclosure is `PARENT_OWNERSHIP_V1.md`)

The delayed-bit task frame, the priced objective and the boundary law are
owned by the frozen #901 law and `gmi-833-real-transition-receipts-v1`
(#903); the six exact markers by `gmi-833-ae-ae9-transition-markers-v1`;
the resource classification and the Landauer audit by
`gmi-833-ae-ae11-thermo-separation-v1`; the structure hierarchy and the
architecture derivations by `gmi-833-ae-ae6-geometric-structure-v1`; RAPL as
an energy instrument by Intel's documentation and the measurement
literature; intrinsic-dimension estimation, representational-geometry
probes, grokking and emergence analyses by their published parents. The
residual contribution of this tranche is exactly: the four instruments,
built on a registered real corpus and host with pre-registered checksums,
predictions and decision rules, and run once with every outcome recorded.

## Forbidden promotions

`INTELLIGENCE_EQUALS_COMPRESSION`, `ALL_LEARNING_IS_COMPRESSION`,
`MANIFOLD_HYPOTHESIS_UNIVERSAL`, `MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`WORLD_MODEL_ALWAYS_REQUIRED`, `FREE_ENERGY_PRINCIPLE_PROVED`,
`THERMODYNAMIC_INTELLIGENCE_LAW`, `GENERAL_REASONING_REDUCED_TO_PREDICTION`,
`COMPLETE_GMI`, `ENERGY_CLAIM_WITHOUT_HARDWARE_MEASUREMENT`,
`UNIVERSAL_ARCHITECTURE_PREDICTION`, `ARCHITECTURE_GENERALITY_BEYOND_TWO_REGISTERED_FAMILIES`,
`BIOLOGICAL_ENERGETICS_SEPARATED`, `INDEPENDENT_TEAM_REPLICATION`, `M5`.
