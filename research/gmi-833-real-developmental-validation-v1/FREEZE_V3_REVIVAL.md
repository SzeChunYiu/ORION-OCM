# FREEZE V3 — second registered revival of the continual-learning row

**Package:** `gmi-833-real-developmental-validation-v1`.
**Parent freezes:** `FREEZE_V1.md` @ `808054d9`, `FREEZE_V2_REVIVAL.md` @ `bdf2cdab`.
**V2 outcome commit (unedited):** `50db5224d7f7d1280f213fd38610b04ce6dcb1dc`.
**Claim ceiling:** unchanged. Nothing here widens it. V1 and V2 are not edited
and their misses stand as recorded.

Committed and pushed **before any V3 implementation or outcome exists**.

## 1. What V2 showed, attributed to ONE stage

V2 removed the ceiling and produced one clean full hit — S1, Gutenberg 1342:
`p0 = 12/24`, `pH = 17/24`, `HISTORY_STRICTLY_IMPROVES` at `h_low`, not at
`h_high`, no stored solution reaching `U`, `SEARCH_POLICY_CAPITAL`, EV-1A in
band. The other four POS sequences missed the direction prediction, and missed
hard: `pH = 0/24` on S2, S3 and S4 while `p0` was `1/24`, `19/24`, `4/24`.

The history-initialized draws did not merely fail to help; they failed
absolutely. `C_now^H` was far **below** `C_now^0` on several sequences
(S1: 40 vs 82 correct; S7: 23 vs 84). That is the signature of a carried body
trained to convergence — `SEQ_STEPS = 480` per task, four tasks — into a
representation specialized to its own four XOR offset pairs, whose
re-initialized head cannot be refit inside a 120-step proposal budget.

**Single failing stage: the sequence-training budget, which over-specializes
the carried body.** HIST-1 names this exact falsifier — *"policy overhead is
omitted"*: the priced overhead of a history policy must include the cost of
un-specializing it, and at `SEQ_STEPS = 480` that cost exceeds the whole
proposal budget.

A second, separable defect is also fixed here, and it is a **registry
calibration** fault of V2, not a scientific one: `B_prop = 120` was calibrated
by pilot on Gutenberg 1342 only, and did not transfer — V2's baseline mass sat
at floor or ceiling on four of eight sequences, which cannot test a direction.

Not the failing stage, and unchanged: HIST-1, CAPITAL-1, DP-1, EV-1, the price
vector, `N = 24`, the criterion `theta = 1/8`, the net shape, `T_train`,
`T_eval`, and the requirement that `U` be absent from the stored solutions.

## 2. The levers

1. **`SEQ_STEPS = 120`** per sequence task, down from 480. This is the single
   lever aimed at the attributed stage.
2. **Per-source proposal budget** `B_prop`, set by a p0-only pilot (it never
   constructs a history-conditioned law and so cannot reveal what this freeze
   predicts) to put the baseline mass strictly interior. Measured grid and the
   selected budget, disclosed in full:

| source | p0 at B = 60 / 90 / 120 / 180 / 240 / 360 / 540 | registered `B_prop` | pilot `p0` |
|---|---|---|---|
| Gutenberg 2701 | 0 / 0 / 0 / 9 / 16 / 21 / 24 | **180** | 9/24 |
| Gutenberg 11 | 3 / 18 / 24 / 24 / 24 / 24 / 24 | **90** | 18/24 |
| `/usr/share/dict/cracklib-small` | 0 / 4 / 15 / 24 / 24 / 24 / 24 | **120** | 15/24 |
| `/usr/lib/python3.8/argparse.py` | 0 / 13 / 21 / 24 / 24 / 24 / 24 | **90** | 13/24 |
| `/usr/lib/python3.8/difflib.py` | 0 / 1 / 3 / 14 / 20 / 20 / 22 | **180** | 14/24 |
| `/usr/lib/python3.8/tokenize.py` | 0 / 2 / 14 / 23 / 24 / 24 / 24 | **120** | 14/24 |
| `/usr/share/dict/swedish` | 0 / 2 / 11 / 20 / 23 / 24 / 24 | **120** | 11/24 |

`/usr/share/sounds/alsa/Front_Center.wav`, `/usr/share/sounds/alsa/Rear_Right.wav`
and `/usr/bin/git` are at ceiling (`24/24`) at **every** budget on the grid and
are therefore **excluded** from the V3 registry in advance, by name, rather
than being carried and then explained away.

