# FREEZE V2 — registered revival of the continual-learning row

**Package:** `gmi-833-real-developmental-validation-v1`.
**Parent freeze:** `FREEZE_V1.md` @ `808054d94dcdc188b7ef3e72cd55c18265ef22af`.
**V1 outcome commit (unedited, the honest record):** `1e4fba1c63d6b34990fff531df8f0289cb59cfb6`.
**Claim ceiling:** unchanged from `FREEZE_V1.md`. Nothing here widens it.

This file is committed and pushed **before any V2 implementation or outcome
exists**. `FREEZE_V1.md` is not edited; its predictions stand as recorded and
are reported as MISSES where they missed.

## 1. What failed, attributed to ONE stage

Every V1 POS prediction (CL-P1, CL-P2, CL-P4, CL-P5) missed. Measured:
`p0 = pH = 24/24` on **all eight** sequences, so
`h + c/pH < c/p0` reduces to `h < 0` and the HIST-1 verdict is `TIE` for every
sequence at both registered overhead regimes. On five of eight sequences a
stored solution reached `U` with no further training, so the CAPITAL-1 gate
returned `CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION`.

**Single failing stage: the difficulty of the registered discovery task `U`.**
`AND`/`OR`/`MAJ` over two or three low delay offsets is learned by a 16-unit
MLP in 300 Adam steps from **every** drawn initialization, so the baseline
proposal mass is at its ceiling. A law cannot strictly improve a mass that is
already 1, and a task a stored solution already solves cannot test
search-policy capital. This is a measurement-design failure. It is **not**
evidence about HIST-1, CAPITAL-1, DP-1 or EV-1, and none of those is amended.

Not the failing stage, and therefore unchanged: the HIST-1 inequality, the
CAPITAL-1 2x2, the EV-1A band, the price vector, `N = 24`, the POS/NEG
registry structure, the sequence sources, and the requirement that `U` be
absent from the stored solution set.

## 2. The lever

Replace the registered discovery-task family with one whose baseline mass is
strictly interior, and lower the proposal budget accordingly.

**Difficulty pilot (disclosed).** A pilot measured **only** the scratch law
`p0` — it never constructs a history-conditioned law, so it cannot reveal the
POS/NEG answer this freeze predicts. On Gutenberg 1342 it found
`XOR` over two low offsets at `B_prop = 120`, width 6, `theta = 1/8` gives
`p0 = 11/24`: strictly interior. Three-way parity at the same budget gives
`0/24` (floor) and the V1 family gives `22-24/24` (ceiling). The pilot fixed
the budget band and nothing else.

## 3. Registered V2 design (changes ONLY the stage attributed above)

- Feature vector unchanged: `b[z-1] .. b[z-16]`.
- Net: body `Linear(16,6) + ReLU`, head `Linear(6,1)`. Head re-initialized per
  task and per proposal; body carried across the sequence.
- `T_train = 512`, `T_eval = 128`, success criterion `theta = 1/8`, i.e. at most
  **16** held-out errors.
- `B_prop = 120` optimizer steps = `c` (price 1 per step). `N = 24` proposals
  per law, registered seeds `5000 + 31i + <sequence number>`.
- `SEQ_STEPS = 480` per sequence task, `K_seq = 4`, so
  `h_high = K_seq * SEQ_STEPS = 1920`; `h_low = 0`.
- **Budget ladder for DP-1:** proposals are additionally evaluated at
  `B1 = 40` and `B2 = 120` steps; the protected capability score `s_c` is the
  **integer count of correct held-out predictions** (0..128), `C_now` is the
  score of the undeveloped draw, `C_pot(B) = max s_c` over the 24 proposals at
  budget `B`, and `H_dev(B) = C_pot(B) - C_now`.

Every task is `XOR` over a registered offset pair of the real bit stream. `U`
is never one of the four sequence tasks, so no stored solution is a solution
to `U` by construction.

