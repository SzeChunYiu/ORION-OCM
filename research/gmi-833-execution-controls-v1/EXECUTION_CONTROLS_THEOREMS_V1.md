# #859 execution controls: definitions and finite theorems v1

Issue #859, child of #833 Section D. Freeze `FREEZE_V1.md` (commit `3682a045`). Claim ceiling `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`.

Every result below is stated at the registered finite scope. That scope is the #901 universe `U` (16 stateless 4-bit output tables plus 65,536 one-bit transducers, 65,552 in total), its 20 frozen cases (40 endpoint worlds and 20 boundary worlds `lambda = lambda* = eta*p/2`), and the encodings, search procedures and weight vectors registered in the freeze. Proofs are analytic where stated. The receipt fields named in each ledger are certified finite checks of the same statements on the registered objects; they are not claims beyond that scope. Numbers quoted here are read from `RESULT_V1.json`.

## Definitions and notation

For a candidate `c`, the canonical projection is `rho(c) = (s, en, ed)`. Here `s` is the number of state bits and `en`, `ed` are the exact error counts on the current-symbol and lag modes. Each mode has 16 scored events: 8 sequences times the 2 scored steps. The resource vector is `r(c) = (en, ed, s)`. A world has parameters `(p, eta, lambda)`, and its weights on `r` are `w = (a, b, c) = (eta*(1-p)/16, eta*p/16, lambda)`. The objective is `J_w(c) = a*en + b*ed + c*s`.

- **Mechanism `K`.** Data-dependent internal state. The fingerprint of `K` on a candidate is "the next-state table is not constant as a function of `(S, M, X)`". The K-dependent target property is `ed < 8`, evaluated as the rate `ed / 16 < 1/2`.
- **Twin descriptor `D(G)`.** The frozen nine coordinates: candidate count, primitive envelope, non-K operator inventory, evaluator id, sequence set, budget, tie rule, stopping rule, and the representable K-free behaviour set. The last is the set of scored-output signatures of K-free candidates.
- **`G-`.** In-place state-register ablation. Every stateful candidate keeps its table slots, and its next-state table is replaced by the constant-0 table.
- **Canonical trace.** The ordered list of `rho` over every item a search procedure evaluates. The **acceptance sequence** is one letter per evaluated item: `N` for a new incumbent, `T` for a tie, `R` for a rejection. Digests are the first 16 hex characters of SHA-256 over the compact JSON of the trace, and over the ASCII letter string.
- **Admissible no-smuggling state of an arm.** Every #855 sub-audit is `CLEAN_AT_REGISTERED_AUDIT_SCOPE`, or it is a sensitivity terminal whose findings are all routed to a registered control. A cost scalarization reversal is routed to D-X4, and a search order dependence to D-X3. An arm is *evaluable* when no sub-audit is `CANNOT_AUDIT_*`.

## DX1-T1 In-place ablation keeps capacity and collapses behaviour

**Assumptions.** The registered `G+` and `G-`, with initial state 0, both modes, and all 8 length-3 sequences.
**Dependencies.** #901 candidate universe and evaluator. `substrate_v1.evaluate_grammar`, checked per candidate against #901 `full_enumeration_v1.build_universe`.
**Falsifiers.** Any coordinate of `D(G-)` differs from `D(G+)`. A `G-` candidate carries the K fingerprint. The K-free class count or multiplicity differs from the stated values (`RESULT_V1.json`: `d_x1_matched_twin.gates.G_MINUS`, `k_free_multiplicity_reweighting`).
**Strongest parents.** Ablation and matched negative-control design (no novelty claimed). #863 R1 background-multiset twin contract, which D-X1 tightens from "count may fall" to "count equal".

*Statement.* In `G-`, the state of every stateful candidate `(nu, o)` is 0 at every step, so its scored output is `o(0, m, x_t)`. Its scored behaviour is therefore that of the stateless table given by the low nibble of `o`, with `rho = (1, en, ed)` of that table. So `G-` realizes exactly the 16 K-free scored behaviours, each with multiplicity `1 + 256*16 = 4097`, and `min ed = 8`.

