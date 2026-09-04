# OCM self-application ledger — the build treated as a problem the finished machine would solve

Operator directive (2026-09-04): *treat the development of OCM like a problem the finished OCM will
tackle; play the OCM yourself; the obstructions met while building are the leads for improving it.*

Every row is written in the machine's own vocabulary: what was navigated, where the gated walk
stopped, the four-valued outcome, which lower-level dispositions were tried, what was composed,
which checker now guards it, and the parent that already owned the fix. A row whose outcome is
`OBSTRUCTION_WITNESSED` at a level above J1 is a candidate architecture change and must go through
the Jump interface (`src/ocm/kso/jump.py`), never be adopted silently. Rows are append-only.

| # | stage | task atomised | outcome | witness / lower-level dispositions | composed fix | checker | parent | J-level |
|---|---|---|---|---|---|---|---|---|
| S1 | M1 warrant | make `UNKNOWN` compose under ⊗/⊕ | `OBSTRUCTION_WITNESSED` for the single completeness bit: `P=⟨∅,incomplete⟩ ⊗ Q=⟨{{2}},complete⟩` under `R={2}` reads UNKNOWN, `∧₃` says DEAD | BUDGET: irrelevant (algebraic); WARRANT: irrelevant; RESTART: irrelevant — no re-labelling of the bit repairs it; the object itself was the wrong one | warrant **interval** `⟦L,U⟧` (exhibited / possible); liveness is then an exact Kleene homomorphism (KS-T21) | `warrant.check_three_valued_reduction` (168 intervals, 225,792 checks); ORION-V2 `kso_three_valued_warrant_exact.py` counterexample | Pawlak 1982 lower/upper approximation; Kleene 1938; Belnap 1977 | J3 (representation of the label) — proposed and adopted at M1 because the incumbent was witnessed insufficient on an exact counterexample |
| S2 | M1 revocation | prove prune–solve equivalence on random spaces | `GAP_NOT_FOUND → FAIL` at `R={1}` on seeded space #2: `v1→{v4,v3}` with `v3` DEAD; gated `v1→v4 = 5/13`, pruned `3/13` | BUDGET/WARRANT/RESTART: irrelevant; the pruned object dropped a whole edge because it touched a dead head | prune keeps the edge, deletes the dead head, **retains its original γ share** (dissipation), never renormalises survivors (KS-T04c head clause); the renormalising version is now a planted mutant | `revocation.prune_equivalence` on 30 random spaces × 7 revocations; `mutant_prune_renormalize_heads` differs | KS-T04 (contract) — the reference's independent prune already did this implicitly | J1 (local repair) |
| S3 | M1 admission | replay the inherited F4 admission cases | `FOUND` with a mismatch: reference case 1 admits a COMPOSITION head whose warrant ≠ bridge ⊗ tails, which KS-S2 forbids once the space is governed | lower level available: enforce S2 at admission (typed rejection) instead of only at genome check | `COMPOSITION_WARRANT_MISMATCH` rejection; documented tightening in `tests/m1/test_equivalence_reference.py` | `checks.check_admission_channels` | KS-S2 (#203 S2) | J1 |
| S4 | M0 → M1 migration audit | resolve the immune-system row's dependency | `GAP_NOT_FOUND:TARGET_ABSENT` — six frozen artifacts audit against a root `FAILURE_LEDGER.md` that was never migrated (a *document* dependency outside the runtime-only closure policy) | hook = acquisition channel: materialise from the frozen source | `docs/provenance/ORION_V2_FAILURE_LEDGER_42b1b0d.md` byte-bound in CI; dependency-audit policy widened to document dependencies | CI job `ledger-materialization` (blob `4394f4b6…`) | — | J0 |
| S5 | M1 admission (design) | compose an atom with undeclared authority | `FOUND` with a design decision: an undeclared authority coordinate is **bottom**; composing with it yields no authority (conservative, non-amplifying) | alternative (missing = top) rejected: it would let an unlabelled component launder authority | `Authority.meet` treats missing ranks as 0 | `checks.check_summary_no_authority` (explicit case) | Denning 1976 lattice flow | J0 |

## Underperforming modules — revival backlog (never tuned to outcome; improved by mechanic)

| module | evidence of underperformance | attribution (one stage) | lever | test that must move | status |
|---|---|---|---|---|---|
| reaction surprise `ρ_Q` | M2 receipt: on 12/50 dev instances the decisive live request atom scores surprise 0 and drops out of `G_Q` although live and one hop from a seed (uniform background `π≈0.0061` > activation `≈0.0057` on a 57-atom graph) — `results/KSO_M2_SOLVE_OUTCOME_V1.md` | EXTRACT (background model), not NAVIGATE | seed-count-conditioned / fan-out-aware background (M2.1 lever named in the receipt, never built); register as an alternative `SurpriseModel`, compare against the frozen uniform model on the same 50 worlds, keep the two-direction hub theorem (KS-T06b) as the no-regression gate | mechanic column 38/50 on the dev split; must not lose the hub witness | `OPEN — M2` |
| exact PCST extraction | bounded to ≤ 12 free atoms; greedy arm has no guarantee | EXTRACT | bounded-treewidth or ILP-free branch-and-bound; report approximation ratio on the instances where exact is available | tie/optimum agreement on all exact-feasible instances | `OPEN — M2` |
| navigation scale | exact rational solver is O(n³); float power iteration exists but no sparse path | NAVIGATE | sparse row storage + power iteration with the KS-T05 rate as the stopping certificate | 10²…10⁵ synthetic sweep (M2 §13) | `OPEN — M2` |
| RWR comparator walk | comparator is undirected while the mechanic is directed (`kso_m2_comparator_v1.py`) — a comparator mechanism gap, not a KSO advantage | PARENT | directed RWR arm added alongside, budgets matched (F8) | comparator table re-run on the dev split | `OPEN — M2` |

## How to add a row

1. Name the stage in the machine's pipeline (atomise → navigate → fire → extract → compose → check → learn → revoke/reopen → jump).
2. Give the four-valued outcome and, for an obstruction, the witness and the three lower-level dispositions (budget, warrant, restart).
3. Compose the fix as a registered object with a checker and a planted mutant.
4. Name the parent. If none exists, the row is a candidate residual — it goes to the parent-subtraction table before any claim.
5. Assign the minimum sufficient J-level; J3+ rows require a `JumpProposal` with preservation obligations and falsifiers.
