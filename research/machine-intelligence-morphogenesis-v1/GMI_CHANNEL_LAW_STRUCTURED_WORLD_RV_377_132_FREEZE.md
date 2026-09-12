# RV-377-132 — FREEZE: channel law CL-5, structured world — the generalization ceiling

Frozen BEFORE the run. Harness: `gmi_channel_laws.py --law cl5`. Receipt:
`microscopes/results/CHANNEL_LAW_STRUCTURED_WORLD_RV_377_132.json`. Alias: tasking "TI-5".

## 1. Channel and derivation

The world is no longer free: `W = G θ` over GF(2), with `θ` uniform on `H ≤ L` bits and `G` a
**public** full-rank `L × H` matrix fixed before the world draw (so `I(W; G) = 0` and `G` is a
legitimate part of the frozen design `P`). Development reveals `r` indices `S` with their bits
`W[i] = g_i · θ`. Query: a uniform index `j`.

Given `S` and the revealed bits, `θ` is uniform on the affine subspace cut out by the `r`
linear constraints. Row `g_j` lies in `span{g_i : i ∈ S}` iff `W[j]` is a fixed linear
combination of the revealed bits — **determined**. If `g_j` is outside the span, `g_j · θ` is
uniform on that subspace — a **coin** for every machine. Hence, with `f_G(S)` = fraction of the
`L` rows lying in the span of the revealed rows,

```
E_θ[ acc | S ]  =  ½ + f_G(S)/2        for the eliminating machine, and  ≤  for every machine (CL-5)
```

The prediction is **exact per draw**: `f_G(S)` is computed from `S` and `G` alone, before any
answer is served. Averaged over `S`:

* `G_rep` = `L/H` stacked copies of `I_H` (each basis direction appears `L/H` times). A
  direction is covered iff any of its copies is revealed, so
  `E[f] = 1 − C(L − L/H, r)/C(L, r)` — closed form (hypergeometric), tested here.
* `G_rand` = random full-rank `L × H` matrix (seed fixed, public). No closed form; the per-draw
  prediction is exact and its mean is estimated over 2000 independent `S` draws (a computation
  about `G` and `S`, not about `W`) for the table below.

**Boundary containment (analytic, unit-tested):** `H = L` makes every full-rank `G` square and
invertible, so the rows are linearly independent, `f_G(S) = r/L` exactly, and CL-5 reduces to
CL-1 `½ + r/(2L)` for both matrix kinds. `r = 0` gives `½`; `r = L` gives `1`.

**Why this is the generalization law.** CL-1 says a memorising machine can only ever know the
`r` indices it was shown. CL-5 says structure lets a machine answer indices it was **never
shown**, and predicts *exactly how many*: the span fraction, no more. For `G_rep, H = 16,
r = 16` the ceiling is 0.847 against 0.625 for memorisation — structure buys 0.222 of accuracy
on unseen indices, and a machine that reads the same development but ignores `G` gets none of it.

The two matrix kinds predict qualitatively different curves, and both are frozen:

* `G_rep`: coverage grows smoothly (coupon-collecting directions).
* `G_rand`: `r` random rows in GF(2)^H span `2^r` of `2^H` vectors, so an unrevealed row is in
  the span with probability ≈ `2^{r−H}` — **negligible until `r` approaches `H`, then a sharp
  transition to full coverage**. Generalization from generic linear structure is a phase
  transition at `r = H`, not a gradual gain.

## 2. Machines

| machine | reads | expected |
|---|---|---|
| `eliminate` | development + `G`; Gaussian elimination over GF(2), coin outside the span | ceiling (attains, per draw) |
| `table` | development only; ignores `G` | CL-1 line `½ + r/(2L)` |
| `eliminate_wrong_G` | development + a **different** random matrix `G'` (wrong structure); revealed indices first | CL-1 line |

