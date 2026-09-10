# RV-A one-stage attribution — evidence and discrimination

Parent: [CORE.md](CORE.md). Receipt: `results/RVA_A1_ATTRIBUTION.json`.

## What the endpoint computes

`hpc/aggregate_gs_r2.py:175` assigns the verdict:

```python
"verdict": ("SURVIVOR_T3_GENERALIZATION_HOLD" if r3["feasible"]
            else "SURVIVOR_T3_GENERALIZATION_FAIL"),
```

`r3["feasible"]` is `hard_gate_report(...)["feasible"]` — the conjunction of
`GATE_CORRECTNESS` (`harmful_transfers == 0 and stale_answers == 0`),
`GATE_INVARIANTS`, `GATE_PROTECTED_ISOLATION`, `GATE_REVOCATION_FIDELITY`
(`R != "none"`) and `GATE_CAPABILITY_FLOOR` (`solved_fraction >= 0.5`).
No solved-fraction delta between T2 and T3 enters the verdict at any point.

The label reads as a transfer measurement. The computation is a feasibility read.

## The predicate asymmetry, verbatim

`evaluation/lifetime2.py:141` (T2 `scoped_failure`, the only T2 family that can
set `harmful_transfers`):

```python
if cap["can_check"] or g.F_arch == "hierarchical_fibred":
    s._charge(s.cm["consistency_work"] * (
        0.4 if g.F_arch == "hierarchical_fibred" else 1.0), "verification")
    s.correct_refusals += 1
    solved = True
```

`evaluation/t3_ecology.py:134` (T3 `t3_doubt_probe`):

```python
if can_probe and can_check:  ...      # solved
elif can_check:              ...      # solved
else:
    s.harmful_transfers += 1          # no fibred route
```

`can_check` is defined identically in both (`lifetime2.py:55`,
`t3_ecology.py`): `("constraint_solver" in types) or (L == "scoped_nogood")`.
It is also exactly the enabling condition for the `check_consistency` operator
(`morphology/compile.py:26` plus `LEARNING_SUBSTITUTES` at `:41`).

Consequence, forced by the code and not by any fit: a checker-free organism can
clear T2 `GATE_CORRECTNESS` only via `hierarchical_fibred` (and does so at a
0.4× consistency discount), then necessarily incurs exactly one harmful transfer
per T3 call on `t3_doubt_probe`.

## Discriminating the four candidate stages

**Candidate: descriptor/representation overfit to T2.** Rejected. The verdict is
not a descriptor read at all; it is a gate read that reduces exactly to one
genome bit, with fp = fn = 0 over 100693 survivors. A representation-overfit
account predicts graded, descriptor-correlated failure. Observed failure is
binary and grammar-determined.

**Candidate: gate leakage.** Accepted, and in its strong form. The T2 admission
criterion admits on `can_check OR fibred`; the T3 correctness gate demands
`can_check`. The cross-tab is exhaustive:

| can_check | fibred | verdict | n |
|---|---|---|---|
| False | True | FAIL | 85025 |
| True | True | HOLD | 8131 |
| True | False | HOLD | 7537 |
| False | False | — | **0** (cannot survive T2) |

Every FAIL is fibred; the empty cell is the gate's own signature.

**Candidate: selection pressure (higher yield buys more non-generalizers).**
Demoted to a real but secondary effect. It cannot be primary: the frozen-parent
replication arm `GSA5P_fixed`, which runs no revival lever, is already 82.5%
FAIL on its exclusive survivors. The levers modulate the composition
(0.0541 to 0.2058 checker-bearing across arms) without creating the phenomenon.
Quantified separately in [COMPOSITION.md](COMPOSITION.md).

**Candidate: genuine non-generalizing morphology.** Rejected as stated. The
survivors do lack a real capability, but the endpoint does not measure transfer:
it has zero variance over 18 independently key-derived instance draws at
m = 153 ≥ m* = 104 (`results/RVA_A2_DRAW_INVARIANCE.json`). A genuine
generalization failure produces a distribution over `feasible_calls ∈ [0, 18]`;
the observed distribution has support {0, 18} and nothing between.

## Falsifier that was run

`hpc/rva_attrib.py` records every survivor whose verdict disagrees with the
single-bit prediction `NOT can_check ⇒ FAIL`, capped at 40 samples, and reports
`exact: true` only when both error counts are zero. The field
`contradiction_samples` in the receipt is empty and `false_pos = false_neg = 0`.
The capability bit is derived from `grammar_signature` (the search's own frozen
grammar key), independently of the evaluation path that produced the verdicts.

## What this does not claim

It does not claim the T3 battery is wrong to require a checker, nor that the
84.4% is a defect in the zoo's physics. It claims the recorded number is a
population-composition statistic reported under a transfer label, and that any
revival must therefore move an **absolute** count of checker-bearing viable
survivors rather than a rate.
