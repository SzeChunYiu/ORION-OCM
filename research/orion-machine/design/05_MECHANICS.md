# 05 — Mechanics: what happens, step by step, when a question enters

Three traces plus the growth loop are reproduced by one command on #295 —
`reference/kso_trace_v1.py` → `results/KSO_TRACES_V1.json` (`all_reached`, exit 0), on **real ME-X1
dev instances**; the two operator probes remain `[SPEC → M5]`. The state after every step is named,
and each step names the algorithm (04) and the invariant it preserves (02/03). The tables are what
the receipt shows; the receipt is the evidence, the table is not.

## Trace 1 — FOUND `[MACHINE: kso_trace_v1 T1_FOUND — instance dev-X1-A_CLAIM_PROBLEM_IDENTITY-000, 57 steps, 21 hyperedge visits, reached]`

| step | algorithm | state after | invariant |
|---|---|---|---|
| 0 load | — | `𝒦` from the M1 receipt (digest checked), `R` = registered revocations for this instance version | `Σ` digest matches freeze |
| 1 atomize | A2 | `s_Q` over the instance's claim atoms, `req` = the queried claim cell, `η_Q` = claim-kind prior | `s_Q` committed before any navigation (KS-T10a) |
| 2 navigate | A3 | `ρ*` (exact rational if `n ≤ N_exact`), `converged = true`, `B_spent.steps` | `‖ρ*‖₁ ≤ 1`; gated atoms exactly 0 |
| 3 fire | A4 | `E_R` | dead tails disable (KS-T02) |
| 4 extract | A5 | `X_Q` = seed component ∩ supp `ρ*`; ranked by `r_Q` | unique (KS-T11); hub not on top by raw `ρ` alone (KS-T06b). **M2 finding:** the request atom was in `X_Q` on 38/50 instances; on 12/50 one-hop request atoms fell below the uniform background (fan-out dilution on small graphs) and the answer came from the store read in step 5 — those 12 are `FOUND_BY_STORE_READ`, not navigation successes (M2.1 revival: attribute to EXTRACT, lever = background baseline at matched seed size) |
| 5 compose | A6 | `π` from seeds to `req`; `L(π) = ⊗` | KS-T20 |
| 6 outcome | A12 | `Ω = FOUND`, `warrant = L(π)`, `live(L(π), R) = true` | S7: `Ω` computed, not written |
| 7 score | — | answer object = the claim value the oracle scores; `agree = true` | receipt row: instance id, `Ω`, agree, `B_spent`, stage of any disagreement |

## Trace 2 — GAP_NOT_FOUND with the channel hook `[MACHINE: kso_trace_v1 T2_GAP_NOT_FOUND — instance dev-X1-B_MEASUREMENT_CALIBRATION-003, 88 steps, 13 visits, GAP_NOT_FOUND:WARRANT with acquisition hook; step 7 (acquire) → M3]`

| step | state after | note |
|---|---|---|
| 1–3 | as above, but `req`'s supporting atom `a†` was removed at population (registered ablation) | `E_R` lacks every edge with `a†` in tails |
| 4 extract | `X_Q` does not contain `req` | |
| 6 outcome | ceiling walker (ungated, all types) **does** reach `req` through `a†`'s registered edge type ⇒ `Ω = GAP_NOT_FOUND`, hook = `(missing: a†, type: τ(h†))` | KS-T19: gap, not obstruction |
| 7 (M3) acquire | INSTRUCTION transaction supplies `a†` with `{{src}}` label ⇒ re-run ⇒ `Ω = FOUND` | KS-T13: labels of pre-existing atoms unchanged; a FEEDBACK transaction with the same content must **not** close the gap (KS-T15) |

## Trace 3 — OBSTRUCTION_WITNESSED with the Jump trigger `[MACHINE: kso_trace_v1 T3_OBSTRUCTION_WITNESSED — the §29 island witness, admissible JumpTrigger, lower-level dispositions recorded, controls present; step 7 (Jump) → M4]`

