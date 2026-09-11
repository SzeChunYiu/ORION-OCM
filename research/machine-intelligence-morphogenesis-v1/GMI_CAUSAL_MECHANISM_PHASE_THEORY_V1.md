# GMI Causal Mechanism Phase Theory v1

Status: **THEORY HARDENING / FORMAL SYNTHESIS — NO NEW EMPIRICAL LAW CLAIMED**

Status date: 2026-09-12.

Refs:

- `GMI_REALIZATION_DEMAND_SIGNATURE_V0.md`
- `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`
- `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`
- `GMI_DEVELOPMENTAL_REALIZATION_PRINCIPLE_V1.md`
- `GMI_MISSING_MORPHOLOGY_PREDICTION_V1.md`
- `GMI_VLC_PREDICTION_UPDATE_V2.md`
- `GMI_PREDICTIVE_EXPERIMENT_PROGRAMME_V1.md`

This document preserves the frozen V0/V1/V2 scientific record. It does not rewrite a failed prediction after the fact. Its purpose is to state the stronger theory that the existing failure, no-go results and parent literature now require before E1-E3 can support a cross-paradigm predictive-morphogenesis claim.

---

# 0. Hostile expert lenses and parent literature

Five independent lenses are required for this hardening pass.

## L1 — mathematical foundations / identifiability

Role:

- type the scientific objects;
- distinguish observables, latent coordinates, interventions and outcomes;
- expose non-identifiability;
- state necessity/sufficiency claims only at their actual scope.

Relevant parents include causal identifiability, sufficient statistics, nonlinear ICA/disentanglement identifiability, rate-distortion and information bottleneck.

## L2 — statistical mechanics / phase theory

Role:

- distinguish a finite winner crossover from a genuine critical/asymptotic phase transition;
- require order parameters and size-scaling before importing strong phase-transition language;
- detect multicritical/interacting mechanism boundaries and hysteresis.

Relevant parents include finite-size scaling and critical-phenomena methodology.

## L3 — information / representation theory

Role:

- separate obligation information from implementation coding;
- derive lower bounds where rollback, persistence or semantic sufficiency requires recoverable information;
- prevent representation factorization from being treated as uniquely identifiable without assumptions.

## L4 — distributed systems / PL / incremental computation

Role:

- distinguish historical persistence, concurrency/version lineage, speculative validation, rollback and ordinary update rate;
- distinguish dependency tracking from physical module boundaries;
- recognize implementation-equivalent mechanisms such as shadow copies, copy-on-write, undo logs and persistent pointers.

Relevant parents include Lamport ordering, version vectors, persistent data structures, optimistic concurrency control and self-adjusting/incremental computation.

## L5 — causal inference / adversarial falsification

Role:

- require matched interventions for mechanism effects;
- separate environment-side demand from morphology-side response;
- test invariance under family/surface changes;
- construct signature collisions and negative twins before protected evaluation.

Consensus:

> The next GMI object should not be a stronger binary claim that “VLC wins.” It should be an architecture-neutral law over **which realization mechanisms become frontier-necessary, frontier-useful or frontier-dominated under a typed obligation/context**, with named morphologies treated as realizations of mechanism combinations.

---

# 1. Why V2 is not yet the final decomposition

V2 correctly separated:

```text
factorization granularity
!=
verify-before-swap versioning.
```

That correction is load-bearing and remains valid.

However, each side still contains logically independent mechanisms.

“Factorization” can refer to at least:

```text
semantic decomposition
physical/materialization partition
query composition boundaries
dependency tracking
local incremental repair
stable interfaces/routing
```

These can exist independently.

Likewise “versioning” can refer to at least:

```text
speculative candidate isolation before admission
rollback/undo information
historical-state persistence
concurrent snapshot support
branch/lineage preservation
```

These are not the same mechanism and are not driven by the same demand variables.

Therefore the next theory target is a **mechanism activation lattice**, not a binary named-morphology phase.

---

# 2. Scientific type system

The theory becomes easier to falsify if every quantity has a declared type.

Use the following types.

```text
O  obligation / semantic contract
X  obligation-side demand measurement
P  physical/resource/exogenous realization context
M  concrete morphology / realization
A  realization mechanism witness
Z  internal developmental realization state
Y  protected capability/resource outcome
G  morphogenetic search/development process
```

The allowed causal/comparison direction is conceptually:

```text
O ---> X
|      |
|      v
|    demand
|
v
semantic admissibility

P --------------------v
M ---> A ---> realization response ---> Y
^                                  
|                                  
G / search process ----------------
```

This is schematic, not a complete SCM.

The crucial prohibitions are:

```text
protected Y MUST NOT be used to define pre-outcome X;
architecture/family identity MUST NOT be smuggled into X;
morphology-specific learning response MUST NOT be called an obligation coordinate;
resource price/hardware regime MUST NOT be called semantic obligation structure.
```

---

# 3. Correct the demand/context/response boundary

## 3.1 Move `pi` out of the obligation-side signature

`GMI_REALIZATION_DEMAND_SIGNATURE_V0.md` names

