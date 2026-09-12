# RV-377-134 — FREEZE: channel law CL-7, external store / retrieval channel

Frozen BEFORE the run. Harness: `gmi_channel_laws.py --law cl7`. Receipt:
`microscopes/results/CHANNEL_LAW_EXTERNAL_STORE_RV_377_134.json`. Alias: tasking "TI-7".

## 1. Channel and derivation

Same world (`W` uniform on `L = 64` bits; development reveals `r` indices `S`). **New
channel:** an external store `C ⊂ [L]` of size `cL`, drawn uniformly and independently of `S`
at world time, holding the true bits of its indices. At query time the machine may retrieve
index `i` from the store; if `i ∈ C` the retrieval returns `W[i]` with probability `ρ` and an
independent uniform bit otherwise (the machine cannot tell which). If `i ∉ C` the store
returns nothing.

For a query `i`: revealed by development (probability `r/L`) → determined. Otherwise, in the
store (probability `c`, by independence of `C` and `S`) → the retrieved bit is correct with
probability `ρ + (1−ρ)/2 = (1+ρ)/2`, and no other information about `W[i]` exists. Otherwise
→ coin. So for every machine in the `{D, store}` class:

```
E_W[acc]  ≤  r/L + (1 − r/L)·[ c(1+ρ)/2 + (1−c)/2 ]  =  1 − (1 − r/L)(1 − cρ)/2         (CL-7)
```

**Boundary containment (analytic, unit-tested):**

* `cρ = p` → `1 − (1 − r/L)(1 − p)/2` = CL-2: a store of coverage `c` and reliability `ρ` is
  worth exactly a query hint of rate `p = cρ`. RAG is TI-2 with `p` factored into coverage
  times reliability.
* `c = 0` or `ρ = 0` → `½ + r/(2L)` = CL-1.
* `c = ρ = 1` → 1.

Two further lines are derived for the machines that misuse the channel:

* store only, ignoring development: `½ + cρ/2`, flat in `r`;
* store **before** development (wrong precedence: trusts the volatile channel over the exact
  one): `ceiling7 − (r/L)·c·(1−ρ)/2`. The shortfall is the fraction of indices that are both
  revealed and stored, times the store's error rate `(1−ρ)/2`, and vanishes iff `ρ = 1`.

## 2. Machines

| machine | order | expected |
|---|---|---|
| `rag` | development, then store, then coin | ceiling (attains) |
| `ignore_store` | development, then coin | CL-1 line, flat in `(c, ρ)` |
| `store_only` | store, then coin | `½ + cρ/2`, flat in `r` |
| `store_first` | store, then development, then coin | `ceiling7 − (r/L)c(1−ρ)/2` |

## 3. Predicate rule, grid, pilot

Expectation across 60 independent `W` draws (each with its own `S` and `C`), s.e. across
draws, 32 passes over all 64 indices; 4 s.e. primary, 3 s.e. diagnostic. Pilot: 2 draws × 1
pass, rc 0 only, verdicts not read.

Grid: `c ∈ {0, 0.25, 0.5, 1}` × `ρ ∈ {0, 0.5, 1}` × `r ∈ {0, 16, 32, 48}` × 4 machines = 192
cells.

Predicted ceilings (`L = 64`) and `store_first` lines:

| `c` | `ρ` | r=0 | r=16 | r=32 | r=48 | store_first at r=32 |
|---|---|---|---|---|---|---|
| 0 | any | 0.5 | 0.625 | 0.75 | 0.875 | 0.75 |
| 0.25 | 0 | 0.5 | 0.625 | 0.75 | 0.875 | 0.6875 |
| 0.25 | 0.5 | 0.5625 | 0.6719 | 0.7812 | 0.8906 | 0.75 |
| 0.25 | 1 | 0.625 | 0.7188 | 0.8125 | 0.9062 | 0.8125 |
| 0.5 | 0 | 0.5 | 0.625 | 0.75 | 0.875 | 0.625 |
| 0.5 | 0.5 | 0.625 | 0.7188 | 0.8125 | 0.9062 | 0.75 |
| 0.5 | 1 | 0.75 | 0.8125 | 0.875 | 0.9375 | 0.875 |
| 1 | 0 | 0.5 | 0.625 | 0.75 | 0.875 | 0.5 |
| 1 | 0.5 | 0.75 | 0.8125 | 0.875 | 0.9375 | 0.75 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 |

At `c = 1` the ceiling column is the RV-377-124 `bound2` table with `p = ρ`, cell for cell.

