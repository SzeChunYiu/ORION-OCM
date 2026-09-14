# GMI #602 formal-gap closure V2

Status: **NORMATIVE FORMAL SUPPLEMENT**  
Date: 2026-09-14.  
Authority: #602 under #233/#373. Read with `GMI_602_PARENT_ATLAS_AND_FORMAL_CLOSURE_V1.md` and `GMI_602_PARENT_ATLAS_AMENDMENTS_V1.md`.

## 0. Purpose

The first spine closed the generic quotient/resource/causal/domain/statistical limits. A direct cross-check against the unchecked #602 ledger exposed additional theorem-shaped rows that deserved explicit derivations rather than section-level summaries.

This supplement supplies those derivations. It does **not** turn prospective, neutral-search, real-scale, cross-species, statistical-power, or physical-metering obligations into formal theorems.

The parent-first rule remains:

```text
strongest matched parent theorem/mechanism
-> instantiate assumptions on the registered GMI object
-> subtract everything the parent already owns
-> keep only morphology/resource/development residual
-> otherwise PARENT_SUFFICIENT
```

---

# T602-24 — residual external-memory / absorption lifecycle theorem [P1]

Let protected target state be `S_O`, already-internal state be `P`, and optional external residual state be `R`.

Exact target sufficiency through the split state is equivalent to factorization

\[
S_O=g(P,R)
\]

on the registered support. If there exist two target states inside the same `(P,R)` fiber, exact obligation satisfaction from that state is impossible. T602-02 gives the corresponding residual-cardinality/information lower bound.

Now freeze a horizon with:

- `q` target queries/uses;
- `u` knowledge-changing updates;
- one-time external build/index/storage cost `K_ext`;
- per-query external retrieval+verification cost `c_ext`;
- external update cost `a_ext`;
- one-time internal absorption/build cost `K_abs`;
- per-query internal serving cost `c_abs`;
- absorbed-state update/retraining/reverification cost `a_abs`.

Under additive stable charges, total burdens are

\[
C_{ext}=K_{ext}+q c_{ext}+u a_{ext},
\]

\[
C_{abs}=K_{abs}+q c_{abs}+u a_{abs}.
\]

External residual memory is lifecycle-cheaper exactly when

\[
K_{ext}-K_{abs}+q(c_{ext}-c_{abs})+u(a_{ext}-a_{abs})<0.
\]

This is a bookkeeping identity, not an RAG novelty theorem.

### Index threshold

If unindexed scan costs `s` per lookup, indexed lookup costs `i<s`, and index construction costs `B`, then indexing is strictly cheaper over `q` lookups iff

\[
B+qi<qs
\iff
q>\frac{B}{s-i}.
\]

With integer `q`, the first winning lookup count is `floor(B/(s-i))+1` when the quotient is not already an integer equality case; exact comparison should be made directly at the boundary.

### Drift/update consequence

High update rate `u` favors whichever representation has lower *verified* revision burden, not automatically external memory. High query reuse `q` favors low serving cost. A static “external vs parametric” verdict without `(q,u)` is therefore under-specified.

### Parent subtraction

Databases, indexes, caches, IR/kNN, RAG, model editing, adapters and amortized-analysis parents own the mechanisms. The residual GMI claim can only be a prospectively verified common ecology/resource phase law or a target quotient not already supplied by those parents.

### #602 rows formally addressed

B12 predictive-target residual quotient; external-memory vs absorption condition; retrieval/index frequency law; changing-knowledge update law; parent comparison. **Neutral recovery remains P4.**

---

# T602-25 — common learning/update object and specialization theorem [P1 definition + parent reduction]

Let developmental state be

\[
z_t=(M_t,\theta_t,A_t,H_t),
\]

where `M_t` is morphology, `θ_t` mutable parameters/state, `A_t` auxiliary retained structures (examples, rules, populations, libraries, optimizer state, etc.), and `H_t` registered history.

A common update law is a Markov kernel

