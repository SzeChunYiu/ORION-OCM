# GMI #602 parent atlas and formal-closure spine V1

Status: **FORMAL CLOSURE / PARENT-SUBTRACTION ARTIFACT — NOT A NEW THEORY AUTHORITY**  
Authority: #602 closure ledger under #233 formal theory and #373 programme convergence. Specialist donors: #377, #431, #433, #422, #426, #419.  
Date: 2026-09-14.

## 0. Purpose

This document closes the *formal* gaps that can be closed by deduction and exposes the gaps that cannot. It does not award an empirical checkbox because an experiment has merely been specified. It does not relabel a mature parent theorem as GMI novelty.

The proof classes inherited from #233 remain normative:

```text
P1 formal theorem
P2 finite exact theorem / exhaustive certificate
P3 probabilistic or generalization bound under explicit assumptions
P4 prospective empirical hypothesis/test
P5 impossibility / limit
```

A repository defect discovered during this audit is material: `research/machine-intelligence-morphogenesis-v1/PARENT_LEDGER_V2.json` is empty although `DEFINITIONS_V2_EXACT.md` cites it as a parent-verification source. Parent coverage is therefore reconstructed here instead of inherited transitively.

## 1. Review lenses

Five adversarial roles were applied to every load-bearing statement:

| lens | background | question |
|---|---|---|
| Formal CS | automata, computability, communication complexity, formal verification | what is actually provable / undecidable? |
| Learning | statistical learning, optimization, meta-learning, program synthesis, evolutionary search | what is already a learning-theory parent? |
| Decision/causal | decision theory, MDP/POMDP, metareasoning, SCMs, experimental design | what information/action condition is necessary and sufficient? |
| Development/cognition | cognitive architectures, continual learning, HRL, cultural/evolutionary dynamics | what is genuinely developmental rather than stored state or a parent mechanism? |
| Statistics | concentration, adaptive analysis, preregistration, extrapolation | what evidence class can support the stated claim? |

A row is accepted only after stating object, assumptions, strongest parent, residual, falsifier and claim ceiling.

---

# 2. Common formal objects

Use a registered scope

\[
\Omega=(\mathcal W,\mathcal O,\mathcal E,\mathcal R,\mathcal V,\mathcal H,\Gamma,\mathcal C,\varepsilon),
\]

where `W` is the world/task family, `O` protected obligation, `E` ecology, `R` resource prices/hard budgets, `V` verifier, `H` developmental history, `Γ` legal neutral construction/search grammar, `C` protected constitutional boundary and `ε` declared error tolerance.

A morphology is bookkeeping-only architecture-independent structure

\[
M=(F,O,\Pi,U,\Lambda,\Theta,J)
\]

with representation/carrier, operators, controller, update law, composition/topology, mutable state and external interfaces.

The lifecycle vector is

\[
c_\Omega(M)=(desc,state,exec,upd,ver,rev,comm,search,acq,lat,fail).
\]

No scalar total exists unless a price vector was frozen before protected outcomes. Hard capacity and latency remain feasibility constraints.

For histories `h,h'`, exact obligation equivalence is

\[
h\sim_{\mathcal O}h'
\iff
\text{all registered continuations/probes have identical protected obligation response.}
\]

At continuation-closed sequential scope this is a right congruence. Approximate `distance <= ε` is not automatically transitive and must not be called a quotient unless transitivity is separately established.

Finally keep five questions distinct:

```text
EXPRESSIBLE: Γ contains a composite with the property.
ADMISSIBLE:  such a composite can satisfy obligation/budgets.
REACHABLE:   the declared development/search process can reach it.
SELECTED:    it is on the frozen optimum/Pareto frontier.
REPLICATED:  it survives the required disjoint encoding/search/scale/substrate test.
```

No implication to the next rung is automatic.

---

# 3. Parent work for the registered whole-GMI scope

The table is a first-refusal ledger, not a claim that all relevant literature is known.

