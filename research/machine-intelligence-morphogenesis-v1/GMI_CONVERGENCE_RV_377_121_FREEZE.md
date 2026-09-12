# RV-377-121 — FREEZE: does the K4 search converge at all?

Frozen BEFORE the run. Outcomes appended only.

## Why this is the only well-posed question left

`RV-377-120` established that at budget 20 000 the recovered architecture is a function of the
random seed: cross-seed agreement at fixed `(family, grammar, cell)` is **0.5 %**, below a
2.01 % baseline, and **0 of 54** `(family, grammar)` pairs keep their modal winner across
seeds.

Every property-vector prediction presupposes that cost-minimisation *selects* an architecture.
If the search does not converge, there is nothing to predict, and no answer key — GMI's,
mine, or anyone's — can be right or wrong about it.

**Cross-seed agreement is the measurable that decides this, and no run in this programme has
ever measured it.** Every previous sweep used a single seed, which is exactly why the
non-convergence was invisible for so long.

## Method

A subset of the grid — the first 6 families × all 3 grammars × cell `w1` = **18 cells** — run
at **two independent seeds** at each of **three budgets**: 20 000, 100 000, 500 000.

Measured at each budget:

* **cross-seed agreement**: fraction of the 18 cells where both seeds recover the same
  8-axis winner vector;
* **baseline**: probability two randomly chosen winners from the pooled set agree;
* **lift** = agreement / baseline.

Subset rather than the full grid because 18 cells × 2 seeds × 500 000 is already ≈ 2.5 h of
the container's remaining capacity, and a clean answer on 18 cells at three budgets is worth
more than a noisy one on 264 at one budget. The subset is declared here, before the run, and
is the first 6 families in canonical order — not chosen by inspecting any result.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| C1 | **Cross-seed agreement rises monotonically with budget.** | agreement at 500 000 ≤ agreement at 20 000 |
| C2 | **At 500 000 cross-seed agreement exceeds 25 %** — i.e. the search is beginning to converge and 10⁶ is a reasonable bar. | ≤ 25 % at 500 000 |
| C3 | Within-seed agreement across cells stays high (> 50 %) at every budget — the seed keeps determining the trajectory even as budget grows. | < 50 % at any budget |
| C4 | **Even at 500 000, cross-seed agreement stays below 60 %** — convergence, if it starts, is far from complete at this scale. | ≥ 60 % |

C2 is the prediction that decides whether the K4 programme has a future at achievable budget.

* **C1 and C2 both hold** → the search converges with budget, a property-vector prediction is
  well-posed at sufficient scale, and the protected 10⁶ LUNARC run tests whether 10⁶ suffices.
* **C1 holds, C2 fails** → convergence is real but far slower than 10⁶; the programme needs a
  budget estimate before any further key is fitted.
* **C1 fails** → **K4 as designed can never be predictive at any budget.** The selection
  principle, not the answer key, is what needs replacing. That is the outcome most damaging to
  the programme and it is the one being tested for rather than around.

## What this cannot settle

Two seeds per budget gives a coarse estimate; a real convergence rate needs more. The subset is
6 of 22 families at one cell width. And convergence of the *search* is not the same as
correctness of the *key* — C1/C2 holding would make the prediction well-posed, not true.