\[
\Xi(\Omega)=(\sigma,\delta,\gamma,\nu,\chi,\eta,\lambda,\pi)
\]

an obligation-side object, while `pi` is explicitly a physical/resource price regime.

`GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md` already gives the correct separation:

\[
\mathcal F
=
\mathcal F(\Omega,\mathcal M_{avail},\rho,\pi).
\]

Therefore v1 theory uses:

\[
\Xi_{obl}(\Omega)
\]

for architecture-neutral obligation measurements and a separate context

\[
P=(\pi,\mathcal H,B,\ldots)
\]

for resource prices, hardware/substrate constraints and any other exogenous realization budget.

Changing `P` may move the frontier without changing the semantic obligation.

## 3.2 Split exogenous feedback from feedback utilization

The V0 `gamma` examples currently mix two types:

```text
obligation/environment-side feedback informativeness
vs
fraction of a chosen morphology's internal degrees that receive useful credit.
```

The latter is a realization response and cannot be an architecture-neutral obligation coordinate.

Define instead an exogenous feedback contract

\[
\gamma_{obl}
=
\Gamma_F(\Omega),
\]

which may describe, before choosing `M`:

```text
feedback alphabet / channel
latency
granularity
noise / calibration
counterexample or witness availability
information about registered semantic choices/actions
```

Then morphology `M` has a distinct utilization response

\[
g_M(\gamma_{obl}),
\]

measuring how efficiently its update law turns that feedback into protected improvement.

“Differentiable with respect to this architecture's parameters” belongs in `g_M`, not in `gamma_obl`, unless the obligation itself legally exposes a fixed architecture-independent derivative oracle.

## 3.3 Split retention demand from plasticity response

Likewise V0 `lambda` mixes:

```text
allowed degradation of protected old competence
```

with morphology outcomes such as:

```text
new-task acquisition rate
interference matrix
relearning burden.
```

Define the obligation-side retention contract

\[
\lambda_{obl}
=
(\mathcal K_{protected},\epsilon_{deg},T_{retain},\ldots),
\]

where the protected competencies, allowable degradation and evaluation horizon are frozen before target outcomes.

Then morphology `M` has stability/plasticity response

\[
\Lambda_M(\lambda_{obl},H_{dev}),
\]

including measured forgetting, interference, relearning burden and residual plasticity.

This distinction matters because the same strict retention obligation can be easy for one morphology and hard for another.

## 3.4 Make verifier demand and verifier integration distinct

The external verifier/admissibility contract `V` may induce architecture-neutral measurements such as:

```text
soundness / false-accept bound
completeness / false-reject behavior
witness granularity
call latency / price
which semantic sub-obligations can be checked locally
```

Call this structured object

\[
\chi_{obl}.
\]

The morphology-specific cost of presenting a locally checkable artifact, proof, test target or candidate is a response term, not part of `chi_obl`.

## 3.5 Do not assume `nu` and `eta` are independent primitives

Drift/invalidation hazard and effective reuse can be controlled separately in a synthetic world, but in many real ecologies they are causally linked.

Let `T_inv` be the random time to semantic invalidation and `N_use(t)` the useful-use counting process. Then where this model applies,

\[
\eta
=
E[N_{use}(T_{inv})].
\]

A real-data model should therefore declare whether `eta` is:

```text
an independently manipulated control,
a measured derived statistic,
or a separate reuse-intensity coordinate combined with nu.
```

Otherwise the theory can double-count the same causal pressure.

---

# 4. Split dependency locality into query and update geometry

The current scalar `delta` asks mainly how far a semantic change propagates.

That is not enough to predict factorization granularity.

Two obligations can have identical semantic state complexity and identical one-factor update cones while having opposite serving economics:

```text
World A: most queries are local to one factor.
World B: every query composes nearly all factors.
```

A fine factorization can be attractive in A and expensive in B even though update locality is identical.

Therefore replace an overloaded scalar `delta` with at least a structured dependency geometry

\[
\Delta
=
(\Delta_Q,\Delta_U,\Delta_V),
\]

where:

- `Delta_Q` — query/composition hypergraph or distribution over semantic scopes;
- `Delta_U` — intervention/update consequence geometry;
- `Delta_V` — verifier/check locality relative to those scopes when applicable.

Possible summaries include:

```text
scope-size distributions
separator profiles
cut weights
hypergraph conductance
expected descendant closure
conditional-independence structure
treewidth-like quantities
locality under legal interventions
```

No claim is made that these summaries are interchangeable. If a scalar projection is used, its information loss is part of the falsification risk.

### GMI-DQ/U collision

If two obligations match the old measured `Xi` but differ only in `Delta_Q` and reverse the preferred factor granularity, then the old signature was insufficient rather than the realization law being mysterious.

This hostile should be created deliberately.

---

# 5. Add lineage/coexistence demand: drift is not version demand

A high invalidation/update rate does not by itself imply historical versioning.

Example:

```text
A sensor estimate changes every millisecond.
Only the latest admissible estimate matters.
Old estimates may be destroyed immediately.
```

This has high drift/update rate but potentially zero historical-version obligation.

Conversely:

```text
A legal/scientific corpus changes slowly,
but past states, branches, provenance and rollback points must remain addressable for years.
```

This can have low update rate but high version-lineage demand.

Introduce a structured architecture-neutral lineage/coexistence demand

\[
\beta_{lin}.
\]

Candidate components include:

```text
maximum/expected simultaneously live semantic revisions
historical query depth
rollback window
branch coexistence requirement
provenance/lineage fidelity
concurrent-reader snapshot requirement
conflicting-update concurrency
whether old states remain semantically addressable after new admission
```

This is distinct from:

```text
nu          update/invalidation frequency
lambda_obl  retention of competence/capability
chi_obl     verification/admission structure
```

A scalar `beta_lin` is not mandatory; a structured object is safer until a sufficient compression is demonstrated.

---

# 6. Mechanism witnesses, not architecture labels

Let

\[
\phi(M)=a(M)
\]

map a concrete morphology to a vector of behaviorally measured mechanism strengths.

For the current VLC programme define at least:

```text
A1  factor/materialization partition
A2  authoritative developmental state vs derived serving-state separation
A3  dependency-tracked incremental repair / invalidation locality
A4  speculative candidate isolation before external admission
A5  historical/branch persistence after admission
A6  interface/routing semantic stability under local updates
A7  local realization heterogeneity / polymorphism
```

Use continuous strengths when possible instead of brittle booleans.

Examples:

```text
a1 = normalized partition/locality strength
a3 = 1 - ordinary update blast-radius fraction
a4 = fraction of rejectable updates for which incumbent authority stays untouched/servable until admission
a5 = fraction/depth of required historical states remaining exactly addressable
a6 = semantic interface drift under matched local content updates
a7 = diversity of internal realization classes under a common external contract
```

The witness must be behavioral/operational.

The following implementation differences must not create different mechanism labels by themselves:

```text
full shadow copy
copy-on-write
undo/redo log
persistent pointer/root swap
transactional workspace
MVCC-like version chain
```

if they satisfy the same registered semantic mechanism contract.

---

# 7. Factorization itself decomposes

V2's “factorization phase” should now be read as a family of coupled choices.

## A1 — factor/materialization partition

Question:

> At what granularity are serving/developmental artifacts materially separated for accounting and replacement?

Pressure comes from:

```text
semantic/materialization curvature in R_M
Delta_Q composition geometry
Delta_U update geometry
eta reuse
P / resource prices
```

## A3 — dependency-tracked incremental repair

Question:

> Does the machine know enough about dynamic dependence that a semantic change can trigger work proportional to the affected region rather than routine global recomputation?

A physically modular system can still fail A3 if its modules are densely invalidated.

A physically monolithic implementation can satisfy A3 if it tracks dependencies and changes only the affected computation.

Therefore:

```text
module boundaries
!=
incremental-update locality.
```

## A6 — stable composition/interface semantics

Question:

> Can local content change without silently changing unrelated composition semantics?

Stable interfaces are a separate pressure. A system can be factored yet repeatedly rewrite routing/global interface meaning, destroying local-update isolation.

---

# 8. “Versioning” decomposes into speculative isolation and persistence

## A4 — speculative candidate isolation

Definition:

> During a rejectable update, the incumbent authoritative semantic state remains recoverable/servable until the candidate satisfies the external admission rule.

This is the mechanism actually required by verify-before-adopt semantics.

It does **not** imply that arbitrary old versions remain queryable after successful adoption.

## A5 — historical/branch persistence

Definition:

> After successful transitions, multiple semantically distinct historical or branched states remain addressable for a registered period/scope.

This is driven primarily by `beta_lin`, provenance/audit/rollback obligations and concurrency semantics.

### Independence constructions

A4 without A5:

```text
build candidate in a private workspace;
validate;
atomically overwrite the incumbent;
discard all older state immediately after commit.
```

A5 without A4:

```text
append every committed state to immutable history;
apply updates immediately with no pre-admission validation gate.
```

Therefore:

\[
A4 \not\Rightarrow A5,
\qquad
A5 \not\Rightarrow A4.
\]

The label “versioned” is too coarse for the final theory unless its exact semantic contract is stated.

---

# 9. Safe-adoption information theorem

The verify-before-swap prediction can be strengthened from an architecture heuristic to an implementation-neutral information requirement.

Let:

- `S` be the set of incumbent semantic states at a registered local scope;
- `T:S->C` be the candidate-producing transformation applied before external verification;
- the verifier may reject after `T` has been evaluated;
- on rejection, the obligation requires exact restoration/continued serving of the incumbent semantic state;
- no external oracle is allowed to re-supply information for free.

Suppose an implementation applies `T` destructively and stores auxiliary rollback information `R(s)`.

For exact rollback, the map

\[
s\mapsto (T(s),R(s))
\]

must be injective over the registered state set.

Therefore for every candidate image `c`, rollback metadata must distinguish all states in the preimage

\[
T^{-1}(c).
\]

A worst-case information lower bound is

\[
\boxed{
B_{rollback}
\ge
\left\lceil
\log_2
\max_c |T^{-1}(c)|
\right\rceil
}
\]

