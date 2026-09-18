# FREEZE V1 — gmi-833-developmental-reuse-v1 (#833 Section L)

**Status:** pre-implementation formalism / fixture / claim freeze.
**Source main:** `bfb7d8c296a60c0bc76632ed69551540644e74e6`
**Parent issue:** #833, Section L "Development, morphogenesis, and evolvability".
**Claim ceiling (verbatim, enforced by CI and pinned in `MANIFEST_V1.json`):**

```text
GMI_833_FINITE_EXACT_REPRESENTATION_CHANGE_CRITERION_GRAMMAR_GROWTH_NOVELTY_CHARACTERIZATION_AND_ECOLOGY_CONDITIONAL_SEARCH_DYNAMIC_COMPARISON_AT_REGISTERED_SCOPE
```

This file is committed **before** any executor, oracle, test, receipt, manifest,
reconciliation JSON or workflow exists on this branch. Git order is the proof.
Every claim this package may ever make is bounded by what is written here.

---

## 0. Rows in scope (VERBATIM from the live #833 body at `source_main`)

This tranche may reconcile **exactly** these three rows under anchor
`# L. Development, morphogenesis, and evolvability`:

```text
- [ ] Derive representation changes that reduce future search cost.
- [ ] Compare mutation, local search, GP/CGP, evolutionary, gradient, NAS-like, and meta-search dynamics.
- [ ] Test whether P4 recursive grammar growth discovers mechanisms absent from `G0`.
```

This tranche was **also assigned** the following two rows and **deliberately
leaves them OPEN**; they appear here so the reconciliation JSON cannot be read
as having silently dropped them:

```text
- [ ] Predict evolvability on genuinely future task families.
- [ ] Validate developmental predictions on continual-learning systems.
```

Reasons, frozen now so they cannot be rationalised later:

- *"genuinely future task families"* is a **custody** claim. Any family this
  package could construct is authored by the same process that authors the
  predictor, or is drawn from repository blobs that provably **predate** the
  predictor freeze — i.e. past, not future. Git order can prove
  *predictions-before-outcomes*, but it cannot manufacture futurity. Closing
  the row on an out-of-sample-but-past family would close it by narrowing its
  stated meaning, which the #833 discipline forbids. **LEFT OPEN.**
