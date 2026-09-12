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
| **G14** | the cost model did not charge the **failed draws** of a stochastic carrier | `B_search` and `B_failed_candidates` applied to the D′/E′ frontier at a declared reliability q, taken from `vm.lifecycle_vector` on the live ledger of each re-executed cell. The stochastic carrier occupies **0 of 336** registered cells at q = 1/32 and at the pooled q, against 14/56 to 56/56 before; `RV-377-041b` is re-adjudicated clause by clause and **2 of its 5 clauses survive** — exactly the two that are not cost claims. Break-even reliability q\* = 0.4992–0.8426 by column against a measured 1 of 32 | `RV-377-067` |
| **G8** | the new-form criterion needed lower bounds, not only occupancy | exhaustive census over a declared nineteen-kind alphabet pushed from size 4 to **size 7 exactly** (195 s). Three counts per size, and they are three different things: **336 242 configurations, 84 767 canonical forms, 127 response classes** at size 7. Four **exact lower bounds** with committed witnesses: none of size ≤ 3 realizes a semantic distinction, none of size ≤ 5 learns, none of size ≤ 7 generalizes exactly, none of size ≤ 7 is admissible (ceiling 0.7917 against θ = 0.85). The ceiling is invariant over 8/16/32 development events — a size-and-alphabet bound, not a development-length one — and moving one frozen alphabet parameter (`NEAREST` k: 1 → 3) lifts the same six-node structure to 0.8542 and admissibility, which is GMI-DA1 made executable | `RV-377-069` |
| **DG-2** | "no cell exists" clauses checked on truncated grids | enforcement instrument written (`gmi_microscope/grid_audit.py`) and run over the whole corpus: of 73 committed receipts with a frontier, **30 SAFE, 34 TRUNCATED (all MAJOR, none MINOR), 9 UNAUDITABLE**. The registered instance is reproduced independently at exactly H\* = 1 856; the worst case is H\* = 4 106 532, **32 082×** its grid maximum. The defect is confined to receipts written before the rule was registered | `RV-377-068` |

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

## 2c. G15 — no registered minimum discoverability, so no saturation claim

| id | gap | why it blocks | concrete closure experiment |
|---|---|---|---|
| **G15** *(step (i) REACHED — `RV-377-082`)* | **no registered `p_min`.** DSAT-1/2/3 (parallel lane) bound the chance of a missed domain only if every material domain has a minimum discoverability `p_min > 0`; DSAT-2 is explicit that consecutive no-new-domain runs justify no stopping rule without it | it blocks every statement of the form "the domain list is complete". The executed data gives no positive lower bound: read on **atrophied** carriers the coefficient carrier D1 is recovered in **0 of 6** B1 runs, and zero successes give no lower bound at all | **steps (i) and (ii) are done and the answer is negative.** A witness exists on `E_smooth1` (registered gradient row at h = 6, lr = 2, capability 0.8906, surviving atrophy as `DENSE` at 0.9062), and three recovery runs there recover it **0 of 3 times** on the atrophied reading (`RV-377-083`, 5 of 6 clauses, the decisive one failed). So the zero is **not only** an ecology result. The executed per-encoding rates are `p(D1 | expression tree)` ≈ 1 (24 of 24 winners) against `p(D1 | typed IR)` = 0 of 3 — **the encoding decides reachability, not the ecology**, which is DSAT-3's cross-encoding term measured rather than assumed. Still no positive lower bound over the IR, now for a substantive reason. Next: whether the IR recovers it at 10⁶ evaluations with an archive, as the expression tree needed. Then estimate `p_min` per encoding; estimate `p_min` from that rate (the first two rates are now measured: `p(D2) = 1.0`, `p(D4/D5) = 1/3`. **`p(D1) = 0/6` is NOT a rate** — `RV-377-081` shows the coefficient carrier has no known admissible witness on either of those ecologies, so all six trials are zero-exposure for it; on the encoding where a witness does exist it is recovered); then `n ≥ ln(⌊1/p_min⌋/δ)/p_min` independent **cross-encoding** units (9 executed so far; 29 needed at `p_min = 1/6`, 53 at 0.10, 120 at 0.05) |

## 3. Open, non-blocking