bits, excluding information already retained elsewhere and legally available for restoration.

An average-case formulation can use conditional entropy under a frozen state/update distribution:

\[
E[B_{rollback}]
\gtrsim
H(S_{old}\mid S_{cand}).
\]

This is elementary injective-coding logic, not claimed as novel information theory.

### Consequence

GMI should predict the **necessary preservation of old-state information under rejectable destructive updates**, not “two full copies” as a universal mechanism.

Full shadow versions, logs, copy-on-write and persistent roots are competing realizations of the same requirement with different `R_M` profiles.

### Locality corollary

If a sound dependency contract proves that only semantic cone `C(u)` can change, the rollback-information obligation can often be localized to the information destroyed within that cone.

This creates a real interaction between A3 and A4:

```text
better proven locality
-> smaller affected semantic preimage
-> potentially smaller rollback / staging burden.
```

This interaction is stronger than merely adding two lifecycle cost terms.

---

# 10. State-role separation from developmental sufficiency

Let

\[
K:S_\Omega\to C_{serve}
\]

be a compiled/serving representation.

If there exist developmental semantic states `s1 != s2` such that

\[
K(s_1)=K(s_2)
\]

but some legal future intervention/development programme produces different protected future consequences from `s1` and `s2`, then `C_serve` is not a sufficient developmental state for `Omega`.

An exact admissible realization must therefore do at least one of:

```text
retain additional persistent developmental information;
reacquire the missing information through a charged/legal external process;
change the serving representation so the required distinction is preserved;
weaken the protected developmental obligation.
```

This makes VLC P2 a conditional consequence of developmental sufficiency whenever the high-throughput serving artifact is intentionally lossy relative to future developmental needs.

It does not imply that every morphology needs two named databases or two physical copies.

---

# 11. Dynamic response, path dependence and hysteresis

The V0 notation

\[
\mathcal R_M(\Xi)
\]

is useful as shorthand, but it silently assumes that current demand coordinates are sufficient for the morphology's current response.

Continual/developmental systems can violate this.

Two runs can have the same current environment-side signature but different:

```text
optimizer state
learned representation geometry
plasticity
memory occupancy
fragmentation
routing specialization
accumulated interference
historical version set
```

and therefore different future burden/frontier behavior.

Use the stronger dynamic object

\[
\mathcal R_M
\left[
\Xi_{obl,0:t},
P_{0:t},
Z_{M,0}
\right]
\to
\mathcal L(Y_{0:t},B_{0:t},Z_{M,t}).
\]

A static response

\[
\mathcal R_M(\Xi_{obl,t},P_t)
\]

is licensed only after one of the following is frozen:

```text
Markov/sufficient-state assumption;
a history summary H_M proved/validated sufficient;
reset protocol that erases relevant path dependence;
a bounded finite calibration in which history is fixed.
```

### History-collision hostile

Construct two developmental histories with matched present `Xi_obl` and `P` but different orderings of old/new tasks or revisions.

If morphology ranking reverses, a memoryless response law is insufficient.

This is not automatically a failure of GMI; it means developmental state/history belongs in the response law.

---

# 12. Causal mechanism effects

For a registered context

\[
c=(\Omega,\Xi_{obl},P,H_{dev},\mathcal M_{avail}),
\]

let `a_k` be one measured mechanism strength.

When a valid matched intervention exists, define a mechanism effect on a registered outcome coordinate `Y_j` by

\[
\Delta_{k,j}(c)
=
E[Y_j\mid do(a_k=a_k^+),c]
-
E[Y_j\mid do(a_k=a_k^-),c].
\]

This notation is aspirational unless the intervention is actually identifiable.

A valid experiment must control or meter:

```text
semantic adequacy
capacity / parameter budget
training or search budget
hidden preprocessing
resource prices
other mechanism changes induced by the intervention
```

If toggling `a_k` necessarily changes another mechanism, report the joint intervention rather than pretending to identify an atomic effect.

---

# 13. Frontier mechanism core

Named morphologies are often non-identifiable at the scientifically interesting level because different implementations can realize the same useful mechanism.

Define the registered near-frontier set

\[
\mathcal F_\epsilon(c)
\]

over semantically admissible realizations under the existing Pareto/capability rules.

For threshold `tau_k`, define mechanism `k` as **frontier-necessary at scope** when

\[
\boxed{
N_k(c)=1
\iff
\forall M\in\mathcal F_\epsilon(c),
\;a_k(M)\ge\tau_k.
}
\]

Define the **frontier mechanism core**

\[
K^*(c)
=
\bigcap_{M\in\mathcal F_\epsilon(c)}
\{k:a_k(M)\ge\tau_k\}.
\]

Define the **frontier optional shell** as mechanisms present in some but not all near-frontier realizations.

This gives GMI a stronger target than architecture selection:

> predict which mechanism invariants become unavoidable near the frontier, while allowing many source-code/architecture realizations of those invariants.

A “missing morphology” is then scientifically interesting when neutral search repeatedly discovers new realizations of a prospectively predicted mechanism core that known parent families fail to occupy efficiently at the registered scope.

---

# 14. Mechanism interactions and multicritical regions

