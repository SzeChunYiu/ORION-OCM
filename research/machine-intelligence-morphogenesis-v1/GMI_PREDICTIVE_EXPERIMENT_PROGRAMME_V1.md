# GMI Predictive Experiment Programme v1

Status date: 2026-09-11.

Status: **FROZEN EXECUTION PLAN FOR TESTING GMI PREDICTIVITY AND THE VLC MISSING-MORPHOLOGY PREDICTION.**

Authority: `GMI_MISSING_MORPHOLOGY_PREDICTION_V1.md` must already be committed before any confirmatory execution.

The goal is not to accumulate supportive demonstrations. The programme is staged so that each level can kill or narrow the theory before the next expensive level.

---

# 1. Scientific objective

The theory becomes genuinely predictive only if pre-outcome obligation/machine structure predicts **future developmental geometry/frontier movement** and, eventually, predicts a morphology property vector before search.

The central chain is:

\[
\Xi(\Omega)
+\mathcal R_M
\longrightarrow
\widehat{\mathcal G}_M
\longrightarrow
\widehat{\mathcal F}(\Omega)
\longrightarrow
\text{predicted morphology properties}
\longrightarrow
\text{neutral recovery}.
\]

The programme has six experimental tiers.

---

# 2. E0 — exact finite VLC phase microscope

Purpose: verify that the frozen qualitative phase prediction has executable, non-ambiguous measurement semantics. This is a calibration only; generic lifecycle economics owns the mathematics.

Executable: `gmi_vlc_exact_phase.py`.

## 2.1 Exact world

Number of semantic factors:

```text
N = 15
```

Every query touches exactly four distinct factors. Instead of random sampling, **all** `C(15,4)=1365` query scopes are enumerated.

An update has a registered semantic dependency cone of size `r`; every `r`-subset is enumerated for exact expected affected-module counts.

Candidate realizations use equal-size contiguous factors with module size

```text
k in {1,3,5,15}
```

and one binary lifecycle policy

```text
versioned in {false,true}.
```

These labels are not an unknown-form search. E0 only checks the lifecycle phase logic underlying the property prediction.

## 2.2 Frozen cost semantics

For module size `k`:

```text
module_count          = N / k
local_materialization = 2^k
build_work            = module_count * 2^k
```

For a query touching `m_q` modules:

```text
serve_work = m_q + 0.25 * max(0,m_q-1)
```

For an update cone touching `m_u` modules:

```text
rebuild_work = m_u * 2^k
update_work  = rebuild_work * 1.5
```

where the `0.5` increment is local verification work.

Standing materialized-state charge:

```text
memory_charge = 8 * module_count * 2^k * copies
copies = 2 if versioned else 1
```

Retention/availability penalty per update:

```text
retention_penalty = retention_price * rebuild_work * exposure
exposure = 0.05 if versioned else 1.0
```

Total lifecycle score:

\[
C=build+H\,E[serve]+U\,E[update]+memory+U\,E[retention\ penalty].
\]

No parameter may be changed after confirmatory output is inspected.

## 2.3 Frozen regimes

### R* target

```text
H = 120000
U = 600
update_cone = 1
retention_price = 2.5
```

Prediction:

```text
winner.versioned = true
1 < winner.module_size < 15
```

### T1 stationary twin

```text
H = 120000
U = 0
update_cone = 1
retention_price = 2.5
```

Prediction:

```text
winner.module_size = 15
winner.versioned = false
```

### T2 dense-dependency twin

```text
H = 120000
U = 600
update_cone = 12
retention_price = 2.5
```

Prediction relative to R*:

```text
winner.module_size >= R*.winner.module_size
```

### T3 weak-retention twin

```text
H = 120000
U = 600
update_cone = 1
retention_price = 0
```

Prediction:

```text
winner.versioned = false
```

### T4 short-reuse twin

```text
H = 6000
U = 600
update_cone = 1
retention_price = 2.5
```

Prediction relative to R*:

```text
winner.module_size <= R*.winner.module_size
```

## 2.4 E0 acceptance

Strong E0 terminal:

```text
VLC_PHASE_PREDICTION_EXACT_MICROSCOPE_GREEN
```

