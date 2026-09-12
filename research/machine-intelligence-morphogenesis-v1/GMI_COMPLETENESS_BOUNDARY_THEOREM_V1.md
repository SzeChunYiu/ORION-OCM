# The GMI Completeness / Boundary Theorem, V1

**CP7.** One statement of exactly what has been proved, over exactly which universe — and,
with equal weight, what has not.

Status date: 2026-09-12. Written from the executed record, not from the programme's
intentions. Every clause below is traceable to a receipt in
`research/machine-intelligence-morphogenesis-v1/microscopes/results/`.

---

## 0. The form of the answer

The critical path asked to "complete the general machine intelligence theory". The executed
record does not permit a completeness theorem in the sense of *the theory is finished*. It
permits — and this document delivers — a **boundary theorem**: a precise statement of the
frontier between what GMI has established and what it has not, with the universe of
quantification named exactly.

That is not a lesser deliverable. A theory whose boundary is unknown cannot be used; a
theory whose boundary is exact can be. What follows is the boundary.

---

## 1. The universe of quantification

Every positive claim below holds over **this** universe and no larger one. The universe is
not a formality; it is the load-bearing part of the theorem.

| axis | extent |
|---|---|
| **alphabet `A`** | 36 typed primitive kinds (`morph.KINDS`); 33 non-structural |
| **grammar** | the R5 operator grammar over the typed morphology IR; 3 K4 grammars (`G1` tensor, `G2` register machine, `G3` FSM message) |
| **instrument `p`** | 8-bit fixed point, `FRAC_BITS = 4`, `FX_ONE = 16`, clamp `[-128, 127]`; one fx unit of mean absolute error = 1/(1.5·16) = **0.041667** capability |
| **depth `d`** | `{1}` — the only depth ever evaluated in the closure lattice |
| **ecologies `F`** | 6 registered (`E_parity`, `E_smooth1`, `E_smooth3`, `E_sym3`, `E_sym5`, `E_wit1`); of these **only 4** survive rule 40 |
| **interventions** | 6 registered; of these **only 5** are known to measure what they claim |
| **threshold** | θ = 0.85 |
| **development** | 16 events (registry) / 48 events (the `smooth_dense_max` lane) |
| **lattice coverage** | **541 / 120 960 = 0.4473 %** of `A × d × p × F` |

> **Boundary clause U.** No claim in this document extends beyond `d = 1`, beyond the 8-bit
> instrument, or beyond the four rule-40-discriminating ecologies. `RV-377-114` measured
> that mean capability falls from 0.7510 at `fx8` to 0.4368 at wide precision, so results do
> **not** carry up the `p` axis: raising precision requires re-searching, not re-reading.

---

## 2. What is PROVED

### T1 — Neutral recovery of the coefficient carrier (`G15` step ii)

> There exists a genotype, found by a search whose alphabet contains **no architecture
> macro**, whose served computation reads the `DENSE` carrier, which is admissible on a
> rule-40 discriminating ecology under **every** registered intervention, and which
> demonstrably learns.

Witness: `E_sym5 | DENSE`, capability 0.9115 standard, **minimum 0.8542 over all six
interventions**, best constant 0.7917, margin **1.500 fx units**. Fixed-function null passed
with the extractor validated on a known inert row (1 distinct) and a known learner (5
distinct) *before* the witness was read; witness reads 5/5 distinct. Obligation verified
non-degenerate.

Controls cleared: rule 36, rule 40, rule 42, rule 45. Record: `RV-377-113`, unchanged when
recomputed over the leak-free five-intervention set (`RV-377-114`).

**Seven carrier recoveries** clear every control (`E_sym5` × 4, `E_smooth3` × 3); **eight**
on the leak-free five.

*Scope:* one seed, one column, 20 000 evaluations, unswept. A **point claim**, not a rate.

### T2 — `GMI-DA9` predicts the intervention that breaks coefficient carriers

`GMI-DA9` names `half_events` and `shuffled_events` as the interventions that break
coefficient rows. Derived on different rows, ecologies and development lengths. In
`RV-377-111`, `half_events` is the binding intervention on **11 of 11** re-scored cells,
across `h ∈ [3,16]` and `lr ∈ [0.0625, 0.25]`. Corroborated on ground it was never fitted to.

### T3 — The registered core obligations are non-degenerate

