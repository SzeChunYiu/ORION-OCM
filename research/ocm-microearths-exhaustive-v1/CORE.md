# EB-F0-X — Exhaustive Micro-Earths (START HERE)

Issue #296 §16. Lane branch `bio/ebf0-microearths`. Binds the frozen EB-F0
contract at `af4fa91e` (`../ocm-digital-biosphere-formal-v1/FREEZE_V1.json`).

**Scope.** Exhaustive 2–8 organism biospheres where ground truth is
enumerable, used to machine-check the BIO-T rows and to show every formal
instrument can *fail*. This is EB-F0 infrastructure. It does not start #292's
EB-2..EB-8 Earth ensemble and does not decide a privileged unit `L*`.

## Read in this order

| File | What it holds |
|---|---|
| `PROTOCOL_V1.json` | The frozen protocol: axes, bounds, instruments, falsifiers, no-alarm controls. Frozen before any result. |
| `binding.py` | Recomputes every frozen contract sha256. Drift is `CANNOT_CHECK_CONTRACT_DRIFT`, never a pass. |
| `worlds.py` | World enumeration (`FULL` / `MULTISET`), trajectory observable, stride sampling, bound arithmetic. |
| `ablation.py` | Kernel-ablation instruments, including the replacement for the frozen no-op checker. |
| `vacuity.py` | Detects a pass that holds because the decision never happened. |
| `invariance.py` | Tests whether the `MULTISET` quotient is licensed. |
| `hostiles_x.py` / `hostile_probes.py` | All 15 registered hostiles across all 8 registered worlds. |
| `smoke.py` | Runs every instrument small. Exit 0 only if each is wired and each no-alarm control is silent. |

## Two defects this lane exists to fix

1. **`kernels.assert_independent_ablation` returns `ok=True` unconditionally**
   (its own docstring: "contract check on spec, not dynamics proof").
   `run_ebf0.gate()` counts only rows with `status == "FAIL"`, so §17
   condition 2 is reported closed by an instrument that cannot fail.
   Replacement: `ablation.baseline_effect_matrix` + `lattice_completeness`.
2. **`hostiles.py` gates on 6 hand-written ids**, so 9 of the 15 entries in
   `HOSTILE_REGISTRY_V1.json` never gate anything. Replacement:
   `hostiles_x.run_matrix` runs all 15 across all 8 worlds and reports, per
   cell, the flip, the silent clean control, or a named structural immunity.

## Enumeration honesty

`MULTISET` is a quotient of `FULL` by population permutation. It is licensed
only while `invariance.probe` returns `PERMUTATION_INVARIANT`; a single
counterexample forces `FULL`. `FULL` is infeasible at n=7,8 (2.2e11 and 2.6e12
worlds); that is reported as `CANNOT_CHECK` naming the missing instrument (a
canonical-form enumerator), never as a resource shortage.

## Rules that bind this lane

- Every negative and every `CANNOT_CHECK` is preserved. `PARENT_SUFFICIENT` is
  a success terminal. `OPEN_ENDED` is not an available terminal (§12).
- No outcome is tuned positive. Improvements come from mechanic changes.
- LUNARC: partition `lu48`, account `lu2026-2-51`. **Never `nuc`** — a submit
  plugin refuses this project there and neither `sinfo` nor `scontrol` shows
  it. No network connection is ever made from the cluster.