## 3. Registered V3 design — a matched control

Fourteen sequences: **seven POS and seven NEG, on the same seven real sources.**
For each source the NEG sequence is identical to the POS sequence in source,
discovery task `U`, proposal budget, seeds, criterion and net — **only the four
sequence task offsets differ.** Sequence structure is therefore the single
manipulated variable, and every confound the source could introduce is held
fixed by construction.

- `U` is `XOR(1,2)` on every sequence (the task the budget grid was calibrated on).
- POS sequence tasks: `XOR(1,3)`, `XOR(2,4)`, `XOR(1,4)`, `XOR(2,3)` — low-offset
  XOR pairs sharing the structure `U` needs, none of them equal to `U`.
- NEG sequence tasks: `XOR(12,13)`, `XOR(13,14)`, `XOR(14,15)`, `XOR(12,15)` —
  the same structure class on offsets `U` never reads.
- `SEQ_STEPS = 120`, `K_seq = 4`, so `h_high = 480`; `h_low = 0`.
  `c = B_prop` (per-source, from the table above).
- `N = 24` proposals per law, seeds `5000 + 31i + <sequence number>`, four
  first-hit blocks of six. DP-1 budget ladder `B1 = B_prop/3`, `B2 = B_prop`.
- Net, criterion, splits, feature vector: unchanged from V2.

Sequence ids `T01..T07` (POS) and `T11..T17` (NEG), paired by source:
`T01/T11` Gutenberg 2701, `T02/T12` Gutenberg 11, `T03/T13` cracklib-small,
`T04/T14` argparse.py, `T05/T15` difflib.py, `T06/T16` tokenize.py,
`T07/T17` swedish. sha256 of every source is recorded at run time.

## 4. The V3 predictions, frozen before any V3 run

- **CL3-P1 (direction).** POS: `pH > p0` strictly. NEG: `pH <= p0`.
- **CL3-P2 (HIST-1 at `h_low = 0`).** POS: `HISTORY_STRICTLY_IMPROVES`.
  NEG: any verdict other than `HISTORY_STRICTLY_IMPROVES`.
- **CL3-P3 (overhead flip at `h_high = 480`).** POS: **not**
  `HISTORY_STRICTLY_IMPROVES`, i.e. `h* = c/p0 - c/pH < 480`.
- **CL3-P4 (CAPITAL-1).** POS: no stored solution reaches criterion on `U`
  without further training; with `law_changed` the classification at `h_low` is
  `SEARCH_POLICY_CAPITAL`.
- **CL3-P5a (DP-1A).** For both laws and every sequence, `C_pot(B1) <= C_pot(B2)`.
- **CL3-P5b (DP-1B).** POS: `C_now^0 == C_now^H` and `H_dev^H(B2) > H_dev^0(B2)`.
  NEG: `H_dev^H(B2) <= H_dev^0(B2)`.
- **CL3-P6 (EV-1A).** With `p = pH > 0` the mean first-hit index over the four
  blocks lies in the registered 2-sigma band, compared by squaring in exact
  rational arithmetic; `p = 0` gives `UNREACHABLE_ZERO_USEFUL_MASS`; a censored
  block makes the cell `CENSORED`, which is not a hit.
- **CL3-P7 (EV-1 typing).** `Ev_Q(U)` is an exact `Fraction`, never a float, and
  is a distinct typed object from `C_now`, `C_pot` and `stored`.
- **CL3-P8 (matched control — the load-bearing one).** For each of the seven
  sources, `pH(POS) > pH(NEG)` strictly. Everything but the sequence structure
  is held fixed, so a hit isolates *shared sequence structure* as the cause of
  any history advantage, and a miss falsifies that attribution directly.

## 5. Closure and fail-closed semantics

The row `- [ ] Validate developmental predictions on continual-learning systems.`
is earned iff all fourteen V3 sequences run on their registered real sources,
every CL3-P* is recorded as HIT/MISS/CENSORED with exact numbers, at least five
POS sequences pass the CAPITAL-1 disjointness gate, and every NEG sequence's
predicted non-improvement is checked. The V1, V2 and V3 tallies are all
reported; no earlier record is deleted or re-scored.

If the V3 POS predictions miss again, the package reports the row as an
attributed negative at registered scope and leaves it OPEN, with the
obstruction named. **Three registered passes is the stopping rule frozen here:
there is no V4 in this package.** `FREEZE_V1.md`, `FREEZE_V2_REVIVAL.md` and
this file are append-only.
