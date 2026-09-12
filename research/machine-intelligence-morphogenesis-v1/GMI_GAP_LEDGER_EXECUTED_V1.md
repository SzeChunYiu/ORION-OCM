# GMI executed-lane gap ledger — every open dependency with its closure experiment (V1)

Status: **LIVE REGISTER.** The hardening fixed point (`GMI_RECURSIVE_THEORY_HARDENING_FIXED_POINT_V1.md`) requires every
recursively reachable claim dependency to be proved, executed at a declared tier, reduced to a parent, falsified and
replaced, or **explicitly open with a concrete closure experiment**. This file is the last category for this lane, plus
the gaps this lane has closed, so that the closure status is auditable rather than asserted. Issue #422.

Claim levels: `PROVED_AT_SCOPE`, `PARENT_THEOREM_UNDER_ASSUMPTIONS`, `EMPIRICALLY_SUPPORTED_AT_TIER_X`,
`REGISTERED_FOR_EXPERIMENT`, `REDUCED_TO_PARENT`, `FALSIFIED_AND_REPLACED`, `OPEN_BLOCKING`, `OPEN_NONBLOCKING`,
`OUT_OF_SCOPE`.

---

## 1. Closed in this lane

| id | gap | how it closed | record |
|---|---|---|---|
| G1 | the price vector was frozen and charged, not a hardware one | a declared tensor-priced column executed on three ecologies; the occupant flips to the coefficient carrier on every cell where it is admissible (168/168) and none where it is not (0/56) | `RV-377-035` |
| G3 | search-row description is data-dependent | certified per ecology, and the description corner is now **abstained** rather than predicted — the ecology-dependence was measured at 154–334 bits | `RV-377-025`, `RV-377-059` |
| G4 | no retention/exposure term in the cost model | lifecycle extended with wrong-answers-served, abstentions and collateral regression, priced by λ; executed in four records | `RV-377-032`, `036`, `037`, `038` |
| G5 | probabilistic and policy forms are precision-gated at 8 bits | two declared precision instruments with **identical charged operation sequences** now run side by side, so a capability difference is attributable to precision alone; its **consequence is now executed** — `RV-377-066` raises GMI-DA5 from admissibility to **occupancy** and opens DG-6 | `RV-377-045` (GMI-DA5), `RV-377-066` |
| G9 | attention needs a normalization primitive | executed: the attention row's closed form held at four points and it is dominated everywhere by hard retrieval | `RV-377-034` |
| G2 | single seed on every frontier prediction | second seed executed; deterministic rows are seed-invariant by construction and the frontier is unchanged; re-opened as G2b below | `RV-377-039` |
| **DG-1** | D6 (dynamical / controller) had no IR kind of its own | closed the other way: the A axis of `GMI-DA7` was executed and the primitive adds **no class**. A one-entry store used as a register (`INSERT(tab, key, g(LOOKUP(tab, key), f(INPUT)))`) emulates the iterated map bit for bit on **108 of 108 cells** at a **constant 4-bit** description overhead, taking 0 of 9 828 frontier cells. D6 is the read-modify-write phase of D2 | `RV-377-072` (GMI-DA8) |
| **G6b** | admissibility was recovered by neutral search; the FORM was not | closed by charged morphogenetic atrophy: **all 24** recovered winners lose **every** store-write rule and reduce to a **two-rule error-driven coefficient learner** (`c0 ← ADD(out, MUL(kh, e))` plus a target-tracking rule), median 65 nodes against the planted learner's 47, minimum per-machine rule-ablation delta 0.4668. The memory classification was an artefact of 55–68 % introns | `RV-377-071` |
| **G6** | the coefficient carrier was not recovered by neutral search | closed at the ADMISSIBILITY level: both quality-diversity seeds cross θ at 10⁶ evaluations (0.8809, 0.8796) against a plateau of 0.7346–0.7798, and B1 over the typed IR recovers four carrier classes. Restated at the FORM level as G6b below | `RV-377-057`, `RV-377-058` |

## 2. Open, blocking

