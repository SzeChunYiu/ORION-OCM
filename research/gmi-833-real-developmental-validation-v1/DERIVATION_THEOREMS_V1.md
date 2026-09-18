# GMI #833 — derived operator-invention and library-formation conditions
# Named-theorem note for `FREEZE_V1.md` §4

**Package:** `gmi-833-real-developmental-validation-v1`
**Executors:** `derivation_v1.py` (Route A, closed form) and
`oracle_derivation_v1.py` (Route B, explicit enumeration).
**Results:** `DERIVATION_RESULT_V1.json`, `ORACLE_DERIVATION_RESULT_V1.json`.
**Tests:** `test_derivation_v1.py` (70 tests, pass under `-I -B` and `-I -O -B`).
**Claim ceiling (inherited, not widened):**
`GMI_833_REAL_SYSTEM_UPDATE_LAW_AND_DEVELOPMENTAL_VALIDATION_AND_DERIVED_INVENTION_LIBRARY_CONDITIONS_AT_REGISTERED_SCOPE`
**Evidence level for every claim below: EV1 (deductive) + EV2 (exact bounded
certificate). Maturity M1 (theorem) — M2 (exact witness). NOT EV3, EV4, EV5;
NOT M3 and above.** Nothing here is a frozen held-out experiment, an
independent-team replication, or a real-scale prospective validation.

---

## 0. Setting and notation

`A` is a finite alphabet, `n = |A| >= 2`. `Phi(n,l) = sum_{j=1..l} n**j`,
`Phi(n,0) = 0`. `l*_G(w)` is the minimal program length for target `w` under
grammar `G`. All arithmetic is exact `int` / `fractions.Fraction`; no float
appears in any computed quantity (machine-checked by walking both result JSONs
and by a token-level scan of both executors).

**The one identity everything rests on is #897's `T3`, which is on
`origin/main` and is NOT claimed novel here:**

> the first program in the breadth-by-length, lexicographic-within-length
> enumeration whose expansion equals `w` has burden
> `B_G(w) = Phi(|A|, l*-1) + rank_{l*}(p) + 1`, `rank in [0, |A|**l* - 1]`.

Consequently a target of minimal length `l` occupies the burden interval
`[Phi(n,l-1)+1, Phi(n,l)]`, and every verdict below is **rank-free**: it uses
only the two endpoints of that interval and therefore holds at *every* rank
assignment. Route B re-derives the same endpoints by counting enumerated words
one at a time, never by evaluating `Phi`.

### 0.1 Registered domain assumptions (load-bearing)

1. **`ADMISSIBLE_PROGRAM_LENGTHS_ARE_>=1`** — `l0, l1, lL, lj >= 1`. The empty
   program is not a program; `Phi(.,0) = 0` is an interval endpoint, never a
   realizable target length. *This assumption is load-bearing twice:* it
   quarantines the 11 degenerate `l0 = 1` cells in `OI-2`, and it is what makes
   `LF-4`'s `gammastar` undefined at `lj = 2` (with `lL = 0` admissible,
   `gamma = lj` would always succeed and `gammastar` would never be undefined).
2. **`COMPRESSION_ADMISSIBILITY`** — `l1 <= l0` and `lL <= lj`. A candidate
   that lengthens the minimal program is inadmissible (hostile `H4`).
3. **`ALPHABET_GROWTH_IS_EXACTLY_ONE_SYMBOL_PER_ADMITTED_OPERATOR`** — `G0` has
   `n` symbols, `G0 u {o}` has `n+1`, a shared library of `k` members has `n+k`.
4. **`CHARGES_ARE_NONNEGATIVE`** — `D(o) >= 0`, `len(body) >= 0`, `kappa >= 0`.
5. **`RANK_FREE`** — no verdict may depend on the rank coordinate of `T3`.

### 0.2 Bands (the frame every verdict is stated in)

Comparing `(n_new, l_new)` against `(n_old, l_old)`:

- `GUARANTEED_REDUCTION` iff `Phi(n_new,l_new) <= Phi(n_old,l_old-1)`
  (new interval entirely below the old);
- `GUARANTEED_INCREASE` iff `Phi(n_new,l_new-1) >= Phi(n_old,l_old)`
  (new interval entirely above the old);
- `RANK_DECIDED` otherwise (intervals overlap).

---

## 1. Parent ownership — what is NOT claimed novel here

### 1.1 #897 (merged, `research/gmi-833-g0-grammar-growth-v1/`) owns the BUILT mechanism

#897 owns, and this tranche claims **no** novelty in:

- the `T3` burden identity `B_G(w) = Phi(n, l*-1) + rank + 1` — **we rest on it**;
- `T1`'s conservative monotone extension and the `RECURSIVE_LIBRARY_CYCLE`
  fail-closed admission API;
- `T2`/`INV-1`: the deterministic corpus-only invention rule
  `gain = o(b-1) - b - kappa > 0`, the `m1 -> a b` / `m2 -> m1 m1` admissions,
  the charge `K_total(L) = sum_m (len(body_m) + kappa)`, the derived
  `kappa = 1` ablation, the saturation depth `D_reg = S_0 = 23`, and the
  measured held-out burden `50,052 -> 1,307`;
- the Section E row `Implement recursive library formation / primitive
  invention.`, whose verb is *Implement*.

`GRAMMAR_GROWTH_OWNED_HERE`, `LIBRARY_IMPLEMENTATION_NOVEL_HERE` and
`INVENTION_MECHANISM_NOVEL_HERE` are forbidden promotions of this freeze and
are not asserted anywhere in this package.

**The residual actually claimed here** is: (a) the *condition* under which
admitting an operator pays in the burden frame, and the exact map of where
#897's corpus rule and the burden frame **disagree** (`OI-1`…`OI-4`); and
(b) the comparison **one shared library of `k` members versus `k` separate
single-member grammars** (`LF-1`…`LF-4`, `IND-1`, `IND-2`).

### 1.2 #1019 (`research/gmi-833-developmental-reuse-v1/`, UNMERGED branch `origin/research/833-l-dev`) — concurrent prior art, disclosed

#1019 owns `REP-1` (the rank-free band on `Phi` comparing `G1 = G0 u L` against
`G0`) and `REP-2` (the portfolio net with `K_total` charged). Its comparison is
**library against no library**. The comparison here is **shared library against
`k` separate keeps** — a different pair of alphabets (`n+k` vs `n+1`, not
`n'` vs `n`) — and by `LF-2` it is charge-free, which is exactly where `REP-2`,
in which `K_total` is decisive, has nothing to say.

