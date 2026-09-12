# GMI novel-domain hypotheses N8 and N11 — executed exact microscopes and bounded-reduction verdicts (V1)

Status: **EXECUTED REDUCTION MICROSCOPES — NO NEW DOMAIN IS CLAIMED IN THIS DOCUMENT.**
Issue: #422 (Track B). Branch: `claude/gmi-domain-n8-n11`.
Companions: `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` (domain criterion §2, domain-novelty criterion §14),
`GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` (§0 the reduction preorder, §2 the per-candidate method),
`gmi_microscope/dn_autocatalytic.py`, `gmi_microscope/dn_obstruction.py`,
`microscopes/results/STAGE_DN_V28_N8_AUTOCATALYTIC.json`,
`microscopes/results/STAGE_DN_V29_N11_OBSTRUCTION.json`,
`microscopes/results/STAGE_DN_V30_N11_OBSTRUCTION_R2.json`,
`REVIVAL_LEDGER_N8_N11.jsonl` (RV-377-052, RV-377-053, RV-377-054).

---

## 0. Provenance of the hypothesis specs — a disclosed instrument note

The brief directed this lane to read `GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md` (N8 and N11 sections),
`GMI_NOVEL_DOMAIN_THEOREMS_V1.md`, `run_gmi_novel_domain_exact_microscope_v1.py`,
`GMI_NEW_DOMAIN_HARDENING_PROGRAMME_V1.md` and `GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md`.
**None of those five files exists** on the parent branch `claude/gmi-d0-d1-research-dnbp8i`, on this
branch, or on any other remote branch of the repository (checked by `git ls-remote` plus a content
search of the working tree); the parent session has not pushed them. The terminal
`NOVEL_DOMAIN_EXACT_FINITE_THEOREM_LAYER_GREEN` is likewise unavailable here, so this lane could not
calibrate against it and does not claim to go beyond a layer it could not read.

The N8 and N11 hypothesis specs executed here are therefore **reconstructed from the worker directive**,
in the eight fields the directive names (carrier, native operators, natural complexity coordinate,
predicted niche, capability hypothesis, weak regime, parent attacks, domain discriminator). Each spec
is stated in full in its module docstring and reproduced in §1 and §2 below. Everything downstream of
the spec — the ecologies, rows, charging, receipts and verdicts — is this lane's own executed work and
stands on its own. What is *not* claimed: that these specs are the upstream document's specs. If the
upstream document lands and differs, the verdicts must be re-derived against it.

