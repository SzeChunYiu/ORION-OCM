# Machine Epistemics Evolvability Theory V0.2
## Developmental evolvability = locality + self-identifiability + searchability under external epistemic governance

**Status:** PROVISIONAL THEORY + E2 EXPLORATORY SYNTHETIC FALSIFICATION.  
**Supersedes for steering:** `MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0.md` while preserving V0 as historical theory.  
**Claim authority:** NO OCM SUPERIORITY CLAIM. NO NEURAL/TRANSFORMER SUPERIORITY CLAIM. NO UNIVERSAL COGNITIVE BASIS CLAIM.  
**Programme:** #143 empirical ladder; #144 publication constitution; #145 operator/field theory; #149 self-evolution; #151 developmental spine; #62 experience consolidation; #93 General Epistemic Field.  
**Synthetic evidence:** `research/evolvability-theory-v0/SYNTHETIC_RESULTS_V0_2.json`, reproducible from `synthetic_evolvability.py`.

---

# 0. Research disposition

V0 proposed that learned sparse causal factorization may make cognition and self-change local enough to amortize the cost of explicit epistemic structure.

The deeper research pass changes that claim.

> **Sparse factorization is necessary in some favorable regimes but is not sufficient for evolvability.**

A machine can be modular and still be hard to improve if:
- its failures do not reveal which component or interaction is responsible;
- affordable interventions cannot distinguish competing causes;
- the localized repair space remains huge or deceptive;
- the factorization drifts faster than it can be maintained;
- useful future architectures require temporarily worse intermediate states that a monotonic search discards;
- a simpler direct empirical, probabilistic, AutoML, reflective-search, or open-ended-search parent reproduces the benefit.

The revised central object is therefore **Developmental Epistemic Evolvability**:

> Can one persistent machine use verified task experience and verified interventions on itself to become progressively easier to learn, diagnose, modify and extend, such that future competence and future self-repair require less information and search while task quality, explicit revision and external authority are preserved?

This is a trajectory claim, not a fixed-architecture claim.

---

# 1. Machine object

Keep the programme factorization:

```text
M_t = (F_t, O_t, Π_t, C)
```

where:
- `F_t` = persistent typed epistemic field/state;
- `O_t` = executable operator algebra including learned methods/macros;
- `Π_t` = executive/navigation/composition/acquisition policy;
- `C` = external constitution: checking, authority, metering, adoption/commit boundary.

For developmental self-improvement define:

```text
S_t = SelfModel(M_t)
```

and a learned causal organization:

```text
H_t = CausalFactorization(M_t)
```

The separation remains load-bearing:

```text
machine state
!=
machine model of machine state
!=
authority to change machine state
```

`S_t/H_t` may be wrong, incomplete, stale, or unidentifiable. They never self-authorize.

---

# 2. The evolvability triad

The revised theory uses three independent coordinates.

## 2.1 Locality / effective cognitive coupling `κ`

Let `V_t` be registered cognitive components and `Closure_H(z)` the true set that must be reconsidered after failure/intervention/change `z`.

```text
κ_H(z) = |Closure_H(z)| / |V_t|
```

and under ecology `E`:

```text
κ(M;E) = E_z[κ_H(z)]
```

Low `κ` means a change can in principle be local.

Low stored graph density does **not** imply low `κ`; missing dependencies can manufacture false locality.

## 2.2 Self-identifiability / epistemic self-observability `Ω`

Let `Z` be the latent responsible fault/coupling class and `Q` the allowed diagnostic probes/interventions.

Define the minimum expected diagnostic burden for target error `ε`:

```text
B_id(ε)
=
min_policy E[ total probe/intervention cost ]
subject to P(Z_hat != Z) <= ε.
```

Define a secondary observability coordinate:

```text
Ω(ε) = H(Z) / B_id(ε)
```

in bits per registered diagnostic-cost unit.

High `Ω` means affordable observations/interventions sharply distinguish internal causes.

This is not ordinary software logging. It includes whether interventions are causally discriminating.

## 2.3 Repair searchability `χ`

After diagnosis evidence `e`, let `R(e)` be admissible repairs and `p(r|e)` their posterior/proposal weights.

Define effective repair-space size:

```text
χ(e) = 2 ^ H(R | e)
```

or, when a probabilistic repair model is unavailable, report the complete candidate count and evaluation-cost distribution instead.

Low `χ` means localization actually constrains the repair search.

A perfect diagnosis with a combinatorially enormous repair language may still provide no useful evolvability advantage.

---

