# OCM foundation closure V1: conditional results and executable obligations

**Status:** scoped mathematical supplement and finite engineering calibration. **Not full OCM completion, scientific admission, or a novelty claim.**

This supplement belongs to the existing #165 closure spine, especially #145, #149, #151, #152 and KS-T12. It neither changes the canonical `(F,O,Π,C)` architecture nor unlocks a learned router. Historical receipts and the frozen G2 studies are unchanged. The implementation branch was created at `ab0df16692c5e05b34a1543aa738cde7528d6315`; the direct liveness oracle is `src/ocm/kso/warrant.py`, blob `6cf431adb2e7e45fe5e23122a482262e45e11211`.

The existing V0.2 evolvability theory supplies useful research coordinates, not an unconditional efficiency theorem. This document sharpens eight obligations: constitutional preservation, incremental support maintenance, adaptive identifiability, repair-search burden, action-specific stopping, lifetime payback, inferential validity, and lifecycle-safe abstraction. Each result states what its assumptions buy and what remains outside its scope. The accompanying gap ledger is an audit of outstanding evidence obligations, not a second roadmap and not an exhaustive enumeration of every possible future defect.

## 1. Objects and claim types

Retain the canonical machine `M_t=(F_t,O_t,Π_t,C)`. Its complete execution state must also bind the evidence/revocation epoch, scope, authority, goal, resource envelope, environment version, and lineage predecessor. These are part of the state relevant to checking even when an implementation stores them in separate components. A proposal `Δ_t` has no authority merely because `Π_t` selected it.

Distinguish four predicates for a learned method `m`:

| Predicate | Meaning | Insufficient substitute |
|---|---|---|
| Correctness | An identified checker establishes a stated property at a stated scope. | The search procedure returned a candidate. |
| Usefulness | A registered comparison finds a specified downstream benefit. | The program is shorter or correct. |
| Acquisition lineage | The method was obtained from the declared prior information and episodes. | A convenient method was inserted after test access. |
| Current authorization | Its current supports, scope and external authority permit this use. | It was once useful or once admitted. |

A correctness proof does not prove useful acquisition; a useful method does not prove an architectural residual; an architectural residual in one ecology does not establish general intelligence. The classical mechanisms below remain parent-owned [R1–R10].

## 2. FC-T1 — conditional constitutional preservation

**Assumptions.** Let `I(S)` be the conjunction of the registered constitutional invariants. The initial state satisfies `I`. The external shell is outside the proposed modification's authority. Every externally consequential accepted transition, including speech and self-change, passes a checker which is sound for the obligation `I(S) ⇒ I(S')`. Rejected and uncheckable proposals do not modify committed state or perform unregistered external effects. Metering and identity binding are included in the checked transition contract, rather than presumed to follow from a content hash.

**Statement.** Every committed state reachable through that transition interface satisfies `I`.

**Proof.** The initial state satisfies `I` by assumption. Given a committed predecessor satisfying `I`, acceptance entails the checked implication and therefore the successor satisfies `I`. Rejection leaves the predecessor committed. Induction on the finite committed trace proves the result. A trace prefix of any infinite execution is covered by the same argument. ∎

**Boundary.** This is a verification obligation for the shell, not a proof that today's entire runtime satisfies it. It establishes neither the truth of unchecked world evidence nor the correctness of the checker, filesystem durability, callback isolation, or resource observations. Those require separate implementation evidence. A caller-controlled epoch string is an identity check, not a proof of the caller's honesty. `UNKNOWN` and `CANNOT_CHECK` remain representable and cannot be silently converted to acceptance.

**Falsifiers.** A callback with an ungoverned state mutation, stale predecessor binding, a checker selected by the challenger itself, or post-check speech containing new unsupported claims violates an assumption. The correct response is to reopen the applicable invariant, not cite this induction as protection.

## 3. FC-T2 — exact incremental liveness for a frozen warrant snapshot

### 3.1 Semantic contract

The existing `WarrantProfile` is an interval `(L_i,U_i)` of canonical antichains of finite evidence sets, ordered `L_i ≤ U_i` in the existing monotone Boolean order. For revoked identities `R`, define

`b_w(R) = |w ∩ R|`,

`a_i^-(R) = Σ[w in L_i] 1[b_w(R)=0]`,

`a_i^+(R) = Σ[w in U_i] 1[b_w(R)=0]`.

The answer is `LIVE` when `a_i^- > 0`, `DEAD` when `a_i^+ = 0`, and `UNKNOWN` otherwise. The interval order guarantees that a surviving lower warrant implies a surviving upper warrant. This is exactly the existing oracle, not a new definition of authority. Alternative clauses remain alternatives; members of one clause remain conjunctive. ATMS and provenance support are inherited mechanisms [R1,R2].

### 3.2 Construction and update

`WarrantLivenessIndex` interns identical support sets into clauses. It stores each clause's blocker count, evidence-to-clause incidences, clause-to-object/bound incidences, and each object's two live-clause counts. **Both bounds are indexed.** The existing `WarrantProfile.evidence` exposes only lower evidence and is therefore insufficient for constructing this index.

For one batch, first deduplicate and validate finite requested revoke/reinstate lists. Overlapping requests are rejected before mutation. Let `A` be newly revoked identities and `B` newly reinstated identities. They are disjoint. The final state is `R'=(R\B)∪A`, so

