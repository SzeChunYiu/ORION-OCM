# GMI #833 Section I — admissible update-law space and credit-assignment regimes — FREEZE V1

**Status:** PRE-IMPLEMENTATION SCIENTIFIC CUSTODY RECORD.
Every executor, oracle, test, receipt, theorem note, manifest, reconciliation spec and
workflow in this package MUST postdate this commit in git order.

**Parent issue:** SzeChunYiu/ORION-OCM#833, Section I
("Learning-law derivation without algorithm priors").
**Package:** `research/gmi-833-update-law-space-v1/`
**Frozen from main:** `6590cd998cdc7d60333d3c4ec446ae7757788a4b`

**Claim ceiling:**
`GMI_833_SECTION_I_UPDATE_LAW_SPACE_AND_CREDIT_ASSIGNMENT_REGIMES_AT_REGISTERED_FINITE_SCOPE`

---

## 1. Exact target rows

This tranche may reconcile ONLY these four rows, quoted VERBATIM from the #833 issue
body (lines 232-235 under the anchor `# I. Learning-law derivation without algorithm priors`):

```
- [ ] Define the space of admissible update laws architecture-neutrally.
- [ ] Derive conditions favoring local trial-and-error updates.
- [ ] Derive conditions favoring directional/gradient information.
- [ ] Derive reverse-mode credit assignment from graph/resource structure rather than naming backprop.
```

**No neighboring row is earned here.** In particular the Section I rows on Bayesian
update behavior, memory/exemplar update, rule induction, program/library learning,
evolutionary/population search, meta-learning and self-modification are NOT touched,
and no row in Sections A-H or J-onward is touched.

---

## 2. Parent ownership, pinned before any result exists

This tranche claims NO novelty for any of the following. They are absorbed
(assimilation-first) and their mathematics is theirs.

### 2.1 External literature parents

- **S. Linnainmaa (1970)**, *The representation of the cumulative rounding error of an
  algorithm as a Taylor expansion of the local rounding errors*, MSc thesis, Univ. of
  Helsinki; and **Linnainmaa (1976)**, *Taylor expansion of the accumulated rounding
  error*, BIT 16(2):146-160, DOI `10.1007/BF01931367`. Reverse accumulation of
  derivatives over a computational graph.
- **B. Speelpenning (1980)**, *Compiling Fast Partial Derivatives of Functions Given by
  Algorithms*, PhD thesis, Univ. of Illinois at Urbana-Champaign (UILU-ENG 80-1702).
  Automatic reverse-mode generation of gradients.
- **A. Griewank and A. Walther (2008)**, *Evaluating Derivatives: Principles and
  Techniques of Algorithmic Differentiation*, 2nd ed., SIAM, DOI
  `10.1137/1.9780898717761`. **The cheap-gradient principle — that a reverse-mode
  gradient costs a small constant multiple of the function evaluation, independent of
  the number of independent variables — is PARENT MATHEMATICS. This tranche does NOT
  claim it.** Vertex/edge elimination on the linearized graph, and checkpointing as a
  recomputation/retention trade, are likewise parent-owned (Ch. 9, Ch. 12).
- **U. Naumann (2008)**, *Optimal Jacobian accumulation is NP-complete*, Mathematical
  Programming 112(2):427-441, DOI `10.1007/s10107-006-0042-z`. This tranche's
  elimination-order census is a BOUNDED FINITE CERTIFICATE over registered small
  graphs; it is NOT a solution to optimal Jacobian accumulation, and no general
  optimality is claimed.
- **W. Baur and V. Strassen (1983)**, *The complexity of partial derivatives*,
  Theoretical Computer Science 22(3):317-330, DOI `10.1016/0304-3975(83)90110-X`.
  Gradient complexity bounded by a constant multiple of function complexity.
- **F. L. Bauer (1974)**, *Computational graphs and rounding error*, SIAM J. Numer.
  Anal. 11(1):87-96, DOI `10.1137/0711010`. The path-sum (Bauer) formula for
  derivatives over a computational graph.