In `G+`, the K-free candidates are the 16 stateless tables and the 512 stateful candidates with a constant next-state table (`0x00` or `0xFF`). For `0xFF` the state is 1 at both scored steps, so the scored behaviour is that of the high nibble. These candidates realize the same 16 behaviours with multiplicity 33 each. Hence `D(G-) = D(G+)` on all nine coordinates, while the multiplicity change from 33 to 4097 is reported and not hidden.

*Proof.* A constant-0 next-state table sends every address to state 0, and the initial state is 0. The output lookup at address `4*0 + 2m + x` reads only the low nibble. The multiplicity count follows because the 256 next tables and the 16 high-nibble values are free. The same argument applies to `0x00`, and to `0xFF` from `t = 1` onward. Capacity coordinates are properties of slots, operators, evaluator, sequences, budget and rules, and ablation changes none of them. QED.

## DX1-T2 The K target is realizable only by K-carrying candidates

**Assumptions.** Registered ecology `E+`: the lag-mode target is the previous symbol, and all 8 sequences are scored.
**Dependencies.** DX1-T1.
**Falsifiers.** A candidate with a constant next-state table (or with no state) and `ed < 8`. The receipt check `substrate_k_target_only_realized_by_k` and the substrate fact `every_ed_below_8_candidate_carries_k` (65,024 K-carrying candidates, 528 K-free).
**Strongest parents.** #901 frozen derivation of the stateless delay floor `1/2`.

*Statement.* If the next-state table is constant, or absent, then `ed = 8`. Hence `ed < 8` implies the K fingerprint.

*Proof.* With a constant table, the state at scored step `t` is a data-independent constant `k_t`, so the lag-mode output is a function `g_t(x_t)`. Over the 8 sequences, each pair `(x_{t-1}, x_t)` occurs twice. For each value of `x_t`, the target `x_{t-1}` takes both values equally often, so exactly 4 of the 8 lag-mode episodes are wrong at each scored step, and `ed = 4 + 4 = 8`. QED.

## DX1-T3 The persistent-state regime vanishes in the matched twin

**Assumptions.** Every registered world has `p > 0`, `eta > 0` and `lambda > 0`. `G-` is matched in the sense of DX1-T1.
**Dependencies.** DX1-T1, DX1-T2, the #901 law `lambda* = eta*p/2`.
**Falsifiers.** A `G-` world whose argmin contains `s = 1`. `d_x1_matched_twin.phase_law_on_matched_twin.worlds_stateless` below 60, or `phase_law_on_g_plus` other than 20 transitions and 20 boundary ties.
**Strongest parents.** #901 held-out law and its 20/20 transitions.

*Statement.* At every registered world, the `G-` argmin contains only `s = 0` points. On `G+` the law gives `PERSISTENT_STATE -> STATELESS` at 20/20 cases and ties at 20/20 boundaries. The outcome differs between `G+` and `G-` at 40 worlds: the 20 low endpoints and the 20 boundaries. Because the twin is matched, this difference is interpreted against it: the persistent regime requires `K` at equal non-K capacity.

*Proof.* By DX1-T1, every `s = 1` point of `G-` is `(1, en, ed)` with a stateless companion `(0, en, ed)`, and `J` differs by exactly `lambda > 0`. QED.

## DX1-T4 Unmatched twins are refused, whatever the outcome