- *"continual-learning systems"* requires real systems with sha256-bound data
  sources in the style of `gmi-833-real-transition-receipts-v1` (#903). No such
  data source is in hand for this tranche. Closing it on synthetic trajectories
  would be a category error. **LEFT OPEN.**

**No neighboring row is earned here.** In particular this tranche makes **no**
claim on `Derive operator invention.`, `Derive library formation.`, `Derive
developmental phase transitions.`, `Derive path dependence and hysteresis.`,
`Derive conditions for escaping local developmental traps.`, or `Prove/measure
reachability mass for predicted morphologies.` The last four are owned by the
concurrent lane on #910 / PR #924 and are not touched.

### 0.1 Recorded discrepancy in the tranche brief

The worker brief for this tranche asserted that the Section-L rows `Derive
operator invention.` and `Derive library formation.` were already checked and
credited to #897. At `source_main` they are **unchecked** in the live issue
body (verified by direct `gh issue view` read), and #897's own reconciliation
file `research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V2.json`
carries anchor `# E. Universal architecture-neutral machine grammar` for **all
three** of its replacements — it never targeted a Section-L row. The
discrepancy is recorded, not acted on: those two rows remain outside this
tranche's scope and are left untouched.

---

## 1. Coverage adjudication against #897 / `gmi-833-g0-grammar-growth-v1` (+ v2)

This adjudication is performed **before** any new derivation, as required.

**What #897 (v1) owns.** `GRW-1` conservative monotone extension with cycle
rejection; `INV-1`/`REC-1` deterministic charged invention forming `m1 -> a b`,
`m2 -> m1 m1`; `HLD-1`/`THR-1`/`NULL-1`: on 12 frozen reuse-positive held-outs,
exact burdens `50,052 -> 1,307` with `K_total = 6` (net `−48,739`), negative
control net `+1,178`, `0/200` equal-size random-admission nulls better,
`κ`-ablation deriving `κ = 1`. Its `T4` derives the pure-widening regression
formula (the **no-reuse** case); its `T5` derives the linear lifecycle threshold
`H_eff · Δ > K` on **description length**.

**What v2 (`gmi-833-g0-grammar-growth-v2`) adds.** `T7` depth-3 formation
saturation under INV-1; `T8` the EXEC-B execution-cost closed form and the
cost-relativity of the v1 rank claim (`19/200` exec-nulls beat the true library);
`T9` *tier-conditional compounding*, stated as: for macro depth `g` and target
reuse depth `t`, burden strictly decreases when `g ≤ t` and strictly increases
when `g > t`; `T10` the head-to-head finding that **neither compression nor
utility-gated admission dominates** (trap3: compression regresses by `+43,897`).

**Verdict: #897 (and v2) own a PART of the row, not the row.** Precisely:

1. Their result is a **measurement of one library on one frozen fixture family**
   under the Section-E row *"Test whether newly invented primitives reduce
   future discovery cost on unseen tasks."* The Section-L row says **Derive**.
   The #833 header itself legislates this distinction:
   `expressible != admissible != derivable != reachable != selected != recovered != predicted != replicated != real-scale validated`.
   A measured instance does not discharge a derivation row.
2. Neither package states a **criterion** on representation changes. v2's own
   headline finding — that no admission rule dominates, with a `+43,897`
   regression on `trap3` — is direct evidence *from the parents themselves* that
   the governing criterion is not yet in the corpus. A criterion is what tells
   you `trap3` will regress **without running it**.
3. The nearest miss is `HIST-1` (#909/#908): *history helps held-out discovery
   exactly when its charged expected burden, including policy overhead, is
   smaller.* That is an **accounting identity** — it restates the verdict in
   terms of the quantity you must measure. The residual claimed here is the
   **structural inequality in `(n, n', ℓ0, ℓ1, K, reuse mass)`** that decides
   the identity's sign **without running the search**.
4. v2's `T9` is stated informally as a match-implies-cheaper law. This tranche
   **bounds it by exact counterexample** (see `REP-3` below): a target that
   *does* use the macro (`g ≤ t`, one greedy occurrence, description length
   strictly reduced) and whose burden **strictly increases for every possible
   rank assignment**. The parent statement is true at the parent's measured
   parameter point and false as a general law; the boundary is earned, not
   asserted.

**Residual claimed by this tranche (named):** the exact, rank-free,
scope-free *decision bracket* for whether a representation change reduces
discovery burden, its portfolio (expected-cost) form with charges, and the
boundary counterexample. `#897` and `v2` are cited as strongest parents and
their fixtures are used as **validation targets** — this package must re-derive
their published integers from the criterion, or the criterion is wrong.

No duplicate package is manufactured: nothing here re-measures a library's
held-out benefit, re-runs INV-1, or re-states GRW-1.

---

## 2. Frozen substrate (inherited verbatim from #897 FREEZE §3–§4)

- Base token set `Σ = {a, b, c}`, frozen total order `a < b < c`.
- A **program** is a finite nonempty sequence of symbols of the current
  grammar alphabet `A_t = Σ ∪ M_t`; the only combinator is concatenation.
- Each macro `m_k` has a body over `Σ ∪ M_{k-1}`. `Expand` is recursive
  symbol-wise substitution to base tokens; total iff the macro dependency
  relation is acyclic (#897 `T1`(3); cyclic libraries return
  `RECURSIVE_LIBRARY_CYCLE` and are out of scope for every theorem below).
- **Canonical symbol order:** `a < b < c < m_1 < m_2 < ...`.
- **Enumeration order:** breadth by description length, lexicographic within a
  length under the canonical order.
- **Discovery burden** `B_G(w)` for a base target word `w`: the 1-based count of
  programs enumerated up to and including the first whose expansion equals `w`.
- **Closed form** (#897 `T3`): with `n = |A|`, `ℓ* = ℓ*_G(w)` the least program
  length whose expansion is `w`, and `rank_{ℓ*}(p*) ∈ [0, n^{ℓ*} - 1]` the
  `n`-ary index of the lex-least hit program,
  `B_G(w) = Φ(n, ℓ* − 1) + rank_{ℓ*}(p*) + 1`, where
  `Φ(n, ℓ) = Σ_{j=1}^{ℓ} n^j` (and `Φ(n, 0) = 0`).
- **Library overhead:** `K_total(L) = Σ_{m ∈ L} (|body_m| + κ)`, frozen `κ = 1`
  (#897's derived value; every verdict additionally reports its exact break-even
  `κ` where `κ` is load-bearing).

All arithmetic in this package is **exact integer / `fractions.Fraction`**.
No float appears in any claim, receipt, test assertion, or reconciliation line.

### 2.1 Immediate consequence used throughout (bracket)

For every grammar `G` with `|A| = n ≥ 2` and every target `w`:

```text
Φ(n, ℓ* − 1) + 1  ≤  B_G(w)  ≤  Φ(n, ℓ*)
```

both bounds attained (rank `0` and rank `n^{ℓ*} − 1`).

---

## 3. Named results this tranche may claim

Nothing outside this list may be claimed. Each result names its falsifier.

### REP-1 — exact decision bracket for a representation change

**Scope.** `G0` with `|A_0| = n ≥ 2`; `G1 = G0 ∪ L` acyclic, `|A_1| = n' > n`;
target `w`; `ℓ0 = ℓ*_{G0}(w)`, `ℓ1 = ℓ*_{G1}(w)` (`ℓ1 ≤ ℓ0` by conservativity).

**Statement (three-way, rank-free on the outer bands).**

```text
GUARANTEED_REDUCTION   iff  Φ(n', ℓ1)      ≤  Φ(n, ℓ0 − 1)
GUARANTEED_INCREASE    iff  Φ(n', ℓ1 − 1)  ≥  Φ(n, ℓ0)
RANK_DECIDED           otherwise
```

In the first band `B_{G1}(w) < B_{G0}(w)` for **every** rank assignment; in the
second `B_{G1}(w) > B_{G0}(w)` for every rank assignment; in the third the sign
is decided by the exact closed form and both signs are realisable.

**Falsifier.** A `(n, n', ℓ0, ℓ1, w)` instance in band 1 or 2 whose exactly
computed burdens contradict the band, on either route.

**Forbidden extrapolation.** REP-1 is a statement about the registered
breadth-by-length enumeration burden. It says nothing about wall-clock cost,
about other enumeration orders, or about execution-cost metrics (v2 `T8`
`EXEC-B`) unless separately derived.

### REP-2 — portfolio (expected-cost) form with charges

**Scope.** A frozen finite target multiset `T` (or rational weight
distribution `D`), library `L`, charge `K_total(L)`.

**Statement.** `ΔNet(T, L) = Σ_{w ∈ T} (B_{G1}(w) − B_{G0}(w)) + K_total(L)`
decomposes **exactly** into
`− Saving(T⁺) + Tax(T⁰) + K_total(L)` where `T⁺ = {w : ℓ1 < ℓ0}` and
`T⁰ = {w : ℓ1 = ℓ0}`, `Tax(T⁰) = Σ_{w ∈ T⁰} [Φ(n',ℓ0−1) − Φ(n,ℓ0−1) + rank_{n'}(p*) − rank_n(p*)] > 0`
strictly whenever `n' > n` and `ℓ0 ≥ 2` (this is #897 `T4` generalised off its
fixture). A representation change reduces expected future search cost **iff**
`Saving(T⁺) > Tax(T⁰) + K_total(L)`; per-target membership of `T⁺` in the
guaranteed bands is decided by REP-1 without computing ranks.

**CAPITAL-1 boundary (mandatory case, not optional).** The *solution-capital*
library `L_sol = {m → w*}` for a single registered target `w*` must be
evaluated. REP-1 will place `w*` in `GUARANTEED_REDUCTION`; REP-2 must reject
`L_sol` on the registered distribution via `Tax(T⁰) + K_total`. This is the
exact registered separation of **solution capital** from **search-policy
improvement** (parent `CAPITAL-1`, #909/#908) in burden terms.

**Falsifier.** A registered `(T, L)` where the decomposition does not reproduce
the directly computed `ΔNet` integer exactly; or `L_sol` not rejected.

### REP-3 — EARNED-BY-COUNTEREXAMPLE boundary on "the target uses the macro"

**Statement.** There exists a registered instance with `n = 3`, `n' = 4`,
`L = {m1 → (a,b)}`, `|w| = 11`, `w` containing exactly one greedy `ab`
occurrence, hence `ℓ0 = 11`, `ℓ1 = 10` (strict description-length reduction,
the macro **is** used by the lex-least hit program), for which
`Φ(4, 9) = 349,524 ≥ Φ(3, 11) = 265,719`, so `B_{G1}(w) ≥ 349,525 > 265,719 ≥ B_{G0}(w)`
for **every** rank assignment: burden strictly increases.

Therefore *"the target uses the macro"* / *"the macro shortens the description"*
is **not sufficient** for future-search-cost reduction. The parent statement
(v2 `T9`, informal reading) is bounded here, not refuted at its own measured
parameter point.

**Registered near-miss hostile (`H-NEARMISS`).** The same construction at
`|w| = 10`, `ℓ1 = 9`: `Φ(4, 8) = 87,380 < Φ(3, 10) = 88,572`, so the brackets
**overlap** and REP-1 must classify it `RANK_DECIDED`, not as a boundary. A
checker that reports it as a guaranteed increase is broken. The exact sign at
this point is computed and reported, whichever way it falls.

**Falsifier.** Enumeration disagreeing with the closed form on either instance;
or REP-1 classifying `H-NEARMISS` outside `RANK_DECIDED`.

### NOV-1 — conservative grammar growth adds ZERO expressive power

**Scope.** Every acyclic library `L` reachable by conservative growth from `G0`
(#897 `GRW-1`), every `t`.

**Statement.** `{ Expand(p) : p a program over A_t } = Σ⁺ = { Expand(p) : p a program over Σ }`,
for every `t`. Growth cannot make any semantics expressible that was not
already expressible, and cannot remove one.

**Proof obligation.** Induction on the topological order of the macro
dependency DAG (⊆-direction), plus the identity program `w` (⊇-direction).

**Consequence (the sharp reading of the row).** *"A mechanism absent from `G0`"*
is **incoherent** under the expressibility reading: provably no such mechanism
exists at any `t`. This is a **proven impossibility**, delivered as a positive.

**Falsifier.** An acyclic admitted library and a program over `A_t` whose
expansion is not a `Σ⁺` word, or a `Σ⁺` word not expressible over `A_t`.

**Forbidden extrapolation.** NOV-1 is about the frozen concatenation-only
substrate with body-over-earlier-alphabet macros. It is **not** a claim that
library learning never adds expressive power in richer substrates (e.g. with
recursion through a fixpoint combinator, conditionals, or unbounded iteration).

### NOV-2 — budget-reachability is genuinely non-monotone under growth

**Scope.** Registered budget `B ∈ ℕ`, `Reach_G(B) = { w ∈ Σ⁺, |w| ≤ Lmax : B_G(w) ≤ B }`,
finite by construction, decidable by finite enumeration.

**Statement.** For the registered `(G0, L, B, Lmax)` census both difference sets
are **nonempty**:

```text
ADDED(B)   = Reach_{G1}(B) \ Reach_{G0}(B)   ≠ ∅
REMOVED(B) = Reach_{G0}(B) \ Reach_{G1}(B)   ≠ ∅
```

with exact counts reported. Hence: under the **only coherent** reading of
"absent from `G0`" that survives NOV-1 — namely *not reachable within the
registered budget* — recursive grammar growth **does** discover targets absent
from `G0`, **and simultaneously loses others**. Growth is a trade, not a gain;
membership of each difference set is decided by REP-1 with `B` interposed.

**Falsifier.** Either difference set empty at the registered parameters, or a
census disagreement between the two routes.

**Forbidden extrapolation.** `ADDED ≠ ∅` is an existence result at registered
finite scope. It is **not** open-endedness, not unbounded novelty, and not a
claim that growth adds *capabilities* in any architecture-level sense.

### SD-1 — common charged frame, exact win matrix, no dominance

**Frame (what is held fixed — the scientific requirement).** All dynamics face:
the same search space `X = Σ^ℓ` (`|X| = 3^ℓ`); the same registered target
multiset; the same evaluation-charged cost accounting (**1 unit per objective
evaluation, repeats charged**); the same budget `B_eval`; the same registered
deterministic seed stream (an exact integer LCG frozen in §5). The **only**
thing that varies is the dynamic. Any deviation is a frame violation and must
be detected by the frame validator (§4).

**Dynamics (8, all deterministic given the seed).** `ENUM` (lexicographic
enumeration, the #897 baseline), `MUT` (single-position mutation random walk),
`LS` (steepest-ascent 1-Hamming local search with registered restart), `GP`
(one-point sequence crossover + mutation), `EVO` (`(μ,λ)` truncation selection +
mutation), `GRAD` (exact coordinate descent — the registered discrete proxy),
`NAS` (two-level: outer representation proposal from a registered library pool,
inner `ENUM` under the grown grammar, charged `K_total` and both levels),
`META` (registered round-robin budget portfolio over `{ENUM, LS, EVO}`, paying
each arm's full cost).

**Ecologies (3, the objective oracle).** `OPAQUE`: `f(x) = 1` iff `x = w`, else
`0`. `GRADED`: `f(x) = #{ i : x_i = w_i }` (separable Hamming agreement).
`DECEPTIVE`: `f(x) = #{ i : x_i = z_i }` for `x ≠ w` and `f(w) = ℓ + 1`, with
`z` the registered decoy at Hamming distance `ℓ` from `w`.

**Statement.** The exact 8×3 matrix of evaluations-to-first-hit (or
`NOT_FOUND_IN_BUDGET`) is reported. **No dynamic is best in every ecology and no
dynamic is worst in every ecology**, with the exception recorded exactly.

**Falsifier.** A route disagreement on any matrix cell; or a dynamic dominating
all others in all three ecologies.

### SD-2 — the mechanism (why the ordering is what it is)

Three derived statements; the ordering in SD-1 is a **consequence**, not a
leaderboard.

- **SD-2a (`OPAQUE` expected-query optimality, expectation-form).** With `w`
  uniform on `X`, any dynamic whose only access to `w` is the `OPAQUE` oracle
  has expected evaluations-to-hit `≥ (|X| + 1) / 2`, with equality **iff** it
  never repeats a query. `ENUM` attains it exactly. Every resampling dynamic
  (`MUT`, `EVO`, `GP`) is **strictly worse**, and the exact mechanism is its
  duplicate-revisit count. (Per-instance luck is not excluded; the claim is
  over the registered uniform target distribution.)
- **SD-2b (`GRADED` separability separation).** Because Hamming agreement is
  separable across positions, `GRAD` hits `w` in **exactly** `ℓ · (n − 1)`
  evaluations in the worst case over `X` (exact, not measured), against
  `ENUM`'s `(|X| + 1) / 2 = (3^ℓ + 1) / 2`. Exponential separation, derived
  from the objective's decomposability — **not** from any property of gradient
  methods.
- **SD-2c (`DECEPTIVE` structural failure).** `GRAD` and `LS` provably never
  hit `w` from any start: both converge to `z`, at `z` every 1-neighbour has
  strictly smaller `f`, and `w` is at Hamming distance `ℓ ≥ 2`, so `w` is not a
  1-neighbour of any point they can occupy at a local optimum. Zero hits is a
  **proven structural** outcome, not a measured one. `ENUM` is unaffected.

**Joint consequence.** The SD-1 ordering is fully determined by two structural
properties of the **ecology** — whether the objective is graded, and whether it
is deceptive — and not by any intrinsic merit ordering of the dynamics. Stating
the ecology-conditionality exactly **is** the result.

**Falsifier.** Any measured cell contradicting SD-2a/b/c at the registered
scope.

**Forbidden extrapolations (explicit).**
- `GRAD` here is **coordinate descent**. The registered substrate has **no
  differentiable structure** — that absence is itself part of the finding. **No
  claim whatsoever** is made about gradient methods on differentiable
  substrates (neural training, continuous optimisation).
- `GP` here is **one-point sequence crossover + mutation**. **No claim** is made
  about tree-GP, Cartesian GP, or any typed-program genetic programming system.
- `NAS` here is **two-level representation-then-enumeration search**. **No
  claim** is made about neural architecture search on real networks.
- The no-dominance statement is at **registered finite scope over three
  registered ecologies**. It is neither a general No-Free-Lunch theorem nor a
  strengthening of one. Parent: `gmi-833-update-law-nfl-v1` (#870), which proves
  a uniform-completion NFL boundary for **update laws / held-out prediction
  accuracy** — a different object from discovery burden under search dynamics.

### SD-3 — meta-search charged overhead and its exact break-even

**Statement.** `META` pays a registered overhead (it funds arms that do not hit)
and is reported with its exact charged cost and its exact break-even share. The
claim is the derived accounting, plus its position in the SD-1 matrix. `NAS` is
reported under REP-1/REP-2: representation search is governed by the same
criterion, so `NAS`'s charged performance is **predicted** by REP-2 and the
prediction is checked.

**Falsifier.** `META`'s reported cost not equal to the sum of its arms' charged
costs; or `NAS`'s charged outcome disagreeing with the REP-2 prediction.

---

## 4. Hostiles that MUST be detected (frame + criterion integrity)

Registered now; the checker must flag every one and the tests assert detection.

| id | hostile | must be flagged as |
|---|---|---|
| `H-NEARMISS` | REP-3 construction at `|w| = 10` (overlapping brackets) | `RANK_DECIDED`, never a guaranteed band |
| `H-CYCLE` | library with a dependency cycle | `RECURSIVE_LIBRARY_CYCLE`, grammar unchanged, NOV-1 not applied |
| `H-UNCHARGED` | a dynamic that evaluates the oracle without incrementing its counter | `FRAME_VIOLATION_UNCHARGED_EVALUATION` (independent instrumented counter mismatch) |
| `H-BUDGET` | a dynamic run at a larger budget than the frame's | `FRAME_VIOLATION_BUDGET_MISMATCH` |
| `H-TARGET` | a dynamic run on a different target than the frame's | `FRAME_VIOLATION_TARGET_MISMATCH` |
| `H-ORACLE-PEEK` | a dynamic that reads `w` directly rather than through `f` | `FRAME_VIOLATION_TARGET_LEAK` |
| `H-CAPITAL` | `L_sol = {m → w*}` solution-capital library | accepted by REP-1 on `w*`, **rejected** by REP-2 on the distribution |
| `H-NOREUSE` | library whose body occurs zero times in any target | `Saving(T⁺) = 0`, `ΔNet > 0` strictly |
| `H-RANKFLIP` | a burden implementation using rank `0` instead of the true rank | detected by two-route disagreement |

**No-alarm obligation.** The checker must also be asserted **silent** on the
known-clean registered instances (true library, true frame, true dynamics). A
checker that fires on clean data is a defect, not a finding.

## 5. Frozen fixtures, constants and seeds

Everything numeric below is frozen now; the machine-readable copy lives in
`FROZEN_FIXTURES_V1.json` **in this same commit**, consumed by content hash.

- `Σ = {a,b,c}`, `n = 3`; `κ = 1`.
- REP-1 census: all `(n, n', ℓ0, ℓ1)` with `n ∈ {2,3,4}`, `n' ∈ {n+1, n+2, n+3}`,
  `1 ≤ ℓ1 ≤ ℓ0 ≤ 12`; every cell classified and, where realisable at the
  frozen scope, witnessed by an actual `(w, L)` instance.
- REP-3 primary: `w_star11`, a length-11 word over `Σ` with exactly one greedy
  `ab`; `H-NEARMISS`: `w_near10`, length 10, exactly one greedy `ab`. Both
  literal strings are frozen in `FROZEN_FIXTURES_V1.json`.
- REP-2 registered distribution `T`: the #897 held-out sets reused verbatim
  (`H+` 12 reuse-positive, `H−` 12 unrelated), plus the `L_sol` target `w*`.
  Re-deriving #897's published integers (`50,052 → 1,307`, `K_total = 6`, net
  `−48,739`; control `538 → 1,710`, net `+1,178`) from REP-2's decomposition is
  a **required validation**, not an optional check.
- NOV-2 census: `Lmax = 6` (all `1092` words over `Σ` of length `≤ 6`),
  `L = {m1 → (a,b), m2 → (m1,m1)}` (#897's registered library),
  budget grid `B ∈ {10, 100, 1000, 5000, 20000}`.
- SD frame: `ℓ = 8` primary (`|X| = 6561`), scaling rows at `ℓ ∈ {6, 8, 10}`;
  budget `B_eval = |X|` (one full sweep's worth); population `μ = 8`, `λ = 32`;
  `LS` restart after a local optimum; `META` round-robin shares `(1,1,1)`.
- Seed stream: exact integer LCG `s_{k+1} = (1103515245 · s_k + 12345) mod 2^31`,
  seed `s_0 = 20260918`. Null controls use `s_0 ∈ {1 .. 200}` (`RAND`, uniform
  sampling with the same charging).
- **Two-sided null (SD).** Guided dynamics **must** beat the 200-seed `RAND`
  control in `GRADED`, and **must not** beat it in `OPAQUE`. Both directions are
  asserted; either failing falsifies SD-2a/SD-2b.

## 6. Two-route obligation

Every computational claim is produced twice:

- **Route A** (`developmental_reuse_v1.py`): closed-form burdens (segmentation
  DP for `ℓ*`, `n`-ary rank arithmetic), REP-1 band arithmetic, analytic
  SD-2 formulas.
- **Route B** (`independent_oracle_v1.py`): **literal enumeration** — programs
  generated breadth-by-length and expanded, burdens counted 1-based; SD matrix
  recomputed by a separately written simulator. Route B **must not import**
  Route A. Agreement on every registered integer is a test.

The REP-3 instance is within literal-enumeration reach (`Φ(4,9) = 349,524`), so
the boundary result carries an enumeration witness, not only a closed form.

## 7. Execution environment

Executor and tests: stdlib-only, `python3 -I -B` and `python3 -I -O -B`, CPython
`>= 3.8` (no `match`, no `X | Y` unions). All runs on **laptop-billy**; the Mac
is git/gh only. Hosts, commands and hashes recorded in `RECEIPTS_RUN_LOG.md`.

## 8. Forbidden promotions (CI-enforced, copied to `MANIFEST_V1.json`)

1. No universal / asymptotic / architecture-level claim from any finite census.
2. No claim that library learning adds expressive power (NOV-1 forbids it here,
   and NOV-1 itself is scoped to this substrate).
3. No open-endedness, unbounded-novelty, or capability-gain reading of NOV-2.
4. No claim about gradient methods on differentiable substrates from `GRAD`.
5. No claim about tree-GP / Cartesian GP from `GP`; none about neural
   architecture search from `NAS`.
6. No general No-Free-Lunch claim from SD-1.
7. No claim on `Predict evolvability on genuinely future task families.` or
   `Validate developmental predictions on continual-learning systems.` — both
   deliberately left OPEN (§0).
8. No claim on any row owned by #910 / PR #924.
9. No wall-clock, execution-cost (`EXEC-B`), or alternative-enumeration-order
   reading of REP-1/REP-2/REP-3.