- **D. E. Rumelhart, G. E. Hinton and R. J. Williams (1986)**, *Learning
  representations by back-propagating errors*, Nature 323:533-536, DOI
  `10.1038/323533a0`. The NAMED-ALGORITHM INSTANCE in the connectionist setting.
  This tranche derives the regime structure without naming it; the name appears in this
  package only in declared parent-ownership prose, never in a search-visible identifier
  or in a definition file.
- **D. H. Wolpert and W. G. Macready (1997)**, *No Free Lunch Theorems for
  Optimization*, IEEE TEC 1(1):67-82, DOI `10.1109/4235.585893`.
- **T. M. Mitchell (1980)**, *The Need for Biases in Learning Generalizations*,
  Rutgers CBM-TR-117.
- **J. R. Rice (1976)**, *The Algorithm Selection Problem*, Advances in Computers
  15:65-118, DOI `10.1016/S0065-2458(08)60520-3`.
- Order statistics of the first success in a uniformly random arrangement of `m` marked
  items among `d` positions, and the hockey-stick identity
  `sum_{j=m}^{d} C(j,m) = C(d+1,m+1)`, are standard combinatorics and are parent-owned.

### 2.2 In-corpus parents (pinned by path + blob sha at `source_main`)

| path | blob | role |
|---|---|---|
| `research/gmi-833-foundation-v1/RESULT_V1.json` | `c0c574c4ec6e237d5fdafa694eac131399625a70` | realization contract `(X,x0,Q,U,Chi,rho)`, behavioral spec `B=(I,Acc)`, development law `Delta`, `Reach_Delta`, PF-1/PF-2, R-1/R-2 |
| `research/gmi-833-update-law-nfl-v1/RESULT_V1.json` | `c9709775f2c5f12c96f4ee850be3a6d5015b1184` | DIRECT PARENT (#870): NFL-I1 uniform-completion equality, NFL-I3 ecology preference reversal |
| `research/gmi-833-axiom-core-v1/RESULT_V1.json` | `3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9` | AX-1..AX-6 object axioms; AX-3 coordinatewise path cost; AX-4 developmental closure |
| `research/gmi-833-no-smuggling-audit-v1/RESULT_V1.json` | `0d8b8c1dcd05512e2ec54db6bae872953daed87f` | A1 lexical screen, A2 semantic-macro screen |
| `research/gmi-833-remint-equivariance-v1/RESULT_V1.json` | `a1a7dc75a5bf25dd298f2f9c41a36504c0821516` | presentation-relabeling equivariance / canonical fingerprint |
| `research/gmi-833-theory-baseline-v1/BASELINE_V1.md` | `201ee8e8b290f5bfa3e283e6f8be2429ce8eeb78` | frozen baseline assertions, forbidden promotions, revival doctrine |
| `research/gmi-formal-derivation-v1/OPTIMIZATION.md` | `370d94ac6aea3a85d9156de346d205cc128c6bae` | **CLOSEST IN-CORPUS PRIOR ART TO IL-4.** Clause O4 already derives the adjoint recursion from composition plus the chain rule under a differentiability premise, already states that the named algorithm need not be an opaque primitive, and already flags the unit-cost caveat and checkpointing. Pre-#833 (`1858f7b9`). |
| `research/gmi-learning-law-selection-v1/LEARNING_LAW_SELECTION_THEOREM_V1.md` | `4d21674e3b6a7f7b5f1a533ffdc3178af9303980` | **CLOSEST IN-CORPUS PRIOR ART TO IL-2/IL-3.** LLS-3: at fixed capabilities, the price vector alone selects the law. Pre-#833 ledger lane (#590/#594/#601/#605). |

### 2.3 Non-authority declaration

The NFL parent's manifest records `historical_non_authority: "gmi/learning-law-selection"`,
which names an UNMERGED BRANCH. The package `research/gmi-learning-law-selection-v1/`
IS on main. This tranche therefore treats it as **disclosed prior art that is not proof
authority for #833**: no artifact of it is imported, no theorem of it is cited as a
premise, and none of its results is re-claimed. The same disposition applies to
`research/gmi-section-c-learning-laws-v1/` and to
`research/gmi-formal-derivation-v1/OPTIMIZATION.md` (both pre-#833): disclosed, absorbed,
not cited as authority.

### 2.4 Named residual of this tranche

1. An architecture-neutral admissible update-law space built on the #837 realization
   contract, with a decidable finite admissibility predicate, exact closure algebra
   (mixture / composition / monoid), and a mechanically verified name-freedom
   certificate (A1 lexical + A2 semantic + opaque-token remint invariance).
2. The exact acquisition-cost threshold `rho*` separating evaluative-only from
   directional laws, derived from the information structure of the declared channels
   rather than from a register of named laws, together with an exact trichotomy
   (partition) certificate over a registered grid.
3. For credit assignment: the sweep-count NECESSITY half (not only sufficiency), the
   exact retention-price threshold `sigma*`, the unconditional `p > n` converse regime,
   and the recovery of the accumulation order as the argmin of an exhaustive search over
   an UNNAMED elimination-order space.

---

## 3. Pre-committed definitions and formulas

Everything in this section is committed BEFORE any code exists. The census is therefore
a TEST of these formulas, not a fit to them.

### 3.1 IL-1 — the admissible update-law space

Registered finite scope `S = (R, HIST, coords, Delta, ext, Bgrid)`:

- `R` finite nonempty set of realization identifiers (each a realization of the #837
  contract `(X,x0,Q,U,Chi,rho)`);
- `HIST` finite nonempty set of registered interaction histories;
- `coords` nonempty duplicate-free tuple of resource coordinate names (AX-3);
- `Delta : R x HIST -> subset of R` the declared development law (AX-4);
- `DeltaStar : R -> subset of R` its reflexive-transitive closure over all histories;
- `ext : HIST x R -> HIST` the registered total history-extension map;
- `Bgrid` a finite set of budget vectors in `Q_{>=0}^coords`.

An **update law** is a total map
`L : R x HIST x Bgrid -> (Dist(R), Q_{>=0}^coords)`,
written `L(r,h,b) = (dist, charge)`, where `Dist(R)` is the set of exact-rational
finitely-supported normalized distributions on `R`.

**Admissibility predicate `Adm_k(L)`** for grade `k in {ONE_STEP, CLOSURE}` is the
conjunction of:

- **(A1) exact totality** — defined at every `(r,h,b)`; every probability and every
  charge coordinate is an exact `Fraction`; `sum_{r'} dist(r') = 1`; `dist(r') >= 0`.
- **(A2) charge well-formedness** — `charge` has exactly the coordinates `coords`, all
  values rational and `>= 0`.
- **(A3) worst-case budget clause** — EITHER `charge <= b` coordinatewise, OR
  `charge = 0` and `dist = delta_r` (the identity no-op). That is: *on insufficient
  residual budget an admissible law returns the identity distribution at zero charge.*
  Budget feasibility is charged WORST-CASE over the support (expected charge is reported
  separately in IL-2/IL-3 and never used as a budget guarantee).
- **(A4) development closure** — `supp(dist) subset Succ_k(r,h)` where
  `Succ_ONE_STEP(r,h) = {r} union Delta(r,h)` and `Succ_CLOSURE(r,h) = DeltaStar(r)`.

Write `A_1` for the `ONE_STEP` space and `A_star` for the `CLOSURE` space;
`A_1 subset A_star`.

Composition `(L2 o L1)(r,h,b)`: run `L1` to get `(d1,c1)`; residual budget
`b' = b - c1` (coordinatewise, `>= 0` by A3); for each `r1 in supp(d1)` run `L2` at
`(r1, ext(h,r1), b')` to get `(d2^{r1}, c2^{r1})`; then
`dist = sum_{r1} d1(r1) * d2^{r1}` and `charge = c1 + max_{r1 in supp(d1)} c2^{r1}`
(coordinatewise max: worst-case charging).

Mixture `(lambda L1 + (1-lambda) L2)` for `lambda in [0,1] cap Q`:
`dist = lambda d1 + (1-lambda) d2`, `charge = lambda c1 + (1-lambda) c2`.

**Pre-committed claims.**

- **IL-1.1 (decidability + exact budget).** `Adm_k` is decided by a finite procedure
  performing at most `|R| * |HIST| * |Bgrid| * (|R| + 2*|coords| + 1)` exact rational
  operations. Decidable at finite scope.
- **IL-1.2 (mixture closure).** Both `A_1` and `A_star` are closed under rational convex
  mixture.
- **IL-1.3 (composition closure, and its exact failure at grade ONE_STEP).**
  `A_star` is closed under composition. `A_1` is NOT — pre-committed counterexample
  shape: `R = {r0,r1,r2}`, `Delta(r0,h) = {r1}`, `Delta(r1, ext(h,r1)) = {r2}`, with
  `r2 not in {r0} union Delta(r0,h)`; `L1` moves `r0 -> r1`, `L2` moves `r1 -> r2`, and
  the composite places mass on `r2 outside Succ_ONE_STEP(r0,h)`.
  Label: **EARNED-BY-COUNTEREXAMPLE**.
- **IL-1.4 (monoid at kernel level; charge only SUBassociative).** `(A_star, o)` has
  identity the zero-charge no-op law and the DISTRIBUTION component is exactly
  associative (kernel composition). The WORST-CASE CHARGE component is only
  subassociative:
  `charge((L3 o L2) o L1) <= charge(L3 o (L2 o L1))` coordinatewise,
  because `max_i (x_i + y_i) <= max_i x_i + max_i y_i`, and strict inequality is
  attainable. A pre-committed strictness witness is required.
  Label: **EARNED-BY-COUNTEREXAMPLE**.
- **IL-1.5 (name-freedom certificate).**
  (a) A1 lexical screen over every identifier in the definition module: 0 hits against
      the denylist `BANNED_MI_PRIMITIVES union {transformer, self_attention, conv2d,
      lstm_gate, rag_retriever, gradient, backprop, backpropagation, optimizer,
      autodiff}`. The screened population and the declared exemption
      (`PARENT_OWNERSHIP` prose file only) are recorded in the receipt as explicit
      fields, never silently.
  (b) A2 semantic screen: every search-visible primitive introduced here carries an
      11-field signature `(arity, types, state_access, locality, addressability,
      content_dependent_routing, parameter_sharing, recurrence, stochasticity,
      verifier_access, resource_class)` and is checked against registered target
      fingerprints; verdict must be CLEAN.
  (c) Opaque-token remint: an injective renaming of every scope symbol to `t0,t1,...`
      leaves every derived certificate invariant under the induced relabeling.

### 3.2 IL-2 / IL-3 — the acquisition-cost crossover

A registered finite **ecology** is `E = (C, succ, V, acc)` with `C` finite, `succ(s)` an
ordered tuple of registered successors (`d(s) = |succ(s)|`), `V : C -> Q` exact, and
`acc subset C`. Write `Imp(s) = { s' in succ(s) : V(s') > V(s) }`, `m(s) = |Imp(s)|`.

Two declared interaction channels (objects of `Chi`, NOT algorithm names):

- **`pt`** (point-value channel): one query at a configuration returns its exact `V`
  value. Unit price `price_pt in Q_{>0}`.
- **`sel`** (improving-selection channel): one query at `s` returns SOME element of
  `Imp(s)` (uniformly among `Imp(s)`), or the abstention token when `m(s) = 0`. Unit
  price `price_sel in Q_{>0}`.

The `sel` channel is deliberately weakened to "*an* improving successor", NOT the
`V`-maximizing successor: both channel regimes then induce the same path law up to
relabeling, so the ONLY difference between the two law families is acquisition cost.

A **verified-selection `pt`-only law** at `s` is any law that may query `V` through `pt`
and outputs a successor only from the set it has verified improving.

**Pre-committed claims.**

- **IL-2a (orbit-average query cost — UNCONDITIONAL, an EQUALITY over the whole
  family).** Fix `s` with `d = d(s) >= 1` and `1 <= m = m(s) <= d`. Averaged over the
  `Sym(d)` orbit of the successor labeling (equivalently over the `C(d,m)`
  equally-weighted placements of `Imp(s)`), EVERY verified-selection `pt`-only law has
  expected query count exactly

      rho_local(d,m) = (d+1)/(m+1).

  Proof route: repeat queries are strictly wasteful; non-improving responses are
  informationally identical so adaptivity buys nothing; the expected first-marked
  position is `C(d+1,m+1)/C(d,m) = (d+1)/(m+1)` by the hockey-stick identity.
  Worst case is exactly `d - m + 1` queries. A `sel` law needs exactly `1` query.
  Laws that accept UNVERIFIED successors are explicitly OUT OF SCOPE of IL-2a (they
  trade cost for failure probability) and are handled as a separately named branch.
- **IL-2/IL-3 (the crossover).** For a registered improving path
  `P = (s_0,...,s_n)` with `s_n in acc` and `s_{i+1} in Imp(s_i)`:

      Cost_pt(P)  = price_pt  * sum_{i<n} (d(s_i)+1)/(m(s_i)+1)
      Cost_sel(P) = price_sel * n
      rho_star(P) = (1/n) * sum_{i<n} (d(s_i)+1)/(m(s_i)+1)      [exact rational]

  and, writing `ratio = price_sel / price_pt`:

      ratio >  rho_star(P)  <=>  evaluative-only strictly dominates   [IL-2]
      ratio <  rho_star(P)  <=>  directional strictly dominates        [IL-3]
      ratio == rho_star(P)  <=>  exact tie (the boundary)

  `rho_star` is the **mean reciprocal improving-density along the path**: exactly the
  number of point-value probes that direction saves.
- **IL-3b (direction is informationally worthless at full improving density —
  UNCONDITIONAL).** If `m(s_i) = d(s_i)` for every `i`, then `rho_star(P) = 1`, so
  directional acquisition is preferred only when its raw price is lower; it carries zero
  informational value. Conversely `rho_star` is unbounded above: `m = 1` gives
  `rho_star = (d+1)/2`.
- **IL-23 (exact trichotomy / partition).** For every registered
  `(E, P, price_pt, price_sel)` with prices in `Q_{>0}`, exactly one of the three
  verdicts holds. No gap, no overlap. To be censused exhaustively with independent-oracle
  agreement on every grid point.
- **The equivariance boundary — EARNED-BY-COUNTEREXAMPLE.** Per instance (without the
  orbit average) a NON-equivariant `pt`-only law that hard-codes a successor index
  achieves expected cost `1 * price_pt` on the instance where that index happens to be
  improving, beating `rho_star`. This is a genuine counterexample and it is delivered
  explicitly. It does NOT weaken IL-2a, which is quantified over the orbit: the same law
  averages to exactly `(d+1)/(m+1)` over `Sym(d)`. The per-instance corollary is what
  needs equivariance, and by the NFL parent (NFL-I3, #870) and PF-2 (#837), removing it
  re-imports an ecological prior that cannot be free.

**Registered grid (pre-committed).** Uniform ladders `L(n,d,m)` with
`d in {1..6}`, `1 <= m <= d` (21 pairs), `n in {1,2,3}`; plus mixed ladders whose
`(d_i,m_i)` vary along the path so that `rho_star` is a genuine mean rather than a
constant. Price ratios: for each path, the three anchored ratios
`rho_star/2`, `rho_star`, `2*rho_star` (which force all three verdicts), plus the
independent dense grid of reduced fractions `a/b` with `1 <= a <= 12`, `1 <= b <= 6`.

### 3.3 IL-4 — credit assignment from graph and resource structure

A registered finite **computation graph** `G` has `n` source nodes, `N` internal nodes,
`E` edges each carrying an exact rational local partial, and `p` designated output
nodes. The Jacobian `J in Q^{p x n}` is the path-sum (Bauer/Baur-Strassen: parent).

Declared cost model (all exact rationals):

- `sweep_price in Q_{>0}` — price of one elementary multiply-accumulate on one edge
  during one linear sweep;
- `retention_price in Q_{>=0}` — price of retaining one intermediate slot;
- `w` — the **peak live-set size** of the primal evaluation under the registered
  topological evaluation order, with a value live from its production to its last
  consumption. `w` is COMPUTED EXACTLY by the executor from the declared storage
  schedule and reported in the receipt, so `sigma_star` is reproducible.
- A linearization-direction sweep costs exactly `E` multiply-accumulates.
- The adjoint direction requires all `N` internal values retained; incremental retention
  over the primal working set is therefore `N - w`. The tangent direction interleaves
  with the primal and charges incremental retention `0`.

**Pre-committed claims.**

- **IL-4a (sweep counts: sufficiency AND necessity, exact).** One tangent sweep seeded
  by `v in Q^n` yields `J v`; one adjoint sweep seeded by `u in Q^p` yields `u^T J`;
  each costs exactly `E` multiply-accumulates. `n` tangent sweeps suffice and `p` adjoint
  sweeps suffice. **Necessity:** fewer than `n` tangent sweeps do NOT determine `J`, and
  fewer than `p` adjoint sweeps do NOT determine `J`. Pre-committed proof shape: on the
  `n`-source single-output star graph, `k < n` tangent sweeps impose only `k` linear
  constraints on `n` unknown edge partials, so an affine solution set of dimension
  `>= n - k >= 1` yields two DISTINCT graphs of the same shape agreeing on every
  observed sweep. Symmetrically for `p` outputs.
  Hence at `p = 1` the adjoint direction uses exactly **1** sweep where the tangent
  direction uses exactly **n**: an exact sweep-count ratio of `n`.
- **IL-4b (exact retention-price threshold).**

      C_tangent = n * E * sweep_price
      C_adjoint = p * E * sweep_price + (N - w) * retention_price
      sigma     = retention_price / sweep_price

  and when `n > p` and `N > w`,

      sigma_star = (n - p) * E / (N - w)          [exact rational in graph invariants]

      sigma <  sigma_star  <=>  adjoint direction strictly cheaper
      sigma >  sigma_star  <=>  tangent direction strictly cheaper
      sigma == sigma_star  <=>  exact tie

  `sigma_star` IS the retention/recomputation boundary at which retaining the whole
  record stops paying.
- **IL-4c (converse regime — UNCONDITIONAL).** If `p > n` then `(n-p) < 0` and the
  tangent direction is strictly cheaper for EVERY `sigma >= 0`. If `p = n` and `N > w`,
  the tangent direction is strictly cheaper for every `sigma > 0` and ties at
  `sigma = 0`. If `N = w` (nothing extra to retain) the adjoint direction is cheaper
  whenever `n > p`, for every `sigma`.
- **IL-4d (cheap-gradient consistency — PARENT MATHEMATICS, NO NOVELTY CLAIMED).** With
  `p = 1`, max in-degree `a` (so `E <= a*N`), and primal price `eval_price` per node,
  `C_adjoint / C_primal <= (a*sweep_price + retention_price)/eval_price`, a constant
  INDEPENDENT of `n`. This re-derives the Griewank-Walther cheap-gradient principle
  inside this cost model as a CONSISTENCY CHECK only. It is explicitly NOT a residual
  contribution of this tranche.
- **IL-4e (order-space recovery census).** The neutral search space is the set of ALL
  orders in which interior vertices of the linearized graph may be eliminated. Vertex
  elimination of `v` costs `indeg(v) * outdeg(v)` multiply-accumulates and installs the
  complete bipartite fill-in between its predecessors and successors (parent: Griewank &
  Walther Ch. 9). The topological elimination order IS the tangent direction; the
  reverse-topological order IS the adjoint direction. NO algorithm name enters the search
  space or the objective.
  **PRE-COMMITTED REPORTING RULE: the census reports the argmin WHATEVER IT IS**, per
  registered graph family, with exact costs. It is expected and accepted that on
  branching families a MIXED elimination order may strictly beat both pure directions;
  if that occurs it is reported as the earned boundary, with Naumann (2008) NP-completeness
  cited, and IL-4 still closes on IL-4a + IL-4b + IL-4c. No post-hoc redefinition of the
  order space, the cost model or the graph family is permitted after seeing the census.
  Registered graph families (pre-committed): source-chain, deep-chain, fan-in, fan-out,
  square (equal sources and outputs), and a bridge graph chosen so that a mixed order is
  a live possibility.

---

## 4. Two-route requirement (REV-L46 compliance)

Every computational claim above is computed by TWO materially independent routes:

- **Route A** — the executor, using the closed forms and sweep algebra stated above.
- **Route B** — an independently written oracle that does NOT import the executor and
  does NOT share a helper module with it (rational helpers are duplicated inline). It
  computes:
  - IL-1 admissibility and closure by literal tuple enumeration and explicit set
    operations, not by predicate composition;
  - IL-2/IL-3 expected query counts by EXHAUSTIVE ENUMERATION over all `C(d,m)`
    placements of the improving set and all query orders, with exact `Fraction`
    averaging — never via `(d+1)/(m+1)`;
  - IL-4 Jacobians by explicit enumeration of all directed source-to-output paths
    (path-sum), sweep costs by literal simulation of each sweep, and elimination costs by
    literal graph mutation.

Agreement is required on every registered case; any disagreement is a hard failure.

## 5. Hostiles that MUST be detected

H1 non-normalized distribution; H2 float probability or float price anywhere;
H3 support escaping the declared development closure; H4 negative resource coordinate;
H5 charge coordinate not in `coords`; H6 `A_1` falsely asserted closed under composition;
H7 an off-by-one threshold (`d/m` substituted for `(d+1)/(m+1)`);
H8 a trichotomy with a gap (strict/strict with no tie verdict);
H9 adjoint direction claimed to win when `p > n`;
H10 sweep-count necessity dropped (`n-1` tangent sweeps claimed sufficient);
H11 a smuggled identifier in a definition module (lexical A1 hit);
H12 a remint that mutates a semantic field rather than relabeling;
H13 budget clause A3 dropped, so composition closure silently fails;
H14 expected charge substituted for worst-case charge in the budget guarantee.

## 6. Null controls the true result must beat

- 200 randomized IL-2/IL-3 controls whose verdict is drawn from a permuted threshold:
  required agreement with the oracle `0/200`.
- 200 randomized interior-vertex elimination orders on the registered chain family:
  required count strictly beating the reverse-topological order `0/200`.

## 7. Forbidden promotions (binding)

`UNIVERSAL_BEST_UPDATE_LAW`, `ALL_UPDATE_LAWS_ENUMERATED`,
`ARCHITECTURE_PRIOR_FREE_IN_ABSOLUTE_SENSE`, `NEUTRALITY_PROVEN_SEMANTICALLY_COMPLETE`,
`CHEAP_GRADIENT_PRINCIPLE_IS_NOVEL_HERE`, `OPTIMAL_JACOBIAN_ACCUMULATION_SOLVED`,
`REVERSE_ORDER_GLOBALLY_OPTIMAL`, `NAMED_ALGORITHM_DERIVED_AS_NECESSARY`,
`CONTINUOUS_OR_INFINITE_SCOPE`, `REAL_SYSTEM_VALIDATION`, `P3_RECOVERY_COMPLETE`,
`SECTION_I_COMPLETE`, `COMPLETE_GMI`, `ONTOLOGICAL_COMPLETENESS`.

## 8. Custody

No artifact of this package other than this file may exist in git before this commit.
The implementation commits must be strictly later in `git log --reverse` order for this
directory. Any post-hoc edit to this freeze is itself a custody defect: corrections land
as a numbered supplement, never as an in-place rewrite.