| GMI pressure/object | strongest parent work | what parent already owns | residual GMI question |
|---|---|---|---|
| exact finite-state sufficiency | Myhill–Nerode, automata minimization, fooling sets | right-congruence state and state lower bound | obligation-first reconstruction + lifecycle phase + neutral recovery |
| information/communication | Shannon coding, rate-distortion, communication complexity | information/transcript floors for separated states | unified resource-vector cuts across morphologies |
| decision sufficiency | Blackwell experiments, Bayesian decision theory | information cannot hurt when free; Bayes risk/value of information | information-price -> morphology frontier |
| universal computation | Turing/lambda/register machines, simulation/invariance | computable representability | not morphology choice, learnability, resource law or development |
| universal induction/search | Solomonoff, Levin search, OOPS, MDL | universal prior/search allocation and reuse under their assumptions | ecology-specific reachable/frontier law |
| optimizer null | Wolpert–Macready NFL, Blum speedup | no unrestricted universally best optimizer / relevant universal fastest solver | conditional learning-law selection only |
| active automata learning | Angluin L*; query-learning parents | feedback/query access can change learnability | cost of verifier/feedback in common ecology |
| SQ learning | Kearns statistical-query family | noise/query model and SQ learnability | resource phase on feedback type |
| linear/GLM/kernel | linear models, exponential families, RKHS/kernel theory | coefficient/basis mechanisms and standard learning results | obligation-derived basis demand + lifecycle crossover |
| low-rank adaptation | SVD/matrix approximation, ridge/regularization, adapters/LoRA | low-rank restriction/adaptation | residual target geometry and update/reuse phase |
| neural composition/gradients | circuit/universal-approximation theory, AD/backprop, smooth optimization | nonlinear composition and reverse-mode differentiation | when parent machinery is selected/reachable under full costs |
| architecture/algorithm search | NEAT, NAS, AutoML-Zero | generic search can rediscover neural structures and learning algorithms | cross-paradigm prediction *before* neutral search |
| symmetry/equivariance | group theory, convolution/equivariant networks, categorical/compositional DL | symmetry-licensed sharing/equivariance | obligation-derived symmetry + cross-morphology pricing |
| graphs/message passing | GNN/WL, local/distributed algorithms | locality/message-passing mechanisms and limits | topology/communication phase law |
| recurrence/state space | automata, state-space/control/system-ID | sufficient dynamical state under model assumptions | recurrence-vs-history-vs-external-memory phase |
| attention/routing | conditional computation, routing, associative/content-addressable memory | input-dependent source selection | dependency variability + access cost predictor |
| sparse/local attention | sparse routing, indexing/local algorithms | restricted access saves work but loses dependencies | obligation-derived radius/sparsity boundary |
| MoE | conditional computation/load-balancing parents | specialization/routing/communication mechanisms | heterogeneity-to-specialization phase law |
| exemplar/cache/RAG | kNN, cache/IR, databases, materialized views | retrieval/indexing/external memory and amortization | residual quotient + external-vs-absorbed lifecycle boundary |
| probabilistic belief | Bayes, graphical models, probabilistic programming/BPL | posterior/inference/update under a declared model | belief-vs-replay/count/map resource phase |
| continual learning | stability–plasticity, complementary learning systems, replay/regularization/expansion | retention/plasticity mechanisms | common safe-update/resource frontier |
| symbolic rules | term rewriting, production systems, Soar/ACT-R/TMS/ATMS | rule execution/chunking/conflict resolution | pressure for symbolic state and its frontier |
| hierarchy/planning | options/HRL, HTN/search, dynamic programming | skills/subgoals/planning mechanisms | reuse and stopping/selection laws |
| program/library learning | inductive programming, CEGIS, GP, DreamCoder, Stitch | synthesis and reusable libraries | when compilation/library acquisition pays |
| ensembles | bagging, boosting, mixture methods | aggregation/variance/margin mechanisms | correlation/diversity -> ensemble phase law |
| generative models | autoregressive, latent-variable, flow, diffusion/score models | factorization/inversion/score mechanisms | target geometry/resource estimator choosing factorization |
| control | MDP/POMDP, MPC, model-based/model-free RL | policy/belief planning under declared dynamics/reward | model-build/amortization/search phase |
| metareasoning | Russell–Wefald value of computation, bounded rationality | rational allocation of computation/information | only a cross-morphology residual if a shared predictor survives |
| causality | SCMs, do-calculus, potential outcomes/identification | observational/interventional/counterfactual semantics and identification | quotient statement of alias + priced interventions |
| active causal learning | Bayesian experimental design, active causal discovery, value of information | intervention/probe choice to identify target | no new algorithm unless parent residual survives |
| meta-learning | MAML, learned optimizers, inductive-bias/multitask representation learning | faster future learning from learned parameters/representations/rules | verified change in future search burden |
| evolutionary search | EC/population genetics, NEAT/QD/evolvability theory | variation/selection and useful-descendant distributions | inherited ecology-specific change in useful-successor mass |
| self-improvement | Gödel machines, OOPS/PowerPlay, AI4AI/self-improvement parents | self-change / solver-task accumulation under assumptions | governed architecture-independent verified-burden decrease |
| language/communication | coding, signaling games, information theory | protocols crossing a semantic cut | compositional/reuse phase under full cost |
| social cognition | game theory, inverse planning, social/Bayesian learning | models of other agents under assumptions | when retained agent model changes decisions enough to pay |
| teaching/culture | machine teaching, pedagogy/imitation, cultural evolution | informative demonstration/transmission mechanisms | sender/receiver and intergeneration lifecycle economics |
| indexing/history | Selinger access paths, deferred data structuring, amortized analysis, switching costs/warm starts | preprocessing/query/migration tradeoffs | developmental-history coordinate in common morphology law |
| HDC/VSA | hyperdimensional/vector-symbolic computing | binding/bundling/permutation/cleanup and capacity results | new domain only if bounded D1/D2/D4 reductions fail |
| relational/sheaf | CSP/SAT, factor graphs, message passing, sheaf/relational methods | constraints/consistency/gluing machinery | domain residual only after reduction + burden separation |
| local-field/cellular | CA/NCA, reaction-diffusion, distributed dynamical systems | local-update self-organization | domain residual only if D6/D7 reduction fails |
| energy/relaxation | Hopfield/modern Hopfield, energy-based models/optimization | energy-minimum/associative mechanisms | separate domain only with resource lower-bound separation |
| physical/analog/reservoir | reservoir/analog/neuromorphic/physical computing | substrate dynamics as computation | total I/O/preparation/calibration burden residual |
| quantum | quantum algorithms/learning; state prep/readout/error-correction theory | quantum mechanism and conditional advantages | end-to-end separation from classical parents |
| embodied/extended | robotics, active perception, morphological computation | body/environment can alter computational burden | system-boundary-sensitive phase law |
| statistical validity | Hoeffding/concentration, sequential inference, adaptive-data-analysis/reusable-holdout work | coverage/error guarantees under explicit sampling/adaptivity | register which parent theorem actually licenses each claim |
| verification | model checking, theorem proving, proof certificates | validity for formalized decidable objects | distinguish theorem from tested implementation |
| natural cognition | Soar, ACT-R, complementary-learning-systems and neuroscience/cognitive models | domain-specific cognitive mechanisms | G10 held-out operational bridge, not analogy |