Mechanisms need not contribute additively.

For two matched interventions on a scalarized diagnostic outcome used only when its valuation is frozen, define an interaction contrast

\[
I_{ij}
=
\Delta_{ij}-\Delta_i-\Delta_j,
\]

with the baseline term included in the usual factorial-design way.

For primary inference, retain the full outcome vector or Pareto relation instead of manufacturing a post-hoc scalar.

Expected interactions in the VLC regime include:

```text
A1 partition x A3 dependency tracking
A3 locality x A4 speculative isolation
A2 authority/serve split x eta reuse
A4 speculative isolation x chi_obl verifier latency/failure structure
A5 persistence x beta_lin lineage demand
A6 interface stability x A3 local repair
A7 heterogeneity x Delta_Q composition cost
```

The relevant “phase diagram” can therefore contain regions where:

```text
only A1 is useful;
A1+A3 are useful;
A4 is required without A5;
A5 is required without A4;
A1+A2+A3+A4+A6 jointly enter the core;
heterogeneity A7 remains optional.
```

This is a lattice of mechanism combinations, not a single switch.

---

# 15. Revised mapping of VLC P1-P6

The frozen VLC prediction remains historically valid, but its properties should be interpreted through the mechanism map.

| Frozen VLC property | Stronger mechanism interpretation |
|---|---|
| P1 sparse semantic factorization | A1 partition strength, measured separately from repair locality |
| P2 authority / serving separation | A2 developmental-sufficient authority vs derived serving state |
| P3 local rebuild / unlearning cone | A3 dependency-tracked incremental repair |
| P4 verify-before-swap versioning | primarily A4 speculative candidate isolation; A5 only if history remains addressable after adoption |
| P5 stable typed composition/routing | A6 interface/routing semantic stability |
| P6 local realization polymorphism | A7 heterogeneity |

The next prediction should target

\[
(a_1,a_2,a_3,a_4,a_5,a_6,a_7)
\]

or a reduced preregistered subset, not merely the composite label `VLC`.

---

# 16. Revised demand-to-mechanism hypotheses

The following are candidate conditional hypotheses, not established laws.

## H-A1 — partition pressure

A1 moves toward the frontier when:

```text
materialization/build curvature rises with factor size
AND Delta_U is local enough to reward separation
AND Delta_Q does not impose overwhelming cross-factor coordination
AND the reuse/resource regime repays the partition overhead.
```

High `sigma` alone does not imply a specific partition.

## H-A2 — authority/serving separation

A2 moves toward necessity when:

```text
fast serving compilation is lossy relative to future developmental sufficiency
AND serving reuse is high enough to justify compiled artifacts
AND reacquiring the lost developmental information is illegal or costly.
```

## H-A3 — incremental repair

A3 moves toward the frontier when:

```text
true update consequence sets are sparse/local
AND those dependencies are observable/trackable cheaply enough
AND updates occur often enough for avoided recomputation to repay tracking overhead.
```

## H-A4 — speculative isolation

A4 moves toward necessity/value when:

```text
candidate updates can fail admission
AND incumbent capability must remain available/unchanged before admission
AND verification has nontrivial latency/work
AND rollback/rebuild exposure is costly under lambda_obl/P.
```

The implementation may be a copy, log, checkpoint or another reversible staging mechanism.

## H-A5 — historical/branch persistence

A5 moves toward necessity when `beta_lin` requires old/branched semantic states to remain addressable.

`nu` is neither necessary nor sufficient for A5.

## H-A6 — stable interface/routing semantics

A6 moves toward value when local changes are frequent but most cross-factor semantic contracts should remain invariant; it loses value when the true obligation itself changes global composition semantics on each update.

## H-A7 — heterogeneous local realization

A7 moves toward the frontier only when local sub-obligations have materially different response optima and the savings exceed interface/routing/coordination overhead.

“Different local tasks exist” is not enough.

---

# 17. Phase terminology contract

The word “phase” is useful but can overclaim.

Use three levels.

## Level F — finite frontier crossover

A fixed finite candidate set changes winner/frontier membership as a registered control variable changes.

This is exactly what the current E0/V2 microscope establishes.

Preferred wording:

```text
finite frontier crossover
finite regime boundary
exact finite lifecycle transition
```

## Level S — scaling regime transition

A family indexed by problem/system size `n` shows a transition region whose location/width and a prospectively defined mechanism/order parameter obey a stable scaling law.

This is stronger than a finite crossover.

## Level C — critical/asymptotic phase transition

Reserve strong critical-phenomena language for an asymptotic family where a normalized response/order parameter develops a genuine limiting singularity/discontinuity or accepted finite-size scaling evidence supports such a claim.

A generic scaling ansatz might take the form

\[
m_n(x)
=
n^{-a}
F((x-x_c)n^{1/z}),
\]

with the order parameter, exponents and collapse test frozen prospectively.

No current VLC E0 result requires this stronger claim.

This terminology protects the theory: a useful finite architecture crossover is scientifically meaningful even if it is not a thermodynamic-style phase transition.

---

# 18. Signature sufficiency and identifiability

