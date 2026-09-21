# Named results — `gmi-833-kl-revival-v1` (issue #833, body rows K and L)

Claim ceiling
`GMI_833_KL_REVIVAL_SET_VALUED_BRIDGE_AND_POSTERIOR_DATED_FUTURITY_AT_REGISTERED_FINITE_SCOPE`.
`source_main = f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`, freeze
`233bb38a504f7ba10a1a75578840c0416b2e5c0d` (2026-09-19T07:16:31Z), amendment 1
`65d0025765fef14d423d4e98e0194d23922c0b3d` (2026-09-19T12:25:23Z).

Every result below is an exact statement about named frozen artifacts, with
`Fraction`/`int` arithmetic and two materially independent routes
(`kl_revival_v1.py`, structural; `oracle_route_b_v1.py`, black-box worlds
installed on the parent's registration surface). **None asserts that any GMI
theorem is true.** `F`, the registration protocol, the 99/100 band, the
continual-learning instrument, `Ev_Q`, `C_pot`, `CL3-P8` and `FFA-1` are
parent-owned and unchanged.

---

## SB-1 — set-valued emission semantics and the derived bridge `SB-L*`

**Scope.** The parent predictor `F` on the registered population `SIGMA_REAL4`
(32 machines: `mech ∈ {MLP, GRU}`, widths `{6, 48}`, `w ∈ {0,1}`,
`h ∈ {1,3,5,7}`; descriptor `rho[3] ∈ {15,16}`, disjoint from every registered
population by the parent's exhaustive certificate), grid of 51,840 inputs.

**Statement.** (i) The commitment rule `CR-1` of `FREEZE_V1.md` §3.3, applied
mechanically to the parent's three real receipts `REAL_MEASURED_V1/V2/V3.json`,
returns exactly the frozen table: untrained heads `{UNSOLVED}` (72/72 below the
band, max `909/1000`), `T0` trained `{SOLVED}` (24/24), `MLP T1` and `MLP T2`
trained `{UNSOLVED}` (12/12 each, max `81/125` and `769/1000`), `GRU T1`
trained `{SOLVED}` for `size >= 12` (`s*_1 = 12`) and abstain below,
`GRU T2` abstain at every width (`s*_2` undefined). Both routes derive it with
different code; CI asserts equality. (ii) On `SIGMA_REAL4` the bridge commits
**84** `(machine, head)` cells, resolves **22** of 32 machines to a single
admissible bit vector and abstains on 10 (every `GRU` machine with `T1` at
width 6 or `T2` trained). (iii) For every input `x` with `S(x) ≠ ∅` the
set-valued emission `I(x)` of §3.5 equals the union over all admissible
product worlds of `F`'s identified sets: route B installs the value-index
worlds (one per admissible bit vector of each machine), runs `predict` end to
end and takes the union; the resulting per-input stream, written in route A's
frozen format, has sha256
`0c81049d6c75062bc9a6438f0bda57558743bec53e76e0c3c3f5677e12b6a854` — equal
to route A's and to the stream frozen before training. Eight seeded random
product worlds emit **0** identified values outside the union over
**161,664** checked emissions.

**Quantifiers.** All 51,840 inputs, both contracts, all 32 machines; every
admissible world of `SB-L*`.

**Assumptions.** The parent's `survivor_mask` is world-independent (it never
reads `CAP`) — the property the parent lane proved and this package relies on;
the band is the parent's `99/100`; `MU_REAL = (8/17, 6/17, 3/17)`.

**Falsifiers.** A derived table differing from §3.3; any input whose black-box
union differs from route A's `I(x)`; any random-world emission outside the
union; `F`'s code fingerprint changing under `install_universe` (checked
in-process, `parent_code_unchanged = true`, blob `7f1bb680…`).

**Strongest parents.** `gmi-833-capability-predictor-v1` (`F`, KP-1A image
exactness, `U-1a FeasibleSet`); `gmi-833-capability-predictor-evaluation-v1`
(`install_universe`, receipts); `gmi-833-body-residual-akl-v1` (`CB-PROTO`,
world-installation route). Form parents: set-valued prediction with a reject
option (Chow 1970; Vovk–Gammerman–Shafer 2005).

**Forbidden extrapolations.** `SB-L*` is not a fourth registration law
(`FOURTH_REGISTRATION_LAW`), not a claim that any point law is true, and not
a bridge for any population other than `SIGMA_REAL4`.

---

