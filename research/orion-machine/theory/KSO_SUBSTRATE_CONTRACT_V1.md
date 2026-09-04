# KnowledgeSpace.v1 — mathematical substrate contract for ORION OCM

Status: **M0 FINITE MATHEMATICAL CORE — theorem/checker package. NO NOVELTY, SUPERIORITY, LANGUAGE OR FRONTIER-MATH CLAIM.**  
Umbrella: #194 · execution master: #197 · prototype/convergence owner: #284.  
Parent subtraction: `KSO_PARENT_SUBTRACTION_V1.md`.  
Executable checker: `../reference/kso_math_v1.py`.

The purpose of this contract is to replace the phrase “knowledge space” with a precise object that can be implemented, attacked and revised. It intentionally adopts parent mathematics where parents are sufficient. The research question is the coupled system, not a renamed graph, PageRank, ATMS, program algebra, sheaf or graph-rewrite formalism.

---

## 1. Object of study

At cognitive epoch `t`, the Knowledge Space is

\[
\mathcal K_t=(V_t,H_t,\tau_V,\tau_H,\Lambda_t,A_t,S_t,W_t,\mathscr F_t,\Pi_t,\mathcal P_t,\mathcal R_t).
\]

- `V_t`: finite set of **knowledge atoms**.
- `H_t`: finite set of typed **directed hyperedges**.
- `τ_V`, `τ_H`: atom and relation/operator types.
- `Λ_t`: warrant profile attached to every authority-bearing atom/edge.
- `A_t`: authority object/scope, ordered by non-amplifying composition.
- `S_t`: applicability scope and validity epoch.
- `W_t`: non-negative structural weights/costs.
- `𝓕_t`: local-context / atlas assignment and restriction data.
- `Π_t`: query-conditioned navigation operator.
- `𝓟_t`: executable procedure algebra induced by operator hyperedges.
- `𝓡_t`: resource ledger.

The cognitive machine is multi-timescale:

\[
\mathfrak M_t=(\mathcal K_t,\eta_t,\Pi_t,\mathcal C_t,\mathcal U_t,\mathcal J_t),
\]

with question atomizer `η`, navigator `Π`, composer `𝒞`, learning update `𝒰`, and governed structural rewrite / Jump mechanism `𝒥`.

A small constitutional boundary is external to the self-modifying object:

\[
\mathfrak C=(\mathsf{Check},\mathsf{Authority},\mathsf{Meter},\mathsf{Commit}).
\]

The machine may propose modifications to that boundary, but it cannot grant itself the authority to accept them.

---

## 2. Atoms and hyperedges

A knowledge atom is

\[
v=(\mathrm{id},c_v,\tau_v,\Lambda_v,A_v,S_v,e_v,\kappa_v),
\]

where `c_v` is its denotation/content, `τ_v` its registered type, `Λ_v` its warrant profile, `A_v` authority, `S_v` scope, `e_v` epoch and `κ_v` resource/provenance metadata.

Typical registered atom types include claim, procedure, constraint, representation, observation, goal, counterexample, proof, model and temporary query seed. These are an extensible type vocabulary, not a fixed ontology of intelligence.

A directed typed hyperedge is

\[
h=(T_h,O_h,r_h,\phi_h,\Lambda_h,A_h,S_h,w_h,\gamma_h),
\]

where

- `T_h ⊆ V` is a non-empty tail set (joint prerequisites),
- `O_h ⊆ V` is a non-empty head/output set,
- `r_h` is its relation/operator type,
- `φ_h` is optional executable semantics,
- `Λ_h,A_h,S_h` are warrant/authority/scope,
- `w_h≥0` is structural weight/cost,
- `γ_h` is a probability distribution over `O_h` when the edge is used for navigation.

Ordinary edges are the special case `|T_h|=|O_h|=1`. Hyperedges are required because a relation like

\[
\{a,b,c\}\longrightarrow d
\]

is not in general equivalent to three independent pairwise edges.

### Design correction: connectivity, not arbitrary density

The phrase “dense by construction” is replaced by the stronger and safer invariant

\[
\operatorname{LIVE}(v)\land \operatorname{NEW}(v)
\Rightarrow
\bigl(\operatorname{CONNECTED}_{\rm typed}(v,\mathcal K)\lor \operatorname{QUARANTINED}(v)\bigr).
\]

Global density creates spurious paths and hub noise. Newly admitted live knowledge must instead be **semantically connected by at least one live typed relation** or explicitly quarantined.

---

## 3. Warrant algebra

Let `E` be the finite universe of evidence/assumption identities. A warrant is a finite subset `W⊆E`. A profile is the antichain of inclusion-minimal sufficient warrants:

\[
P\subseteq 2^E,\qquad
\forall W,W'\in P:\; W\not\subset W' .
\]

Let `Min` remove duplicate and non-minimal sets. Define

\[
P\oplus Q = \operatorname{Min}(P\cup Q)
\]

(alternative support), and

\[
P\otimes Q
=
\operatorname{Min}\{W_P\cup W_Q:W_P\in P,W_Q\in Q\}
\]

(conjunctive support).

The additive zero and multiplicative unit are

\[
\mathbf 0=\varnothing,\qquad
\mathbf 1=\{\varnothing\}.
\]

For a revoked evidence set `R⊆E`, the exact live predicate is

\[
\ell_R(P)=1
\iff
\exists W\in P:\;W\cap R=\varnothing.
\]

If a profile is not certified complete, absence of a surviving exhibited warrant is `UNKNOWN`, not false.

### Theorem KS-T01 — idempotent warrant semiring

`(𝒜_E,⊕,⊗,0,1)`, where `𝒜_E` is the set of finite antichains over `2^E`, is a commutative idempotent semiring.

**Proof.** Associate every profile `P` with the monotone Boolean function

\[
f_P(X)=1\iff \exists W\in P:W\subseteq X.
\]

Minimal true sets of a monotone Boolean function form a unique antichain, so this map is injective and surjective onto monotone Boolean functions on `E`. Under it,

\[
f_{P\oplus Q}=f_P\lor f_Q,
\qquad
f_{P\otimes Q}=f_P\land f_Q.
\]