iff all five registered predictions hold.

Any miss is reported verbatim. No parameter retuning on the same confirmatory world.

The exact output must include every candidate/regime row, not only winners.

---

# 3. E1 — controlled parent-portfolio phase experiment

Purpose: move from algebraic microscope to actual learning/revision systems.

## 3.1 Synthetic ecology family

Generate tasks with a known sparse causal/dependency graph. Each semantic factor has a local predictor and may be invalidated/redefined over time. Queries compose 1–6 factors. The experiment controls independently:

```text
delta   dependency-cone fraction
nu      update/invalidation rate
eta     query reuse horizon
lambda  tolerated collateral regression
chi     verifier locality/cost
gamma   feedback density / learnability
pi      compute-memory-verification price vector
```

Surface labels and feature encodings are reminted independently of the graph so family labels cannot solve the prediction.

## 3.2 Strong parent implementations

At minimum compare:

```text
P-N   monolithic neural learner with replay/regularization control
P-M   sparse/modular neural or MoE continual learner
P-U   SISA-style partitioned retraining / exact-unlearning control
P-T   explicit dependency/TMS-like rule or table system
P-P   tractable probabilistic/factored circuit control where applicable
P-R   retrieval/external-memory control
P-H   strongest ordinary neuro-symbolic / explicit hybrid available
VLC   hand-instantiated predicted property vector
```

No weak straw parent may count.

## 3.3 Metrics

Primary vector, never post-hoc scalarized:

```text
fresh-task verified accuracy / admissibility
serving work and latency
build/acquisition work
revision/unlearning work
unaffected-query regression after local updates
update blast-radius fraction
retention/plasticity over task lifetime
verifier calls/work
persistent and peak memory
failure/censored-run rate
```

## 3.4 E1 prediction

VLC need not win everywhere.

Required signature:

```text
R* target: VLC enters the Pareto frontier and beats every single parent on at least one
           registered tradeoff while matching all protected obligations.
T1/T2/T3/T4: at least two twins remove VLC from the frontier or reverse the targeted advantage.
```

If VLC dominates every regime, suspect benchmark/search encoding bias.

---

# 4. E2 — GMI realization-demand signature prediction

Purpose: show that GMI predicts frontier movement from architecture-neutral coordinates, not merely that one designed VLC system works.

## 4.1 Development / protected split

Use disjoint ecology seeds and surface remints.

Development side may estimate/freeze a compact mapping

\[
(\Xi,\mathcal R_M)\to\widehat{B}_M
\]

with no architecture-label features.

Protected side evaluates rank/frontier membership.

## 4.2 Parent first refusal

For each morphology family, include its strongest native predictor:

```text
neural scaling/optimization features
MoE routing/load features
symbolic search/graph features
probabilistic circuit structural features
program-search/library features
```

GMI passes E2 only if the shared coordinates add held-out predictive value beyond the product of native predictors.

## 4.3 Acceptance

Minimum publishable-style target:

```text
family-held-out frontier classification AUROC >= 0.75
AND
rank-correlation improvement >= +0.10 over the best family-native/product baseline
AND
same coordinate definitions used unchanged in every family
```

These numerical gates are provisional until a development-only power/calibration pass is completed; once a confirmatory gate is frozen, it cannot be changed after protected outcomes.

---

# 5. E3 — neutral morphology recovery

Purpose: test the real D3/U4 claim: theory predicts a morphology **before** search.

## 5.1 Neutral grammar

The search vocabulary must not contain:

```text
VLC
NEURON
ATTENTION
MOE
TMS
PRODUCTION_RULE
BAYES_UPDATE
PROGRAM_INTERPRETER
OCM_ASSET
VERSIONED_MODULE
```

Allowed primitive categories must be generic and low-level, such as:

```text
typed state cells
local transition kernels
composition edges
bounded local mutable state
copy/checkpoint primitive
external verifier call
conditional routing edge
cache/materialize primitive
create/delete/replace generic component
```

A search-encoding tournament is mandatory so the descriptor does not manufacture the target species.

## 5.2 Prediction scored without labels

After search, measure P1–P5 behaviorally:

```text
factor locality
persistent-vs-serving state separation
update invalidation cone
verify-before-adoption behavior
router/update timescale separation
```

The search succeeds only if the R* ecology recovers the frozen property vector significantly more often than negative twins and random/ordinary multiobjective/QD controls.

## 5.3 Acceptance

Minimum:

```text
>= 70% of independent R* searches produce P1-P5 match
<= 30% pooled negative-twin searches produce P1-P5 match
no single search encoding accounts for > 60% of all matches
candidate remains on the registered Pareto frontier after all search cost is charged
```

These are intentionally demanding initial gates; a preregistered power analysis may tighten/replace them before first protected search, never after.

---

# 6. E4 — real-regime transfer

Purpose: show the same theory survives domains where verification/revision are real rather than synthetic.

Run at least three regimes with unchanged GMI definitions.

## E4-A code maintenance

Ecology:

```text
versioned repository
execution tests/static checks
localized API/spec changes
repeated serving/repair tasks
explicit dependency graph
```

Key outcome: can pre-change structure predict repair/update burden and whether local compiled factors beat monolithic adaptation?

## E4-B formal mathematics

Ecology:

```text
Lean theorem corpus
kernel verification
lemma addition/revocation/replacement
fresh theorem obligations
```

Key outcome: local theorem/library changes with exact verifier and dependency cones.

## E4-C changing factual/scientific knowledge

Ecology:

```text
versioned evidence/fact corpus
source withdrawal/revision
multi-hop queries
provenance requirement
held-out updated facts
```

Key outcome: correctness after revocation, stale-influence rate, collateral regression and update cost.

Do not collapse these three into one score.

---

# 7. E5 — novelty / reduction attack

Even a successful E3/E4 candidate is not automatically a new form.

For each survivor:

1. compile/reduce to sparse MoE/modular CL;
2. reduce to SISA/unlearning;
3. reduce to TMS/ATMS + compiled rules;
4. reduce to probabilistic circuits/factored models;
5. reduce to neuro-symbolic parent products;
6. reduce to program/library learning + verifier;
7. reduce to proof-carrying/dynamic-update system;
8. rerun under alternate hardware/resource prices;
9. ablate versioning, authority/serving split, locality and stable router separately;
10. replicate on disjoint surface/ecology generation.

A serious new-morphology claim requires a bounded developmental/resource separation, not a new diagram.

---

# 8. E6 — K2/K3 / meta-morphogenesis

Only after E1–E5.

K2 question:

> Does inherited morphology/dependency structure reduce the cost of acquiring **new useful factorization/proposal geometry** on fresh families?

K3 question:

> Does the process that chooses boundaries, compilation strategy and replacement policy itself improve across fresh ecology families under a fixed external constitution?

Primary K3 metric:

\[
B^{discover}_{g+1}(\text{verified frontier improvement})
<
B^{discover}_{g}(\text{verified frontier improvement}).
\]

AutoML, learned optimizer, MetaBBO, PowerPlay and other meta-search parents receive first refusal.

---

# 9. Kill conditions

Stop or demote the theory if any of the following survives replication:

```text
E0 prediction fails under frozen semantics
family identity is required for E2 prediction
family-native parents explain all shared-signature gains
VLC-like properties occur equally in negative twins
search encoding predicts recovered species better than Xi
complete lifecycle accounting removes the phase advantage
VLC compiles to a registered parent with bounded overhead and no developmental distinction
real code/math/factual regimes require incompatible redefinitions of the GMI quantities
```

Correct negative terminal:

```text
GMI_REMAINS_SYNTHESIS_METROLOGY__PREDICTIVE_MORPHOGENESIS_NOT_ESTABLISHED
```

---

# 10. Execution order

```text
NOW:   E0 exact confirmatory microscope
NEXT:  E1 parent portfolio + E2 shared-signature prediction
THEN:  E3 neutral recovery only if E1/E2 are green
THEN:  E4 real code/math/factual transfer
THEN:  E5 novelty reductions
LAST:  E6 K2/K3
```

Do not jump directly to large morphology search. The theory must first predict where and why the target property vector should appear and disappear.
