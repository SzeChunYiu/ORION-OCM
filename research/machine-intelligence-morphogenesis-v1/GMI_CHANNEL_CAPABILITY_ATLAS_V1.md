# GMI Channel Capability Atlas V1

Status: `CHANNEL_LAW_FAMILY_VERIFIED_AT_REGISTERED_SCOPE` = **TRUE** for CL-1 … CL-7.
Status date: 2026-09-12. Every number here traces to a receipt in `microscopes/results/` or to
a closed form in `gmi_channel_laws.py` (boundary identities pinned by `test_gmi_channel_laws.py`).

The completeness/boundary theorem (§7 v) says GMI predicts *what a machine can achieve given
its channels*, not *which machine a search builds*. This atlas is that predictive half laid out
as a family: seven verified capability laws indexed by channel configuration, the lattice of
which contains which, the registered species each law bounds, and the channel configurations
no registered species occupies, with their ceilings derived in advance.

---

## 1. The law family and its boundary lattice

World family (all laws): `W` uniform on `L = 64` bits, drawn after the machine is frozen;
development `D` reveals `r` indices; obligation = exact identification of a queried index
(CL-6: of an aligned `m`-bit block). Every ceiling is on `E_W[accuracy]` over the class of
**all** machines whose only access to `W` runs through the named channels.

| law | channel added | ceiling | record | attained by | status |
|---|---|---|---|---|---|
| CL-1 | development `D` | `½ + r/(2L)` | RV-377-123 | `table` | verified, tight |
| CL-2 | + query hint, rate `p` | `1 − (1−r/L)(1−p)/2` | RV-377-124 | `table2` | verified, tight |
| CL-3 | `D` through BSC(`q`), `k` copies | `(r/L)·max(m_k(q), 1−m_k(q)) + (1−r/L)/2` | RV-377-130 | `know_noise` / `majority` | verified, tight |
| CL-4 | `D` held in ≤ `s` bits of state | `(r/L)(1 − d*(r,s)) + (1−r/L)/2` | RV-377-131 | `repetition`, `hamming`, `even_weight`, `truncate` at perfect-code points | verified; converse only at other `(r,s)` |
| CL-5 | public linear structure `W = Gθ`, `H` dims | `½ + E[f_G(S)]/2` (per-draw exact) | RV-377-132 | `eliminate` | verified, tight |
| CL-6 | `k` proposals to an exact checker, `m`-bit blocks | `Σ_u P_hyp(u)·min(1, k/2^u)` | RV-377-133 | `verifier_search` | verified, tight (closed form 47/48 + re-test) |
| CL-7 | external store, coverage `c`, reliability `ρ` | `1 − (1−r/L)(1−cρ)/2` | RV-377-134 | `rag` | verified, tight |

`m_k(q)` = P(majority of `k` BSC(`q`) copies is correct); `d*(r,s)` = sphere-covering distortion of
a `2^s`-word code on `r` bits; `f_G(S)` = fraction of rows of `G` in the span of the revealed
rows; `P_hyp(u)` = hypergeometric probability that an `m`-block has `u` unrevealed bits.

**Containment lattice** (each arrow: the target reduces to the source at the stated boundary;
all checked analytically in `test_gmi_channel_laws.py` and empirically in the records):

```
CL-1  ←(p=0)──  CL-2  ←(c=1, p=ρ; generally p=cρ)──  CL-7
CL-1  ←(q=0)──  CL-3
CL-1  ←(s≥r)──  CL-4        CL-4 = truncation line exactly at s ∈ {0, r−1} ∪ [r, ∞)
CL-1  ←(H=L)──  CL-5
CL-1  ←(m=1,k=1)──  CL-6    CL-6 = 1 at k ≥ 2^m
CL-1  ←(cρ=0)──  CL-7
```

Three derivations replaced the forms first proposed for this family, **before any run**:
CL-3's `(1−q)` form (a machine line, not a ceiling, for `q > ½`); CL-4's truncation form
(falsified as a ceiling by 8 of 8 registered cells, up to 133 s.e.); CL-6's `2^{−k}` form
(impossible for any binary-answer obligation). The corrected forms are the verified ones.

**Three verified sub-laws that are about machines, not classes**, all derived in advance:

* *wrong channel model* — trust the bits at `q > ½`: `(r/L)(1−q) + (1−r/L)/2`, below chance
  (CL-3; observed 0.0000 at `q = 1, r = 64`);
* *wrong precedence* — store before exact memory: `ceiling7 − (r/L)c(1−ρ)/2` (CL-7; observed
  0.4982 with 48 correct bits in hand);
* *wrong structure* — eliminate under a different `G'`: exactly the CL-1 line (CL-5; neutral).

---

## 2. Registered species mapped to channel classes

Every row is a **CLAIM about the channel class**, valid under the stated membership
assumption. A species is bounded by a law iff its only access to the protected world runs
through that law's channels; the assumption column is what has to hold for the row to apply.
Ceilings are quoted at `L = 64` for the parameter values given; the receipts contain the grids.