**No step of §4 or of this note depends on #1019.** The only parent load-bearing
here is #897's `T3`, which is on `origin/main`. This tranche claims **no part**
of the three rows #1019 claims:
`- [ ] Derive representation changes that reduce future search cost.`,
`- [ ] Compare mutation, local search, GP/CGP, evolutionary, gradient, NAS-like,
and meta-search dynamics.`, and
`- [ ] Test whether P4 recursive grammar growth discovers mechanisms absent from
G0.` — i.e. `REPRESENTATION_CHANGE_ROW_OWNED_HERE`,
`SEARCH_DYNAMICS_COMPARISON_OWNED_HERE` and `P4_NOVELTY_ROW_OWNED_HERE` remain
forbidden and unasserted. Because #1019 is unmerged and independently derived
the band frame, the `GUARANTEED_REDUCTION` / `GUARANTEED_INCREASE` /
`RANK_DECIDED` trichotomy must be read as **concurrent**, not as a result
originating here.

---

## 2. Named results

Each block carries the thirteen `result_required_fields` of
`research/gmi-833-foundation-v1/FOUNDATION_SCHEMA_V1.json`:
`claim_id`, `statement`, `domain`, `quantifiers`, `assumptions`, `proof_mode`,
`evidence_level`, `maturity_level`, `falsifiers`, `strongest_parents`,
`prior_disclosure`, `forbidden_extrapolations`, `open_gaps`.

---

### `OI-1` — the invention affordance

- **claim_id:** `OI-1`
- **statement:** For a registered workload `T` of targets with exact rational
  weights `w`, minimal length `l0` under `G0` (alphabet `n`) and `l1` under
  `G0 u {o}` (alphabet `n+1`), define
  `Saving = sum_{l1 < l0} w * (Phi(n,l0-1) + 1 - Phi(n+1,l1))`,
  `Tax = sum_{l1 = l0} w * (Phi(n+1,l0) - Phi(n,l0-1) - 1)` and
  `Theta_inv(o) = Saving - Tax`. Then admitting `o` **strictly reduces total
  priced burden at every rank assignment** iff
  `D(o) + (len(body) + kappa) < Theta_inv(o)`.
  `Saving` is the guaranteed (worst-case) gain on compressed targets: old
  minimum burden minus new maximum burden. `Tax` is the guaranteed worst-case
  loss on untouched targets: new maximum minus old minimum. `Theta_inv` is
  therefore the exact rank-free charge ceiling.
- **domain:** finite alphabets `n >= 2`; finite weighted target workloads with
  rational weights; nonnegative integer charges.
- **quantifiers:** `forall[D]` for the threshold identity;
  `forall_fin[U]` over the registered 6-workload census (`W1`…`W6`).
- **assumptions:** §0.1 (1)–(5); the price vector is prospectively frozen per
  foundation `R-1`/`R-2`; charges are carried in the 14-coordinate lifecycle
  vector (`search_discovery`, `build_acquisition`, `maintenance`).
- **proof_mode:** deductive from `T3`'s interval endpoints, plus an exhaustive
  exact census; Route B re-derives `W1` from actual macro expansion.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** a workload with `D + len(body) + kappa < Theta_inv` on which
  some rank assignment leaves total burden unreduced; or a workload with
  `D + len(body) + kappa >= Theta_inv` on which admission strictly reduces
  burden at *every* rank assignment; any float in the computed `Theta_inv`.
- **strongest_parents:** #897 `T3` (burden identity) — merged, load-bearing;
  #897 `K_total` (charge form). #1019 `REP-2` — concurrent, not depended on.
- **prior_disclosure:** #1019 independently derives a band frame over the same
  `Phi`; `Theta_inv` as an explicit charge ceiling with a Saving/Tax split over
  a weighted workload is the residual claimed here.
- **forbidden_extrapolations:** `INVENTION_MECHANISM_NOVEL_HERE`;
  `CONTINUOUS_OR_INFINITE_SCOPE`; any reading in which `Theta_inv > charge` is
  claimed *necessary* for a burden reduction at *some* rank (it is a worst-case
  sufficiency threshold, and `RANK_DECIDED` cells can still improve on a
  favourable draw).
- **open_gaps:** `Theta_inv` is rank-free and therefore conservative; the
  rank-sensitive expected-burden threshold is not derived here.
- **Certificate:** `W1` (`n=2`, one target, `l0=8 -> l1=2`, weight 1):
  `Saving = Phi(2,7)+1 - Phi(3,2) = 255 - 12 = 243`, `Tax = 0`,
  `Theta_inv = 243/1`, charge `D+len+kappa = 1+4+1 = 6 < 243` → **PAYS**.
  `W2` (`gamma = 0`) gives `Saving = 0`, `Theta_inv = -105/1` → cannot pay.
  `W6` (`gamma = 1` only) gives `Theta_inv = -965/1` → cannot pay, as `OI-2`
  requires. Route B recovers `l0 = 8`, `l1 = 2`, `Theta_inv = 243` for `W1` by
  brute-force macro expansion of `m -> abab` over target `abababab`
  (enumerated burdens `340` under `G0` and `12` under `G0 u {m}`).

---

### `OI-2` — one-symbol compression is never guaranteed to pay

- **claim_id:** `OI-2`
- **statement:** For every `n >= 2` and every `l >= 1`,
  `Phi(n+1,l-1) >= Phi(n,l-1)`. Hence, on the admissible domain `l0 >= 2`, a
  compression of depth `gamma = 1` is **never** in the guaranteed-reduction
  band `Phi(n+1, l0-gamma) <= Phi(n, l0-1)`, whatever the charge.
- **domain:** `forall[D]` over all `n >= 2, l >= 1`; certified
  `forall_fin[U]` on `n in 2..12`, `l in 1..14` (154 cells).
- **quantifiers:** `forall[D]` for the inequality; `forall_fin[U]` for the
  census certificate. These are **not** interchangeable and are not rewritten
  as one another anywhere.
- **assumptions:** §0.1 (1)–(3), (5).
- **proof_mode:** term-by-term deduction `(n+1)**j >= n**j` for every `j >= 1`,
  summed; plus exhaustive census.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** any `(n,l)` with `Phi(n+1,l-1) < Phi(n,l-1)`; any admissible
  `(n, l0 >= 2)` whose `gamma = 1` verdict is `GUARANTEED_REDUCTION`.