| id | gap | why it blocks | concrete closure experiment |
|---|---|---|---|
| **DG-4** *(now partially closed — see §2b)* | **L8-ADMISSIBILITY.** The occupancy half of the domain selection law is `PROVED_AT_SCOPE` (1 980/1 980 cells given the true admissible set), but predicting *which* carriers are admissible in an unseen ecology is unsolved. | Every domain-level prediction of an unseen niche runs through it; it is the whole error term of `RV-377-060` (0.3932 against 0.99). | A closed form per carrier on the symmetric family. Executed so far: `cap_S5h = (48 − |k|)/48` for \|k\| ≤ 12 (breaks at 13), `cap_S5 = 1 − |k|/12`. Needed: an **initialization-relative** form for the coefficient carrier (its admissibility is not sign-symmetric: 0.9167 at k = 2 against 0.8490 at k = −2) and a **grammar-distance** form for the search carrier (admissibility falls to 0.8333 at \|k\| ≥ 12, where no registered carrier is admissible at all). |

### 2b. DG-4 after `RV-377-062`: closed for retrieval carriers, restated for optimization carriers

Adjudicating seventeen executed symmetric ecologies against candidate closed forms splits the four registered carriers
two and two:

| carrier | closed form | exact on | fails at |
|---|---|---|---|
| exemplar memory | `cap = 1 − |k|/12` | 17 of 17 | — |
| generalizing memory | `cap = (48 − |k|)/48` | 16 of 16 with \|k\| ≤ 12 | k = 13 (0.7083 against 0.7292) |
| program search | `cap = f(distance to the nearest grammar coefficient)`: 1.0 / 0.9375 / 0.9167 at distance 0 / 1 / 2 | 12 of 12 with \|k\| ≤ 8 | \|k\| > 8, as target values approach the fixed-point range |
| coefficient / gradient | **none** | — | polynomial fits err 0.064 / 0.037 / 0.034 (degrees 1/2/3) on held-out k = 4, 7, 11; and it is initialization-asymmetric by 0.07–0.15 between +k and −k |

So the gap is not a missing formula. Capability is **combinatorial** for retrieval-type carriers — a counting argument over
what the ecology exposes — and **dynamical** for optimization-type carriers, where it is the endpoint of a trajectory from
a fixed initialization. A domain-level prediction of an unseen niche is exactly as a-priori as its weakest carrier's
admissibility model; for any niche containing an optimization carrier it is not a-priori at all, and admissibility must be
obtained by replay. The residual is therefore reclassified `OPEN_NONBLOCKING`, and its closure experiment becomes a bound
on how far replay can be truncated, not a search for a formula.

## 3. Open, non-blocking

| id | gap | concrete closure experiment |
|---|---|---|
| **DG-2** | a "no cell exists" clause checked only on a truncated reuse grid | every frontier grid must extend to the analytic crossover of every price vector reported; found when `RV-377-045` clause 7 held to H = 1 024 while the crossover it denied lay at H = 1 856 |
| **DG-3** | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **DG-6** | the domain-novelty criterion is stated without an **arithmetic instrument** | opened by `RV-377-066`: on the ambiguous-evidence ecology `E_ambig` NO carrier of any registered kind is admissible in the registered 8-bit universe (all ten rows exactly 0.0) although an 8-bit-representable answer would score 0.910880, and above 10 total bits (5 fractional) every frontier cell is held by a probabilistic carrier. Criterion 3 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 must therefore read "no bounded semantics-preserving reduction to existing domains over the registered family **at a declared precision**", as it already must name a depth bound (DG-3) and a parent-maximal opponent (DG-5). Closure = re-adjudicate the eleven executed candidates under the wide instrument |
| **DG-5** | bounded reduction is only meaningful against a **parent-maximal** opponent | exposed by N11, where the separation against a naive search parent is exponential and collapses to a constant against a dense-coefficient parent computing the same annihilator. Closure = a declared parent-maximality procedure (literature sweep plus an adversarial parent-construction step) run before every reduction verdict |
| **G2b** | admissibility of a **stochastic** carrier is a distribution over seeds | executed at two points (5 % of seeds admissible; on an admissible seed it occupies 14/56 to 56/56 cells): closure = a declared reliability index `q` on every frontier table, and a census for every stochastic row added later |
| **G14** | the cost model does not charge the **failed draws** of a stochastic carrier as search cost | `lifecycle_vector` in `gmi_microscope/vm.py` already carries `B_search` and `B_failed_candidates`; closure = apply them to the D′/E′ frontier and re-adjudicate `RV-377-041b` with failed draws charged |
| **G8** | the new-form criterion needs lower bounds, not only occupancy | exhaustive size census gives exact bounds only to size 4; closure = formal obstruction proofs for a property vector against parent products |
| **G10** | "predict a new form" | eleven candidates executed, all reduced, and stage B4's first open-world pre-test returns **0 of 7** unknown forms (every recovered machine bit-identical to a known parent, one node-for-node identical). Closure = an admissible **atrophied** elite whose final served response matches no admissible parent's, then bounded reduction and recurrence |
| **G12** | reachability of the search and algebraic forms by neutral search | **closed at scope by `RV-377-058`**: the symbolic program/search carrier is recovered to admissibility (0.8958) from primitives |

