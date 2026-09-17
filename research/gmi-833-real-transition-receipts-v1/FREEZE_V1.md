# GMI #833 real-system morphology transition receipts v1 — FREEZE

**Issue:** #903 (real-system validation row of #833 Section J); receipts extend `gmi-833-real-transition-protocol-v1` (PR #904).
**Claim ceiling:** `GMI_REAL_SYSTEM_TRANSITION_VALIDATION_PROTOCOL_MACHINE_CHECKABLE` at five-system scope; scientific row `Validate at least 5 transitions on real systems` is earned only if the protocol terminal is `REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE` with `>=5` qualifying distinct real-system receipts.
**Custody:** this file is the complete pre-outcome prediction artifact. It is committed and pushed BEFORE any training/evaluation run executes. Implementation (`real_transition_receipts_v1.py`, `train_real_transitions_v1.py`) and all outcome artifacts (`REAL_RUNS/`, `RECEIPTS_V1.json`, `RESULT_V1.json`) are created only in descendant commits. CI pins the freeze commit hash and asserts none of the outcome files existed at freeze.

## 1. Registered task family (real-data delayed/immediate bit prediction)

For each real system `s`, a registered REAL byte source `D_s` (real file on the execution host, sha256-recorded at run time, never synthetic) is converted to a bit stream by the registered extractor: raw file bytes, MSB-first, truncated to the first `T_s` bits.

The registered protocol mode stream is `m_t in {IMMEDIATE, DELAYED}` generated per system by `numpy.random.Generator(PCG64(seed=seed_s)).integers(0,2,size=T_s)` — the mode stream is part of the registered intervention design (like the `(p,eta,lambda)` grid), not part of the real data. The delayed-mode frequency is therefore `eta = 1/2` in expectation for every system; the realized frequency is measured and recorded.