| species (registry / phenomena atlas) | channel class | membership assumption | predicted ceiling | example |
|---|---|---|---|---|
| memorising table, kNN / memory-based learning (atlas §8) | CL-1 | serves only what development revealed; query carries no `W` | `½ + r/(2L)` | r=32: 0.750 |
| in-context / prompted LLM (atlas §7) | CL-2 | prompt = query channel with hint rate `p`; weights frozen pre-world | `1 − (1−r/L)(1−p)/2` | r=16, p=½: 0.8125 |
| retrieval-augmented generation (atlas §8; U6) | CL-7 | store fixed at world time, coverage `c`, retrieval reliability `ρ`; consulted after exact memory | `1 − (1−r/L)(1−cρ)/2` | r=16, c=½, ρ=½: 0.7188 |
| RAG that lets retrieval override memory | CL-7 precedence line | store consulted first | `ceiling7 − (r/L)c(1−ρ)/2` | r=48, c=1, ρ=0: **0.500** |
| verifier-gated / test-time search; species atlas F3 VGSC | CL-6 | exact checker, `k` distinct consistent proposals, block-valued answer | `Σ_u P_hyp(u) min(1, k/2^u)` | m=4, k=4, r=32: 0.8327 |
| search that resubmits one guess | CL-6 `k = 1` line | proposals not distinct | `Σ_u P_hyp(u) 2^{−u}` | m=4, r=48: 0.583 at any `k` |
| bounded-memory / compressed / distilled models (atlas §12; U4) | CL-4 | ≤ `s` bits of world-information state; index bookkeeping uncharged | `(r/L)(1−d*(r,s)) + (1−r/L)/2` | r=63, s=57: 0.9768 |
| model that truncates rather than compresses | CL-4 truncation line | keeps `min(r,s)` bits exactly | `½ + min(r,s)/(2L)` | r=63, s=57: 0.9453 |
| generalising linear / structured learners; species atlas F1 RQM (structure-reading half) | CL-5 | structure public and linear over GF(2); machine reads it | `½ + E[f_G(S)]/2` | G_rand H=16, r=24: **1.000** |
| any learner ignoring the structure | CL-1 | reads development only | `½ + r/(2L)` | r=24: 0.6875 |
| noisy-label learners (atlas §17) | CL-3 | labels through BSC(`q`), noise level known | `(r/L)·max(q,1−q) + (1−r/L)/2` | r=32, q=¼: 0.625 |
| noisy-label learner that trusts labels | CL-3 trust line | noise level unknown or assumed zero | `(r/L)(1−q) + (1−r/L)/2` | r=32, q=¾: **0.375** |
| repeated-annotation / majority-vote pipelines | CL-3 `k` copies | `k` independent label copies per item | `(r/L) m_k(q) + (1−r/L)/2` | r=32, q=¼, k=5: 0.698 |
| species atlas F7 ETMI (evidence-tiered memory) | CL-7 × CL-4 | tiers = stores of differing `(c, ρ)`; serving tier bounded in state | composition, §3 (not run) | — |

What no row claims: that the species *reaches* its ceiling (only the named attaining machines
do), that a species' architecture is predicted (RV-377-121: it is not), or that any row extends
beyond exact identification on this world family.

---

## 3. Channel configurations no registered species occupies

Each configuration below is a **prospective prediction**: the ceiling is derived from the same
channel argument, contains two verified laws as boundaries, has an attaining machine written
down, and has a falsifier. None has been run. Reserved ids: RV-377-135 … RV-377-138.

### 3.1 Noisy development × bounded state (CL-3 × CL-4) — RV-377-135

Revealed bits arrive through BSC(`q`), `q ≤ ½`, and the machine keeps ≤ `s` bits of state.
State is a function of the noisy word `B̃ = B ⊕ N`; `B̃` is uniform and independent of `N`, so
for any reconstruction `b̂(Z)`: `P(b̂_i ≠ B_i) = q + (1−2q)·P(b̂_i ≠ B̃_i)`, and the average of
the second term is bounded below by `d*(r, s)` (sphere-covering, applied to the uniform `B̃`).

```
E[acc]  ≤  (r/L)·(1 − [q + (1−2q)·d*(r, s)])  +  (1 − r/L)/2
```

Contains CL-3 at `s ≥ r` and CL-4 at `q = 0`. Attained at perfect-code points by the CL-4
quantisers applied to the noisy word (quantiser error and channel noise are independent, so
the errors add as `q ⊕ d*`). **Prediction:** at `(r, s) = (63, 57)`, `q = 0.1`: ceiling
`(63/64)(1 − [0.1 + 0.8·0.0156]) + 1/128 = 0.8815`; the Hamming machine meets it, truncation
sits at `(57·0.9 + 6·0.5)/64 + 1/128 = 0.856`. **Falsifier:** any legal machine above the
ceiling, or the Hamming machine short of it by 4 s.e.

### 3.2 Noisy development × external store (CL-3 × CL-7) — RV-377-136

An index may carry a BSC(`q`) development bit (accuracy `a = max(q, 1−q)`) and a store
retrieval (accuracy `b = (1+ρ)/2`), independent. For two independent symmetric binary
observations the Bayes rule follows the more reliable one: `ab + max(a(1−b), b(1−a)) = max(a, b)`.

