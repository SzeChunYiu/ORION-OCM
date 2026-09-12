# RV-377-131 — FREEZE: channel law CL-4, bounded state — the proposed law is false, and the corrected one is frozen instead

Frozen BEFORE the run. Harness: `gmi_channel_laws.py --law cl4` (100 draws, 64 passes).
Receipt: `microscopes/results/CHANNEL_LAW_BOUNDED_STATE_RV_377_131.json`. Alias: tasking "TI-4".

## 1. The proposed form, and why derivation rejects it before any run

The tasking proposed: *a machine that may retain at most `s` bits of development obeys
`acc ≤ ½ + min(r, s)/(2L)`, tight at `s ≥ r`.* That is the accuracy of a machine that keeps
`min(r, s)` revealed bits **exactly** and tosses a coin on the rest. It is a line some machine
attains. It is **not a ceiling**, because `s` bits of state can hold *lossy* information about
all `r` revealed bits at once, and a lossy code beats exact truncation on average.

Example, `r = 7`, `s = 4`. Truncation keeps 4 bits: mean correct among the 7 revealed =
`(4 + 3·½)/7 = 0.786`. The Hamming(7,4) code is a perfect code: every 7-bit string is within
Hamming distance 1 of exactly one codeword. Store the nearest codeword (4 bits); reconstruct
it; the reconstruction is wrong in at most one of the 7 positions, and in zero positions with
probability 1/8. Mean correct = `1 − (7/8)/7 = 0.875 > 0.786`. The proposed law is violated by
a legal 4-bit machine.

The finding is recorded here, before the run, as a **theorem error in the proposed form**, and
the corrected law is the one frozen and tested.

## 2. Channel and corrected derivation

Channel: the machine receives the revealed index set `S` (`|S| = r`, independent of `W`, so
it carries no world-information and is not charged) and may retain a state `Z` with at most
`2^s` values that depends on the revealed bits `B = (W[i])_{i∈S}`. At query time it serves
`g(S, Z, i)`. The budget `s` bounds **world-information state**; index bookkeeping is a known
additive cost left outside the law and named in scope.

Derivation. Given `S`, the `r` revealed bits are iid uniform. For fixed `(S, Z)` the machine's
answers over `i ∈ S` form a reconstruction `b̂(Z) ∈ {0,1}^r` (a randomized machine is a mixture
of deterministic ones and cannot do better in expectation). With `Z` ranging over `≤ 2^s`
values, `b̂` ranges over a codebook of `≤ 2^s` words, and the expected number of wrong revealed
answers is at least the expected distance from a uniform `B` to the nearest codeword. Each
codeword can be the nearest word for at most `C(r, t)` strings at distance `t`, so filling
Hamming balls greedily gives the **sphere-covering lower bound**

```
d*(r, s)  =  (1 / (r · 2^r)) · Σ_t  t · n_t,    n_t = min( 2^s · C(r, t),  2^r − Σ_{t'<t} n_{t'} )
```

on the per-bit distortion of any `2^s`-word code, and unrevealed indices are coins, so

```
E_W[acc]  ≤  (r/L) · (1 − d*(r, s))  +  (1 − r/L)/2                              (CL-4)
```

`d*` is attained exactly wherever a **perfect code** exists: repetition `{0^r, 1^r}` at `s = 1`
(`r` odd), Hamming at `r = 2^m − 1, s = r − m`, even-weight at `s = r − 1`; and trivially at
`s = 0` and `s ≥ r`. At other `(r, s)` the ceiling is a converse; tightness is **not claimed**.

**Boundary containment (analytic, unit-tested):**

* `s ≥ r` → `d* = 0` → `½ + r/(2L)` = CL-1.
* `s = 0` → `d* = ½` → `½` = CL-1 at `r = 0`.
* `s = r − 1` → `d* = 1/(2r)` → `½ + (r−1)/(2L)` = the truncation line: the proposed form and
  the corrected law **coincide** at `s = r − 1`, and nowhere else in `0 < s < r − 1`.
* For `0 < s < r − 1`: `ceiling4 > naive4` strictly (a lossy code strictly beats truncation).

## 3. Machines (`legal` means the state fits in `s` bits)