# 3. Revised evolvability cost law

A self-change episode has:

```text
failure/opportunity
→ observe
→ discriminate / diagnose
→ localize
→ propose/search
→ construct challenger
→ shadow evaluation
→ assurance
→ external adoption/rejection
→ migration/reopening
→ monitor/rollback
```

The primary resource object remains a vector, but a schematic lower-bound decomposition is:

```text
C_evolve
>=
B_id(ε)
+ B_search(κ, χ)
+ C_verify
+ C_migrate
+ C_maintain
```

A structured/local machine can beat global reoptimization only when:

```text
B_id
+ B_search(local)
+ verification
+ maintenance
<
global/direct adaptation cost
```

This generalizes the V0 diagnosis-value inequality.

The theory therefore predicts no universal OCM advantage. Advantage is a **phase regime**.

---

# 4. Information-theoretic self-identifiability bound

For a uniform `m`-way responsible-cause variable `Z`, any estimator with error probability at most `ε` requires, by Fano's inequality:

```text
I(Z;Y)
>=
log2(m)
- h2(ε)
- ε log2(m-1)
```

where `Y` is the complete diagnostic observation and `h2` is binary entropy.

If every allowed probe yields at most `b` bits of mutual information under the registered ecology, then any strategy requires at least:

```text
n
>=
ceil(
  [log2(m)-h2(ε)-ε log2(m-1)] / b
)
```

probes, ignoring additional adaptivity/overhead costs.

Example from the committed harness:

```text
m = 30 causes
ε = 0.05

required information >= 4.3776 bits
```

Therefore the lower bounds are:

```text
0.10 bit/probe -> >= 44 probes
0.25 bit/probe -> >= 18 probes
0.50 bit/probe -> >=  9 probes
1.00 bit/probe -> >=  5 probes
2.00 bit/probe -> >=  3 probes
```

This is parent-owned information theory, not an OCM theorem.

Its Machine Epistemics relevance is concrete:

> A self-repair architecture that supplies an oracle-like ablation channel is studying a different problem from one whose real failures expose only low-information traces.

This explains why M11 controlled diagnosis and historical real-failure diagnosis must never share one claim without measuring their diagnostic information channels.

Reference:
- Fano lower-bound form: https://www.mdpi.com/1099-4300/19/11/617
- Active fault diagnosis explicitly designs interventions to separate fault hypotheses: https://www.sciencedirect.com/science/article/pii/S1367578819300070

---

# 5. Self-intervention as learned self-structure

Each resolved self-change can be treated as an intervention:

```text
component perturbation/change
→ observed downstream consequences
→ verified responsible component(s)
→ update self-model H_t
```

Thus self-improvement episodes need not only improve the current machine.

They can train future self-diagnosis.

This idea is **not novel by itself**.

A direct 2026 parent is Self-Interventional Learning (SIL), which perturbs a neural system, observes functional consequences, learns predictive self-knowledge, generalizes to unexecuted interventions, and uses that knowledge for later structural action.

SIL reports strong self-prediction improvements, but its model-guided action did not significantly beat a direct empirical-memory policy and its CIFAR-10/ResNet validation did not establish a robustness advantage.

Reference:
- https://arxiv.org/abs/2608.14894

Therefore OCM may not claim novelty for:

```text
perturb self
→ observe outcome
→ learn predictive self-model
→ use self-model to repair
```

The residual must come from a stronger lifecycle, if one exists.

---

# 6. Synthetic self-intervention result V0.2

The harness creates 30 hidden components and 80 observable symptoms.

Resolved single-component failures teach:
- an explicit component→symptom self-graph;
- a direct Bernoulli probabilistic parent using the same resolved interventions.

Metric:

```text
components inspected before all true causes are reached
```

## 6.1 Single-fault tests

At 200 resolved interventions:

```text
blind search                   15.845
explicit learned self-graph     1.140
direct probabilistic parent     1.362
```

At 400:

```text
blind                           14.958
explicit graph                   1.058
direct parent                    1.035
```

So self-intervention history can reduce future localization search by more than an order of magnitude in this synthetic world.

But the direct parent closes the gap at scale.

## 6.2 Unseen two-fault composition

Training still contains only single faults.

At 200 resolved interventions:

```text
blind                           20.427
explicit graph                   4.672
direct parent                    3.050
```

At 400:

```text
blind                           20.575
explicit graph                   2.577
direct parent                    2.163
```

The explicit self-graph loses to the simple probabilistic parent on compositional faults.

Disposition:

```text
SELF_INTERVENTION_INFORMATION_USEFUL
+
EXPLICIT_SELF_GRAPH_RESIDUAL_NOT_ESTABLISHED
```

This directly attacks any claim that explicit self-structure is automatically the best self-model.

---

# 7. Interaction discovery is the harder problem

Single-component intervention effects do not identify all higher-order interactions.

Current branch evidence already found this empirically in another form: leave-one-out dependency attribution misses redundant supports.

The general problem is:

```text
main effects
!=
alternative support
!=
conjunction
!=
redundancy
!=
synergy
!=
context-conditioned interaction
```

A serious learned self-model must therefore represent **support families / interaction structure**, not only edges.

Candidate machinery includes:
- group interventions;
- adaptive intervention design;
- ATMS/minimal environments;
- hitting-set/support-family discovery;
- factorial/sparse interaction models;
- BDD/ZDD or related compiled support representations;
- learned probabilistic interaction models.

All have strong parents.

An OCM residual exists only if the full epistemic lifecycle—identity, warrant, scope, revision, exact stale-state prevention and lifetime amortization—survives those parents.

---

# 8. Monotonic deployment is not enough for open-ended development

Current governed self-change correctly prevents a worse candidate from replacing the deployed incumbent.

However, the scientific search process need not require every intermediate architecture to be deployable.

Some useful architecture paths are:

```text
M0
→ M1'  (worse now)
→ M2'  (still worse)
→ M3'  (better than M0)
```

If `M1'` is deleted solely because it is immediately worse, `M3'` may become unreachable.

Therefore separate:

```text
DEPLOYED LINEAGE
```

from

```text
SHADOW DEVELOPMENT LINEAGES.
```

The constitution may require monotonic deployment while allowing non-deployed branches to continue evolving in isolated shadow state.

A shadow branch has:
- no authority;
- no protected-test feedback;
- separate persistent state;
- full resource accounting;
- provenance to every ancestor;
- no effect on the incumbent;
- eligibility for external adoption only when a descendant independently passes the frozen gate.

This is **not novel by itself**.

Darwin Gödel Machine explicitly keeps an archive of diverse generated agents to preserve stepping stones and explore multiple paths.

Reference:
- https://arxiv.org/abs/2505.22954

---

# 9. Synthetic stepping-stone result V0.2

The harness uses a 12-bit deceptive landscape with four 3-bit modules.

For each module:

```text
000 -> local optimum 0.8
111 -> global optimum 1.0
1-2 changed bits -> fitness valley
```

A strict monotonic single-bit self-improver stops at:

```text
quality = 0.800
after 13 evaluations
```

A governed shadow archive retains lower-quality variants while deployed quality never regresses.

At budget 4000:

```text
shadow archive mean best quality = 0.985
global optimum reached = 70% of runs
```

So stepping stones matter.

But a conventional broader 1–3-bit mutation/search parent is substantially stronger:

```text
budget 500:
  parent mean quality = 0.990
  optimum in 80% of runs

budget 1000:
  parent quality = 1.000
  optimum in 100% of runs
```

Disposition:

```text
MONOTONIC_SEARCH_INSUFFICIENT_ON_DECEPTIVE_LANDSCAPE
+
SHADOW_STEPPING_STONES_USEFUL
+
BROAD_SEARCH_PARENT_SUFFICIENT_FOR_THIS_FIXTURE
```

Therefore adding a shadow archive is justified as search hygiene, not as an OCM residual.

---

# 10. Credit assignment and reflective search are parent-owned

MARS addresses expensive opaque performance attribution through:
- modular construction;
- budget-aware search;
- comparative reflective memory.

Its paper reports that 63% of utilized lessons in its analysis came from cross-branch transfer.

Reference:
- https://arxiv.org/abs/2602.02660

Thus OCM may not claim novelty for:

```text
compare successful/failed branches
→ identify what changed
→ store lesson
→ reuse lesson elsewhere
```

MARS must receive first right of refusal for self-improvement credit-assignment claims.

---

# 11. Developmental curriculum should optimize future learnability

Issue #151 correctly creates a developmental spine.

V0.2 adds a stronger curriculum principle.

Developmental experiences should not be selected only by:
- easy→hard ordering;
- immediate task score;
- novelty;
- resemblance to human schooling.

An experience can be valuable because it reveals **overhypotheses** that make later learning cheaper.

A provisional developmental utility is:

```text
U(e)
=
ΔQ_now
- λ C(e)
+ α I(Θ_reusable ; Y_e)
+ β E[ future acquisition-cost reduction ]
```