Useful verified anchors include Shannon (1948), Blackwell (1953), Solomonoff (1964), Angluin (1987), Karp–Motwani–Raghavan (1988), Russell–Wefald (1991), Puterman (1994), Pearl (1995+), Wolpert–Macready (1997), Kaelbling–Littman–Cassandra (1998), Sutton–Precup–Singh (1999), Tishby–Pereira–Bialek (1999), Schmidhuber OOPS (2004), Finn–Abbeel–Levine (2017), Kocaoglu–Dimakis–Vishwanath (2017), Real et al. AutoML-Zero (2020), plus the specialist parents already enumerated by #233/#377/#422/#426.

Allowed parent-saturation terminal: `PARENT_COVERAGE_SATURATED_AT_REGISTERED_GMI_SCOPE`, never `ALL_RELEVANT_PARENTS_KNOWN`.

---

# 4. Formal residual theorem suite

## T602-01 — obligation-quotient necessity [P1]

If a machine encoding `q` maps two histories to the same state while the protected obligation requires pairwise incompatible correct continuation behavior, no policy using only `q` can be exact on both.

**Proof.** The policy receives the same state in the two cases and therefore cannot choose two incompatible exact responses. ∎

For a continuation-closed sequential obligation with finite quotient index `K`, every exact deterministic realization needs at least `K` distinguishable states; the quotient transition system gives a matching `K`-state realization. In regular-language scope this is Myhill–Nerode, not GMI novelty.

## T602-02 — residual-quotient lower bound [P1]

Let predictive state be `S_P` and protected target state `S_O`. For each predictive class `p`, let

\[
m(p)=|\{s_O:P(S_O=s_O,S_P=p)>0\}|.
\]

Any exact residual symbol `R` that allows reconstruction of `S_O` from `(S_P,R)` requires

\[
|R|\ge\max_pm(p),\qquad B_{fixed}\ge\lceil\log_2\max_pm(p)\rceil.
\]

**Proof.** In a predictive class attaining the maximum, fewer residual symbols force two target states onto the same `(p,r)` by pigeonhole. ∎

Expected residual information is lower-bounded by `H(S_O|S_P)` under the ordinary probabilistic coding setup. This is the formal core already exercised by #422; RAG/adapters/caches/databases remain parent-owned realizations.

## T602-03 — universality does not imply predictive GMI [P1/P5]

Take any universal interpreter `U` for a target `M`. For each `d>0`, construct `U_d` that performs `d` charged no-ops before each simulated target step. Every `U_d` computes the same target behavior while resource cost differs arbitrarily.

Therefore computational universality alone does not determine morphology frontier, learning law, phase boundary, state/update/search/verification burden, or developmental trajectory. This is an explicit witness for `UNIVERSAL_COMPUTATION_ONLY` and matches the resolution logic of `DEFINITIONS_V2_EXACT.md` §5.

## T602-04 — compensation-aware basis equivalence/minimality [P1]

