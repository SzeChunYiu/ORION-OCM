# GMI Experiment Programme v2 — derive every known form, be predictive, predict a new form

Status: **main-researcher plan against the user's success criteria (2026-09-11). Supersedes nothing; sits on `GMI_VALIDATION_PROGRAMME_V1.md` (levels F0–F3, E1–E7) and `GMI_KNOWN_FORM_DERIVATION_LADDER_V1.md` (D0–D3) and states, per criterion, what is done, what is running, what is next, and what each step can and cannot earn.** Refs #377, #233, #373, #165, #221.

The criteria (user, verbatim in substance):

```text
S1  the theory must derive neural networks, machine learning, all kinds of existing machine intelligence
S2  the theory must be predictive
S3  we should be able to predict a new form of machine intelligence — work until we can
S4  plan the experiments needed to support GMI theory
```

## 0. The one-paragraph state

The theory derives the major known forms at level D1 (constructive, with charged constants) for five row families and one basis family, and at D0 (embedding in one realization normal form) for every family Codex registered. It is predictive at the exact layer in the operational sense (frozen numeric prediction → fresh evidence) with a recorded score of 5 held / 5 failed / 3 pending over 25 records, every failure diagnosed and revived. It has **not** derived any form at D2 (blind rediscovery) except memory forms, and has **not** predicted a new form (E6 locked: no hole; every predicted hole occupant so far is a known parent). The path to S3 is concrete and staged below; the honest possible terminal of that path is "the theory predicts that no undiscovered form exists at these scopes", which would itself be a result.

## 1. S1 — derivation status of every known form

Levels (`GMI_KNOWN_FORM_DERIVATION_LADDER_V1`): **D0** embedding in the realization normal form; **D1** constructive derivation from a basis with charged constants; **D2** blind rediscovery by label-free search; **D3** prospective phase prediction (predicted before the run where the form wins).

| known form | exact-layer row / basis | D0 | D1 | D2 | D3 |
|---|---|---|---|---|---|
| neural / gradient (backprop) | M4, S4 (ReLU net, fixed-point backprop; native adjoint in B1) | yes | **compiled** (GMI-T4/T5 corrected; sizes 1–4 h) | **no** — exists in grammar (0.9258 planted) but unreached at 10^5 × 3 (RV-018); diversity lever running (RV-023) | **yes** on the revision axis (RV-017, 336/336; RV-025 running) |
| exact symbolic / program search | M2, S2 (consistency search), S2a (scoring search), P3 basis | yes | compiled (GMI-T8) | no (not attempted: search forms need a grammar-over-grammars leaf) | yes: owns r = 0 (RV-017) |
| algebraic / linear identification (GF(2)) | S6 (RV-024) | yes | compiled | no | **running** (predicted occupant of the parity hole) |
| production / rewrite (rule systems) | M1 (typed store + match + rule addition) | yes | compiled (GMI-T7) | partial: blind winners on binding ecologies are store-based rewrite forms (7/9, 6/7) | yes: type axis (Stage E) |
| probabilistic / generative | M3, S3 (particles over a grammar) | yes | compiled (GMI-T6; native sampling in B3) | no | inadmissible on every executed ecology (never on a frontier) — **gap: no ecology yet registered where the stochastic form should win (partial observability / expensive observation axis)** |
| exemplar memory | M5, S5 | yes | compiled | **yes** (two seeds) | yes (Stage E) |
| generalizing memory / kNN / retrieval | S5h (corrected in RV-025) | yes | compiled | no | running (closed-form admissibility law) |
| in-context / meta-learned adaptation | — | yes (Codex normal form; Chan 2022, Mikulik 2020 parents) | **not compiled** | — | — |
| attention / Transformer | — | yes (D0 only) | **not compiled** | — | — |
| reinforcement / temporal credit assignment | — | yes (D0 only) | **not compiled** | — | — |
| library learning (DreamCoder / Stitch) | P3 basis (compressed-program parent) | yes | as a basis, not as a row | — | — |
| continual / plasticity-preserving | — | yes (D0; L1 parents) | not compiled | — | — |
| evolutionary / population search | Γ (the search family), not a row | yes | as the generator | — | — |
| OCM-like explicit governed developmental | Codex `GMI_SPECIALIZATIONS_V1` | yes | outside the exact layer | — | — |