## SB-2 — the `SIGMA_REAL4` census: `ND-1`, `ND-2`, positive controls, null

**Scope.** As SB-1; the frozen stream `FROZEN_PREDICTIONS_REAL4_V1.json`
(commit `2f7a191e`, 2026-09-19T07:20:43Z), committed **before** the training
receipt `REAL_MEASURED_V4.json` (commit `59f69dad`, 07:35:53Z).

**Statement.** Of 51,840 inputs, **31,632** are `INCONSISTENT` (empty survivor
set, as under `F`), **8,744** emit a point and **11,464** a set (sizes
2: 6,312; 3: 864; 4: 4,136; 5: 152). **`ND-2 = 2,100`** non-degenerate
world-invariant points, every one of value `8/17`; **`ND-1 = 7,976`**
informative sets (strictly inside the `CB-PROTO` image and containing a
positive value); 6,644 degenerate points (`{0}` or `{UNSATISFIED}`). Positive
controls: the parent's V3 point law installed as a bridge gives **`ND-2` =
3,376 > 2,100** (`PK-1`); `CB-PROTO` gives **`ND-1 = ND-2 = 0`** (`PK-2`, the
parent lane's theorem re-derived on a fourth population). Hostiles: dropping
the protocol clause drives `ND-2` to **0** and `ND-1` to 3,004 (`HK1`);
counting degenerate points raises `ND-2` to 8,744 (`HK2`); one value dropped
from route A's `I(x)` at input 6,552 changes the stream sha and route B
reports the disagreement (`HK5`). The random-commitment null (200 seeded
bridges with the same 84 committed cells, bands drawn uniformly) yields `ND-2`
between 0 and 1,936.

**Quantifiers.** Every input; every value in every emitted set.

**Assumptions.** `ND-2`'s degeneracy standard is the parent's (`{0}` and
`{UNSATISFIED}` are degenerate); `ND-1` is measured against `CB-PROTO` at the
same input.

**Falsifiers.** `PK-1 <= 2,100`; `PK-2 ≠ 0`; a recomputed stream sha differing
from the frozen one; either route's census differing in any field.

**Strongest parents.** `gmi-833-body-residual-akl-v1` `BR-1`/`BR-2` (the 0 of
155,520 under truthful-by-construction bridges — the quantity this census
revives); `gmi-833-capability-predictor-evaluation-v1` `KE-1`/`KE-2` (the
non-degenerate point counter).

**Forbidden extrapolations.** 2,100 is a count on one frozen grid, not a rate,
a coverage probability, or a statement about any other population
(`PREDICTOR_TESTED_BEYOND_SIGMA_REAL4`).

---

## SB-3 — real-system soundness and truthfulness on `SIGMA_REAL4`

**Scope.** The 32 systems of `REAL_MEASURED_V4.json` (torch 2.4.1+cpu, one
thread, the parent's protocol byte-for-byte: `argparse.py` bits, word length
12, windows (0,6000)/(6000,8000), Adam `1/1000`, 400 epochs, batch 256, seeds
`8317 + 101·mech + 17·size + 3·w + task`), solved iff exact protected-split
accuracy `>= 99/100`.

**Statement.** (i) **Truthfulness 32/32**: every measured solved-bit vector lies
in its machine's admissible set — including the eight width-48 `MLP` machines
(measured bits `1`, `T1` max `1213/2000`, `T2` max `773/1000`) and the eight
width-48 `GRU` machines (every trained head solved: `T1` `1`, `T2` `124/125`
and `497/500`), the two extrapolations the freeze named as the genuine risk;
no committed cell is falsified. (ii) **Soundness 0 violations over 131,136**
(input, survivor) pairs: at every consistent input the externally evaluated
real capability of every survivor lies in `I(x)`. (iii) The V3 point law, more
resolved (`PK-1`), is truthful on only **28/32** and violates soundness on
**8,880** pairs at 4,832 inputs (first at input 15,264: `extcap = 11/17`,
image `{8/17}`); `CB-PROTO` is truthful on 32/32 with `ND-2 = 0`. (iv) The
random-commitment null: **0 of 200** bridges truthful on 32/32; the best
reaches 11/32 (histogram peak 6/32). Hostiles: flipping `MLP T1` to `{SOLVED}`
flags **8** machines (`HK3`, applicable: 8 `MLP` machines with `T1` trained
measure UNSOLVED); complementing the first admissible survivor at an `ND-1`
input (`MLP|6|0|1`) produces **11,220** violating pairs (`HK4`); a mutated
parent blob is refused by the same check the true blob passes (`HK7`); the
freeze-order gate with its negative control neutralised exits 1 (`HK6`).

**Quantifiers.** All 32 machines; all 131,136 (input, survivor) pairs; both
contracts.

**Assumptions.** The training receipt is what it says (source sha256 verified
in-run; untrained heads 24/24 below the band, max `1273/2000`); `extcap` is
the parent's external definition.

**Falsifiers.** Any machine outside `Adm`; any pair with `extcap ∉ I(x)`; a null
seed truthful on 32/32 beyond the registered 2.

**Strongest parents.** `gmi-833-capability-predictor-evaluation-v1`
(`REAL_MEASURED_V1/V2/V3`, `FREEZE_V3_ADDENDUM` §6 terminal — taken as a
premise: exact-band solvability is not a function of the structural
coordinates, so the bridge commits only where the receipts never disagreed).

**Forbidden extrapolations.** `BRIDGE_TRUTHFUL_IN_GENERAL`,
`CAPABILITY_PREDICTION_SOLVED`, `F_IS_DEFECTIVE`, `KE_3_INVALIDATED`,
`REVEALING_SET_RESCORED` (`SIGMA_REAL`/`REAL2`/`REAL3` carry no part of this
result), `SECTION_K_COMPLETE`. Truthfulness on 32 machines at two widths is
the registered scope, not a law.

**Disposition of `ROW_K`.** All five clauses of `FREEZE_V1.md` §3.6 hold and
both routes agree on `ND-1`, `ND-2`, the violation count and the truthfulness
count: **the row closes** at this scope.

---

## FP-1 — posterior custody: `FFA-1P` verdicts with their attestations

**Scope.** Window 1: `POSTERIOR_SOURCES_V1.json`, fetched once at
2026-09-19T12:08:25Z by `PS-1` from `rcstart = 07:17:31Z` (freeze + 60 s);
window 2: `POSTERIOR_SOURCES_V2.json`, fetched once by the same rule from
`rcstart` = amendment 1 + 60 s (12:26:23Z).

**Statement (window 1).** 117 mainspace page creations lay in the window at
`T_fetch`; the first seven in creation order were examined; one was skipped by
size (1,205 < 2,000 bytes) and **six admitted** (`P01`–`P06`, revisions
1375672761–1375674663, created 07:25:53Z–07:41:56Z, 2,939–15,113 bytes). For
each, Wikimedia's own revision `sha1` equals the sha1 of the scored bytes
(clause 4), the creation timestamp is later than the freeze + 60 s (clause 2),
the sha256 of the bytes matches no blob of the freeze tree and — checked on the
host holding the bytes — the bytes' git blob object is absent from the whole
repository object store (clause 3); every recorded verdict is replayed from the
recorded fields by both routes, in ascending creation order, stopping at
`k = 6` (`PS-1` replay, 9/9 checks). **Custody 6/6.** The checker admits a
planted posterior candidate and rejects `HL1` (pre-freeze timestamp, clause 2),
`HL1b` (inside the 60 s guard), `HL2` (`FREEZE_V1.md`'s own bytes, clause 3),
`HL3` (outside hash mismatch, clause 4), the parent lane's five repository
blobs and its in-session candidate; a later commit read as the freeze (`HL6`)
rejects all six real sources at clause 2.

**Quantifiers.** Every admitted source; every clause; both routes (string-
compared ISO timestamps and a size-prefiltered `ls-tree`/`show` query on
route B).

**Assumptions.** Wikimedia's revision record is an attestation service (its
timestamp and content hash), not endorsed content
(`WIKIPEDIA_CONTENT_ENDORSED` forbidden). The full bytes are kept
off-repository, as the parent did; the committed record carries ids,
timestamps, both hashes, lengths and 80-byte prefixes.

**Falsifiers.** An admitted source with a non-posterior timestamp, a mismatched
outside hash, or a sha256 among the anchor tree's blobs; a recorded verdict the
replay cannot reproduce.

**Strongest parents.** `gmi-833-body-residual-akl-v1` `FFA-1`/`FC-2` (every
repository blob is endogenous; futurity cannot be constructed in-session — the
theorem this package's lever answers by provenance); Nosek et al. 2018
(time-stamped pre-registration).

**Forbidden extrapolations.** `FUTURE_TASK_FAMILY_CONSTRUCTED`,
`OUT_OF_SAMPLE_EQUALS_FUTURE` — the sources are posterior and exogenous; that
is all custody asserts.

---

## FP-2 — `EP-1`/`EP-2`/`EP-3` on the first posterior window

**Scope.** The six admitted window-1 families under the parent instrument
(`train_continual_v4.py` = `train_continual_v3.py` with the source table and
the explicit pilot rule `PR-1`; `NFEAT 16`, `WIDTH 6`, `T_TRAIN/T_EVAL
512/128`, criterion 112/128, `N_PROP 24`, `SEQ_STEPS 120`), predictions frozen
at the freeze commit.

**Statement.** `PR-1` chose budgets 120, 90, 120, 120, 90, 120 (all interior;
0 exclusions). `pH(POS)` = 13, 6, 12, 16, **0**, 12 of 24; `pH(NEG)` = 0 on
all six; `p0(POS)` = 11, 12, 15, 17, 15, 16. **`EP-1` 5/6** (the miss is `P05`,
a tie at 0/24); **`EP-2` 6/6**; **`EP-3` 1/6** (frozen as expected-unreliable;
the parent hit 3/7). Under `FREEZE_V1.md` §4.6 the registered `k/k` is not met:
**`ROW_L` stays OPEN on window 1**; the exact label-permutation probability of
a record at least this good is `7/64`. Hostiles: swapping the POS/NEG history
score lists flips `EP-1` to MISS (`HL4`); equal lists score a MISS with the tie
flagged (`HL5`). The random-sign null (200 seeds, `6/6` required) is beaten.

**One-stage attribution (post-outcome, `L4_DIAGNOSIS_V1.json`).** Custody and
pilot are excluded (all clauses pass; `p0` interior). The history bodies were
reproduced op-for-op: all twelve keep 5–6 of 6 units live on the `U` inputs
(`P05`-POS: 5, no all-zero rows), the labels are balanced (`129/256`), the
evaluation majority class (71/128) is far below the criterion — the
loss-of-plasticity hypothesis is **rejected**. The parent's graded potential
`C_pot_QH_B2` orders POS above NEG at `P05` (**103 > 78**) and on all six
sources (123>79, 118>81, 123>101, 125>89, 103>78, 123>77), and on the parent's
seven (7/7): the miss is the hit threshold (112/128) inside `Ev_Q = pH`
saturating both families at 0 where the POS potential lies below it —
**the instrument's threshold resolution, not the transfer mechanism.**

**Quantifiers.** All six sources; all 24 proposals per law; both routes
(integer counting over the raw score lists).

**Assumptions.** The parent's instrument, seeds and criterion; `Ev_Q(U) = Q(U)
= pH`.

**Falsifiers.** Any recomputed `pH` differing from the receipt's own score
list; a scored source whose `EP-1` verdict differs between routes.

**Strongest parents.** `gmi-833-real-developmental-validation-v1` (the
instrument and its 7/7 in-session result); #909/#908 (`Ev_Q`, `C_pot`).

**Forbidden extrapolations.** `EVOLVABILITY_MECHANISM_GENERAL`,
`CONTINUAL_LEARNING_GENERAL_CLAIM`, `THRESHOLD_TUNED_TO_OUTCOME` (the graded
ordering is reported, the frozen quantity is not redefined),
`FIRST_WINDOW_RESCORED_OR_DROPPED`.

---

## FP-3 — window-2 custody and `EP-1`/`EP-2`/`EP-3` scores, and the combined two-window record

**Scope.** `POSTERIOR_SOURCES_V2.json` and its registered continuation
`POSTERIOR_SOURCES_V2_EXTENDED.json` (window 2, amendment 1, anchor
`65d00257`), the `REAL_RUNS_L5/` receipts, the instrument and `PR-1` as in
FP-2; `EP-4` is reported here and in FP-4, never closure-bearing.

**Statement (window 2).** Seven sources were admitted (`P01`–`P07`,
`FFA-1P` custody 7/7; every revision's Wikimedia `sha1` equals the sha1 of the
scored bytes). The sixth, `P06` (revision 1375698114, created 12:45:04Z),
measured `AT_FLOOR_OR_CEILING` under `PR-1` (pilot grid 60:2, 90:7, 120:22,
180:24, 240:24, 360:24, 540:24 — no budget with `p0` in [9/24, 21/24]) and was
**excluded by name and replaced** by the next admitted candidate in the same
ordered list, `P07` (revision 1375698478, created 12:49:31Z, posterior to the
anchor + 60 s, Wikimedia `sha1 f16d3fff…` equal to the sha1 of the bytes), per
`FREEZE_V1.md` §4.6 clause 2 — disclosed as D4. The six scored sources give
`pH(POS)` = 9, 17, 1, 1, 10, 7 of 24, `pH(NEG)` = 0 on all six,
`p0(POS)` = 15, 20, 11, 10, 12, 13, so **`EP-1` 6/6** (`k2 = 6 >= 6`), `EP-2`
6/6, `EP-3` 0/6, `EP-4` 6/6. The exact label-permutation null of `6/6` is
`1/64`; `NULL_RANDOM_SIGN` (200 seeds) is beaten. **Combined record:** window 1
`5/6` (the miss `P05`, a tie at 0/24, reported verbatim, never re-scored) plus
window 2 `6/6` = **11/12**, exact null `13/4096`; the two-window procedure null
(`1/64 + (6/64)(1/64) = 70/4096`) is disclosed beside it. Both routes agree on
every `p0`, `pH`, `C_pot`, verdict and custody clause, and
`FREEZE_V1_AMENDMENT_1` §5 clause 3 is met: **`ROW_L` closes.**

**Quantifiers.** All seven admitted sources (custody); all six scored sources
(every prediction); all 24 proposals per law; both routes.

**Assumptions.** As FP-1/FP-2; the continuation record's first six admitted
entries are byte-identical to the frozen `POSTERIOR_SOURCES_V2.json`.

**Falsifiers.** Any window-2 scored source with `pH(POS) <= pH(NEG)`; an
excluded source not reported; a replacement not posterior; either route's
window-2 numbers differing.

**Strongest parents.** As FP-1/FP-2; `FREEZE_V1.md` §4.6 clause 2 and
`FREEZE_V1_AMENDMENT_1` §3–5 (the registered replacement rule).

**Forbidden extrapolations.** `FIRST_WINDOW_RESCORED_OR_DROPPED`,
`THIRD_WINDOW_OPENED` (the continuation to `P07` is the same window's
replacement, not a new window), `EV_Q_DEFINITION_CHANGED`,
`THRESHOLD_TUNED_TO_OUTCOME`, `SECTION_L_COMPLETE`.

---

## FP-4 — the `EP-4` developmental-potential ordering (`C_pot`)

**Scope.** The parent's graded potential `C_pot_QH_B2` (the best evaluation
score reached by any of the 24 history-conditioned proposals) on the parent's
seven in-session sources, window 1 and window 2.

**Statement.** `C_pot_QH_B2(POS) > C_pot_QH_B2(NEG)` holds on **7/7** of the
parent's sources (post hoc; values 124>108, 121>103, 124>108, 125>90, 128>98,
122>82, 117>88), on **6/6** window-1 sources (post hoc; 123>79, 118>81,
123>101, 125>89, 103>78, 123>77) and on **6/6** window-2 sources
(**prospective**; 121>82, 128>97, 117>88, 115>88, 128>99, 122>80). The window-1
miss `P05` is ordered by the graded quantity (103 > 78) although the frozen
`Ev_Q = pH` reads 0/24 on both families. `EP-4` is a mechanism-level
co-prediction reported beside `EP-1`; **it is not closure-bearing for
`ROW_L`** (`POTENTIAL_ORDERING_CLOSES_EVOLVABILITY_ROW` forbidden).

**Quantifiers.** Every source named; the post-hoc / prospective split per
window is stated.

**Assumptions.** `C_pot_QH_B2` as recorded in the parent and this lane's
receipts; `Ev_Q` is the parent's definition and is unchanged.

**Falsifiers.** Any source with `C_pot_QH_B2(POS) <= C_pot_QH_B2(NEG)`; a
recomputed `C_pot` differing from the receipt's own score list.

**Strongest parents.** #909/#908 (`C_pot`, "Formalize developmental potential
separately from current capability"); `FREEZE_V1_AMENDMENT_1` §3 (the
registered lever).

**Forbidden extrapolations.** `POTENTIAL_ORDERING_CLOSES_EVOLVABILITY_ROW`,
`EV_Q_DEFINITION_CHANGED`, `THRESHOLD_TUNED_TO_OUTCOME`,
`FIRST_WINDOW_RESCORED_OR_DROPPED`.