`b_w(R') = b_w(R) + |w∩A| - |w∩B|`.

The index aggregates the entire batch before propagating liveness changes. Only clauses whose zero/nonzero blocker status changes alter object/bound counts. It then reports final object liveness changes. It does not report transient `DEAD` or `UNKNOWN` changes from an arbitrary ordering of one mixed batch.

**Statement.** For any valid frozen profile snapshot, valid initial revoked set, and sequence of valid serialized batches at its bound epoch, indexed answers equal direct `WarrantProfile.liveness` after every batch.

**Proof.** Construction computes the defined blocker counts and live-clause sums. Assume these equal their definitions before a batch. The displayed set identity gives the exact next blocker count for every touched clause. Untouched clauses contain no changed evidence, so retain their exact count. The truth value `b_w=0` changes precisely for the clauses propagated by the algorithm. Updating each incident bound by the change in that indicator therefore restores the defining sums. Applying the three-way decision rule yields the direct oracle. Induction over batches completes the proof. ∎

### 3.3 Work and storage statement

Let `r` count input entries including duplicates, `D` be identities whose revoked membership changes, and `WΔ` be clauses whose live status changes. Under expected-amortized constant-time dictionary access and bounded-cost identifier operations,

`T_batch = O(r + Σ[e∈D] degree_e(e) + Σ[w∈WΔ] degree_bound(w))`.

The final touched-object work is bounded by these incidences. Unknown evidence has zero incidence work but still incurs input/set work and remains in the revoked set. Duplicate input consumption is not free. Global answer snapshots cost `O(number of objects)`; revoked-set snapshots cost `O(|R|)`. Build, profile canonicalization, hashing, serialization, persistence, allocation, and integer bit complexity are separately charged. No physical speedup follows merely from these operation counts.

Storage is proportional to objects, distinct clauses, evidence-clause incidences, clause-bound incidences, and retained revoked identities. Canonical antichain construction can itself be expensive; it is not hidden inside a supposed constant-time build. Large shared-support fanout is genuinely large work. Exact explicit reporting of `k` changed identities requires at least `k` output entries, so an update bound independent of affected fanout would be false.

### 3.4 Implementation and scope of closure

The new module is an **optional snapshot index**. No production call site is switched to it. Profile, operator, scope or authority changes require a new externally bound epoch and rebuilding. The owning runtime must serialize calls. Planned validation precedes mutation, but the object does not provide crash atomicity, durable replay, rollback after `MemoryError`, or a transaction protocol. Evidence identifiers must have stable, side-effect-free hash/equality behavior.

Finite tests cover all 168 valid intervals over three evidence identities and all 64 ordered revoke-set transitions: **10,752 oracle comparisons**. Random mixed batches add 24,000 comparisons. Tests also cover upper-only evidence, incomplete support, redundancy, conjunction, two blockers, shared clauses, stale epochs, immutable results, idempotence, input failure, and 5,000 unrelated profiles. Two planted faulty alternatives are detected: omitting upper-only incidences and treating a multi-blocker clause as a single Boolean blocker.

This discharges the **frozen-profile liveness-maintenance sub-obligation** of KS-T12, subject to the proof assumptions. It does **not** discharge general lifecycle-safe macro discovery, dynamic dependency maintenance, cyclic derivation, abstraction transport, integrated restart/replay, or whole-runtime KS-T12.

