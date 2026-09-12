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
| **G14** | the cost model did not charge the **failed draws** of a stochastic carrier | `B_search` and `B_failed_candidates` applied to the D′/E′ frontier at a declared reliability q, taken from `vm.lifecycle_vector` on the live ledger of each re-executed cell. The stochastic carrier occupies **0 of 336** registered cells at q = 1/32 and at the pooled q, against 14/56 to 56/56 before; `RV-377-041b` is re-adjudicated clause by clause and **2 of its 5 clauses survive** — exactly the two that are not cost claims. Break-even reliability q\* = 0.4992–0.8426 by column against a measured 1 of 32 | `RV-377-067` |
| **G8** | the new-form criterion needed lower bounds, not only occupancy | exhaustive census over a declared nineteen-kind alphabet pushed from size 4 to **size 7 exactly** (195 s). Three counts per size, and they are three different things: **336 242 configurations, 84 767 canonical forms, 127 response classes** at size 7. Four **exact lower bounds** with committed witnesses: none of size ≤ 3 realizes a semantic distinction, none of size ≤ 5 learns, none of size ≤ 7 generalizes exactly, none of size ≤ 7 is admissible (ceiling 0.7917 against θ = 0.85). The ceiling is invariant over 8/16/32 development events — a size-and-alphabet bound, not a development-length one — and moving one frozen alphabet parameter (`NEAREST` k: 1 → 3) lifts the same six-node structure to 0.8542 and admissibility, which is GMI-DA1 made executable | `RV-377-069` |
| **DG-2** | "no cell exists" clauses checked on truncated grids | enforcement instrument written (`gmi_microscope/grid_audit.py`) and run over the whole corpus: of 73 committed receipts with a frontier, **30 SAFE, 34 TRUNCATED (all MAJOR, none MINOR), 9 UNAUDITABLE**. The registered instance is reproduced independently at exactly H\* = 1 856; the worst case is H\* = 4 106 532, **32 082×** its grid maximum. The defect is confined to receipts written before the rule was registered | `RV-377-068` |

## 2. Open, blocking

| id | gap | why it blocks | concrete closure experiment |
|---|---|---|---|
| **DG-4** *(now partially closed — see §2b)* | **L8-ADMISSIBILITY.** The occupancy half of the domain selection law is `PROVED_AT_SCOPE` (1 980/1 980 cells given the true admissible set), but predicting *which* carriers are admissible in an unseen ecology is unsolved. | Every domain-level prediction of an unseen niche runs through it; it is the whole error term of `RV-377-060` (0.3932 against 0.99). | A closed form per carrier on the symmetric family. Executed so far: `cap_S5h = (48 − |k|)/48` for \|k\| ≤ 12 (breaks at 13), `cap_S5 = 1 − |k|/12`. Needed: an **initialization-relative** form for the coefficient carrier (its admissibility is not sign-symmetric: 0.9167 at k = 2 against 0.8490 at k = −2) and a **grammar-distance** form for the search carrier (admissibility falls to 0.8333 at \|k\| ≥ 12, where no registered carrier is admissible at all). |
| **G6** | the coefficient carrier was not recovered by neutral search | the biosphere protocol makes known-form recovery a gate on every unknown-form claim | Superseded in part: over the **typed IR alphabet** neutral search recovers retrieval memory, indexed memory and symbolic search to admissibility in 6 000 evaluations, and one seed recovers the coefficient carrier as well (`RV-377-058`, running). In the **expression-tree** grammar the quality-diversity revival reaches 0.8689 against a sound baseline of 0.7346 (`RV-377-057`, running). Closure = both records adjudicated with their ablations. |

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
| **DG-1** | D6 (dynamical-state / controller) has no IR kind of its own; recurrent state is expressed only through `DENSE` plus an update law | add a `RECUR` state kind with an explicit iterated-map execution kind, re-run the B1 recovery harness, and check whether the carrier descriptor separates it from `DENSE` |
| **DG-3** | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **DG-5** | bounded reduction is only meaningful against a **parent-maximal** opponent | exposed by N11, where the separation against a naive search parent is exponential and collapses to a constant against a dense-coefficient parent computing the same annihilator. Closure = a declared parent-maximality procedure (literature sweep plus an adversarial parent-construction step) run before every reduction verdict |
| **G2b** | admissibility of a **stochastic** carrier is a distribution over seeds | executed at two points: **9 of 192 runs admissible (4.6875 %, 1/q = 21.33 draws)** — `RV-377-067` recounted the committed census and found the published "10 of 192, about 5 %" of `RV-377-040`, GMI-DA6 and this ledger to be off by one run. On an admissible seed the carrier took 14/56 to 56/56 cells under the uncharged model and takes **0 of 336** once its failed draws are charged (`RV-377-067`). Closure = a declared reliability index `q` on every frontier table **and the matching `B_search` charge at the same q** (rule 20), plus a census for every stochastic row added later |
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
| 20 | a frontier table containing a stochastic row must charge `B_search = (1/q − 1)·D_draw` at the **same** declared reliability q that admitted the row; a table that declares q for admissibility and charges q = 1 for cost is internally inconsistent | `RV-377-067` (G14) |
| 21 | a frontier receipt must report, per context, either the crossover of every admissible row pair or the fact that none lies beyond its grid; **no occupancy sentence may be written unconditionally** — "row R occupies no cell" must read "row R occupies no cell at H ≤ H_max", with H_max named | `RV-377-068` (DG-2) |
| 22 | a receipt that reports a frontier must carry the **per-row cost coordinates that frontier was computed from**, so the grid can be audited from the receipt alone; nine committed receipts fail this and `STAGE_E_FRONTIER_V1` (672 cells) carries none | `RV-377-068` (DG-2) |
| 23 | the three census counts are **three different objects** — configurations, isomorphism classes, response classes — and **none of them may be called a species count**: a species-level claim needs a developmental-equivalence and a reproduction criterion that a static enumeration does not supply | `RV-377-069` (G8) |
| 24 | an obstruction result must name the alphabet **and its frozen parameter values**, and must report a parameter sweep off those values: a non-existence result over a frozen alphabet can be an artefact of one parameter — in `RV-377-069` it is | `RV-377-069` (G8) |
