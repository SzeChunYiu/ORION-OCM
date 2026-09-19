# FREEZE_V1_AMENDMENT_1 — `gmi-833-kl-revival-v1`, row L second posterior window

`FREEZE_V1.md` is **not edited**; this numbered amendment extends it. It is
committed **before** any second-window source is fetched and before any
second-window training exists (`check_freeze_order_v1.py` asserts the order).
The freeze commit remains `233bb38a504f7ba10a1a75578840c0416b2e5c0d`; the
amendment's own committer time is the start of the second window.

## 1. What the first window returned (reported verbatim, never re-scored)

Under `FREEZE_V1.md` §4.5–4.6, six posterior-dated sources (`P01`–`P06`,
`POSTERIOR_SOURCES_V1.json`, created 2026-09-19T07:25:53Z–07:41:56Z, all after
the freeze + 60 s) were admitted, all six passed `PR-1` (budgets
120, 90, 120, 120, 90, 120), and the frozen predictions scored:

| source | `p0(POS)` | `pH(POS)` | `pH(NEG)` | `EP-1` | `EP-2` | `EP-3` |
|---|---|---|---|---|---|---|
| `P01` | 11/24 | 13/24 | 0/24 | HIT | HIT | HIT |
| `P02` | 12/24 | 6/24 | 0/24 | HIT | HIT | miss |
| `P03` | 15/24 | 12/24 | 0/24 | HIT | HIT | miss |
| `P04` | 17/24 | 16/24 | 0/24 | HIT | HIT | miss |
| `P05` | 15/24 | **0/24** | 0/24 | **MISS (tie)** | HIT | miss |
| `P06` | 16/24 | 12/24 | 0/24 | HIT | HIT | miss |

`EP-1` **5/6**, `EP-2` 6/6, `EP-3` 1/6. The registered rule (§4.6 clause 3,
`k/k`) is not met: **`ROW_L` is OPEN under `FREEZE_V1.md`.** The label-
permutation null probability of a record at least this good is `7/64`, above
the registered `1/64`. Nothing in this amendment changes that disposition of
the first window.

## 2. One-stage attribution of the miss (post-outcome; `L4_DIAGNOSIS_V1.json`)

§4.6 names three candidate stages. Each was tested:

- **Custody** — `P05` passes all four `FFA-1P` clauses (revision 1375674594,
  Wikimedia sha1 equals the sha1 of the scored bytes; created 07:40:41Z).
  Not the stage.
- **Pilot** — `p0(POS) = 15/24` is interior; `PR-1` chose the smallest budget
  (90) exactly as registered. Not the stage.
- **Prediction mechanism, examined at the level the parent stated it** ("shared
  low-offset XOR structure raises the useful proposal mass"). The
  history-conditioned bodies were reproduced op-for-op and inspected before any
  proposal is trained: every one of the twelve bodies keeps 5 or 6 of its 6 ReLU
  units live on the `U` training inputs (`P05`-POS: 5 live, 0 all-zero
  activation rows, 16 distinct sign patterns — the same range as the five
  sources that hit), the `U` labels are balanced (`129/256` on the training
  window), the majority class of the evaluation window (71/128) is far below
  the criterion 112/128, and the byte structure is ordinary wikitext (407/410
  leading bits zero). **The body did not collapse and the task is not
  degenerate.**

What does separate `P05` is the parent's *graded* potential measure recorded in
every receipt, `C_pot_QH_B2` = the best evaluation score reached by any of the 24
history-conditioned proposals: **POS 103/128 versus NEG 78/128**, POS above NEG
and the only POS value below the hit criterion 112/128 in the window. `Ev_Q = pH`
is that graded quantity thresholded at 112/128 and averaged over 24 proposals;
when the POS potential lies wholly below the threshold, `pH` reads `0/24` for
both families and **the ordering is invisible to the frozen quantity although
it is present in the graded one.** Across the six window-1 sources the graded
ordering `C_pot_QH_B2(POS) > C_pot_QH_B2(NEG)` holds **6/6**
(123>79, 118>81, 123>101, 125>89, 103>78, 123>77), and on the parent's seven
in-session sources **7/7** (124>108, 121>103, 124>108, 125>90, 128>98, 122>82,
117>88). Both are **post-hoc observations, reported here, not load-bearing.**

**Attributed stage: the instrument's resolution — the hit threshold inside
`Ev_Q`, not the transfer mechanism and not the futurity custody.** The
mechanism ordered POS above NEG at `P05`; the frozen quantity could not express
it.

## 3. The lever (registered now)

Two things, both prospective:

1. **`EP-4` — developmental-potential ordering** (the parent's `C_pot`, the row
   "Formalize developmental potential separately from current capability"):
   for every admissible source, `C_pot_QH_B2(POS(D)) > C_pot_QH_B2(NEG(D))`.
   A tie is a MISS. Registered as the **mechanism-level co-prediction**; it is
   expected to hit on every source, it is scored on the second window, and it
   is **reported, not closure-bearing, for `ROW_L`** — the row is about
   evolvability `Ev_Q`, whose definition is the parent's and is not changed.
2. **A second, independent posterior window** on which `EP-1` — **unchanged**
   (`pH(POS) > pH(NEG)`, tie = MISS) — is scored at the registered strength.
   `EP-2` and `EP-3` are scored and reported exactly as in §4.3.

Nothing else moves: `G`, `PR-1`, the instrument, seeds, criterion, `N_PROP`,
`FFA-1P`, `PS-1`, both routes, hostiles `HL1`–`HL6`, and the nulls are reused
byte-for-byte. The second-window sequence ids are `T41`–`T46` (POS) and
`T51`–`T56` (NEG); the record is `POSTERIOR_SOURCES_V2.json`, the receipts
`REAL_RUNS_L5/pilot_T4*.json`, `REAL_RUNS_L5/cl5_T*.json`.

## 4. Window 2 — `PS-1` unchanged, new start

`rcstart` = **this amendment's committer time + 60 s** (read from
`git show -s --format=%cI <amendment commit>`); `k = 6`; a single pass at one
recorded `T_fetch`; candidates in ascending creation order; the same admission
test; the wrapper `run_fetch_v1.py` (repository-URL contact) runs the committed
fetcher unchanged with `--out POSTERIOR_SOURCES_V2.json`. Every window-2 source
is therefore posterior to the first window's `T_fetch` (12:08:25Z) and to every
window-1 receipt, so no window-1 outcome can have selected it.