For a bound class `K` closed under compiler composition, define `B1 ≡_K B2` iff each primitive of either basis has a semantics/development-preserving `K`-bounded compilation into the other. Then `≡_K` is an equivalence relation.

A primitive `p in B` is `K`-resource-irreducible only if no compensating composite over `B\{p}` implements `p` within `K` on the protected scope. A `K`-minimal basis has every primitive irreducible in this sense.

**Proof.** Identity gives reflexivity, mutual compilation gives symmetry, compiler composition plus closure of `K` gives transitivity. If a compensating bounded compiler exists, removing `p` cannot establish necessity at that resolution. ∎

Hence #602 A1 may correctly end in `MULTIPLE_EQUIVALENT_MINIMAL_BASES`; uniqueness is not required.

## T602-05 — lifecycle reuse/amortization threshold [P1]

Let retained mechanism `m` replace baseline `b` for `H` useful uses before invalidation. Under a prospectively frozen price vector `w`, let per-use saving be

\[
\Delta=w\cdot(c_b-c_m)
\]

and acquisition/build/maintenance/expected-revision burden be

\[
K=w\cdot(c_{build}+c_{acq}+c_{maint}+E[c_{revision}]).
\]

Retention/compilation is cheaper over the horizon iff

\[
H\Delta>K.
\]

Without a frozen scalar price vector compare full lifecycle vectors/Pareto feasibility instead. The arithmetic is parent-owned by amortized analysis/indexing/library learning; GMI's residual is a shared accounting object across memory, skills, teaching, culture, compilation and routing.

## T602-06 — information-conditioned morphology value [P1]

Assume a finite morphology set (or that the relevant minima are attained). Let world be `W`, choice be `m`, frozen loss be `L(m,W)`, and side information `Z` arrive before choice. Define

\[
R_Z=E_Z\min_mE[L(m,W)|Z],\qquad R_0=\min_mE[L(m,W)].
\]

Then `R_Z <= R_0`. Equality holds iff at least one morphology is a conditional minimizer for every positive-mass value of `Z`; otherwise it is strict.

**Proof.** Conditional minimization is no worse than any fixed `m0`; take expectations and minimize over `m0`. Equality is obtained exactly when one fixed minimizer is simultaneously conditionally optimal on every positive-mass cell. ∎

This is standard statistical decision theory. #674 is an exact finite instantiation/pressure test.

## T602-07 — expressibility/reachability separation and hitting bounds [P1]

Let `A` be a target set and `τ_A` its first hitting time under the *declared* proposal process. If on every not-yet-hit history the next-step conditional target probability obeys

\[
p_t=P(X_t\in A\mid\mathcal F_{t-1},\tau_A\ge t)\ge p_{min}>0,
\]

then by iterated conditioning

\[
P(\tau_A>T)\le(1-p_{min})^T.
\]

If proposals are iid with constant target mass `p`, equality becomes

\[
P(\tau_A>T)=(1-p)^T,\qquad E[\tau_A]=1/p.
\]

If the target has conditional proposal mass zero on every reachable not-yet-hit history, it is unreachable even if another abstract grammar can express it. If a necessary operator is absent from the registered grammar, the target is likewise unreachable in that grammar.

Thus a neutral-recovery claim needs both grammar support and nonzero search support. Derivability/admissibility alone is insufficient.

## T602-08 — no universal learning/update law [P5 + conditional P1]

NFL blocks a universally superior optimizer on unrestricted appropriately closed problem classes. Therefore GMI cannot universally derive gradient descent, Bayes, rule induction, evolutionary search or another fixed update law as *the* law.

The valid target is conditional:

\[
U^*(E,R,V,H)\in\arg\min_{U\in\mathcal U_{adm}}E[L(U,W)|E,R,V,H].
\]

Parent-owned examples:

- if `f` is `L`-smooth, `f(x-η∇f(x)) <= f(x)-η(1-Lη/2)||∇f(x)||²` for `0<η<2/L`;
- with a declared prior/likelihood, Bayesian conditioning supplies the posterior and Bayes decision rules under the registered loss;
- exact counterexamples/discrete reusable structure can privilege rule/program induction;
- derivative-free rugged regimes can privilege black-box/evolutionary search.

GMI's possible residual is an architecture-name-free ecology/resource descriptor that predicts which parent law enters the frontier and then survives neutral recovery/negative twins.

## T602-09 — capability information floor [P1]

If a capability contract has `K` world classes requiring pairwise incompatible exact actions, an exact deterministic sufficient state needs at least `K` values and a fixed code needs at least `ceil(log2 K)` bits.

For uniform `K`-class target `W` decoded from state `S` with error at most `ε`, Fano gives

\[
I(W;S)\ge\log_2K-h_2(\varepsilon)-\varepsilon\log_2(K-1).
\]

