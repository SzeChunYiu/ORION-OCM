# 08 — Parents: who owns each piece, and where a delta is stated

Extends `theory/KSO_PARENT_SUBTRACTION_V1.md` (14 `PARENT_OWNED`, 1 `PARENT_SUFFICIENT`) to every
structure, dynamic and algorithm in this set. Verdicts: `PARENT_OWNED` (we re-implement faithfully,
nothing added), `PARENT_SUFFICIENT` (the parent already meets the requirement; our component adds
nothing measurable), `DELTA_STATED` (a named difference forced by a genome constraint, with the
checker that exhibits it). `NO NOVELTY OR BREAKTHROUGH CLAIM`: a `DELTA_STATED` row is a
difference, not a claim of advantage, until a frozen, budget-matched comparison says otherwise.

| piece (file §) | strongest parent(s) | verdict | delta and its checker |
|---|---|---|---|
| warranted typed hypergraph (01 §S1) | de Kleer 1986 ATMS; AND/OR graphs; Gallo et al. 1993 hyperpaths | `PARENT_OWNED` | — |
| warrant semiring (01 §S2, KS-T01) | de Kleer labels; Green–Karvounarakis–Tannen 2007 provenance semirings | `PARENT_OWNED` | — |
| edge vocabulary (01 §S3) | typed KGs; ORION v1 atlas | `PARENT_OWNED` (own prior work) | — |
| restart walk, fixed point (KS-T03/T05) | Page et al. 1999; Tong–Faloutsos–Pan 2006 RWR | `PARENT_OWNED` | — |
| **frozen-denominator gating (KS-T04)** | RWR/PPR (renormalise after pruning); JTMS IN/OUT gate | `DELTA_STATED` | the KSO law is `(JTMS gate) ∘ (spreading activation with frozen denominators)`; no single parent produces it — executable subtraction on one witness: 8 parents run, 0 own it (#295). Delta = exact-share retraction; checker = renormalising parent raises an unreachable atom (16/50 worlds) |
| reaction surprise, hub normalisation (KS-T06/T06b) | Collins & Loftus 1975 (fan effect); Anderson ACT-R activation; tf-idf/PMI style background subtraction | `PARENT_OWNED` (mechanism) | two-direction theorem is a restatement on this walk; no advantage claimed |
| label-gated conjunctive firing (KS-T02) | ATMS/JTMS | `PARENT_OWNED` | — |
| extraction as seed-component support (KS-T11) | connected-subgraph / PCST retrieval (Johnson–Minkoff–Phillips 2000) | `PARENT_OWNED` | uniqueness is inherited from the unique fixed point; ties reported |
| procedure = hyperpath with `⊗` label (KS-T20) | ATMS explanation; hyperpath search | `PARENT_OWNED` | — |
| impact cone (KS-T09) | Doyle 1979 dependency-directed backtracking; incremental TMS | `PARENT_OWNED` | — |
| quotient / lumpability (KS-T07, S4) | Kemeny–Snell lumpability; Theorem S4 (own, #203) | `PARENT_THEOREM_ADOPTED` | — |
| admission connectivity (KS-T08) | — (implementation invariant) | `PARENT_SUFFICIENT` (trivial) | — |
| acquisition channels (τ2) | instruction: rule induction / structured ingestion; demonstration: LfD (Argall et al. 2009); interaction: Angluin 1987 queries, KWIK; experimentation: optimal experimental design; feedback: RLHF | `PARENT_OWNED` per channel | — |
| **feedback cannot warrant (KS-T15)** | RLHF (reward ≠ justification); proof assistants (certificate = warrant) | `DELTA_STATED` (a constraint, not a capability) | FEEDBACK enters with `L = 0`; checker: feedback atom cannot enable any edge |
| consolidation (KS-T12, A9) | DreamCoder (Ellis et al. 2021) library learning; EC² | `PARENT_OWNED` + S4 constraint | delta = warrant-measurability requirement; checker planted non-measurable merge `[SPEC → M3]` |
| self-revision under RCL (A10) | Schmidhuber Gödel machine; ATMS | `PARENT_PRODUCT_SUFFICIENT` | constraint (c) of the directive is owned by the product |
| stem-cell growth invariant (KS-T16) | Gödel machine × ATMS; safe self-modification literature | `PARENT_PRODUCT_SUFFICIENT` | the invariant is a test, not a mechanism |
| obstruction witness (KS-T19) | H-EXT-1R (own); CEGAR-style "no abstraction refines" witnesses; ME-X2 | `PARENT_OWNED` (own prior work) | ceiling-walker rule is the finite form of H-EXT-1R |
| Jump ladder / minimum escalation (KS-T14) | v1 J0–J8 (own); ME-X2 (own); abstraction refinement | `PARENT_OWNED` (own prior work) | `[SPEC → M4]`; benchmark #558 |
| budget clause (KS-T17) | ORION v2 B5 federation discipline; cell-probe / information-matching arguments (lane #201) | `PARENT_OWNED` | — |
| typing as coverage prior (KS-T18) | ME-X6 V3 (own) | `PARENT_OWNED` | — |
| codec boundary (01 §S8) | E30-R14 (own); tool-use / structured-output interfaces | `PARENT_OWNED` | translator-invariance gate `[OPEN_M5]` |
| exact-checker channel | Lean / SymPy; ME-X3 cross-check (own) | `PARENT_OWNED` | — |
| comparator arms (A14) | `mex1_parents` (own faithful re-implementations); RWR retrieval; CBR (Aamodt & Plaza 1994); KG-QA retrieval; LLM alone | `ABSORBED_AS_PARENT` | expected `PARENT_SUFFICIENT` on ME-X1 and P2 |
| parameter study (KS-T21) | walk-forward validation; `[[feedback-no-hardcoded-params]]` | `PARENT_OWNED` (methodology) | — |
| the machine as a whole (unbundled store + solver + codec) | ATMS-backed problem solvers (de Kleer & Williams GDE 1987); KG-QA systems; CBR systems | `PARENT_PRODUCT_SUFFICIENT` until the end-to-end gate is frozen and passed | the only stated delta anywhere is KS-T04's exact-share retraction under a typed restart walk, and KS-T15's channel typing; both are constraints |

## What could remain ORION-specific enough to investigate (from the parent-subtraction doc, unchanged)

1. Exact-share retraction *composed with* query-conditioned typed navigation (KS-T04 on `W_Q`) — a
   difference exhibited on a witness, not yet a measured advantage on any registered task.
2. The obstruction-witness rule as a terminal outcome of retrieval (KS-T19) — a *property* (honest
   refusal), measured by false-escalation rate (ME-X2: 0), not by accuracy.
3. Warrant typing of channels (KS-T15) — a constraint whose value shows only when feedback-trained
   parents assert unwarranted answers on the registered probes; that comparison is `[OPEN_M5]`.

Everything else is `PARENT_OWNED`. That is the expected shape of an honest design.