## 4. Open, outside this lane

| id | gap | owner |
|---|---|---|
| G7 | no real-system validation of any law | Codex E3/E4 (real code, Lean, lifelong machine) |
| G11 | developmental capital (does experience lower the next acquisition's burden) | Codex SPG protocols |
| B7 | protected real-regime transfer (code, mathematics, changing facts, multimodal control) | requires LLM-scale compute; `REGISTERED_FOR_EXPERIMENT` |

## 5. Protocol rules this lane has had to add (each from a failure)

| rule | statement | from |
|---|---|---|
| 11–15 | check each row against its closed form in one column before freezing; per-column threshold before freezing; state clause units; check clauses against the disclosed calibration and against each other | `RV-377-021`, `025`, `026`, `029`, `031` |
| 16 | a stochastic row is admissible at a **declared seed reliability** q; undeclared tables are q = 0.5 tables | `RV-377-040` |
| 17 | state the **frontier rule** a clause is evaluated under (largest ladder size vs best admissible size) | `RV-377-041` |
| 18 | any cache or surrogate that assigns a fitness a candidate did not itself earn must be **audited for soundness on the registered grammar before the run**, and the audit receipt cited in the run receipt | `RV-377-061` (34.65 % of candidates mis-scored) |
| 19 | a reduction verdict is only valid against a **parent-maximal** opponent | N11, `DG-5` |
| 20 | a **recovery** claim must name which known form was recovered and exhibit the structural match, not only a capability at or above θ — an admissibility gate is passable by bulk | `RV-377-057` (winners 3–4× the planted learner's size at a lower score) |
| 21 | *(narrowed by its own test)* no admissible row may serve **state written during development** without a charged operation — a store lookup or a state read carrying developed information must be charged. The original wording ("no admissible row has zero execution cost per query") is `FALSIFIED_AND_REPLACED`: a machine serving a **constant** legitimately costs nothing to run | `RV-377-072` (an unmetered serve took 175 frontier cells at 802 against 12 296); narrowed by `RV-377-073` |
| 26 | the reference catalogue a novelty claim is measured against must be **atrophied by the same charged instrument** as the candidate | `RV-377-077` (hand-built parents carry 0 introns, evolved machines a median 0.53) |
| 25 | an unknown-form claim is decided on the **developmental response** under the registered interventions, never on a structural signature, mechanism vector or carrier descriptor; structural signatures may shortlist candidates, never certify one | `RV-377-077` (5 of 7 novel structurally, 0 of 7 by response, same genotypes, same receipt) |
| 24 | a **gate** claim (precision, capacity, reliability, depth) must enumerate the **representations of the carrier's state** the alphabet admits and test the strongest at the gated setting; rule 19's parent-maximality covers the opponent's *state encoding*, not only its carrier family | `RV-377-075` (an 8-bit log-domain posterior scored 0.874265 where ten linear rows scored exactly 0.0) |
| 23 | a carrier descriptor is computed on the **atrophied** genotype, never on the raw one, in every archive, recovery receipt and B-stage gate — a descriptor read off a raw graph measures the search's introns, not the machine's carrier | `RV-377-074` (2 of 7 recovered carriers mis-credited; median intron fraction 0.53) |
| 22 | an obligation is history-dependent only where the best **constant** answer is below θ; every temporal ecology carries a hindsight-optimal constant-answer control row and clauses are evaluated only where that control fails. A mode whose control is admissible at every length is **VOID**, not weak | `RV-377-072`; confirmed by `RV-377-073` (the running-maximum control scored exactly 1.0 at all five lengths, voiding 30 of 90 cells) |