## 4. FC-T3 — adaptive diagnostic information bounds

Let `Z` be uniform over `m≥2` responsible causes. The complete pre-probe history `H_(i-1)` includes previous queries, results, and an independent algorithmic random seed. The next query is selected using that history. There is no undeclared side channel giving the selector additional information about `Z`.

**Load-bearing assumption.** At every reachable active history and legal query, the *conditional* information supplied by the next observation is at most `b` bits. A marginal assertion `I(Z;Y_i)≤b` is not enough without additional independence/channel assumptions. This is the adaptive distinction required by the information-theory parents [R3,R4].

For target error `0≤ε<1−1/m`, write

`J(m,ε)=log2(m)−h2(ε)−ε log2(m−1)`.

**Statement.** A fixed `n`-probe strategy attaining error at most `ε` requires `n≥ceil(J/b)` when `b>0`. For a bounded history-adapted stopping time `T`, the corresponding bound is `E[T]≥J/b`, **without taking the ceiling of an expectation**. If `b=0<J`, this observation contract cannot attain the target.

**Proof.** Queries are functions of history and independent randomness, so they add no new information conditional on that history. The chain rule bounds complete transcript information by the sum of conditional observation information, at most `nb`. Fano's inequality and data processing require transcript information at least `J`. For bounded stopping, pad the trace after stopping with deterministic null observations. The active-step conditional information is bounded by `b Pr(T≥i)` after averaging histories; summing yields `b E[T]`. ∎

A cost version follows when the conditional information is bounded by `β` times conditional expected paid cost: `E[total paid cost]≥J/β`. Unbounded stopping requires additional integrability/limit justification and is not asserted here. With prior side information `W`, the remaining entropy `H(Z|W)` and a conditional Fano argument replace the uniform no-prior calculation. Prior diagnostic competence is not free new information from later probes.

**Exact counterexample to marginal addition.** Take independent fair bits `Z,N`, with observations `Y1=N` and `Y2=Z XOR N`. Each observation alone has zero mutual information about `Z`. Together they determine `Z` exactly. Thus `I(Z;Y1)=I(Z;Y2)=0`, but `I(Z;Y1,Y2)=1` and `I(Z;Y2|Y1)=1`. The reference computes this four-outcome distribution, rather than estimating it from samples.

**Calibration.** For `m=30, ε=.05`, `J≈4.3775946` bits. Caps `.1,.25,.5,1,2` bits give fixed-horizon lower bounds `44,18,9,5,3`. A two-bit cap gives only `E[T]≥2.1887973` for expected stopping time. These are necessary information bounds, not constructive sufficient algorithms or measured OCM diagnostic ability.

## 5. FC-T4 — repair search burden is not Shannon effective count

The V0.2 quantity `χ=2^H(R|e)` can remain a diversity descriptor. It must not be substituted for expected repair evaluations. Guesswork and Shannon entropy are different objects [R5].

For a bounded reference model, assume exactly one acceptable repair among `n` candidates, probabilities `p_i`, known deterministic test costs `c_i>0`, no shared test work, and a failed test revealing only that this candidate is not the correct one. The successful repair must be tested before use. For order `π`,

`E[C_π]=Σ_i p_i Σ_(j≤rank_π(i)) c_(π(j))`.

**Statement.** An optimal ordering sorts decreasing `p_i/c_i`.

**Proof.** Consider adjacent candidates `i,j`. Their ordering does not change costs on paths where a later candidate succeeds. On the two affected success paths, the expected cost of `i,j` minus `j,i` is `p_j c_i−p_i c_j`. Placing `i` first is no worse precisely when `p_i/c_i≥p_j/c_j`. Exchanging inversions yields an optimal sorted order. ∎

For probabilities `(.6,.4)` and costs `(100,1)`, probability-only ordering costs `100.4` in expectation, whereas cost-aware ordering costs `61`. Exhaustive permutation tests check 729 distinct three-candidate probability/cost settings.

**Counterexample to entropy as search cost.** Let one repair have probability `1−ε` and `M=2^k` alternatives each have probability `ε/M`, with `ε=1/k`. Then

`H=h2(1/k)+1`, while `E[guesses]=1+(M+1)/(2k)`.

Entropy tends to one bit as `k` grows, while expected unit-cost guesses diverge. At `k=20`, entropy effective count is below `2.5`, but expected guesses are **26,215.425**. Low entropy alone cannot establish affordable repair.