- **strongest_parents:** #897 `T3`. #1019 `REP-1` (concurrent band frame).
- **prior_disclosure:** the inequality itself is elementary; what is claimed is
  its exact consequence in the band frame plus the certified exception set.
- **forbidden_extrapolations:** a `gamma = 1` operator can still be *useful* —
  `RANK_DECIDED` is the common verdict (131 of 143 admissible census cells) and
  simply means the guarantee is unavailable, not that the operator loses.
- **open_gaps:** none at this scope.
- **Certificate and the honest exception:** 0 inequality violations in 154
  cells. The band condition `Phi(n+1,l0-1) <= Phi(n,l0-1)` is satisfiable only
  with equality, i.e. only at `l0 - 1 = 0`. There are exactly **11 such cells**
  — one per `n in 2..12`, all at `l0 = 1` — and each has `l1 = 0`, the empty
  program, excluded by assumption §0.1(1). The 11 cells are reported in the
  result JSON, not removed from the census. Admissible `gamma = 1` verdicts:
  `GUARANTEED_REDUCTION 0`, `GUARANTEED_INCREASE 12`, `RANK_DECIDED 131`.
  Route B confirms 0 guaranteed-reduction cells by enumeration on `n in 2..4`,
  `l0 in 2..6` (15 cells, 15/15 agreement with Route A).

---

### `OI-3` — guaranteed-loss depth (PARTLY FALSE AS FROZEN; corrected)

- **claim_id:** `OI-3`
- **statement as frozen (§4.3):** "`L*(n) := min{ l : Phi(n+1,l-1) >= Phi(n,l) }`
  exists for every `n >= 2`, is computed exactly on the registered range, and is
  bracketed `n+2 <= L*(n) <= 1 + ceil(n(n^2-n+1)/(n-1))`. At depth `>= L*(n)` a
  `gamma = 1` admission strictly loses at **every** nonnegative charge — the
  matched converse."
- **verdict:** the **definition and the bracket are TRUE**; the **`gamma = 1`
  consequence is FALSE as frozen**. Reported as false, with counterexamples,
  and repaired below. The frozen definition of `Lstar` is *not* edited (§6 of
  the freeze forbids post-hoc edits of a frozen threshold); a new companion
  quantity `Mstar` is introduced to carry the corrected converse.
- **corrected statement (what is true):**
  1. `Lstar(n) = min{ l : Phi(n+1,l-1) >= Phi(n,l) }` is exactly the
     **`gamma = 0` guaranteed-loss depth**: for every `l >= Lstar(n)`,
     `band(n,l -> n+1,l) = GUARANTEED_INCREASE`, i.e. an operator that
     compresses nothing strictly loses at every nonnegative charge. (The frozen
     condition `Phi(n+1,l-1) >= Phi(n,l)` *is* the `GUARANTEED_INCREASE`
     predicate `Phi(n+1,l1-1) >= Phi(n,l0)` at `l1 = l0 = l`.)
  2. The **`gamma = 1` guaranteed-loss depth** is the strictly larger companion
     `Mstar(n) = min{ l >= 2 : Phi(n+1,l-2) >= Phi(n,l) }`: for every
     `l >= Mstar(n)`, `band(n,l -> n+1,l-1) = GUARANTEED_INCREASE`.
  3. `Mstar(n) > Lstar(n)` at every `n in 2..24`, and **`Mstar` satisfies the
     same frozen bracket** `n+2 <= Mstar(n) <= 1 + ceil(n(n^2-n+1)/(n-1))`.
- **domain:** finite alphabets `n in 2..24`; integer program lengths in the
  probe window `[Lstar(n), Mstar(n)+24]`.
- **quantifiers:** `forall_fin[U]` over that box for the tables, the bracket
  and both converses. No `forall[D]` claim is made for the bracket.
- **assumptions:** §0.1 (1)–(3), (5); the upper bound uses exact integer
  ceiling division (`-((-a)//b)`), never `math.ceil` on a float.
- **proof_mode:** exact integer computation plus exhaustive census; the two
  converses are certified cell-by-cell past each threshold.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** an `n` with `Lstar(n)` or `Mstar(n)` outside the bracket; a
  cell `l >= Lstar(n)` whose `gamma = 0` verdict is not `GUARANTEED_INCREASE`;
  a cell `l >= Mstar(n)` whose `gamma = 1` verdict is not `GUARANTEED_INCREASE`.
- **strongest_parents:** #897 `T3`. #1019 `REP-1` (concurrent).
- **prior_disclosure:** #1019's `REP-1` independently derives the same band
  trichotomy over `Phi` on the unmerged branch `origin/research/833-l-dev`;
  the `Lstar` / `Mstar` split, the bracket certificate and the falsification of
  the frozen `gamma = 1` consequence are the residual claimed here, and none of
  them depends on #1019.
- **forbidden_extrapolations:** `Lstar` must **not** be quoted as a `gamma = 1`
  guaranteed-loss depth; no extrapolation of either table beyond `n <= 24`;
  `CONTINUOUS_OR_INFINITE_SCOPE`.
- **open_gaps:** a closed-form asymptotic for `Mstar(n)` is not derived; only
  the exact table and the (loose) shared bracket are certified.
- **Certificate.** 0 bracket violations over `n in 2..24` for **both** `Lstar`
  and `Mstar`. **860** counterexample cells to the frozen `gamma = 1`
  consequence, i.e. cells with `Lstar(n) <= l0 < Mstar(n)` whose `gamma = 1`
  verdict is `RANK_DECIDED`. Lexicographically first: `n = 2, l0 = 4, l1 = 3`,
  `Phi(3,2) = 12`, `Phi(2,4) = 30`, `12 >= 30` is false → `RANK_DECIDED`,
  while `l0 = 4 >= Lstar(2) = 4`. Corrected converses: 1435 `gamma = 0` cells
  and 575 `gamma = 1` cells certified `GUARANTEED_INCREASE`, **0 failures each**.

