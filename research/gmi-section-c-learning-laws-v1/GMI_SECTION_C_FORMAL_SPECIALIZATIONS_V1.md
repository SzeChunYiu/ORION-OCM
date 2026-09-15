# GMI #602 Section C — formal learning-law specializations V1

Status: **FORMAL / PARENT-SUBTRACTION CLOSURE FOR SECTION-C SPECIALIZATION ROWS**  
Date: 2026-09-15.  
Authority: #602 Section C, building on merged PR #707 (`GMI_UPDATE_OBJECT_V1`) and the existing MIM update/credit-assignment derivations.

## 0. Claim boundary

Merged PR #707 established the common bounded update object

\[
U:(state,evidence)\to state
\]

and exhaustively showed that familiar structural update predicates occupy only a small fraction of the finite update-map space. This artifact does **not** change that object. It closes the next formal step: instantiate nine named learning/update families as restrictions/refinements of a common developmental kernel and derive the conditions under which each is admissible, cheaper, or dominated.

The following two Section-C rows remain deliberately **open empirical/prospective gates**:

1. neutral recovery of at least two qualitatively different learning laws with identity hidden;
2. prediction of the learning-law class for a held-out ecology **before** search/outcome.

Mechanism rediscovery is parent-owned and never counts as GMI novelty.

---

# 1. Common developmental update kernel

For this formal layer write developmental state

\[
z_t=(M_t,\theta_t,A_t,H_t),
\]

where `M` is morphology, `theta` mutable numeric/parametric state, `A` auxiliary retained state (examples, rules, populations, libraries, optimizer state, beliefs, etc.), and `H` registered developmental history.

A general update is a Markov kernel