**Boundary.** Multiple acceptable repairs, information-rich failures, state-dependent costs, correlated evaluations, side effects and shared computation require a richer search model, often a Bellman recursion. The reference ordering theorem does not certify those settings. Report posterior assumptions, full cost distribution, and failure outcomes; do not call `χ` a sufficient statistic for evolvability.

## 6. FC-T5 — stopping is relative to decisions and future value

Let `Θ` be surviving admissible world models and `A(θ)` their permitted actions. A common *safe* action need not be a common *optimal* action. Information can still change which safe action has the highest utility.

**Statement.** Suppose one action `a*` is pointwise utility-maximizing for every surviving model, with the same complete registered continuation consequences. Suppose a contemplated diagnostic experiment cannot change the feasible actions, the world, the utility function, or any future decision beyond this choice, and incurs nonnegative cost. Then taking `a*` immediately is at least as valuable as that experiment followed by any action.

**Proof.** In every model, any experiment-conditioned action has utility at most that of `a*`. Average this pointwise inequality over observation randomness and any admissible prior; subtract the experiment's nonnegative cost. ∎

The continuation assumption is essential: an answer can be correct now while its trace, support or reusable state has different future value. For multi-stage cognition, compare stopping against the full Bellman alternative

`V(s)=max{V_commit(s), max_q[-cost(q,s)+E[V(s')|s,q]]}`

at a registered finite horizon and fully specified state/transition model. Computing that expectation and the policy is also paid work. This is ordinary metareasoning, not an OCM-owned principle [R6].

A one-step value-of-information calculation is not generally a global stopping proof. In the XOR example, each individual observation has no action value for predicting `Z`, but the pair can determine it. A strictly myopic gate rejects both even when their combined cost is below the value of an exact answer. Conversely, information gain about distinctions irrelevant to every future registered action need not be useful. The current exact-routing gate stays closed unless a measured residual and legally informative features warrant reopening it.

## 7. FC-T6 — lifetime payback under invalidation and complete costs

Use a resource vector rather than an outcome-selected scalar. Additive coordinates include paid compute, checker work and I/O. Peak memory is a maximum over time, not the sum of successive resident sizes. Capacity, retained storage, latency, and information exposure may impose constraints rather than a freely exchangeable price. Scalar results require a price vector fixed before outcome access.

The general expected surplus of a persistent method is

`E[Σ_(t≤H) 1[valid and available at t] (saved_work_t−carry_cost_t)]`

`− acquisition − validation − integration − maintenance_not_in_carry − migration − revocation/replay − assurance`.

Do not multiply expected reuse by expected survival unless the needed independence or conditional model is stated. Do not charge a cost twice, and do not omit a cost because a parent absorbs it into another component. Quality, current authority and capability constraints must hold before a cost saving counts.

**Exact special case.** A method is initially alive. After each served opportunity it independently survives with probability `s`. Its conditional expected net gain at every alive opportunity is constant `g`, build cost is `F`, and invalidation costs `R` once if it occurs by opportunity `H`. No regeneration, final liquidation charge or discounting is assumed. Then

`Δ_H = g(1−s^H)/(1−s) − F − R(1−s^H)` for `s≠1`,

and `Δ_H=Hg−F` for `s=1`.

**Proof.** Opportunity `t` is reached alive with probability `s^(t−1)`. Linearity of expectation gives a geometric sum of gains. Invalidation by `H` has probability `1−s^H`. Subtract the declared costs. ∎

For stable deterministic reuse and positive `g`, the first integer horizon with **strict** payback is `floor(F/g)+1`; an equality is not a positive residual. At `F=10,g=2`, five uses merely break even and six pay back. At horizon ten, stability yields surplus ten, whereas survival `.5` yields a negative surplus even before adding revocation cost. Longer nominal lifetime does not imply longer usable lifetime.

Componentwise lower cumulative costs at matched quality and no worse non-additive constraints imply no greater scalar cost for every nonnegative price vector. Mixed-sign cost differences establish a price-dependent trade, not universal efficiency. The current reference produces these arithmetic checks only; it measures no physical OCM speedup.

## 8. FC-T7 — evidence needed for causal and statistical closure

### 8.1 Causal contrast