This is an information-theory parent floor; it does not choose the realizing architecture.

## T602-10 — interaction sign is not universal [P1/P5]

For lower-is-better cost with baseline `C0`, mechanisms `A,B` and joint cost `CAB`, define synergy of saved cost

\[
Syn(A,B)=C_A+C_B-C_{AB}-C_0.
\]

All signs are possible. With `C0=10`, `CA=CB=8`: `CAB=3` gives `+3`, `CAB=6` gives `0`, `CAB=7` gives `-1`.

Therefore F3/F4 cannot inherit universal complementarity. Joint laws must be derived from shared state/search/communication/verification or frozen-budget competition in the registered ecology. #670/#671/#672 are bounded P2 instances, not a universal sign theorem.

## T602-11 — developmental-history switching threshold [P1]

If installed morphology `A` may migrate to `B` at future cost `K>0` and `B` thereafter saves `Δ>0` per future block, migration with `h` blocks remaining is strictly cheaper iff

\[
h\Delta>K.
\]

The first integer horizon favoring migration is

\[
h^*=\lfloor K/\Delta\rfloor+1.
\]

Direction-dependent migration costs give ordinary hysteresis/path dependence; zero migration cost erases this source of history dependence. #680 is a prospective finite instance; switching-cost/indexing/warm-start parents own the mechanism.

## T602-12 — evolvability/useful-descendant burden [P1 with P3/P4 boundary]

For proposal kernel `Q(.|x)` and registered useful-successor set `U`, define

\[
Ev(x;U)=Q(U|x).
\]

Under iid proposals with exact verification and constant charged attempt cost `c`, expected first-useful-success burden is `c/Ev` when `Ev>0`. An inherited transformation reducing this full burden is useful only after charging its own acquisition, maintenance and revision cost.

Under prefix-coded Levin-style allocation, shortening a target code by `Δ` bits multiplies nominal search share by `2^Δ`; wall-time benefit remains conditional on scheduler/execution/verification costs.

These are parent-owned Levin/OOPS/evolvability mechanisms. GMI/HST's residual is prospective prediction of the transformation on a registered future-task ecology.

## T602-13 — species equivalence/preorder [P1]

At scope `Ω` and compiler bound class `K`, define `M1 <=_K M2` when a `K`-bounded compiler/simulator preserves the protected capability/development profile from `M1` into `M2`. Mutual simulation gives equivalence when `K` is composition-closed.

A distinct species therefore requires more than an architecture name: it needs a nonempty capability/resource region plus failure of registered bounded reductions in at least one direction, or a proved lower-bound separation. Implementation variants must be quotiented before species are counted.

## T602-14 — finite domain closure vs universal undecidability [P2/P5]

With finite grammar, finite world/input set, finite resource cap and decidable protected equivalence, candidate generation and all registered reductions are finite; domain closure is decidable at that scope.

For unrestricted programs, nontrivial extensional properties of the computed partial function are undecidable by Rice's theorem, and general semantic equivalence is undecidable. Therefore a universal algorithm certifying absence of every semantically distinct computational domain is impossible in general.

Correct terminal: `DOMAIN_BASIS_COMPLETE_AT_REGISTERED_FINITE_SCOPE`, never universal ontological completeness.

## T602-15 — candidate new-domain gate [definition]

A new-domain residual survives only if all hold:

1. operationally distinct carrier;
2. operationally distinct native operator/execution law;
3. all frozen D1–D8 reductions attempted;
4. at least one failed reduction has material proved/measured lifecycle separation;
5. a preregistered ecology puts the candidate on/off the frontier as predicted;
6. matched negative twin;
7. neutral recovery without the domain macro/name;
8. disjoint remint/search implementation and claim-appropriate real transfer.

Successful bounded reduction with no residual terminates `PARENT_SUFFICIENT`/reclassification.

## T602-16 — prospective unseen-form custody gate [P1 methodology]

Let `Y` be protected outcome and `P` the prediction artifact. A prospective result requires custody showing `P`, its scoring rule and its falsifier were fixed before any process with access to `Y` could modify them.

At minimum freeze:

```text
property/morphology vector;
phase/crossover or impossibility prediction;
negative twin;
score/falsifier;
parent-reduction set;
protected outcome source.
```

Surface remint alone does not establish prospective custody. The preregistered composition laws recorded around #663/#665 are valuable family-scale prospective predictions, not by themselves a universal new-domain result.

## T602-17 — causal observational alias iff target fails to factor through observation [P1]

Let admitted causal state be `θ`, observational object be `O(θ)` and registered interventional/counterfactual target be `I(θ)`. Observational prediction is sufficient for `I` iff a function `g` exists with

\[
I=g\circ O.
\]

Equivalently,