## 4. Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| **E1** | No machine exceeds the CL-7 ceiling by more than 4 s.e. in any cell. | any cell above |
| **E2** | `rag` meets the ceiling within 4 s.e. in every cell. | any shortfall |
| E3 | `ignore_store` sits on the CL-1 line within 4 s.e. at every `(c, ρ)`, including `c = ρ = 1`. | any rise with `c` or `ρ` |
| E4 | `store_only` sits on `½ + cρ/2` within 4 s.e. at every `r`. | off the line |
| **E5** | `store_first` sits on `ceiling7 − (r/L)c(1−ρ)/2` within 4 s.e. everywhere, and is below the ceiling by more than 4 s.e. wherever `r > 0`, `c > 0`, `ρ < 1`. | off its line, or not below |
| E6 | Boundaries: at `c = 1` the ceiling equals CL-2 with `p = ρ` cell for cell (identity), and at `c = 0` or `ρ = 0` `rag` sits on CL-1 within 4 s.e. | either fails |

**E5 is the one with content beyond containment.** Wrong channel *precedence* — consulting a
lossy store before an exact memory — costs exactly `(r/L)·c·(1−ρ)/2`, derived in advance: at
`c = 1, ρ = 0, r = 48` the `store_first` machine is predicted at **0.5** while `rag` is at
0.875 and `ignore_store` at 0.875. A retrieval-augmented species that lets retrieval override
what it already knows exactly is predicted to fall to chance as retrieval reliability falls.

## 5. What confirmation licenses

Confirming E1–E6 establishes the RAG-class ceiling as a member of the family that contains
CL-2 (at `c = 1`) and CL-1 (at `cρ = 0`), and adds a precedence law: capability tracks the
information a machine uses **in the order it uses it**. One obligation, one world family, no
architecture claim.

---

# RV-377-134 — ADJUDICATION: all six confirmed

192 cells, 60 independent `W` draws × 2048 evaluations each. Receipt
`microscopes/results/CHANNEL_LAW_EXTERNAL_STORE_RV_377_134.json`
(md5 `e19b795fa7a216ea226fb167cec8384c`, verified both sides).

| id | outcome |
|----|---------|
| E1 | **CONFIRMED** — 0 cells above ceiling + 4 s.e.; 0 above 3 s.e. (null 0.26) |
| E2 | **CONFIRMED** — `rag` meets the ceiling in all 48 cells, max \|z\| 2.29 |
| E3 | **CONFIRMED** — `ignore_store` on CL-1 at every `(c, ρ)`, including `c = ρ = 1` |
| E4 | **CONFIRMED** — `store_only` on `½ + cρ/2` at every `r` |
| **E5** | **CONFIRMED** — `store_first` on its line in all 48 cells and below the ceiling by more than 4 s.e. in every cell with `r > 0, c > 0, ρ < 1` |
| E6 | **CONFIRMED** — `c = 1` ceiling equals CL-2 with `p = ρ` cell for cell; `cρ = 0` cells sit on CL-1 |

| `c` | `ρ` | `r` | ceiling | `rag` | `ignore_store` | `store_only` | `store_first` (line) |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.5 | 48 | 0.8906 | 0.8909 | 0.8752 | 0.5630 | 0.8460 (0.8438) |
| 0.5 | 0.0 | 48 | 0.8750 | 0.8746 | 0.8745 | 0.4982 | 0.6896 (0.6875) |
| 0.5 | 0.5 | 16 | 0.7188 | 0.7178 | 0.6257 | 0.6253 | 0.6879 (0.6875) |
| 0.5 | 1.0 | 48 | 0.9375 | 0.9392 | 0.8754 | 0.7494 | 0.9396 (0.9375) |
| 1.0 | 0.0 | 48 | 0.8750 | 0.8748 | 0.8758 | 0.5001 | **0.4982** (0.5000) |
| 1.0 | 0.5 | 16 | 0.8125 | 0.8112 | 0.6288 | 0.7497 | 0.7508 (0.7500) |
| 1.0 | 0.5 | 48 | 0.9375 | 0.9375 | 0.8747 | 0.7512 | 0.7511 (0.7500) |
| 1.0 | 1.0 | 48 | 1.0000 | 1.0000 | 0.8751 | 1.0000 | 1.0000 (1.0000) |

## The result worth reading directly

`(c, ρ, r) = (1, 0, 48)`: the store covers everything and retrieves garbage. `rag` — which
asks its own memory first — scores 0.8748, the CL-1 number. `store_first` — same memory, same
store, but it asks the store first — scores **0.4982**: chance. It has 48 correct bits in hand
and overrides every one of them with a coin. The shortfall `(r/L)·c·(1−ρ)/2 = 0.375` was
written down before the run.

> **Capability tracks the information a machine uses, in the order it uses it.** The RAG
> ceiling is CL-2 with `p = cρ`: coverage times reliability is exactly a hint rate. And a
> retrieval channel consulted *ahead of* exact memory subtracts, in closed form, the
> store's error rate on every index it shadows.

## Terminal

`CL7_EXTERNAL_STORE_LAW_VERIFIED_AT_REGISTERED_SCOPE` = **TRUE**. Contains CL-2 at `c = 1`
(identity, E6) and CL-1 at `cρ = 0` (E6). The precedence line is a verified sub-law.