All **12** registered smooth/table obligations (6 ecologies × 2 criteria) take more than one
value over their own evaluation sets (`RV-377-112`). The core ecology set is sound on the
degeneracy axis.

### T5 — The carrier is an observable property of any non-trivial machine

Restricted to the 116 behaviourally non-trivial genotypes of 600, **12 of 12** observable
signatures map to exactly one carrier. Two systems indistinguishable under all 6 registered
ecologies x all 6 registered interventions, and exhibiting more than one distinct answer,
always have the same carrier on this sample.

All three identifiability failures across the full 600 are among **behaviourally trivial**
machines, and all three involve `NONE` — the benign case: a machine emitting at most one
distinct answer exhibits nothing to infer from.

This **rescues the descriptor T1 depends on.** `G15` step (ii) is a claim about
`E_sym5 | DENSE` at capability 0.9115, squarely non-trivial. Had identifiability failed
there, T1 would have been a claim about a genotype's internals rather than about anything an
observer could measure. Record: `RV-377-116`. Two of that record's four predictions failed
**in GMI's favour**.

### T4 — Universal computation is a boundary, not a basis

Rung B0 is `EARNED_AS_BOUNDARY`: parent mathematics dominates at expressivity, so
expressivity alone cannot individuate a cognitive atom.

---

## 3. What is DISPROVED

These are not gaps. They are established negatives.

### F1 — The K4 property prediction fails, and fails **structurally**

**0 of 264** cells recover their frozen target vector. Re-run at **10× budget: 0 of 264
cells changed verdict** — counts identical at 159 / 69 / 36.

The budget was verified honoured (wall ratio 15.34×; search winner cost improved on 194 of
264 cells). Yet the null-vs-witness margin is unchanged on **all 264**, so the target witness
cost improved on **none**.

> **Ten times the search budget made the non-target frontier materially cheaper on 194 cells
> and moved the frozen-target witness on zero. The gap between what cost-minimising search
> converges on and what GMI predicts does not close with compute — it widens.**

`K4_PROPERTY_PREDICTION_GREEN_AT_REGISTERED_SCOPE = FALSE`, structurally.
(`RV-377-107`, `RV-377-109`.)

### F2 — Known-form results do **not** lift to domain-wide results

The candidate reduction is **unsound** (594/600; six counterexamples, five explained by
store-mediated dataflow the edge relation does not represent). The normal form is **wildly
incomplete**: 266 forms → 17 behaviours, worst 183:1, and the incompleteness **survives**
restriction to the 116 behaviourally non-trivial genotypes (41 → 12, worst 15:1).

The deeper obstruction is structural, not empirical: **observational equivalence on a
Turing-complete IR is undecidable, so no computable normal form can be complete over the
full IR.** CP2's goal as stated is not merely unachieved — it is **unachievable at that
scope**. Any domain-wide lift must be confined to a declared decidable fragment; the corpus
has never named one.

`KNOWN_FORM_RESULTS_LIFT_TO_DOMAIN_WIDE_RESULTS = FALSE`. (`RV-377-115`.)

### F3 — `p(D1)` is not estimable, so the domain list cannot be closed

`E_sym3` is `NON_DISCRIMINATING` on both criteria, and all six rows `RV-377-089b` offered as
witnesses are **strictly worse than emitting the constant 6**. `D1` exposure among the five
originally-registered ecologies falls from 1-of-5 to **0-of-5**, so every coefficient-carrier
recovery trial ever run was a zero-exposure trial.

`E_wit1` cannot repair the denominator: it was **selected** from 6561 enumerated targets *for
the property of bearing a witness*, so it conditions on the outcome.

`P_MIN_LOWER_BOUND_EXISTS = FALSE`; `DOMAIN_LIST_COMPLETE = BLOCKED`. (`RV-377-108`.)

### F4 — 38.1 % of the registry can certify nothing

Of 42 audited ecology × criterion pairs: **9 NON_DISCRIMINATING** (21.4 %), **7
WITHIN_QUANTIZATION** (16.7 %), 26 discriminating (61.9 %). (`RV-377-108`.)

### F5 — DG-7's overturn count is zero

`RV-377-088`, the record that *opened* DG-7 and supplied **both** its claimed overturns,
never swept the intervention index. Re-scored: **0 of 11 cells survive**. The two
`NOT_OBSERVABLE` terminals withdrawn on its strength are **restored verbatim**.
(`RV-377-111`.)

### F6 — Two registered instruments do not do what they are named