\[
O(\theta_1)=O(\theta_2)\Rightarrow I(\theta_1)=I(\theta_2)
\]

for every admitted pair.

**Proof.** Factorization immediately gives the implication. Conversely, if `I` is constant on every fiber of `O`, define `g(o)` as the common `I` value on that fiber; the implication makes `g` well-defined. ∎

So observational prediction aliases causal states exactly when equal observational objects can correspond to different causal targets. No learner restricted to `O` can identify both correctly. This closes the missing formal converse in #602 I5; SCM/identifiability theory owns the causal semantics.

### T602-17b — active-causal parent subtraction

For an experiment/intervention policy, exact target identification at terminal time occurs iff every positive-probability terminal transcript cell lies wholly inside one `I`-equivalence class. Minimizing intervention/probe cost subject to that condition is active causal learning/Bayesian experimental design/value-of-information territory. GMI has no separate intervention-algorithm novelty unless a residual survives those parents.

## T602-18 — cross-substrate identifiability boundary [P1/P4]

Let measurement map `ψ` send biological/physical substrate states to registered observations. If `ψ(s1)=ψ(s2)` while the protected GMI capability target differs, no predictor using only `ψ` can be correct on both. This is T602-01 applied to the substrate-measurement channel.

Thus G10 cannot be earned by analogy. It requires held-out operational measurements/interventions preserving the needed distinctions and comparison against the strongest cognitive/neuroscience parent. The identifiability condition is P1; the cross-substrate bridge is P4.

## T602-19 — fixed-sample concentration is not adaptive validity [P1/P3]

For iid `X_i in [0,1]` with mean `μ`, Hoeffding gives

\[
P(|\bar X-\mu|\ge\epsilon)\le2e^{-2N\epsilon^2}.
\]

This licenses a fixed-sample statement under its assumptions. It does not license repeated adaptive inspection of the same protected sample followed by the original fixed-test guarantee. Adaptive reuse needs fresh protected data or an adaptive/sequential-validity theorem.

Remint is an anti-leakage/invariance check, not statistical independence. #681's Hoeffding experiment is correctly a controlled synthetic P3 test, not real-world uncertainty evidence.

## T602-20 — finite-data extrapolation non-identifiability [P5]

For distinct observed inputs `x_1,...,x_n`, let any fitted law `f` match the observations. For nonzero `a`, define

\[
g_a(x)=f(x)+a\prod_{i=1}^n(x-x_i).
\]

Then `g_a(x_i)=f(x_i)` for every observed input while the functions can diverge arbitrarily outside the observed set as `a` varies.

Therefore finite exact fit does not identify an unrestricted out-of-range law. Extrapolation requires a preregistered model/regularity class plus protected out-of-range evaluation. #681's affine restriction and frozen `n=17,31` tests are a valid finite test of that class, never proof of universal scaling.

## T602-21 — complete lifecycle accounting invariant [P1]

Fix the system boundary. Partition registered run events into disjoint lifecycle stages `E_j`, with their union covering every charged event. For resource coordinate `k`,

\[
c_k=\sum_j\sum_{e\in E_j}c_k(e).
\]

Overlapping stage event sets double-count; omitted proposal failures, compilation, acquisition, migration, verification or maintenance undercount. An event may contribute to several *resource coordinates* through its cost vector, but it belongs to one lifecycle stage for stage aggregation. Scalarization still needs a preregistered price vector.

This turns #602 N into an auditable condition.

## T602-22 — theorem / certificate / empirical separation [P1 governance]

A theorem artifact contains definitions, assumptions, statement and derivation independent of witness code. A P2 exhaustive certificate may verify a finite instance or refute a universal, but cannot promote an otherwise unproved universal statement to P1. A P4 positive does not become P1–P3 by wording.

Every theorem-shaped #602 row therefore needs:

```text
formal statement/proof;
independent finite checker or proof assistant where feasible;
hostile/countermodel for omitted assumptions;
claim ceiling.
```

## T602-23 — #602 closure is a dependency conjunction [P1]

Let the four target maps be architecture/domain derivation `A`, capability prediction `B`, development prediction `C`, and domain discovery `D`. Let the claim rung `r` require a registered gate set `Gates(r)` such as parent subtraction, prospective custody, negative twins, neutral recovery, replication, real transfer and falsification.

Then scientific closure at rung `r` is

\[
Closure_r(\Omega)=A_r\land B_r\land C_r\land D_r\land\bigwedge_{g\in Gates(r)}g.
\]

A single open required antecedent blocks that higher-rung claim. GitHub issue state or checkbox percentage is not scientific closure.

---

# 5. #602 section-by-section gap derivation

Legend: `F` formal proof, `C` finite/exhaustive certificate, `P` prospective protected test, `R` real/independent replication, `S` parent subtraction, `X` impossibility/limit.

