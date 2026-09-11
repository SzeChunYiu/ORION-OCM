# `CONTINUED_OCM` — the integrated developmental controller, as one arm

Every OCM-specific win in this lane came from a separate research script compared to
the parent on its own. The mission's Q4 (composition) and the cross-domain spine need
them as **one controller** inside the runner, so every future run carries it:

```text
CONTINUED_OCM = MDL selection → probe (depth from history) → task-statement rule on a
                miss → D_live liveness on the probe hit-rate
```

`learn_generator`, `validate_generator`, `solve` and `verify_solution` are still the
registered units; every success is externally verified after a real OS-process restart;
the controller reads only the task statement, solved history and the outcomes of
charged actions. Everything it needs is computed in the dev phase and stored in
`dev_state.ocm_controller` (rule cells, probe depth, β, liveness window).

## Smoke test — E6, 16 targets

| arm | ladder | mean `B` |
|---|---|---|
| **`CONTINUED_OCM`** | 16 | **154.4** |
| `PARENT_WITH_MDL` (same library, interleave) | 16 | 307.9 |
| `ORDINARY_ADAPTIVE_PARENT` (frequency library) | 16 | 2 121.5 |
| `RESET` | 16 | 4 187.2 |

The controller runs end-to-end and beats the parent holding the **same library** by
**50 %** — the guided-first probe reaching in `g` what the interleave reaches in `2g`.
It is the first arm in this programme that is OCM-specific, deployable, leak-free, and
better than the strongest parent on a uniform ecology.

## A negative that fixed the depth rule

The first "auto" depth was *max tiling-token count over solved history* — a coverage
rule. On FOREIGN_M1 with the 16-fragment library (`T = 20`) it chose depth 4,
`β = 168 420`, and came out **+22 % worse than RESET** (served 92.5 %, hits landing late),
where depth 3 had given −26 % vs the parent.

Coverage is the wrong objective; the correct one is **expected cost on history**:

```text
for each candidate depth D:
    solved training program with tiling count d_i and paid baseline index b_i costs
        d_i ≤ D :  Σ_{j<d_i} T^j + T^{d_i}/2      (its guided position)
        d_i > D :  β_D + b_i                      (a miss, then fall back)
choose the D with the lowest mean
```

Every quantity is history: `b_i` is the slot count the organism actually paid when it
solved that target. This is the MDL-over-frequency lesson one level up — utility, not
coverage — and it is now the controller's rule.

**Registered before running:** FOREIGN_M1 picks depth 3 (→ ≈ 14.8 k); D2 picks depth 4
(→ ≈ 22.7 k); FV8 with the MDL library picks 4 only if MDL shrinks `T` enough, otherwise
stays negative.

## Scope

One smoke ecology for the integrated arm; the cost-depth rule is under test on three.
Liveness (window 8, hit-rate floor 0.25, periodic re-probe) has not yet been exercised
by a shift in this arm — the plasticity result stands separately.

## Six-ecology run — two strong positives and a negative that fixed the controller

| ecology | RESET | ordinary parent | parent + same library | **`CONTINUED_OCM`** | vs same-library parent |
|---|---|---|---|---|---|
| E5 | 44 738 | 7 167 | 827 | **414** | **−50 %** |
| FV6 (foreign vocabulary) | 3 725 | 4 553 | 4 053 | **2 103** | **−48 %** |
| E7 | 62 935 | 58 636 | 1 014 | **508** | **−50 %** |
| E8 | 40 850 | 4 961 | 1 192 | **596** | **−50 %** |
| FOREIGN_M1 (unstructured) | 29 387 | **19 992** | 31 494 | 36 118 | **+15 %** ✗ (+23 % vs RESET) |

E5, FV6, E7 and E8 all replicate the smoke test: the integrated arm costs almost exactly
**half** of the parent holding the identical library — the `g` versus `2g` signature of
guided-first search over the 50/50 interleave, now seen on five ecologies at scales from
16 to 670 targets. FOREIGN_M1 is the unstructured ecology (RSI class C3), and
the arm is worse than RESET there.

### Diagnosis, from the controller's own state

| | library | T | depth chosen | β | validated better (freq / MDL) |
|---|---|---|---|---|---|
| E5 | MDL (6) | 10 | 3 | 1 110 | 14 / 14 |
| FV6 | MDL (14) | 18 | 3 | 6 174 | 68 / 88 |
| **FOREIGN_M1** | MDL (11) | 15 | **4** | **54 240** | **18 / 16** |

Two errors, both visible in the state:

