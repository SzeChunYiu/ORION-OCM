# KSO architecture V1 — components, contracts, and what may call what

Status: **M0 architecture record; every contract below names the theorem that governs it, the
checker that guards it, and the parent it absorbs. NO NOVELTY OR BREAKTHROUGH CLAIM.**
Umbrella #194 · master #197 · prototype #284 · maths `KSO_SUBSTRATE_CONTRACT_V1.md` (Part I §1–§23,
Part II §24–§36) · parents `KSO_PARENT_SUBTRACTION_V1.md` · checkers `../reference/kso_math_v1.py`,
`../reference/kso_m0_freeze_checks_v1.py`, `../reference/kso_m1_mex1_population_v1.py`.

The operator's unbundling (#284 §1): the LLM did three jobs — store, solver, language interface.
The KSO takes the first two; the codec stays at the edge. This document is the component view of
that sentence, with the arrows drawn.

## 1. Components

| # | component | inputs → outputs | invariants preserved | governing theorems | guarding checker | parent absorbed |
|---|---|---|---|---|---|---|
| C1 | **Store** — the governed warranted hypergraph `𝒢=(𝒦, cert, |E|, meter, R)` | admission / composition / revocation transactions → `(P_{Q,R}, s_{Q,R})`, live set, impact cone | KS-S1…S7 (the genome); KS-T00 well-formedness; KS-T08 connectivity-or-quarantine; labels canonical antichains | KS-T01 (semiring), T03 (substochastic), T04/T04b (exact-share retraction), T09 (impact cone) | `kso_math_v1` (semiring 20/400/8,000; matrices; cone) · `kso_m0_freeze_checks_v1` G1 (S1–S7 planted 7/7) · M1 P1/P2/P5 on 100 populated spaces | ATMS labels (de Kleer 1986) + typed hypergraph + provenance semiring |
| C2 | **Solver** — the mechanics acting on the store: atomize → navigate → fire → extract → compose → warrant-check | `(𝒢, question parts, budget)` → `NavigationResult` (FOUND / GAP_NOT_FOUND / OBSTRUCTION_WITNESSED / CANNOT_CHECK), reacting subgraph `G_Q`, composite atom, live verdict | reads labels, never writes them; budget stated per arm; determinism under the committed seed | KS-T05 (fixed point), T02 (label-gated firing), T06/T06b (surprise), T11a (extraction unique), T19 (outcome exhaustive/exclusive), T20 (compose = ⊗), T10a (seed-function) | F5, F6, F3, G2-compose/extract/translator/nonidentifiability, F8 · M1 P3/P4 | PPR/RWR (Andersen–Chung–Lang; Tong et al.), spreading activation, Petri firing, PCST, KAT |
| C3 | **Codec** at the boundary (E30-R14 boundary-contract template, `research/experiments/e30-r14/BOUNDARY_CONTRACT_TEMPLATE_V1.md` §6 substitution) | text → question parts (`η_c`); rendered whole subgraph with elision receipt → text (`ρ_c`); proposals as content-hash references | closed under what was shown (ledger class 17); references located by content hash exactly once; **never writes a label or a graph coordinate**; unlocatable reference voids the whole proposal | KS-T10a (invariance reduces to seed equality); KS-T10 `OPEN_M5` | F10 (`ASKED_FOR_WHAT_WAS_NOT_SHOWN`, `AMBIGUOUS_REFERENCE`), G2-translator | `anchored_edit_interface.py` / `APPLY_CLEAN_BY_CONSTRUCTION` — the one typed interface that worked |
| C4 | **Acquisition channels** — INSTRUCTION, DEMONSTRATION, INTERACTION, EXPERIMENTATION, FEEDBACK, EXACT_CHECKER | `(atom, edges, certificate)` → admitted / quarantined / typed rejection | edges > 0 or quarantine; reachable by navigation; certificate decides the label: FEEDBACK ⇒ `Λ=0`; EXACT_CHECKER ⇒ exact warrant | KS-T08, KS-T18 (feedback cannot warrant; proof assistant ≠ feedback) | F4 (8 cases) · M1: every populated atom certified, S1 holds 100/100 | PCC admission (Necula); #197 stem-cell row 2; stage-1 "feedback provably cannot warrant" |
| C5 | **Immune system** — checkers, kill-gate, ledgers | every operator's checker; `FAILURE_LEDGER.md` (28 classes) + `OCM_FAILURE_LEDGER.md` (7) | three exit codes, never collapsed (0 / 1 / 2 = `CANNOT_CHECK`); a planted failure per clause; no-alarm control per clause; must-differ parent per dynamic clause | none — it is the thing that checks theorems | self: every `main()` has the 0/1/2 test; `test_kso_m0_freeze_v1::test_cli_exit_codes_are_three_and_distinct` | V2 `FAILURE_LEDGER.md`, `pr_merge_gate.py` |
| C6 | **Growth operators** — compose (revocable), self-revise under RCL (policy swap KS-S5; representation quotient KS-T07 ∧ S4), consolidate (§11, open) | `𝒢_t → 𝒢_{t+1}` | genome unchanged (digest); authority preserved under registered revocation; fixed point when nothing new | KS-T17 (stem-cell invariant), KS-T20, KS-T07, S4/S5; KS-T12 open | G3 (3 steps, fixed point, cancers 3/3) · M1 P5 S4/S5 | ATMS composition; Blackwell/CEGAR (lane 201); DreamCoder/LILO for consolidation (open) |
| C7 | **Jump proposer** (M4 hooks only) | `ObstructionWitness Ω` → `orion_v2.jump.JumpTrigger` → `JumpProposal` (level, lineage, correspondence, preservation, predicted consequences, falsifiers) | minimum sufficient level; proposes, never adopts; witness must be `is_admissible` | KS-T19; §15 governed rewrite (parent) | F6 witness→trigger binding; loop itself `OPEN_M4` | V2 `jump.py` J0–J8; ME-X2 minimum escalation; DPO rewriting |
| C8 | **Authority / constitution** `𝔠=(Check, Authority, Meter, Commit)` — external | proposals → accepted / refused | never self-modified by the machine; a J8 proposal cannot self-authorize | §1 boundary; KS-S7 metering | S7 planted unmetered mutation caught | Gödel-machine boundary; RSHEA sign-off = continuation, never promotion |