where `Θ_reusable` denotes hypotheses about reusable task/cognitive structure.

This equation is a design hypothesis, not a theorem.

Strong parents already exist.

Human active-causal-learning work finds evidence that people learn and transfer causal overhypotheses and may choose interventions that facilitate future learning.

Reference:
- https://link.springer.com/article/10.1007/s42113-023-00195-0

Developmental curiosity work also finds 4-year-olds preferentially explore activities with novelty and learning progress.

References:
- https://doi.org/10.1111/cdev.14158
- https://www.sciencedirect.com/science/article/pii/S1364661324000287

Therefore Machine Epistemics cannot claim novelty for curiosity, learning progress, information gain or overhypothesis learning.

The candidate residual is whether one persistent governed machine can turn such developmental experience into **explicitly reusable, revisable, cross-domain cognitive structure** whose future causal effect is independently witnessed.

---

# 12. Modularity is not a universal evolvability law

Biological evolvability literature is a useful warning, not authority for machine design.

Modularity can reduce interference, but it is not the only possible basis of evolvability and maximum modularity need not be optimal. Intermediate integration can be favorable in some models.

References:
- Hansen, "Is modularity necessary for evolvability?": https://pubmed.ncbi.nlm.nih.gov/12689723/
- Review noting mixed/contingent modularity–evolvability relations: https://doi.org/10.1007/s11692-022-09570-4

Therefore the OCM objective is not:

```text
minimize κ at any cost
```

It is:

```text
maximize capability/evolvability Pareto quality
subject to complete epistemic obligations.
```

---

# 13. Revised phase diagram

Three primary axes:

```text
κ = effective coupling
Ω = self-observability / identifiability per cost
χ = effective repair-space size
```

with structural drift `δ_H` as a fourth pressure.

## Regime A — local, observable, searchable

```text
κ low
Ω high
χ low
δ_H low
```

Prediction:
- local diagnosis works;
- repair search remains small;
- factorization investment can amortize;
- self-improvement becomes progressively cheaper.

This is the strongest candidate Machine Epistemics regime.

## Regime B — local but unobservable

```text
κ low
Ω low
```

The right repair may be small but finding where to act is expensive.

Prediction:
- self-model/logging/probe design dominates;
- oracle-ablation experiments overstate practical evolvability.

## Regime C — observable but unsearchable

```text
Ω high
χ high
```

The machine knows what subsystem is responsible but cannot efficiently construct a repair.

Prediction:
- program synthesis/AutoML/evolutionary/neural search dominates.

## Regime D — dense/entangled

```text
κ high
```

Local models lose sufficiency.

Prediction:
- global/statistical optimization gains relative value;
- explicit epistemic governance may still aid correction/authority, but no efficiency advantage should be presumed.

## Regime E — drifting

```text
δ_H high
```

Any learned self-model/factorization becomes stale.

Prediction:
- maintenance/refactorization can erase the lifetime advantage.

---

# 14. The developmental evolvability trajectory

The strongest theory is now a trajectory over #151:

```text
D0 games / exact interaction
→ D1 composition / failure
→ D2 planning / probes
→ D3 mathematics + controlled language
→ D4 coding/science
→ D5 metacognition
→ D6 governed self-evolution
```

At developmental checkpoint `t`, measure:

```text
Q_t       verified capability
κ_t       effective cognitive coupling
Ω_t       self-identifiability per diagnostic cost
χ_t       effective repair/search space
P_t       new primitive pressure
k_t/N_t   active fraction
C_acq,t   acquisition cost
C_rep,t   reasoning/query cost
C_rev,t   revision cost
C_evo,t   self-change cost
```

The strongest developmental prediction is not merely:

```text
Q_t increases.
```

It is:

```text
Q_t increases
while
future C_acq and C_evo decrease
because
κ/Ω/χ move into a more favorable regime.
```

Candidate favorable trend:

```text
κ_t ↓
Ω_t ↑
χ_t ↓
reuse/composition ↑
primitive pressure ↓ or becomes phased
```

None is assumed.

A negative trajectory is scientifically decisive.

---

# 15. Self-improvement should train the self-improver

Every governed self-change episode should emit two products:

```text
A. the adopted/rejected machine change
B. training evidence about the machine's own causal organization
```

For episode `e` retain:

```text
pre-change machine identity
failure observations
competing diagnoses
probe/intervention identity
predicted consequences
candidate origin
actual shadow consequences
preservation effects
resource effects
adoption/rejection
rollback result
later recurrence
```

