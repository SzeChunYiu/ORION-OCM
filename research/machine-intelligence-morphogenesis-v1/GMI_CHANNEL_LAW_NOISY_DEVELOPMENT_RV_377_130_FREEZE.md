# RV-377-130 — FREEZE: channel law CL-3, noisy development

Frozen BEFORE the run. Harness: `gmi_channel_laws.py --law cl3`. Receipt:
`microscopes/results/CHANNEL_LAW_NOISY_DEVELOPMENT_RV_377_130.json`.

Naming: the tasking calls this law "TI-3". `GMI_TARGET_INFORMATION_ACQUISITION_THEOREM_V1.md`
already uses `TI-3` for the description-charging theorem, so the channel laws are indexed
`CL-k` here (`CL-1` = TI-1 of RV-377-123, `CL-2` = TI-2 of RV-377-124). "TI-3" in the tasking
is an alias for `CL-3`.

## 1. Channel and derivation

Same world as RV-377-123: `W` uniform on `L = 64` bits, drawn after the machine is frozen;
development reveals `r` distinct indices; the query is a uniform index. **New channel
property:** each revealed bit reaches the machine through a binary symmetric channel — flipped
independently with probability `q`. In the `k`-copy variant every revealed index is delivered
`k` times, each copy flipped independently.

For an unrevealed index nothing the machine holds depends on `W[i]` (independence of `P`, `R`,
and the other bits), so success is `½`. For a revealed index the machine holds `k` noisy copies
`W[i] ⊕ N_1, …, W[i] ⊕ N_k`; the posterior on `W[i]` is monotone in the copy count, so the
Bayes-optimal rule is the majority (ties: coin), **inverted when `q > ½`**. Let
`m_k(q) = P(majority of k copies equals the true bit)`. Then for every machine in the class:

```
E_W[acc]  ≤  (r/L) · max( m_k(q), 1 − m_k(q) )  +  (1 − r/L)/2            (CL-3)
m_1(q) = 1 − q
```

The tasking's proposed form `(r/L)(1−q) + (1−r/L)/2` is the `k = 1`, `q ≤ ½` branch. It is
**not** a ceiling for `q > ½`: a machine that knows the channel inverts the bit and scores
`(r/L)·q` on revealed indices. The derivation therefore replaces the proposed form with the
`max` form before any run. The proposed form survives as the **"trust the bits" line** —
the exact expected accuracy of the machine that ignores channel noise.

**Boundary containment (checked analytically, unit-tested in `test_gmi_channel_laws.py`):**

* `q = 0` → `m_k = 1` → `½ + r/(2L)` = CL-1 for every `k`.
* `q = ½` → `m_k = ½` → `½` for every `r`: development carries no information, the law
  collapses to the CL-1 point `r = 0`.
* `q = 1`, `k = 1` → deterministic relabelling → `½ + r/(2L)` = CL-1 again (for the machine
  that inverts).
* `k = 1` → `max(1−q, q)` form; `k ≥ 1` contains `k = 1`.

Why the tasking's remark "ignore-noise and know-noise machines coincide" holds only on one
side: for `q ≤ ½` the trusting table *is* the Bayes rule, so both sit on the ceiling; for
`q > ½` the trusting table sits on `(r/L)(1−q) + (1−r/L)/2 < ½`, i.e. **below a machine that
ignores development altogether**. Being wrong about a channel costs more than not reading it.

## 2. Machines

Single-reveal grid (`k = 1`):

| machine | reads | expected line |
|---|---|---|
| `know_noise` | copies + `q`; inverts when `q > ½` | ceiling (attains) |
| `trust` | first copy, ignores `q` | `(r/L)(1−q) + (1−r/L)/2` |
| `ignore_dev` | nothing | `½` |

`k`-copy grid (`q < ½` only, so majority is optimal and no inversion arises):

| machine | reads | expected line |
|---|---|---|
| `majority` | all copies, majority, coin on ties | ceiling (attains) |
| `first_copy` | first copy only | `(r/L)(1−q) + (1−r/L)/2`, flat in `k` |
| `unanimous` | trusts only a unanimous set of copies, else coin | `(r/L)[(1−q)^k + ½(1−(1−q)^k−q^k)] + (1−r/L)/2` |