The documents that **were** available and used as written: `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §2
and §14, `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` §0 and §2, `gmi_microscope/dc_vsa.py`,
`gmi_microscope/dc_energy.py` (including its two-instrument `Arith` pattern),
`gmi_microscope/core.py`, `gmi_microscope/bases.py`, and `REVIVAL_LEDGER.jsonl` records RV-377-044
and RV-377-045 (the exact record format, followed field for field in the new ledger file).

`REVIVAL_LEDGER.jsonl` is **not touched**; the new records live in `REVIVAL_LEDGER_N8_N11.jsonl`.

---

## 1. N8 — Constructive / Autocatalytic Intelligence

### 1.1 Carrier, law, coordinate

| field | as executed |
|---|---|
| carrier | a **construction set**: seed artifacts + composition rules + the set built so far. Sufficient cognitive state is seeds + rules; the built set is the developmental body, and **products re-enter as reagents**. |
| native operators | `BUILD(u, v)` (apply a rule to two already-built artifacts), `CLOSE` (one round of BUILD over the whole built set, products re-entering), `MEMBER` (is this artifact built?). |
| complexity coordinate | the artifact-size cap `L`, which grows the closure `|C(L)|` exponentially while seeds and rules stay fixed. |
| predicted niche | obligations whose answer set is exponentially larger than the generating rule set, queried by constructibility of artifacts never shown. |
| capability hypothesis | exact decision of constructibility, described by the rule set rather than the answer set, served without re-deriving per query. |
| weak regime | short reuse horizons — the closure must be paid for before the first query. |
| parent attacks | **D5/D4** a derivation search testing candidates one by one with no reuse; **D2** a memory/table row *given the whole closure*. |
| domain discriminator | does a bounded semantics-preserving reduction to D2/D5 exist, and is its lifecycle burden qualitatively different? |

**Ecology `E_construct(L)`.** Artifacts are bit strings of length ≤ `L`. Declared seeds `01` and `110`;
one declared rule `CONCAT(u, v) = uv` when `|uv| ≤ L`. Development streams the two seeds and then six
labelled **shallow** instances (≤ two blocks); every row sees the same events. Evaluation asks
constructibility of 8 artifacts never shown: 5 distinct **deep** closure members (≥ three blocks) and
3 non-constructible strings of the same lengths from the declared LCG. Column `B0`, every op charged
through `Machine`; membership is a real binary search with charged lexicographic comparisons (the
declared `indexed_emulation` amendment), used identically by every row that stores artifacts. θ = 0.85.

**Rows.** `AUTOCAT_EAGER` (candidate, CLOSE to a fixed point in development) · `AUTOCAT_LAZY`
(candidate, seeds + rule only, closure rebuilt per query) · `SEARCH_DERIV` (D5/D4 parent) ·
`TABLE_FULL` (D2 parent, granted the closure) · `TABLE_SEEN` (D2 parent, development sample only) ·
`AUTOCAT_NOFEED` (**negative twin**: one BUILD round, products never re-enter).

### 1.2 Executed numbers (`STAGE_DN_V28_N8_AUTOCATALYTIC.json`, sha `3598bc2dadefe7ea…`, 2.2 s)

| L | \|C(L)\| | CLOSE rounds | cap: EAGER / LAZY / SEARCH / T_FULL / T_SEEN / NOFEED | desc EAGER = T_FULL | desc LAZY | compile EAGER / T_FULL | exec/q EAGER = T_FULL | exec/q LAZY | exec/q SEARCH |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 14 | 3 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 168 | 32 | 1077 / 184 | 15.5 | 774.1 | 259.1 |
| 10 | 26 | 4 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 364 | 36 | 5123 / 537 | 21.875 | 1523.0 | 299.1 |
| 12 | 47 | 4 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 752 | 40 | 14431 / 1427 | 30.125 | 9547.5 | 2487.3 |
| 14 | 84 | 4 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 1512 | 44 | 35739 / 3493 | 30.125 | 8570.5 | 6847.6 |
| 16 | 149 | 4 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 3129 | 50 | 82332 / 8084 | 47.875 | 31863.1 | 19251.0 |
| 18 | 263 | 5 | 1.0 / 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 6049 | 54 | 306909 / 17932 | 56.375 | 70912.5 | 47394.5 |

All costs are exact charged `Machine` ops; `desc` is information-theoretic and declared per row in the
receipt; θ = 0.85.

### 1.3 Exact developmental equality with the parent — **YES**

`AUTOCAT_EAGER`, `AUTOCAT_LAZY`, `SEARCH_DERIV` and `TABLE_FULL` share **one answer signature in all
six cells** (24 of 24 equality checks against the three parents true). Against `TABLE_FULL` the
reduction is not merely bounded but **exact at overhead factor 1.0**: identical answers, identical
description, identical serve cost in every cell. The eager candidate *is* the memory parent, differing
only in who paid to produce the array — and it is therefore **strictly dominated** and occupies the
reduced-price frontier in **no cell at no horizon** (0 of 58 frontier entries).

### 1.4 Measured growth law

- closure: `|C(L)| = 14 / 26 / 47 / 84 / 149 / 263`, with ratios at `L ≥ 12` of **1.7872 / 1.7738 / 1.7651**,
  descending toward the plastic-number square 1.7549 — exponential in the complexity coordinate.
- description separation `desc(TABLE_FULL)/desc(AUTOCAT_LAZY)` = **5.25 / 10.11 / 18.8 / 34.36 / 62.58 / 112.02**,
  strictly monotone and unbounded: the carrier's advantage is description, and it lives entirely in development.
- native-price crossover between `AUTOCAT_LAZY` and `TABLE_FULL`: **45.33 / 104.96 / 178.0 / 419.43 / 794.58 / 1498.75**
  — law L4's amortization point, growing as the closure does.
- negative twin pinned at **0.375 in every cell**: removing the feedback of products costs exactly the deep closure.

### 1.5 Claim level

> **`REDUCED_TO_PARENT(D2 × D5)`** — an *exact* serve-time reduction to the memory parent (overhead
> factor 1.0) with a D5 derivation search as the compile step. Criterion 3 fails outright at serve;
> criterion 4 is satisfied **only in the development coordinate**. A carrier whose separation lives
> entirely in development is a compiler, not a domain. Criteria 5 and 6 (neutral recovery, remint
> recurrence) remain untested. Record RV-377-052, **5 of 7 clauses**: the compile ratio is not monotone
> in `L` (it dips at `L = 16`), and `TABLE_FULL` takes the `H = 1` frontier from `L = 12` onward — both
> prediction-writing errors, no instrument defect.

---

## 2. N11 — Invariant / Obstruction Intelligence

### 2.1 Carrier, law, coordinate

| field | as executed |
|---|---|
| carrier | a finite set of **certified invariants** (annihilator/obstruction functionals) `h_1…h_d` that every registered move preserves. Sufficient cognitive state is the invariant basis, **not** the reachable set. |
| native operators | `DERIVE` (compute a basis of the move set's annihilator), `EVALUATE` (apply an invariant to an instance), `CERTIFY` (an invariant mismatch is a *proof* of unreachability — no search performed). |
| complexity coordinate | the **corank** `d = m − rank(moves)`: the number of independent obstructions. |
| predicted niche | obligations whose interesting instances are **unsatisfiable**: a search carrier must exhaust the move space to say "no"; an invariant carrier answers in `d` evaluations. |
| capability hypothesis | exact decision of reachability with serve cost independent of the search-space size `2^k`. |
| weak regime | large corank (`d` near `m`): the invariant basis becomes as large as the reachable-set description. |
| parent attacks | **D5** a program-search row testing candidate move combinations one by one; **D1** a dense-coefficient row carrying the row-echelon basis of the move span. |
| domain discriminator | does a bounded semantics-preserving reduction to D1/D5 exist, and is its lifecycle burden *qualitatively* different? |

**Ecology `E_obstruct(m, k, d)`** over GF(2)^m. `d` hidden check functionals are declared from the LCG
and normalized so check *i* owns pivot bit *i*; `m − d` **independent** moves are drawn inside their
common kernel (rejection on rank) and the remaining `k − (m − d)` moves are declared XOR combinations
of those. **Rank is therefore `m − d` and corank exactly `d` for every `k`** (confirmed by the measured
rank in all ten cells), so the k-sweep varies the search-space size `2^k` *alone*. Development streams
the `k` moves and then six labelled instances; every row sees the same events. Evaluation asks
instances never seen, the **majority unsatisfiable** (5 of 8 in V29; 10 of 16 in the V30 re-run).
Column `B0`, every op charged; θ = 0.85; declared `SEARCH_ENUM` node budget 65536, on exhaustion the
row returns `−1` ("no decision", counted incorrect) so it is never credited with a lucky default.

**Rows.** `OBSTRUCT` (candidate) · `DENSE_RREF` (strongest D1 parent) · `SEARCH_ENUM` (strongest D5
parent, exhaustion cost **measured**, Gray-code order) · `TABLE_SEEN` (D2 memory parent) ·
`OBSTRUCT_NOCERT` (**negative twin**: DERIVE/CERTIFY removed — `d` functionals of the same size drawn
from the LCG instead of derived from the moves).

### 2.2 Executed numbers (`STAGE_DN_V29_N11_OBSTRUCTION.json`, sha `6f65598421042f2c…`, 4 min 7 s)

| cell | rank / corank | cap: OBSTRUCT / DENSE / SEARCH / T_SEEN / NOCERT | desc OBSTRUCT / DENSE / SEARCH | exec/q OBSTRUCT / DENSE | exec per **unsat** query SEARCH |
|---|---|---|---|---|---|
| m10 d2 k8 | 8 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.625 | 20 / 80 / 80 | 44 / 68 | 7 670 |
| m10 d2 k10 | 8 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.625 | 20 / 80 / 100 | 44 / 64.25 | 30 710 |
| m10 d2 k12 | 8 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.5 | 20 / 80 / 120 | 44 / 68 | 122 870 |
| m10 d2 k14 | 8 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.5 | 20 / 80 / 140 | 44 / 59.25 | 491 510 |
| m10 d2 k16 | 8 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.375 | 20 / 80 / 160 | 44 / 68 | 1 966 070 |
| m16 d2 k16 | 14 / 2 | 1.0 / 1.0 / 1.0 / 0.0 / 0.5 | 32 / 224 / 256 | 68 / 152 | 3 145 712 |
| m24 d2 k24 | 22 / 2 | 1.0 / 1.0 / **0.0** / 0.0 / 0.375 | 48 / 528 / 576 | 100 / 331 | 4 718 640 *(budget)* |
| m32 d2 k32 | 30 / 2 | 1.0 / 1.0 / **0.0** / 0.0 / **0.875** | 64 / 960 / 1024 | 132 / 662 | 6 291 520 *(budget)* |
| m48 d2 k48 | 46 / 2 | 1.0 / 1.0 / **0.0** / 0.0 / 0.625 | 96 / 2208 / 2304 | 196 / 1144 | 9 437 280 *(budget)* |
| **m32 d16 k32** (weak) | 16 / 16 | 1.0 / 1.0 / 0.375 / 0.0 / 0.625 | **512 / 512** / 1024 | **1056 / 360** | 6 291 520 *(budget)* |

### 2.3 Exact developmental equality with the parent — **YES**

`OBSTRUCT` and `DENSE_RREF` return **identical answers with capability exactly 1.0 in all ten cells**
(10 of 10 signature equalities), in both the V29 and V30 runs. Over GF(2) the row space of the moves
and the null space of the derived annihilator are orthogonal complements, so the two rows evaluate one
predicate in complementary coordinates. **A bounded semantics-preserving reduction to D1 exists;
criterion 3 fails.** `SEARCH_ENUM` shares the signature in exactly the six in-budget cells and in none
of the four over-budget ones.

### 2.4 Measured growth law — the constant-vs-exponential separation

Two exact closed forms, each reproduced **bit-identically across two independently sized evaluation
sets** (V29 at 8 instances, V30 at 16):

```
exec_per_query(OBSTRUCT)                 = d * (2m + 2)          independent of k
exec_per_unsat_query(SEARCH_ENUM)        = 2m + 3m * (2^k - 1)   linear in the search space
```

measured over five instance sizes at fixed `m = 10`, `d = 2`:

| k | search space 2^k | OBSTRUCT exec / unsat query | SEARCH_ENUM exec / unsat query | ratio | successive ratio |
|---|---|---|---|---|---|
| 8 | 256 | 44 | 7 670 | **174.3182** | — |
| 10 | 1 024 | 44 | 30 710 | **697.9545** | 4.0043 |
| 12 | 4 096 | 44 | 122 870 | **2 792.50** | 4.0010 |
| 14 | 16 384 | 44 | 491 510 | **11 170.6818** | 4.0003 |
| 16 | 65 536 | 44 | 1 966 070 | **44 683.4091** | 4.0001 |

The candidate's burden is **constant** in the search-space size and the parent's is **exactly linear in
2^k** — the ratio quadruples for every 2 bits. That is domain criterion 4's "qualitatively different
asymptotic burden", **measured and not assumed** (the parent's exhaustion is charged op by op).

**But it is a separation against a strictly dominated parent.** Against the *strongest* parent the
separation is only polynomial:

| m (corank 2) | desc DENSE / desc OBSTRUCT = (m−d)/d | exec/q DENSE ÷ exec/q OBSTRUCT |
|---|---|---|
| 16 | **7** (exact) | 2.2353 |
| 24 | **11** (exact) | 3.3100 |
| 32 | **15** (exact) | 5.0152 |
| 48 | **23** (exact) | 5.8367 |

`Θ(d·m)` for the candidate against `Θ(m²)` for the parent at fixed corank — a polynomial-degree
separation with *identical answers*, i.e. a bounded reduction with a real but non-qualitative overhead.

### 2.5 The hypothesis's own declared weak regime — confirmed

At `m32_d16_k32` (corank = m/2, the self-dual point) the two descriptions are **exactly equal (512 bits
each)**, the candidate's serve cost **exceeds** the parent's (1056 vs 360), the reduced-price frontier is
**`DENSE_RREF` alone at every horizon**, and under the declared native price the two rows **tie exactly**
at every horizon (native cost 16 each, desc 512 each). The carrier's advantage is exactly the dimension
ratio `(m−d)/d` of the two dual presentations and vanishes precisely where the hypothesis said it would.

### 2.6 Claim level

> **`REDUCED_TO_PARENT(D1, annihilator/dual presentation)`** at scope. Criteria 1, 2 and 4 hold — a
> distinct carrier, a distinct law, and a measured constant-against-exponential burden difference
> against the search parent. Criterion 3 **fails** against D1 with exact answer equality in 10 of 10
> cells. The executed exponential separation is recorded as a separation against a parent that the
> dense row beats by four to six orders of magnitude on the same instances. Criteria 5 and 6 remain
> untested. Records RV-377-053 (**5 of 8 clauses**) and RV-377-054 (**7 of 10 clauses**).

---

## 3. What the two microscopes add to the theory

1. **A parent-maximality clause for the domain criterion.** N11's exponential separation is genuine,
   measured, and worth nothing for domain status, because the parent it beats is itself beaten by four
   to six orders of magnitude by a parent that matches the candidate answer for answer. Criterion 4 may
   only be certified against a parent that is **frontier-optimal among D1–D9 on the registered
   obligation**. This is the main theory movement of this lane.
2. **Criterion 3 and criterion 4 must be evaluated separately in the development and serve
   coordinates.** N8 satisfies criterion 4 only in development (the closure a memory parent must be
   handed grows as 1.7549^L) and fails criterion 3 at serve with overhead factor exactly 1.0.
3. **Law L4 (compile amortization) gains two axes**: the artifact-size axis (N8, crossover growing with
   the closure: 45.33 → 1498.75) and the primal/dual axis (N11: description ratio `(m−d)/d`, serve ratio
   `Θ(m²)` vs `Θ(d·m)`, exact tie at `d = m/2`). This is the same law family as RV-377-044's
   structure-depth axis and RV-377-033/038's crossovers — GMI *derives* both candidates as phases of an
   existing domain rather than admitting either as a carrier.
4. **Gap DG-2 honoured.** Every emitted frontier grid extends past twice its largest finite positive
   crossover, in both price vectors, in every cell of both microscopes. No "no cell exists" statement in
   either record is checked on a truncated grid.
5. **Gap DG-3 opened and left open (`OPEN_NONBLOCKING`).** A single-draw negative twin has undeclared
   variance. At `m32_d2_k32` the twin drew two functionals that clear θ = 0.85 by chance (0.875: 10 of
   10 unsatisfiable at p = 3/4, 4 of 6 satisfiable at p = 1/4 — joint ≈ 0.2 % per cell), and since it
   carries the candidate's exact description and serve cost with **none of its derivation cost**, it
   displaces the candidate on that cell's frontier. The one minimal justified change permitted by the
   directive (enlarging the evaluation set from 8 to 16 instances, RV-377-054) was executed and
   **failed for a diagnosable reason**: twin admissibility is a property of the twin's own fixed declared
   draw, not instance-sampling noise, and a nested instance stream cannot resample it. The correct
   remedy — a declared **twin ensemble** with the capability reported as an ensemble mean and spread —
   is `REGISTERED_FOR_EXPERIMENT` (RV-377-055) and is **not executed here**. It affects one frontier cell
   of ten and no law, no closed form and no reduction verdict. It also applies retroactively to the
   single-draw twins of RV-377-044 (`VSA_NOBIND`) and RV-377-045 (`HOPFIELD_RND`).
6. **A reproduction check as a by-product.** The N11 re-run on a differently sized evaluation set
   reproduces every deterministic quantity bit-identically — both closed forms, the growth ratios to
   four decimals, the description ratio `(m−d)/d` — so the executed laws are not artifacts of one draw.

## 4. Claim-level summary

| hypothesis | exact developmental equality with a parent? | measured growth law | claim level |
|---|---|---|---|
| **N8** constructive / autocatalytic | **yes**, with `TABLE_FULL` (D2 granted the closure) in 6 of 6 cells, overhead factor **1.0** | closure `1.7549^L`; description separation 5.25 → 112.02; native-price crossover 45.33 → 1498.75 | **`REDUCED_TO_PARENT(D2 × D5)`** |
| **N11** invariant / obstruction | **yes**, with `DENSE_RREF` (D1) in 10 of 10 cells | serve `d(2m+2)` constant in `k` vs exhaustion `2m + 3m(2^k − 1)`; ratio ×4.00 per 2 bits over 5 sizes; vs the strongest parent only `(m−d)/d` = 4/7/11/15/23 | **`REDUCED_TO_PARENT(D1, annihilator/dual presentation)`** |
| domain criterion parent-maximality clause | — | — | **`PROVED_AT_SCOPE`** (as a statement about this programme's criterion, executed on ten cells) |
| gap DG-3 (single-draw negative twins) | — | — | **`OPEN_NONBLOCKING`**; remedy `REGISTERED_FOR_EXPERIMENT` |
| criteria 5 and 6 for N8 and N11 (neutral recovery, remint recurrence) | — | — | **`OPEN_NONBLOCKING`** — not attempted by this lane |

## 5. Reproduction

```bash
cd research/machine-intelligence-morphogenesis-v1
python3 -m gmi_microscope.dn_autocatalytic V28_N8_AUTOCATALYTIC      # ~2 s
python3 -m gmi_microscope.dn_obstruction    V29_N11_OBSTRUCTION      # ~4 min  (n_eval 8 — set N_EVAL=8, N_UNSAT_EVAL=5)
python3 -m gmi_microscope.dn_obstruction    V30_N11_OBSTRUCTION_R2   # ~8 min  (n_eval 16, the committed defaults)
python3 -m pytest test_gmi_microscope.py -q -k "autocatalytic or obstruction"
```

Deterministic and exactly reproducible: no wall-clock, no unseeded randomness, one declared LCG
(`1103515245, 12345`, bit 16 per draw) throughout; every op charged through `gmi_microscope.core.Machine`;
`receipt_sha256` over the receipt with the field removed.
