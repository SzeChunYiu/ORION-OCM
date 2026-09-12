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