## 2. Dependency graph — what may call what, and what may never

```
                 text in                                   text out
                    │                                          ▲
                    ▼                                          │
              ┌──────────┐   question parts   ┌──────────┐  rendered whole subgraph
              │  C3 codec│ ─────────────────▶ │ C2 solver│ ──────────────────────▶ C3 codec
              └──────────┘                    └──────────┘
                    │ proposals (content-hash refs)  │ reads P, s, labels, live set
                    ▼                                ▼
              ┌──────────┐   admit(atom,edges,cert)  ┌──────────┐
              │C4 channels│ ────────────────────────▶ │ C1 store │ ◀── C6 growth (compose / self-revise / revoke)
              └──────────┘                            └──────────┘
                                                          │ Ω (obstruction witness)
                                                          ▼
                                                    ┌──────────┐  proposal  ┌──────────┐
                                                    │ C7 jump  │ ─────────▶ │ C8 auth. │ ── accept / refuse ──▶ C1 (via C4/C6 only)
                                                    └──────────┘            └──────────┘
   C5 immune system: reads every arrow; writes nothing but verdicts (0 / 1 / 2) and ledger rows.
```

**May call.** C3 → C2 (question parts; rendered subgraph back); C2 → C1 (read); C4 → C1 (write, through `admit` only); C6 → C1 (write, through `compose` / policy swap / `revoke` only, each metered); C2 → C7 (emit `Ω`); C7 → C8 (propose); C8 → C1 (accepted proposals re-enter through C4/C6, never directly); C5 → everything (read).

**May never.**
- C3 (codec) may never write a label, a warrant, or a graph coordinate; it may only reference atoms it was shown, by content hash (F10; ledger class 17).
- C4 FEEDBACK may never confer warrant: `Λ=0` by construction (KS-T18); no channel may set a label the certificate does not license (KS-S1).
- Nothing may modify KS-S1…S7: the genome digest is checked before and after every growth loop and every population (G1, G3, M1 P5); a changed digest is a cancer, not a revision.
- C2 (solver) may never write to C1; extraction and composition produce *candidates* that enter through C4/C6.
- C7 may never adopt: a Jump is a proposal object; adoption authority is C8 and stays external (#284 §4b; RSHEA: sign-off = continuation).
- C6 self-revision may never change an admitted atom's liveness signature (KS-S5) nor coarsen `E` against a non-measurable `Γ` (KS-S4); a representation move needs lumpability **and** warrant measurability (§9.2).
- No component may renormalise survivors after a revocation (KS-T04/T04b): dead mass dissipates; the renormalising parent is the planted control everywhere it could matter.
- No comparison may cross unmatched navigation budgets (F8) and no typed-navigation advantage may be claimed on a role the comparator has covered (F9).

## 3. The problem's path through the machine (one line per arrow, each with its checker)

1. `u_t` → C3 `η_c` → parts → **F5** (exactly `k` seeds; non-atomic / unbound rejected; committed seed).
2. parts → C2 `navigate` under budget `B` → `NavigationResult` → **F6 / G2-nonidentifiability** (four outcomes; timeout is a gap; obstruction only when the ceiling walker also fails; witness admissible for C7).
3. `a^*_{Q,R}` → `ρ_Q` → **F3 / M1 P4** (hub two directions; background zero).
4. `ρ_Q` → `G_Q` (reacting subgraph) → **G2-extract** (unique; optimiser ties reported).
5. `G_Q` → C2 `fire` (label-gated enabling) → **`kso_math_v1` KS-T02** (revoked tail disables).
6. enabled operators → `compose` → candidate atom with `Λ=⊗` → **G2-compose / M1 S2**.
7. candidate → warrant check `ℓ_R` → live / not → **KS-T03/T04b; M1 P2** (label ≡ oracle on 1,344 cells).
8. `G_Q` (whole, with elision receipt) → C3 `ρ_c` → `y_t`; proposals back by content hash → **F10**.
9. a revocation `R` at any time → C1 gates; impact cone reopens → **F2 / M1 P3** (400/400 both directions; events replayed 50/50).
10. gap → C4 (atom + edges + certificate) → **F4**; obstruction → C7 → C8 → **`OPEN_M4`**.
11. growth loop → **G3** (genome held; fixed point; cancers caught).

## 4. What this architecture does not claim

It is the component view of a set of parent mechanisms coupled by one design choice (the frozen
denominator under a JTMS/ATMS gate). It does not establish that the coupled machine solves anything
better than the strongest faithful parent product (`KSO_PARENT_SUBTRACTION_V1.md`); M2 measures
that against `mex1_parents.py` + an RWR parent, information- and budget-matched, with
`PARENT_SUFFICIENT` the expected honest result. Language competence (C3 as a real codec) is M5;
Jump adoption is M4; consolidation is open (KS-T12).