Boolean `∨,∧` satisfy associativity, commutativity, distributivity, idempotence of `∨`, identities `false,true`, and annihilation of `false` under `∧`; injectivity transfers all laws to antichains. ∎

The executable checker independently enumerates all 20 antichains over three evidence atoms, checks 400 ordered pairs and 8,000 ordered triples.

### Composition law

For components `x_1,…,x_n` and a bridge/operator warrant `P_b`,

\[
\Lambda(\operatorname{compose}(x_1,\dots,x_n))
=
P_b\otimes\Lambda(x_1)\otimes\cdots\otimes\Lambda(x_n).
\]

Authority and scope are non-amplifying:

\[
A_{\rm comp}\preceq A_b\wedge\bigwedge_i A_i,
\qquad
S_{\rm comp}=S_b\cap\bigcap_i S_i.
\]

This algebra is parent-owned by ATMS/provenance-style machinery; KSO adopts it.

---

## 4. Navigation is not execution

KSO separates two notions that must not be conflated.

**Navigation** asks which existing atoms are relevant to a query. It may traverse a typed higher-order relation to propagate relevance.

**Execution/firing** uses Petri-like conjunctive enabling: an executable hyperedge may fire only when every required tail is live, sufficiently activated, in scope, and the edge itself is live/authorized.

For threshold `θ_h`,

\[
\operatorname{ENABLED}_R(h,a)
\iff
\ell_R(\Lambda_h)=1
\land
\forall v\in T_h:
\ell_R(\Lambda_v)=1\land a(v)\ge \theta_h.
\]

### Theorem KS-T02 — revocation disables conjunctive firing

If any required tail atom `v∈T_h` or `h` itself becomes non-live after revocation `R`, then `ENABLED_R(h,a)=false` for every activation vector `a`.

**Proof.** `ENABLED_R` is a conjunction containing the corresponding live predicate. One false conjunct makes the conjunction false. ∎

The planted checker uses a two-tail operator, revokes one tail's sole warrant, and verifies that the edge ceases to fire.

---

## 5. Query-conditioned typed navigation

A question `x` is atomized into temporary seeds

\[
Q=\eta_c(x)=\{q_1,\ldots,q_m\},
\]

where `c` is the boundary codec. Let `s_Q` be a normalized seed distribution over `V` after the query seeds are connected to the current KSO.

For a relation type `r`, let `β_r(Q)≥0` be query-conditioned relevance. For every structural tail `v`, define the **pre-revocation denominator**

\[
D_Q(v)=\sum_{h:v\in T_h} w_h\,\beta_{r_h}(Q).
\]

Crucially, `D_Q(v)` is a property of the registered structure for this query; it is **not renormalized after revocation**.

Let

\[
g_R(x)=\mathbf 1[\ell_R(\Lambda_x)=1].
\]

Then the warranted navigation matrix is

\[
P_{Q,R}(v,u)
=
\sum_{h:\,v\in T_h,\,u\in O_h}
\frac{w_h\beta_{r_h}(Q)}{D_Q(v)}
\gamma_h(u)
\;g_R(v)g_R(h)g_R(u)
\prod_{z\in T_h}g_R(z),
\]

with the fraction taken as zero when `D_Q(v)=0`.

### Why the denominator is frozen

A natural but wrong implementation removes dead edges and renormalizes the surviving ones. If `v` originally sends half of its mass through `h_1` and half through `h_2`, and `h_1` is revoked, renormalization gives all mass to `h_2`. The invalidated knowledge has silently made unrelated surviving knowledge **more influential**.

KSO instead removes the exact dead contribution. Missing row mass is dissipation / restart mass. This is the mathematical meaning of “a revoked node takes its share out.”

### Theorem KS-T03 — navigation is substochastic

For every `v`,

\[
0\le\sum_u P_{Q,R}(v,u)\le1.
\]

**Proof.** Every term is nonnegative. Before gating, for each `v` the structural edge shares `w_hβ/D_Q(v)` sum to one (or zero when the denominator vanishes), and each `γ_h` sums to one. Every gate is in `{0,1}`, so gating can only remove mass. ∎

### Theorem KS-T04 — exact-share pruning equivalence

Let `Prune_R^0(𝒦)` remove every non-live atom/edge but retain the **original pre-revocation structural denominators**. Then

\[
P_{Q,R}(\mathcal K)
=
P_{Q,\varnothing}(\operatorname{Prune}_R^0(\mathcal K)).
\]

**Proof.** Both matrices contain exactly the same structural contribution for every live `(v,h,u)` incidence, with the same original denominator. Every dead incidence contributes zero in the gated expression and is absent in the pruned expression. Entry-wise equality follows. ∎

Two independently written exact implementations are required to agree. A planted “renormalize survivors” implementation must disagree on a registered witness.

---

## 6. Restart dynamics and the meaning of “reaction”

Choose restart probability `α∈(0,1]`. The fast cognitive dynamics are

\[
a_{k+1}
=F_Q(a_k)
=\alpha s_Q+(1-\alpha)P_{Q,R}^{\mathsf T}a_k.
\]

### Theorem KS-T05 — contraction and unique fixed point

For all real vectors `a,b`,

\[
\|F_Q(a)-F_Q(b)\|_1
\le(1-\alpha)\|a-b\|_1.
\]

Therefore `F_Q` has a unique fixed point and iteration converges geometrically to it.

**Proof.** A substochastic nonnegative matrix has induced `ℓ_1` norm at most one after transposition:

\[
\|P^{\mathsf T}x\|_1\le\|x\|_1.
\]

Hence

\[
\|F(a)-F(b)\|_1
=(1-\alpha)\|P^{\mathsf T}(a-b)\|_1
\le(1-\alpha)\|a-b\|_1.
\]

Because `1-α<1`, Banach's fixed-point theorem applies. Equivalently,

\[
a^*=\alpha[I-(1-\alpha)P^{\mathsf T}]^{-1}s_Q
=\alpha\sum_{k\ge0}(1-\alpha)^k(P^{\mathsf T})^k s_Q,
\]

where the Neumann series converges. ∎