| `n` | `Lstar` | `Mstar` | lower `n+2` | upper `1+ceil(n(n²-n+1)/(n-1))` |
|---|---|---|---|---|
| 2 | 4 | 7 | 4 | 7 |
| 3 | 6 | 11 | 5 | 12 |
| 4 | 8 | 15 | 6 | 19 |
| 5 | 11 | 20 | 7 | 28 |
| 6 | 13 | 26 | 8 | 39 |
| 7 | 16 | 32 | 9 | 52 |
| 8 | 19 | 38 | 10 | 67 |
| 9 | 22 | 44 | 11 | 84 |
| 10 | 26 | 51 | 12 | 103 |
| 11 | 29 | 58 | 13 | 124 |
| 12 | 33 | 65 | 14 | 147 |
| 13 | 36 | 72 | 15 | 172 |
| 14 | 40 | 79 | 16 | 199 |
| 15 | 44 | 86 | 17 | 228 |
| 16 | 47 | 94 | 18 | 259 |
| 17 | 51 | 102 | 19 | 292 |
| 18 | 55 | 109 | 20 | 327 |
| 19 | 59 | 117 | 21 | 364 |
| 20 | 63 | 125 | 22 | 403 |
| 21 | 67 | 133 | 23 | 444 |
| 22 | 71 | 142 | 24 | 487 |
| 23 | 75 | 150 | 25 | 532 |
| 24 | 79 | 158 | 26 | 579 |

Route B reproduces `Lstar(2,3,4) = 4, 6, 8` and `Mstar(2) = 7` by enumeration
and independently records `gamma0_verdict_at_Lstar = GUARANTEED_INCREASE`
alongside `gamma1_verdict_at_Lstar = RANK_DECIDED` at every reachable `n` —
i.e. the falsification is visible from both routes. `Mstar(3) = 11` would need
`sum_{j<=11} 4**j = 5,592,404` enumerated words, above the registered Route-B
budget of 1,000,000 words per scan; that cell is reported `OUT_OF_BUDGET` and
is **not** filled in by any closed form.

---

### `OI-4` — frame divergence (EARNED-BY-COUNTEREXAMPLE)

- **claim_id:** `OI-4`
- **statement:** #897's corpus-symbol admission rule
  `gain = occ*(b-1) - b - kappa > 0` is **neither sufficient nor necessary**
  for burden reduction in the `Phi` frame.
- **domain:** the registered census `n in 2..6`, `occ in 1..8`, `b in 1..6`,
  `kappa in 0..3`, `l0 in 1..10`, `1 <= l1 <= l0` — **52,800 cells**, scanned
  in lexicographic `(n, occ, b, kappa, l0, l1)` order.
- **quantifiers:** `forall_fin[U]` over that census for the counts and the
  criterion certificate; `exists_fin[U]` for the three witnesses, which are
  EARNED-BY-COUNTEREXAMPLE, i.e. existential and exact.
- **assumptions:** §0.1 (1)–(5); #897's rule is read exactly as its `T2` states
  it, with `occ` the greedy non-overlapping occurrence count.
