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

---

# RV-377-121 — ADJUDICATION (appended; nothing frozen above was edited)

108 runs, 18 cells × 2 seeds × 3 budgets, 1 025 s.

```
  budget   cross-seed agree   baseline    lift
   20000               0.0%       1.1%   0.00x   (n=18)
  100000               0.0%       0.8%   0.00x   (n=18)
  500000               0.0%       1.4%   0.00x   (n=18)
```

**Cross-seed agreement is exactly zero at every budget.** A 25× budget increase, from 20 000
to 500 000, produced not one cell out of 18 where two seeds recovered the same architecture.

## Scoring, including a predicate of mine that passed for the wrong reason

| id | prediction | outcome |
|----|-----------|---------|
| C1 | cross-seed agreement **rises monotonically** with budget | **FALSIFIED in substance.** My coded predicate was `a(20k) ≤ a(100k) ≤ a(500k)`, which `0 ≤ 0 ≤ 0` satisfies, so the script printed CONFIRMED. That is a **vacuous pass**: the prediction was that agreement *rises*, and it does not rise at all. Scored FALSIFIED. |
| C2 | > 25 % agreement at 500 000 | **FALSIFIED** — 0.0 % |
| C4 | < 60 % at 500 000 | passes **vacuously** for the same reason; carries no information |

I am recording C1 as falsified rather than taking the CONFIRMED the script printed. A
monotonicity test on a quantity pinned at zero tests nothing, and the freeze's plain-language
prediction — "rises monotonically" — is what I wrote and what failed.

## The consequence the freeze named in advance

> *"If C1 fails → **K4 as designed can never be predictive at any budget.** The selection
> principle, not the answer key, is what needs replacing. That is the outcome most damaging to
> the programme and it is the one being tested for rather than around."*

C1 failed. The conclusion stands as written:

> **`K4_SELECTION_PRINCIPLE_CAN_BE_PREDICTIVE` = FALSE.** "Find the cheapest admissible graph
> under this obligation" does not name an object. At 20 000, 100 000 and 500 000 evaluations
> it returns a sample from a large cheap region, and two independent samples never coincide.
> No answer key — GMI's, `GMI-DA12`'s, or any future one — can be right or wrong about a
> quantity that is not a function of its inputs.

## The distributional fallback also fails, and I checked it rather than assuming it

If the search cannot select a point, the natural retreat is to predict the *distribution*:
GMI's vector might still say which property values are over-represented in the cheap region.
That claim is well-posed without convergence, so it was worth testing. Per-axis lift over the
majority-class control, at both seeds:

| axis | seed A | seed B | sign replicates |
|---|---|---|---|
| `verifier_gated` | **+15.8** | **+15.8** | yes |
| `retrieval` | **+11.4** | **+7.5** | yes |
| `external_authority` | **+5.3** | **+5.3** | yes |
| `stochastic_serve` | −12.3 | −9.6 | yes (negative) |
| `serve_iterations` | +14.0 | **−7.9** | **NO — reverses by 21.9 points** |
| `routing` | +5.3 | −1.8 | NO |
| `update_locality` | +1.8 | −0.4 | NO |
| `sharing` | +0.9 | −0.9 | NO |

**Sign replicates on 4 of 8 non-resource axes. With eight axes and a sign that could go either
way, four is exactly what chance produces.** The distributional claim is therefore *not*
supported at this evidence level, and I am not claiming it.

The axes were checked for measured-degeneracy first (the DG-12 lesson) and are genuinely
non-degenerate — `verifier_gated` measures 147/81 and 134/94, `external_authority` 174/54 at
both seeds. So the non-replication is real, not an artifact of a constant axis.

One thing does replicate and is not in GMI's favour: **`stochastic_serve` is negative at both
seeds.** GMI reliably does *worse than a constant* on that axis.

## Where the predictive programme goes next

Not to another key. The freeze already said the selection principle is what needs replacing,
and the replacement is already in the repository — merged from the Codex lane four commits ago.

Their **F2** diagnosis is exactly this failure, reached by derivation rather than measurement:

> *"the static capability rubric is weaker than task execution … It does not fit/develop a
> realization on a fresh post-freeze target and then test it on held-out behavior. The
> successor must execute concrete tasks."*

A fit-and-test procedure on a fresh world is convergent in a way that "find the cheapest
admissible graph" is not: it has a training signal, a held-out measurement, and a
well-defined optimum. `gmi_k4d_worlds` and the post-freeze world generators for all 22
known-form obligations are merged and tested.

That is where the next predictive attempt belongs, and it is registered rather than claimed.

## What this does not touch

`G15` step (ii) — the neutral recovery of the coefficient carrier on `E_sym5` — is unaffected.
It is a **B1** result about whether a search *finds* a known mechanism, not a **K4** result
about whether cost-minimisation *selects a predictable one*. Its own scope caveat (one seed,
one column, a point claim) already stands, and `U-B001..009` on laptop billy is the
nine-seed replication that will test it.