* `extra_unseen_feedback` trains on `UNSEEN[:4]` and scores on all 8 of `UNSEEN` — a **50 %
  leak** in one of the six bars rule 36 requires.
* `ecology.REGISTRY["E_parity"]`'s target is the **identity** `0..15`, not parity.

Neither repaired: repairing either re-points every historical reference at a different
object. (`RV-377-114` / DG-13.)

### F7 — The grammar axis is verdict-inert

All three K4 grammars agree on the verdict for **88 of 88** family × cell combos, at both
budgets, while producing different numbers on every combo where they are defined. The 3×
replication supplies **no independent evidence**; the effective K4 sample is **88, not 264**.
(DG-11.)

### F8 — Four fifths of the search space does nothing

**484 of 600 (80.7 %)** random genotypes from the R5 grammar are behaviourally trivial —
at most one distinct non-abstain answer. This bears on every claim about what a neutral
search "could have found". (`RV-377-115`.)

---

## 4. The claim ladder, as executed

| rung | claim | status |
|---|---|---|
| B0 | universal computation baseline | **EARNED_AS_BOUNDARY** |
| B1 | minimal / equivalent adaptive generating basis | **NOT_EARNED** |
| B2 | bounded derivation of multiple known morphologies | **NOT_EARNED** |
| B3 | unified specialization of multiple learning laws | **NOT_EARNED** |
| B4 | prospective morphology phase law | **NOT_EARNED** |
| B5 | blind recovery of predicted known morphologies | **BLOCKED** on B4 |
| B6 | cross-paradigm developmental morphogenesis | **BLOCKED** (GMI-T12) |
| B7 | novel morphology residual | **BLOCKED** |
| B8 | replicated architecture-independent generative principle | **BLOCKED** |

> **Boundary clause L.** Exactly one rung is earned, and it is earned *as a boundary* — a
> statement about what cannot individuate intelligence, not about what does.

---

## 5. The terminal register

| terminal | value |
|---|---|
| `G15_STEP_ONE_REACHED` | **TRUE**, at `E_wit1` only, 3.751 fx units |
| `G15_STEP_TWO_REACHED` | **TRUE** at registered scope (`E_sym5 | DENSE`) |
| `REGISTERED_SMOOTH_TABLE_OBLIGATIONS_NON_DEGENERATE` | **TRUE**, 12/12 |
| `K4_PROPERTY_PREDICTION_GREEN_AT_REGISTERED_SCOPE` | **FALSE**, structurally |
| `KNOWN_FORM_RESULTS_LIFT_TO_DOMAIN_WIDE_RESULTS` | **FALSE**, and unachievable over the full IR |
| `P_MIN_LOWER_BOUND_EXISTS` | **FALSE** |
| `DOMAIN_LIST_COMPLETE` | **BLOCKED** |
| `KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE` | **FALSE** |
| `NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE` | **FALSE** |
| `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` | **FALSE** |
| `ALL_REGISTERED_INTERVENTIONS_MEASURE_WHAT_THEY_CLAIM` | **FALSE** |
| `ALL_REGISTERED_ECOLOGIES_ARE_WHAT_THEY_ARE_NAMED` | **FALSE** |
| `CARRIER_IDENTIFIABLE_FROM_BEHAVIOUR_ON_NON_TRIVIAL_MACHINES` | **TRUE**, 12/12 |
| `FINE_STRUCTURE_IDENTIFIABLE_FROM_BEHAVIOUR` | **FALSE** |
| `CP5_REALIZATION_ADDRESSED` | **FALSE** — not started |
| `K4_SELECTION_PRINCIPLE_CAN_BE_PREDICTIVE` | **FALSE** — cross-seed agreement 0.0 % at 3 budgets |
| `TI_1_EXPERIMENTALLY_VERIFIED_ON_REAL_MACHINES` | **TRUE** at registered scope |
| `GMI_PREDICTS_CAPABILITY_OF_AN_UNSEEN_FORM` | **TRUE** — TI-1, verified and tight |
| `K4D_WORLDS_NON_DEGENERATE` | **FALSE** — 4 of 22 have M = 1 |

---

## 6. Open gaps, by kind

**Instrument defects (repair changes historical meaning):** DG-13 — the leaky intervention,
the misnamed ecology.