The M0 checker solves one instance exactly over rational numbers, verifies the fixed-point equation, and runs 200 independent contraction checks.

### Reaction is surprise, not popularity

Let `π(v)` be a query-independent or background activation baseline. Define

\[
\rho_Q(v)
=a_Q^*(v)
\left[
\log\frac{a_Q^*(v)+\varepsilon}{\pi(v)+\varepsilon}
\right]_+.
\]

### Theorem KS-T06 — background-equal atoms have zero reaction surprise

If `a_Q^*(v)=π(v)`, then `ρ_Q(v)=0`.

**Proof.** The logarithm is `log 1=0`. ∎

Thus a generic hub that is active for nearly every query is not automatically a strong clue. A normally quiet atom that becomes unusually active can outrank it.

This is a design choice, not a novelty theorem; alternative statistically principled surprise functions may replace it if they survive the same invariants.

---

## 7. Extracting the reacting subspace

A solution is not defined as the top `k` atoms. KSO extracts a connected typed subhypergraph balancing reaction prize and resource cost:

\[
G_Q^*
\in
\arg\max_{G\subseteq\mathcal K}
\left[
\sum_{v\in V(G)}\rho_Q(v)
+\lambda\sum_{h\in H(G)}\rho_Q(h)
-\mu C(G)
\right]
\]

subject to

- connectivity to the relevant query seeds,
- type/port compatibility,
- live-warrant constraints for warranted mode,
- declared resource budget.

This is a prize-collecting connected-subgraph / Steiner-style parent problem. M0 defines the objective; M2 must instantiate an exact bounded solver and a strongest-parent approximation/control. No extraction-algorithm novelty is claimed.

Maintain separate modes:

\[
G_Q^W\quad\text{(warranted)},
\qquad
G_Q^X\quad\text{(exploratory)}.
\]

Exploratory structures may suggest hypotheses but cannot silently authorize a final claim.

---

## 8. Procedure space

Relevant knowledge is not yet a method. A candidate procedure is a typed executable expression in a KAT-/wiring-style algebra.

Primitive procedure semantics are partial or stochastic maps

\[
p:X\rightharpoonup Y
\quad\text{or}\quad
p:X\to\Delta(Y).
\]

The minimal control operators are sequencing, typed parallel/wiring composition, guarded choice/tests, and explicitly bounded iteration. Their algebra is inherited from Kleene algebra with tests and hypergraph-category / operadic wiring parents.

For a responding subgraph `G`,

\[
\operatorname{Compose}(G)
\subseteq\mathbf{Proc}_{\mathcal K}
\]

contains only type-compatible expressions whose required operator hyperedges exist or are explicitly proposed as new relations.

A successful composition inherits warrant by `⊗`, scope by intersection, and resource cost additively/non-compensatorily. The hard open question is not control-flow algebra; it is whether KSO can **learn and consolidate useful reusable procedures** under these lifecycle constraints.

---

## 9. Representation, quotienting and local contexts

### 9.1 Navigation-preserving quotient

Let `κ:V→\bar V` define a partition of states into representation blocks. For a Markov quotient to be well-defined, require Kemeny–Snell lumpability:

\[
\forall B,B',\;v,v'\in B:
\sum_{u\in B'}P(v,u)
=
\sum_{u\in B'}P(v',u).
\]

Then

\[
\bar P(B,B')=\sum_{u\in B'}P(v,u),\quad v\in B
\]

is independent of the representative, and for every distribution `x`,

\[
\kappa_*(xP)=(\kappa_*x)\bar P.
\]

### KS-T07 — quotient navigation commutes with pushforward

The equality above is exactly the standard lumpability theorem. KSO adopts it as a representation gate; it is parent mathematics, not an OCM theorem claim.

The executable checker validates a 4-state/2-block example on 80 nonzero rational distributions and carries a planted non-lumpable mutation.

### 9.2 Authority preservation is a separate condition

Navigation lumpability does **not** imply revocation/warrant preservation. A quotient is authority-safe only when every admitted revocation/authority decision is measurable with respect to the representation partition (the existing #201/S4 requirement).

Therefore a representation move is admissible only when both hold:

\[
\boxed{\text{navigation lumpability}\;\land\;\text{warrant/authority measurability}.}
\]

This prevents a good dynamical compression from laundering epistemic distinctions.

### 9.3 Local-to-global structure

The existing epistemic atlas is retained as a presheaf-like contextual cover `𝔘={U_i}`. Local compatibility does not itself authorize a global section:

\[
\text{matching local family}\not\Rightarrow\text{global truth}.
\]

A global section requires an independently registered witness, consistent with the existing `epistemic_atlas.py` semantics.

---

## 10. Learning is a typed graph transaction

An acquisition event from channel `c` proposes

\[
\Delta_c=(\Delta V,\Delta H,\Delta\Lambda,\Delta A,\Delta S).
\]

Admission is atomic:

1. validate atom and relation types/ports;
2. bind content/provenance identities;
3. check the channel's permissible certificate kind;
4. check warrant and authority boundaries;
5. meter the resource delta;
6. insert the atoms **and their typed connections** in one transaction, or quarantine them.

Instruction, demonstration, interaction, experimentation and feedback may use different certificate interfaces, but the substrate does not assume a particular learning algorithm.

Feedback alone can update behavior/utility but does not by itself create evidential warrant.

### Theorem KS-T08 — semantic-connectivity invariant

If admission enforces

\[
\operatorname{NEWLIVE}(v)\Rightarrow \operatorname{CONNECTED}(v)\lor\operatorname{QUARANTINED}(v),
\]

then every newly live non-quarantined atom is incident to at least one live typed relation.

**Proof.** Immediate from the admission rule. The significance is that the condition is mechanically checkable rather than aspirational. ∎

The checker includes a connected atom, a quarantined isolated atom, and a planted isolated live non-quarantined atom that fails.

---

## 11. Consolidation / abstraction

Repeated useful subgraphs may be compressed to macro-atoms or macro-procedures. For candidate macro `m` representing subgraph `G`, require at minimum:

\[
\llbracket m\rrbracket=\llbracket G\rrbracket
\]

on the registered scope, a reconstruction/provenance map to `G`, and preservation of its live dependency information.

A compression objective may use an MDL-style criterion

\[
\Delta L=L(G)-[L(m)+L(\chi)+L(\text{exceptions})],
\]

but positive compression is not sufficient for admission: semantics, warrant, scope and future-revocation behavior must also pass.

**Open residual KS-T12.** Prove a lifecycle-safe consolidation theorem showing when a macro can be maintained/reopened in work proportional to the actually affected dependency region rather than full re-derivation. This is not proved at M0.

---

## 12. Active acquisition / experiment selection

Internal navigation may identify an information deficit that requires interacting with the world. Let belief state be `B`, authorized action `a`, environment transition `T`, and observation channel `Z`.

Choose an epistemic action by decision value, not raw entropy reduction:

\[
a^*
\in
\arg\max_{a\in A_{\rm authorized}}
\mathbb E[V(B_{t+1})-V(B_t)\mid a]
-C(a)-\operatorname{Risk}(a).
\]

The resulting observation is inserted with causal/action provenance. Observation and intervention are typed separately. This is parent-owned value-of-information / Bayesian experimental-design mathematics; KSO's task is integration with its warrant and rewrite lifecycle.

---

## 13. Revocation, reopening and the impact cone

Revocation changes warrant gates, which changes navigation, firing, extracted subgraphs, cached procedures and consolidations.

For dependency relation types `D`, define the forward impact operator

\[
\Gamma_D(X)
=
X\cup\{u:\exists h,\;r_h\in D,\;T_h\cap X\ne\varnothing,\;u\in O_h\}.
\]

Define the impact cone as the least fixed point

\[
\operatorname{Impact}_D(X)=\mu Y.\Gamma_D(Y).
\]

### Theorem KS-T09 — impact cone is the least dependency-closed superset

`Impact_D(X)` contains `X`, is closed under all registered dependency hyperedges, and is contained in every other dependency-closed superset of `X`.

**Proof.** `Γ_D` is monotone on the finite lattice `2^V`. Iterating from `X` reaches a finite fixed point. By induction, every iterate is contained in every closed superset containing `X`; hence the fixed point is the least such superset. ∎

The checker verifies the exact cone on a three-node dependency chain.

Only objects in the sound impact cone may need forced reopening; unrelated objects are a no-alarm control.

---

## 14. Gap versus structural obstruction

Failure to answer is typed.

A **local gap** means the current representation/operator family is still adequate, but a missing atom, relation, observation or certificate could close an obligation. The acquisition channels may be invoked.

A **structural obstruction** requires a witness

\[
\Omega=(M,\mathcal O,W_{\rm fail},D_{<j},R_{\rm bound})
\]

identifying the incumbent mechanism `M`, failed obligation `𝒪`, witness/counterexample set, dispositions of all lower-level repairs, and resource boundary.

Low score, timeout or subjective “stuckness” alone is not a structural obstruction.

---

## 15. Jump as governed graph rewrite

A structural Jump is a typed algebraic graph transformation

\[
L\xleftarrow{l} I\xrightarrow{r}R
\]

matched into the current KSO. The interface `I` is the protected structure that must correspond across the rewrite. A proposal carries

- admitted ORION Jump level `J0…J8`,
- obstruction witness `Ω`,
- parent/donor lineage,
- correspondence map,
- preservation obligations,
- predicted consequences **before** outcome access,
- falsifiers,
- resource delta,
- dependency impact/reopen set,
- rollback/recovery path.

Use the existing ORION levels:

`J0` action parameter; `J1` local repair/composition; `J2` model/hypothesis family; `J3` representation; `J4` problem/objective; `J5` method/operator; `J6` workflow/meta-skill; `J7` framework; `J8` constitution proposal.

The minimum sufficient level wins. A `J8` rewrite may be proposed by OCM but cannot self-authorize adoption.

DPO/adhesive-category rewrite mathematics is parent-owned. The open ORION question is whether obstruction, authority, warrant/reopen and resource obligations create a useful residual when coupled to rewrite.

---

## 16. Multi-timescale dynamics

KSO intelligence is explicitly not one forward pass.

Fast query dynamics:

\[
a_{t,k+1}=F_{\mathcal K_t,Q_t}(a_{t,k}).
\]

Learning / memory dynamics:

\[
\mathcal K_{t+1}=\mathcal U(\mathcal K_t,Q_t,p_t,o_t,C_t).
\]

Meta-structural dynamics:

\[
\mathfrak M_{n+1}=\mathcal J_n(\mathfrak M_n).
\]

The timescales are separately metered and may use different algorithms.

---

## 17. Language / chat boundary

Incoming text is an encoding, not the cognitive state:

\[
u_t\xrightarrow{\eta_c}Q_t\xrightarrow{\mathrm{KSO}}(G_t,p_t)\xrightarrow{\rho_c}y_t.
\]

Strong translator invariance would require two semantically valid codecs `c_1,c_2` to produce equivalent verified internal outcomes:

\[
\operatorname{Solve}_{\mathcal K}(\eta_{c_1}(u))
\cong
\operatorname{Solve}_{\mathcal K}(\eta_{c_2}(u)).
\]

A weaker M5 gate may compare verified denotation/answer rather than graph isomorphism.

**KS-T10 remains OPEN.** No natural-language competence follows from the M0 mathematics.

---

## 18. Frontier mathematics

The intended M6 loop is

\[
\text{problem}
\to\text{atomize}
\to\text{navigate}
\to\text{extract}
\to\text{compose conjecture/lemma procedure}
\to\text{formal checker}
\to\text{learn or retract}
\to\text{Jump if a structural obstruction is witnessed}.
\]

A proof assistant is a warranting checker, not mere feedback. A rejected conjecture becomes a counterexample/failure atom rather than disappearing.

This pattern has strong neuro-symbolic theorem-proving parents (including AlphaGeometry-class systems). KSO does not claim a frontier-math residual until a frozen matched comparison survives.

---

## 19. Whole-system resources

Every claimed gain reports at least

\[
\mathcal R=(
B_{\rm core},B_V,B_H,B_\Lambda,B_{\rm index},
T_{\rm nav},W_{\rm nav},T_{\rm comp},V_{\rm cost},
IO,BW,N_{\rm probe},N_{\rm jump},C_{\rm rewrite},C_{\rm rollback}
).
\]

Optional energy is reported only under a defensible measurement/model. Comparisons are Pareto/non-compensatory. No small-core claim may hide a huge graph, privileged verifier, free codec/index, or unbounded navigation.

---

## 20. Theorem and implementation ledger

| ID | obligation | M0 disposition |
|---|---|---|
| `KS-T00` | finite object well-formedness and nonnegative resource coordinates | `DEFINED_AND_CHECKED` |
| `KS-T01` | warrant antichains form the stated idempotent commutative semiring | `PROVED_V1`; exhaustive n=3 checker |
| `KS-T02` | revocation of a required tail/edge disables conjunctive firing | `PROVED_V1`; planted firing witness |
| `KS-T03` | warranted navigation matrix is substochastic | `PROVED_V1` |
| `KS-T04` | gate-based exact-share revocation equals pruning with original denominators | `PROVED_V1`; two implementations agree; renormalization mutant caught |
| `KS-T05` | restart navigation is an `ℓ1` contraction and has one fixed point | `PROVED_V1`; parent mathematics; exact rational witness + 200 checks |
| `KS-T06` | background-equal atom has zero reaction-surprise score | `PROVED_V1` |
| `KS-T07` | representation quotient commutes with navigation under lumpability | `PARENT_THEOREM_ADOPTED`; 80 exact commutation checks + negative control |
| `KS-T08` | admission connectivity/quarantine invariant | `DEFINED_AND_CHECKED`; implementation invariant, not novelty theorem |
| `KS-T09` | dependency impact cone is the least dependency-closed superset | `PROVED_V1` |
| `KS-T10` | codec/translator invariance | `OPEN_M5` |
| `KS-T11` | exact/approximate connected reacting-subgraph extraction contract | `PARENT_PROBLEM_ADOPTED__M2_IMPLEMENTATION_OPEN` |
| `KS-T12` | lifecycle-safe consolidation / deconsolidation frontier | `OPEN_RESIDUAL_CANDIDATE` |
| `KS-T13` | gap-learning closes missing structures with warrant preserved | `OPEN_M3` |
| `KS-T14` | governed Jump loop preserves interface/authority and improves only when lower level insufficient | `OPEN_M4` |
| `KS-T15` | frontier-math pilot with proof-assistant warrant | `OPEN_M6` |
| `KS-T16` | strict whole-system frontier beyond strongest faithful parent product | `OPEN_DECISIVE`; required for architecture-residual language |

No lower row is implied by an upper row.

---

## 21. Exact M0 evidence

`reference/kso_math_v1.py` uses exact rational arithmetic for the finite checks.

Registered result denominators:

- warrant profiles over 3 evidence atoms: **20**;
- semiring pair checks: **400**;
- semiring triple/distributivity checks: **8,000**;
- independent navigation-matrix equality checks: **2** (pre/post revocation);
- planted post-revocation renormalization defect: **1/1 detected**;
- exact rational fixed-point equation: **1/1**;
- independent contraction checks: **200/200**;
- conjunctive firing / revocation checks: **2/2**;
- lumpability pushforward-commutation checks: **80/80**;
- planted non-lumpable matrix: **1/1 rejected**;
- semantic-connectivity cases: **5** including an isolated live failure and a quarantined isolated no-alarm;
- dependency impact-cone case: **1/1**.

Unit test contract: `tests/unit/test_kso_math_v1.py`.

Finite enumeration is calibration/evidence for the implementation; it is **not** authority for the all-size proofs. The all-size claims above carry explicit mathematical proofs or are marked parent theorem / open.

---

## 22. Strongest-parent comparator and scientific terminal

Every future KSO claim receives first-right-of-refusal from the product recorded in `KSO_PARENT_SUBTRACTION_V1.md`:

```text
typed hypergraph
+ local/restart hypergraph navigation
+ optional sheaf-valued transports
+ ATMS/provenance labels
+ KAT/typed wiring
+ Petri-style conjunctive firing
+ connected-subgraph extraction
+ Markov-lumpable compression
+ DPO graph rewriting
+ proof-carrying admission
+ DreamCoder/LILO-style library learning
+ active experiment selection
+ identical memory, tools, verifier, codec and resource budgets
```

A faithful simulation/equivalence is a valid `PARENT_SUFFICIENT` result.

Current terminals:

```text
KSO_M0_FINITE_MATH_CORE = GREEN
KSO_NOVELTY = NOT_ESTABLISHED
KSO_ARCHITECTURE_RESIDUAL = NOT_ESTABLISHED
M1_KSO_INSTANCE = NOT_RUN
M2_SOLVE_LOOP = NOT_RUN
M3_GAP_LEARNING = NOT_RUN
M4_JUMP_LOOP = NOT_RUN
M5_CHAT = NOT_RUN
M6_FRONTIER_MATH = NOT_RUN
```

## 23. Binding direction

The next work is **M1**, not another disconnected conceptual lane: instantiate this exact contract on one existing oracle domain, populate atoms/hyperedges from that domain, and require the M0 invariants to survive unchanged. Only after M1 exists should M2 test the full `atomize → navigate → fire → extract → compose → check` loop.

---

# Part II — freeze addendum (M0-F): the clauses #284 §2–§4, #194 and #197 require, each bound to a checker on the machine

Status of Part II: every clause below is `DEFINED → THEOREM → PROOF → CHECKER` with the checker in
`../reference/kso_m0_freeze_checks_v1.py` (finite, exact, planted failure / must-differ control /
no-alarm / distinct `CANNOT_CHECK` exit) and, where marked **[M1]**, re-run on real ME-X1 worlds by
`../reference/kso_m1_mex1_population_v1.py` (receipt `../results/KSO_M1_POPULATION_RECEIPT_V1.json`).
Part I is unchanged; `kso_math_v1.py` and its pinned results are byte-identical to PR #290.
**NO NOVELTY OR BREAKTHROUGH CLAIM.** Most rows are parent-owned and say so.

## 24. Edge vocabulary is the atlas vocabulary (A2)

`τ_H` ranges over the registered set

\[
\mathcal T_H=\underbrace{\{\mathrm{RESTRICTION},\mathrm{EMBEDDING},\mathrm{SCALE\_CHANGE},\mathrm{BOUNDARY\_CHANGE},\mathrm{REPRESENTATION\_TRANSPORT},\mathrm{DECISION\_TRANSPORT}\}}_{\texttt{epistemic\_atlas.ContextMapKind}}
\cup\{\mathrm{DEPENDENCE},\mathrm{SUPPORT},\mathrm{COMPOSITION},\mathrm{CONSTRAINT}\}.
\]

The first six are read from `src/orion_v2/epistemic_atlas.py` at check time and must match the
literal list above (drift is a failure, unimportability is `CANNOT_CHECK`); the last four are the
relation kinds #194 names (dependence, support/transport, composition, constraint). A hyperedge
whose type is outside `𝒯_H` is the typed rejection `UNREGISTERED_RELATION_TYPE`, at construction
and at acquisition. Dependency types for the impact cone (§13) are the last four.
Checker F1. Parent: the atlas itself (V2 `epistemic_atlas.py`); nothing new.

## 25. The restart seed is warrant-gated, not renormalised (B2, B4)

Part I gates edges and atoms; the seed must be gated the same way or a dead atom keeps the restart
mass `α s_Q(v)`. Define

\[
s_{Q,R}=g_R\odot s_Q\qquad\text{(entry-wise; NOT renormalised).}
\]

**Theorem KS-T04b (exact-share retraction propagates to activation).** Let `D_R` be the set of
atoms non-live under `R`, and `Reach(D_R)` their ungated forward closure. For the fixed point
`a^*_R` of `F_{Q,R}(a)=α s_{Q,R}+(1-α)P_{Q,R}^{\mathsf T}a`:
(i) `a^*_R(v)=0` for every `v∈D_R`; (ii) `a^*_R(u)=a^*_∅(u)` for every `u∉Reach(D_R)`;
(iii) `a^*_R(u)≤a^*_∅(u)` for every `u`; (iv) `a^*_{∅}` is restored exactly when `R` is lifted.

*Proof.* (i) row and column `v` of `P_{Q,R}` and the entry `s_{Q,R}(v)` are zero, so the Neumann
series (KS-T05) contributes nothing to `v`. (ii) every walk from the seed support to `u` avoids
`D_R` (else `u∈Reach(D_R)`), and on such walks every factor of `P_{Q,R}` equals the corresponding
factor of `P_{Q,∅}` because denominators are frozen (KS-T04); the series for `u` is term-wise
identical. (iii) `P_{Q,R}≤P_{Q,∅}` entry-wise and `s_{Q,R}≤s_Q`, and the series has nonnegative
terms. (iv) the map `R↦(P_{Q,R},s_{Q,R})` is a function of `R` alone. ∎
Under the renormalising parent (ii) fails: a survivor of a revoked sibling gains mass. Checker F2
(mutation asserted applied; unapplied planted retraction is `CANNOT_CHECK`); **[M1]** P3 on 400
planted revocations over 50 worlds, 400/400, parent differed on 16 worlds; registered events
replayed as the real revocation 50/50 with 0 disagreements against the oracle at v1.
Parent: none owns the conjunction (§32); the pieces are JTMS/ATMS gating and PPR.

## 26. Two-direction hub theorem (A9)

Let `π=a^*_{\rm uniform}` be the background and `ρ_Q(v)=a^*_Q(v)[\log(a^*_Q(v)/π(v))]_+` (§6).

**Theorem KS-T06b.** On the witness (hub `H` linked both ways to `x_1..x_4`; `sp` fed by `x_1`
only): (i) for the question seeded at `x_1` (touching both `H` and `sp`), `a^*(H)>a^*(sp)` and
`ρ(sp)>ρ(H)` — the popularity ranking and the surprise ranking differ, and the specific atom wins
the second; (ii) for the question seeded at `x_2` (touching only `H`), `H` wins both rankings;
(iii) `ρ≡0` for the background question.

*Proof.* (iii) is KS-T06. (i)–(ii) are finite exact computations over ℚ (activations) followed by
the monotonicity of `t↦t\log(t/c)` on `t>c`; the checker performs them.
Checker F3 (popularity ranker = planted control that must differ). **[M1]** P4: background 0
everywhere and hub-seeded question makes the hub positive and top, 50/50; for an evidence-seeded
question the hub wins by surprise on 2/50 worlds only (reported, not asserted: on these graphs the
degree hub is usually the target claim itself). Parent: IDF / degree normalisation; nothing new.

## 27. Acquisition is a typed transaction with a certificate kind (B8, C4)

Channels are certificate kinds `𝒞={INSTRUCTION, DEMONSTRATION, INTERACTION, EXPERIMENTATION,
FEEDBACK, EXACT\_CHECKER}`. `admit(𝒦, v, H_v, c)` succeeds iff: `v` is fresh; `H_v≠∅` or `v` is
quarantined (else `ISOLATED_ATOM_REJECTED`); every edge is incident to `v` and typed in `𝒯_H`;
`v` lies in the ungated closure of the existing atoms and, if warranted, receives positive
activation from a uniform seed on them (else `UNREACHABLE_BY_NAVIGATION`); and the label is set by
the certificate: `c=FEEDBACK ⇒ Λ_v=\mathbf 0`; `c∈𝒞∖\{FEEDBACK\}` requires `Λ_v≠\mathbf 0`
(else `WARRANTING_CHANNEL_WITHOUT_WARRANT`).

**Theorem KS-T18 (feedback cannot warrant, carried in from stage 1).** A feedback-admitted atom
is never live and never enables a firing: `ℓ_R(\mathbf 0)=0` for all `R`, so by KS-T02 every
hyperedge with it in the tail is disabled. An `EXACT_CHECKER` atom (a proof assistant's verdict)
enters with `Λ_v≠\mathbf 0` and enables. *Proof.* immediate from §3 and §4. ∎
Checker F4 (8 cases). **[M1]** every populated atom carries a certificate (base atoms and
evidence `EXPERIMENTATION`, families/claims `INSTRUCTION`, formal results `EXACT_CHECKER`) and S1
holds on 100 populated spaces. Parent: PCC (admission), #197 stem-cell row 2.

## 28. Atomisation (B1)

`η(x)` maps a question given as parts `(text, type, refs)` to exactly `k=|parts|` query seeds and
a seed distribution `s_Q` over the referenced atoms (uniform within a part, parts equally
weighted). Rejections: `EMPTY_QUESTION`, `NON_ATOMIC_INPUT` (a part without a type), `UNBOUND_SEED`
(no or unknown refs). `s_Q` is a function of the parts (deterministic, the committed seed).
Checker F5. Parent: question decomposition / Zettelkasten atoms; nothing new.

## 29. Navigation outcome and the obstruction witness (B7) — a definition, not prose

`navigate(𝒦, s_Q, t, B)` with budget `B=(steps, restarts, depth)` (`B` must be positive, else
`CANNOT_CHECK`) returns one of

\[
\mathrm{FOUND}\;|\;\mathrm{GAP\_NOT\_FOUND}\;|\;\mathrm{OBSTRUCTION\_WITNESSED}\;|\;\mathrm{CANNOT\_CHECK}.
\]

Let `a_k` be the bounded gated walk (`k≤steps`), `C^\circ` the **ceiling walker** = ungated,
unbounded closure of the seed support over every registered relation, and `C^R` the gated closure.

- `FOUND` iff `∃k≤steps: a_k(t)≥θ`.
- `GAP_NOT_FOUND` iff not found and (`t∉V` — reason `TARGET_ABSENT`, hook = acquisition channels;
  or `t∈C^\circ∖C^R` — reason `WARRANT_GATED`, hook = acquire warrant; or `t∈C^R` — reason
  `BUDGET_EXHAUSTED`, hook = more budget). **Timeout alone is a gap.**
- `OBSTRUCTION_WITNESSED` iff `t∈V` and `t∉C^\circ` (the ceiling walker fails too), with witness
  `Ω=(M, 𝒪, W_{\rm fail}=C^\circ, D_{<j}, R_{\rm bound})`, `D_{<j}` naming why budget, warrant and
  restart are not repairs; **or** (identification asked) `t` is found but a same-type atom has
  exactly the same activation under the committed seed — witness kind
  `STRUCTURAL_NONIDENTIFIABILITY`, the ME-X2 `CANNOT_IDENTIFY` case; re-atomisation is a J3
  proposal, not a lower-level repair.

**Escalation rule (H-EXT-1R, finite form).** Escalate to the Jump ladder iff the gated walker fails
**and** the ceiling walker is witnessed off ceiling (`t∉C^\circ`). `Ω` maps onto
`orion_v2.jump.JumpTrigger(kind=GLOBAL\_OBSTRUCTION | STRUCTURAL\_NONIDENTIFIABILITY,
incumbent\_level=J1, witness\_ids=W_{\rm fail}, lower\_level\_dispositions=D_{<j})` and must be
`is_admissible`. **Theorem KS-T19.** The four outcomes are exhaustive and pairwise exclusive on
every finite `𝒦`. *Proof.* case split on `t∈V`, `t∈C^\circ`, `t∈C^R`, `a_k(t)≥θ`. ∎
Checker F6 (three outcomes exhibited on one space, timeout-is-gap, zero budget is
`CANNOT_CHECK`, witness admissible) and G2-nonidentifiability. Parents: V2 `jump.py`; ME-X2.

## 30. Compose (B6) and extract (B5)

`compose(𝒦, (x_1..x_n), y, P_b)` adds `y` with `Λ_y=P_b⊗\bigotimes_iΛ(x_i)` and one COMPOSITION
hyperedge `(x_1..x_n)→y`. **KS-T20.** `y` is non-live whenever any component is; the *merge*
`⊕_iΛ(x_i)` is not a composition (it outlives a revoked component) and is caught by S2.
Checker G2-compose. **[M1]** S2 holds on every populated space (evidence, family and result
atoms are compositions); planted merged family label caught 50/50.

**KS-T11a (the reacting subgraph is well-defined and unique).** `G_Q=(V_Q,H_Q)` with
`V_Q=\{v∈C^R_{\rm seed}: ρ_Q(v)>0\}∪\mathrm{supp}(s_Q)` and `H_Q` the live hyperedges inside `V_Q`
is a function of `(𝒦,R,s_Q,α)` because `a^*` is (KS-T05). The prize-collecting optimiser of §7 is
a different object and may have several optima (planted tie: prize = cost); M2 must report ties.
Checker G2-extract. Parent: PCST; nothing new.

## 31. Translator invariance, the provable half (A13)

**KS-T10a.** `Solve_𝒦` is a function of `(𝒦, s_Q)`: two codecs `c_1,c_2` with
`η_{c_1}(u)=η_{c_2}(u)` yield identical `G_Q` (by KS-T11a). The open half, KS-T10, is whether two
independent codecs agree on `s_Q` — measurable at M5 with the same checker. Checker
G2-translator (equal seeds ⇒ identical extraction; unequal seeds differ = must-differ).

## 32. The genome: S1–S7 on the knowledge space, and the stem-cell invariant (A4, A16, C6)

A **governed space** is `𝒢=(𝒦, cert:V→𝒞, |E|, meter, R)`. The seven predicates:

| | statement on `𝒢` | planted violation caught |
|---|---|---|
| **KS-S1** | `Λ_v≠\mathbf 0 ⇒ cert(v)∈𝒞∖\{FEEDBACK\}` | feedback carrying warrant |
| **KS-S2** | every COMPOSITION head has `Λ=P_h⊗\bigotimes_{t∈T_h}Λ_t` | merged (⊕) label |
| **KS-S3** | for every `R`, an atom with a nonzero row or column of `P_{Q,R}` is live under `R` | (exhaustive at M0; sampled at M1: `R_0`, singletons, `R_0∪` singleton) |
| **KS-S4** | a coarsening of `E` answers every `R∈Γ` exactly iff each `R` is a block union (Theorem S4) | merging `{0,1}` while `Γ∋\{0\}` |
| **KS-S5** | re-certifying admitted atoms under another warranting policy leaves every liveness signature unchanged | re-admission through feedback |
| **KS-S6** | labels are canonical antichains; signature ↦ label is injective (`n=3` exhaustive) | dropping one coordinate collides |
| **KS-S7** | every transaction increments its meter coordinate; no store change without a counter change | unmetered admission |

The **genome digest** is the SHA-256 of the seven predicates' source. **Theorem KS-T17 (stem-cell
invariant, #197).** For the growth loop `acquire → compose → self-revise → registered revocation →
reinstate`, iterated from a governed space on which KS-S1..S7 hold: every iterate satisfies
KS-S1..S7, the composite of a revoked component is non-live at the revocation step (authority
preserved), the genome digest is unchanged, and the loop reaches a fixed point when nothing new can
be acquired. *Proof.* each operator is admitted through §27/§30 which enforce KS-S1/S2, meters
(KS-S7), and leaves labels of existing atoms untouched (KS-S5); KS-S3 is KS-T02/T04; the digest is
of code the operators never touch. ∎ The three **cancers** — feedback retained as warrant, a
composite outliving a revoked component, growth that edits a predicate — are each caught.
Checker G1 (7/7 planted violations) and G3 (3 growth steps, fixed point, 3/3 cancers). **[M1]** P5:
KS-S1, S2, S3 (sampled), S4, S5, S6 (canonical form), S7 hold on 100 populated spaces (v0 and v1 of
50 worlds); the digest is unchanged by population. Parents: #203 S1–S7 (PCC, ATMS, Doyle,
Blackwell, TMS in-lists, RCL-0, #194 §4 honesty rule) — restated, not new.

## 33. Gates carried in from other lanes (A14, A15, C3)

- **Budget clause (FM60 / ME-F1).** `NavigationBudget` is stated per arm; a comparison whose arms'
  budgets differ is `CANNOT_CHECK` (`UNMATCHED_NAVIGATION_BUDGET`). Checker F8.
- **Typing is a coverage prior over edges, not a capability (ME-X6 V3, n = 1800).** With full
  role coverage the typed and untyped walkers tie on the navigation outcome (3/3 targets on the
  witness); a typed advantage is admissible only on a relation type the comparator never exercised,
  which the checker exhibits by name; no typed advantage is claimed. Checker F9.
- **Closed under what was shown (E30-R14; ledger class 17).** The codec renders a whole subgraph
  with an elision receipt; atom references are located by content hash exactly once; an unshown or
  ambiguous reference voids the proposal whole (`ASKED_FOR_WHAT_WAS_NOT_SHOWN`,
  `AMBIGUOUS_REFERENCE`); the codec never writes a label or a graph coordinate. Checker F10.

## 34. Executable parent subtraction (D)

Eight parents were *run* on the retraction witness of §25 (checker F7; rows with sources in
`KSO_PARENT_SUBTRACTION_V1.md` §"Executable rows"): spreading activation, Quillian marker passing,
ACT-R activation, Hopfield recall, CBR retrieval, KG retrieval / RWR-with-deletion, JTMS, ATMS.
Finding, shown not assumed: each owns activation *or* retraction; **no single parent owns
label-gated activation with exact-share retraction** (0/8); and the honest converse — the KSO law
equals `(JTMS/ATMS gate) ∘ (spreading activation with pre-revocation denominators)` entry-wise on
the witness. The coupling is a product of two parents; it is a design choice, not a residual.

## 35. Ledger additions

| ID | obligation | disposition |
|---|---|---|
| `KS-S1…S7` | the genome on the knowledge space | `DEFINED_AND_CHECKED` (M0 planted 7/7; M1 100 spaces) |
| `KS-T04b` | exact-share retraction propagates to activation (i)–(iv) | `PROVED_V1`; F2; M1 400/400 |
| `KS-T06b` | two-direction hub theorem | `PROVED_V1` (finite); F3; M1 P4 |
| `KS-T10a` | translator invariance reduces to seed equality | `PROVED_V1`; KS-T10 stays `OPEN_M5` |
| `KS-T11a` | reacting subgraph well-defined and unique; optimiser distinct | `PROVED_V1`; G2 |
| `KS-T17` | stem-cell growth invariant | `PROVED_V1` (finite loop); G3 |
| `KS-T18` | feedback cannot warrant; exact checker can | `PROVED_V1`; F4 |
| `KS-T19` | navigation outcome exhaustive and exclusive; witness admissible | `PROVED_V1`; F6 |
| `KS-T20` | compose is ⊗, not ⊕ | `PROVED_V1`; G2 |
| `KS-A1` | edge vocabulary bound to the atlas source | `DEFINED_AND_CHECKED`; F1 |
| `KS-A2` | budget clause; typing coverage prior; closed-under-shown | `DEFINED_AND_CHECKED`; F8–F10 |
| `KS-P1` | no single parent owns label-gated exact-share retraction (8 run) | `SHOWN_ON_WITNESS`; F7 |

Rows `KS-T12`–`KS-T16` of Part I remain open at their stated milestones; none is implied here.

## 36. Freeze record

`KSO_M0 = FROZEN_V1` at the digests in `../results/KSO_M0_FREEZE_V1.json` (this file, the
architecture and parent files, the three checkers, the three unit-test files, the results). Reopen
conditions: any counterexample to a Part I/II theorem; an independent implementation disagreeing
with a checker; M1/M2 revealing an invariant unrealisable without changing its statement; a
stronger parent product absorbing an asserted residual (none is asserted).

```text
KSO_M0_FINITE_MATH_CORE = GREEN
KSO_M0_CONTRACT         = FROZEN_V1
M1_KSO_INSTANCE         = GREEN_DEV_SPLIT (ME-X1, 50 worlds; protected NOT_RUN)
M2_SOLVE_LOOP           = NOT_RUN
KSO_NOVELTY             = NOT_ESTABLISHED
```