Then update:
- self-structure hypotheses;
- diagnosis policy;
- proposal prior;
- repair-cost model;
- expected information gain of future probes.

This creates the recursive developmental loop:

```text
self-change experience
→ better self-model
→ better probe selection
→ cheaper localization
→ narrower proposal space
→ better future self-change.
```

The loop is the target.

SIL, active fault diagnosis, causal discovery, AutoML and meta-learning remain strong parent components.

---

# 16. Strongest-parent collision matrix

| Candidate idea | Strong parent | Consequence for OCM claim |
|---|---|---|
| self-intervention → predictive self-model | Self-Interventional Learning (2026) | parent-owned |
| active discriminating probes | active fault diagnosis / Bayesian active causal learning | parent-owned |
| modular credit assignment from branch comparison | MARS (2026) | parent-owned |
| archive non-monotonic stepping stones | Darwin Gödel Machine | parent-owned |
| architecture/configuration search | AutoML / BO / evolutionary search / program repair | parent-owned |
| reusable learned program abstractions | DreamCoder / Stitch / grammar induction | parent-owned |
| active learning of future-useful abstract structure | causal overhypothesis learning | parent-owned |
| curiosity / learning progress curriculum | developmental/curiosity literature | parent-owned |
| modularity implies evolvability | evolutionary-biology literature explicitly says relationship is contingent | universal claim rejected |

A future OCM residual must survive the **composition** of the relevant parents, not each separately.

---

# 17. Candidate residual after subtraction

The surviving candidate contribution is narrower:

> **Epistemically governed developmental evolvability:** a persistent heterogeneous cognitive machine converts verified task experience and verified self-interventions into explicit, revisable causal knowledge about both the world and its own cognition; that accumulated structure causally reduces the information and search required for later learning and later self-change, while exact provenance/scope/revocation and an external non-self-certifying adoption boundary remain intact.

Even this may be parent-sufficient.

The decisive comparison is against a strongest product containing, where feasible:

```text
persistent memory
+ learned self-model
+ active diagnosis
+ AutoML/program repair
+ reflective credit assignment
+ open-ended archive
+ learned abstraction/library induction
+ neural/Transformer adaptation
+ same external checker/tools.
```

If that product reproduces the developmental frontier:

```text
PARENT_PRODUCT_SUFFICIENT
```

is the correct result.

---

# 18. Synthetic V0.2 summary

All results are E2 synthetic theory pressure.

## 18.1 Diagnosis cost phase boundary

Example:

```text
noise 0.05, probe cost 0.05:
blind/guided cost ratio = 1.584
guided accuracy          = 0.865

noise 0.05, probe cost 0.80:
blind/guided cost ratio = 0.587
```

Cheap informative diagnosis helps; expensive diagnosis loses.

## 18.2 Factorization/coupling

High-budget evolutionary parent, 24 generations:

```text
K=1 stable:
factor quality = 0.968
evo quality    = 0.976
factor cost    = 321.5
evo cost       = 1152

K=5 stable:
factor quality = 0.879
evo quality    = 0.908
factor cost    = 409.5
evo cost       = 1152
```

Sparse coupling preserves near-parent quality at much lower evaluation-equivalent cost; dense coupling produces a material quality gap.

Approximately matched-cost parent:

```text
K=2 stable:
factor quality = 0.964 at cost 386
evo quality    = 0.891 at cost 432
```

No strongest-parent closure is claimed.

## 18.3 Self-intervention learning

Resolved self-interventions strongly reduce later fault search, but the direct probabilistic parent closes or beats the explicit self-graph, especially for unseen multi-fault composition.

## 18.4 Stepping stones

Strict monotonic local search is trapped.
A shadow archive improves reachability.
A broader ordinary search parent dominates the naive archive.

Thus every positive synthetic mechanism has already received a negative/parent boundary in the same harness.

---

# 19. Direct implications for #149

Current #149 has:

```text
g0 → g1 → g2 → g2
```

and `AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION`.

V0.2 says the next goal is **not** merely to force `g3`.

Instead measure why generation 3 fails along the triad:

```text
Was κ too high?
Was Ω too low?
Was χ too high?
Was the candidate language missing?
Was a stepping-stone path required?
Did maintenance dominate?
```

A failure becomes useful training evidence only if it changes the future diagnosis/proposal distribution.