`eliminate_wrong_G` is the deliberately wrong machine. For `j ∉ S`, it serves `Σ α_i W[i]` with
`α` fixed by `G'`; under the true `G` that equals `W[j]` iff the same relation holds in `G`,
which for a random `G'` has negligible probability, and otherwise `W[j] ⊕ Σ α_i W[i]` is a
uniform bit. So a wrong structural belief is predicted to be **neutral**: it neither buys nor
costs, and the machine sits on the CL-1 line.

## 3. Predicate rule, grid, pilot

Predicates over the expectation across 60 independent `θ` draws (each with its own `S`),
s.e. across draws, 32 passes over all 64 indices per draw; primary threshold 4 s.e., 3 s.e.
counts diagnostic. For `eliminate` the reference is the **per-draw** ceiling `½ + f_G(S)/2`,
so the tightness test is not blurred by the variance of `S`. Pilot: 2 draws × 1 pass, rc 0
only, verdicts not read.

Grid: `G ∈ {rep, rand}` × `H ∈ {16, 32, 64}` × `r ∈ {0, 8, 16, 24, 32, 48, 64}` × 3 machines
= 126 machine cells + 21 closed-form check cells.

Predicted mean ceilings (`L = 64`):

| `H` | `r` | `G_rep` closed form | `G_rand` (2000 `S` draws) | CL-1 |
|---|---|---|---|---|
| 16 | 8 | 0.7110 | 0.5651 | 0.5625 |
| 16 | 16 | 0.8469 | 0.8489 | 0.625 |
| 16 | 24 | 0.9281 | 0.9992 | 0.6875 |
| 16 | 32 | 0.9717 | 1.0000 | 0.75 |
| 16 | 48 | 0.9986 | 1.0000 | 0.875 |
| 32 | 8 | 0.6181 | 0.5625 | 0.5625 |
| 32 | 16 | 0.7202 | 0.6250 | 0.625 |
| 32 | 24 | 0.8065 | 0.6887 | 0.6875 |
| 32 | 32 | 0.8770 | 0.9032 | 0.75 |
| 32 | 48 | 0.9702 | 1.0000 | 0.875 |
| 64 | any | = CL-1 | = CL-1 | — |

## 4. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| **S1** | No machine exceeds the per-draw ceiling `½ + f_G(S)/2` by more than 4 s.e. in any cell. | any cell above |
| **S2** | `eliminate` meets the per-draw ceiling within 4 s.e. in every cell. | any shortfall |
| S3 | `table` sits on the CL-1 line within 4 s.e. in every cell — reading the same development without the structure channel buys nothing. | off the line |
| S4 | For `G_rep` the mean of the per-draw span fraction matches the closed form `1 − C(L−L/H, r)/C(L, r)` within 4 s.e. (s.e. across `S` draws) at every `(H, r)`. | mismatch |
| **S5a** | For `G_rep`, `H < L`, `0 < r < L`: `eliminate` exceeds the CL-1 line by more than 4 s.e. in every cell (structure buys the span fraction). | any no-gain cell |
| **S5b** | For `G_rand`, `H < L`: the excess of `eliminate` over CL-1 is below 0.01 at every `0 < r ≤ H/2`, and above 4 s.e. at every `H ≤ r < L` — the phase transition. | gain where none predicted, or none where predicted |
| S6 | `H = L`: `eliminate` sits on CL-1 within 4 s.e. for both matrix kinds. | divergence |
| S7a | `eliminate_wrong_G` never exceeds the CL-1 line by more than 4 s.e. | any cell above |
| S7b | `eliminate_wrong_G` sits **on** the CL-1 line within 4 s.e. everywhere — a wrong structural belief is exactly neutral. | off the line |

S5b is the prediction that distinguishes this law from a curve-fit: two matrices with the same
`H` and the same development are predicted to give **different** generalization curves, one
smooth, one a step, from the same theorem.

## 5. What confirmation licenses

Confirming S1–S7 establishes the first law in the family that bounds capability **beyond the
memorised indices**, with the bound equal to a computable property of the public structure and
the revealed set, containing CL-1 at `H = L`. It does not extend to non-linear structure, to
approximate identification, or to any architecture claim.