**Coverage:** DG-8 — 0.4473 % of the lattice; `d ∈ {1}`, `p ∈ {fx8}`; **zero** cells crossing
either axis off-diagonal. DG-12 — 12 obligation-bearing modules unaudited for degeneracy.

**Methodological:** DG-11 — no cell has ever been exhibited whose verdict differs between two
grammars.

**Independence:** IG-4 (meter bucketing) and IG-5 (primitive selection) remain **PENDING**.
Same-author evaluator, meter and primitives remain the standing limitation on every claim in
§2.

**Critical path:** CP1 executing; CP3, CP4, CP6 not started. CP5's identifiability half is
**settled and holds** (`RV-377-116`); its realization half is not started.

---

## 7. The boundary, stated once

> **GMI Boundary Theorem.** Over a 36-kind typed alphabet at depth 1 and 8-bit precision,
> on four rule-40-discriminating ecologies under six registered interventions of which five
> are trustworthy, and having searched 0.4473 % of its own closure lattice:
>
> **(i)** A neutral search over primitives, containing no architecture macro, **does**
> rediscover the coefficient carrier and two memory carriers as intervention-robust,
> non-constant, genuinely-learning machines. GMI's central constructive claim survives at a
> point.
>
> **(ii)** Cost-minimising search over the same primitives **does not** converge on GMI's
> predicted property vectors — on 264 of 264 cells, invariantly under a tenfold budget
> increase, with the discrepancy *widening* as compute grows. GMI's central predictive claim
> fails structurally.
>
> **(iii)** No result proved of one form extends to its behavioural class, and over a
> Turing-complete IR none can. Every result in (i) is a **point claim** about the genotype
> it was measured on. But the *class label* those claims use is real: the fine structure of a
> machine is not identifiable from its behaviour, while its **carrier is** — the
> observational quotient is far too coarse to recover a genotype and just fine enough to
> recover which of five mechanism classes it belongs to.
>
> **(iv)** Therefore GMI is, at registered scope, an **existence theory** as regards *which*
> architecture arises: it can say that such machines arise from primitives, and that the class
> they belong to is measurable from outside; it cannot say which ones will arise, nor lift what
> it learns from one to any other. `RV-377-121` sharpens this — the K4 selection principle is
> not merely unpredictive but **not well-posed**, since cross-seed agreement is 0.0 % at
> 20 000, 100 000 and 500 000 evaluations.
>
> **(v)** But GMI **is predictive about capability**, and verifiably so. For the channel class
> *"machines whose only access to a post-freeze protected `W` is development `D` and query
> `Q`"*, theorem TI-1 gives `accuracy ≤ ½ + r/(2L)`. `RV-377-123` verified this against real
> machines: **0 violations** over 40 draws × 5 machines × 9 values of `r`, **tight** (attained
> at every `r`), **linear to R² = 0.999815** with the predicted slope and intercept, and a
> registered hostile re-test at 200 draws found no leak. This is a quantitative capability
> prediction, derived in advance, about **machines that do not exist** — the class is defined
> by its information channels, not by any architecture.
>
> The distinction is the theory's real shape: **GMI predicts what a machine can achieve given
> its channels, and does not predict which machine a cost-minimising search will build.**

The distance between (i) and (ii) is the theory. Closing it requires exactly the four things
§6 names as not started — and the undecidability obstruction in (iii) means one of them,
the domain-wide lift, is not closable in the form it was posed.

---

## 8. Preservation

No RED result was deleted, weakened or rewritten in producing this document. The original
real-transfer V1 failure, every grammar-bias and developmental falsification, `RV-377-081`'s
0-of-6, `RV-377-083`'s 0-of-3, and `RV-377-089b`'s text (struck in substance, retained in
place) all stand. Restored terminals are reinstated verbatim rather than re-derived.

Four protocol rules were opened by the work behind this document: **44** (control rules apply
retrospectively), **45** (obligations must be shown non-degenerate before use), **46**
(instruments must be validated against their own declared semantics), **47** (no class claim
without a sound *and* complete quotient).

---

## Addendum V1.3 (2026-09-12) — protected K4/K5 V7 folded in; F7 reclassified; K5 revival