| id | family | real source | sequence tasks (XOR offset pairs) | `U` |
|---|---|---|---|---|
| S1 | POS | Gutenberg 1342 | (1,3) (2,4) (1,4) (2,3) | XOR(1,2) |
| S2 | POS | `/usr/share/sounds/alsa/Noise.wav` | (1,2) (3,4) (1,4) (2,4) | XOR(2,3) |
| S3 | POS | `/usr/lib/python3.8/json/__init__.py` | (1,2) (2,3) (3,4) (2,4) | XOR(1,3) |
| S4 | POS | `/usr/share/dict/american-english` | (1,2) (1,3) (2,3) (3,4) | XOR(2,4) |
| S5 | POS | Gutenberg 84 | (1,2) (2,3) (3,4) (1,3) | XOR(1,4) |
| S6 | NEG | `/usr/bin/python3.8` | (12,13) (13,14) (14,15) (12,15) | XOR(1,2) |
| S7 | NEG | `/usr/share/sounds/alsa/Rear_Left.wav` | (12,14) (13,15) (12,15) (13,14) | XOR(2,3) |
| S8 | NEG | `/usr/share/dict/swedish` | four degenerate constant-1 tasks | XOR(1,3) |

POS sequences share the low-offset XOR structure `U` needs. NEG sequences are
the same structure class on offsets `U` never reads, or degenerate — the
licensed band's other side, as #903 registered three systems predicted **not**
to transition.

## 4. The V2 predictions, frozen before any V2 run

- **CL2-P1 (direction).** POS: `pH > p0` strictly. NEG: `pH <= p0`.
- **CL2-P2 (HIST-1 at `h_low = 0`).** POS: `HISTORY_STRICTLY_IMPROVES`.
  NEG: any verdict **other than** `HISTORY_STRICTLY_IMPROVES`.
- **CL2-P3 (overhead flip at `h_high = 1920`).** POS: **not**
  `HISTORY_STRICTLY_IMPROVES`. Equivalently `h* = 120/p0 - 120/pH < 1920`.
- **CL2-P4 (CAPITAL-1).** POS: no stored solution reaches criterion on `U`
  without further training, so `stored ∩ U = empty`, and with `law_changed`
  the classification at `h_low` is `SEARCH_POLICY_CAPITAL`.
- **CL2-P5a (DP-1A monotonicity).** For **both** laws and **every** sequence,
  `C_pot(B1) <= C_pot(B2)`.
- **CL2-P5b (DP-1B non-identification).** POS: `C_now^0 == C_now^H` **and**
  `H_dev^H(B2) > H_dev^0(B2)` — equal current capability, different potential,
  on a real system. NEG: `H_dev^H(B2) <= H_dev^0(B2)`.
- **CL2-P6 (EV-1A).** With `p = pH > 0`, the mean one-indexed first-hit index
  over the four registered blocks of six lies in
  `[1/p - 2 sqrt((1-p)/p^2), 1/p + 2 sqrt((1-p)/p^2)]`, compared by squaring in
  exact rational arithmetic. `p = 0` returns `UNREACHABLE_ZERO_USEFUL_MASS`.
  A censored block (no hit in six) makes the cell `CENSORED`, which is **not**
  counted as a hit.
- **CL2-P7 (EV-1 typing).** `Ev_Q(U) = Q(U)` is an exact `Fraction`, never a
  float, and is a different typed object from `C_now`, `C_pot` and `stored`.

## 5. Closure and fail-closed semantics

The row `- [ ] Validate developmental predictions on continual-learning systems.`
is earned iff all eight V2 sequences run on their registered real sources,
every CL2-P* is recorded as HIT/MISS/CENSORED with exact numbers, at least five
POS sequences pass the CAPITAL-1 disjointness gate, and every NEG sequence's
predicted non-improvement is checked. Both the V1 and the V2 tallies are
reported; the V1 misses are not deleted.

If a V2 POS prediction misses, the failure is attributed to one stage and any
further revival requires a **third** freeze over a **newly registered** set of
sequences — never a re-score of these. `FREEZE_V1.md` and this file are
append-only.