| machine | state | legal | expected |
|---|---|---|---|
| `truncate` | first `min(r,s)` revealed bits, exact | always | proposed line `½ + min(r,s)/(2L)` |
| `repetition` | majority bit of all `r` revealed bits (1 bit) | `s ≥ 1` | ceiling at `s = 1` |
| `hamming` | nearest Hamming codeword (`r − m` bits) | `r = 2^m−1`, `s ≥ r−m` | ceiling at `s = r − m` |
| `even_weight` | nearest even-weight word (`r − 1` bits) | `s ≥ r − 1` | ceiling at `s = r − 1` |
| `parity_store` | parity of the revealed bits (1 bit), served as every revealed answer | `s ≥ 1` | `½` — the wrong statistic |
| `truncate_flip` | first `min(r,s)` bits, served inverted | always | `½ − min(r,s)/(2L)` — wrong about the world |

## 4. Grid, predicted numbers, pilot

`L = 64`, `r ∈ {7, 15, 31, 63}` (Hamming lengths), `s ∈ {0, 1, ⌊r/4⌋, r−m, r−1, r}`;
100 independent `W` draws per cell, 64 full passes (4096 evaluations per draw). 100 draws
rather than 60 because the smallest predicted margin over the proposed line, at `(7, 1)`, is
0.0093 and needs the extra draws to clear 4 s.e. with room. Pilot: 2 draws × 1 pass, rc 0
only, verdicts not read.

| `r` | `s` | ceiling (CL-4) | proposed line | `d*` | predicted margin |
|---|---|---|---|---|---|
| 7 | 1 | **0.5171** | 0.5078 | 0.3438 | +0.0093 (repetition) |
| 7 | 4 | **0.5410** | 0.5312 | 0.1250 | +0.0098 (Hamming) |
| 7 | 6 | 0.5469 | 0.5469 | 0.0714 | 0 (coincide) |
| 15 | 1 | **0.5245** | 0.5078 | 0.3953 | +0.0167 |
| 15 | 3 | 0.5492 | 0.5234 | 0.2901 | converse only |
| 15 | 11 | **0.6025** | 0.5859 | 0.0625 | +0.0166 |
| 15 | 14 | 0.6094 | 0.6094 | 0.0333 | 0 |
| 31 | 1 | **0.5350** | 0.5078 | 0.4278 | +0.0272 |
| 31 | 7 | 0.6167 | 0.5547 | 0.2591 | converse only |
| 31 | 26 | **0.7271** | 0.7031 | 0.0312 | +0.0240 |
| 31 | 30 | 0.7344 | 0.7344 | 0.0161 | 0 |
| 63 | 1 | **0.5497** | 0.5078 | 0.4495 | +0.0419 |
| 63 | 15 | 0.7557 | 0.6172 | 0.2403 | converse only |
| 63 | 57 | **0.9768** | 0.9453 | 0.0156 | +0.0315 |
| 63 | 62 | 0.9844 | 0.9844 | 0.0079 | 0 |

## 5. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| **B1** | No legal machine exceeds the CL-4 ceiling by more than 4 s.e. in any cell. | any cell above |
| B2 | `truncate` sits on the proposed line `½ + min(r,s)/(2L)` within 4 s.e. in every cell. | off the line |
| **B3** | The proposed law is **falsified as a ceiling**: `repetition` at `s = 1` and `hamming` at `s = r − m` exceed the proposed line by more than 4 s.e. in all 8 such cells, by the margins tabled above. | any of the 8 cells not above |
| **B4** | The corrected ceiling is **attained** (within 4 s.e.) at every perfect-code and boundary point: `s = 0` (truncate), `s = 1` (repetition), `s = r − m` (hamming), `s = r − 1` (even_weight and truncate), `s = r` (truncate). | any shortfall |
| B5 | `parity_store` sits on `½` and `truncate_flip` on `½ − min(r,s)/(2L)`, within 4 s.e. everywhere. | either off |
| B6 | *(diagnostic, no falsifier)* at `s = ⌊r/4⌋` the ceiling is respected; no machine here is claimed to attain it. | — |

**B3 and B4 together are the content.** B3 says the tasking's law is wrong by a margin the
theory computes; B4 says the replacement is exact where a perfect code exists. Both were
derived before a single world was drawn.

## 6. What confirmation licenses, and scope

Confirming B1–B5 establishes that the bounded-state ceiling is the rate-distortion form, not
the truncation form: **compressed memory buys capability equal to the sphere-covering
distortion gap**, and the gap is zero at `s = 0`, `s = r − 1`, `s ≥ r` and positive between.
This is the first law in the family that is not attained at every grid point, and the doc says
so. Not charged: the `log₂ C(L, r)` bits of index bookkeeping. One obligation, one world family,
no architecture claim.
