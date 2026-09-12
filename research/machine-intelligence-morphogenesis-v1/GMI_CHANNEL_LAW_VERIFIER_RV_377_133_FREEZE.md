# RV-377-133 — FREEZE: channel law CL-6, verifier channel — the proposed form cannot hold for a binary answer

Frozen BEFORE the run. Harness: `gmi_channel_laws.py --law cl6`. Receipt:
`microscopes/results/CHANNEL_LAW_VERIFIER_RV_377_133.json`. Alias: tasking "TI-6".

## 1. Why the proposed form is replaced before the run

The tasking proposed `acc ≤ 1 − (1 − r/L)·2^{−k}` for a machine allowed `k` proposals per query
to an exact checker. On the RV-377-123 obligation the answer is **one bit**: with `k = 2`
distinct proposals the checker always accepts one of them, so accuracy is 1 for every `r`,
not `1 − (1 − r/L)/4`. No obligation with a binary answer can carry the proposed form. The
verifier channel is only non-trivial when the answer alphabet is larger than `k`, so the
obligation is changed to **block identification** and the law re-derived. This is recorded as
a derivation correction, not a run outcome.

## 2. Channel and derivation

Same world (`W` uniform on `L = 64` bits; development reveals `r` indices). The query names
an **aligned `m`-bit block** (`L/m` blocks); the machine may submit up to `k` proposals for
the block's `m`-bit word to an exact checker, which accepts iff a proposal equals the truth.
Success = some proposal accepted.

Given development, a block with `u` unrevealed bits has exactly `2^u` completions consistent
with what the machine holds, and the truth is uniform among them (the unrevealed bits are
independent of everything held). `k` distinct consistent proposals succeed with probability
`min(1, k/2^u)`; proposals outside the consistent set, or repeated, are wasted. Hence, per
draw, with `u_b(S)` the unrevealed count of block `b`:

```
E_W[ acc | S ]  =  (m/L) Σ_b  min(1, k / 2^{u_b(S)})     for the searching machine, ≤ for all    (CL-6)
```

Averaging over `S`, `u_b` is hypergeometric — `P(u) = C(m, m−u)·C(L−m, r−(m−u)) / C(L, r)` —
giving the closed form

```
ceiling6(L, r, m, k)  =  Σ_{u=0..m}  P(u) · min(1, k / 2^u)
```

**Boundary containment (analytic, unit-tested):**

* `m = 1, k = 1`: `P(u=0) = r/L`, `P(u=1) = 1 − r/L` → `r/L + (1 − r/L)/2 = ½ + r/(2L)` = CL-1.
* `k ≥ 2^m` → every term is 1 → accuracy 1 (the verifier solves the block outright).
* `k = 1`, general `m`: `E[2^{−u}]` — exact block identification with no verifier, itself a
  new closed form contained in the family.
* `m = 1, k ≥ 2` → 1, which is what kills the proposed form.

**What the law says the verifier channel is worth.** The verifier converts *proposals* into
*bits* at the rate of one accepted proposal per query: `k` tries cover `log₂ k` bits of
residual uncertainty per block. Test-time search does not create information about `W`; it
lets the machine *spend* proposals against a channel that leaks exactly one bit of `W` per
query (accept/reject), and the ceiling is the accounting of that leak.

## 3. Machines

| machine | reads | expected |
|---|---|---|
| `verifier_search` | development; enumerates consistent completions; submits `k` distinct ones in random order | ceiling (attains, per draw) |
| `single_proposal` | development; submits one consistent completion, ignores the extra `k − 1` tries | the `k = 1` line `E[2^{−u}]`, flat in `k` |
| `repeat_proposal` | development; submits the same consistent completion `k` times | the `k = 1` line — wastes the channel |
| `random_k` | nothing; submits `k` distinct random `m`-bit words | `min(1, k/2^m)`, flat in `r` |

`single_proposal` and `repeat_proposal` are the R3-style machines: a channel not used, or used
without diversity, buys nothing however wide it is opened.

## 4. Predicate rule, grid, pilot

Expectation across 60 independent `W` draws, s.e. across draws, 32 passes over all `L/m`
blocks per draw; 4 s.e. primary, 3 s.e. diagnostic. `verifier_search`, `single_proposal`,
`repeat_proposal` are referenced to **per-draw** lines computed from `S`. Pilot: 2 draws × 1
pass, rc 0 only, verdicts not read.

Grid: `m ∈ {1, 4, 8}` × `k ∈ {1, 2, 4, 16}` × `r ∈ {0, 16, 32, 48}` × 4 machines = 192
machine cells + 48 closed-form checks.