**This is the only additional window.** No third window may be opened by this
lane whatever window 2 returns; a further attempt belongs to a new freeze.

## 5. Decision rule for `ROW_L` under this amendment

`ROW_L` closes **iff all of**:

1. `>= 6` window-2 sources pass `FFA-1P` (the checker's two-directional
   validation of §4.6 clause 1 is inherited);
2. every admitted window-2 source passes `PR-1` (exclusions reported and
   replaced only by a later-created admitted candidate, as in §4.6 clause 2);
3. **`EP-1` hits on every scored window-2 source (`k2/k2`, `k2 >= 6`)** — the
   original strength, on new material;
4. routes A and B agree on every window-2 `p0`, `pH`, `C_pot`, verdict and
   custody clause;
5. the reconciliation line **quotes the first window verbatim** (`EP-1 5/6`,
   `P05` tie at `0/24`) beside the second — the first window is never dropped,
   averaged away or re-scored.

**Nulls.** Record-level: the label-permutation probability of the combined
record is reported exactly (for `11/12` it is `13/4096`; for `12/12`, `1/4096`).
Procedure-level, disclosed: a two-window procedure that closes on `6/6` in
window 1 or on `5/6` then `6/6` has null probability
`1/64 + (6/64)(1/64) = 70/4096`, marginally above the single-window `1/64`;
this excess is stated in the receipt and the theorem note, never hidden.
`NULL_RANDOM_SIGN` (200 seeds) is run on the window-2 record and on the
combined record.

If `EP-1` misses on any window-2 source the row stays **OPEN** and is
**terminal for this lane**: the receipt reports both windows exactly, the
attribution of §2 is re-tested (does the window-2 miss also lie below the
threshold with the graded ordering intact?), and `EP-4`'s record — if it holds
on every source — is the adjacent scoped positive, labelled as a
developmental-potential result, not an evolvability closure.

## 6. Named results added by this amendment

`FP-3` (window-2 custody and `EP-1`/`EP-2`/`EP-3` scores, and the combined
two-window record) and `FP-4` (the `EP-4` developmental-potential ordering on
the parent's seven sources, window 1 and window 2, with the post-hoc /
prospective split stated per window). They join `SB-1`–`SB-3`, `FP-1`, `FP-2`.

## 7. Forbidden promotions added

`POTENTIAL_ORDERING_CLOSES_EVOLVABILITY_ROW` (`EP-4` is not `Ev_Q`),
`FIRST_WINDOW_RESCORED_OR_DROPPED`, `THIRD_WINDOW_OPENED`,
`EV_Q_DEFINITION_CHANGED`, `THRESHOLD_TUNED_TO_OUTCOME`.

## 8. Order of commits (registered now; CI asserts it)

1. **This commit**: `FREEZE_V1_AMENDMENT_1.md`, `L4_DIAGNOSIS_V1.json`,
   `diagnose_history_bodies_v1.py` only.
2. `POSTERIOR_SOURCES_V2.json` (fetched after this commit's committer time).
3. `REAL_RUNS_L5/` receipts.
4. Executor, oracle, tests, gates, receipts, notes, manifest, reconciliation.