\[
U_t(\cdot\mid z_t,e_t,v_t,R_t,E_t),
\]

from current developmental state, acquired evidence `e_t`, verifier/feedback `v_t`, resources `R_t` and ecology `E_t` to a distribution over `z_{t+1}`. Deterministic updates are degenerate kernels.

This object is intentionally more general than parameter optimization: `M_{t+1}` may differ from `M_t` when morphology change is legal.

## 25.1 Parent-owned specializations

Each familiar learning law is a restriction of the common transition object, not a new GMI mechanism:

| specialization | restricted state/update structure | parent owns |
|---|---|---|
| gradient descent / backprop | numeric differentiable `θ`; update uses local derivative/adjoint | smooth optimization + AD/backprop |
| Bayesian updating | `θ` is a probability law/model state; update is conditioning/approximate inference | Bayesian statistics / probabilistic programming |
| exemplar insertion / nearest neighbor | `A` retains labeled/evaluated instances; query uses metric/index | nonparametric learning / IR / databases |
| symbolic rule induction | `A` is rule/hypothesis structure changed by counterexamples/evidence | symbolic learning / ILP / production/rewrite parents |
| program/library learning | `A` is program/library; update searches and retains reusable code | program synthesis / DreamCoder/Stitch/GP/OOPS-like parents |
| evolutionary update | `A` is population; update is variation-selection-recombination kernel | evolutionary computation / population genetics |
| learned optimizer/meta-learning | parameters of `U` are themselves adapted across tasks | meta-learning / learned-optimizer / meta-RL parents |
| self-modification/morphology change | transition may alter `M` or `U` subject to verifier/governance | self-improvement / NAS / morphogenesis / governed self-change parents |

## 25.2 Conditional selection law

For a frozen admissible law set `mathcal U`, horizon and full lifecycle loss `L`, a law is selected only conditionally:

\[
U^*\in\arg\min_{U\in\mathcal U}E[L(U)\mid E,R,V,H].
\]

T602-08 blocks a universally best law over unrestricted problem classes. Therefore the formal conclusion of #602 C is **not** one update rule. It is an ecology/feedback/resource-conditioned parent-selection problem.

## 25.3 What formal derivation cannot close

A formal specialization does not establish that a low-level neutral grammar will rediscover that law, nor that a new held-out ecology will select it. Those are separate reachability/prospective P4 gates.

### #602 rows formally addressed

C common update object; gradient/backprop/Bayes/exemplar/rule/program/evolution/meta/self-modification specializations; resource-optimality target; negative-ecology requirement typed as empirical/countermodel; universal-best-law claim terminated by P5. Neutral rediscovery and held-out law prediction remain P4.

---

# T602-26 — developmental reachability, local barrier and encoding invariance [P1]

Fix a registered developmental/search process with state space `Z` and conditional transition kernel `K_t(z'|h_t)`, where `h_t` is the reachable history through time `t`.

## 26.1 Reachability

A target set `A subseteq Z` is reachable by time `T` iff there exists a legal history

\[
z_0,z_1,\ldots,z_T
\]

with `z_T in A` and strictly positive product of the registered conditional transition probabilities along that path (or legal positive-weight edges in a nondeterministic support graph).

If no positive-support path exists at any finite time, `A` is globally unreachable under that developmental law even when `A` is expressible by the grammar.

## 26.2 Local barrier vs global impossibility

Let a local selector accept a transition only when registered score decrease is at most `beta` (with `beta=0` for strictly monotone improvement). A **local barrier** exists when a positive-support path to `A` exists but every such path contains at least one transition whose score decrease exceeds `beta`. The target is globally reachable but unreachable by that selector.

Adding a developmental operator restores reachability exactly when it adds at least one legal positive-support path satisfying the selector's acceptance constraints.

## 26.3 Encoding/search invariance

Let encodings `phi:Z -> Z'` be bijective. Two search processes are encoding-equivalent when the second kernel is the pushforward of the first:

\[
K'_t(\phi(z')\mid\phi(h_t))=K_t(z'\mid h_t)
\]