The existence of a compact `Xi_obl` is itself a falsifiable hypothesis.

Do not assume the coordinates are uniquely recoverable from observational data.

Representation-learning literature gives a direct warning: latent factorization/disentanglement is generally non-identifiable without structural assumptions, inductive bias or auxiliary/interventional information.

Therefore each demand coordinate must be one of:

```text
A. directly operationally measured from the registered obligation;
B. identified under explicit structural assumptions;
C. only identifiable up to a declared equivalence/transformation class;
D. latent/unidentified and therefore forbidden from confirmatory prediction.
```

## Operational anchor requirement

For each confirmatory coordinate `x_i`, freeze:

```text
measurement functional mu_i(Omega)
legal data available to mu_i
units / normalization
estimator and uncertainty
which interventions can move x_i
known covariance with other coordinates
failure/undefined conditions
```

## Signature sufficiency at scope

`Xi_obl` is **frontier-sufficient at registered scope** only if no admissible architecture-neutral residual description of the obligation gives material held-out improvement in predicting the registered frontier once `Xi_obl` is known.

Operationally test with:

```text
collision search
residual predictors on withheld structural features
conditional predictive-gain tests
family-held-out invariance
surface reminting
intervention twins
```

No finite experiment proves universal sufficiency; it can only support sufficiency over the registered ecology/family scope.

---

# 19. Invariance as the cross-paradigm criterion

A shared predictor should earn the word “cross-paradigm” by invariance, not by pooled accuracy alone.

Let family/environment index be `e`.

A candidate shared law should predict a response/mechanism relation that remains calibrated under family-held-out environments after family identity is removed.

Required tests should include:

```text
train/freeze on some morphology families;
test on a materially different held-out family;
remint surface labels/encodings;
change legal implementation details while preserving the mechanism contract;
verify that the same demand measurement retains the same semantic meaning.
```

If the mapping changes arbitrarily by family, the result is a portfolio of family-native theories, not a common GMI law.

This criterion follows the broader causal/invariant-prediction intuition that stable mechanisms should survive relevant environment shifts better than accidental correlates.

---

# 20. Strengthened E1 design requirements

E1 should not only ask whether hand-instantiated VLC enters the frontier.

It should contain a **mechanism factorial** or as close an approximation as the realizations permit.

At minimum create matched controls for:

```text
A1 partition only
A3 dependency tracking/local repair only
A4 speculative isolation only
A5 historical persistence only when beta_lin > 0
A1+A3
A3+A4
A1+A2+A3+A4+A6 VLC-core-like combination
```

Do not force impossible/meaningless combinations merely to complete a matrix; mark structural non-intervenability explicitly.

## New obligation twins

Add at least these hostile pairs.

### X1 — high drift, no lineage

```text
nu high
beta_lin ~ 0
old states disposable after admission
```

Prediction:

```text
A5 should not be required merely because nu is high.
A4 depends separately on admission/availability pressure.
```

### X2 — low drift, high lineage

```text
nu low
beta_lin high
past/branched states remain queryable/auditable
```

Prediction:

```text
A5 remains necessary/useful despite low nu.
```

### X3 — local update / global query

```text
Delta_U local
Delta_Q global/dense
```

Prediction:

```text
A3 can remain useful while very fine A1 factorization may lose serving advantage.
```

### X4 — global update / local query

```text
Delta_U dense
Delta_Q local
```

Prediction:

```text
fine serving partition may remain useful even when local repair advantage collapses.
```

### X5 — same present signature, different history

Matched current `Xi_obl` and `P`; different developmental task/revision order.

Prediction:

```text
if ranking differs, dynamic/history-conditioned R_M is required.
```

### X6 — implementation-equivalent safe adoption

Compare:

```text
shadow copy
copy-on-write / delta log
undo log / checkpoint
persistent-root swap
```

under the same semantic A4 contract.

Prediction:

```text
GMI should group them by mechanism while R_M predicts their resource differences.
```

If the theory predicts only the literal “two copies” encoding, it has overfit the microscope.

---

# 21. Strengthened E2 target

The current E2 target predicts burden/frontier membership from `Xi + R_M`.

Add a mechanism-level target.

For protected worlds, predict before outcomes:

\[
\widehat K^*(c)
\]

the expected frontier mechanism core and optional shell.

Score separately:

```text
mechanism-core precision/recall
frontier membership/rank
burden-vector calibration
family-held-out transfer
boundary calibration under demand interventions
```

A model can be wrong in different ways:

```text
correct cost but wrong causal mechanism;
correct mechanism but wrong resource response;
correct within-family ranking but no cross-family invariance;
correct composite VLC label for the wrong decomposed reasons.
```

These failures should not be collapsed into one AUROC.

---

# 22. Strengthened E3 neutral recovery

E3 should score the decomposed mechanisms independently before scoring the conjunction.

Post-search behavioral scoring should therefore include at least:

```text
A1 partition / materialization granularity
A2 developmental-sufficient authority vs derived serving state
A3 update work vs true affected semantic cone
A4 incumbent preservation until admission
A5 historical/branch addressability when beta_lin requires it
A6 interface/routing semantic drift under local replacement
A7 realization diversity where predicted
```