Predicted ceilings (`L = 64`):

| `m` | `k` | r=0 | r=16 | r=32 | r=48 |
|---|---|---|---|---|---|
| 1 | 1 | 0.5 | 0.625 | 0.75 | 0.875 |
| 1 | ≥2 | 1 | 1 | 1 | 1 |
| 4 | 1 | 0.0625 | 0.1509 | 0.3131 | 0.5827 |
| 4 | 2 | 0.125 | 0.2989 | 0.5695 | 0.8592 |
| 4 | 4 | 0.25 | 0.5525 | 0.8327 | 0.9767 |
| 4 | 16 | 1 | 1 | 1 | 1 |
| 8 | 1 | 0.0039 | 0.0221 | 0.0952 | 0.3342 |
| 8 | 2 | 0.0078 | 0.0442 | 0.1881 | 0.5831 |
| 8 | 4 | 0.0156 | 0.0882 | 0.3495 | 0.8147 |
| 8 | 16 | 0.0625 | 0.3293 | 0.7875 | 0.9898 |

## 5. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| **V1** | No machine exceeds the per-draw ceiling by more than 4 s.e. in any cell. | any cell above |
| **V2** | `verifier_search` meets the per-draw ceiling within 4 s.e. in every cell. | any shortfall |
| V3 | The hypergeometric closed form matches the mean per-draw ceiling within 4 s.e. (s.e. across `S` draws) at every `(m, k, r)`. | mismatch |
| V4 | Boundaries: at `(m, k) = (1, 1)` `verifier_search` reproduces CL-1 within 4 s.e. at every `r`; at every cell with `k ≥ 2^m` it scores exactly 1. | divergence |
| **V5** | `single_proposal` and `repeat_proposal` sit on the `k = 1` line within 4 s.e. in every cell, independent of `k`. | any rise with `k` |
| V6 | `random_k` sits on `min(1, k/2^m)` within 4 s.e. in every cell, independent of `r`. | off the line |

## 6. What confirmation licenses

Confirming V1–V6 establishes the verifier channel's exact worth in this world family and
retires the proposed `2^{−k}` form. It licenses the atlas claim that verifier-gated /
test-time-search species are bounded by `Σ_u P(u) min(1, k/2^u)` under the stated obligation,
and nothing about how a machine chooses its proposals beyond "distinct and consistent".

---

# RV-377-133 — ADJUDICATION: five of six confirmed; V3 falsified as written at 1 of 48 cells, diagnosed as a sampling extreme of the revealed set, closed form upheld on a registered 2 000-draw re-test

192 machine cells + 48 closed-form checks, 60 independent `W` draws × 32 passes each.
Receipt `microscopes/results/CHANNEL_LAW_VERIFIER_RV_377_133.json`
(md5 `a1904a4c679d032572d95f53b712bece`, verified both sides).

| id | outcome |
|----|---------|
| V1 | **CONFIRMED** — 0 cells above the per-draw ceiling + 4 s.e.; 1 cell above 3 s.e. (`(8, 2, 48)` at z = 3.31; null expectation 0.26) |
| V2 | **CONFIRMED** — `verifier_search` meets the per-draw ceiling in all 48 cells, max \|z\| 3.31 |
| **V3** | **FALSIFIED as written** — 47 of 48 closed-form checks within 4 s.e.; at `(m, k, r) = (4, 4, 32)` the mean of the 60 per-draw ceilings is 0.8534 against the closed form 0.8327, z = **4.67** |
| V4 | **CONFIRMED** — `(1, 1)` is CL-1 at every `r`; every `k ≥ 2^m` cell scores exactly 1 |
| V5 | **CONFIRMED** — `single_proposal` and `repeat_proposal` on the `k = 1` line in all 96 cells, flat in `k` |
| V6 | **CONFIRMED** — `random_k` on `min(1, k/2^m)` in all 48 cells, flat in `r` |