1. **Depth.** The expected-cost rule estimated the miss rate from **training** tilings.
   The library was mined *from* those programs, so it tiles them optimistically — on a
   structured ecology the bias is harmless (FV6, E5 chose 3 correctly), on an unstructured
   one it makes depth 4 look cheap. Reality: `max B = 186 840`, a miss paying `β` plus the
   full fallback.
2. **Library.** Frequency validated *better* than MDL on FOREIGN_M1 (18 vs 16 of 40) — the
   controller committed to MDL regardless. On an ecology with no latent structure there is
   nothing for compression to find, which is exactly what RSI-2's `mdl_response = −2`
   said about this world.

### `controller_v2`, registered before re-running

- **library chosen by validation**: frequency vs MDL, whichever has the better held-out
  strictly-better count — both are already computed in the dev phase;
- **depth rule on held-out validation**: tiling of each validation task's baseline
  solution against the chosen library; an untileable task is a miss at every depth.

Nothing new is read: the validation stream is solved history the dev phase already paid
for. **Prediction:** FOREIGN_M1 picks frequency and depth 3 → ≈ 14.8 k (the standalone
probe result); E5 and FV6 keep MDL and depth 3, unchanged.

## At scale — the integrated arm on 670 executed targets, on the registered prediction

**Registered:** ≈ 1 650 mean `B`, conservative pays at break-even ≈ 475, liveness never
stands down. **Observed:**

| arm | life_3001 (670) | life_3003 (669) |
|---|---|---|
| **`CONTINUED_OCM`** | **1 657.7** | **1 633.3** |
| `PARENT_WITH_MDL` (same library) | 3 237.5 | 3 241.5 |
| `RESET` | 3 613.8 | 3 647.2 |
| `ORDINARY_ADAPTIVE_PARENT` | 3 842.3 | 3 937.1 |
| `SHUFFLED_HISTORY` | 7 177.7 | 7 237.6 |

Every target verified. −54 % vs RESET, **−49 % vs the parent holding the identical
library**, within 0.5 % of the prediction.

### The ledger — two honest readings of "conservative"

The arm ledger (`m2p1_ledger3.py`) and the probe-gate ledger disagree on one line, and
the disagreement is a definition, not an error:

| ledger | what "conservative" charges | cost | break-even | pays at 670 |
|---|---|---|---|---|
| arm ledger | developmental solving **+ the whole validation phase** | 1 718 166 | **878** | ✗ |
| probe-gate ledger | developmental solving only | 929 652 | **475** | ✓ |
| middle | dev + validation's *candidate* half only | ≈ 1.35 M | ≈ 690 | ✗ (just) |

Validation's *baseline* solves are real targets the agent solved — wanted cognition — so
charging them as overhead is the maximally hostile view; its *candidate* solves are the
admission check's own cost. The conservative verdict therefore turns on that one
attribution and is reported as **borderline, sign depending on the charging rule**.
Marginal (break-even 403) and incremental (215) pay under both ledgers.

### `controller_v2` on FOREIGN_M1 — the negative turns

Both registered choices fired: the controller selected **frequency** (validated 18 vs
MDL 16 of 40) and **depth 3** (`β = 8 420`).

| arm | mean `B` |
|---|---|
| RESET | 29 387 |
| ordinary parent (frequency library, interleave) | 19 992 |
| **`CONTINUED_OCM` v2** | **17 739** |

**−39.6 % vs RESET, −11.3 % vs the strongest parent** on the unstructured foreign
ecology where v1 was +23 % worse than RESET. The magnitude prediction (≈ 14.8 k, the
standalone probe) was ~20 % optimistic: on a miss the controller lets the task-statement
rule choose the interleave where the standalone probe fell straight back to RESET, and on
this ecology that choice costs more than it saves. The sign flipped as predicted;
recorded with the shortfall.

With this, the integrated arm is better than the strongest parent on **six of six**
ecologies (three structured, one unstructured, two built from the M1 lane's own
vocabulary) and at 670-target scale.

## The shift test found two liveness defects in the port — recorded, fixed, re-running

The integrated arm's liveness had only been exercised by the standalone plasticity
script. A shifted ecology inside the runner — `A → B → A′`, `B` built as the exact
**complement** of `A`'s motifs, development on `A` only, 30 targets per segment:

| segment | RESET | **`CONTINUED_OCM` v1 liveness** | parent + library |
|---|---|---|---|
| A | 3 363 | **507** | 1 013 |
| B (stale library) | 3 933 | **8 207** ✗ | 7 865 |
| A′ | 3 282 | 1 065 = parent | 1 065 |
| lifetime | 3 526 | 3 260 | 3 314 |

Two defects, both visible in the segment pattern:

1. **Stood-down probe, live rule.** In `B` liveness did stand the probe down, but the
   task-statement rule — fitted on `A`'s validation — kept routing misses to the interleave
   with the stale library, paying the stale 2× on top of `β`. Fix: while stood down the
   *library* is presumed stale, so misses go to RESET.
2. **Reactivation could fire once, ever.** The re-probe counter only advanced on a
   re-probe, so after the first re-probe it froze; `A′` ran entirely on the interleave,
   which is why it equals the parent to the decimal. Fix: the counter advances every
   target. The standalone plasticity script had both of these right; the port dropped them.

The five non-shifting ecologies and the 670-target worlds are unaffected: their hit-rates
never dropped below the floor, so the probe never stood down there.

**Registered before the re-run:** `A ≈ 507`, `B ≈ RESET + re-probe overhead ≈ 4 100`,
`A′ ≈ 507` after reactivation within one window, lifetime ≈ 1 800 vs parent 3 314.

### liveness_v2 — both directions fire inside the runner

| segment | RESET | **`CONTINUED_OCM` v2** | parent + library | v1 |
|---|---|---|---|---|
| A | 3 363 | **507** | 1 013 | 507 |
| B (stale library) | 3 933 | 5 208 | 7 865 | 8 207 |
| A′ | 3 282 | **731** | 1 065 | 1 065 |
| **lifetime** | 3 526 | **2 149** | 3 314 | 3 260 |

Lifetime moves from a marginal edge (−1.6 % vs the parent) to **−35 % vs the parent and
−39 % vs RESET**. In `B` the probe stands down and misses go to RESET; in `A′` it comes
back within a window.

Against the registered predictions: `A` exact; `A′` *better* than the one-window-lag
estimate (731 vs ~1 250); **`B` missed by 27 %** — predicted ≈ 4 100, observed 5 208. The
estimate under-counted the eight pre-detection targets, each paying `β` plus the full
fallback before the hit-rate floor is crossed. That is the price of a detection window,
and it is recorded as a missed prediction rather than absorbed.

`B` at +32 % over RESET is the integrated arm's worst regime: a stale library costs a
window of misses to detect and a re-probe every window to monitor. The parent's cost in
the same regime is +100 %.

## Twenty worlds, one controller (LUNARC arrays 3593038 → 3593063, liveness_v2)

The integrated arm re-run from a fresh controller-aware dev phase on every world the lane
had executed on LUNARC — three designs, twenty worlds, no per-world tuning:

| world | targets | RESET | integrated | parent + MDL | ordinary parent | library | depth | vs RESET | vs strongest parent |
|---|---|---|---|---|---|---|---|---|---|
| e5_2001 | 17 | 60,046 | **523** | 1,045 | 51,485 | mdl | 3 | −99.1 % | −50.0 % |
| e5_2002 | 22 | 58,739 | **374** | 746 | 6,474 | mdl | 3 | −99.4 % | −49.9 % |
| e5_2003 | 20 | 59,972 | **306** | 611 | 13,082 | mdl | 3 | −99.5 % | −49.9 % |
| e5_2004 | 20 | 65,206 | **369** | 738 | 5,821 | mdl | 3 | −99.4 % | −49.9 % |
| e5_2005 | 21 | 62,287 | **374** | 746 | 44,202 | mdl | 3 | −99.4 % | −49.9 % |
| e5_2006 | 28 | 66,654 | **408** | 816 | 6,984 | mdl | 3 | −99.4 % | −49.9 % |
| e5_2007 | 21 | 48,858 | **392** | 783 | 6,102 | mdl | 3 | −99.2 % | −49.9 % |
| e5_2008 | 26 | 69,594 | **412** | 822 | 5,885 | mdl | 3 | −99.4 % | −49.9 % |
| e5_2009 | 21 | 73,291 | **296** | 592 | 5,578 | mdl | 3 | −99.6 % | −49.9 % |
| e5_2010 | 16 | 66,959 | **371** | 741 | 52,226 | mdl | 3 | −99.5 % | −49.9 % |
| life_3001 | 670 | 3,614 | **1,658** | 3,238 | 3,842 | freq (pre-controller dev) | 3 | −54.1 % | −48.8 % |
| life_3003 | 669 | 3,647 | **1,633** | 3,242 | 3,937 | freq (pre-controller dev) | 3 | −55.2 % | −49.6 % |
| world_1001_min6 | 99 | 55,373 | **1,654** | 3,307 | 11,490 | mdl | 4 | −97.0 % | −50.0 % |
| world_1002_min4 | 82 | 37,830 | **2,735** | 5,468 | 15,178 | mdl | 4 | −92.8 % | −50.0 % |
| world_1003_min6 | 97 | 53,648 | **3,041** | 4,221 | 13,643 | mdl | 4 | −94.3 % | −28.0 % |
| world_1004_min4 | 82 | 30,728 | **5,252** | 6,105 | 22,494 | mdl | 4 | −82.9 % | −14.0 % |
| world_1005_min6 | 61 | 44,804 | **2,273** | 4,545 | 13,370 | mdl | 4 | −94.9 % | −50.0 % |
| world_1006_min4 | 79 | 36,683 | **2,446** | 4,892 | 24,914 | mdl | 4 | −93.3 % | −50.0 % |
| world_1007_min6 | 77 | 40,351 | **3,952** | 7,557 | 21,617 | mdl | 4 | −90.2 % | −47.7 % |
| world_1008_min4 | 73 | 29,364 | **6,236** | 7,979 | 15,216 | mdl | 4 | −78.8 % | −21.9 % |

