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
