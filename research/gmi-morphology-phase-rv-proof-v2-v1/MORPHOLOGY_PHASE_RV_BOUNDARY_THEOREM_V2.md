# Morphology Phase R/V Boundary Theorem V2 — proof strengthening at stated scope

Status: **revival package REV-L45-073-PROOF-STRENGTHENING (#833).** Strengthens
legacy claim object `GMI833_V2_LEGACY_073_MORPHOLOGY_PHASE_RV_THEO`
(package `gmi-morphology-phase-rv-v1`, doc `MORPHOLOGY_PHASE_RV_THEOREM_V1.md`,
untouched bound artifact) from its L45 weakest-support state (Theorem 1 = one-line
definitional rearrangement; Theorem 2 + Corollaries 1-4 proofless, supported only by
an 8x8 sweep witness) to **full analytic support at the claim's stated scope**.

Claim statement being supported (THEOREM_SCORES_V2.json statement_excerpt):
"Formal theorem: R/V-parameterized burden, 2-morphology phase condition, corner
regimes, held-out prediction protocol." Census class: THEOREM / ANALYTIC_DEDUCTIVE.
Every component of that statement now carries a written proof; two assertions of V1
that are false as printed are corrected **earned-by-proof** (Appendix CX).

## 0. Conventions and provenance

- Reals; `R in (0, inf)` (resource abundance), `V in [0,1]` (ecology complexity;
  V1 Definitions fix this domain), ecology `E` fixed throughout (hence `N`, `H`,
  `P`, and every `D_KL(P || Q_M)` are fixed constants).
- V1 registered constants (reused, none new): `N = 100`, `H = 50` (so `N/H = 2`),
  `alpha_v = 10`; archetype vectors (build, KL, adopt, complexity penalty cp,
  resource requirement rho = storage+compute+comm):

| M | build | KL | adopt | cp | rho |
|---|---|---|---|---|---|
| neural (n) | 15 | 0.1 | 4 | 0.3 | 40+30+20 = 90 |
| symbolic (s) | 5 | 1.0 | 1 | 4.0 | 5+5+2 = 12 |
| probabilistic (p) | 10 | 0.5 | 2 | 2.0 | 20+15+10 = 45 |

- No new numeric constants are introduced anywhere in this package; all numbers
  below are the registered ones or their exact arithmetic consequences. Theorem
  statements are symbolic; numeric values appear only in the registered
  instantiation (Section 9) and its exact-fraction control targets.

## 1. The burden family (kernel-general)

**Definition 1.1 (morphology parameters).** A morphology `M` at fixed `E` is the
tuple of reals `(a_M, b_M, rho_M)` with `rho_M > 0`, together with the shared
kernel data `(k, alpha_r)`, `alpha_r >= 0`, where the **resource kernel** `k` is
one of

- divisor kernel `div`: `k(x) = x`;
- hinge kernel `hng`: `k(x) = max(0, x - 1)`;

derived from the primitive parameters by

    a_M := B_build(M) + D_adopt(M) + (N/H) * D_KL(P || Q_M)
    b_M := (N/H) * D_KL(P || Q_M) * alpha_v + cp_M
    S_M(R) := alpha_r * k(rho_M / R)
    B_M(R, V) := a_M + b_M * V + S_M(R).

**Instantiation D (V1 doc model).** `hng` kernel, `cp = 0`, `alpha_r = 1`:
this is exactly the boxed V1 definition `B_M = B_build + (N/H) KL (1 + V alpha_v)
+ alpha_r max(0, R_M/R - 1) + D_adopt` (expand: `a_M + b_M V` with `b_M =
(N/H) KL alpha_v` regroups the V-constant and V-linear parts; `S_M` is the
resource pressure term).

**Instantiation W (V1 witness model, route 1).** `div` kernel, `alpha_r = 1`,
with the registered `cp_M > 0`: this is exactly the burden implemented by
`phase_rv_witness.py` (`build + (N/H) KL (1 + V alpha_v) + rho_M / R + cp_M V
+ adopt`). The V1 witness therefore implements a *different model* than the V1
doc's boxed definition (divisor vs hinge; an unregistered `cp * V` term). This
defect is recorded in Appendix CX-3; the theorems below cover BOTH
instantiations, so the witness is a control of a proven object.

**Definition 1.2 (pairwise difference).** For morphologies `i, j`:

    D_ij(R, V) := B_i(R, V) - B_j(R, V) = da_ij + db_ij * V + dS_ij(R)
    da_ij := a_i - a_j,  db_ij := b_i - b_j,  dS_ij := S_i - S_j
    G_ij(V) := da_ij + db_ij * V        (the asymptotic gap: lim_R->inf D_ij)

**Definition 1.3 (winner).** `M` **wins** at `(R, V)` iff `B_M(R,V) < B_M'(R,V)`
for every other `M'` (strict argmin). The winner is defined off the boundary
set `Union_ij {D_ij = 0}`.

## 2. Lemma K (resource-kernel regularity)

Fix `alpha_r >= 0`, `rho > 0`; write `S^k(R) = alpha_r * k(rho/R)`.

**K1 (values).** Both kernels map `(0, inf)` into `[0, inf)` and are finite.
*Proof.* `R > 0` implies `rho/R > 0`; `x` and `max(0, x-1)` are `>= 0` for
`x > 0`; multiplication by `alpha_r >= 0` preserves this; all quantities finite. ∎

**K2 (continuity).** `S^k` is continuous on `(0, inf)` for both kernels.
*Proof.* `R -> rho/R` is continuous and positive on `(0, inf)`; `x -> alpha_r x`
and `x -> alpha_r max(0, x-1)` are continuous on `(0, inf)`; compositions of
continuous functions are continuous. ∎

**K3 (monotonicity).** `S^k` is non-increasing on `(0, inf)`; strictly decreasing
on `(0, rho)` for `hng` and on `(0, inf)` for `div` (when `alpha_r > 0`); for
`hng`, `S ≡ 0` on `[rho, inf)`.
*Proof.* `rho/R` is strictly decreasing in `R`. For `div`: `alpha_r rho / R` is
strictly decreasing when `alpha_r > 0`, constant 0 when `alpha_r = 0`. For `hng`:
if `R < rho` then `rho/R - 1 > 0` and `S = alpha_r (rho/R - 1)`, strictly
decreasing when `alpha_r > 0`; if `R >= rho` then `rho/R - 1 <= 0` and `S = 0`;
hence `S ≡ 0` on `[rho, inf)` and the whole map is non-increasing. ∎

**K4 (limits).** If `alpha_r > 0`: `lim_{R->0+} S^k(R) = +inf` for both kernels.
Always: `lim_{R->inf} S^k(R) = 0`.
*Proof.* `rho/R -> +inf` as `R -> 0+`. For `div`, `S = alpha_r rho / R -> +inf`.
For `hng`, on `R < rho`, `S = alpha_r (rho/R - 1) -> +inf`. As `R -> inf`,
`rho/R -> 0`, so `div` gives `S -> 0` and `hng` gives `S = 0` for all
`R >= rho`. ∎

**K5 (ordering).** If `rho_i > rho_j` then `S_i(R) >= S_j(R)` for all `R > 0`,
with strict inequality for every `R < rho_i` (`hng`) resp. every `R` (`div`,
`alpha_r > 0`); equality for `hng` exactly on `[rho_i, inf)`.
*Proof (hng).* Three cells. `R >= rho_i > rho_j`: `S_i = S_j = 0`. 
`rho_j <= R < rho_i`: `S_i = alpha_r (rho_i/R - 1) > 0` while
`max(0, rho_j/R - 1) = 0` (as `rho_j/R <= 1`), so `S_i > S_j`. `R < rho_j`:
`S_i - S_j = alpha_r (rho_i - rho_j)/R > 0`. ∎
*Proof (div).* `S_i - S_j = alpha_r (rho_i - rho_j)/R > 0` for all `R > 0`. ∎

**K6 (piecewise reciprocal-affine form).** For a pair `(i, j)` partition
`(0, inf)` by the breakpoints `rho_< := min(rho_i, rho_j)`,
`rho_> := max(rho_i, rho_j)` (a single cell if `rho_i = rho_j`). On each cell,
`S_i`, `S_j`, and hence `dS_ij`, are identically `p + q/R` with constants
`p, q >= 0` (per kernel):
- `div` (one cell, all `R`): `S_M = 0 + alpha_r rho_M / R`.
- `hng`, cell `(0, rho_<)`: both active, `S_M = -alpha_r + alpha_r rho_M / R`.
- `hng`, cell `[rho_<, rho_>)`: the hungry one `h` (larger `rho`) active:
  `S_h = -alpha_r + alpha_r rho_h / R`, the light one `S_l = 0`.
- `hng`, cell `[rho_>, inf)`: both inactive, `S = 0`.
*Proof.* Immediate substitution of `k` on each cell; cell membership fixes which
of `max(0, rho_M/R - 1)`'s two branches applies. ∎

## 3. Lemma D (pairwise difference regularity)

**D1.** `D_ij` is continuous on `(0,inf) x [0,1]` and affine in `V` with slope
`db_ij`. *Proof.* K2 plus finitely many sums/products of continuous functions;
the `V`-dependence is `da + dS(R) + db * V`, affine in `V`. ∎

**D2 (R-monotonicity of dS).** If `rho_i >= rho_j` then `dS_ij(R) >= 0` for all
`R`, `dS_ij` is non-increasing on `(0, inf)`, and — when `alpha_r > 0` and
`rho_i > rho_j` — strictly decreasing on `(0, rho_i)` (`hng`) resp. `(0, inf)`
(`div`).
*Proof.* Non-negativity is K5. For monotonicity, evaluate `dS_ij` on the K6
cells (take `i` hungry, `rho_i > rho_j`; the case `rho_i = rho_j` gives
`dS ≡ 0` trivially):
- `hng`, `(0, rho_j)`: `dS = alpha_r (rho_i - rho_j)/R`, strictly decreasing
  (`alpha_r (rho_i - rho_j) > 0`).
- `hng`, `[rho_j, rho_i)`: `dS = alpha_r (rho_i/R - 1)`, strictly decreasing.
- `hng`, `[rho_i, inf)`: `dS = 0`.
- `div`, all `R`: `dS = alpha_r (rho_i - rho_j)/R`, strictly decreasing.
Each cell's expression is non-increasing (strictly where its `q > 0`), and at
each breakpoint the two adjacent expressions agree — at `R = rho_j`:
`alpha_r (rho_i - rho_j)/rho_j = alpha_r rho_i/rho_j - alpha_r`; at
`R = rho_i`: `alpha_r (rho_i/R - 1)|_{R=rho_i} = 0` — so the glued function is
continuous (K2) and non-increasing globally, with the stated strictness on
`(0, rho_i)` resp. `(0, inf)`. ∎

**D3 (limits).** If `rho_i > rho_j` and `alpha_r > 0`:
`lim_{R->0+} dS_ij(R) = +inf`; `lim_{R->inf} dS_ij(R) = 0`; for `hng`,
`dS_ij ≡ 0` on `[rho_i, inf)`. *Proof.* K6 cell forms plus K4. ∎

**D4 (V-monotonicity).** For fixed `R`, `D_ij(R, .)` is affine with slope
`db_ij`, strictly monotone iff `db_ij != 0`. *Proof.* D1. ∎

## 4. Proposition P1 (= V1 Theorem 1, full quantifier scope)

**P1.** For all morphologies `i, j` and all `(R, V) in (0,inf) x [0,1]`:

    B_i(R,V) < B_j(R,V)  iff  da_ij + db_ij * V + dS_ij(R) < 0.

*Proof.* By Definition 1.1, `B_i - B_j = (a_i - a_j) + (b_i - b_j) V +
(S_i(R) - S_j(R))` (collect terms; subtraction distributes over the sum). An
inequality `x < y` between reals is equivalent to `x - y < 0`; substituting the
collected difference gives the claim. ∎

*Honest labelling (the L45 caveat, owned).* P1 is a **definitional equivalence**:
its entire content is the regrouping of Definition 1.1. V1 presented this as the
package's theorem ("Direct from the winner criterion ... QED"); that labelling
was the weakest-support defect. P1 is retained as the anchor with its logical
status stated; the substantive phase-structure content of the claim — the parts
V1 asserted without proof — is Theorems T2-T4 below.

## 5. Theorem T2 (= V1 Theorem 2, corrected): boundary structure

**Hypotheses H2:** `db_ij != 0`. Define the phase boundary
`Gamma_ij := {(R,V) in (0,inf) x [0,1] : D_ij(R,V) = 0}` and
`V*_ij(R) := -(da_ij + dS_ij(R)) / db_ij`.

**T2(i) (graph).** `Gamma_ij = {(R, V*)_ij(R)}` — the graph of `V*_ij`, and
`V*_ij` is continuous on `(0, inf)`.
*Proof.* For fixed `R`, `D_ij(R,V) = db_ij * (V - V*_ij(R))` (expand the right
side: `db_ij V - db_ij V* = db_ij V + da + dS` ✓). So `D = 0` iff
`V = V*_ij(R)`. Continuity: `dS_ij` is continuous (K2), `db_ij != 0`, and
arithmetic operations preserve continuity. ∎

**T2(ii) (piecewise reciprocal-affine form).** On each K6 cell, `V*_ij` is
identically `C_0 + C_1/R` with explicit constants:
- `div` (single cell, all `R > 0`): `V* = -(da_ij + alpha_r (rho_i - rho_j)/R) / db_ij`.
- `hng`, `rho_i != rho_j` (hungry `h`, light `l`, cells as in K6):
  - `(0, rho_<)`: `V* = -(da_ij + alpha_r (rho_i - rho_j)/R) / db_ij`
  - `[rho_<, rho_>)`: `V* = -(da_ij + sigma * (alpha_r * rho_h / R - alpha_r)) / db_ij`
    (with `sigma := +1` if `i` is the hungry one, `sigma := -1` if `i` is the
    light one)
  - `[rho_>, inf)`: `V* = -da_ij / db_ij` (constant in `R`).
- `hng`, `rho_i = rho_j`: `dS ≡ 0`, so `V* ≡ -da_ij/db_ij` (single constant piece).
*Proof.* Substitute the K6 cell forms of `dS_ij` into T2(i); on the middle
  cell `dS_ij = S_h - S_l` scaled by `sigma` according to which of `i, j` is
  hungry. ∎

**T2(iii) (correction of V1 Theorem 2's shape claim; earned-by-proof).** V1
asserted: "This is a piecewise-linear boundary with up to 2 segments (one per
morphology's resource pressure becoming active)." Both parts are corrected:
1. *Not piecewise-linear in general.* On any cell with `C_1 != 0`,
   `dV*/dR = -C_1/R^2` and `d^2 V*/dR^2 = 2 C_1 / R^3 != 0`, so `V*` is not
   affine in `R` on that cell; it is a translate of a rectangular hyperbola.
   Linearity holds only where `C_1 = 0`: the `hng` constant cell `[rho_>, inf)`,
   and the degenerate `rho_i = rho_j` case.
2. *Up to three segments, not two.* The two activation events (`rho_>` of the
   hungry morphology, `rho_<` of the light one) cut `(0, inf)` into at most
   THREE cells (K6), giving at most three boundary segments; "one segment per
   activation event" undercounts by one (n+1 cells from n breakpoints).
*Proof.* Differentiation of `C_0 + C_1/R` as displayed; segment count is the K6
cell count. ∎

**T2(iv) (comparative statics).** If `rho_i > rho_j` and `db_ij < 0` then
`V*_ij` is non-increasing on `(0, inf)`, strictly decreasing on `(0, rho_i)`
(`hng`) resp. `(0, inf)` (`div`).
*Proof.* For `R2 > R1`, D2 gives `dS(R2) <= dS(R1)`, hence
`da + dS(R2) <= da + dS(R1)`; dividing by `-db_ij > 0` preserves the inequality:
`V*(R2) = (da + dS(R2))/(-db) <= (da + dS(R1))/(-db) = V*(R1)`. Strictness
follows from D2's strictness. ∎

## 6. Lemma SC (single-crossing comparison)

**SC.** Let `f, g: (0,inf) -> R` be continuous non-increasing with
`lim_{R->0+} f = lim_{R->0+} g = +inf` and `g(R) < f(R)` for all `R > 0`. If `f`
has a zero `R_f`, then `g` has a leftmost zero `R_g` and `R_g < R_f`.
*Proof.* `g(R_f) < f(R_f) = 0`. Since `g(0+) = +inf > 0`, the intermediate value
theorem gives a zero of `g` in `(0, R_f)`; let `R_g := inf{R > 0 : g(R) <= 0}`
(the leftmost zero, well defined and positive since `g -> +inf` at `0+`).
Continuity gives `g(R_g) = 0` (limits from both sides bracket 0), and
`R_g <= ` (some zero in `(0, R_f)`) `<= R_f`; if `R_g = R_f` then
`g(R_f) = 0`, contradicting `g(R_f) < 0`. Hence `R_g < R_f`. ∎

## 7. Theorem T3 (= V1 Corollary 2, corrected): R-axis law

**Hypotheses H3** (pair `(n, s)`, "n hungrier and better aligned"):
`rho_n > rho_s`, `db_ns < 0`, `alpha_r > 0`. Fix `V in [0,1]`; write
`D(R) := D_ns(R, V)`, `G(V) := G_ns(V)`.

**T3(i) (monotonicity + limits).** `D` is continuous and non-increasing on
`(0, inf)`, strictly decreasing on `(0, rho_n)` (`hng`) resp. `(0, inf)`
(`div`); for `hng`, `D ≡ G(V)` on `[rho_n, inf)`; `lim_{R->0+} D = +inf`;
`lim_{R->inf} D = G(V)`.
*Proof.* `D = G(V) + dS_ns(R)`; apply D2 and D3 with `rho_i = rho_n > rho_s`. ∎

**T3(ii) (existence + uniqueness of the resource crossover).** If `G(V) < 0`
then there is a unique `R*(V) in (0, rho_n)` (`hng`) resp. `(0, inf)` (`div`)
with `D(R*(V)) = 0`; `D > 0` on `(0, R*)` and `D < 0` on `(R*, inf)`.
*Proof.* Existence: `D(0+) = +inf > 0`; and `D(rho_n) = G(V) < 0` for `hng`
(T3(i) identity), resp. for `div` pick `R_0` with `D(R_0) < 0` (exists since
`D -> G(V) < 0`); IVT gives a zero in `(0, rho_n)` resp. `(0, R_0)`.
Uniqueness and the sign pattern: `D` is strictly decreasing on `(0, rho_n)`
(resp. everywhere) by T3(i); for `hng`, `D ≡ G(V) < 0` on `[rho_n, inf)` so no
further zero exists and the sign there is negative. ∎

**T3(iii) (no-crossing regime).** If `G(V) >= 0` then `D(R) > 0` for all
finite `R < rho_n` (`hng` strict regime) resp. all `R` (`div`): s strictly wins
at every finite abundance. Degenerate tie case (`hng`, `G(V) = 0`): `D ≡ 0` on
`[rho_n, inf)` — the boundary contains the whole ray
`[rho_n, inf) x {V}` — while `D > 0` on `(0, rho_n)` still separates strictly.
*Proof.* `D` strictly decreases to its infimum `G(V) >= 0` on the strict cell,
so `D > G(V) >= 0` there; the `hng` identity `D ≡ G(V)` on `[rho_n, inf)`
finishes both claims. ∎

**T3(iv) (corrected crossover closed forms).** Assume `G(V) < 0`, `alpha_r > 0`,
`rho_n > rho_s`. Then:

- `div` kernel (single cell): `R*(V) = alpha_r (rho_n - rho_s) / (-G(V))`.
- `hng` kernel, two branches with exactly one valid:
  - both-active branch `R*_A := alpha_r (rho_n - rho_s) / (-G(V))`, valid iff
    `R*_A < rho_s`, i.e. `alpha_r (rho_n - rho_s) < -G(V) * rho_s`;
  - n-active branch `R*_B := alpha_r * rho_n / (alpha_r - G(V))`, valid iff
    `rho_s <= R*_B < rho_n`, i.e. `alpha_r (rho_n - rho_s) >= -G(V) * rho_s`
    (the upper bound `R*_B < rho_n` holds automatically: `R*_B < rho_n iff
    alpha_r < alpha_r - G(V) iff G(V) < 0`).

Each valid branch equals the unique zero of T3(ii).
*Proof.* Solve `D = 0` cellwise using K6 forms. `div`: `G(V) + alpha_r
(rho_n - rho_s)/R = 0 iff R = alpha_r (rho_n - rho_s)/(-G(V))` (division by the
positive `-G(V)`). `hng` cell `(0, rho_s)`: same equation, same root `R*_A`,
valid iff it lands in the cell. `hng` cell `[rho_s, rho_n)`: `G(V) +
alpha_r (rho_n/R - 1) = 0 iff rho_n/R = 1 - G(V)/alpha_r iff R = alpha_r rho_n
/ (alpha_r - G(V)) = R*_B`. The validity conditions are complementary (compute
`R*_B >= rho_s iff alpha_r rho_n >= rho_s (alpha_r - G(V)) iff alpha_r
(rho_n - rho_s) >= -G(V) rho_s`, i.e. the negation of branch A's condition), so
exactly one branch applies, and by T3(ii) uniqueness it is THE zero. ∎

*Correction record (Appendix CX-1).* V1 Corollary 2 printed
`R*(V) = alpha_r (R_neural - R_symbolic) / [Delta B_build + (N/H)(KL_1 - KL_2)
(1 + V alpha_v) + Delta D_adopt]`. The bracket IS `G(V)`, which is negative
throughout the crossing regime `G(V) < 0` (necessary for a crossover at all,
T3(ii)); the printed quotient is therefore negative, not a resource level — a
sign error — and the formula additionally omits the branch condition of
T3(iv) and the hypotheses H3. Corrected form: T3(iv).

**T3(v) (comparative statics: ecology complexity lowers the crossover).** If
`V1 < V2` with `G(V1), G(V2) < 0`, then `R*(V2) < R*(V1)`.
*Proof.* `D_{V2}(R) = D_{V1}(R) + db (V2 - V1) < D_{V1}(R)` for all `R` (as
`db < 0`). `f := D_{V1}` and `g := D_{V2}` satisfy Lemma SC's hypotheses by
T3(i); `f`'s zero is `R*(V1)`; SC gives `R*(V2) < R*(V1)`. ∎

## 8. Corollary C3 (= V1 Corollary 3, corrected): V-axis law

**Hypotheses H3.** Fix `R > 0`.

**C3(i) (unique crossing, corrected formula).** `D_ns(R, .)` is strictly
decreasing affine (slope `db < 0`), crossing zero at exactly

    V*(R) = (da_ns + dS_ns(R)) / (-db_ns),

and n strictly wins at `(R, V)` iff `V > V*(R)`. The crossing is interior to
the claim domain (`0 < V*(R) < 1`) iff `0 < da_ns + dS_ns(R) < -db_ns`; if
`V*(R) >= 1`, s wins the whole V-domain at that R; if `V*(R) <= 0`, n does.
*Proof.* D1/D4 and the T2(i) identity `D = db (V - V*)`; the interior
condition transposes `0 < V* < 1` multiplying by `-db > 0`. ∎

*Correction record (Appendix CX-2).* V1 Corollary 3 printed the numerator as
`B_build(neural) - B_build(symbolic) + alpha_r (max(0, R_neural/R - 1) -
max(0, R_symbolic/R - 1))`: the build-difference and resource-difference signs
are INVERTED relative to the true numerator `-(da + dS) = -[Delta B_build +
Delta D_adopt + (N/H) Delta KL] - dS` (equivalently: it divides `+(da + dS)` by
the positive denominator, yielding a negative threshold whenever the crossing
is interior), and it omits `Delta D_adopt` from the numerator entirely. With
the registered signs (`da_ns > 0`, `dS_ns >= 0`) the printed numerator is
positive over the wrong denominator sign, so the printed `V*` is negative
wherever the true `V*` is interior. Corrected form: C3(i).

**C3(ii) (comparative statics).** `V*(R)` is non-increasing in `R`, strictly on
the strict cells of D2 — resource abundance lowers the complexity threshold for
the hungrier, better-aligned morphology.
*Proof.* T2(iv) with `rho_n > rho_s`, `db < 0`. ∎

**Corollary C1' (= V1 Corollary 1, corner regimes; proved under explicit
hypotheses).** Assume the **full regularity R+**: `b_n < b_p < b_s` (strict
slope order), `rho_s < rho_p < rho_n` (strict resource order), `alpha_r > 0`
(pairwise H3 then holds for every pair: the better-aligned morphology is the
hungrier one). Then:

- **C1'(a) (scarce-resource corner).** There is an explicit threshold
  `R_0 > 0` such that for ALL `R < R_0` and ALL `V in [0,1]`, s strictly wins.
  One valid choice: `R_0 := min over i in {n, p} of alpha_r (rho_i - rho_s) /
  max(0, -m_{is})`, where `m_{is} := da_{is} + min(db_{is}, 0)`.
  *Proof.* For pair `(i, s)`: `min_{V in [0,1]} D_{is}(R, V) = m_{is} +
  dS_{is}(R)`. On `R < rho_s`, `dS_{is}(R) = alpha_r (rho_i - rho_s)/R` (K6),
  so `D_{is} > 0` on the whole V-domain once `alpha_r (rho_i - rho_s)/R >
  -m_{is}`, i.e. once `R < alpha_r (rho_i - rho_s)/max(0, -m_{is})` (if
  `m_{is} >= 0` the condition is vacuous and any `R` works; the min over the
  two pairs gives `R_0`). Below `R_0`, s beats n AND p, hence wins. ∎
- **C1'(b) (high-complexity corner).** At `V = 1`: n strictly wins iff
  `V*_ns(R) < 1` and `V*_pn(R) < 1` (T4(i) below); by C3(ii) both thresholds
  are non-increasing in `R`, so the set `{R : n wins at V = 1}` is an
  upper interval `(R_min_n, inf)` (possibly empty), explicit via C3(i).
- **C1'(c) (build-cost corner, V = 0).** At `V = 0` the winner is
  `argmin_M (a_M + S_M(R))`, decided by the explicit pairwise inequalities
  `da_{is} + dS_{is}(R) > 0` (i loses to s); under the registered
  instantiation this is s for every `R` (Section 9, exact).
- **C1'(d) (middle cell).** p strictly wins exactly on the sandwich band
  `{(R, V) : V*_sp(R) < V < V*_pn(R)}` (T4(ii)); the V1 table's unconditional
  "Mid V, Mid R -> Probabilistic" holds exactly where that band is nonempty
  and `(R, V)` lies in it — an explicit, checkable condition, not a default.

## 9. Theorem T4 (= V1 Corollary 4, corrected): three-morphology envelope

Fix `R > 0`; write `A_M := a_M + S_M(R)` (the V-intercept at this R) and assume
`b_n, b_p, b_s` pairwise distinct.

**E1 (pairwise crossing identity).** For `i != j`:
`B_i(R,V) - B_j(R,V) = (b_i - b_j) (V - V*_ij(R))` with
`V*_ij(R) := (A_i - A_j) / (b_j - b_i)`; `i` strictly beats `j` at `V` iff
`(b_i - b_j)(V - V*_ij) < 0`.
*Proof.* The right side expands to `(A_i - A_j) + (b_i - b_j) V` (the constant
term cancels by the definition of `V*_ij`), which is `B_i - B_j`; the last
claim transposes the sign. ∎

**E2 (transitions follow slope order).** If `i` strictly wins at `V1` and `j`
strictly wins at `V2 > V1`, then `b_j < b_i`.
*Proof.* `i` wins at `V1`: `B_i(V1) < B_j(V1)`, so `(b_i - b_j)(V1 - V*_ij) < 0`.
`j` wins at `V2`: `B_j(V2) < B_i(V2)`, so `(b_j - b_i)(V2 - V*_ij) < 0`, i.e.
`(b_i - b_j)(V2 - V*_ij) > 0`. Subtracting the two displayed inequalities:
`(b_i - b_j)(V2 - V1) > 0`; as `V2 - V1 > 0`, `b_i > b_j`. ∎

**E3 (crossing convexity).** With `b_s > b_p > b_n`:
`V*_sn = [(b_s - b_p) V*_sp + (b_p - b_n) V*_pn] / (b_s - b_n)` — a convex
combination (both weights positive, summing to 1); hence `V*_sn` always lies
between `V*_sp` and `V*_pn` (strictly, when they differ).
*Proof.* `B_s - B_n = (B_s - B_p) + (B_p - B_n) = (b_s - b_p)(V - V*_sp) +
(b_p - b_n)(V - V*_pn)` by E1 applied to the two pairs; also
`B_s - B_n = (b_s - b_n)(V - V*_sn)` by E1. Equating the two expressions and
solving for the zero: `(b_s - b_n) V*_sn = (b_s - b_p) V*_sp + (b_p - b_n)
V*_pn` (set the affine functions' constant terms equal at `V = 0`, or
equivalently compare roots of both displayed affine forms of `B_s - B_n`).
The weights `(b_s-b_p)/(b_s-b_n)` and `(b_p-b_n)/(b_s-b_n)` are positive and
sum to 1. ∎

**T4(i) (exact region predicates).** For every `(R, V)` off the boundaries:

    n strictly wins  iff  V > V*_ns(R)  and  V > V*_pn(R)
    s strictly wins  iff  V < V*_ns(R)  and  V < V*_sp(R)
    p strictly wins  iff  V > V*_sp(R)  and  V < V*_pn(R)

*Proof.* Winning = strictly beating each other morphology; apply E1 pairwise
(and note the sign of `b_i - b_j` for each registered pair to orient the
inequality). ∎

**T4(ii) (sandwich criterion).** With `b_n < b_p < b_s`, the p-region at `R` is
the interval `(V*_sp(R), V*_pn(R))` — possibly empty — and is nonempty iff
`V*_sp(R) < V*_pn(R)`, an explicit linear-fractional inequality in
`(a_M, S_M(R))` via E1's closed forms. Outside its nonempty set, the partition
at that R is two regions meeting along `V*_ns(R)`.
*Proof.* The p-predicate of T4(i) is exactly the interval condition; nonemptiness
is the stated strict inequality. For the two-region alternative, suppose the
p-band is empty, i.e. `V*_sp(R) >= V*_pn(R)`; by E3, `V*_sn` is a convex
combination of `V*_sp` and `V*_pn`, hence `V*_pn <= V*_sn <= V*_sp`. Then
`min(V*_ns, V*_sp) = V*_sn = max(V*_ns, V*_pn)`, so the s-predicate of T4(i)
reduces to `V < V*_sn` and the n-predicate to `V > V*_sn`: two regions meeting
along the single curve `V = V*_sn(R)`. ∎

**T4(iii) (winner sequence).** As `V` increases in `[0,1]`, the strict winner
takes at most 3 constant blocks, in slope-decreasing order — i.e. the sequence
is a subsequence of `(s, p, n)` under R+.
*Proof.* The set `T := {V*_ij(R)} (pairwise distinct values) in [0,1]` has at
most 3 elements; off T every pairwise order is constant (E1 signs fixed), so
the winner is constant on each open component of `[0,1] \ T` (at most 4
blocks). E2 forces the winner's slope to strictly decrease block-by-block;
with only 3 distinct slopes there are at most 3 blocks, ordered by slope;
under R+ the slope order is `b_s > b_p > b_n`. ∎

**T4(iv) (boundary curves).** Each `V*_ij : (0,inf) -> R` is continuous,
piecewise reciprocal-affine (T2(ii) applied to the pair), and — under R+ —
non-increasing (T2(iv) pairwise: the better-aligned morphology of each pair is
its hungrier one). Hence the three-phase diagram of V1 Corollary 4 exists
exactly as: s-region `V < min(V*_sp, V*_ns)`, p-band `(V*_sp, V*_pn)` where
nonempty (T4(ii)), n-region `V > max(V*_pn, V*_ns)`; boundaries piecewise
reciprocal-affine (not piecewise-linear — T2(iii)).

## 10. Proposition P5 (held-out protocol, honest status)

**P5.** Fix all parameters (the `a, b, rho` tuples, kernel, `N, H, alpha_v,
alpha_r`) before prediction, and define the measurement at a cell as the
recomputation of the strict argmin from the same frozen parameters. Then the
predicted winner equals the measured winner at EVERY cell: accuracy is
identically 1.
*Proof.* Both procedures evaluate the same finite set of burden functions
(Definition 1.1) at the same inputs and take the same strict argmin; equality
of outputs follows from substitutivity of identical inputs into a deterministic
function. ∎

*Status.* P5 is a determinism identity with **no discriminative power** (the
maturity rescore's `DEGENERATE_HELDOUT_NO_DISCRIMINATIVE_POWER` tag is correct
and is hereby owned, not disputed). It is retained as a control only. The
falsifiable content of claim object 073 is T2-T4 + C1'/C3, whose closed forms
are checkable against independent numerics — the two-route standard of
Section 11.

## 11. Two-route verification standard

- **Route 1** (existing, `gmi-morphology-phase-rv-v1`): grid argmin enumeration
  over the three burdens (`compute_phase_grid`), 8x8 registered sweep + 23
  unittests. Hereby DEMOTED to a declared control: a regression pin of the
  registered parameter point, not proof support.
- **Route 2** (new, `phase_rv_boundary_route2.py`): evaluates ONLY the closed
  forms of T2/T3(iv)/T4(i) — pairwise thresholds `V*_ij(R)` per kernel with
  branch selection by the K6 cells, region predicates, crossover branches —
  with NO burden enumeration and NO argmin. Agreement of the two routes on
  winner identity at every sampled cell (registered 8x8 grid + resolution
  ladder {40, 120, 360} over the registered domain `R in [2, 60]`,
  `V in [0.1, 0.8]` extended to the claim domain edges `V in [0, 1]`, plus
  fixed-seed random draws, seed 42 = the V1 registered seed), plus bisection
  cross-checks of `R*(V)` and `V*(R)` roots and exact-fraction re-derivations
  of every registered-instantiation number below, constitute the
  implementation cross-check required for computational proof components.
- Registered-instantiation control targets (exact; route 2 re-derives them in
  `fractions.Fraction` arithmetic):
  - Instantiation D (`hng`, `cp = 0`): `a = (n 19.2, s 8.0, p 13.0)`,
    `b = (n 2.0, p 10.0, s 20.0)`, `rho = (n 90, p 45, s 12)`; R+ holds.
    `V*_ns(inf) = 11.2/18 = 140/225 = 28/45`; `V*_sp(inf) = 5/10 = 1/2`;
    `V*_pn(inf) = 6.2/8 = 31/40`; sandwich `1/2 < 31/40` holds at `R = inf`;
    sandwich holds for ALL `R > 0` (route 2 proves this by exact evaluation
    of the finitely many K6-cell endpoint candidates of the
    reciprocal-affine difference `V*_pn - V*_sp`).
  - Instantiation W (`div`, registered `cp`): `b = (n 2.3, p 12.0, s 24.0)`;
    same `a`, `rho`; R+ holds. `V*_ns(inf) = 11.2/21.7 = 112/217`;
    `V*_sp(inf) = 5/12`; `V*_pn(inf) = 6.2/9.7 = 62/97`; sandwich
    `5/12 < 62/97` (cross-multiplied: 485 < 744) holds at `R = inf` and, the
    difference being a single reciprocal-affine cell, monotone in `R`, for all
    `R > 0`. Registered crossover example: `R*(0.8) = 78/6.16 = 1950/154 =
    975/77` (div, pair n-s), matching the witness comment "neural from R=15
    up at V=0.8" (12.66 lies between the registered grid nodes 10 and 15).

## 12. What changed relative to V1 (summary)

| V1 item | V1 status | V2 |
|---|---|---|
| Theorem 1 | definitional rearrangement labelled a theorem | P1: retained, honestly labelled; content moved to T2-T4 |
| Theorem 2 "piecewise-linear, up to 2 segments" | assertion, false as printed | T2: proved piecewise reciprocal-affine, up to 3 segments (CX) |
| Corollary 1 corner table | qualitative, unproved | C1'(a-d): proved under explicit regularity R+ |
| Corollary 2 R*(V) formula | sign error + no branch conditions | T3(iv): both branches + validity conditions |
| Corollary 3 V*(R) formula | numerator signs inverted, adopt term omitted | C3(i): corrected |
| Corollary 4 three-region sandwich | asserted | T4: exact predicates + sandwich criterion + sequence law |
| Held-out 100% | presented as prediction power | P5: honest determinism identity, demoted to control |
| 8x8 sweep + 23 tests | implicit proof support | declared control; proof support = T2-T4 via route 2 cross-check |
| witness vs doc model mismatch | unnoticed | recorded (CX-3); both covered by the kernel-general family |

## Appendix CX — corrections earned-by-proof

- **CX-1** (V1 Corollary 2): printed `R*(V)` denominator is `G(V) < 0` in the
  crossing regime, making the printed crossover negative; branch conditions and
  hypotheses H3 missing. Corrected in T3(iv).
- **CX-2** (V1 Corollary 3): numerator sign inverted (build and resource
  differences) and `Delta D_adopt` omitted; corrected in C3(i).
- **CX-3** (model/witness mismatch): V1's witness implements
  `rho_M/R + cp_M V` (divisor kernel, `alpha_r = 1`, registered cp) while the
  V1 doc's boxed definition is `alpha_r max(0, R_M/R - 1)` (hinge) with no cp
  term. Both are instantiations of Definition 1.1; all theorems cover both;
  the mismatch is closed by construction, not by editing V1.

## Terminal

```text
MORPHOLOGY_PHASE_RV_BOUNDARY_FULL_SUPPORT_AT_STATED_SCOPE
```

The claim's stated scope (R/V-parameterized burden, 2-morphology phase
condition, corner regimes, held-out protocol) is now fully covered by written
proofs at that scope; the V1 assertions that were false as printed are replaced
by their corrected, proved forms. No claim boundary was widened and none needed
to be narrowed: the strengthened statements hold at the ORIGINAL stated scope.
