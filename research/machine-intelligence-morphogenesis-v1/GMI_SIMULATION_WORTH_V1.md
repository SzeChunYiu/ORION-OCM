# When model-based future simulation is worth its cost — I4 (#602)

Date: 2026-09-14. Status: **CLAIM SHARPENED BY PARTIAL FAILURE INTO A CLOSED-FORM BOUNDARY**. Closes
I4's *"derive model-based future simulation"*.

## 1. The comparison, with no new principle

Simulation is not free. The model must be retained, which CSR-1 charges, and each simulated future costs
compute. The alternative is to act and observe, paying in real mistakes.

* **act and observe** — expected wrong tries × mistake cost, or the ruin penalty if mistakes are
  irreversible;
* **simulate** — model retention + per-option simulation cost, then one correct act.

## 2. What I predicted, and the half that failed

Two claims were registered before the sweep:

| claim | outcome |
|---|---|
| with reversible mistakes, expensive mistakes flip the winner to simulation | **FAILED** |
| irreversibility favours simulation more than reversibility does | **HELD** — 8/8 irreversible cells against 3/8 reversible |

The first is too strong. At mistake cost 8 with a **cheap** model, simulation wins 7.00 against 20.00; with
an **expensive** model, acting still wins 20.00 against 24.00. Expensive mistakes flip the winner *only
when the model is cheap enough*.

## 3. The boundary the failure exposes

Simulation wins iff `model + n·sim < (n−1)/2 · mistake`, i.e.

> **`mistake > 2(model + n·sim) / (n − 1)`**

Checked against every cell at `n = 6`:

| model, sim | predicted crossover | observed flips |
|---|---:|---|
| 4, 0.5 | **2.8** | 0.5 ✗, 2 ✗, 8 ✓, 32 ✓ |
| 12, 2 | **9.6** | 0.5 ✗, 2 ✗, 8 ✗, 32 ✓ |

Exact agreement in all eight reversible cells. The claim is not "expensive mistakes favour simulation" but
a **crossover whose location is set by model cost** — which is a phase boundary, and strictly more useful
than the claim it replaces.

## 4. The structural asymmetry under irreversibility

Under irreversibility the act-and-observe cost is `(1 − 1/n) × ruin` — it **does not depend on mistake
magnitude at all**, because the outcome is dominated by the probability of ruin rather than the size of
each error. The comparison is therefore against a constant, which is why **all eight irreversible cells
fall the same way** regardless of mistake cost.

> **Irreversibility does not merely raise the cost of acting; it removes mistake magnitude from the
> comparison entirely.** That is why it favours simulation uniformly rather than gradually, and it is the
> non-obvious content here.

## 5. Scope

**Derived:** the simulate-versus-act boundary in closed form, its dependence on model cost, and the
structural asymmetry irreversibility introduces.

**Assumptions:** a uniformly distributed correct option, a perfect model (simulation always identifies the
correct option), and independent option costs. **A model with error would add a term and could reverse the
advantage** — which the planning theorem already notes for the plan-versus-amortize crossover, and which
`GMI_REPLANNING_UNDER_DRIFT_V1.md` handles for drift.

**Not derived:** where the model comes from. Retention is charged here, but acquiring an accurate model is
the acquisition problem, already covered separately.

**Falsifier:** a reversible cell violating `mistake > 2(model + n·sim)/(n−1)`, or an irreversible regime
whose winner depends on mistake magnitude.

## 6. I4 status

| box | status |
|---|---|
| goal formation | derived |
| subgoal discovery | derived |
| planning stopping rule | derived |
| plan-vs-habit crossover | covered (GKF-11) |
| **model-based future simulation** | **derived here** |
| replanning under model error/drift | derived |

**All six boxes of I4 now have a derivation.**
