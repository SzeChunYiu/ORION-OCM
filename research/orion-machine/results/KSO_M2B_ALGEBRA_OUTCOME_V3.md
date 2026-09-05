# KSO M2b V3 — outcome record

Terminal: `M2B_V3_SOLVED_FROM_THE_SOURCE_AND_WARRANTED`
Receipt: `KSO_M2B_ALGEBRA_RECEIPT_V3.json` (30/30 exact; 90 ROOT_CLAIMs VALID / 0 INVALID / 0 CANNOT_CHECK under the SymPy EXACT_CHECKER)
Design freeze: `KSO_M2B_DESIGN_V3.json` (committed before the run; the module refuses to run on drift, exit 2)
Supersedes: V2 (`KSO_M2B_DESIGN_V2.json`, `KSO_M2B_ALGEBRA_RECEIPT_V1.json`, outcome `KSO_M2B_ALGEBRA_OUTCOME_V1.md`)

NO NOVELTY OR BREAKTHROUGH CLAIM.  This record establishes that on one registered domain the roots the
machine produces come from the registered source, that applicability is decided by labels, and that the
gates are exit codes.  It does not establish that the machine solves quadratics better than anything; the
comparator for M2 remains the strongest faithful parent and the expected honest outcome there is
`PARENT_SUFFICIENT`.

## Why V3 exists

The V2 receipt reported 30/30 exact and the terminal `M2B_POPULATED_AND_SOLVED_ON_DEV`.  lane-guards'
independent adversarial replay of that receipt (ORION-V2 #295, review 5116123643) found that the figure
was not evidence for the claim it was cited for.  Five defects:

| # | defect in V2 | what V3 does | plant | no-alarm |
|---|---|---|---|---|
| a | procedures were Python (`apply_procedure`); the source only named them, so a corrupted step in the registered source could not change a root | each procedure is a hyperpath of STEP atoms (registered operation + SymPy-parsable template); ONE generic interpreter walks it; no per-procedure Python | corrupt `step:qf:1` (`4*a*c`→`3*a*c`) ⇒ root changes `(-7/8)±(1/4)√(275/12)` → `1/4, -2`; oracle disagrees at COMPOSE; checker INVALID; only `proc:quadratic_formula` affected, `proc:complete_square` (its own `step:cs:1`) still warranted | clean run: 30/30, 0 INVALID |
| b | the Δ<0 block on factoring was a code conditional; the Δ case atoms constrained `proc:quadratic_formula` only and were disjoined, so the OR was always live and they gated nothing | a case atom's `constraint_on` is the set of procedures it LICENSES; `con:delta_neg` does not license `proc:factor`; every conditional that decided applicability is deleted (`atomize_labels` mentions no procedure id) | flip `con:rational_roots` on a real irrational instance ⇒ factoring fires, root INVALID over Q; flip the case licence on a complex instance ⇒ complex root over Q INVALID | factoring fires on 0/5 irrational and 0/5 complex instances |
| c | `main()` exited 0 at 26/30, 25/30, 20/30 | threshold registered in the freeze (`n=30, min_exact=30`); `main()` returns 1 below it | `--plant-corrupt-step` over the split ⇒ 10/30, **exit 1** | clean run **exit 0** |
| d | a second-oracle disagreement was folded into the family rejection counter and re-drawn | `OracleDisagreement` raised naming the instance ⇒ CANNOT_CHECK, **exit 2**; proposal-shape re-draws stay counted separately | perturbed second oracle ⇒ raised at `dev-COMPLEX_PAIR-000` | clean split raises nothing |
| e | no admissibility predicate; out-of-range instances accepted | `REGISTERED_RANGE_V3` over drawn AND derived coefficients (`abs ≤ 1728`, `denominator ≤ 64`); typed `OutOfRegisteredRange` at oracle and solver | `c = -100000` rejected at both ends | all 30 generated instances admissible |

The instance set is byte-identical to V2 (`ids_sha256 75de2299…`), so V2 and V3 are directly comparable.

## What is the same as V2

Population through `admit()` with certificate INSTRUCTION for every atom; the M0 invariants (S1, S2, S7,
genome digest unchanged) hold; retraction propagation both directions now over constraint, definition AND
step atoms (25 revocations; the renormalising parent differs on ≥1).  `alpha = 1/3` is still a
PRE_STUDY_PLACEHOLDER; it is not yet traceable to a parameter-study row.

## A correction made on the record

The first pass at verifying the exit codes read `$?` through a pipe (`python … | tail`), so the shell
reported `tail`'s exit and printed 0 for all three cases.  Re-run without the pipe the codes are 0 / 1 / 2
as designed.  The first reading was worthless and is flagged rather than left standing.

## Reproduction

```
python research/orion-machine/reference/kso_algebra_quadratic_v3.py --self-test        # exit 0
python research/orion-machine/reference/kso_exact_checker_sympy_v1.py --self-test       # exit 0
python research/orion-machine/reference/kso_m2b_algebra_v3.py --per-family 5 --out research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V3.json   # exit 0
python research/orion-machine/reference/kso_m2b_algebra_v3.py --plant-corrupt-step     # exit 1
python -m pytest -q tests/unit/test_kso_m2b_algebra_v3.py                               # needs SymPy 1.14
```
Receipt body (minus `provenance`) reproduced byte-identically in the ORION-OCM checkout: sha256 `b7285ced95a1360e…`.