| `m` | `k` | `r` | closed form | per-draw ceiling | `verifier_search` | `single_proposal` | `repeat_proposal` | `random_k` |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 32 | 0.7500 | 0.7500 | 0.7497 | 0.7495 | 0.7495 | 0.4984 |
| 1 | 2 | 32 | 1.0000 | 1.0000 | 1.0000 | 0.7498 | 0.7508 | 1.0000 |
| 4 | 1 | 48 | 0.5827 | 0.5830 | 0.5840 | 0.5818 | 0.5794 | 0.0631 |
| 4 | 2 | 48 | 0.8592 | 0.8510 | 0.8497 | 0.5899 | 0.5869 | 0.1275 |
| 4 | 4 | 32 | 0.8327 | **0.8534** | 0.8527 | 0.2995 | 0.3004 | 0.2460 |
| 4 | 4 | 48 | 0.9767 | 0.9721 | 0.9724 | 0.5830 | 0.5826 | 0.2485 |
| 4 | 16 | 48 | 1.0000 | 1.0000 | 1.0000 | 0.5852 | 0.5814 | 1.0000 |
| 8 | 1 | 48 | 0.3342 | 0.3365 | 0.3370 | 0.3346 | 0.3389 | 0.0043 |
| 8 | 4 | 48 | 0.8147 | 0.8217 | 0.8197 | 0.3205 | 0.3283 | 0.0155 |
| 8 | 16 | 32 | 0.7875 | 0.7806 | 0.7817 | 0.0962 | 0.1000 | 0.0624 |
| 8 | 16 | 48 | 0.9898 | 0.9896 | 0.9891 | 0.3290 | 0.3301 | 0.0613 |

## V3 diagnosis — predicate error or theorem error?

V3 does not test a machine. It tests that the mean of a `W`-independent quantity — the
per-draw ceiling, a function of the revealed set `S` alone — over 60 draws of `S` lands within
4 s.e. of its exact expectation. The closed form is exact by linearity of expectation (each
block's unrevealed count is marginally hypergeometric), so a genuine failure would have to be
a harness fault in either the per-draw computation or the closed form.

Three checks, all run on billy-old after the outcome and recorded as post-hoc:

1. **The same code path passes at the other 47 cells**, including `(4, 1, 32)` and
   `(4, 2, 32)` — same `m`, same `r`, different seeds — at z = −0.31 and −0.71. The 48
   z-scores are `[-2.12, -1.99, -1.40, …, 1.41, 1.72, 4.67]`; 27 are exactly 0 (the
   `k ≥ 2^m` cells are constant), so the outlier is 1 of 21 non-degenerate checks.
2. **An independent Monte Carlo of 20 000 fresh `S` draws** at `(4, 4, 32)` gives
   0.83283 ± 0.00025 against the closed form 0.83265: z = 0.7.
3. **Registered re-test** (`gmi_channel_law_verifier_v3_retest.py`, receipt
   `CHANNEL_LAW_VERIFIER_RV_377_133_V3_RETEST.json`, md5
   `80e623d26af587104c82adec36791bbd`): the **continuation draws `d = 60 … 2059`** of the
   same cell key — 2 000 draws independent of the registered 60 — give a mean per-draw
   ceiling of **0.832977**, z = **0.41** against the closed form, and `verifier_search`
   measured on those 2 000 draws meets its per-draw ceiling at z = 0.55.

The registered 60 draws for this one cell are an extreme sample of `S` (their sorted values
are all legitimate multiples of 1/64; their sd 0.0344 matches the Monte-Carlo sd 0.0361).
Under a Gaussian tail such a cell has probability ≈ 3·10⁻⁶ and among 21 non-degenerate checks
≈ 6·10⁻⁵ — rare, and reported as rare. No systematic cause was found: the path is shared with
the 47 passing cells and the continuation of the same cell converges to the closed form.

**Classification: predicate error of the calibration kind, not a theorem error.** The
theorem is tested by V1 and V2 against the *per-draw* ceiling, exactly because the RV-377-123
lesson says the draw variance must not be folded into a constant reference; those two clauses
hold at all 48 cells, including this one (z = −0.58). V3 is upheld on the registered re-test
and is recorded here as `FALSIFIED_AS_WRITTEN_AT_1_OF_48__UPHELD_ON_2000_DRAW_RETEST`.

## The result worth reading directly

`single_proposal` and `repeat_proposal` at `(4, 16, 48)`: 0.5852 and 0.5814, against
`verifier_search` at **1.0000** and the `k = 1` line 0.5830. Sixteen tries at an exact
checker, and the machine that submits the same guess sixteen times gets nothing from
fifteen of them. The verifier channel is worth `log₂ k` bits of residual per block **only
to a machine that spends its proposals on distinct consistent completions**; R3 of RV-377-124
again, for a third channel.

## Terminal

`CL6_VERIFIER_CHANNEL_LAW_VERIFIED_AT_REGISTERED_SCOPE` = **TRUE** (V1, V2, V4–V6 at all
cells; V3 at 47/48 and on re-test). The tasking's `1 − (1 − r/L)2^{−k}` form is retired: it
cannot hold for any binary-answer obligation. Contains CL-1 at `(m, k) = (1, 1)`.
