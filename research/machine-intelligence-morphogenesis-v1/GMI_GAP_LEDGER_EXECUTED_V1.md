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
| G5 | probabilistic and policy forms are precision-gated at 8 bits | two declared precision instruments with **identical charged operation sequences** now run side by side, so a capability difference is attributable to precision alone | `RV-377-045` (GMI-DA5) |
| G9 | attention needs a normalization primitive | executed: the attention row's closed form held at four points and it is dominated everywhere by hard retrieval | `RV-377-034` |
| G2 | single seed on every frontier prediction | second seed executed; deterministic rows are seed-invariant by construction and the frontier is unchanged; re-opened as G2b below | `RV-377-039` |

## 2. Open, blocking

| id | gap | why it blocks | concrete closure experiment |
|---|---|---|---|
| **DG-4** | **L8-ADMISSIBILITY.** The occupancy half of the domain selection law is `PROVED_AT_SCOPE` (1 980/1 980 cells given the true admissible set), but predicting *which* carriers are admissible in an unseen ecology is unsolved. | Every domain-level prediction of an unseen niche runs through it; it is the whole error term of `RV-377-060` (0.3932 against 0.99). | A closed form per carrier on the symmetric family. Executed so far: `cap_S5h = (48 − |k|)/48` for \|k\| ≤ 12 (breaks at 13), `cap_S5 = 1 − |k|/12`. Needed: an **initialization-relative** form for the coefficient carrier (its admissibility is not sign-symmetric: 0.9167 at k = 2 against 0.8490 at k = −2) and a **grammar-distance** form for the search carrier (admissibility falls to 0.8333 at \|k\| ≥ 12, where no registered carrier is admissible at all). |
| **G6** | the coefficient carrier was not recovered by neutral search | the biosphere protocol makes known-form recovery a gate on every unknown-form claim | Superseded in part: over the **typed IR alphabet** neutral search recovers retrieval memory, indexed memory and symbolic search to admissibility in 6 000 evaluations, and one seed recovers the coefficient carrier as well (`RV-377-058`, running). In the **expression-tree** grammar the quality-diversity revival reaches 0.8689 against a sound baseline of 0.7346 (`RV-377-057`, running). Closure = both records adjudicated with their ablations. |

## 3. Open, non-blocking

| id | gap | concrete closure experiment |
|---|---|---|
| **DG-1** | D6 (dynamical-state / controller) has no IR kind of its own; recurrent state is expressed only through `DENSE` plus an update law | add a `RECUR` state kind with an explicit iterated-map execution kind, re-run the B1 recovery harness, and check whether the carrier descriptor separates it from `DENSE` |
| **DG-2** | a "no cell exists" clause checked only on a truncated reuse grid | every frontier grid must extend to the analytic crossover of every price vector reported; found when `RV-377-045` clause 7 held to H = 1 024 while the crossover it denied lay at H = 1 856 |
| **DG-3** | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **DG-5** | bounded reduction is only meaningful against a **parent-maximal** opponent | exposed by N11, where the separation against a naive search parent is exponential and collapses to a constant against a dense-coefficient parent computing the same annihilator. Closure = a declared parent-maximality procedure (literature sweep plus an adversarial parent-construction step) run before every reduction verdict |
| **G2b** | admissibility of a **stochastic** carrier is a distribution over seeds | executed at two points (5 % of seeds admissible; on an admissible seed it occupies 14/56 to 56/56 cells): closure = a declared reliability index `q` on every frontier table, and a census for every stochastic row added later |
| **G14** | the cost model does not charge the **failed draws** of a stochastic carrier as search cost | `lifecycle_vector` in `gmi_microscope/vm.py` already carries `B_search` and `B_failed_candidates`; closure = apply them to the D′/E′ frontier and re-adjudicate `RV-377-041b` with failed draws charged |
| **G8** | the new-form criterion needs lower bounds, not only occupancy | exhaustive size census gives exact bounds only to size 4; closure = formal obstruction proofs for a property vector against parent products |
| **G10** | "predict a new form" | nine candidates executed, all reduced; closure = a candidate whose carrier is **not** a bounded composition of the primitive alphabet, which by GMI-DA1 means enlarging the alphabet |
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