for every reachable history. Then hitting-time distributions of corresponding target sets are identical. A change of names alone cannot change reachability.

If instead, at each corresponding not-yet-hit history, the proposal kernels have total-variation distance at most `delta_t`, a stepwise maximal coupling gives for any event determined by the first `T` transitions

\[
|P_K(A_T)-P_{K'}(A_T)|\le\min(1,\sum_{t=1}^T\delta_t).
\]

Thus search/encoding dependence is measurable. A search result cannot be called ecology-determined when the observed morphology distribution moves materially under matched encodings/searchers without a theory-predicted reason.

## 26.4 Search burden

Full search burden includes every failed proposal, evaluation, verification and repair event before the accepted target. Reporting only accepted-candidate cost biases morphology comparisons toward search-heavy representations.

### #602 rows formally addressed

E formal reachability; search burden; representability vs reachability; local barriers vs global impossibility; sufficient restoration by added operators; search/encoding dependence; search-negative terminal. Cross-search/grammar neutral recoveries remain P4/P2 evidence.

---

# T602-27 — hybrid solver routing, verification and fallback theorem [P1]

Let task/context be `x`, candidate solvers be `s in S`, and total verified loss of choosing solver `s` be `ell_s(x)` including execution, communication and task loss. Let routing overhead be `r(x)`.

An oracle hybrid with access to exactly the registered routing information has expected serving loss

\[
E[r(x)+\min_{s\in S}\ell_s(x)].
\]

A monolith `m` has `E[ell_m(x)]`. After one-time build/maintenance differences are amortized on the same horizon, heterogeneous routing dominates exactly when its full total is lower. Heterogeneity alone is neither necessary nor sufficient.

## 27.1 Failure-aware verifier gate

Suppose a primary solver costs `c_p`, fails with probability `f`, undetected failure has loss `L`, a verifier costs `v`, detects a true failure with probability `d`, and a detected failure invokes a correct fallback costing `b` (all quantities registered on the same loss/cost scale).

Without verification:

\[
C_0=c_p+fL.
\]

With verifier and fallback:

\[
C_V=c_p+v+f[d b+(1-d)L].
\]

Verification/fallback is strictly beneficial iff

\[
v<f d(L-b).
\]

If fallback is itself fallible, replace `b` by its complete expected verified loss. False-positive verification costs must likewise be added; the simple inequality is the clean special case.

## 27.2 Hybrid vs distinct domain

If router + solvers + verifier compile into registered existing domains with bounded lifecycle overhead, the hybrid is composition, not a new domain/species. Distinct-domain wording requires the T602-15 reduction gate.

### #602 rows formally addressed

B20 heterogeneous-solver dominance; routing/verification cost; failure-aware fallback; verifier-gated admission; hybrid composition-vs-domain criterion. Neuro-symbolic/statistical-symbolic mechanisms remain parent-owned unless residual survives.

---

# T602-28 — capability interaction calculus [P1]

Let `V(S)` be a higher-is-better protected value obtained with capability/component set `S`, after charging the registered resource costs. For components `A,B`, define second-order interaction

\[
I(A,B)=V(\{A,B\})-V(\{A\})-V(\{B\})+V(\varnothing).
\]

Then:

```text
I > 0  superadditive/complementary at the registered scope
I = 0  additive at that scope
I < 0  interference/substitution at that scope
```

No sign follows from the component names (T602-10).

## 28.1 Parent reductions for every #602 F3 pair

| interaction row | strongest formal reduction |
|---|---|
| memory × planning | value of retained information/state for future decision; memory helps only if it changes a future action/value enough to pay |
| memory × abstraction | sufficient compression: abstraction helps memory only if required obligation distinctions survive and saved state/serving burden exceeds abstraction cost |
| search × learned heuristic | value of computation: verified expansions/work removed must exceed heuristic acquisition/evaluation cost |
| social model × communication | model is useful only if its information changes message/action policy enough to exceed modeling/communication burden |
| communication × teaching | machine-teaching/signaling value: transmitted evidence must reduce receiver burden enough to exceed sender/channel/verification cost |
| teaching × culture | T602-05 amortization across recipients/generations; cumulative retention wins only above reuse/maintenance threshold |
| metacognition × resource allocation | rational metareasoning/value-of-computation minus introspection/allocation overhead |
| causal model × planning | causal information has value only where interventions/actions distinguish plans not equivalent under observational prediction |
| tool routing × verification | T602-27 verifier/fallback value and routing-selection burden |

Superadditive thresholds are therefore **derived conditions on shared information/search/resource structure**, not a universal promise that combining capabilities creates emergence. Interference is expected whenever shared budgets, incompatible representations, routing errors or maintenance costs dominate.

### #602 rows formally addressed

All named F3 interaction rows receive an exact common interaction quantity and strongest-parent reduction. Quantitative signs/thresholds in new worlds remain P2/P4 evidence.

---

# T602-29 — capability-predictor sufficiency and abstention theorem [P1]

Let architecture-name-free registered descriptor be

\[
\phi(M,E,R,H)
\]

and protected capability vector be `C(M,E,R,H)`.

An exact deterministic capability predictor using only `phi` exists **iff** capability is constant on every descriptor fiber:

\[
\phi(x_1)=\phi(x_2)\Rightarrow C(x_1)=C(x_2).
\]

Equivalently there exists `g` with `C=g circ phi`.

**Proof.** Same fiber/factorization proof as T602-17. ∎

For metric capability space, an `epsilon`-accurate deterministic predictor exists on a fiber only if that fiber's target values fit inside an `epsilon`-radius ball around some prediction. If no such ball exists, the descriptor is insufficient at that tolerance.

Therefore a calibrated predictor must either:

1. refine `phi` using information available under the registered contract;
2. output a set/distribution/uncertainty region justified by a statistical parent; or
3. abstain `CANNOT_IDENTIFY`.

Resource repricing, ablation and environmental drift are prospective inputs to `phi`; they cannot be treated post hoc after capability outcomes are seen.

### #602 rows formally addressed

F4 architecture-independent descriptor sufficiency; failure-mode identifiability; uncertainty/abstention; repricing/ablation/drift as registered predictor inputs. Held-family/real-regime success remains P4.

---

# T602-30 — machine-species ecology formalization [P1 definitions + conditional consequences]

Use corrected T602-13/C602-13. A **species** at registered scope `(Omega,K)` is an equivalence class under bounded mutual capability/development-preserving compilation.

## 30.1 Variation and distance

Within-species variation is variation among representatives inside one equivalence class. Between-species distance requires a prospectively declared metric/pseudometric on quotient descriptors; no unique natural scalar distance exists without weights or operational probes.

Substrate/compiler change preserves species exactly when it stays inside the equivalence class at the registered burden class.

A **speciation event** occurs only when a developmental lineage crosses into a non-equivalent class under the frozen reduction relation. Parameter drift inside one class is not speciation.

## 30.2 Niche and coexistence

For species `s`, define its niche

\[
N_s=\{(E,R,H):s\text{ has an admissible Pareto-undominated representative}\}.
\]

Multiple species can coexist on the morphology frontier at a condition iff at least two non-equivalent classes are simultaneously undominated there. This is frontier coexistence, not yet a population-frequency theorem.

## 30.3 Competitive exclusion and resource partition

If every admissible representative of species `t` is strictly Pareto-dominated by some representative of species `s` throughout the registered condition set, and the population/selection dynamics admit no frequency-dependent or protected niche effect, then `t` cannot be selected as a resource optimum. Any observed persistence requires an omitted resource, switching/history cost, frequency dependence, constraint or stochastic/dynamic mechanism.

Resource partitioning corresponds to different species occupying different undominated regions because their cost/capability vectors cross as resource prices/budgets/ecologies vary.

## 30.4 Symbiosis/hybridization

Species `a,b` are symbiotic at a registered condition when a joint composition achieves protected value/resource points unattainable by either alone and the joint gain exceeds communication/routing/maintenance cost. If the composite remains boundedly reducible to ordinary composition of `a,b`, it is a hybrid/composite, not automatically a third species.

## 30.5 Invasion, abundance and extinction require population dynamics

For a declared population dynamic such as replicator dynamics with fitness `F_s(p,E)`, a rare type `j` can invade resident `i` when

\[
F_j(e_i,E)>F_i(e_i,E).
\]

Persistent negative relative fitness implies local exclusion/extinction under that dynamic; equality/feedback can permit coexistence.

**Crucial limit:** species abundance/frequency, invasion speed and extinction cannot be derived from morphology descriptors alone. They require a population/selection dynamic, mutation/input process and interaction structure. Without those, the #602 abundance/invasion rows are underdetermined, not missing algebra.

### #602 rows formally addressed

G equivalence, within/between variation, compiler/substrate identity, speciation, hybridization, niche, coexistence, exclusion, symbiosis, resource partition, invasion/extinction conditions. Exact multi-species microscopes and abundance predictions remain P2/P4 after a population dynamic is registered.

---

# T602-31 — development, inheritance, reset, expansion and finite-state open-endedness [P1/P5]

Let current competence be `Cap(z,E)` and future acquisition/search burden on a future-task distribution `D` be `B(z;D)`. These are distinct objects: equal current competence does not imply equal future burden.

## 31.1 Optional inheritance monotonicity

Suppose a descendant receiving inherited structure `h` may discard/ignore it at **zero** extra cost and can exactly reproduce every no-inheritance strategy. Then optimal future burden with optional inheritance cannot exceed the no-inheritance optimum:

\[
B^*_{with\ optional\ h}\le B^*_{without\ h}.
\]

**Proof.** The inherited system can choose the no-inheritance strategy. ∎

This monotonicity fails when maintenance, routing, interference, verification, switching or reset has unavoidable positive cost. Thus “inheritance cannot hurt” is only true under an explicit free-ignore option.

## 31.2 Negative transfer and reset

Let continued-development cost be

\[
C_{cont}=K_{maint}+B(h;D)
\]

and reset cost

\[
C_{reset}=K_{reset}+B(\varnothing;D).
\]

Reset is cheaper exactly when `C_reset<C_cont`. Negative transfer is the region where inherited structure raises complete future burden after all reuse benefits are counted.

## 31.3 Expansion and pruning

For candidate expansion `a`, let discounted/finite-horizon protected benefit be `G_a` and full build/maintenance/revision burden be `K_a`. Expansion is lifecycle-beneficial iff `G_a>K_a` under the frozen value/price model and hard constraints.

For retained structure `r`, pruning is beneficial when its expected future contribution to protected value/search reduction is smaller than its maintenance, interference, routing and revision burden, after including switching cost.

Self-compilation is T602-05 applied to a retained transformation that reduces repeated future search/serve burden.

## 31.4 Learned representation/operator/search-prior value

A learned representation, operator or search prior makes future acquisition cheaper **only** if the complete expected future burden decreases on tasks not already solved merely by replaying stored answers. Warm-start reuse and acquisition improvement must therefore be measured separately.

## 31.5 Finite closed-system open-endedness limit [P5]

A deterministic developmental system with a finite joint internal+environment state space and time-homogeneous transition must eventually enter a cycle. It cannot generate an unbounded sequence of pairwise distinct joint states.

**Proof.** Pigeonhole principle on the finite joint state space. Once a state repeats under a deterministic time-homogeneous transition, all future states repeat periodically. ∎

This does **not** rule out open-ended behavior when the registered system receives unbounded external information, has expanding memory/state space, stochastic innovation with an unbounded support, changing transition laws, or a growing environment. Those mechanisms must be charged and stated.

### #602 rows formally addressed

H competence vs future potential; adaptation/search burden; inheritance monotonicity scope; maintenance reversal; representation/operator/search-prior transfer; negative transfer/reset; expansion/pruning; self-compilation; finite-state open-endedness limit. Prospective future-task and multi-generation validations remain P4.

---

# T602-32 — global statistical-validity and uncertainty propagation rules [P1/P3]

## 32.1 Finite global good event without independence

For registered events `G_1,...,G_m` with valid marginal failure bounds

\[
P(G_i^c)\le\delta_i,
\]

Boole's/union bound gives

\[
P(\cap_i G_i)\ge 1-\sum_i\delta_i
\]

**without requiring independence**.

This closes repeated-row validity only when each row's stated bound remains valid under the way that row was selected/generated.

## 32.2 Adaptive row creation

If a hypothesis/row is created after inspecting the same protected data used for its nominal fixed-hypothesis bound, the original bound need not remain valid. Valid routes include, depending on assumptions:

- fresh protected data;
- simultaneously valid uniform bounds over the whole predeclared class;
- confidence sequences/anytime-valid tests/e-values;
- differential-privacy/reusable-holdout style adaptive guarantees;
- explicit alpha/error spending whose per-step guarantees remain valid under the filtration.

Merely applying a union bound to invalid post-selection p-values/confidence intervals does not repair adaptivity.

## 32.3 Unlimited horizon

If at each time `t` an anytime/adaptively valid failure event satisfies the required conditional/marginal guarantee and a prospectively chosen spending sequence obeys

\[
\sum_{t=1}^{\infty}\delta_t\le\delta,
\]

then the union bound yields probability at least `1-delta` that none of those failures ever occurs. If no such sequential guarantee/spending construction is supplied, unlimited-horizon validity is not earned.

## 32.4 Epistemic vs aleatoric uncertainty

Aleatoric uncertainty is variability remaining under the registered data-generating law even with its parameters known; epistemic uncertainty is uncertainty over the law/parameters/model because available information is insufficient. The decomposition is model-dependent and must name the model class.

## 32.5 Deterministic propagation bound

If downstream map `f` is `L`-Lipschitz on the registered region, input uncertainty has radius `r`, and approximation/model error is bounded by `e`, then downstream error is bounded by

\[
Lr+e.
\]

Composition repeats this rule with the relevant local Lipschitz constants; without regularity, small upstream uncertainty need not remain small.

When T602-29 fiber identifiability fails, uncertainty calibration cannot manufacture the missing information: output must widen or abstain.

### #602 rows formally addressed

M repeated rows; adaptive row creation; unlimited-horizon boundary; dependence without hidden independence; one global good event; epistemic/aleatoric distinction; composition/update propagation; abstention. Numerical calibration remains P3/P4 evidence.

---

# T602-33 — scaling, bottlenecks and finite phase-boundary semantics [P1/P5]

## 33.1 Finite resource phase boundary

For two admissible morphologies with prospectively defined cost/value surfaces `C_1(x),C_2(x)` over registered scalar control `x`, a pairwise crossover occurs at a root of

\[
C_1(x)-C_2(x)=0
\]

with an ordering change across the root. For vector costs, a frontier transition occurs when Pareto dominance/feasibility changes; scalar equality is not required.

This is a finite morphology **selection boundary**. It need not be a thermodynamic/nonanalytic phase transition.

## 33.2 Bottleneck/reachability threshold

If capability requires resource lower bound `L(n)` and available resource is `R(n)`, capability is impossible wherever `R(n)<L(n)`. Crossing `R(n)>=L(n)` makes the capability *admissible*, not necessarily reachable or selected. Search/development gates remain separate.

## 33.3 Saturation

A registered performance quantity saturates only relative to a declared ceiling/model, e.g. when further resource increase cannot improve the protected optimum beyond tolerance `epsilon`. Apparent empirical flattening over a finite interval is not by itself a saturation theorem.

## 33.4 Smooth scaling vs phase transition

Finite observations cannot establish a universal nonanalytic transition or unique out-of-range scaling law (T602-20/C602-20). The theory must preregister the candidate function/regularity class and the operational definition of “phase.”

## 33.5 Finite-size corrections

If an asymptotic/structural law `f(n)` is proposed, define residual correction `r(n)=y(n)-f(n)` and freeze a bound/rate/model for `r` before extrapolation. Saying “finite-size effects” after a miss is not a closure condition.

### #602 rows formally addressed

U quantities-to-scale must be tied to explicit resource/lower-bound objects; saturation/bottleneck; smooth-vs-phase distinction; capability resource thresholds; finite-size correction registration; extrapolation limit. Preservation of sign/order at larger scale is empirical P4.

---

# 11. Formal status of remaining #602 sections after T602-24..33

The issue contains many unchecked rows because it mixes theorem work, exact certificates, infrastructure and prospective science. After the formal supplements, the remaining gap types are:

| section | formal closure now supplied | what **cannot** be closed by derivation alone |
|---|---|---|
| A | basis equivalence, universality null, compensation criterion | run complete primitive-removal census and enumerate bounded alternative bases |
| B | generic family protocol + residual memory + hybrid routing laws | held-out family/ecology predictions, neutral recovery, real sequences/tasks, selector-family experiments |
| C | common update object, parent specializations, no-universal-law limit | neutral rediscovery of multiple laws; held-out law-selection prediction |
| D | architecture-free frontier object and finite crossover semantics | execute remaining boundary-uncertainty/extrapolation experiments and real-scale replication |
| E | reachability/support, local barrier, encoding dependence, search burden | neutral cross-search/cross-grammar recovery on registered worlds |
| F | capability lower-bound logic, interaction calculus, descriptor sufficiency/abstention | quantitative held-family interaction/predictor success and real-task replication |
| G | species equivalence, niche/coexistence/exclusion/symbiosis/invasion conditional definitions | register population dynamics; run multi-species microscopes; held-out abundance/invasion predictions |
| H | evolvability burden, optional-inheritance theorem, reset/expand/prune, OEE limit | future-task and multi-generation prospective tests |
| I | including causal-alias iff theorem and active-causal parent subtraction | claim-specific empirical/real transfer only |
| J | finite-domain decidability with candidate-finiteness certificate; new-domain gate | build registry/reduction matrix, execute D1–D8 attacks and candidate tournaments/recoveries |
| K | prospective custody and parent gate | actually predict/recover an unseen form before discovery and pass reductions/replications |
| L | cross-substrate identifiability limit | biological/cognitive held-out observations and interventions |
| M | global-good-event/adaptivity/uncertainty rules | choose/validate numeric statistical procedures for each empirical programme |
| N | event-partition lifecycle accounting theorem | implement meters/counters and audit completeness on runs |
| O | evidence-class separation and theorem assumptions | independent machine-checking/certificates for individual rows where practical |
| P | terminal/falsifier schema | populate complete machine-readable registry and preserve all historical negatives |
| Q | broad parent-first atlas + amendments | maintain saturation against new/missed literature; no `ALL_PARENTS_KNOWN` theorem exists |
| R | role of exact microscopes formalized | build/execute missing exhaustive worlds and negative twins |
| S | neutral-search validity/reachability rules | execute multiple grammars/searchers/encodings with charged failures |
| T | transfer contract only | real code/proof/science/control/social experiments and resource meters |
| U | scaling/phase semantics and unrestricted-extrapolation impossibility | protected larger-scale tests |
| V | dependency-conjunction closure | every antecedent required by the requested rung must actually be green |

---

# 12. Claim ceiling after this supplement

The formal programme can now defensibly claim, subject to hostile review and green repository validation:

`GENERIC_FORMAL_GAPS_DERIVED_OR_TYPED_AS_PARENT_OWNED_EMPIRICAL_INFRASTRUCTURE_OR_IMPOSSIBLE_AT_REGISTERED_602_SCOPE`

It still cannot claim complete GMI theory closure because #602 deliberately requires P2/P3/P4 and real-transfer antecedents in addition to formal derivation.
