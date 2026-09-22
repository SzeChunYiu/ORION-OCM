# Section-H real-scale measurement — row `Diffusion/iterative-refinement systems.` (`SIGMA_H33R`)

New package `research/gmi-833-h-real-scale-diffusion-refinement-v1/`. Issue #833,
section H. This PR replaces exactly the one row it measures; the coordinator
owns the body write.

## What the measurement delivers

A recovery, on a sha256-bound external source (`/usr/share/dict/american-english`
on billy-old, `9e66281f7e51`, 104,334 tokens, 168,834 distinct contexts,
`T_ctx` = 671,860 context positions), on the registered stochastic-refinement
ecology `F33`, with the registered 7:1 slice (`n_fit` 587,877 / `n_held` 83,983,
query set 38,103), exact integer arithmetic throughout, and two materially
independent routes.

| quantity | value |
|---|---|
| held winner, family-blind winner rule | `REFINE<=25` — class `REFINEMENT_INDEX` (a refinement step index) |
| held errors | **1,479** (majority rule 5,197; F1 need 2,598 — holds; prototype agreement 36,624 / 38,103) |
| rank stage (6,057 vs 11,218) and regeneration (15,409 / 18,069 vs 18,574 / 18,638) | same class at all four stages |
| sibling single-draw family (H31's channel), best arm | `DRAW0`, **30,557** — beaten **20.7x** |
| raw cardinality family, best arm | `CNT>=1`, 5,197 — beaten **3.5x** |
| `MEM_FALLBACK` (storable label) | admitted; reaches the minimum at every stage and **loses the registered tie-break on charged cost at every stage**: 2 units against the refinement arm's 1 |
| registered **global** design null (seed 20261001) | 1,479 → **6,678** (**4.52x** > 3x bar); cardinality arm **bit-identical** 5,197 → 5,197; single-draw arm 30,557 → 27,553 |
| label-shuffle null (seed 20261002) | **10,043** > 5,197 |
| store ladder | monotone 32,173 → 1,479 |
| crossover `m*` | 57,567 (`2m > V + 27`, `V` = 115,105, index cost 115,132) |
| source-order matched presentation control | fires (registered arm 4,657 vs F1 need 2,598) |
| R8 frozen predictions | 38,103 rows, sha256 `26661dc087eebf635e961ab3acdd1dce8f34854a9d43d4c619fca25d44254d33`, written and flushed before any null or control |

**The registered design.** The labeller is a registered sequence of stochastic
perturbations: the source's 69 characters under the Knuth order
`(ord(c) * 2654435761) mod 2**32` with successor `sigma`, the canonical
candidate advanced by a target-free probe offset, and the protected interface is
the **refinement index** — the number of `sigma` steps required before the
presented candidate re-enters the context's full-source support, capped at 256 —
thresholded at the registered `T*`. The labelling configuration and `T*` are
fixed **before any fit** by a registered balance criterion over four
source-derived configurations, measured on the full source with no slice, no
store and no readout evaluated; the criterion's outcome (`T* = 25`, rate
84,340 / 168,834) is recorded in the receipt rather than named in the freeze.
The R8 record is written before any null.

**The registry contract is a steer.** `STOCHASTIC_SOURCE_CHANNEL` and its
hallmark are carried verbatim, cited to the merged sibling's steer reading. The
interface this package registers is justified in `FREEZE_V1.md` section 12 by a
measured design fact: the contract's `x5` expression is a source *address*, so a
family-blind argmin over raw source-probe arms is mechanically nearest-exemplar
retrieval, the mechanism the nearest-neighbor row already owns at its own scope.
The sibling class is not avoided — it sits **inside** the language and loses by
measurement, which is the normal shape of a real recovery.

## Custody (freeze-first)

Commit 1 of this branch is `FREEZE_V1.md` **alone**; commit 2 is
`FREEZE_V1_SLICE_ADDENDUM_H33_V1.md` **alone**; both precede any executor, test,
data extraction, fit or result artifact. CI asserts the commit order, that the
freeze survives the squash publication, that the manifest's freeze pins are the
committed bytes, and — the strongest form of freeze-first this programme has —
that neither freeze document contains a delivered result or a post-outcome
value.

## Verification

- `independent_oracle_dr_v1.py` (route B) imports none of the primary executor and **agrees** on all 25 checks.
- `real_scale_diffusion_refinement_v1.py` (route A): 11/11 coordinates measured at `SIGMA_H33R`, no gate carries a foreign scope, no parent result file is read, every committed block replays exactly, and the design null is re-scored directly on the committed reassigned tallies.
- 37 tests pass under both `-I -B` and `-I -O -B`.
- `ci_gates_v1.py`: foreign-sigma, closure-consistency, annotation-budget (replacement payload 895 chars against the measured 2,143 limit), two-route-namespace, terminology, selftest — every gate fires on a planted positive and is silent on clean input.
- Hostiles all applicable, detected, and silent on the clean receipt (source digest, artifact path, grammar extension, tampered replay row, null seed drift, moved raw arm).
- Determinism: two full runs byte-identical (`scope_SIGMA_H33R.json` md5 `bc471d6b8981cdfc55a8d1140f9d9499`, `FROZEN_PREDICTIONS_R8.json` md5 `920eebc620e0415fca9e2d6b7eaae811`).

Everything above was produced on the host of record (billy-old, CPython 3.14.4)
and re-verified from the committed receipts offline.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