Every machine's expected accuracy is derived, not just the ceiling: the theory predicts the
whole table.

## 3. Predicate rule (RV-377-123 lesson) and disclosed pilot

Every predicate is over the **expectation across independent protected draws of `W`**, with
the standard error across draws. 60 draws per cell, 32 full passes over all 64 indices per draw
(stratified queries; 2048 evaluations per draw). Primary falsifier: 4 s.e. The number of cells
beyond 3 s.e. is reported as a diagnostic against its null expectation (0.00135 per cell,
one-sided), not used as a falsifier.

Disclosed pilot: the harness was executed once with 2 draws × 1 pass on all five laws to check
that it runs to completion (rc 0 for each). With 2 draws the printed verdicts are meaningless
and were not read for content. No cell of the registered grid has been run.

## 4. Grid

Single: `q ∈ {0, 0.1, 0.25, 0.4, 0.5, 0.75, 1.0}` × `r ∈ {0, 16, 32, 48, 64}` × 3 machines
= 105 cells. Multi: `q ∈ {0.1, 0.25, 0.4}` × `k ∈ {1, 3, 5}` × `r ∈ {16, 32, 48}` × 3
machines = 81 cells. 186 cells, 11 160 draws.

Predicted ceilings (single, `L = 64`):

| `q` | r=0 | r=16 | r=32 | r=48 | r=64 | trust line at r=32 |
|---|---|---|---|---|---|---|
| 0.0 | 0.5 | 0.625 | 0.75 | 0.875 | 1.0 | 0.75 |
| 0.1 | 0.5 | 0.600 | 0.70 | 0.800 | 0.9 | 0.70 |
| 0.25 | 0.5 | 0.5625 | 0.625 | 0.6875 | 0.75 | 0.625 |
| 0.4 | 0.5 | 0.525 | 0.55 | 0.575 | 0.6 | 0.55 |
| 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| 0.75 | 0.5 | 0.5625 | 0.625 | 0.6875 | 0.75 | **0.375** |
| 1.0 | 0.5 | 0.625 | 0.75 | 0.875 | 1.0 | **0.25** |

Predicted ceilings (multi, `r = 32`): `q=0.1`: k=1 0.70, k=3 0.736, k=5 0.7457; `q=0.25`:
0.625, 0.6719, 0.6982; `q=0.4`: 0.55, 0.574, 0.5913. Unanimity line at `q=0.25, r=32`: k=3
0.6016, k=5 0.5591 — the wasteful machine gets *worse* with more copies while the ceiling rises.

## 5. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| **N1** | No machine exceeds the CL-3 ceiling by more than 4 s.e. in any of the 186 cells. | any cell above |
| **N2** | `know_noise` **meets** the ceiling within 4 s.e. at every `(q, r)`, including `q ∈ {0.75, 1.0}`. | any shortfall |
| **N3** | `trust` sits on `(r/L)(1−q) + (1−r/L)/2` within 4 s.e. everywhere, and for `q ∈ {0.75, 1.0}`, `r ≥ 16` it is **below ½ by more than 4 s.e.** | off its line, or not below chance |
| N4 | At `q = ½` every machine is within 4 s.e. of `½` at every `r`. | any cell off ½ |
| N5 | At `q = 0`, `trust` and `know_noise` reproduce the RV-377-123 CL-1 curve within 4 s.e. | divergence |
| **N6** | `majority` meets the `k`-ceiling everywhere; `first_copy` sits on its `k = 1` line at every `k` (flat in `k`); `unanimous` sits on its derived line and is below the ceiling by more than 4 s.e. wherever `k ≥ 3`. | any clause |

**N3 is the sharp one.** A channel read with the wrong noise model is worse than a channel
not read: the trusting table at `q = 0.75, r = 64` is predicted at **0.25**, against 0.5 for
`ignore_dev` and 0.75 for `know_noise`, all three numbers derived before the run.

## 6. What confirmation licenses

Confirming N1–N6 establishes CL-3 as a verified member of the channel-law family with CL-1 as
its `q = 0` boundary, and adds the first law in the family in which *knowledge of the channel*
(the value of `q`) is itself a capability-bearing quantity. It says nothing about architecture
(RV-377-121 stands), nothing beyond exact identification on this world family.