| step | state after | note |
|---|---|---|
| 1–4 | `X_Q` reaches a set of atoms indistinguishable from `req` under `s_Q` (same type, same label, same reaction) | non-identifiability |
| 6 outcome | bounded walker fails **and** ceiling walker fails (or target non-identifiable) ⇒ `Ω = OBSTRUCTION_WITNESSED`, witness = `(level = current, reason = NON_IDENTIFIABLE | CEILING_FAIL, atoms)` | KS-T19; binds to `JumpTrigger.is_admissible` |
| 7 (M4) Jump | minimum sufficient level `J_j` proposed as an atom with an EXPERIMENTATION/EXACT_CHECKER certificate; admitted only if S4/S5 hold; re-run τ1 | KS-T14; benchmark v1 #558 |
| control | a planted instance where the ceiling walker *does* reach `req` must produce GAP, not OBSTRUCTION | the alarm must be able to be wrong |

## Trace 4 — the growth loop `[MACHINE: kso_trace_v1 G_GROWTH_LOOP — fixed point reached, genome digest unchanged, cancers caught; stem-cell invariant in kso_m0_freeze_checks_v1]`

acquire (INSTRUCTION) → compose → self-revise (admissible `φ`) → registered revocation → assert `Σ`
digest unchanged and every pre-existing live label still live → repeat to fixed point (`≤ k`). The
three cancers (Σ edit, label merge, feedback-only growth) are caught by the same checker.

## Operator probe P1 — "solve quadratic equations" `[SPEC → M2b + M5]`

| step | state after |
|---|---|
| codec₁ / codec₂ | `s_Q` over {`quadratic_equation`, `solve`}; `req` = a **procedure** atom of kind SOLVE with target type `roots`; `η_Q` = procedure prior. Both codecs must produce equal `s_Q` (KS-T10) |
| navigate + fire | `E_R` enables `discriminant → cases`, `quadratic_formula`, `complete_square`, `factor` (all INSTRUCTION-labelled from the registered algebra source) |
| extract + compose | `π` = the quadratic-formula procedure (highest `r_Q` under the procedure prior), `L(π) = {{algebra_src}}` |
| exact check | for the general question the machine instantiates a worked instance (`x² − 5x + 6 = 0`), runs `π`, and calls the EXACT_CHECKER channel: SymPy substitutes the roots back ⇒ certificate `c` ⇒ `warrant = {{algebra_src, c}}` |
| render | procedure steps + worked instance + roots; `Ω = FOUND`; budget line |
| specific input "solve x²−5x+6=0" | same path, `req` = roots of this instance; answer `{2, 3}`, verified |
| unsolvable / malformed | atomize rejects an unbound part ⇒ `GAP_NOT_FOUND` with the hook, or over ℝ with `Δ < 0` the procedure returns the registered "no real roots" atom — never a fluent guess |

## Operator probe P2 — "hello how are you" `[SPEC → M5 (dialogue policy source)]`

| step | state after |
|---|---|
| codec | `s_Q` over dialogue-act atoms {`GREETING`, `WELLBEING_QUERY`}; `req` = a RESPONSE procedure |
| navigate + extract | `π` = the registered dialogue procedure for (GREETING, WELLBEING_QUERY): greet back, **report actual state** (loaded space id, atoms, budget remaining, last `Ω`), offer capabilities |
| warrant | `L(π) = {{dialogue_policy_src}}` (INSTRUCTION); no claim about feelings exists in `𝒦`, so none can be rendered (S7 / no fabrication) |
| render | "Hello. I am a knowledge-space object with N atoms loaded; last query outcome FOUND; I can solve registered algebra problems and tell you what I do not know." |
| comparator | an LLM alone will be more fluent; `PARENT_SUFFICIENT` on P2 is the expected honest result and is reported as such |

## Immune system in the loop (06)

Every trace runs under: the freeze digest check at load, `Σ` predicates before and after any write,
the four-valued outcome rule (never a codec-written `Ω`), the budget clause (overrun ⇒ `CANNOT_CHECK`),
and the receipt writer (no receipt ⇒ the run did not happen). Failure classes from
`FAILURE_LEDGER.md` / `OCM_FAILURE_LEDGER.md` that have a checker on the machine are listed in 07;
those without one are open build items, not assumptions.