Append-only. Nothing above is edited. Source receipts: `microscopes/results/k4_v7/K4_V7_AGGREGATE.json` (job
3605505, beacon 32138309, 264/264) and `microscopes/results/k5_bh_v7/K5_BH_AGGREGATE_V7.json` (job 3605249, beacon
32138625, 256/256), both under execution freezes with unique no-reroll drand rounds (PR #455).

**F1 now holds at PROTECTED tier.** `K4_RECOVERY_GREEN` = **0 of 264** at budget 10^6 on every task (max wall
127.6 s), beacon 32138309: THEORY_RED 150, THEORY_RED_NULL_DOMINATES 76, INCONCLUSIVE_GRAMMAR 38. The §3 F1
statement, previously same-author development-tier, is reproduced under public-beacon seeding.
`K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER = FALSE`.

**F7 / DG-11 closes as `GRAMMAR_AXIS_NOT_VERDICT_INERT`.** The §3 F7 clause ("88 of 88") was a development-tier
reading. At protected tier the three grammars agree on **78 of 88** (family, cell) pairs; the five families whose
verdict splits across grammars are **K4-A09** (THEORY_RED 5 / INCONCLUSIVE_GRAMMAR 7), **K4-A11** (10 / 2),
**K4-A18** (NULL_DOMINATES 3 / INCONCLUSIVE_GRAMMAR 9), **K4-A19** (THEORY_RED 3 / NULL_DOMINATES 9) and
**K4-A20** (NULL_DOMINATES 4 / INCONCLUSIVE_GRAMMAR 8). DG-11 asked for one cell whose verdict differs between
two grammars; ten now exist. The effective K4 sample is therefore larger than 88 and smaller than 264, and the
grammar axis is a real (if minor) source of evidence rather than pure replication. F7 as written is **withdrawn
at protected tier**; F1 is unaffected because no split reaches GREEN.

**K5 terminal at protected tier:** `K5_HELD_FAMILY_RESPONSE_LAWS_GREEN_ON_6_OF_8_LANES_AT_PROTECTED_TIER`.
GREEN on all four grid values: B_ROUTING, B_SPECIALIZATION, B_RESIDUAL, B_COMPILE_SEARCH, D_GENERATIVE,
F_CONTINUAL. Non-green: **C_FEATURE_LEARNING** THEORY_RED (nonlinear_signal 0.6: 0/8 agree, mean margin -1.07;
1.0 INCONCLUSIVE) → revival **RV-377-170**; **E_CONTROL** INCONCLUSIVE (goal_reuse 1/2/8 carry
predicted-inadmissible replicates; 26/26 admissible replicates agree) → revival **RV-377-171**. Both revivals
attribute to the prediction stage (`GMI_K5_V7_REVIVAL_RV_377_170_FREEZE.md`): the feature-learning crossover was
placed by residual magnitude without the reachability clause the theory carries (the developed trainable
realization's training error at 0.6, 0.0910, equals the analytic linear-Bayes floor 0.0911); the control
predictor omitted the admissibility term for its stochastic DIRECT route (per-goal return mean 0.859, sd 0.161).
The corrected predictions on fresh grids ({0.40, 0.50, 0.75, 0.85} and {48, 64, 96, 128}) are GREEN on both lanes
at development tier (billy-old, 80/80, all six probe predictions holding) **and at protected tier** (LUNARC job
3605817, beacon round 32144246, 80/80, terminal `K5_BH_V8_PROTECTED_GREEN`, all fourteen numbered predictions
holding; that document's §4.2). The V7 verdicts are not reopened. Ledger rows RV-377-170 and RV-377-171.

**Terminal register additions (§5):**

| terminal | value |
|---|---|
| `K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER` | **FALSE**, 0/264, beacon 32138309 |
| `GRAMMAR_AXIS_VERDICT_INERT` | **FALSE** at protected tier (78/88); DG-11 closed as `GRAMMAR_AXIS_NOT_VERDICT_INERT` |
| `K5_HELD_FAMILY_RESPONSE_LAWS_GREEN_ON_6_OF_8_LANES_AT_PROTECTED_TIER` | **TRUE**; non-green C (RV-377-170), E (RV-377-171) |

**Boundary clause (vii), appended to §7.** At protected tier the theorem's shape is unchanged: the predictive
claim about *which* machine cost-minimising search builds fails on 264/264 (ii); the held-family response laws,
which are claims about *what a realization can achieve at a given lifecycle price*, hold on six of eight synthetic
lanes, and the two that failed did so because the prediction omitted a clause the theory itself states
(reachability; admissibility). The grammar axis carries a small amount of independent evidence rather than none.
Bookkeeping: `GMI_CLOSURE_GAP_LEDGER_V7.md` reclassifies the LEARNING-SCALE EMPIRICAL residual accordingly;
`GMI_WORK_MANIFEST_V1.json` unit U-A001 is marked done against the K4 V7 receipt with a note that the V7
submitter, not the stale V5 command, was executed.

## Addendum V1.3 (2026-09-12, real transfer and physical sign) — classes 3 and 4 of the closure ledger

Append-only. Nothing above is edited. Source receipts: `microscopes/results/real_transfer_v3/` (RV-377-190, freeze
`cd4c653d`, 104/104), `…/real_transfer_v3_revival/` (RV-377-191/192, freeze `7fe510c7`, 72/72),
`…/real_transfer_v3_revival2/` (RV-377-193, freeze `267f39ee`, 32/32), all on billy-laptop with prediction records
hashed before test access; `microscopes/results/physical_frontier_rv_377_195/` (RV-377-195). Bookkeeping:
`GMI_CLOSURE_GAP_LEDGER_V8.md`.

**Real transfer (class 3).** Three of the eight held-family laws were transferred to scikit-learn learners on real
data with the phase parameter *estimated on the training split*: C_FEATURE_LEARNING (reachability form) is GREEN on
4/4 cells and identical to cross-validation on 32/32 replicates (`PARENT_SUFFICIENT_CV`); F_CONTINUAL is right on
30/32 off-crossover replicates with 0 opposing and undecidable on its crossover cell (0.7 pp of headroom against a
test sd of 0.9 pp at the frozen 0.95 bar); B_SPECIALIZATION is GREEN at high heterogeneity (7/8, margin ten times
the test sd) once the world's feature tails are bounded and undecidable at the three low-heterogeneity grid values
(objective gap below the test sd). Terminal `REAL_TRANSFER_PHASE_LAWS_GREEN_ON_1_OF_3_LANES`. Two learner-class
terms the K5 laws lack were located and are named, not fitted: the continual law's retention fraction (the real MLP
keeps ≈ 2/3 of the disputed mass under replay at high overlap, not 1/2) and the specialization law's mass-weighted
variance term (`σ² p m / n`, hidden by the K5 balanced world).

**Physical sign (class 4).** With published measured constants (Willow gate/readout/T1, Sycamore 26 kW system power,
HERMES 0.86–3.38 µJ per 64-core MVM at 3–4-bit weight precision, Horowitz 45 nm datapath energies) the NC-1 burden
inequality on the protected K5 C `s = 0.6` fixed readout has sign **PARENT** for both an analog crossbar (ratio
64–7.7×10⁴) and a superconducting processor (79–87 majority shots; ratio 10¹⁰–6×10¹⁴), invariant over the quoted
error bars. Terminal `PHYSICAL_FRONTIER_SIGN_FROM_PUBLISHED_CONSTANTS__NOT_MEASURED_IN_PROGRAMME`. Per EF-1 the
variables that could flip it are the obligation's inner dimension (crossbar; `d* ≈ 10⁴–2×10⁵` MACs per query) and the
native saving (quantum; `S ≳ 10¹⁰ pJ` per query); neither is fixed by any registered obligation.

**Terminal register additions (§5):**

| terminal | value |
|---|---|
| `REAL_TRANSFER_PHASE_LAWS_GREEN_ON_1_OF_3_LANES` | **TRUE** (C); F, B direction-green off their crossovers (RV-377-191, RV-377-193) |
| `REAL_TRANSFER_PHASE_LAWS_ADD_NOTHING_OVER_CV_WHERE_DECIDABLE` | **TRUE** |
| `PHYSICAL_FRONTIER_SIGN_FROM_PUBLISHED_CONSTANTS__NOT_MEASURED_IN_PROGRAMME` | **PARENT**, both carriers, one obligation |

**Boundary clause (viii), appended to §7.** The held-family response laws survive contact with real learners exactly
where their descriptors resolve the crossover, and there they coincide with ordinary cross-validation; where the
grid sits inside the finite-sample band of the frozen constitution they are undecidable by construction, and the
laws as stated lack the learner-class terms that would move the crossover. The physical frontier, evaluated from
external measurements rather than derived, points at the classical parent for every registered obligation, and its
identifiability boundary is now a pair of named, bounded, unmeasured workload variables rather than an open set.

## Addendum V1.3 (2026-09-12, RV-377-194) — real-transfer crossover cells re-tested off-band; cost-charged parent

Append-only. Nothing above is edited. Source receipts: `microscopes/results/real_transfer_rv194/` (RV-377-194, freeze
`03a2fea8`, billy-laptop, 96/96, prediction records hashed before test access). Bookkeeping: `GMI_CLOSURE_GAP_LEDGER_V9.md`,
`GMI_REAL_TRANSFER_RV_377_194_FREEZE.md` §8.

**What changed in the laws (pre-registered, learner-class terms named in the previous addendum).** The specialization
law's variance term is the mass-weighted `σ² p m / n`; the continual law's retention fraction is a within-train probe
quantity `ρ̂_s` (fraction of the disputed mass the deployed strategy loses on the old task, measured on a 20 % probe of
the training split, never on the test), with the K5 midpoint rule as the special case `ρ̂ = 1/2`. Both lanes carry the
K5 B lane's finite-sample band explicitly (z = 2 on the paired per-query test errors, or on the accuracy bar), and the
B grid was placed off the band by a frozen power calculation (n_test = 8000, τ ∈ {0.5, 0.65, 0.8, 1.0}). The F crossover
cell cannot be placed off the band on digits (≈ 7 600 queries needed, 1 797 rows exist) and was declared inside-band
by construction before the run.

**Result.** Off the band the transferred laws name the protected winner on 63/64 replicates (B 32/32 across four cells,
0 opposing; F 31/32 across four cells, 0 opposing) at zero extra training runs, where 3-fold cross-validation names it
on 53/64 at 12–15 extra fits per replicate; the eight F differences are all CV naming NONE for a baseline that passes
the bar when trained on the full development data. At the crossovers neither predictor is reliable (law 21/32, CV
20/32; free holdout selection 6/8 on F), and the obstruction has moved: the measured test bands (se 0.002–0.013 at
8 000 queries) are narrower than the crossover gaps, so the residual misses are the descriptors' own finite-sample
noise (τ̂² from 7–17-row modes, ρ̂ from 8–17 disputed probe rows). The corrected continual law names REPLAY at the
crossover on 5/8 where the K5 rule named it 0/8. The frozen aggregate terminal is
`REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV`, produced by a kill condition that scored agreement with CV rather
than correctness against it and fired on CV's errors; the label is carried unchanged and its defect recorded.

**Terminal register additions (§5):**

| terminal | value |
|---|---|
| `REAL_TRANSFER_PHASE_LAWS_ADD_NOTHING_OVER_CV_WHERE_DECIDABLE` | **FALSE** (superseded by RV-377-194: same winner at zero cost in B; more accurate than CV in F) |
| `REAL_TRANSFER_PHASE_LAWS_FREE_PREDICTOR_RIGHT_ON_63_OF_64_OFF_BAND_REPLICATES__CV_53_OF_64_AT_12_TO_15_EXTRA_FITS` | **TRUE** |
| `REAL_TRANSFER_CROSSOVER_CELLS_INSIDE_BAND_BY_CONSTRUCTION__UNDECIDED_BY_LAW_21_OF_32_OR_CV_20_OF_32` | **TRUE** |
| `F_CONTINUAL_REAL_LAW_EQUALS_FREE_HOLDOUT_SELECTION` | **TRUE** (37/40) |
| `REAL_TRANSFER_RV_377_194_FROZEN_TERMINAL` | `REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV` (mis-specified kill; not re-scored) |

**Boundary clause (viii), amended by appending.** Where the held-family laws carry their learner-class terms and the
grid is off the finite-sample band, they are a free, pre-outcome substitute for cross-validation on real learners
(same-author data); where the grid sits at the crossover the limit is no longer the protected test but the descriptors'
sample sizes, and no free predictor tested here resolves it. The boundary is unchanged in kind — independent
authorship, modern scale, fresh episodes rather than datasets — and narrower in extent by one class of claim: the laws
are no longer "equal to CV where decidable", they are cheaper than CV where decidable and at least as accurate.

## Addendum V1.3 (2026-09-12, RV-377-118D) — DG-12 completed on the twelve unaudited modules; the terminal stays FALSE

Append-only. Nothing above is edited. Source receipts: `microscopes/results/STAGE_DG12_COMPLETION_<module>_old.json`
(12) and `STAGE_DG12_COMPLETION_old.json` (RV-377-118 Lane D, freeze `3e91942e`, laptop billy-old, content hashes
identical across two invocations). Bookkeeping: `GMI_DG12_COMPLETION_RV_377_118D_FREEZE.md`, ledger row `RV-377-118D`.

**What was asked (§6, Coverage).** `RV-377-112` (T3) audited 16 obligations, found `e1_scdi` regime B to be a constant,
and listed twelve obligation-bearing modules as uncovered. Prediction D1 of the distributed batch, frozen before the
run: at least one further degenerate or near-degenerate obligation is found among the 12.

**Result.** D1 **held**. Of the twelve, eleven carry an obligation of the DG-12 shape and one (`b2_common`) is an
instrument library with none. Three of the eleven carry degenerate or near-degenerate obligations over the evaluation
set their own `run()` scores: `axis_a`'s `MAXV` obligation is the constant 15 (12 at T = 4) on the scored second half
of **every** registered stream length, and `PARITY` at T = 4 is the constant 0; `e1_cp`'s regime B is 21-of-24 or
23-of-24 constant at the coefficients capability is scored against (a constant emitter of 1 is admissible there at
0.875 / 0.9583 ≥ 0.85), and its coefficient space is degenerate on exactly the 37 824 / 65 536 assignments `e1_scdi`'s
is, because it is the same function; `refine_f`'s own fifth serving regime E (1 iff the scope sum is positive) is the
constant 1 on all 24 queries, and the regime B it re-imports likewise. The other eight — the three B2 band obligations
at every declared width, `e1_iql` at all 16 orientations, `e1_lmhm`, `e1_vgsc` on every cell, `e1_vlc` on every cell —
are non-degenerate; `b1x` inherits the registry obligations T3 already covers. Eleven own-registered rows in all, ten
beyond the `e1_scdi` construction.

**What this does and does not void.** Rule 22 and rule 40 had already caught three of the four constructions
incidentally (`RV-377-072` voids exactly the `MAXV` and `PARITY`-T=4 cells; `RV-377-108` marks `e1_cp` regime B
non-discriminating), so no verdict in §2 or §3 moves. What moves is the reading — those obligations are constants, not
merely easy for a constant — and one thing nothing could have caught: `refine_f` takes no verdict against a truth, so
its regime-E demand (`COMPOSITIONAL_UNSEEN`) witnesses the parent's abstention rather than any derivation, and the
regime-B/E parts of its `ABSTAIN_OBLIGATION` lifecycle score (48 of 120 scored cells per pair) carry no information.
`P13`'s split is decided first by `OVERFLOW` and stands; `P12` and `P14` are unaffected.

**Terminal register additions (§5):**

| terminal | value |
|---|---|
| `DG-12_CLOSED` | **TRUE** as an audit, at registered scope (12 of 12 modules) |
| `NO_DEGENERATE_OBLIGATION_AT_REGISTERED_SCOPE` | **FALSE** (unchanged in value; now on 4 modules — `e1_scdi`, `axis_a`, `e1_cp`, `refine_f` — rather than 1) |
| `AXIS_A_MAXV_OBLIGATION_IS_A_CONSTANT_ON_EVERY_SCORED_WINDOW` | **TRUE** (5 of 5 stream lengths) |
| `E1_CP_REGIME_B_NEAR_DEGENERATE_ON_EVERY_MULTI_REGIME_CELL` | **TRUE** (21/24, 21/24, 23/24; coefficient space 0.5771) |
| `REFINE_F_FIFTH_REGIME_E_IS_A_CONSTANT_ON_EVAL_QUERIES` | **TRUE** (24/24) |
| `REGISTERED_SMOOTH_TABLE_OBLIGATIONS_NON_DEGENERATE` | **TRUE**, 12/12 (unchanged) |

**Open gaps (§6), amended by appending.** Coverage: DG-12 is closed as an audit; the three degenerate constructions
remain in their instruments, and repairing them (a τ or coefficient grid for regime B, a sign regime over signed
factors for E, a scored window that starts before the running maximum saturates) re-points historical claims and is
DG-13-class work. Methodological: rule 45 is enforced by a post-hoc receipt, not by a precondition inside `run()`. The
boundary is unchanged in kind and narrower in extent by one more instrument class: thresholded aggregates (a sum
against a fixed τ, the sign of a positive sum, a running maximum of a bounded stream) evaluated on all-active query
sets are the obligation constructions that degenerate in this corpus; exact sums, pairwise comparisons, band
obligations and the interventional vector do not.