New #149 measurements should include:
- posterior uncertainty over responsible layer;
- expected/realized information gain for probes;
- candidate-space entropy/count before/after diagnosis;
- true affected closure after independent verification;
- learned-vs-supplied causal structure;
- how previous self-change history altered current diagnosis/search.

---

# 20. Direct implications for #151

Every developmental transition should ask two questions.

## Capability transfer

```text
Did prior development make the new domain cheaper to learn?
```

## Evolvability transfer

```text
Did prior development make the machine easier to diagnose, reorganize or extend?
```

A game or math task can be valuable even if its direct skill never transfers to language if it teaches a reusable acquisition/diagnosis/representation strategy.

Conversely, no developmental credit is given merely because the curriculum was chronologically cumulative.

---

# 21. Required real experiments

## EV2-E1 — Real self-identifiability assay

Use actual OCM failures, not generator labels.

For each incident:
- freeze latent external diagnosis only for scoring;
- expose only real traces/outcomes;
- enumerate allowed probes;
- estimate information gain and cost;
- measure `B_id(ε)` and residual uncertainty.

Compare:
- OCM self-model;
- Bayesian active diagnosis;
- direct empirical memory;
- learned classifier;
- reflection agent.

## EV2-E2 — Learned self-causal graph

Across disjoint resolved incidents:
- predict consequences of held-out component interventions;
- predict unseen combinations;
- distinguish main effects/redundancy/synergy;
- persist/restart;
- use predictions to reduce future diagnosis/search.

Ablate the learned self-model.

## EV2-E3 — Repair-search entropy

After matched diagnosis evidence:
- enumerate or estimate the admissible candidate distribution;
- measure `χ`;
- compare OCM proposal policy with BO/AutoML/program-repair/evolutionary/neural proposal parents.

## EV2-E4 — Shadow developmental lineages

Keep deployed OCM unchanged.

Allow sandboxed non-deployed descendants.
Test whether a useful descendant requires an intermediate that would have failed immediate adoption.

Compare DGM/open-ended and ordinary broader-search parents.

## EV2-E5 — Developmental curriculum value

Across #151 stages, compare:
- immediate-performance curriculum;
- random curriculum;
- novelty/learning-progress curriculum;
- information-gain/overhypothesis curriculum;
- OCM developmental policy.

Primary endpoint:
future matched-threshold acquisition cost, not curriculum reward.

## EV2-E6 — Full triad trajectory

Across multiple stages measure:

```text
(Q, κ, Ω, χ, C_acquire, C_evolve)
```

and test whether earlier development causally changes later evolvability.

---

# 22. Kill rules

Positive theory is killed or narrowed by any of:

```text
SELF_IDENTIFIABILITY_TOO_LOW
DIAGNOSTIC_COST_DOMINATES
REPAIR_SEARCH_ENTROPY_DOMINATES
DENSE_COUPLING_PARENT_DOMINATES
STRUCTURAL_DRIFT_DOMINATES
SELF_MODEL_PARENT_SUFFICIENT
ACTIVE_DIAGNOSIS_PARENT_SUFFICIENT
MARS_CREDIT_ASSIGNMENT_SUFFICIENT
DGM_OPEN_ENDED_SEARCH_SUFFICIENT
AUTOML_REPAIR_SUFFICIENT
NO_DEVELOPMENTAL_EVOLVABILITY_TREND
NO_CROSS_DOMAIN_EVOLVABILITY_TRANSFER
SHADOW_ARCHIVE_NO_VALUE
PARENT_PRODUCT_SUFFICIENT
CANNOT_CHECK_<reason>
```

Positive scoped terminals may include:

```text
SELF_IDENTIFIABILITY_LEARNED_AT_SCOPE
DEVELOPMENTAL_EVOLVABILITY_SUPPORTED_AT_SCOPE
SELF_CHANGE_COST_AMORTIZATION_SUPPORTED
CROSS_DOMAIN_META_METHOD_TRANSFER_SUPPORTED
TRIAD_PHASE_BOUNDARY_SUPPORTED
```

No positive terminal implies AGI, universal recursive self-improvement or neural inferiority.

---

# 23. Theory-level completion criterion

This research pass is complete when the programme stops asking:

```text
"Can OCM modify itself?"
```

and instead tests:

```text
"Does developmental experience make future cognition and future self-modification
more local, more identifiable and more searchable at matched capability and total cost?"
```

That is the V0.2 central question.

The eventual field-level result may be:
- positive developmental evolvability;
- a phase diagram showing where it exists;
- strongest-parent sufficiency;
- or an impossibility/maintenance boundary.

All are scientifically successful outcomes.