The search grammar should allow multiple implementation-equivalent realizations of A4/A5.

For example, do not make “copy checkpoint” the only cheap way to preserve rollback information; otherwise the search encoding can manufacture the predicted species.

Search-encoding tournaments should vary the low-level realization of persistence/reversibility while preserving comparable expressive power and charging description/search cost.

---

# 23. Assumption ledger

Every future theorem or experiment should name the relevant subset of these assumptions.

```text
A0  registered bounded semantic scope exists
A1  semantic adequacy/capability floor is matched before resource comparison
A2  demand measurements are pre-outcome and architecture-neutral
A3  resource/hardware context P is declared separately from obligation demand
A4  hidden external state/preprocessing is included in Z or charged
A5  mechanism witnesses are behavioral and implementation-neutral
A6  claimed mechanism intervention does not silently change protected semantics
A7  off-target mechanism changes are controlled or reported jointly
A8  candidate/search class is frozen or independently generated
A9  primary inference uses raw/Pareto outcomes unless valuation is prospectively frozen
A10 developmental history is either conditioned on or proven ignorable
A11 coordinate measurement uncertainty is propagated into boundary uncertainty
A12 multiple testing/model-selection effects are controlled on protected evaluation
A13 family labels/proxies are absent from architecture-neutral predictors
A14 search/discovery cost is charged when morphogenesis rather than normative frontier is claimed
```

A claim without the assumptions that make it true is not stronger theory.

---

# 24. New no-go / kill conditions

Add the following terminals to the theory-hardening layer.

## Type leakage

A supposed obligation coordinate requires knowing the chosen architecture's internals or observed protected performance.

```text
DEMAND_RESPONSE_TYPE_LEAKAGE
```

## Query/update geometry collision

Matched old signature, different `Delta_Q/Delta_U`, opposite frontier transition.

```text
DEPENDENCY_SIGNATURE_OVERCOMPRESSED
```

## Drift/version collision

High `nu` fails to predict lineage/persistence need once `beta_lin` is varied independently.

```text
DRIFT_IS_NOT_VERSION_DEMAND
```

## History collision

Same present `Xi_obl`, different developmental histories, different response/frontier.

```text
STATIC_RESPONSE_INSUFFICIENT__HISTORY_REQUIRED
```

## Mechanism-label overfit

Prediction succeeds only for one literal encoding of a mechanism and fails on implementation-equivalent realizations.

```text
IMPLEMENTATION_LABEL_NOT_MECHANISM_LAW
```

## Family non-invariance

The demand-to-mechanism relation requires family identity or changes meaning across families.

```text
NO_CROSS_PARADIGM_INVARIANCE
```

## Finite crossover overclaim

Only a finite candidate rank switch is shown but a critical/asymptotic phase transition is claimed.

```text
FINITE_FRONTIER_CROSSOVER_ONLY
```

These are narrowing terminals, not project failures.

---

# 25. Theory ladder

The strengthened programme should distinguish these achievement levels.

```text
T0  typed objects and architecture-neutral measurements
T1  exact finite mechanism decompositions / no-go constructions
T2  prospective mechanism-effect reversals in controlled ecologies
T3  frontier mechanism-core prediction across families
T4  neutral recovery of the predicted mechanism core
T5  invariant boundary/scaling law across disjoint ecologies and implementations
T6  lower-bound / necessity theorem for a nontrivial obligation class
T7  genuinely new realization family occupying a prospectively predicted frontier hole after parent reduction
```

The current VLC exact microscope lives primarily at T1.

Issue #419 E1-E3 is the route toward T2-T4.

No later level should be inferred automatically from an earlier one.

---

# 26. What would make GMI powerful rather than merely broad

A powerful GMI theory should eventually do all of the following at a registered scope.

## 26.1 Predict before construction

Given an obligation/context, predict mechanism pressure and frontier movement before running the protected architecture search.

## 26.2 State impossibility

Show regimes in which any semantically adequate realization lacking a mechanism must pay a lower bound or violate an obligation.

The safe-adoption information bound is a small example of this style.

## 26.3 Transfer across implementations

Predict the same mechanism need when the mechanism is realized by different low-level encodings.

## 26.4 Transfer across morphology families

Predict a shared mechanism core without architecture-family identity.

## 26.5 Explain negative cases

Predict where a mechanism should disappear from the frontier.

## 26.6 Admit non-identifiability

State when the available observations do not identify the demanded variable/mechanism rather than filling the gap with a post-hoc label.

## 26.7 Preserve multi-objective structure

Correctness, usefulness, authority/retention, resource cost and discovery burden remain distinct unless a valuation is prospectively declared.

## 26.8 Model development dynamically

Long-horizon path dependence and plasticity are part of the response law when they matter.

---

# 27. Immediate theory work before expensive E1-E3 execution

Before treating issue #419 as a test of the strongest GMI law, add/freeze the following theory artifacts or equivalent content.

## D1 — typed demand signature revision

Create a successor to V0 that:

