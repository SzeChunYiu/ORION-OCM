# GMI #833 finite budget, niche and repricing laws v1

**Issue:** #899, child of #833 Section J  
**Freeze:** `FREEZE_V1.md`, commit `aeda8b184cf2e2384d98f02f61b0d7c9e553cfc8`  
**Claim ceiling:** `GMI_FINITE_BUDGET_NICHE_AND_REPRICING_SELECTION_LAWS_AT_REGISTERED_SCOPE`

## 1. BUDGET-1 — morphology under finite discovery budget

Let each candidate morphology `m` have fixed exact objective `J(m)` and first-availability budget `tau(m)`. At budget `B`, let `A_B={m:tau(m)<=B}` and select the complete argmin of `J` over `A_B`.

Because `A_B subseteq A_B'` whenever `B<=B'`, the best observed objective cannot worsen as budget grows. If the global optimum `m*` is unique, then for every `B>=tau(m*)`, `m*` is present and every rival has strictly worse objective, so the observed argmin is permanently `{m*}`.

This is availability-limited selection, not optimizer convergence. The exact hostile has an early candidate with objective `1` at budget `1` and a later candidate with objective `0` at budget `2`, so finite-budget morphology differs from the eventual winner.

The receipt exhausts all objective triples in `{0,1,2}^3` and all six discovery orders: 162 systems and 486 budget points, with zero monotonicity/stabilization failures.

## 2. NICHE-1 — finite operating-regime partition

Fix a finite regime set `E` with probability weights `mu(e)>=0`, `sum mu=1`, and exact cost `C(e,m)` for each morphology. For each regime keep the full winner set

`W(e)=argmin_m C(e,m)`.

For morphology `m`, define

`L(m)=sum_{e:W(e)={m}} mu(e)`

and

`U(m)=sum_{e:m in W(e)} mu(e)`.

Then `0<=L(m)<=U(m)<=1`. `L` is guaranteed unique-winner regime mass; `U` is possible winner mass when ties are unresolved. Ties therefore widen the interval rather than being allocated by an arbitrary rule.

Define **robust coexistence** when at least two morphologies have positive `L`; define **possible coexistence** when at least two have positive `U`.

The positive witness has three equally weighted regimes, each uniquely favoring a different morphology, giving exact lower/upper mass `1/3` for all three. A tie hostile shows one morphology can have lower mass `0` but upper mass `1/3`, while another spans `1/3` to `2/3`.

The executor exhausts all `2^9=512` binary 3-regime x 3-morphology cost tables and verifies every share bound.

## 3. REPRICE-1 — resource repricing transitions

Let raw resource vector be `r(m)` and let a registered price path be affine:

`w(theta)=w0+theta v`,

with every price coordinate strictly positive throughout the declared interval. The scalar score is

`S_m(theta)=w(theta) dot r(m)`,

which is affine in `theta`. Hence every pairwise equality occurs at at most one exact root unless the score functions are identical. Between consecutive pairwise roots, every pairwise ordering is fixed, so the exact winner set is constant.

This is the resource-specific specialization of the affine phase theorem from #893. Pairwise crossings that do not lie on the lower envelope are retained as diagnostic boundaries but are not promoted to morphology transitions.

### Exact witness

Use

- `A=(1,4)`
- `B=(4,1)`
- `C=(2,2)`

and price path `w(theta)=(theta,1-theta)` on `[1/5,4/5]`. Prices remain strictly positive. Pairwise crossings are exactly `1/3,1/2,2/3`. The open-cell winners are

`B | C | C | A`.

At `theta=1/2`, `A` and `B` cross but `C` remains strictly cheaper, proving a pairwise crossing need not be a morphology transition. Twelve direct exact interior checks verify cell constancy.

## 4. Boundaries

These theorems separate three causes that must not be conflated:

- finite search/discovery budget changes **availability**;
- ecology/operating regime changes **which objective/cost table applies**;
- resource repricing changes the **scalar projection of fixed raw resource vectors**.

The tranche does not establish prospective held-out transition accuracy, independent real-system replication, stochastic ecology dynamics, real-scale validity, all-known-form recovery, or complete GMI.
