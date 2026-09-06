# OCM paper plan V1 — claims, evidence, gates (planning document; no manuscript text yet)

Operator goal (2026-09-05): merge everything, compare OCM with LLM references and benchmarks, then
a top-tier journal paper. Craft rules: the manuscript is written with the `nature-*` skills package
and passes the full `academic-paper-pipeline` before it is called submission-ready; claim
authority stays with the receipts below, never with the prose.

## 1. Candidate title and archetype

*Machine epistemics: one persistent cognitive machine with explicit, revisable evidence state
learns language, work, science and self-repair across a lifetime, and where a matched parent is
sufficient.* Archetype: methods + evaluation paper with a pre-registered matched comparison and a
negative-results section (PARENT_SUFFICIENT families are results, not omissions).

## 2. Claim → evidence map (every claim cites a receipt-bound terminal)

| # | Claim (as it may be written) | Terminal | Receipt |
|---|---|---|---|
| C1 | A KnowledgeSpace with warrant intervals, ⊕/⊗, exact revocation/reopening and authority meet is executable and replay-exact | M1/M2 GREEN; M2.1 PARENT_SUFFICIENT at the discordant scale (equivalence δ = 1/10, S28) | `docs/provenance/M1_RECEIPT_V1.json`, `M2_RECEIPT_V1.json` |
| C2 | Bounded-world language understanding, dialogue and continual acquisition with exact obligations | M3/M4/M5 GREEN (134/134 microworld protected; acquisition regimes E0–E4) | `M3…M5_RECEIPT_V1.json` |
| C3 | A conversational alpha that refuses, clarifies, learns and revokes without a hidden LLM | LANGUAGE_KSO_ALPHA (42/42 scenarios, 0 incidents) | `M6_RECEIPT_V1.json` |
| C4 | Protected matched comparison: a residual on conversations; PARENT_SUFFICIENT / CANNOT_CHECK elsewhere | M7 MIXED: RQ1 conversations 53/54 vs 33/54 (n = 54, δ = 0.05) | `M7_RECEIPT_V1.json`, `research/ocm-m7/M7_COMPARISON_V2.json` |
| C5 | Learned organisation is parent-sufficient at the evaluated scale (4 regions × 8 atoms; 167-atom language stream); the 10^5-atom scaling row is the M2 runtime baseline | M8 PARENT_SUFFICIENT_AT_THIS_SCALE | `M8_RECEIPT_V1.json` |
| C6 | Role-typed partial transfer across work domains: later-domain cost 7 vs 12; deceptive analogies refused | M9 (matrix 14/14; SUPPORTED CANNOT_CHECK at n = 9) | `M9_RECEIPT_V1.json` |
| C7 | Scientific reasoning with identification gates, discriminating experiments, pre-registered analysis, kernel/correspondence warrants, retraction | M10 MIXED | `M10_RECEIPT_V1.json` |
| C8 | Governed self-reorganisation: diagnosis distribution, obstruction certificates, external adoption, exact rollback; 7/7 vs 2/7, 1/7 | M11 MIXED (exact invariants SUPPORTED) | `M11_RECEIPT_V1.json` |
| C9 | One persistent instance across a heterogeneous lifetime; residual over the matched whole-system parent | M12 V2 FULL_OCM_RESIDUAL_SUPPORTED in scope (1 inferential family) | `M12_RECEIPT_V1.json`, `M12_REPLICATION_RECEIPT_V1.json` |
| C10 | Lifetime-level residual: 8 paired lifetimes, 10 families 8/8 at p = 0.0078, 6 ties, replicated | M12 V3 OCM_LIFETIME_RESIDUAL_SUPPORTED | `M12_PAIRED_RECEIPT_V1.json`, `M12_PAIRED_REPLICATION_RECEIPT_V1.json` |
| C11 | An open-weight LLM reference answers out-of-scope questions from pretraining (0/20 honest unknown) while matching on lessons | REFERENCE (F8), descriptive | `M12_REFERENCE_RECEIPT_V1.json`, `research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json` |
| C12 | The build was run as an OCM problem: 36 self-application rows, 6 theory batches, 11 theory-reported defects fixed | ledger S1–S36; intake records | `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md`, `src/ocm/selfmodel/intake.py` |
| T1 | Theory: 48 theorems/obligations with exact checkers (batches 1–6; batch 7 closes the open list) | ORION-V2 PRs #333, #341, #343, #344, #347 (+ batch 7) | `ORION-V2/research/machine-epistemics-theory/` |

Not claimable (must appear as limitations): residual over a frontier foundation-model whole-system
parent (CANNOT_CHECK_MATCHED_PARENT); human usefulness (no blinded raters); external benchmarks
(BLiMP/UD/BabyLM/WorkArena/SWE-bench: CANNOT_CHECK); natural-language generality (streams are
substitutions of one bounded world); novelty (NOT_ESTABLISHED everywhere; assimilation-first).

## 3. Figures and tables (each generated from a receipt-bound JSON by a script in `tools/paper/`)

1. Programme map: milestones → terminals (from `docs/OCM_PROGRAMME_TERMINALS_V1.md`).
2. KnowledgeSpace semantics: warrant intervals, reopening cone, authority meet (schematic).
3. M7 protected comparison: paired outcomes, TOST verdicts, ablations.
4. M9 transfer matrix and acquisition-cost curves per ordering.
5. M11 S0–S7 benchmark: diagnosis/minimum-class/rollback vs parents.
6. M12 V3: eight-lifetime paired vectors per family with sign-test verdicts; V2 tier matrix.
7. Reference arm vs OCM vs parent on the phase-A families (REFERENCE labelled).
8. Self-application ledger timeline (defects caught by the machine's own discipline).

## 4. Gates before "submission-ready"

1. Batch 7 merged and its OCM obligations applied (open list closed or exactly bounded).
2. All receipts verify on main; replication receipts MATCH; CI green.
3. Manuscript drafted with the `nature-*` skills; every numeric statement traced to a receipt by a
   claim-verification script; reference list verified.
4. Full `academic-paper-pipeline`: archetype + venue contract, atomic claim verification, stats
   audit (exact tests, n, δ, α as pre-registered), reviewer simulation + editor synthesis +
   revision loop, release-integrity binding (paper SHA256SUMS bound to the receipt chain).
5. Human gates closed with the strongest proxy and labelled as such.

## 5. Venue candidates (to be decided in the venue contract step)

Nature Machine Intelligence (methods + evaluation), PNAS, JMLR (long-form with theory
appendix), or a Machine Learning / AIJ submission for the theory batches as a companion.