### A — foundations

A1's formal language is mostly present in `DEFINITIONS_V2_EXACT.md`: typed primitive `(S,I,O,δ,F,α,c)`, five combinators, no-smuggling update closure, bounded compilation, basis equivalence and universal-computation null. T602-03/04 close the remaining logic. Still required: `C` compensation-aware removal for every primitive and enumeration of K-equivalent minimal bases. Multiple equivalent minima is a valid terminal.

A2/A3/A4 are G1 registration objects; no higher rung follows automatically.

### B — known forms

#431's 12 derivation atoms remain the correct per-family gate. Protocol declaration is weaker than measured evidence. Existing audits show incomplete lower-bound/control/frozen-prediction/replication coverage. T602-01/02/05/07/08/09 give the formal proof shapes; remaining work is largely `C/P/R`.

Do not infer closure for still-weak families merely from a descriptive derivation. Sparse/local routing, long-sequence state-space recovery, generic rule/rewrite induction and library pressure, held-family ensemble/low-rank/generative/control response, and real task-sequence routing/search must each end in parent-sufficient, bounded residual or preserved failure.

### C — learning laws

Universal closure is impossible by T602-08. Correct closure object:

```text
registered ecology/feedback/structure/resource assumptions
 -> admissible parent law set
 -> frozen law/frontier prediction
 -> neutral recovery + negative twin.
```

Gradient/Bayes/rule/evolution mechanisms are parent-owned. Remaining class is `P/S`, not missing generic algebra.

### D — morphology phase laws

T602-06 supplies the generic information-conditioned decision law; #674/#676/#680 supply bounded prospective phase instances while preserving failures. #681 correctly isolates the remaining phase-boundary uncertainty and out-of-scale extrapolation tests. T602-19/20 establish their limits. Remaining: `P3/P`, not universal proof.

### E — reachability/morphogenesis

T602-07 supplies the formal distinction. For each claimed morphology require grammar support `F/C`, nonzero search support `F/C`, charged hitting burden `F/P`, identity-hidden neutral recovery `P`, and alternate search-encoding/remint `P`. Zero target mass is `INCONCLUSIVE_GRAMMAR/SEARCH`, not theory falsification.

### F — capability prediction/interactions

F1 contracts are registration; F2 lower/ceiling results and F3 bounded interaction laws have dedicated evidence. T602-09/10 supply the general information and interaction limits. F4 remains `P`: predict a previously unmeasured interaction before search. No universal synergy sign exists.

### G — capability species

T602-13 supplies the missing formal species object. Remaining `C/S/P`: quotient implementation-equivalent systems, attack bounded reductions, identify capability/resource regions, predict a held-out frontier/species.

### H — development/evolvability

#233 owns the developmental state. T602-05/11/12 supply generic reuse, switching-history and useful-descendant laws. Meta-learning/OOPS/PowerPlay/evolution/library parents receive first refusal. Remaining `P/R`: future-task burden, harmful-transfer twin, continued-vs-reset lineage, and complete lifecycle cost.

### I — cognitive functions

Dedicated finite derivations cover much of I. T602-17 closes the missing causal-alias converse and T602-17b parent-subtracts active causal learning/Bayesian experimental design. Remaining I work should be typed as parent-owned, finite certificate, prospective reachability, or real-scale evidence rather than vague “derive cognition”.

### J — domains

T602-14/15 close the formal logic. Finite registered closure is decidable; universal semantic closure is not. ND1/DC1/DC2/ND2 and later candidates remain `C/S/P/R`; none is a new domain until bounded reductions fail with material burden separation and held-out recovery.

### K — unseen forms

T602-16 gives the custody gate. Existing preregistered family-level composition laws are useful prospective predictions but not alone a new intelligence form. Remaining `P/S/R`: genuinely held-out property vector, neutral recovery, strongest-parent reduction, disjoint encoding and claim-appropriate transfer.

### L — natural intelligence

T602-18 gives the identifiability boundary. The bridge itself is irreducibly `P/R/S`: operational measurement/intervention, strongest cognitive/neuroscience comparator, held-out prediction and cross-population/substrate replication. Analogy is non-evidence.

### M — statistical validity

T602-19 supplies the formal fixed/adaptive distinction. Every empirical claim must register sampling unit/dependence, freeze point, multiplicity/adaptivity handling, confidence method, protected-holdout lineage and replication unit. Actual real-world power/coverage remains empirical.

### N — lifecycle accounting

T602-21 supplies the formal invariant. Remaining `C`: event partition and instrumentation proving no omission/double-counting plus explicit price/budget custody.

### O — proof programme

T602-22 supplies the proof-class rule. Remaining work is independent formal translation/certification of theorem-bearing rows where feasible; tests accompany, never substitute for, proof.

### P — falsification registry