- **proof_mode:** exhaustive finite search for witnesses + deductive repair.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M2`.
- **falsifiers:** a proof that no such witness exists in the census (would
  contradict the printed numbers); a witness whose band verdict is
  mis-computed (Route B re-derives all three by enumeration).
- **strongest_parents:** #897 `T2`/`INV-1` (the rule being tested — its
  correctness *in the corpus-cost frame* is not disputed here), #897 `T3`.
- **prior_disclosure:** #897 never claimed its rule was a burden-frame
  criterion; this result maps the disagreement, it does not impeach #897 at
  its own scope.
- **forbidden_extrapolations:** this is **not** a claim that #897's admissions
  were wrong — in #897's frozen corpus-cost frame they are correct, and its
  measured `50,052 -> 1,307` stands. It is a claim about what the rule does and
  does not certify **in the burden frame**. `INVENTION_MECHANISM_NOVEL_HERE`.
- **open_gaps:** the census is finite; no claim is made for `n > 6`, `occ > 8`,
  `b > 6`, `kappa > 3`, `l0 > 10`.

**Witness (i) — NOT SUFFICIENT**, lexicographically first:
`n = 2, occ = 2, b = 3, kappa = 0, l0 = 4, l1 = 4` (`gamma = 0`).
`gain = 2*(3-1) - 3 - 0 = 1 > 0` → #897 admits. Burden intervals:
`G0 = [15, 30]`, `G0 u {o} = [40, 120]`; `Phi(3,3) = 39 >= Phi(2,4) = 30` →
**`GUARANTEED_INCREASE`**. Admission strictly loses at every nonnegative charge.
2,583 such cells in the census.

**Witness (i′) — NOT SUFFICIENT even with strict compression** (`gamma >= 1`,
registered as a secondary witness because the lex-first one is `gamma = 0`):
`n = 2, occ = 2, b = 3, kappa = 0, l0 = 7, l1 = 6` (`gamma = 1`).
`gain = 1 > 0`; intervals `G0 = [127, 254]`, `G0 u {o} = [364, 1092]`;
`Phi(3,5) = 363 >= Phi(2,7) = 254` → **`GUARANTEED_INCREASE`**. 738 such cells.
This is exactly `OI-3`'s corrected converse at `l0 = 7 = Mstar(2)`.

**Witness (ii) — NOT NECESSARY**, lexicographically first:
`n = 2, occ = 1, b = 1, kappa = 0, l0 = 3, l1 = 1` (`gamma = 2`).
`gain = 1*(1-1) - 1 - 0 = -1 <= 0` → #897 rejects (its own `o = 1` corollary).
Intervals `G0 = [7, 14]`, `G0 u {o} = [1, 3]`; `Phi(3,1) = 3 <= Phi(2,2) = 6` →
**`GUARANTEED_REDUCTION`**. 11,316 such cells.

**Exact structural side-condition that repairs it.** `gain > 0` must be
**REPLACED, not qualified**:

> the burden-frame criterion that is both **necessary and sufficient** for
> `GUARANTEED_REDUCTION` is `gamma >= gammastar_inv(n, l0)` **alone**, where
> `gamma = l0 - l1` and
> `gammastar_inv(n,l0) = min{ gamma in 0..l0-1 : Phi(n+1, l0-gamma) <= Phi(n, l0-1) }`
> (`None` if no admissible `gamma` works),

together with the matched refusals from `OI-3`: refuse admission whenever
`gamma = 0` and `l0 >= Lstar(n)`, and whenever `gamma = 1` and `l0 >= Mstar(n)`.

**Why conjoining will not do.** `gain > 0 AND gamma >= gammastar_inv` removes
the 2,583 over-admissions but retains **all 11,316 under-admissions** — cells
with `gain <= 0` that are nonetheless `GUARANTEED_REDUCTION`, including the
lex-first witness `(2,1,1,0,3,1)` above — because a conjunct can only ever
refuse *more*. The executor records `conjoined_rule_under_admissions = 11,316`
for exactly this reason.

By `OI-2`, `gammastar_inv(n,l0) >= 2` for every `l0 >= 2`, so the criterion
**contains** the `gamma >= 2` requirement (`min gammastar_inv = 2` wherever
defined). The criterion fixes the **sign** of the burden change only; strict
*payment* additionally requires `OI-1`'s charge test
`D(o) + len(body) + kappa < Theta_inv(o)`.

**What the 0/0 certificate does and does not show.** The census reports
`criterion_false_positive_count = 0` and `criterion_false_negative_count = 0`
over all 52,800 cells. Because `gamma >= gammastar_inv(n,l0)` *is* the
`GUARANTEED_REDUCTION` predicate re-parameterized in `gamma`, those counts
**cannot come out otherwise** — the scan is **not** independent empirical
support for the criterion. What it actually certifies is (a) that the predicate
is **upward-closed in `gamma`** (`upward_closure_violation_count = 0`, so
`gammastar_inv` is a genuine threshold and not merely a first hit) and (b) that
the two implementations — the `min`-search and direct band evaluation — agree
on every census cell. Recorded here rather than left to be misread as evidence
the criterion was tested against a possible failure.

---

### `LF-1` — library-versus-separate band

- **claim_id:** `LF-1`
- **statement:** For a shared LIBRARY (alphabet `n+k`, minimal length `lL`)
  versus `k` SEPARATE single-member grammars (alphabet `n+1`, minimal length
  `lj`): `LIBRARY_GUARANTEED_BETTER iff Phi(n+k,lL) <= Phi(n+1,lj-1)`;
  `LIBRARY_GUARANTEED_WORSE iff Phi(n+k,lL-1) >= Phi(n+1,lj)`; else
  `RANK_DECIDED`. The two bands are **mutually exclusive**.
- **domain:** finite alphabets `n in 2..8`, library sizes `k in 2..6`,
  admissible lengths `1 <= lL <= lj <= 12` — **2,730 cells**.
- **quantifiers:** `forall[D]` for mutual exclusivity; `forall_fin[U]` for the
  band counts over that census.
- **assumptions:** §0.1 (1)–(5); by `LF-2` the comparison is charge-free.
- **proof_mode:** deductive (exclusivity) + exhaustive census; Route A also
  cross-checks every cell against a generic `band()` implementation.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** any cell satisfying both band predicates; any disagreement
  between the closed-form verdict and the enumerated-endpoint verdict.
- **strongest_parents:** #897 `T3`, #897 `T4` (widened-frontier regression).
  #1019 `REP-1` — concurrent, different comparison, not depended on.
- **prior_disclosure:** the `n+k` vs `n+1` comparison is the residual; the band
  *shape* is concurrent with #1019's `REP-1`.
- **forbidden_extrapolations:** `LIBRARY_IMPLEMENTATION_NOVEL_HERE`;
  `SECTION_L_COMPLETE`; `CONTINUOUS_OR_INFINITE_SCOPE`; no extrapolation past
  `n = 8`, `k = 6`, `lj = 12`.
- **open_gaps:** heterogeneous member sets (different `lL` per target) are not
  enumerated; the census fixes one `(lL, lj)` pair per cell.
- **Certificate:** 2,730 cells → **1,653 `LIBRARY_GUARANTEED_BETTER`,
  336 `LIBRARY_GUARANTEED_WORSE`, 741 `RANK_DECIDED`, 0 band collisions**;
  0 internal cross-check mismatches.
  *Proof of exclusivity.* If both held then
  `Phi(n+k,lL-1) >= Phi(n+1,lj) > Phi(n+1,lj-1) >= Phi(n+k,lL) >= Phi(n+k,lL-1)`,
  a strict self-inequality; the strict step uses
  `Phi(n+1,lj) - Phi(n+1,lj-1) = (n+1)**lj > 0` for `lj >= 1`. ∎
  Route B agrees on all 90 enumerable cells (`n in 2..4`, `k in 2..3`,
  `lL <= lj <= 5`), with 0 collisions.

---

### `LF-2` — charge neutrality

- **claim_id:** `LF-2`
- **statement:** Under #897's charge `K_total(L) = sum_{m in L} (len(body_m) +
  kappa)`, the maintenance charge of one shared library of `k` members equals
  the total maintenance charge of the `k` separate single-member grammars over
  the same member set. The `LF-1` decision therefore carries **no charge term**.
- **domain:** finite member sets `L` with integer body lengths and a global
  integer `kappa >= 0`.
- **quantifiers:** `forall[D]` over all such member sets; `forall_fin[U]` over
  the registered 8-member-set census.
- **assumptions:** §0.1 (3), (4); `kappa` is global and member-independent;
  bodies are unchanged by the partition (the same `k` members either way).
- **proof_mode:** deductive (invariance of a sum under partition of its index
  set) + exact census.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** a member set whose shared and separate `K_total` differ; any
  charge model in which `kappa` depends on library size (explicitly out of
  scope — see open_gaps).
- **strongest_parents:** #897 (`K_total` definition and the `kappa = 1`
  ablation). #1019 `REP-2` — concurrent; its portfolio net charges `K_total`
  against *no library*, where it does not cancel.
- **prior_disclosure:** the cancellation is what makes the library-formation
  row a search-charge-only decision, which is the disjointness argument from
  `REP-2` recorded in `FREEZE_V1.md` §4.1(3).
- **forbidden_extrapolations:** does **not** say maintenance is free; it says
  it is *identical on both sides of this one comparison* and therefore cannot
  decide it. Any charge model with a per-library fixed overhead, shared-body
  deduplication, or size-dependent `kappa` falls outside.
- **open_gaps:** size-dependent or shared-substructure charge models.
- **Certificate:** 8/8 member sets equal, `difference = 0` on every row.
  *Proof.* `K_total` is a sum indexed by members whose summand depends only on
  that member's body length and the global `kappa`; partitioning the same index
  set into `k` singletons and summing the partial sums returns the same total.
  The partition is the only thing library-versus-separate changes, so the whole
  priced difference is the search-discovery difference `LF-1` decides. ∎

---

### `LF-3` — no-composition converse

- **claim_id:** `LF-3`
- **statement:** If the composition gain `gamma_w = lj - lL` is `0` for every
  target, then for `k >= 2` **both** `Phi(n+k,lj) > Phi(n+1,lj)` (strict) and
  `Phi(n+k,lj-1) >= Phi(n+1,lj-1)` (weak, tight only at `lj = 1`), and the
  exact same-rank dilution tax is `Phi(n+k,l-1) - Phi(n+1,l-1) > 0` for
  `l >= 2`. **Library formation is not a search-charge phenomenon without
  member composition.**
- **domain:** finite alphabets `n in 2..8`, library sizes `k in 2..6`, lengths
  `1 <= lj <= 12`, restricted to the `gamma_w = 0` diagonal (420 cells).
- **quantifiers:** `forall[D]` for the two inequalities and the tax sign;
  `forall_fin[U]` for the verdict counts over those 420 cells.
- **assumptions:** §0.1 (1)–(3), (5); `k >= 2`.
- **proof_mode:** deductive (`n+k > n+1` term-by-term) + exhaustive census.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** a `gamma = 0` cell verdicted `LIBRARY_GUARANTEED_BETTER`; a
  `l >= 2` cell with non-positive dilution tax.
- **strongest_parents:** #897 `T4` (widened-frontier regression: the same
  dilution mechanism with `|A_L| > 3`). #1019 `REP-1` — concurrent.
- **prior_disclosure:** #897's `T4` already exhibits alphabet dilution as a
  strictly positive burden penalty in the `G0 u L` vs `G0` comparison; the
  residual here is the same-rank tax in the **`n+k` vs `n+1`** comparison and
  the certified 210/210 split between the guaranteed-worse band and
  `RANK_DECIDED`. #1019's `REP-1` supplies the band frame concurrently.
- **forbidden_extrapolations:** see the honesty note below.
- **open_gaps:** the tax is stated same-rank; the expected-burden tax under a
  rank distribution is not derived.
- **Certificate:** 420 `gamma = 0` cells; **0** strict-upper-endpoint failures,
  **0** weak-lower-endpoint failures; minimum dilution tax `1`, 0 non-positive
  tax cells.
- **HONESTY NOTE — endpoint dominance does NOT imply the guaranteed-worse
  band.** Both endpoints of the library interval dominate the corresponding
  separate endpoints at every `gamma = 0` cell, yet only **210 of the 420**
  cells are `LIBRARY_GUARANTEED_WORSE`; the other **210 are `RANK_DECIDED`**,
  because the intervals still overlap (`Phi(n+k,lj-1) < Phi(n+1,lj)`) and a
  favourable rank draw can keep the library ahead. **0** cells are
  `LIBRARY_GUARANTEED_BETTER`. The claim that survives is therefore the
  two-sided one: *at `gamma = 0` the library never earns a guarantee, and it is
  guaranteed to lose only above the dilution threshold.* Anyone quoting `LF-3`
  as "`gamma = 0` ⇒ the library is guaranteed worse" is over-reading it by a
  factor of two on this census. This is the same conflation that falsified the
  frozen `gamma = 1` consequence of `OI-3` (§`OI-3`), recorded here so the two
  are read together.

---

### `LF-4` — minimum composition depth

- **claim_id:** `LF-4`
- **statement:** `gammastar(n,k,lj) = min{ gamma : Phi(n+k, lj-gamma) <=
  Phi(n+1, lj-1) }` over admissible `lL = lj - gamma >= 1`, or `None`. Then
  `gammastar >= 2` wherever defined; `gammastar` is non-decreasing in `k`
  (`None` read as `+infinity`); and `gammastar` is **undefined exactly at
  `lj = 2`**.
- **domain:** finite alphabets `n in 2..8`, library sizes `k in 2..6`,
  separate-grammar lengths `lj in 2..12` (385 cells), admissible `lL >= 1`.
- **quantifiers:** `forall_fin[U]` over that box for the table, the
  `k`-monotonicity and the undefined set; `forall[D]` for `gammastar >= 2`.
- **assumptions:** §0.1 (1) is load-bearing — see below; (2), (3), (5).
- **proof_mode:** exact integer computation + census; the `>= 2` bound is
  deductive.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M1`, `M2`.