```text
moves pi to context P;
splits gamma_obl from morphology feedback utilization;
splits lambda_obl from plasticity/interference response;
represents Delta_Q and Delta_U separately;
adds beta_lin or explicitly proves it unnecessary at the target scope;
declares primitive vs derived coordinates;
adds measurement uncertainty and undefined conditions.
```

## D2 — mechanism witness registry

Freeze behavioral measurements for A1-A7 without naming implementation classes.

## D3 — E1 hostile matrix

Add X1-X6 and matched-budget mechanism ablations.

## D4 — dynamic-response decision

Either:

```text
restrict the initial theory to reset/fixed-history worlds,
```

or freeze the history/state variables admitted into `R_M`.

## D5 — phase-language decision

Label E0/V2 as exact finite frontier crossover/calibration unless an asymptotic scaling experiment is prospectively added.

---

# 28. Literature ownership / subtraction

The following parent results constrain interpretation.

- **Locatello et al. (ICML 2019), “Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations.”** Unsupervised disentanglement is non-identifiable without inductive biases/data assumptions; GMI must not assume its latent axes are uniquely discoverable from observational data.
- **Hyvärinen, Sasaki & Turner (AISTATS 2019), “Nonlinear ICA Using Auxiliary Variables and Generalized Contrastive Learning.”** Identifiability can be recovered under explicit auxiliary-variable/conditional-independence assumptions; GMI should state analogous anchors rather than hand-wave coordinate discovery.
- **Peters, Bühlmann & Meinshausen (JRSS B 2016), “Causal inference by using invariant prediction.”** Invariance across interventions/environments motivates a stronger cross-family criterion than pooled predictive accuracy.
- **Schölkopf et al. (2021), “Towards Causal Representation Learning.”** Transfer and representation discovery are connected to causal structure, but causal variables are not simply given for free.
- **Tishby, Pereira & Bialek, “The Information Bottleneck Method.”** Representation compression vs retained task-relevant information is parent-owned; GMI should use, not rename, this mathematics.
- **Lamport (CACM 1978), “Time, Clocks, and the Ordering of Events in a Distributed System.”** Event ordering/concurrency is partial-order structure, not a scalar update-rate phenomenon.
- **Parker et al. (IEEE TSE 1983), “Detection of Mutual Inconsistency in Distributed Systems.”** Version vectors/lineage distinguish divergent replica histories; branch consistency is structurally different from mere frequency of change.
- **Driscoll, Sarnak, Sleator & Tarjan (JCSS 1989), “Making Data Structures Persistent.”** Persistence means access to old versions and has realizations/resource costs distinct from transactional staging.
- **Kung & Robinson (ACM TODS 1981), “On Optimistic Methods for Concurrency Control.”** Read/validation/write separation and private candidate copies are a parent for speculative validate-before-adopt mechanisms without implying indefinite history retention.
- **Acar et al. (2006), “An Experimental Analysis of Self-Adjusting Computation,” plus Acar's self-adjusting-computation work.** Dependency tracking/change propagation is a parent mechanism for local update work; physical modularity is not required to be the same thing.
- **Dohare et al. (Nature 2024), “Loss of plasticity in deep continual learning.”** Current task/environment conditions do not necessarily determine future learning response; developmental history can change plasticity.
- **Friedman & Meir (CoLLAs/PMLR 2026), “Data-dependent and Oracle Bounds on Forgetting in Continual Learning.”** Retention/forgetting admits model/algorithm-dependent bounds and should remain response-side when measured from a realization.
- **Fisher & Barber (PRL 1972), “Scaling Theory for Finite-Size Effects in the Critical Region.”** Strong critical-phase claims require size-scaling logic; finite rounding/crossover is not enough by itself.
- **Emmerich & Deutz (Natural Computing 2018), “A tutorial on multiobjective optimization.”** Pareto-front reasoning is parent-owned and remains the correct default when objectives conflict and preferences are not frozen.

This bibliography is subtraction, not novelty decoration.

---

# 29. Current strengthened claim ceiling

Allowed after this document alone:

> GMI has a sharper theory target: architecture-neutral obligation measurements and exogenous realization context should predict a **frontier mechanism core**, not a named architecture directly. The current VLC property vector can be decomposed into independently testable mechanisms with distinct demand drivers. Several current signature coordinates require type correction or expansion before cross-paradigm claims. Verify-before-adopt admits an implementation-neutral rollback-information lower bound, while historical persistence requires a separate lineage/coexistence obligation. Developmental response may be path-dependent and must not be assumed memoryless without a registered condition.

Not allowed after this document alone:

```text
GMI_CAUSAL_MECHANISM_LAW_ESTABLISHED
VLC_NEW_INTELLIGENCE_FORM_ESTABLISHED
UNIVERSAL_DEMAND_SIGNATURE_ESTABLISHED
CRITICAL_MORPHOLOGY_PHASE_TRANSITION_ESTABLISHED
CROSS_PARADIGM_INVARIANCE_ESTABLISHED
```

Current terminal:

```text
GMI_CAUSAL_MECHANISM_PHASE_THEORY_SPECIFIED_V1
E1_E3_REQUIRE_TYPED_MECHANISM_VALIDATION
```