**Assumptions.** Registered hostiles: H1a (stateful block deleted), H1b (in-place ablation plus a `READ_PREV` primitive), H1c (in-place ablation plus half of the sequence set, with `x0 = 0`), and H1d (in-place ablation plus half the budget; supplementary to the freeze, from the issue's "halve depth/candidate budget").
**Dependencies.** `robustness_record_v1.evaluate_matched_twin`, DX1-T2.
**Falsifiers.** Any hostile returns `MATCHED_MECHANISM_TWIN` (`d_x1_matched_twin.gates`).
**Strongest parents.** #863 R1 `GRAMMAR_TWIN_UNMATCHED`. #855 semantic and cost audits.

*Statement.* The gate returns `UNMATCHED_MECHANISM_TWIN` whenever one of these holds: a descriptor coordinate differs, a K fingerprint remains, the K target stays realizable, or an operator absent from `G+` appears.

H1a differs on count, envelope, inventory and budget. Its objective gets worse at 20/20 low endpoints, and it is still refused: a worse objective in an unmatched twin is not evidence that `K` is necessary. H1b adds `READ_PREV`, which makes the K target realizable without `K` (`ed = 0` at `s = 0`). H1c shows that halving the sequence set alone creates memory-free lag prediction: with `x0` fixed, the minimum lag error is 2 of 8, a rate of `1/4 < 1/2`. H1d differs on the budget only.

*Proof.* Each condition is checked coordinate by coordinate from the grammar objects. The listed mismatches are computed, not declared. QED.

## DX1E-T1 Matched ecology twin

**Assumptions.** `E-` replaces the lag-mode target with a second current-symbol target. The sequence set, mode count, scoring events, `p` grid, evaluator (including `eta` scale), tie rule and budget are unchanged.
**Dependencies.** #901 ecology. `substrate_v1.ecology_descriptor`.
**Falsifiers.** `E-` unmatched, a hostile ecology matched, or a registered world where `G+` in `E-` is not STATELESS (`d_x1e_ecology_twin`).
**Strongest parents.** Matched positive/negative ecology construction (the #959/#957 row owner). #855 ecology audit.

*Statement.* `E-` is a matched ecology twin: every descriptor coordinate is equal, and the lag demand is removed. The table that echoes the current symbol in both modes attains `rho = (0,0,0)`, so for every `lambda > 0` the argmin is STATELESS at all 60 worlds. The hostile twins with half the sequences and with `eta` rescaled are `ECOLOGY_TWIN_UNMATCHED`.

*Proof.* Direct evaluation of the descriptor, and `J(0,0,0) = 0 < lambda <= J` for every `s = 1` point. QED.

## DX2-T1 Projection invariance under a certified bijection

**Assumptions.** A registered map `phi : E1 -> E2` that is total and bijective on the 65,552-candidate census, and satisfies `rho_2(phi(c)) = rho_1(c)` for every `c`. The decision rule factors through `rho`.
**Dependencies.** `encoding_e2_v1` (an independent symbolic interpreter). The layout map `execution_controls_v1.phi_index`. #901 E1 evaluator.
**Falsifiers.** A non-bijective `phi`, a single per-candidate mismatch, or a world whose `phi`-mapped winner ids differ (`d_x2_encoding`: 0 mismatches, 60/60 worlds).
**Strongest parents.** Semantics-preserving transformation and metamorphic testing (Chen, Cheung and Yiu 1998, HKUST-CS98-01). #863 R2 commuting-diagram contract. #875 `GA/GB` semantic re-encoding.

*Statement.* Under the assumptions, the `rho` histograms are equal. For every objective of `rho` and every world, the `rho`-projected argmin sets and their state properties coincide, and the candidate-level argmin of E2 is the `phi`-image of that of E1. Terminal: `ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE`.

*Proof.* `phi` pushes the census measure forward bijectively and preserves `rho`, so every functional of `rho` is preserved. QED.

## DX2-T2 Census-level detection and non-factoring rules

**Assumptions.** The registered hostiles H2a, H2b and H2c.
**Dependencies.** DX2-T1. `robustness_record_v1.evaluate_encoding`.
**Falsifiers.** H2a or H2b accepted as equivalent. H2c not reported as sensitive (`d_x2_encoding.gates`).
**Strongest parents.** #863 R2 hostile (lexicographic surface tie-break). The #901 candidate-id relabelling control.

*Statement.*
- (a) An alleged encoding whose map drops one candidate (`q00002`, one of the four stateless optima) fails the census check with `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`, even though its projected conclusions still agree at all 60 worlds. The census, not the conclusion, is the object checked.
- (b) An E2 evaluator that scales lag error by `15/16` differs on exactly the 65,040 candidates with `ed > 0`.
- (c) A decision rule that returns the lexicographically first surface id among the argmin does not factor through `rho`. At the 20 boundary worlds the E1 minimum is stateless (`q00002`) and the E2 minimum is stateful, because E2 enumerates the stateful block first. The terminal is `ENCODING_SENSITIVE`.

*Proof.* Direct: (a) the domain is 65,551, not 65,552; (b) `ed*15/16 = ed` if and only if `ed = 0`; (c) at a boundary both property classes are in the argmin, so the property of the first id depends only on the id order. QED.

## DX3-T1 S2 is complete by admissibility

**Assumptions.** `LB2(x) = lambda*s <= J(x)`, since the error terms are nonnegative. Pruning is strict: a point is pruned only when `LB2 > incumbent`.
**Dependencies.** #901 `frontier_branch_bound_v1.search`, with its trace reconstructed from its declared order and checked against its returned counters at 60/60 worlds.
**Falsifiers.** A pruned point with `LB2 <= best`, or a mismatch with #901 counters (`d_x3_search.s2_trace_matches_901_counters_worlds`).
**Strongest parents.** Branch and bound (Land and Doig 1960, Econometrica 28:497-520).

*Statement.* S2 returns the complete argmin set, ties included.

*Proof.* The incumbent is always at least the optimum. A pruned point has `J >= LB2 > incumbent >= optimum`, so it is neither optimal nor tied. Strict pruning keeps every point with `LB2` equal to the incumbent. QED.

## DX3-T2 S3 is complete by optimality certificate and tie sweep

**Assumptions.** `LB3(x) = b*ed + c*s <= J(x)`, because the dropped term `a*en` is nonnegative. Pops follow `(LB3, rho)` order. The loop stops only when the smallest remaining `LB3` exceeds the incumbent.
**Dependencies.** `search_procedures_v1.s3_run`.
**Falsifiers.** A certificate whose remaining points include one with `LB3 <= best`. An admissibility violation. A disagreement with S1 at any registered world.
**Strongest parents.** Best-first search with admissible bounds (Hart, Nilsson and Raphael 1968, IEEE Trans. SSC 4:100-107).

*Statement.* S3 returns the complete argmin set. It evaluates between 3 and 16 of the 146 points per world.

*Proof.* At stop, every unevaluated point has `J >= LB3 > incumbent`. While the smallest `LB3` equals the incumbent, the tie sweep evaluates the point, so no tied point is left out. QED.

## DX3-T3 Distinctness is certified mechanically

**Assumptions.** Two searchers are materially distinct when all three hold: (i) their declared difference tables differ on at least 2 of the 6 frozen axes; (ii) their canonical traces differ on at least one registered probe; (iii) they are not a re-encoding pair, meaning identical traces and identical acceptance sequences on every probe.
**Dependencies.** `robustness_record_v1._pair_distinctness`. Route B reproduces every trace and acceptance digest independently.
**Falsifiers.** The H3b masquerade accepted as distinct, or a registered pair rejected (`d_x3_search.registered_triple`, `h3b_reencoding_masquerade`).
**Strongest parents.** #863 R3 strategy-signature rule, hardened here against the one-algorithm-two-encodings failure the freeze records.

*Statement.* S1, S2 and S3 are pairwise materially distinct. S1-S2 and S1-S3 traces differ at 60/60 probes. S2-S3 traces differ at 40/60 probes; they are identical at the 20 high endpoints, where both evaluate exactly the three stateless points. H3b is S2 run over relabelled point ids, and it declares two differing axes. Its traces and acceptance sequences equal those of S2 at 60/60 probes, so it is rejected as `SEARCHERS_NOT_MATERIALLY_DISTINCT`. A relabelling that feeds the same procedure cannot change a trace defined on `rho`, so criterion (iii) catches every such masquerade whatever it declares.

*Proof.* Criterion (iii) is invariant under any bijective relabelling of ids, because the trace is taken after projection to `rho`. QED.

## DX3-T4 An early stop is surfaced, never averaged

**Assumptions.** H3a: S2's order, the first evaluated point accepted, no certificate. Same objective and budget frame.
**Dependencies.** DX3-T1. `robustness_record_v1.evaluate_search`.
**Falsifiers.** H3a agrees with S1 at every world, or the gate reports anything but `SEARCH_SENSITIVE` (`d_x3_search.h3a_early_stop`).
**Strongest parents.** #863 budget-one forward/reverse hostile. #855 `SEARCH_PRIOR_SENSITIVE`.

*Statement.* H3a returns `(0,0,8)` (STATELESS) at every world. It misses the true optimum at the 20 low endpoints and the 20 boundaries. The gate lists every disagreeing world, and the terminal is `SEARCH_SENSITIVE`; no agreement rate is computed.

*Proof.* In S2's order the first key is `(0, 8, ...)` at `(0,0,8)`. At a low endpoint `J(0,0,1) = lambda < eta*p/2 = J(0,0,8)`. QED.

## DX4-T1 Strictly positive scalarizations never choose a dominated point

**Assumptions.** Weights `w > 0` componentwise, and raw vectors with exact rational coordinates.
**Dependencies.** `robustness_record_v1.pareto_ids` and `argmin_ids`.
**Falsifiers.** A positive-scalarization winner outside the Pareto set (`d_x4_scalarization.positive_winners_all_on_frontier`).
**Strongest parents.** Geoffrion 1968 (J. Math. Anal. Appl. 22:618-630). Miettinen 1999, *Nonlinear Multiobjective Optimization*. #837 scalarization/Pareto theorem.

*Statement.* The exact Pareto set of the 146 points is `{(0,8,0) x4, (0,0,1) x62}`. All winners of the 30 registered positive scalarizations lie on it. The 4 boundary probes with `p = 1` have a zero weight on `en`. There the argmin contains 14 dominated points each: every `(en, 8, 0)` and `(en, 0, 1)` ties. This is why the validator counts only strictly positive weight vectors.

*Proof.* If `y` dominates `x`, then `w.y < w.x` for every `w > 0`. QED.

## DX4-T2 The frontier pair reverses exactly at the phase boundary

**Assumptions.** The two frontier points are incomparable, with `(ed, s) = (8, 0)` against `(0, 1)`: the `(4,1)`/`(1,4)` pattern on real census points.
**Dependencies.** DX4-T1. The #901 law.
**Falsifiers.** A registered positive scalarization whose winner contradicts the price-conditional law. Universal-winner wording accepted. A frontier invariant violated (`d_x4_scalarization`).
**Strongest parents.** #893 affine phase boundary `theta_ij`. The #863 R4 `(1,4)`/`(4,1)` hostile.

*Statement.* `J(0,0,1) - J(0,8,0) = lambda - eta*p/2`, so the winner reverses exactly at `lambda*`. It is `(0,0,1)` at all 15 registered low endpoints and `(0,8,0)` at all 15 high endpoints. Universal-winner wording is `SCALARIZATION_SENSITIVE`, both on the census and on the issue's literal fixture. Price-conditional wording is consistent at all 50 registered weight vectors. The frontier invariants hold on the entire frontier, and so for every positive-scalarization winner:

- `I1`: every frontier point with `ed < 8` has `s = 1`;
- `I2`: every frontier point has `en = 0`.

*Proof.* Both points have `en = 0`. Subtract. QED.

## DXP-T1 Derived perturbation bound for the winner-state partition

**Assumptions.** Endpoint world with margin `m = |lambda - eta*p/2| > 0`. Perturbations `delta` in `{-m/2, 0, +m/2}` of `(eta*(1-p), eta*p, lambda)`, keeping error weights nonnegative and the price positive. 1,008 perturbed worlds; 72 excluded because a zero weight would turn negative.
**Dependencies.** DX4-T1, DX4-T2, DXP-T2.
**Falsifiers.** A perturbed world whose state partition differs from the unperturbed one in any of the three encodings (E1, E1 with relabelled ids, E2). A boundary that fails to tie, or a mirrored price that fails to flip (`metric_perturbation_control`).
**Strongest parents.** Stability regions of weighted-sum argmin in parametric optimization (Miettinen 1999, weighting method).

*Statement.* The state partition is unchanged inside the bound at all 1,008 worlds, in all three encodings. Moving the price exactly to `lambda*` gives the tie at 40/40 endpoints. The mirrored price `2*lambda* - lambda` flips the partition at 40/40.

*Proof.* The frontier values differ by `(lambda - lambda*) + d_lambda - d_(eta*p)/2`, and `|d_lambda - d_(eta*p)/2| <= 3m/4 < m`. The `en` weight does not enter the frontier comparison, because both points have `en = 0`. With positive weights the argmin stays on the frontier (DX4-T1). With a zero `en` weight, every tied point has `ed = 8` and `s = 0`, or `ed = 0` and `s = 1`, so ties never mix states away from the boundary. Every epsilon is `m/2` of the world it perturbs; no constant is chosen by hand. QED.

## DXP-T2 The 146-class risk clustering is metric-free and preserved by re-encoding

**Assumptions.** The clustering is the `rho`-quotient of the census: 146 classes, with multiplicities. The re-encodings are the #901 id relabelling and the E2 bijection.
**Dependencies.** DX2-T1.
**Falsifiers.** Class tables that differ across the three encodings, or a class-level bijection failure (`metric_perturbation_control.risk_clustering_146_classes_identical_across_encodings`).
**Strongest parents.** #901 146-point risk histogram. The #999/#998 clustering-stability row owner.

*Statement.* `J_w` depends on a candidate only through `rho`, so every class lies in one level set of `J_w` for every `w`, and the partition does not depend on `w`. The three encodings give identical class tables, and each class of E1 maps onto the same class of the other two.

The metric-sensitive object at this scope is the winner-state partition (DXP-T1). The finer argmin cell is reported as a diagnostic. It is stable at all 864 perturbed worlds with strictly positive weights. It changes at the 72 zero-`en`-weight worlds once that weight becomes positive, because the dominated ties of DX4-T1 leave the argmin while the state partition stays the same.

*Proof.* Immediate from the definition of `J_w`, and from DX2-T1 for E2. QED.

## ADM-T1 Admission is sound and fails closed

**Assumptions.** A record of schema `GMI833DerivationRobustnessRecordV1`.
**Dependencies.** `robustness_record_v1.validate_record` and its five evaluators. The #855 terminal vocabulary.
**Falsifiers.** A record returning `ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE` while one of the five conditions fails. A census entry whose terminal or failure list differs from the registered expectation. A failing validator self-test (`admission`).
**Strongest parents.** #837 fail-closed claim discipline. #851 abstention semantics. The #863 missing-control census.

*Statement.* `validate_record` returns `ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE` if and only if all of the following hold:

1. the twin is matched, both of its arms are evaluable, and the outcome differs with the K target realized;
2. at least two syntactically disjoint encodings are equivalent on the full census and agree after projection with the claim;
3. a materially distinct complete pair of searchers, or a verified exhaustive construction, supports the claim, and no registered searcher disagrees;
4. at least two distinct strictly positive scalarizations are present, the Pareto set and the winners are recomputed and match, and the wording is not contradicted;
5. every compared arm is admissible.

A missing block gives `CANNOT_ESTABLISH_D_ROBUSTNESS_<CONTROL>` for the first missing control. Otherwise the first failing control is named, and the full ordered list of typed terminals is returned. A declared terminal that disagrees with the recomputation is itself a failure.

The census has 22 records, all exact. They are: the positive witness; five single-control deletions; H1a to H1d; H2a (twin valid, encoding census broken), H2b and H2c; H3a; H3b alone (search re-encodings only); H4a; an empty scalarization set; zero-weight probes only; an unclean negative arm; an unevaluable negative arm; twin plus search hostiles; and all four controls hostile at once.

*Proof.* By construction, the terminal is the conjunction of the five evaluators' pass terminals. Each evaluator recomputes its decision from the record's data. QED.

## ADM-T2 An exact finite positive witness exercises all four controls

**Assumptions.** The #901-family claim, with price-conditional wording and the frontier invariants `I1` and `I2`.
**Dependencies.** DX1-T1 to DX4-T2, ADM-T1.
**Falsifiers.** `DERIVATION_ROBUSTNESS_RECORD_POSITIVE_V1.json` fails validation when loaded from the file (a test does exactly this).
**Strongest parents.** #901 held-out law and its two-searcher replication.

*Statement.* The committed positive record reaches `ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE` with all five conditions true. It carries four blocks:

- the matched twin `G-`;
- the registered E1/E2 pair;
- the three searchers S1, S2 and S3;
- 30 positive scalarizations plus 20 boundary probes.

Its no-smuggling arms are `G_PLUS`, `G_MINUS`, `E_MINUS` and `G_PLUS_E2`. All are clean, except the routed cost scalarization reversal on the `G+` and E2 arms.

The same claim with universal-winner wording is refused (`SCALARIZATION_SENSITIVE`). This is the intended content: robustness at the registered D controls, with the price condition kept in the wording.

*Proof.* Validation of the committed file. QED.
