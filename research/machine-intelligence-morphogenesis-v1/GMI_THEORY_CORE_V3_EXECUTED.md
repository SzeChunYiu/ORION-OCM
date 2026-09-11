# GMI Theory Core v3 — the executed theory: laws, reachability, cost per intelligence, gap register, ability predictions

Status: **main-researcher synthesis of all three lanes (Codex GMI-v1, ChatGPT VLC/CP predictions, this lane's executed records RV-377-001…037) as of 2026-09-12. Explicitly NON-FINAL; every law carries its evidence class and claim ceiling.** Refs #377, #233, #373, #165, #418, #419, #409, #410. Generated tables: `GMI_COST_AND_REACHABILITY_TABLE_V1.md`. Ledger: `REVIVAL_LEDGER.jsonl`.

The mandate (user, 2026-09-11): fill the logic gaps recursively; derive every existing kind of machine intelligence; explain their reachability and their cost per intelligence; predict new forms and their abilities so that experiments can verify them.

Evidence classes used below: **PROVED** (theorem, parent-owned or in `proofs/`), **EXACT** (executed at the 8-bit exact layer, frozen prediction held), **EXACT-FAILED** (frozen prediction failed, diagnosed), **PARENT** (established in the literature at primary-source depth), **PENDING** (frozen, running), **OPEN**.

## 1. The theory in seven laws

**L1 — No unique cognitive unit; realization is compilation with a cost signature.** Any charged universal basis realizes every registered form with identical development tables (C2 on ~1 500 executed cells across six bases and nine columns); bases differ by finite self-simulation bands (3.2 or 131) and by per-phase growth orders that every compilation preserves (GMI-T10-B). The only representation-independent object is the task-relative semantic developmental state (Codex S_Ω). *EXACT + PROVED (Codex T13/T16 flattening; GMI-T0).*

**L2 — The generator of forms is θ = (Ω, ρ, Γ).** Ω the ecology (task algebra, feedback type, horizon H, revision rate r, seen/unseen split, task diversity, observation count, label noise, regime set), ρ the charged cost model, Γ the search/development process. The form that appears is the ρ-cheapest realization that is admissible on Ω and reachable by Γ. *EXACT at scope: RV-017 (336/336), RV-025 (1 569/1 586), RV-024, RV-030; PARENT (Codex RP3/RP5/RP14/RP15).*

**L3 — Four gates bind in order: existence, admissibility, discoverability, cost.** A form must exist in the generator's grammar (RV-015: learning-rate expressibility; RV-029/031: weight precision; RV-030: estimator variance), be admissible under the ecology's criterion (unseen inputs, noise, observation count, algebra: RV-014/017/020/022/024), be reachable by the search under the ecology's selection gradient (RV-016/018/023/028), and only then compete on cost. *EXACT.*

**L4 — Cost laws.** (a) Revision axis: the occupant flips from the search form (r = 0) to the cheapest-update admissible form at r* = (ΔA)/(Δc) with A = desc + H·exec and c = upd + ver + rev/4 (Codex RP3; RV-009/017). (b) The r ≥ 1 occupant is basis-dependent at equal admissibility: generalizing memory in local-transducer bases, gradient in uniform/compressed-program bases (RV-025). (c) Admissibility boundaries can be closed-form: the Hamming-averaging memory is admissible iff the target's local curvature is below the tolerance (a ≤ 7/16; held at four points, RV-025). (d) Materialization curvature keeps realizations factorized even at zero revision rate in every arithmetic-native basis; the monolithic compiled table wins only where lookup is native and arithmetic emulated, at long reuse with no revisions (RV-032: B2 at H ≥ 128). (e) Versioning (verify-before-swap) wins iff the retention price of a wrong served answer exceeds a basis-dependent threshold λ* = {92, 142, 4 036} across bases (ChatGPT VLC v2 inequality; executed instance RV-032: RSTAR → VLC in five of six bases, T3 → unversioned everywhere). (f) Compile-amortization: a source→phenotype organization enters the frontier only beyond H*(basis) = (compile work per window)/(interpretation − lookup cost per query), finite in one of six bases (RV-033: 1 410 reuses per rebuild in B2). *EXACT (a–f), each at one seed and scope.*

**L5 — Reachability law (label-free search).** A search family reaches the class along whose fitness there is a monotone path under the ecology: exact binding → memory forms (7/9, 6/7 at two seeds); a single fixed smooth target → inert transducers (3/3 seeds at 10^5, two families); sign-flip task diversity → context-conditioned memory forms (3/3 seeds), i.e. the in-context class the parents predict, before any in-weights learner; the dense learner needs three to four coordinated depth-3 writes and is not assembled at 10^5 (10^6 PENDING). Existence is certified separately (planted learner 0.93). *EXACT; PARENT (AutoML-Zero, Chan 2022, Mikulik 2020).*

**L6 — Instrument parameters are part of θ.** Update-expression depth (G_DEPTH), fixed-point precision (FRAC_BITS), estimator family, and the emulation macros' exact semantics decide which forms exist; four macro/instrument defects were found by C2 failures and closed (Boolean XOR; SHR on negatives; NORMALIZE saturating sum; the mis-derived clause rule). *EXACT (RV-021/026/029/031).*

**L7 — Negative controls hold.** Under scalar loss on a parity target nothing develops on either split (RV-020/022); the predicted occupant property (XOR closure) holds exactly where the seen set spans GF(2)^4 (RV-024). *EXACT.*

Claim ceiling for the seven laws: exact at tiny scope, one seed per frontier prediction, a frozen charged price vector (not hardware prices), and no real-system validation (Codex E3/E4 OPEN).

## 1b. Derivation: why a neural network (and any machine-learning algorithm) is a machine intelligence, and when it is the one that appears

The theory's definition (Codex `GMI_CORE_ANSWER_V2` §15): a machine intelligence is a resource-bounded realization of the future-relevant semantic distinctions an obligation requires, with (i) a mechanism that generates candidate cognition, (ii) a law by which experience changes that generation, and (iii) optionally a process that changes the realization itself. "Why can a neural network be one" is therefore four derivations, each with its evidence:

**Step 1 — existence (D1).** From any basis with + and × on the parameter type, a finite feed-forward threshold/affine composition is a compiled program (GMI-T4), and the gradient update law is a specialization: reverse-mode adjoints are the request/adjoint combinator natively (B1) or the explicit macro at a constant factor (GMI-T5, corrected for Gavranović 2022). *EXACT at sizes h = 1…4 in six bases; PARENT (backprop as functor).*

**Step 2 — admissibility (the semantic-distinction clause).** On an ecology with real-valued targets and an unseen-input criterion the parametric map realizes the required distinctions iff (a) the target class is approximable by the family (universal approximation at finite width, PARENT: Cybenko 1989 for the general case; exact enumeration at scope) and (b) a stable step is expressible (learning rate below 2 over the number of simultaneously active inputs, RV-015) and (c) the development length suffices (RV-014: 48 events insufficient at 0.841; 16 events sufficient at 0.86–0.89). *EXACT; the general-case sample-complexity bound is PARENT-owned.*

**Step 3 — cost (why it is the occupant where it is).** Its per-event update work is Θ(p) (parameters), its query work Θ(p), its revision work Θ(p·n_stored) (retrain from the store). Every exact or approximate program search pays Θ(|G|·m) per event (|G| grammar size, m stored examples; ~200× here) and a generalizing memory pays Θ(n) per query and O(1) per update. Hence at revision rate r ≥ r*(H) the gradient realization is the cost-minimal admissible form **unless** a generalizing memory is admissible (Hamming-smooth target) **and** the basis's native query cost favours it (RV-025: memory wins B0–B3, gradient wins U/P3). *EXACT (RV-017 336/336; RV-025 1 569/1 586); PARENT (Levin/OOPS accounting; Codex RP3).*

**Step 4 — reachability (why it can arise, not only be designed).** A neutral search reaches it only when the ecology supplies a selection gradient toward learning (task diversity: RV-023) and the search family can assemble coordinated writes (budget/family: RV-018, RV-028 PENDING). Existence is certified independently (planted 0.93). *EXACT (negative at 10^5), PARENT (AutoML-Zero rediscovered linear regression and backprop at ~10^7 evaluations).*

**Step 5 — the definition's clauses.** (i) generation of candidate cognition = the forward pass (a proposal geometry over outputs, Codex SPG; the neural K1 C1 receipt shows history changes proposal probabilities on fresh tasks); (ii) the experience→generation law = the gradient step (Step 1); (iii) self-change = architecture/optimizer change (Γ), optional and here supplied by the search family. *D0 EXACT (embedding), K1 EXACT at synthetic scope (Codex), K2 OPEN.*

**Registry row.** `GMI-TN1` (neural occupancy, finite exact): *Under assumptions A1 (numeric-native basis with + and × on the parameter type), A2 (real-valued targets approximable by the family to tolerance θ), A3 (a stable expressible step), A4 (development length ≥ the certified length), the gradient realization exists, is admissible, and occupies every (H, r ≥ r*) cell of the frontier in which no Hamming-smooth memory is admissible or the basis's query cost favours the gradient; a neutral search reaches it only under a selection-gradient ecology with an assembly-capable family.* Proof class: PARENT (Steps 1–4 general case) + FINITE_CERTIFIED (executed cells). Falsifiers: a gradient row certified admissible that loses an r ≥ r* cell to a non-memory form; a memory form winning U/P3 at equal admissibility; a blind dense winner without diversity.

**Generalization to every machine-learning algorithm (`GMI-TN2`).** An ML algorithm is an update law U with its query law Q; each registered law is a compiled specialization (gradient GMI-T5, conditioning GMI-T6, rule addition GMI-T7, program search GMI-T8, memory insertion M5, kNN S5h, XOR identification S6, RL-as-inference R1) and therefore satisfies clauses (i)–(ii) of the definition; **which one is "the" intelligence of an ecology is the frontier occupant of L2–L4, and its region has been predicted before the run for the gradient, search, memory, algebraic and RL-inference laws** (RV-017/024/025/030), while the probabilistic and policy-gradient laws are precision/estimator-gated at this scope (G5). Claim ceiling: `NEURAL_AND_ML_FORMS_DERIVED_D0_D3_AT_EXACT_SCOPE__GENERAL_CASE_PARENT_OWNED__REAL_SYSTEM_VALIDATION_OPEN`. What would improve it further: the hardware-priced cost vector (G1) to turn "why neural networks dominate in practice" from parent hypotheses N1–N6 into a predicted region, and Codex E3/E4 for real regimes.

## 2. Reachability of the existing forms (D2, label-free)

| form | reached blind? | ecology / search family / budget | gate that decides |
|---|---|---|---|
| exemplar memory / rewrite (M1/M5) | **yes** (7/9, 6/7) | exact discrete binding; random + hill-climb, 3 000 + 40 | cost + admissibility (any generalizing form is dominated) |
| context-conditioned memory (in-context type) | **yes** (3/3 seeds, 0.73 plateau) | smooth diversity ecology; regularized evolution 10^5 | discoverability: diversity creates the selection gradient |
| dense gradient learner (M4) | **no** at 10^5 × 3 (two families); 10^6 PENDING (RV-028) | E_smooth8; certified representable (0.93) | discoverability: 3–4 coordinated writes; no monotone path from the memory plateau |
| approximate / exact program search (M2) | not attempted (needs a grammar-over-grammars leaf) | — | existence in the search grammar |
| algebraic identification (S6) | not attempted | — | existence |
| stochastic / Bayesian (M3, S7) | not attempted | — | precision (weights over > 16 hypotheses underflow at 4 fractional bits) |
| RL consistency search (R1) | not attempted | — | existence |
| policy gradient (R3) | not attempted; not even admissible as a designed row at 8 bits | E_credit | estimator variance / precision |

The reachability account in the note's terms: **what is found is decided before what is cheapest**; the exact layer shows the order in which a neutral search climbs (inert → memory → context-conditioned memory → ?dense) and that an ecology change alone moves the plateau (+0.28 in score, RV-023), whereas a 10× budget alone did not (RV-018 → RV-028 PENDING).

## 3. Cost per intelligence (the note's d(development)/d(cost))

From `GMI_COST_AND_REACHABILITY_TABLE_V1.md` (B0 column, headline cell H = 16, r = 1, admissible rows only):

| form | capability | lifecycle cost | capability per kilo-cost |
|---|---|---|---|
| XOR-linear identification (parity, balanced split) | 1.00 | 451 | 2.22 |
| generalizing kNN memory (E_smooth3 / E_sym3) | 0.90–0.94 | 2 684 | 0.34–0.35 |
| gradient net h = 4 (E_smooth3 / E_sym3) | 0.86–0.89 | 3 349 | 0.26 |
| approximate program search (E_sym8, target in grammar) | 1.00 | 27 618 | 0.036 |
| approximate program search (E_smooth3, target outside grammar) | 0.96 | 90 767 | 0.011 |

Reading: at this scope the cost of a unit of capability is set by per-event update work, not by description or query cost; the cheap-update forms (memory, gradient) dominate whenever they are admissible, and the expensive-update search forms survive only where nothing else is admissible (parity, exact identification) or at r = 0. The note's "→ ∞" does not occur: capability is bounded by admissibility and cost grows at least linearly in revisions; the ratio is a point on the (H, r) diagram, and the *law* is the crossover structure of L4, not a derivative. What is missing for a developmental-productivity law (K1/K2 capital): real-system evidence (Codex E1 OCM capsule is the only real K1 evidence; K2 unestablished).

## 4. Recursive logic-gap register

Each gap names what closes it; a closed gap opens the next one (the recursion). Status as of this file.

| id | gap | closes it | status / record |
|---|---|---|---|
| G1 | frozen charged price vector, not hardware prices | a second price vector (hardware-priced; tensor-favouring) and the prediction that boundaries move as P-N4 says | EXECUTED (RV-035, held 5/6): under `HW_TENSOR_PRICED` the gradient row wins every (H, r ≥ 1) cell of the two ecologies where it is admissible (168/168) and none where it is not (0/56); capabilities unchanged; the six registered columns byte-identical. Next: a *measured* price vector (G1b) |
| G2 | single seed on every frontier prediction | second seed on RV-017/025/032 ecologies | OPEN (laptop, minutes) |
| G3 | search-row description length is data-dependent (17 misses at H = 1, r = 0) | certify desc per ecology or abstain at the desc corner; rule 13 in design §9 | CLOSED as a rule (RV-025) |
| G4 | base cost model has no retention/exposure term | lifecycle extension: wrong answers served, abstentions, collateral regression, priced by λ | EXECUTED in the E1 microscope (RV-032 PENDING) |
| G5 | probabilistic and policy-gradient forms are precision/estimator-gated at 8 bits | wider-precision universe (FRAC_BITS ≥ 8) as a declared instrument; lower-variance estimator row | OPEN (declared; laptop) |
| G6 | dense form not recovered blind | budget/family (RV-028 PENDING at 10^6; 10^7 declared next); then a grammar-over-grammars leaf for search forms | PENDING |
| G7 | no real-system validation of any law | Codex E3 (code #208 H0 episode; math #46 locked), E4 lifelong machine | BLOCKED outside this lane |
| G8 | the new-form criterion needs lower bounds, not only occupancy | exhaustive size census gives exact bounds only to size 4; formal obstruction proofs for the VLC/CP property vectors against parent products (their E5) | OPEN |
| G9 | attention / soft retrieval needs a normalization primitive | predicted basis-dependence: cheap only where NORMALIZE is native (B3); row S5a declared | OPEN (laptop) |
| G10 | "predict a new form" is currently two property vectors from the other lanes (VLC, CP) with E0 green and E1 outstanding | E1 executed at the exact layer (RV-032 VLC running; RV-033 CP designed in §5); then E3 neutral recovery of P1–P5 / CP-1…6 in the positive region vs twins | IN PROGRESS |
| G11 | K1/K2 developmental capital (does experience lower the next acquisition's burden) | Codex SPG protocols; real families | OPEN outside this lane |
| G12 | reachability of the *search* and *algebraic* forms by neutral search | grammar with a bounded enumeration leaf; predicted: found on exact-binding/parity ecologies where they are the sole occupants | OPEN (laptop) |

## 5. Ability predictions for the candidate new forms (so that experiments can verify them)

The theory predicts *abilities* (measurable behaviours) of a candidate form before it is built or found; a candidate that lacks a predicted ability is refuted, one whose abilities a parent reproduces at bounded cost is a parent product.

### 5.1 Versioned Local Compilation (ChatGPT lane, #418; executed instance RV-032)

Predicted abilities in R* (frequent local revision, strict retention, long reuse, local verifier):
- A1 capability equal to the best modular learner (it changes organization, not learning): exact on unseen-pattern queries;
- A2 zero collateral regression on unaffected queries after a revision (dependency cone honoured);
- A3 zero wrong answers served on affected scopes during a revision window (it abstains until the rebuilt factor is verified), at the price of abstentions ≤ 3 × |cone| × |affected queries|;
- A4 revision cost proportional to |cone| (not to the whole realization);
- A5 frontier membership iff λ_wrong > λ*(basis), with λ* strictly between 0 and 256 in every basis at this scope and larger where verification is emulated (B2);
- A6 loses to the unversioned modular row when λ_wrong → 0 (T3) and when there are no revisions (T1); does **not** lose to the monolith at any horizon here (materialization curvature, L4d), an explicit departure from the VLC document's T1/T2 twins.
Experiment: `gmi_microscope/e1_vlc.py` (five cells × six rows × six bases; verdict `compare_e1.py`). **Outcome (RV-377-032, executed):** A1–A4 held as measured (capability 1.0; 0 collateral regressions; 0 wrong answers served, 96 abstentions; revision ∝ cone). A5 held in five of six bases: λ* = 92 (U, P3), 142 (B0, B1, B3) — inside (0, 256), so RSTAR → VLC and T3 → unversioned modular in those bases — but λ* = 4 036 in B2 where verification is emulated at gate level, so MOD_U wins RSTAR there. A6 partly wrong as I wrote it: at H = 2 versioning still wins (the serving term vanishes, the retention term does not); the monolith wins only in B2 at H ≥ 128 with no revisions (the VLC document's T1 twin holds exactly there). Terminal: `VLC_PHASE_DIRECTION_SUPPORTED_AT_SCOPE_IN_FIVE_OF_SIX_BASES`; the phase boundary is a per-basis threshold λ*(basis) that must be computed before freezing (rule 14).

### 5.2 Cognitive Polyphenism (ChatGPT lane, #409/#410; RV-033 designed)

Predicted abilities in P+ (≥ 3 regimes sharing one latent semantics, ongoing revision, sparse active regime, finite compile cost, long reuse):
- B1 cross-regime transfer: feedback received in regime A raises capability in regime B without regime-B feedback (mediated by the shared authoritative state);
- B2 update cost independent of the number of *inactive* phenotypes (lazy recompilation), against an eager multi-phenotype hybrid whose update cost grows linearly with the phenotype count;
- B3 stale-phenotype exposure bounded by the version/dependency check (no stale phenotype certifies itself);
- B4 loses to the eager hybrid when regimes ≤ 2 (N1) or compile cost ≥ retrain cost (N2), and to the broad fixed realization when regimes share no semantics (N3).
Experiment (RV-033, executed): E_factored with three regimes over the same factors — exact scope sums, thresholded Boolean answers, and top-factor argmax — rows: eager multi-phenotype hybrid, single broad interpreter, CP lazy source→phenotype with version tags, per-regime independent learners (no sharing); cells P+, N1 (one regime), N2 (compile price × 16), N3 (independent factor sets per regime). Kill: B1 fails (no transfer) or the eager hybrid wins P+. **Outcome (RV-377-033):** B1, B2 and B4 held as measured (transfer 1.0 with zero labels in the derived regimes; lazy update work 2.6× below eager with one of three regimes active, collapsing to 1.0× under dense activity; N1/N2/N3 remove the advantage, N3 is a hole for every organization; the eager hybrid wins no cell). Occupancy: the single interpreter wins P+ at 64 queries per window in every basis; compiled polyphenism enters the frontier only in the store-native basis beyond H* ≈ 1 410 reuses per rebuild. So the CP positive region at this scope is narrower than the document's qualitative P+: `PARENT_FRONTIER_HOLE_NOT_SUPPORTED_AT_THIS_SCOPE_FOR_OCCUPANCY`, `CP_ABILITIES_B1_B2_B4_SUPPORTED_AT_SCOPE`.

### 5.3 What would make either a *new form* rather than a parent product

Both are conjunctions of parent-owned mechanisms; the theory's claim is the **phase law** (where the conjunction wins and loses), not the mechanisms. Novelty requires the E5 reduction attack: a bounded compilation into sparse MoE / SISA / TMS / knowledge-compilation / self-adjusting-computation parents that preserves the ability vector at ≤ 2× cost would end the novelty claim with the parent-sufficient terminal. At the exact layer this attack is executable: compile the VLC/CP row into each parent row and compare lifecycle costs cell by cell.

## 5b. Integration of the ChatGPT lane's theory hardening (seven documents merged 2026-09-12)

The ChatGPT lane added a typed demand signature (`GMI_REALIZATION_DEMAND_SIGNATURE_V1`: Ξ_obl = (σ, Δ_Q, Δ_U, γ_F, ν, χ_V, ρ_use, λ_R, β_lin) with the price vector moved to a context P), mechanism witnesses A1–A7 with behavioural scoring (`GMI_MECHANISM_WITNESS_REGISTRY_V1`), necessity theorems MN1–MN8 (`GMI_MECHANISM_NECESSITY_THEOREMS_V1`), pre-execution gates G0–G12 for E1–E3 (`GMI_E1_E3_THEORY_VALIDATION_GATE_V2`), a predictive-sufficiency no-go (`GMI_PREDICTIVE_SUFFICIENCY_NO_GO_V1`) and a 48-item gap ledger (`GMI_THEORY_GAP_LEDGER_V1`). None of these cite the executed records; they extend without conflict. Reconciliation with the executed layer:

| their object | executed instance in this lane | status |
|---|---|---|
| A1 factor/materialization partition; A3 dependency-tracked incremental repair | MOD_U and VLC rows (per-factor tables; cone rebuild); measured blast radius = cone (RV-032); single-mechanism rows MONO_A3, MONO_A4, MOD_NOA3 (RV-037) | **executed (RV-037, held 5.5/6)**: A4 is the only mechanism that changes a behavioural witness (wrong served 60 → 0, abstentions 0 → 96, in every column); A1 and A3 change cost only (update work 101 469 → 669 → 387 in B0); interactions I_A4×A1A3 < 0 and I_A3×A1 > 0 in all six columns and *independent of λ* (the T3 half of clause 6 was a prediction-writing error: single-mechanism witnesses cancel λ in the contrast) |
| A4 speculative candidate isolation (verify-before-swap) | VLC row: shadow build, verifier, atomic swap, abstention (0 wrong served vs 60) | executed as a bundle with A1+A3; per-basis threshold λ* = {92, 142, 4 036} is the A4 activation boundary |
| A2 authority/serving separation | all compiled rows (source learner + tables); CP row (source + regime phenotypes) | executed; MN2's side-information bound not measured |
| A5 historical persistence, β_lin | `gmi_microscope/e1_lineage.py` (RV-038): E_EPHEMERAL vs P_PERSISTENT_D1/D8 with identical revision process; rows MOD_U, HIST_SNAP, HIST_LOG | **executed (RV-038, held 4/5)**: MOD_U inadmissible under P in every column (as-of 0.5 / 0.42) and the frontier winner under E; both A5 encodings 1.0 (MN7: witness does not identify encoding); encoding tournament flips with depth in *all six* columns (LOG at depth 1, SNAP at depth 8; H*(depth) = desc surplus 3 020 / exec gap); the native-column depth-1 clause failed by description amortization (H* = 169 > 64) |
| Δ_Q vs Δ_U split (MN5) | CQU1–4 cells (`main_collision`, RV-036): query scope local/global × update cone local/global | **executed (RV-036, held 5/5)**: MONO_C wins only native-lookup × global-query × zero-update cells (6 cells, all B2); VLC beats MOD_U only in the global-update cells (λ* = 27 / 52 vs 406 / 429 in B0; exposure 656 / 308 vs 20 wrong served); sign pattern of (256 − λ*) = (−, −, +, +) in five columns, (−, −, −, −) in B2; with the update cone fixed, query geometry alone flips the (128, 0) occupant in B2 (VLC → MONO_C): no scalar dependency coordinate predicts it |
| P (price vector as context, not demand) | the six registered columns + the declared HW_TENSOR_PRICED column (RV-035, held 5/6) | executed as L4b/L4e basis-dependence; the price vector flips the occupant only within the admissible set (L3 before L4) |
| G0 typed measurement freeze | our coordinates are exact op counts (I0) | passes by construction at this layer |
| G1 collision matrix; G2 factorial; G3 implementation tournament | G1 → RV-036 (collision cells); G2 → RV-037 (A1/A3/A4 factorial); G3 → RV-038 (snapshot vs undo-log encodings of A5) | **all three executed at scope** (held 5/5, 5.5/6, 4/5); RV-032/033 remain E1-L3 (parent frontier); L1/L2/L4 now have their factorial |
| G4 adaptive-search firewall (D/V/P layers) | the freeze-before-run rule with disclosed calibrations; no protected layer separate from development | partially satisfied; a protected world set must be declared before E3 |
| G11 phase language | this lane already restricts itself to finite frontier crossovers (r*, H*, λ*) | satisfied |
| MN1 rollback information ≥ log2 max fiber | VLC keeps two copies of a 4-entry table (rollback information = 32 bits) | consistent; bound not tested |
| MN5 overcompression no-go (F vs G cost table) | MONO_C (coarse) vs MOD_U (fine): fine wins every local-query cell in every column at every H ≤ 128; coarse wins only global-query × native-lookup × U = 0 (RV-036) | **executed and held**: exactly MN5's Q-global/U-small regime, and nowhere else |
| their gap ledger G-07/09/12/14/22/23/27/31/32/34 (P0, block strengthened E1–E3) | this lane's G3/G4/G6/G8 overlap G-14 (history), G-27 (frontier uncertainty), G-31/32 (search firewall/encoding) | cross-referenced; P0 items executable here: G-07 (RV-036), G-23 (factorial), G-27 (frontier margin rule already used: 10%) |

Executable asks from their documents at this layer, in order of cost: (1) C-Q/U collision cells — **RV-036 executed, held**; (2) A1/A3/A4 matched ablations of the VLC row (their G2) — **RV-037 executed, held**; (3) MN4 lineage twin with legal historical queries (A5) — **RV-038 executed, held**; (4) the A5 implementation tournament — **two of four encodings executed in RV-038 (snapshot, undo log); copy-on-write and persistent root remain**; (5) MN1 fiber-size rollback test; (6) PS1 signature-collision construction.

### 5c. What the four twins established together (RV-035…038, all executed 2026-09-11)

- **The occupant is selected by three separable things and nothing else at scope:** admissibility (L3: a price vector cannot rescue an inadmissible form, 0/56 cells), then per-basis cost crossovers (H*, r*, λ*), then the price vector (which flips the occupant only inside the admissible set, 168/168 cells). The note's question 3 ("why do neural networks dominate") has an executed answer of this shape: a price vector under which the gradient row's update-plus-verification work is cheaper than the memory's flips every admissible cell to the gradient row, with capabilities unchanged.
- **Demand needs at least five coordinates, not one:** reuse H, revision U, retention price λ, query scope Δ_Q and update cone Δ_U — RV-036 shows Δ_Q alone flips the occupant with Δ_U held fixed, so no scalar dependency coordinate reproduces the executed table. RV-038 adds a sixth, persistence depth, which makes single-version forms inadmissible and selects among history encodings through H*(depth).
- **Mechanisms split into witness-changing and cost-changing classes:** only verify-before-swap (A4) changes a behavioural witness; factorization (A1) and incremental repair (A3) change costs, and their interactions are independent of λ. A demand-signature prediction of the occupant therefore needs λ only for the witness-changing mechanisms.
- **Three of the four records failed one clause each, all by the same fault:** a clause written from a one-column calibration or in contradiction with another clause of the same record (RV-035 clause 6, RV-037 clause 6 T3 half, RV-038 clause 4 native columns). Protocol rules 12 and 14 (per-column threshold before freezing; check clauses against each other and against the disclosed calibration) are now mandatory in the freeze checklist.

## 6. E-series status across the three lanes

| lane | level | status |
|---|---|---|
| Codex | E0/F0–F3 formal synthesis; exact calibrations (realization, semantic quotient, information bound, bias-phase crossover) | GREEN, receipts reproduce (182 tests pass in this lane's checkout) |
| Codex | E1 neural SPG C1 (synthetic representation learning) | EXECUTED: `NEURAL_K1_SEMANTIC_PROPOSAL_GEOMETRY_SUPPORTED_AT_REGISTERED_SYNTHETIC_SCOPE` |
| Codex | E1 OCM real evidence (#323 K1/C2) | EXECUTED capsule |
| Codex | E2 cross-paradigm bias phase (exact) | GREEN (finite exact) |
| Codex | E3 math/code | gates frozen; #46 locked; code H0 episode (#208) pending — **not runnable here** |
| ChatGPT | VLC E0 (v1 failed twin, v2 green) | GREEN; E1 → this lane's RV-032 (running) |
| ChatGPT | CP E0 exact phase | GREEN; E1 → RV-033 (designed above) |
| this lane | D/E/F exact microscopes, RV-001…038 | held: 013, 017, 019, 020, 022, 024, 026, 030, 034, 036 (+ partial 025, 031, 032, 033, 035, 037, 038 — each with one clause scored as a prediction-writing error); failed-and-revived: 009, 014, 015, 016, 018, 021, 029; pending: 028 (10^6, three seeds at ~0.4–0.6 × 10^6) |

## 7. What success requires now (in order) and the kill terminals

1. RV-028 outcome (10^6) → if no dense winner: RV-029b at 10^7 with crossover/macro-mutation added as a declared family element; if still none: `DENSE_FORM_NOT_BLIND_REACHABLE_AT_1E7__SEARCH_FAMILY_INSUFFICIENT` (a real result about Γ).
2. RV-032 (VLC E1) → if held: their V2 rung earned at scope; next E3-lite: neutral search over a grammar with checkpoint/verify/route primitives in RSTAR vs T3, predicted P1–P5 enrichment. If RSTAR is won by MOD_U: `VERSIONING_NOT_ON_FRONTIER_AT_SCOPE`.
3. RV-033 (CP E1) → analogous.
4. G2 second seeds (cheap, laptop); G1 executed (RV-035) — next G1b: a *measured* price vector for one real accelerator, then the same three ecologies.
5. G5 wider-precision universe → probabilistic and policy-gradient D3 rows.
6. Outside this lane: Codex E3/E4 real regimes; E5 reduction attacks on any survivor; E6/E7 only afterwards.

Kill terminals (unchanged from the lanes' programmes): `GMI_REMAINS_SYNTHESIS_METROLOGY__PREDICTIVE_MORPHOGENESIS_NOT_ESTABLISHED`; `COGNITIVE_POLYPHENISM_PARENT_PRODUCT_SUFFICIENT`; `VLC_NOVELTY_NOT_ESTABLISHED`; `KNOWN_PARENT_FRONTIER_COMPLETE_AT_SCOPE`.