```
E[acc]  ≤  (r/L)·[c·max(a, b) + (1−c)·a]  +  (1 − r/L)·[c·b + (1−c)/2]
```

Contains CL-3 at `c = 0` and CL-7 at `q = 0`. **Sharp prediction:** on doubly-covered indices
the less reliable channel is worth *exactly nothing* — a second channel of lower reliability
does not raise the ceiling, however wide its coverage. **Falsifier:** a machine combining both
channels exceeding `max(a, b)` on doubly-covered indices by 4 s.e. (it would mean the two
observations are not conditionally independent, i.e. the world leaks a correlation).

### 3.3 Structured world × verifier (CL-5 × CL-6) — RV-377-137

`W = Gθ`, block obligation, `k` proposals. Given `S`, the consistent completions of block `b`
form an affine subspace of dimension `δ_b(S)` = rank of the block's rows modulo `span(S)`
(not the unrevealed count `u_b`: structure can pin unrevealed bits and can also tie them).

```
E[acc | S]  =  (m/L) Σ_b  min(1, k / 2^{δ_b(S)})        (per-draw exact)
```

Contains CL-6 at `H = L` (`δ_b = u_b`) and CL-5 at `(m, k) = (1, 1)`. **Prediction:** for
`G_rand, H = 16, m = 8, k = 1`, the ceiling jumps from ≈ `Σ_u P_hyp(u) 2^{−u}` at `r ≤ 8` to
1.0 at `r ≥ 24` (the CL-5 transition, now for whole blocks); the eliminating verifier meets it
per draw. **Falsifier:** any machine above the per-draw ceiling; or `δ_b` computed from the
span failing to predict the eliminating verifier's per-draw score within 4 s.e.

### 3.4 Verifier × external store (CL-6 × CL-7) — RV-377-138

Block obligation with `k` proposals, plus a store giving each covered unrevealed bit a
`(1+ρ)/2`-reliable soft observation. The posterior over the `2^u` consistent completions is a
product of per-bit reliabilities; the optimal machine proposes the `k` highest-posterior
completions, and the ceiling is the expected top-`k` posterior mass:

```
E[acc | S, C]  =  (m/L) Σ_b  top_k( posterior over 2^{u_b} completions )     (per-draw exact)
```

Contains CL-6 at `c = 0` and CL-7 at `(m, k) = (1, 1)`; at `ρ = 1` it is CL-6 with `u_b`
reduced by the covered count. **Prediction:** at `m = 8, k = 4, r = 32, c = ½, ρ = ½` the
ceiling lies strictly between CL-6's 0.3495 and the `ρ = 1` value, and a machine that uses the
store only to *break ties* (not to order proposals) falls below it by 4 s.e. **Falsifier:**
any machine above the top-`k` mass, or the posterior-ordering machine short of it.

### 3.5 Combinations deliberately not derived here

Bounded state × structured world (compression of *dependent* revealed bits) and
noisy × bounded × store need a remote rate-distortion argument with side information; they are
named as open, not guessed.

---

## 4. Scope, stated once

* **One obligation type**: exact identification (bit or block). Nothing here bounds
  approximate or distortion-tolerant obligations; the conditional rate-distortion form of TI-2
  is the route, not taken.
* **One world family**: `W` uniform on 64 bits, or `W = Gθ` over GF(2). No claim for other
  priors, longer `L`, or non-linear structure.
* **Channels are the class, not the machine.** Every ceiling bounds all members of the class
  including machines never built; every "attained" claim is about one named machine.
* **No architecture prediction.** RV-377-121 stands at 0.0 % cross-seed agreement; this atlas
  says what a machine can achieve given its channels and nothing about which machine a search
  will build.
* **Uncharged in CL-4**: `log₂ C(L, r)` bits of index bookkeeping. **Not tight in CL-4** at
  non-perfect-code `(r, s)`: converse only, and the receipts show the registered machines well
  below it there.
* **One record carries a calibration caveat**: CL-6's closed-form check failed at 1 of 48 cells
  (z = 4.67) and was upheld on a registered 2 000-draw continuation (z = 0.41); the machine
  predicates, which test the theorem, held at every cell.
* **Same-author evaluator** (IG-4/IG-5 of the boundary theorem) remains a standing limitation
  on every claim here, as on every claim in §2 of that theorem.

Terminal register:

| terminal | value |
|---|---|
| `CHANNEL_LAW_FAMILY_VERIFIED_AT_REGISTERED_SCOPE` | **TRUE**, CL-1 … CL-7 |
| `CL4_PROPOSED_TRUNCATION_FORM_IS_A_CEILING` | **FALSE**, 8 of 8 cells |
| `CL6_PROPOSED_2_TO_MINUS_K_FORM_IS_A_CEILING` | **FALSE**, analytically (binary answer) |
| `UNOCCUPIED_CHANNEL_CLASSES_DERIVED` | 4 (RV-377-135 … 138), **NOT RUN** |
| `ARCHITECTURE_PREDICTED` | **FALSE** (RV-377-121 stands) |