The G2 estimand must specify the population, predecessor state, intervention, outcome coordinate, horizon and unit of replication. Compare a live learned object against its preplanned removal/revocation from an otherwise matched predecessor, and also against an ordinary persistent system receiving the same method and checking powers. Record actual invocation identity; a library's presence alone is not consumption.

A paired controlled run can establish a finite causal effect in its registered deterministic ecology when interventions differ only as intended. It cannot by itself establish a population effect, rule out an untested answer-cache explanation, or prove architectural uniqueness. Counterfactual arms need separate mutable state reconstructed from matched snapshots and matched exogenous streams. Sharing one live object graph across arms creates interference; reconstructing historical state from current mutable metadata can corrupt the contrast.

Acquisition and admission tasks cannot become fresh test tasks under new labels. Data identity is semantic where the task admits an exact canonical identity. Changing the learner, utility estimator, task grammar, or decision rule after exposure requires a successor registration, not a retroactive repair of the earlier terminal. DreamCoder and Stitch are strong component parents [R7,R8]; compressing a corpus is not sufficient evidence of fresh-task utility.

### 8.2 Conservative time-uniform bound

Let `X_j∈[a,b]` be bounded observations from independent replicate lifetimes with a common mean `μ`, or more generally bounded observations satisfying the fixed conditional-mean assumption `E[X_j|past]=μ`. Predeclare `K` comparison streams; independence between streams is unnecessary for a union bound. Allocate two-sided error `δ/[K n(n+1)]` to stream/look `n`. Set

`w_n=(b−a) sqrt(log(2K n(n+1)/δ)/(2n))`.

**Statement.** With probability at least `1−δ`, every registered stream's sample mean is within its radius of its mean at every positive integer look.

**Proof.** The bounded-variable exponential inequality gives a two-sided tail at most `2 exp(−2n w_n²/(b−a)²)=δ/[K n(n+1)]`. Summing across streams and looks uses `Σ_(n≥1)1/[n(n+1)]=1`. ∎

This elementary confidence sequence is deliberately conservative; sharper time-uniform constructions are established parents [R9]. Under changing conditional means, the analogous concentration target is the average predictable conditional mean, not a stationary population capability claim. If one evolving lineage supplies many tasks, those tasks must not automatically be treated as independent lifetimes. Cluster at the correct experimental unit or justify a valid conditional model.

Adaptive challenger selection additionally requires fresh conditionally valid comparisons and an error budget across proposals. Restarting the significance budget after each rejection invalidates programme-wide control. Multiple gates, outcomes and resource prices cannot be selected after looking at results without charging that selection.

Zero observed failures are not zero failure probability. Under fixed-`n` independent Bernoulli trials, the one-sided upper bound is `1−α^(1/n)`; at `n=100, α=.05` it is approximately `.029513`. This fixed-`n` calculation is **not** an anytime guarantee. Neither formula verifies its own sampling assumptions. Floating-point helpers are research references, not admission decisions at exact numerical thresholds.

## 9. FC-T8 — abstraction must preserve the registered lifecycle

The existing KS-T07b conjunction of navigation lumpability and warrant measurability is relative to the registered navigation/revocation interface. It must not be read as a certificate for every future operator, dialogue behavior or self-modification.

For a deterministic finite reference, let `q:S→B` be a quotient, `obs(s)` contain all registered external distinctions, and `T_a` range over the complete registered action alphabet. Require for all `q(s)=q(t)`:

`obs(s)=obs(t)` and `q(T_a(s))=q(T_a(t))` for every registered `a`.

**Statement.** Every finite registered action word has representative-independent abstract successors and observable outputs.

**Proof.** Observation equality gives the empty-word case. Transition congruence gives a unique next block for each current block and action. Induction on action-word length gives the same blocks and therefore the same observations throughout the word. ∎

For stochastic transitions replace successor-block equality by equality of the probability assigned to each block, together with the registered observation/reward contract. This is ordinary lumpability/bisimulation machinery, not a new architecture result [R10]. Revocation, reinstatement, learning, scope changes and restart must be included if the certificate claims to cover them. Missing actions are not proved by a finite checker.

**Counterexample.** States `x,y` share a current observation and block; `z` has a distinct observation and block. Under only the identity operation the quotient is valid. A new operation sending `x` to `z` but leaving `y` unchanged invalidates it. The reference returns the two-state witness. Operator-set changes therefore invalidate or reopen the corresponding certificate unless a new proof covers the enlarged alphabet. Good current-answer compression is insufficient for lifelong semantic preservation.

