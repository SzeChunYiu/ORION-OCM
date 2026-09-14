# The K4 cost model has no substitutions — a root cause for 0 of 264

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Probe: `gmi_k4_cost_structure_probe_v1.py` (reads the real cost model).
Receipt: `microscopes/results/STAGE_K4_COST_STRUCTURE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified across transfer.

Addresses the standing negative in checklist items 22, 23 and 35, and closes
`DG-11`, open since `RV-377-107`.

## What was already known, and correct

`RV-377-109` established that the K4 recovery failure is **structural, not
budgetary**. At ten times the budget not one of 264 verdicts moved, while
search winner cost changed on 194 cells — the budget was real and the target
was immobile. The freeze had named that consequence in advance and accepted it.

`DG-11` recorded that all three grammars agree on the verdict for **88 of 88**
family × cell combos while changing every numeric quantity, and left open the
challenge: exhibit one cell whose verdict differs between two grammars.

Both stand. What follows explains them rather than disputing them.

## Three questions answered by reading the cost model

No campaign was run. `gmi_k4_resource_native_v4.lifecycle` and the channel sum
the search minimises were read directly, over 4 000–6 000 sampled candidates
per cell.

### Q1 — retained state does not buy serving work

| grammar | scale | corr(storage, serve) | Pareto pts | material trade |
|---|---:|---:|---:|---|
| G1_TENSOR_GRAPH | 2 / 4 / 8 | +0.0120 / +0.0114 / +0.0113 | 2 | **no** |
| G2_SYMBOLIC_PROGRAM | 2 / 4 / 8 | −0.0141 / −0.0154 / −0.0164 | 2 | **no** |
| G3_FSM_MESSAGE | 2 / 4 / 8 | −0.0103 / −0.0097 / −0.0089 | 2 | **no** |

A retention trade-off would appear as a strong *negative* correlation. The
largest magnitude anywhere is **0.017**.

Cross-checked by quartile, which is harder to argue with than a correlation:

| quartile | median storage | median serve |
|---|---:|---:|
| Q1 low | 16.0 | 88.56 |
| Q4 high | 1024.0 | 75.28 |

> **A 64× increase in retained state buys a 1.18× reduction in serving work.**

That is not a trade-off. PVR-3's mechanism — pay storage once, save compute on
every use — has nothing to attach to.

### Q2 — no channel pair trades against any other

Across all channel pairs, **zero** have correlation below −0.3. The most
negative is `search_compute` against `serve_compute_latency` at **−0.018**.
Meanwhile:

| pair | correlation |
|---|---:|
| `description_compiler_burden` ↔ `state_storage` | **+0.9975** |
| `development_compute` ↔ `description_compiler_burden` | +0.9871 |
| `development_compute` ↔ `state_storage` | +0.9822 |

> **Every channel rises together.** Cost is one latent size factor wearing nine
> labels. There is no resource that can be bought with another.

This is the root cause. A cost-minimising search over a space with no
substitutions converges to **small**, never to **structured** — and more budget
makes it smaller, which is precisely the widening `RV-377-109` measured.

### Q3 — the grammar axis is a 1.12× scalar

Doubling `GRAMMAR_PRICE` scales **6 of 9** channels exactly; only
`state_storage` is independent of it. So the objective is
`gp · X(candidate) + Y(candidate)`, and the grammar moves one scalar.

Over a pool of 4 000 candidates:

| grammar price | winner |
|---:|---|
| 1.00 | index 644 |
| 1.08 | index 644 |
| 1.12 | index 644 |

The winner does not change **even at a 1000× price ratio**, while the actual
spread across the three grammars is **1.12×**.

> **DG-11 is closed.** The grammars agree not because the axis was tested and
> found inert, but because a common scalar on six of nine channels cannot
> change an argmin at 12 % separation. The challenge it left open — exhibit a
> cell whose verdict differs between two grammars — is unreachable by
> construction, not merely unmet. Under this cost model the grammar axis can
> never be an independent probe, and the effective K4 sample is **88**, as
> `DG-11` suspected, for a reason it did not have.

## What this does to the verdicts

`GMI_NEUTRAL_SEARCH_ADEQUACY_THEOREM_V1.md`, NS-1 consequence 2: *if no
admissible witness for the target family exists in the candidate set, failure
to recover it is `INCONCLUSIVE_GRAMMAR`, not theory falsification.*

For any target family whose defining property is a **resource substitution** —
retention, caching, compilation, amortisation, specialisation — Q1 and Q2 show
no such witness exists at any budget, in any of the three grammars, at any of
the three scales probed. Those cells are `INCONCLUSIVE_GRAMMAR`.

**This does not convert the whole 159 into `INCONCLUSIVE_GRAMMAR`.** Doing that
requires auditing each cell's target property and showing it is a substitution
claim. That audit is the next step and is not performed here. What is
established is that the *mechanism* the K4 apparatus was built to detect cannot
be expressed in the space it searches.

## The repair this names

> **A cost model in which nothing can be bought with anything else cannot
> exhibit a mechanism, because a mechanism is a purchase.**

The K4 apparatus needs at least one genuine substitution — a channel that
*falls* when another rises — before any recovery result is interpretable. The
concrete minimum: make `state_storage` and `serve_compute_latency` trade, so
that a candidate retaining more state does less work per query. Until then a
green cell would be as uninformative as a red one.

This is a repair to the instrument, not to the theory, and it is why the
0-of-264 result should not be read as evidence against GMI.

## Scope, stated plainly

- **Sampling, not exhaustion.** 4 000–6 000 `sampled_candidate` draws per cell,
  not the full `R_C(G)`. A substitution could exist in an unsampled region,
  though a correlation near zero across nine settings makes that unlikely.
- **One profile.** Correlations are computed at `reuse_multiplier = 1.0`.
  `state_storage` and `serve_compute_latency` are both flat in reuse, so the
  correlation between them does not depend on it.
- **The flip bound** is over one pool of 4 000 at scale 4 for `G1_TENSOR_GRAPH`.
- **No cell is reclassified here.** The verdict audit is named, not done.
- **`RV-377-109` is not disputed.** Its finding — that the failure is
  structural rather than budgetary — is exactly what a space with no
  substitutions predicts.

## Falsifiers

Exhibit a candidate pair in any K4 grammar where one retains substantially more
state and does substantially less serving work. Or exhibit any channel pair
with correlation below −0.3. Or exhibit a grammar price within the registered
spread that changes a winner. The probe asserts all three on every run, so any
of them turning up will fail CI rather than sit unnoticed.