Each claim row needs a machine-readable terminal such as:

```text
HOLDS_AT_REGISTERED_SCOPE
FALSIFIED
PARENT_SUFFICIENT
INCONCLUSIVE_GRAMMAR
INCONCLUSIVE_SEARCH
NON_IDENTIFIABLE
RESOURCE_DOMINATED
FORMAL_IMPOSSIBILITY
CANNOT_CHECK_<reason>
```

Earlier negatives remain immutable evidence.

### Q — parent subtraction

This document supplies a human-readable first-refusal atlas. The empty `PARENT_LEDGER_V2.json` must be repopulated machine-readably. Custom mechanism work is blocked where matched-scope residual is empty.

### R — tiny-world microscopes

Tiny worlds are P2 calibrators. Require universe definition, exhaustive coverage/hash, mutation/negative control, remint and deterministic receipt. They can refute universal claims and validate finite instances; they do not establish real-scale transfer.

### S — neutral emergence

Combine T602-07 and T602-16. Minimum design: family-blind grammar, protected descriptor freeze, charged search, target-support audit, negative twin, alternate search encoding, phenotype classification only after search.

### T — real-scale transfer

No formal theorem substitutes for the real-scale observation. Formal work can specify transfer certificates and sampling/evaluation contracts only. Real code/Lean/science/physical transfer remains `P/R` when required by the rung.

### U — scaling/extrapolation

T602-20 proves unrestricted finite-to-out-of-range extrapolation is non-identifiable. Any scaling claim must freeze its function/regularity class before holdout. #681 is a proper finite prospective test of its affine class; universal scaling is `X`, real-world scaling is `P/R`.

### V — final closure

Use T602-23. Final certificate must enumerate every required antecedent and fail closed on any open dependency. A closed issue state cannot override an open scientific dependency.

---

# 6. Atomic blockers remaining after the formal pass

These are evidence/infrastructure obligations, not hidden missing theorems:

1. A1 compensation census and alternative K-minimal-basis enumeration.
2. B1 per-family completion of lower bounds, true controls, prospective freezes, disjoint re-derivation and required real replication.
3. C prospective architecture-free learning-law selector and neutral recovery.
4. D execution of #681 uncertainty/extrapolation holdouts.
5. E grammar-support/search-mass and neutral morphology reachability evidence.
6. F4/G held-out interaction/species prediction after reduction quotienting.
7. H prospective developmental/evolvability burden prediction with reset/harmful-transfer controls.
8. J candidate-domain reduction tournaments and burden lower-bound separations.
9. K genuinely held-out unseen-form prediction/recovery/parent reduction.
10. L operational natural-intelligence held-out validation.
11. M/N/O/P/Q/R/S machine-readable statistical, lifecycle, proof, falsification, parent, certificate and neutral-search registries.
12. T/U real-scale transfer and protected out-of-range scaling tests.
13. V executable dependency certificate.

Therefore the strongest current statement from this artifact is:

`FORMAL_PARENT_SUBTRACTION_AND_RESIDUAL_DERIVATION_CLOSED_AT_REGISTERED_V1_SCOPE`

with

`COMPLETE_GMI_EMPIRICAL_CLOSURE_NOT_YET_EARNED`.

---

# 7. Explicitly closed formal gaps

This pass supplies theorem/limit objects for:

- universal-computation insufficiency;
- compensation-aware basis equivalence/minimality;
- lifecycle reuse/amortization;
- information-conditioned morphology choice;
- expressible/admissible/reachable separation and search hitting bounds;
- no-universal-learning-law boundary plus conditional target;
- capability information floors;
- interaction sign non-universality;
- developmental-history switching threshold;
- evolvability/useful-descendant burden;
- species equivalence/preorder;
- finite domain closure vs universal undecidability;
- new-domain acceptance gate;
- prospective unseen-form custody;
- **I5 observational/causal alias converse** plus active-causal parent subtraction;
- cross-substrate identifiability;
- fixed-sample vs adaptive statistical validity;
- finite extrapolation impossibility;
- complete lifecycle accounting;
- theorem/certificate/empirical separation;
- final closure as a dependency conjunction.

None of these statements awards an empirical checkbox whose required observation has not occurred.

# 8. Falsifiers

Revise this artifact if any theorem uses an unstated assumption, a stronger parent subsumes the claimed residual, a stated equivalence lacks transitivity at its scope, a K-equivalence uses a non-composition-closed bound while composing compilers, a causal target is called observationally unidentifiable although it factors through the registered observation, an extrapolation is claimed without a frozen class and protected holdout, or a new domain/species reduces with bounded overhead to an existing registered parent.

There is intentionally no `ALL_GMI_PARENTS_KNOWN` or `UNIVERSAL_GMI_COMPLETE` terminal.