## 10. What this closes, and what it does not

The supplement provides conditional proofs and executable counterexamples for the eight stated obligations. Only FC-T2 adds a production-package component, and that component is not adopted into runtime serving here. The other helpers are research calculations. No learned-method utility study, cross-domain experiment, long-lived developmental trial, independent replication, or whole-system physical comparison was executed as part of this change.

Local validation uses the exact retrieved warrant source blob plus the new files, not a full repository clone. The full repository suite, installed distribution, integrated runtime, and remote CI are separate checks. Passing these focused tests cannot renew the September-reopened historical M11/M12 scientific claims.

The G2 length-scaling negative at `4c5d3ec...` and utility-aware tournament negative at `ab0df166...` remain intact. They motivate a materially different, prospectively specified acquisition/search mechanism or a scoped negative programme outcome, not repeated tuning of the same exposed evaluation. `PARENT_SUFFICIENT`, harmful transfer, utility rejection and `CANNOT_CHECK` are valid terminals. Nothing here asserts that all programme gaps are now closed.

### Cross-check obligations before adoption

| Review perspective | Question that must survive | Current disposition |
|---|---|---|
| Formal semantics | Does every upper and lower support transition agree with the oracle? | Conditional proof plus exhaustive small-universe tests. |
| Information and decision theory | Are history, side information, costs and continuation value declared? | Corrected assumptions and finite counterexamples; deployment assumptions unmeasured. |
| Experimental design | Are fresh tasks, causal interventions, parents and replication units genuinely matched? | Explicit gate; no new empirical claim. |
| Runtime assurance | Is the index bound to the actual state transaction and durable lifecycle? | Not integrated; adoption remains gated. |

## References and parent ownership

[R1] Johan de Kleer. *An assumption-based TMS*. Artificial Intelligence 28(2), 127–162, 1986. DOI: 10.1016/0004-3702(86)90080-9. Support environments are a parent, not an OCM invention.

[R2] Todd J. Green, Grigoris Karvounarakis, Val Tannen. *Provenance Semirings*. PODS 2007. DOI: 10.1145/1265530.1265535. Provenance algebra is inherited, as already declared by `warrant.py`.

[R3] Jonathan Scarlett, Volkan Cevher. *An Introductory Guide to Fano's Inequality with Applications in Statistical Estimation*. arXiv:1901.00555v3, 2019, especially §§2–3 and Lemma 3. The information lower-bound machinery is parent-owned.

[R4] Jonathan Scarlett, Volkan Cevher. *Lower Bounds on Active Learning for Graphical Model Selection*. AISTATS, PMLR 54:55–64, 2017. Active information bounds require appropriate conditional analysis.

[R5] Mark M. Christiansen, Ken R. Duffy. *Guesswork, large deviations and Shannon entropy*. IEEE Transactions on Information Theory 59(2):796–802, 2013; arXiv:1205.4135. DOI: 10.1109/TIT.2012.2219036. Entropy and expected guessing burden are not interchangeable.

[R6] Stuart Russell, Eric Wefald. *Principles of metareasoning*. Artificial Intelligence 49(1–3):361–395, 1991. DOI: 10.1016/0004-3702(91)90015-C. Paid computation and decision value are parent-owned.

[R7] Kevin Ellis et al. *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*. PLDI 2021. DOI: 10.1145/3453483.3454080. Learned libraries and search guidance are component parents.

[R8] Matthew Bowers et al. *Top-Down Synthesis for Library Learning*. POPL 2023. DOI: 10.1145/3571234; arXiv:2211.16605. Stitch is a library-learning parent, not evidence that any particular OCM library has future utility.

[R9] Steven R. Howard, Aaditya Ramdas, Jon McAuliffe, Jasjeet Sekhon. *Time-uniform, nonparametric, nonasymptotic confidence sequences*. Annals of Statistics 49(2):1055–1080, 2021. DOI: 10.1214/20-AOS1991; arXiv:1810.08240v9. Time-uniform inference is parent-owned; our elementary union-bound calibration is not their sharper construction.

[R10] John G. Kemeny, J. Laurie Snell. *Finite Markov Chains*, 1976 edition. Lumpability is the parent already identified by `KSO_REPRESENTATION_ABSTRACTION_V1.md`; no all-operators guarantee follows from one fixed navigation matrix.