| id | gap | concrete closure experiment |
|---|---|---|
| **DG-2** *(closed for the receipts that adopt the procedure — see §3b)* | a "no cell exists" clause checked only on a truncated reuse grid | every frontier grid must extend to the analytic crossover of every price vector reported; found when `RV-377-045` clause 7 held to H = 1 024 while the crossover it denied lay at H = 1 856 |
| **DG-3** *(**CLOSED** by `RV-377-065` — see §3b)* | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **DG-6** | the domain-novelty criterion is stated without an **arithmetic instrument** | opened by `RV-377-066`: on the ambiguous-evidence ecology `E_ambig` NO carrier of any registered kind is admissible in the registered 8-bit universe (all ten rows exactly 0.0) although an 8-bit-representable answer would score 0.910880, and above 10 total bits (5 fractional) every frontier cell is held by a probabilistic carrier. Criterion 3 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 must therefore read "no bounded semantics-preserving reduction to existing domains over the registered family **at a declared precision**", as it already must name a depth bound (DG-3) and a parent-maximal opponent (DG-5). Closure = re-adjudicate the eleven executed candidates under the wide instrument |
| **DG-2** *(sharpened by `RV-377-076` — see §3a)* | a "no cell exists" clause checked only on a truncated reuse grid | every frontier grid must extend to the analytic crossover of every price vector reported; found when `RV-377-045` clause 7 held to H = 1 024 while the crossover it denied lay at H = 1 856 |
| **DG-3** | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **DG-6** *(premise corrected by `RV-377-075`/`RV-377-076`)* | the domain-novelty criterion is stated without an **arithmetic instrument** | opened by `RV-377-066`: on the ambiguous-evidence ecology `E_ambig` NO carrier of any registered kind is admissible in the registered 8-bit universe (all ten rows exactly 0.0) although an 8-bit-representable answer would score 0.910880, and above 10 total bits (5 fractional) every frontier cell is held by a probabilistic carrier. Criterion 3 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 must therefore read "no bounded semantics-preserving reduction to existing domains over the registered family **at a declared precision**", as it already must name a depth bound (DG-3) and a parent-maximal opponent (DG-5). Closure = re-adjudicate the eleven executed candidates under the wide instrument |
| **DG-5** | bounded reduction is only meaningful against a **parent-maximal** opponent | exposed by N11, where the separation against a naive search parent is exponential and collapses to a constant against a dense-coefficient parent computing the same annihilator. Closure = a declared parent-maximality procedure (literature sweep plus an adversarial parent-construction step) run before every reduction verdict |
| **G2b** | admissibility of a **stochastic** carrier is a distribution over seeds | executed at two points (**9 of 192 seeds admissible, 0.046875** — the '5 %' carried here was an off-by-one, corrected by `RV-377-067`; on an admissible seed it occupies 14/56 to 56/56 cells): closure = a declared reliability index `q` on every frontier table, and a census for every stochastic row added later |
| **G14** | the cost model does not charge the **failed draws** of a stochastic carrier as search cost | `lifecycle_vector` in `gmi_microscope/vm.py` already carries `B_search` and `B_failed_candidates`; closure = apply them to the D′/E′ frontier and re-adjudicate `RV-377-041b` with failed draws charged |
| **G8** | the new-form criterion needs lower bounds, not only occupancy | exhaustive size census gives exact bounds only to size 4; closure = formal obstruction proofs for a property vector against parent products |
| **G10** | "predict a new form" | eleven candidates executed, all reduced, and stage B4's first open-world pre-test returns **0 of 7** unknown forms (every recovered machine bit-identical to a known parent, one node-for-node identical). Closure = an admissible **atrophied** elite whose final served response matches no admissible parent's, then bounded reduction and recurrence |
| **DG-1** | D6 (dynamical-state / controller) has no IR kind of its own; recurrent state is expressed only through `DENSE` plus an update law | add a `RECUR` state kind with an explicit iterated-map execution kind, re-run the B1 recovery harness, and check whether the carrier descriptor separates it from `DENSE` |
| **DG-3** | novelty criterion 3 is stated without a structure-depth bound | the crossover `H*(d) ~ R^d/d` is unbounded in depth (`RV-377-044`), so the criterion must name the family's depth bound; closure = amend `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14 and re-adjudicate DC1 under the amended text |
| **G12** | reachability of the search and algebraic forms by neutral search | **closed at scope by `RV-377-058`**: the symbolic program/search carrier is recovered to admissibility (0.8958) from primitives |

### 3b. DG-2 and DG-3 after `RV-377-065` (the depth-gated kingdom decision)