**What S1 still needs (in order of leverage):** (a) three missing D1 rows — in-context adaptation (a row whose query conditions on a context store without a weight update), attention (content-addressed weighted retrieval: S5h with learned similarity is the minimal ancestor), temporal credit assignment (a row with delayed scalar reward); each is a compiled program in the same universe with charged constants; (b) an ecology axis on which the stochastic form is predicted to win (partial observability), so that M3/S3 gets a D3 row; (c) D2 for the dense form (RV-023), after which D2 for the search form becomes attemptable.

## 2. S2 — what "predictive" means here and the record

Operational definition (the #373 protocol): a numeric prediction on fresh evidence, frozen in a commit before the run, with a named falsifier; outcome recorded verbatim. Record so far (`REVIVAL_LEDGER.jsonl`):

| held | failed (diagnosed, revived) | pending |
|---|---|---|
| RV-013 per-phase growth orders (0/30 misses at fresh sizes); RV-017 E_smooth3 336/336 cells; RV-019 F1 second seed; RV-020 PH-5; RV-022 PH-5 balanced | RV-009 (locality mechanism → per-event work); RV-014 (dense row uncertified → admissibility-before-phase rule); RV-015 (existence → grammar depth); RV-016/018 (reachability → search family, then ecology diversity); RV-021 (instrument: Boolean XOR → corrected row, per-ecology certification) | RV-023 diversity; RV-024 hole occupant; RV-025 three classes, 1 586 cells |

The failures are as informative as the holds: each moved a rule into the protocol (design §9, now with an eleventh: check every declared row against its own closed form in one column before freezing). **S2 at the exact layer is earned in the weak sense (prospective, at scope) and unearned at the real-system layer (E1/E2 OPEN).**

## 3. S3 — the path to predicting a new form

Standard (`UNKNOWN_MORPHOLOGY_PROGRAMME_V1`, `PHASE_HOLE_AUDIT_V2` §4): a hole is a frozen region where every parent and ordinary hybrid fails a registered property vector within cost bounds, with a lower bound or obstruction explaining why and theory predicting headroom; a new form must survive the reduction attack and climb U0–U6.

What the exact layer can do that the atlas cannot: **enumerate**. At tiny scope the whole candidate space of a neutral grammar is finite, so the Pareto frontier of (capability, charged cost) over ALL programs can be computed exhaustively and every frontier point classified. This converts "is there a hole?" from a literature audit into a computation.

### 3.1 E6-at-scope: exhaustive frontier census (next laptop experiment, RV-377-026)

- Feasibility (counted before freezing): the blind grammar has 1 040 candidates of total size 2, 89 440 of size 3, 988 000 of size 4, 33 million of size 5 and 489 million of size 6 (f + ≤ 2 writes, no SEL), so an exhaustive census reaches total size 4 (1.08 million candidates, ~40 core-minutes per ecology) and, with semantic deduplication, perhaps 5. The learners live at size ≥ 15 (the four-coefficient gradient learner is 43 nodes) and the kNN form needs a scan loop the grammar does not have, so **the census cannot settle E6 in the learner regime; it settles the minimal-size occupants and exact size lower bounds** below which no admissible program exists.
- Freeze: the size-ordered census to total size 4 (declared grammar: f and write expressions over 4 input bits + 4 cells + store leaf + 4 constants; ≤ 2 writes; dead-write elimination; canonical by semantics on the protocol) on E_bind16 and E_smooth8.
- Prediction frozen before enumeration: on E_bind16 the smallest admissible programs (θ = 1.0) have size 2 (f = L, g = INSERT y) and every admissible program of size ≤ 4 classifies LOCAL_MEMORY or STORE_PLUS_NUMERIC; on E_smooth8 (θ = 0.85) NO program of size ≤ 4 is admissible (exact lower bound ≥ 5 on the size of any admissible form); every Pareto point of (score, cost) at size ≤ 4 classifies into a registered class.
- Falsifier (= a new-form candidate at scope, U0–U3): a Pareto point whose canonical program is not compilable into any registered row at ≤ 2× cost (the reduction attack §5 of the programme, run mechanically).
- What it earns: if the prediction holds, `KNOWN_PARENT_FRONTIER_COMPLETE_AT_SCOPE` for that grammar — the theory then *predicts* that no undiscovered form exists at that scope, which is a falsifiable, non-trivial statement, and the census gives the exact lower bounds the hole criterion demands. If it fails, U0–U3 at scope, and the candidate's property vector is what a larger neutral search would be asked to find (U4 needs a second, larger grammar with the property predicted first).

### 3.2 Hole census over axes (RV-377-027, laptop)

Sweep the registered axes — task type (binding / smooth / algebraic), criterion (all / unseen), horizon H, revision rate r, diversity, precision (FRAC_BITS), revision semantics (revoke vs relabel) — with the row set S2/S2a/S4/S5/S5h/S6/S3 and the cost model, and list every cell where no registered row is admissible. For each such cell, predict the occupant's property vector from the target algebra and the ecology (as RV-024 did for parity) BEFORE building a row; build the minimal row; test. Every occupant that turns out to be a known parent narrows the hole map; a property vector no parent satisfies is the E6 unlock condition (with the exhaustive census as its lower bound).

### 3.3 Unlock discoverability first (RV-377-023, running)

A search that cannot rediscover the known dense form (RV-018) cannot be trusted to discover an unknown one. Diversity is the frozen lever; if it works, the same ecology family becomes the first neutral-search bed for §3.1/§3.2 candidates at 10^6–10^7 evaluations (still laptop-days; #221 for more).

### 3.4 Honest terminals for S3

```text
NEW_MORPHOLOGY_CANDIDATE_AT_SCOPE (U0–U3)      : a frontier point outside every registered class survives the reduction attack
THEORY_PREDICTED_BEFORE_SEARCH (U4)            : its property vector was frozen from a hole census before the grammar that found it
KNOWN_PARENT_FRONTIER_COMPLETE_AT_SCOPE        : the exhaustive census finds only registered classes — the theory predicts NO new form at scope
```

The third is a legitimate success of the theory's predictive power, not a failure of the programme; the user's S3 is satisfied only by the first two.

## 4. S4 — the experiment plan (staged, with budgets and what each earns)

| stage | experiment | budget | earns / unlocks |
|---|---|---|---|
| now (running) | RV-023 diversity evolution 3 × 10^5 | laptop 35 min | D2 for the dense form; the ecology lever on discoverability (gate 3 of §3 in the note answer) |
| now (running) | RV-025 three-class frontier, 5 ecologies, 1 586 cells | laptop 10 min | D3 with three classes; closed-form admissibility law; basis-dependent occupant on the revision axis |
| now (running) | RV-024 parity-hole occupant | laptop 6 min | the property-first method for ④ at scope |
| next | RV-026 exhaustive frontier census (§3.1) | laptop hours (≤ 10^7 candidates × 3 ms per ecology; parallel over 4 cores) | E6-at-scope: either a new-form candidate (U0–U3) or KNOWN_PARENT_FRONTIER_COMPLETE_AT_SCOPE with exact lower bounds |
| next | RV-027 hole census over axes (§3.2) | laptop minutes per cell | the hole map; predicted occupant property vectors |
| next | D1 rows for in-context adaptation, attention, temporal credit; a partial-observability ecology for the stochastic form | laptop | S1 rows 8–10; a D3 region for M3/S3 |
| next | blind recovery of the search form (needs a grammar leaf for enumeration) | laptop | D2 for symbolic forms |
| then | neutral search at 10^6–10^7 evaluations under diversity, in predicted holes | laptop-days or #221 | U4 attempts |
| Track A (outside this lane) | E1/E2 cross-paradigm semantic-proposal-geometry predictions on real families; E3 math/code episodes (#46, #208); E4 lifelong machine | real domains | "empirically supported general developmental theory" |
| last | E7 meta-morphogenesis (burden-to-improve declining across generations) | #221-class | RSI rung; not before E5/E6 |

Rules that bind every row (design §9 + the eleventh from RV-021): admissibility certified per ecology before freezing; every declared row checked against its closed form in one column; prediction sha in the commit before the run; outcomes verbatim; no budget escalation without a diagnosed mechanism; classification post hoc after dead-write elimination; a KNOWN-form terminal is recorded as a result, never hidden.

## 5. Claim ceiling of this plan

`S1_D1_FOR_SIX_ROW_FAMILIES__D2_MEMORY_ONLY__S2_PROSPECTIVE_AT_SCOPE_5_HELD_5_FAILED__S3_NOT_EARNED__E6_LOCKED__EXHAUSTIVE_CENSUS_IS_THE_NEXT_DECISIVE_STEP`