Target rule (identical to the frozen #901 law frame):

- `IMMEDIATE`: `y_t = x_t` (visible to every candidate);
- `DELAYED`: `y_t = x_{t-1}` with `x_0 = 0` (NOT visible to any candidate except through carried state).

Split: first 80% of positions are the train stream, last 20% the protected eval stream. No eval position is used for training. Eval stream length `T_eval_s = floor(0.2 * T_s)` gives `N_delay`, `N_imm` measured counts recorded in receipts.

## 2. Candidate pools (real trainable mechanisms)

Each pool contains exactly two trained real candidates plus one analytic floor witness:

- `STATELESS-MLP`: real MLP, inputs exactly `(x_t, m_t)` (no past bits, no window; window size 0 is required so the #901 stateless-floor premise holds), one hidden layer of width `W_s` (registered), ReLU, sigmoid output. Carried state bytes `B = 0`.
- `PERSISTENT-GRU`: real GRU cell, hidden size `H_s` (registered), input `(x_t, m_t)`, carries `h` across time; linear readout. Carried state bytes `B = 4 * H_s` (float32, measured at construction from the recurrent state tensor nbytes).
- `CONST-0` (floor witness, not trained): predicts 0 always; analytic errors `1/2, 1/2`; recorded as the stateless floor witness, never eligible as winner (it is dominated by `STATELESS-MLP` whenever the MLP trains; its recorded purpose is floor verification).

Architecture/family names never enter scoring or classification: the selection and classification stages consume opaque candidate IDs with numeric tuples only.

## 3. Priced objective and frozen law (real-system form)

With registered error price `p_s > 0`, persistent-state price `lambda` (per carried-state byte), measured eval error `err_c` (fraction wrong over the whole eval stream), and carried-state bytes `B_c`:

`J_c(lambda) = p_s * err_c + lambda * B_c`.

The frozen #901 law at `eta = 1/2`: best stateless `J0 = p_s * eta / 2 = p_s/4` in expectation (immediate mode learnable to ~0, delayed mode information-theoretically `1/2` without carried state); persistent winner `J1 = lambda * B + p_s * err_GRU` with `err_GRU -> 0` when trained. Boundary:

`lambda*_s = p_s * eta_s / (2 * B_s) = p_s / (8 * H_s)`   (using `B_s = 4 H_s`, `eta = 1/2`).

Frozen intervention grid per system (identical shape to #901):

- `lambda_low = lambda*_s / 2` (prediction: `PERSISTENT_STATE` wins);
- `lambda_high = 3 lambda*_s / 2` (prediction: `STATELESS` wins).

Predicted transition for all five systems: `PERSISTENT_STATE -> STATELESS`.

Shifted-law falsifier control (as in #901): the wrong boundary `lambda** = 2 lambda*` predicts `PERSISTENT_STATE` also at `lambda_high`; the receipts must show this control prediction FAILS (observed winner at `lambda_high` is `STATELESS`), demonstrating the test can falsify a shifted phase law on real systems.

Boundary-tie control: at `lambda = lambda*_s` exactly, the law predicts a tie cell (either property admissible); boundary runs are recorded as controls and are NOT counted as transition endpoints (predictions at the tie are excluded from receipts, preserving #901 tie semantics).

## 4. Frozen classification rule (derived, blind, with abstention)

The classifier receives ONLY `(N_imm, imm_errors, N_delay, delay_errors)` of the selected candidate — no model object, no name, no family. With binomial floor `q = 1/2` and `sigma = sqrt(q(1-q)/N_delay)`:

- `PERSISTENT_STATE` iff `delay_err <= 1/2 - 3 sigma`;
- `STATELESS` iff `1/2 - 2 sigma <= delay_err <= 1/2 + 3 sigma`;
- otherwise `ABSTAIN` (`classification_identified = false`; receipt must fail).

Trainability gate (else `ABSTAIN`): `imm_err <= 1/2 - 3 sqrt(1/(4 N_imm))`.

All thresholds are the standard 2/3-sigma binomial bounds at the measured counts; no tunable constants.

Selection rule: winner = `argmin_c J_c(lambda)` over trained pool candidates with opaque IDs; ties keep both (winner set > 1 -> `classification_identified = false` for the endpoint, fail-closed).

## 5. Registered five real systems (plus one pre-registered spare)

Distictness is by (data source, pool widths, prices, seeds); `system_id` values are unique.

| id | real data source (primary) | pre-registered fallback | T_s | W_s | H_s | p_s | seed_s |
|----|----------------------------|--------------------------|-----|-----|-----|-----|--------|
| R01-gutenberg-1342 | Project Gutenberg ebook #1342 (Pride and Prejudice), UTF-8 text, downloaded at run time, sha256 recorded | `/usr/bin/git` binary bytes | 400000 | 32 | 32 | 8.0 | 101 |
| R02-alsa-frontcenter | `/usr/share/sounds/alsa/Front_Center.wav` | `/usr/bin/python3.8` | 300000 | 24 | 24 | 4.0 | 202 |
| R03-python38-binary | `/usr/bin/python3.8` | `/usr/bin/git` | 500000 | 16 | 48 | 16.0 | 303 |
| R04-dpkg-log | `/var/log/dpkg.log` | `/usr/share/sounds/alsa/Noise.wav` | 200000 | 24 | 16 | 2.0 | 404 |
| R05-stdlib-json | `/usr/lib/python3.8/json/__init__.py` + `decoder.py` + `encoder.py` + `scanner.py` (concatenated in listed order) | `/var/log/dpkg.log` | 250000 | 32 | 24 | 8.0 | 505 |
| R06-spare-git | `/usr/bin/git` (spare; used only if a primary AND its fallback both fail) | — | 400000 | 16 | 32 | 32.0 | 606 |

Training (registered, no tuning): Adam, lr `0.01`, batch = full sequence in chunks of 64 steps, epochs `E_s = 3` passes over the train stream, binary cross-entropy on the sigmoid output; per candidate two registered seeds `{seed_s, seed_s + 1000}`; the median eval error across seeds is the scored `err_c`; seed spread is recorded in the receipt. Same trained candidates serve both `lambda` settings (lambda reprices only); per-setting evaluation artifacts are emitted separately.

`lambda*_s = p_s/(8 H_s)`; e.g. R01: `8/(8*32) = 1/32`; `lambda_low = 1/64`, `lambda_high = 3/64`.

## 6. Receipts

One receipt per system conforming to `gmi-833-real-transition-protocol-v1` REQUIRED fields:

- `evidence_kind = REAL_SYSTEM`; `system_id/version/implementation_ref` = repo + commit + script path;
- `prediction_ref` = this freeze file at the freeze commit;
- `prediction_frozen_before_outcome = true` (custody-backed);
- `before_context/after_context` = `{resource_price_lambda: lambda_low/high, error_price: p_s, eta: 1/2, lambda_star, boundary:"lambda*=p*eta/(2B)"}`;
- `predicted/observed_before/after_property` from Section 3/4;
- `classification_blind_to_target_family = true` (structural);
- `resources_before/after = [B, param_count, train_seconds]` (measured);
- `run_id_before/after`, `artifact_hash_before/after` = sha256 of per-setting evaluation artifacts;
- `protected_outcome_leakage = false`; `classification_identified` per Section 4.

Extra recorded fields (not required by protocol v1): data source path + sha256 + realized `eta`, `N_imm`, `N_delay`, per-candidate errors and J values, control outcomes (shifted law, boundary tie), seeds, seed spread, library versions.

## 7. Fail-closed semantics

- Any `ABSTAIN`, any prediction/observation mismatch, any pool tie at an endpoint, or any missing measurement => that system's receipt is rejected by the protocol validator; the package reports the honest terminal.
- Fewer than 5 qualifying => `INSUFFICIENT_REAL_SYSTEM_EVIDENCE` and the #833 row stays open; no promotion language.
- If persistent candidates fail to train (delay error at floor), the prediction FAILS by observation; revival follows the operator doctrine (attribute -> lever -> re-test) as a V2 with registered lever, never by editing this freeze.

## 8. Parent ownership and forbidden promotions

Law parent: the frozen #901 exact boundary `lambda* = eta*p/2` (binary sequential morphology frame); real-system extension parent: standard supervised training of real neural mechanisms. This package does not claim stochastic switching, endogenous cost learning, universal architecture prediction, real-world migration calibration beyond these five registered systems, or complete GMI.