- **falsifiers:** a defined `gammastar < 2`; a `(n, lj)` row where `gammastar`
  decreases as `k` increases (including a `None → defined` transition);
  an undefined cell at `lj != 2`.
- **strongest_parents:** #897 `T3`, `T4`. #1019 `REP-1` — concurrent.
- **prior_disclosure:** no parent defines a minimum composition depth. #1019's
  `REP-1` derives the band trichotomy this threshold is read off, concurrently
  and on an unmerged branch; `gammastar` itself, its `>= 2` floor, its
  `k`-monotonicity and its `lj = 2` undefined set are the residual here.
- **forbidden_extrapolations:** no extrapolation past the census box; `None`
  means "no admissible composition depth reaches the guarantee at this
  `(n,k,lj)`", not "the library is worse".
- **open_gaps:** the growth law of `gammastar` in `lj` is observed
  (monotone-looking) but **not** certified here; only `k`-monotonicity is.
- **Certificate:** 350 defined, 35 undefined, undefined exactly at `lj = 2`
  (7 `n` × 5 `k`), `min gammastar = 2`, **0** `gammastar < 2` violations,
  **0** `k`-monotonicity violations.
  *Why `gammastar >= 2`.* `gamma = 0` needs `Phi(n+k,lj) <= Phi(n+1,lj-1)`,
  false since `Phi(n+k,lj) > Phi(n+1,lj) > Phi(n+1,lj-1)` for `k >= 2`,
  `lj >= 1`. `gamma = 1` needs `Phi(n+k,lj-1) <= Phi(n+1,lj-1)`, false for
  `lj >= 2` since `n+k > n+1`. This is `OI-2`'s mechanism with the one-symbol
  step replaced by a `k`-symbol step. ∎
  *Why undefined exactly at `lj = 2`.* At `lj = 2` the admissible `gamma` are
  `0` and `1` only (because `lL >= 1`), and both fail by the argument above.
  **If `lL = 0` were admissible**, `gamma = lj` would always satisfy the
  condition (`Phi(.,0) = 0`) and `gammastar` would never be undefined — so the
  frozen "undefined at `l_j = 2`" clause is true *only* under assumption
  §0.1(1), which is why that assumption is registered rather than left implicit.
  Sample: `gammastar(2,2,3) = 2`, `(2,2,5) = 2`, `(2,2,8) = 3`,
  `(2,6,12) = 7`, `(5,3,7) = 2`, `(8,6,12) = 3`, `(2,2,2) = None`,
  `(8,2,2) = None`. Route B agrees on all 24 enumerable cells.