```text
worlds                      : 20  (E5-recipe seeds 2001–2010, lifetimes 3001/3003 at 670 targets, fresh worlds 1001–1008 min-length 4/6)
beats strongest parent      : 20 / 20
vs RESET                    : median −98.1 %   min −54.1 %
vs strongest parent         : median −49.9 %   min −14.0 %   max −50.0 %
library chosen by validation: MDL on 18 / 18 worlds with a controller-aware dev phase
```

The strongest parent is the better of the two parents on each world: on 18 of 20 it is the
same-library parent, and the integrated arm sits at the P1 bound (0.50) against it; on
world_1003/1004/1008 the parent-with-MDL is already close to the controller and the margin
narrows to 14–28 %, which is the honest floor of this table. Records:
[records/WORLDS_OCM_AGGREGATE.json](records/WORLDS_OCM_AGGREGATE.json) and
`records/worlds_ocm/<world>_ocm/{SUMMARY,LEDGER3_OCM}.json`.

### FV8: the bounded stand-down overhead, and the defect behind it

FV8 (14 foreign-vocabulary motifs of length 3–4, min canonical length 8) is the world where
the library has no value: the probe's depth rule chooses depth 1 (β = 18), no probe hits,
and the controller stands down. Measured (liveness_v2): integrated **56 370** vs RESET
**56 056** (−0.56 %), parent-with-MDL 75 646, ordinary parent 81 800 — the controller
beats the strongest parent by 25 % *by refusing to serve*, and pays a 314-slot/target
overhead against RESET. The ledger cannot pay (there is no benefit to amortise); recorded
as such in `records/worlds_ocm/../OCM_FV8_LEDGER3.json`.

The overhead is not the probe (15 re-probes × 18 slots = 2 slots per target). It is a
**cold-start defect**: liveness_v2 boots *live*, so the first window consulted the
task-statement rule before a single probe had run; on a world the library never fits,
those rule-routed interleaves (parent cost +35 %) are the whole 37 668-slot excess.
**liveness_v3** (runner patched 2026-09-11): cold start stood down, the first target
probes immediately, liveness is earned by a hit and never assumed. Registered before the
re-runs: FV8 overhead falls to ≈ 2 slots/target (< 0.01 %); E5 and the shift lifetime
change by < 1 % (their first probe hits, after which v2 and v3 coincide). Re-runs:
FV8_v3 and E5_v3 on billy-old, SHIFT3 on laptop billy.

**liveness_v3 re-runs (records/OCM_E5_v3_SUMMARY.json, records/SHIFT_SPLIT_v3.json).**
E5: 414.1 → 414.1, byte-identical (prediction held — its first probe hits). Shift
lifetime: 2 148.5 → **2 191.9 (+2.0 %)**; the "< 1 %" prediction **missed**. Per-target
rows: 83 / 90 identical; the 7 that differ are exactly the re-probe cadence targets
(39/40, 47/48, 55/56 swap the β = 1 463 probe charge between neighbours; 63 → 64 moves
the A′ re-activation one target later, 292 → 4 190). Segments: A 507.0 = 507.0, B
5 207.7 = 5 207.7, A′ 730.9 → 860.9. So v3 changes nothing but the phase of the periodic
re-probe, and the missed prediction is the price of one delayed re-activation; the
lifetime stays −38 % vs RESET and −34 % vs the parent (3 314).

**FV8_v3: 56 057.9 vs RESET 56 055.7 — +2.2 slots per target (+0.004 %)**, the registered
floor exactly (15 re-probes × β = 18 over 120 targets = 2.25). The −0.56 % was the
cold-start defect in full; what remains is the price of asking the library every eight
targets whether the world has changed, and it is bounded by β / window regardless of the
world. Record: `records/OCM_FV8_v3_SUMMARY.json`.