\[
\mathcal U_t(dz'\mid z_t,e_t,v_t,E_t,R_t),
\]

conditioned on evidence `e`, verifier/feedback `v`, ecology `E`, and resources `R`. Deterministic updates are point-mass kernels. #707's finite total-map object is a bounded deterministic microscope of this object, not a claim that all learning is deterministic or finite-state.

A named learning law is therefore a **structural restriction** on `(z,e,v,E,R) -> z'`, not a primitive macro.

For any law family `L`, distinguish:

```text
EXPRESSIBLE_L  a legal update in the family can satisfy the obligation;
ADMISSIBLE_L   one does so within hard budgets/verifier rules;
REACHABLE_L    the declared development/search process can acquire it;
SELECTED_L     it is Pareto-undominated / scalar-optimal under frozen prices;
REPLICATED_L   the prediction survives the required disjoint test.
```

No implication to the next row is automatic.

---

# C602-02 — gradient-descent specialization [P1 + existing P2]

Let mutable state be numeric parameters `theta in R^d` and evidence induce differentiable loss `f(theta;e)`. A gradient update is the deterministic specialization

\[
\theta' = \theta-\eta\nabla f(\theta;e),
\]

with morphology and nonparameter auxiliary state unchanged unless separately declared.

If `f` is `L`-smooth, the descent lemma gives

\[
f(\theta-\eta\nabla f(\theta))
\le
f(\theta)-\eta(1-L\eta/2)\|\nabla f(\theta)\|^2
\]

for `0<eta<2/L`. Hence a locally informative differentiable channel supplies a parent-owned sufficient condition for one-step descent.

This does **not** imply global optimality, usefulness under a flat/needle landscape, or lifecycle superiority. Existing `GMI_UPDATE_LAW_DERIVATION_V1.md` already supplies an exact bounded negative/crossover: on its needle landscape gradient information returns nothing while uninformed search can hit the optimum; on its smooth microscope, charged gradient cost wins only above the measured dimension crossover.

**Strongest parents:** smooth first-order optimization; automatic differentiation/backpropagation for gradient acquisition.  
**GMI residual:** prospectively predict when gradient access and smooth local structure repay derivative/adjoint cost relative to other parent laws.

---

# C602-03 — reverse-mode / local credit-assignment specialization [P1 + existing P2]

For a differentiable computation DAG with parameters `theta in R^P` and outputs `y in R^m`, reverse-mode differentiation augments forward state by retained primal intermediates and an adjoint variable for each needed node. The update kernel therefore factors as

```text
forward evaluation -> scalar/vector protected objective
adjoint propagation on the transposed dependency graph
parameter update using accumulated adjoints.
```

Reverse mode is not a separate learning objective; it is a parent-owned mechanism for acquiring derivatives/credit. Forward mode propagates parameter-direction tangents; reverse mode propagates output cotangents.

The repository's merged `GMI_CREDIT_ASSIGNMENT_DERIVATION_V1.md` provides the required exact finite phase evidence on the same graph: reverse wins strongly for one output, but the ordering can reverse for few parameters and many outputs; therefore the correct law depends on graph topology and the number/shape of required directional derivatives, not an architecture label.

**Strongest parents:** reverse-mode automatic differentiation/backpropagation and forward-mode AD.  
**GMI residual:** cost-aware credit-assignment selection on the registered computation graph; no novelty from rediscovering backprop.

---

# C602-04 — Bayesian updating specialization [P1]

Let auxiliary state be a probability measure/density `pi_t(theta)` over a declared latent/model parameter `theta`, and evidence have declared likelihood `p(e|theta)`. If the marginal evidence probability is positive, Bayesian conditioning is the update

\[
\pi_{t+1}(\theta)
=
\frac{p(e_t\mid\theta)\pi_t(\theta)}
{\int p(e_t\mid\vartheta)\pi_t(\vartheta)d\vartheta}.
\]

For a declared loss `ell(a,theta)`, a Bayes action satisfies

\[
a^*\in\arg\min_a E_{\theta\sim\pi_{t+1}}[\ell(a,\theta)]
\]

when the minimum is attained; otherwise use the infimum / epsilon-optimal formulation.

This is a strict specialization of the common update kernel because state is restricted to a normalized probabilistic model and the evidence transition is restricted to conditioning (or a declared approximation to it).

Required assumptions are explicit: model class, prior, likelihood, support/normalization, loss, and inference approximation if exact conditioning is unavailable. Under model misspecification, posterior computation can be perfectly Bayesian relative to the wrong model and still be poor for the protected obligation.

**Strongest parents:** Bayesian inference/decision theory, probabilistic programming, Bayesian program learning.  
**GMI residual:** when a maintained belief state is obligation-sufficient and lifecycle-cheaper than counts, exemplars, direct state, or other parent representations.

---

# C602-05 — exemplar-memory specialization [P1]

Let auxiliary state be a finite multiset/database `A_t` of retained evidence records and let update be insertion (possibly with registered deletion/compaction):

\[
A_{t+1}=A_t\cup\{e_t\}.
\]

Prediction/action is produced by a registered retrieval/index rule `rho(q,A_t)` followed by an emitter. This specializes the common update object by placing learning in retained external/internal examples rather than an absorbed parametric law.

Exact obligation satisfaction requires the retrieved representation to be target-sufficient: if two admitted situations produce the same retrieval result/carried information but require different protected outputs, the exemplar scheme is insufficient regardless of storage size. Conversely, if the retrieval fiber is target-constant, an exact emitter exists.

For `N` retained records, `q` future queries and `u` updates, a generic lifecycle comparison is

\[
C_{ex}=K_{index}(N)+q\,c_{retrieve}(N)+u\,c_{insert}(N)+c_{storage}(N)+C_{verify/revision}.
\]

The scheme wins only if this vector/scalar burden beats a sufficient compressed/parametric alternative. High redundancy/reuse can make absorption cheaper; rapid drift or expensive retraining can make exemplars cheaper.

**Strongest parents:** nearest-neighbor/nonparametric learning, databases/indexes, caches, IR/RAG.  
**GMI residual:** target quotient + external-versus-absorbed lifecycle phase, not exemplar insertion itself.

---

# C602-06 — symbolic rule-induction specialization [P1]

Let auxiliary state `A_t` be a finite hypothesis/rule set `H_t` in a declared language `mathcal H`, with semantics `models(H,x)`. A rule-induction update is any update restricted to legal hypothesis transformations

\[
H_{t+1}\in\Gamma_{rule}(H_t,e_t,v_t)
\]

whose accepted result passes the registered verifier/consistency criterion. Examples include specialization/generalization, clause addition/removal, version-space refinement, or score/MDL-guided rule replacement.

The defining restriction is **discrete reusable intensional structure** plus a verifier, not a particular named induction algorithm. Exact rule state must still preserve all obligation-relevant distinctions; a compact rule theory is useful only when its repeated serving/search savings repay induction and revision cost.

A simple lifecycle condition for retained rule set `H` is

\[
K_{induce}+K_{verify}+K_{maint}
+
q c_{rule\_serve}
<
q c_{baseline}
\]

at the frozen horizon, with revision/drift costs added where present.

Negative regimes are immediate: no reusable discrete structure, high label/noise inconsistency under an exact-rule contract, rule explosion, or rapid drift can make a symbolic rule representation dominated.

**Strongest parents:** term rewriting/production systems, decision-rule learning, inductive logic/program induction, TMS/ATMS/cognitive architectures.  
**GMI residual:** obligation-derived selector/state quotient and full lifecycle frontier.

---

# C602-07 — program/library-learning specialization [P1]

Let auxiliary state be a grammar/library `L_t`. An update proposes a reusable program abstraction `ell` and installs it only after verification:

\[
L_{t+1}=L_t\cup\{\ell\}.
\]

For future tasks `i`, let verified search burden from the base library be `b_i`, and burden with `ell` be `b_i^{(ell)}` **including any larger branching/confusion cost introduced by the bigger grammar**. With acquisition/verification cost `K_ell` and maintenance/revision `M_ell`, retaining the chunk is lifecycle-beneficial exactly when

\[
\sum_i (b_i-b_i^{(\ell)}) > K_\ell+M_\ell.
\]

This is the exact amortization condition behind reusable libraries. A chunk can shorten target programs while making total search worse; compression alone is not sufficient.

**Strongest parents:** DreamCoder/library learning, Stitch/refactoring, LAPS, inductive programming, MDL, Levin/OOPS.  
**GMI residual:** prospectively predict recurrence/search geometry that makes library acquisition pay; DreamCoder/Stitch-like mechanisms themselves are parent-owned.

---

# C602-08 — evolutionary population-update specialization [P1]

Let auxiliary state be a population/distribution `Q_t` over candidates. A generic evolutionary update has three declared components:

```text
proposal/variation     q ~ Mutate/Recombine(Q_t)
measurement            fitness/protected verifier on q
selection/update       Q_{t+1}=Select(Q_t, evaluated proposals)
```

This is a specialization because learning state is a population/search distribution and evidence enters through evaluated candidate fitness/rank rather than a required analytic derivative.

If independent proposals hit a registered useful-successor set with probability `p>0` and each complete attempt costs `c`, expected first-success burden is `c/p`. More sophisticated evolution strategies adapt the proposal distribution; those mechanisms are parent-owned.

Evolutionary/black-box updates can be admissible when gradients are unavailable/unreliable or candidates are discrete. They can be dominated when an informative low-cost derivative exists and population evaluation multiplies verifier cost. Existing PowerPlay explicitly allows stochastic/evolutionary search as one implementation, further preventing mechanism-novelty claims.

**Strongest parents:** evolutionary computation, evolution strategies/CMA-ES, genetic programming, quality-diversity/NEAT, black-box optimization.  
**GMI residual:** ecology/resource prediction of when population search enters the frontier after full evaluation cost.

---

# C602-09 — meta-learning / learned-optimizer specialization [P1]

Let object-level update be parameterized by meta-state `phi`:

\[
z_{t+1}=U_{\phi}(z_t,e_t),
\]

and let cross-task/development evidence update the update rule itself:

\[
\phi_{k+1}=M(\phi_k,\mathcal D_k, v_k).
\]

This is the formal distinction between ordinary learning and **learning the update law / inductive bias**. MAML, learned optimizers and meta-RL are parent specializations of this two-timescale object.

Let meta-training/acquisition/maintenance burden be `K_meta`, and future task burdens be `b_i` without the learned meta-state and `b_i^{meta}` with it. Meta-learning pays at the registered horizon iff

\[
\sum_i (b_i-b_i^{meta}) > K_{meta},
\]

with negative transfer, reset, verification and maintenance included. Similar-task recurrence can make this true; severe distribution shift, short horizon or unavoidable maintenance can reverse it.

**Strongest parents:** MAML, learned optimizers, RL^2/meta-RL, multitask/representation learning.  
**GMI residual:** pre-outcome prediction of future verified acquisition-burden reduction under a declared task ecology.

---

# C602-10 — self-modification / morphology-update specialization [P1]

Allow the developmental transition to change morphology and/or the update law itself:

\[
(M_t,U_t,\theta_t,A_t)\to(M_{t+1},U_{t+1},\theta_{t+1},A_{t+1}).
\]

A legal self-modification must pass the registered verifier/governance boundary before adoption. Let modification `m` have acquisition/search cost `K_m`, migration cost `K_switch`, verification/safety cost `K_ver`, maintenance/revision `K_maint`, and future per-task/horizon saving `Delta_i` relative to continuing the current system. Adoption is lifecycle-beneficial only if

\[
\sum_i\Delta_i > K_m+K_{switch}+K_{ver}+K_{maint}
\]

under the frozen scalarization, or if the modified lifecycle vector is admissible/Pareto-undominated without scalarization.

Short horizon, costly migration, expensive regression verification, or harmful loss of earlier skills are exact negative regimes. If the future saving is unproved/unverified under a proof-based self-rewrite contract, adoption is not licensed.

**Strongest parents:** PowerPlay/OOPS, Goedel machines, NAS/AutoML, program transformation/self-improvement.  
**GMI residual:** resource/history prediction of *when* a self-change should be selected and whether neutral development can reach it; self-modification itself is parent-owned.

---

# C602-11 — common competitiveness theorem [P1]

For each admissible learning-law family `j`, define complete lifecycle vector over the registered horizon

\[
c_j=(acq,state,exec,update,verify,revision,comm,search,latency,failure).
\]

Hard budgets first remove infeasible laws. Without prospectively frozen prices, the only architecture-independent selection statement is Pareto/frontier membership. With frozen nonnegative price vector `w`, scalar burden is

\[
C_j=w\cdot c_j.
\]

A law `j` is uniquely scalar-optimal only if

\[
C_j<C_k\quad\forall k\ne j
\]

among admissible alternatives. If the minimum is not attained use an infimum/epsilon-optimal statement rather than inventing an optimizer.

Therefore **there is no law-name-only ordering**. Feedback type, derivative availability, uncertainty model, recurrence, drift, verifier cost, representation burden and horizon enter through the measured lifecycle vectors.

This is the exact formal meaning of “quantify when each learning law is cheaper.” Actual numerical phase locations belong to finite/prospective experiments.

---

# C602-12 — negative-ecology / losing-regime registry [P1/P2 boundary]

Each named family has a formal losing regime independent of branding:

| family | exact/structural losing condition |
|---|---|
| gradient | local derivative unavailable/uninformative/flat while another supported search can find improvement; or derivative cost exceeds saved search burden |
| reverse mode | required cotangent/output structure makes reverse traversal dearer than the matched forward/local alternative |
| Bayes | declared model/likelihood is misspecified for protected outcomes, or posterior/inference cost exceeds decision value of the uncertainty representation |
| exemplar memory | target is highly compressible/stable and storage+retrieval+verification exceeds an equivalent absorbed representation |
| symbolic rules | no compact reusable rule structure, exact-rule inconsistency/noise, rule explosion, or revision faster than reuse |
| program/library | abstraction reuse savings do not exceed acquisition/maintenance, or enlarged grammar raises search burden more than depth compression saves |
| evolutionary | informative cheap gradient/model channel exists and population evaluation/search cost dominates; or useful-successor proposal mass is effectively zero |
| meta-learning | future tasks are too few/dissimilar; unavoidable meta-state maintenance/negative transfer exceeds adaptation saving |
| self-modification | remaining horizon is too short or migration/verification/regression/revision cost exceeds future saving |

A negative ecology is scientifically useful only when it is registered before scoring if used as prospective evidence. This table is the **formal countercondition registry**; it does not itself claim those prospective experiments have run.

---

# 13. Strongest-parent register

| specialization | strongest parent families that receive first refusal |
|---|---|
| gradient | smooth first-order optimization; stochastic optimization |
| reverse credit | automatic differentiation; reverse-mode/backpropagation |
| Bayesian | Bayesian inference/decision theory; probabilistic programming; BPL |
| exemplar | nearest-neighbor/nonparametric learning; IR/indexing/cache/RAG |
| symbolic | rule learning/ILP; production systems; term rewriting; TMS/ATMS |
| program/library | DreamCoder, Stitch, LAPS, program synthesis, MDL, OOPS |
| evolutionary | ES/CMA-ES, evolutionary computation, GP, NEAT/QD |
| meta | MAML, learned optimizers, meta-RL / learned inductive biases |
| self-modification | PowerPlay/OOPS, Goedel machines, NAS/AutoML/self-improvement |

Representative anchors include: Andrychowicz et al. 2016, *Learning to learn by gradient descent by gradient descent*; Ellis/DreamCoder-family and Wong et al. 2021 PMLR 139; Bowers et al. Stitch library learning; Schmidhuber 2013 PowerPlay, DOI `10.3389/fpsyg.2013.00313`; Schmidhuber's Goedel-machine work; nearest-neighbor/nonparametric learning; Bayesian decision theory; and established evolution-strategy/CMA-ES literature.

---

# 14. #602 Section-C disposition

After this artifact and merged #707, the formal rows should be interpreted as:

```text
[x] common update object                         #707
[x] gradient specialization                      C602-02
[x] reverse/local credit specialization          C602-03
[x] Bayesian specialization                      C602-04
[x] exemplar-memory specialization               C602-05
[x] symbolic-rule specialization                 C602-06
[x] program/library specialization               C602-07
[x] evolutionary population specialization       C602-08
[x] meta-learning/learned-optimizer specialization C602-09
[x] self-modification/morphology-update specialization C602-10
[x] quantify when each is cheaper                C602-11 (formal criterion; numeric worlds remain evidence)
[x] negative ecology where each loses            C602-12 (formal counterconditions; prospective tests remain evidence)
[ ] neutral recovery of >=2 qualitatively different laws
[ ] held-out ecology -> law-class prediction before search
```

Claim ceiling:

`SECTION_C_FORMAL_SPECIALIZATIONS_PARENT_SUBTRACTED_AT_REGISTERED_V1_SCOPE`

Still forbidden:

```text
UNIVERSAL_BEST_LEARNING_LAW
SECTION_C_NEUTRAL_RECOVERY_COMPLETE
HELDOUT_LEARNING_LAW_PREDICTION_COMPLETE
COMPLETE_GMI_LEARNING_LAW_CLOSURE
```

The remaining two rows are the correct next empirical tranche rather than missing formal algebra.
