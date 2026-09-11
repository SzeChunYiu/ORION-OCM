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
| FOREIGN_M1 (unstructured) | 29 387 | **19 992** | 31 494 | 36 118 | **+15 %** ✗ (+23 % vs RESET) |

E5 and FV6 replicate the smoke test: the integrated arm halves the cost of the parent
holding the identical library. FOREIGN_M1 is the unstructured ecology (RSI class C3), and
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