---

### `IND-1` — invention pays, no library is favoured

- **claim_id:** `IND-1`
- **statement:** There is an exact workload on which `OI-1` holds for a single
  operator and on which **no** library of `k >= 2` members drawn from the
  printed candidate set is `LIBRARY_GUARANTEED_BETTER`.
- **domain:** the single registered workload printed below (`n = 2`, one
  weighted target) together with the printed 10-element library candidate set.
- **quantifiers:** `forall_fin[U]` over that candidate set; deductive
  universality over all conceivable libraries is **NOT** claimed.
- **assumptions:** §0.1 (1)–(5); the candidate set is registered in the
  executor and printed in the result JSON.
- **proof_mode:** exact witness (`M2`) + `LF-4` as the blocking mechanism.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M2`.
- **falsifiers:** a candidate in the printed set verdicted
  `LIBRARY_GUARANTEED_BETTER`; an arithmetic error in `Theta_inv`.
- **strongest_parents:** #897 `T3`. `OI-1`, `OI-2`, `LF-1`, `LF-4` internally.
- **prior_disclosure:** no parent — #897 or #1019 — makes any independence
  claim between the invention row and the library-formation row, nor exhibits a
  workload separating them. There is no concurrent prior art to disclose for
  this witness beyond the band frame it is expressed in.
- **forbidden_extrapolations:** **not** "no library can ever help here" — only
  "no candidate in the registered set reaches the *guarantee*". Cells outside
  the set, and `RANK_DECIDED` cells inside it, are untouched.
- **open_gaps:** the candidate set is finite and chosen to realize the
  no-composition regime; a search over all libraries is not performed.
- **Witness:** `n = 2`; one target with weight `1/1`, `l0 = 12`, `l1 = 6`
  (`gamma = 6`); `D = 3`, `len(body) = 5`, `kappa = 1`.
  `Saving = Phi(2,11) + 1 - Phi(3,6) = 4094 + 1 - 1092 = 3003`, `Tax = 0`,
  `Theta_inv = 3003/1`, charge `= 9/1 < 3003` → **invention strictly pays**.
  Separate-grammar length `lj = 6`. Candidate libraries: `k in 2..6` ×
  `lL in {5, 6}` (composition gain `gamma_w in {0, 1}`) — **10 candidates, all
  not `LIBRARY_GUARANTEED_BETTER`**, because `LF-4` gives
  `gammastar(2,k,6) >= 2` for every `k in 2..6`.

---

### `IND-2` — library is favoured, no further operator pays

- **claim_id:** `IND-2`
- **statement:** There is an exact workload on which some `k >= 2` library **is**
  `LIBRARY_GUARANTEED_BETTER` while **no** further candidate operator in the
  printed set satisfies `OI-1`, even at zero charge.
- **domain:** the single registered workload printed below (`n = 2`,
  `lj = 6`) together with the printed 12-element operator candidate set.
- **quantifiers:** `forall_fin[U]` over that candidate set; deductive
  universality is **NOT** claimed.
- **assumptions:** §0.1 (1)–(5).
- **proof_mode:** exact witness (`M2`) + `OI-2` as the blocking mechanism.
- **evidence_level:** `EV1`, `EV2`. **maturity_level:** `M2`.
- **falsifiers:** a candidate in the printed set with `Theta_inv > 0` and a
  charge below it; a mis-verdicted library cell.
- **strongest_parents:** #897 `T3`. `OI-1`, `OI-2`, `LF-1`, `LF-4` internally.
- **prior_disclosure:** as `IND-1` — no parent claims or refutes independence
  of the two rows; #1019's forbidden promotion #10 explicitly disclaims both
  Section L rows, so it asserts nothing here either.
- **forbidden_extrapolations:** **not** "invention is exhausted" — only "no
  candidate in the registered set clears `OI-1`".
- **open_gaps:** as `IND-1`.
- **Witness:** `n = 2`, `lj = 6`; library `k = 2`, `lL = 4` (`gamma_w = 2 =
  gammastar(2,2,6)`): `Phi(4,4) = 340 <= Phi(3,5) = 363` →
  **`LIBRARY_GUARANTEED_BETTER`**. Further operator candidates: `l0 in 3..8` ×
  `gamma in {0, 1}` — **12 candidates, every one with `Theta_inv <= 0`**, so
  none can satisfy `D + len(body) + kappa < Theta_inv` at any nonnegative
  charge (by `OI-2`, `Phi(n+1,l0-1) >= Phi(n,l0-1)`, strictly for `l0 >= 2`).

#### Synthesis: `IND-1` + `IND-2` together (not a separate claim block)

`IND-1` realizes `(invention pays) AND NOT (library favoured)`; `IND-2`
realizes `(library favoured) AND NOT (any further operator pays)`. Neither row
entails the other: **`Derive operator invention.` and `Derive library
formation.` are logically independent** at the registered scope. This is a
`forall_fin[U]` independence over the printed candidate sets, not a `forall[D]`
independence over all workloads.

---

## 3. Hostiles, nulls, and two-route agreement

### 3.1 Registered hostiles — all five DETECTED, with a certified no-alarm case

| code | planted positive | detected | evidence |
|---|---|---|---|
| `H1_GAMMA0_OPERATOR_DECLARED_INVENTABLE` | `n=2, l0=l1=4`, claimed `INVENTABLE` | yes | detector recomputes `Theta_inv <= 0` |
| `H2_GAMMA0_LIBRARY_DECLARED_FAVOURED` | `n=2, k=3, lL=lj=5`, claimed better | yes | `LF-3`: 0 `gamma=0` cells are better |
| `H3_DILUTION_OFF_BY_ONE` (`n` for `n+1`) | full 2,730-cell verdict vector | yes | **481** differing cells |
| `H3_DILUTION_OFF_BY_ONE` (`n+1` for `n+k`) | full 2,730-cell verdict vector | yes | **867** differing cells |
| `H4_INADMISSIBLE_COMPRESSION` | `n=3, l0=4, l1=6` | yes | `l1 > l0` |
| `H5_RECURSIVE_LIBRARY_CYCLE` | `m1 -> a m2`, `m2 -> b m1` | yes | returns `RECURSIVE_LIBRARY_CYCLE`, grammar object returned **unchanged by identity and by content** |

`H3` is deliberately planted **across the whole census**, not on one cell: an
off-by-one alphabet agrees with the correct computation on most cells, so a
single-cell planted positive would have produced a false "detector works".
The differing-cell counts are recorded so the detector's power is visible.

**No-alarm case:** 5 known-clean submissions (a genuine `gamma = 4` inventable
operator, a genuine `gamma = 2` favoured library, the clean 2,730-cell verdict
vector, an acyclic 2-member library install, and a combined clean submission)
→ **0 flags on every one**. The acyclic install still works
(`INSTALLED`, both members present, source grammar untouched), so the cycle
guard is not simply refusing everything.

### 3.2 Null

200 randomized three-way sign predictors over the 2,730-cell `LF-1` census,
drawn from a registered deterministic integer LCG
(`x <- (6364136223846793005*x + 1442695040888963407) mod 2**64`,
seed `8330000041`, label `= (x >> 33) % 3`; the `random` module is not used and
no float is involved, so the run is bit-reproducible).

- derived rule: **2,730 / 2,730** correct;
- nulls matching or beating it: **0 / 200** (target met);
- null score distribution: min **850**, median **907**, max **965**;
- margin of the derived rule over the best null: **1,765 cells**.

### 3.3 Two-route agreement

Route B (`oracle_derivation_v1.py`) does not import `derivation_v1` (checked
structurally on the parsed AST, not by substring). **No reported verdict
derives from a closed form**: the sole closed-form evaluation in the oracle is
the budget guard `scan_size`, which decides whether a scan is affordable and
never produces a verdict; the identifier `Phi` does not occur (checked by AST
name scan). It builds actual words over an explicit finite
alphabet with an explicit macro-expansion semantics, enumerates programs in
breadth-by-length order one word at a time, and reads the burden endpoints off
the enumeration. Agreement on the registered overlap scope:

| check | cells checked | agreeing |
|---|---|---|
| `T3_BURDEN_IDENTITY` | 7 | 7 |
| `OI-1_THETA_INV_ON_W1` | 4 | 4 |
| `OI-2_GAMMA1_NEVER_GUARANTEED_REDUCTION` | 15 | 15 |
| `OI-3_LSTAR_AND_MSTAR` | 4 | 4 |
| `OI-4_WITNESS_VERDICTS` | 3 | 3 |
| `LF-1_THREE_WAY_BAND` | 90 | 90 |
| `LF-4_GAMMASTAR` | 24 | 24 |
| **total** | **147** | **147** |

`HOSTILE_GAMMA0_FACTS_BY_ENUMERATION` additionally certifies by enumeration
that no `gamma = 0` operator has positive rank-free saving (15 cells) and no
`gamma = 0` library is guaranteed better (30 cells) — the `H1`/`H2` facts,
re-derived without the closed form.

**Reachable-scope discipline.** Every cell Route B could not reach within its
registered 1,000,000-word-per-scan budget is reported `OUT_OF_BUDGET` and is
**not** silently computed by a closed form. This is why `Mstar` is enumerated
only at `n = 2` and `LF-1` only on `n in 2..4`, `k in 2..3`, `lj <= 5`.

---

## 4. What is FALSE as frozen, stated plainly

**One frozen statement did not survive the census.** `FREEZE_V1.md` §4.3's
`OI-3` asserts "At depth `>= L*(n)` a `gamma = 1` admission strictly loses at
every nonnegative charge — the matched converse." That is **false**: `Lstar`'s
defining condition `Phi(n+1,l-1) >= Phi(n,l)` is the `GUARANTEED_INCREASE`
predicate at `gamma = 0`, not at `gamma = 1`. There are **860** counterexample
cells in `n in 2..24`; the lexicographically first is `n = 2, l0 = 4, l1 = 3`,
which is `RANK_DECIDED` even though `l0 = 4 = Lstar(2)`. The definition of
`Lstar` and its bracket are **true** and are not edited. The corrected converse
is carried by a new derived companion `Mstar(n) = min{ l >= 2 :
Phi(n+1,l-2) >= Phi(n,l) }`, which satisfies the *same* frozen bracket at every
`n in 2..24` and strictly exceeds `Lstar(n)` everywhere. Both converses are
certified with 0 failures, and both routes see the discrepancy.

Two further statements are true only with an explicitly registered
qualification, recorded rather than silently absorbed:

- `OI-2`'s band consequence has **11 exception cells**, all at `l0 = 1`, all
  requiring the empty program `l1 = 0`. They are excluded by registered
  assumption §0.1(1), not by narrowing the census.
- `LF-3`'s endpoint dominance is **not** the guaranteed-worse band: 210 of the
  420 `gamma = 0` cells are `RANK_DECIDED`.

No other frozen statement of §4 was found false at the registered scope.

---

## 5. Open gaps (carried forward, not closed)

1. Every result is **rank-free**, hence conservative; no expected-burden
   (rank-distributional) threshold is derived for `OI-1`, `LF-1` or `LF-3`.
2. `IND-1` / `IND-2` are `forall_fin[U]` over printed candidate sets; a search
   over all libraries / all operators is not performed.
3. `LF-1`'s census fixes one `(lL, lj)` pair per cell: heterogeneous member
   sets with per-target composition gains are not enumerated.
4. `LF-2` assumes a member-independent global `kappa`; size-dependent or
   shared-substructure charge models are out of scope.
5. No asymptotic closed form for `Mstar(n)`; only the exact table and the
   shared (loose) bracket are certified, and only for `n <= 24`.
6. Route B's enumeration budget leaves `Mstar(n)` for `n >= 3` unverified by
   the independent route.
7. `LF-4`'s monotonicity is certified in `k` only; monotonicity in `lj` is
   observed but **not** claimed.

## 6. Forbidden promotions reasserted for this note

`GRAMMAR_GROWTH_OWNED_HERE`, `LIBRARY_IMPLEMENTATION_NOVEL_HERE`,
`INVENTION_MECHANISM_NOVEL_HERE`, `REPRESENTATION_CHANGE_ROW_OWNED_HERE`,
`SEARCH_DYNAMICS_COMPARISON_OWNED_HERE`, `P4_NOVELTY_ROW_OWNED_HERE`,
`SECTION_L_COMPLETE`, `CONTINUOUS_OR_INFINITE_SCOPE`, `COMPLETE_GMI`.
Nothing in this note is `EV3`, `EV4` or `EV5`, and nothing is `M3` or above.