`RV-377-065` (`GMI_DEPTH_GATED_KINGDOM_V1.md`, receipt `microscopes/results/STAGE_DK_V1_DEPTH_GATED.json`) executed the
depth-indexed role-filler family at structure depths 1–6 against four adversarially constructed exemplar-store opponents.

**DG-2 — closed by construction for every receipt that adopts the procedure.** `gmi_microscope/dk_depth.py` computes
every admissible pair's crossover *first*, in exact rational arithmetic, then builds the reuse grid to bracket each one
and reach `4×` the largest, and asserts `max(grid) ≥ 2·max(crossover)` per cell. That assertion held in **96 of 96**
frontier decisions and is reported per cell as `dg2_grid_covers_twice_every_crossover`. The gap stays listed because the
earlier receipts were not re-run under it; the procedure, not the inspection, is the closure.

**DG-3 — closed.** §14 criterion 3 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` is amended (§14.1) to require three
declared quantities rather than one: the family's structure-depth bound, the **composition operator** whose image fixes
how the parent's store grows with depth, and the reuse-horizon bound. The middle one was not anticipated by the gap as
written and is the executed content of the record: the XOR bind of `RV-377-044` has a path-code image of measured size
`4, 7, 8, 8, 8, 8` at depths 1–6 — it saturates at `2^R`, so one bounded reduction with overhead factor ≤ 5.3449 covers
the whole unbounded-depth family; the permutation-protected code has image exactly `R^d` and the depth escape is real.
GMI-DA3 is therefore relativized to a named operator, and `RV-377-044`'s published depth-2 description ratio of 10.667 is
corrected to 4.6667 against the parent-maximal opponent. DC1 re-adjudicated under the amended text remains
`REDUCED_TO_PARENT(D2)`.

**DG-5 and G8 — reinforced, not closed.** The record is the third application of protocol rule 19 and the first in which
adversarial parent construction changed a published number. G8 is untouched and is now the single gap between this
negative verdict and a theorem: the result is an **occupancy** statement over four constructed opponents, not a lower
bound over all of them.

### 3a. DG-2 after `RV-377-076`: a "no cell" clause has **two** discharges and must say which

`RV-377-076` needed a "`LOGBAYES8@fx8` holds 0 of 42 / 49 / 294 / 899 cross-instrument cells" clause, and found
that DG-2's grid rule is only half of what such a clause needs.

* **Discharge by theorem.** The frozen cost `C = desc + H·exec_q + r·(upd_e + ver_e) + (r/4)·rev_e` is affine in
  `(H, r)` with exactly **three** coefficients — `desc`, `exec_q` and `ρ = upd_e + ver_e + rev_e/4`. If one
  admissible row is no larger on all three and strictly smaller on one, it is cheaper at **every** `H ≥ 0`,
  `r ≥ 0`; no crossover exists and no grid is required. `QCOUNT@fx10` does this to `LOGBAYES8@fx8` in all eight
  keys: `(596, 12, 549)` against `(3 104, 208, 2 075.75)` under the reduced price, `(596, 4, 112)` against
  `(3 104, 96, 904)` under the native price.
* **Discharge by grid, per axis.** Where no dominator exists the grid must pass **twice the largest crossover in
  each axis separately** — `RV-377-076`'s `H` grid reaches 8 192 against a largest `H`-crossover of 75.0, and its
  `r` grid reaches 256 against a largest `r`-crossover of 23.25. Checking one combined maximum, as this lane did
  before, can pass an `H` grid while leaving the `r` axis short.

`RV-377-076`'s own clause 3 **FAILED** on exactly this point: it asserted domination for *every* pair, and
`BAYESM@fx10` has a positive `r`-crossover with the log row at 76/165 = 0.460606. The clause is recorded as failed,
and the rule below is what it earned. → **protocol rule 35**.

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
| 22 | an obligation is history-dependent only where the best **constant** answer is below θ; every temporal ecology carries a hindsight-optimal constant-answer control row and clauses are evaluated only where that control fails. A mode whose control is admissible at every length is **VOID**, not weak | `RV-377-072`; confirmed by `RV-377-073` (the running-maximum control scored exactly 1.0 at all five lengths, voiding 30 of 90 cells) |
| 23 | a carrier descriptor is computed on the **atrophied** genotype, never on the raw one, in every archive, recovery receipt and B-stage gate — a descriptor read off a raw graph measures the search's introns, not the machine's carrier | `RV-377-074` (2 of 7 recovered carriers mis-credited; median intron fraction 0.53) |
| 24 | a **gate** claim (precision, capacity, reliability, depth) must enumerate the **representations of the carrier's state** the alphabet admits and test the strongest at the gated setting; rule 19's parent-maximality covers the opponent's *state encoding*, not only its carrier family | `RV-377-075` (an 8-bit log-domain posterior scored 0.874265 where ten linear rows scored exactly 0.0) |
| 25 | an unknown-form claim is decided on the **developmental response** under the registered interventions, never on a structural signature, mechanism vector or carrier descriptor; structural signatures may shortlist candidates, never certify one | `RV-377-077` (5 of 7 novel structurally, 0 of 7 by response, same genotypes, same receipt) |
| 26 | the reference catalogue a novelty claim is measured against must be **atrophied by the same charged instrument** as the candidate | `RV-377-077` (hand-built parents carry 0 introns, evolved machines a median 0.53) |
| 27 | a **cost** claim for a stochastic carrier is void unless its **failed draws** are charged: lowering the declared reliability moves the carrier into the admissible set and out of the cheap set at the same time | `RV-377-067` (0 of 336 frontier cells once charged, against 14/56–56/56 uncharged) |
| 28 | a receipt that reports a frontier must carry the **per-row cost coordinates that produced it**, or its grid cannot be audited by anyone, including its author | `RV-377-068` (9 of 73 receipts unauditable from their own contents; one reports a 672-cell frontier with no cost coordinates at all) |
| 29 | a **census count** is meaningless outside the triple *(alphabet, servability filter, ecology)* and must carry all three in the same sentence as the number | two exhaustive size-5 censuses in this repository differ by a factor of **59** (12 987 against 220), both exact, both correctly scoped, and mutually unintelligible without their coordinates |
| 30 | parallel lanes must draw **revival-record ids AND protocol-rule numbers** from disjoint reserved ranges, and a lane that publishes first keeps the bare number | happened **twice**: three lanes used `RV-377-052` and two used `RV-377-054` (repaired by renumbering to 078–080 with a redirect note in each record); then the precision-residual lane independently issued rules 24–27 against this lane's 24–27 (repaired by renumbering the later lane to 33–35). A lane that branches before a rule exists cannot see it, so the range must be reserved at spawn time |
| 31 | a **recovery rate** counts only trials on ecologies where the domain has an **exhibited admissible witness**; trials where it does not are reported separately as zero-exposure and excluded from every saturation denominator | `RV-377-081` (the coefficient carrier's own reference scores 0.7604–0.8021 and 0.7188–0.7500 on the two ecologies where it was counted as "not recovered") |
| 32 | **atrophy is performed under the FULL registered intervention set**; a deletion is accepted only if capability stays at or above θ under *every* registered intervention. A pruning run under one intervention bounds the machine's size from above and its capability under the others from below, and must say so | `RV-377-082` (atrophy *raised* a witness from 0.8906 to 0.9062 by deleting the evidence buffer, whose only purpose is revocation replay, on a harness that never revokes). Every committed atrophy receipt inherits this caveat |
| 33 | a row that reads a **declared constant table** must charge every read at the **registered emulation cost of the basis it runs on**; a table is not a free indirection. In `B0` no store kind is native, so a table read is a **linear scan, one `EQ` per entry** | `RV-377-076` (`RV-377-075` charged one `SEL` per read of a 256-entry table — a 256× undercharge; `exec_q` 208 → 8 432 per query) |
| 34 | when **one** declared cell or event sequence fails while its siblings pass, the record must test whether a **single rounding decision in a declared constant** carries the difference — a one-entry intervention with all else held fixed — **before** attributing the failure to the ecology or the evidence | `RV-377-076` (declared sequence B's failure is one of 256 exponent-table entries: the unique half-integer tie at `log₂ w = −5`; flipping its tie-break moves B from 0.400545 to 0.874245 and leaves the other nine sequence-cells bit-identical) |
| 35 | a **"no cell exists"** clause must state **which** DG-2 discharge it uses — a **cost-coordinate domination**, which is a theorem over the whole non-negative quadrant, or a **grid extended past twice the largest crossover in each axis separately** — and must report the pairs only the second covers. Domination is tested in the coordinates the **cost function has**, not the coordinates the receipt prints | `RV-377-076` (its own clause 2 failed by testing five raw coefficients where the cost function has three; the true and stronger statement was one line away) |
