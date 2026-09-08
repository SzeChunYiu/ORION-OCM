# Constructive whole-lifetime benefit: a finite relational cost certificate

**Status:** conditional mathematical derivations, executable finite-model checks, and an exposed native correspondence probe. Not a proof that the current OCM implementation has a general net advantage. No novelty claim.

The objective is to make an architecture claim *provable when true*, rather than assign a completion percentage to it. The parent techniques are amortized analysis [1], finite difference constraints/minimum cycle means [2], relational cost reasoning [3], and semantics-preserving incremental computation [4]. We derive the small combination needed for OCM below. Correctness of reused knowledge and economic benefit remain different obligations.

## 1. A claim with quantifiers

Fix an implementation A, a nonempty finite family of matched parents P, an admissible environment class E, a protected semantic contract K, and a prospectively registered nonzero nonnegative price vector w. Every parent receives the same task inputs, primitive algorithms, legal observations, initial information, and declared resource budgets. Persistent memory and ordinary library learning are allowed in the parent unless specifically being ablated.

A useful target is the conjunction:

1. A and every compared parent meet K on E, including the registered revocation, restart, refusal, and failure semantics;
2. all compared costs include construction, discovery, checking, feature acquisition, policy execution, maintenance, updates, persistence, recovery, and deployment overhead;
3. for every admissible lifetime omega with H completed demand units,

   `min_P [C_P(omega) - C_A(omega)] >= delta H - D`,

   where delta > 0 and D is finite and published.

The inequality permits initial investment losses up to D. It implies strict improvement beyond H > D/delta for lifetimes that actually exist in E. This is a conditional family-level guarantee, not universal superiority over every algorithm or workload. A statistical expected-cost claim is a distinct, weaker quantifier and must be labelled accordingly.

A costly refusal is not silently counted as task completion. Progress units must be paired and fixed by K, not selected independently by each arm. Comparing faster failure against a successful parent is not economic noninferiority.

## 2. Paired lifecycle model

For one parent P, use a finite directed multigraph G=(S,E,s0). A state abstracts a *pair* of machine states plus the relevant environment state. It must retain enough information for future authority, support, persistent state, and cost behavior. The parent state is a proof/evaluation device: it is not free information supplied to the deployed controller.

Each edge e:s->t has a nonnegative integer demand increment d(e) and nonnegative rational resource vectors c_P(e), c_A(e) of the same dimension. Zero-demand edges are allowed for invalidation, checkpoints, maintenance, or internal computation. They still incur cost. Define

`g_w(e) = w . (c_P(e) - c_A(e))`.

The graph describes already specified lawful policies. Universal quantification over paths treats unresolved inputs/nondeterminism adversarially. The algorithm below does not synthesize a better controller, choose a demand prior, or confer an observation channel.

Resource coordinates must be additive for this sum. Peak memory, maximum retained storage, deadlines, and other nonadditive constraints require separate observations/constraints or a state augmentation. Bytes written can be additive; final retained bytes are not automatically a per-event charge. A growing append-only ledger cannot be represented by a fixed warm-state cost without an independent bound.

## 3. The potential certificate

Choose a rational rate delta and a rational potential phi:S_reachable->Q. Require, for every reachable edge e:s->t,

`g_w(e) - delta d(e) >= phi(t) - phi(s)`.                 (1)

A hash of the model binds the certificate to its declared inputs. This establishes source custody only; it does not authenticate model adequacy or software correctness.

### Theorem 1: all-prefix lifetime benefit

Suppose (1) holds. Let F>=0 bound additional fixed architecture cost relative to P that has not already been charged on edges. For any finite path s0,e1,s1,...,en,sn, let H=sum_i d(e_i). Then

`C_P - C_A >= delta H - D`,

where

`D = F + phi(s0) - min_{s reachable} phi(s)`.

**Proof.** Sum (1) along the path. The potential terms telescope:

`sum_i g_w(e_i) >= delta H + phi(sn) - phi(s0)`.

Subtract the upper bound F on extra fixed architecture costs, then bound phi(sn) below by the minimum over reachable states. This gives the stated inequality. F>=0 and the inclusion of s0 ensure D>=0. The argument holds for every prefix and needs no probabilistic independence. QED.

**Corollary.** When delta>0 the first integer demand count at which the certificate guarantees strict improvement is floor(D/delta)+1. The result says nothing about whether the environment supplies that many demands. In an acyclic finite graph, arbitrarily large claimed rates can be offset by arbitrarily large finite debt; this is not evidence of sustained useful reuse.

## 4. A constructive existence theorem and a failure witness

Let the adjusted edge weight be a(e)=g_w(e)-delta d(e).

### Theorem 2: cycle characterization

There exists a potential satisfying (1) exactly when every reachable directed cycle has nonnegative total adjusted weight.

**Necessity.** Sum (1) around a cycle. Potentials telescope to zero, so sum a(e)>=0.

**Sufficiency.** Add a synthetic source with zero-cost edges to all actually reachable vertices. If there is no negative cycle, shortest-path distances from this source are finite: removing a nonnegative cycle never worsens a walk, and there are finitely many simple paths. Let phi(v) be these distances. For every edge s->t, shortest paths obey phi(t)<=phi(s)+a(e), which is precisely (1). The synthetic source constructs the certificate and is not a runtime action. QED.

Bellman-Ford with exact rational arithmetic computes either such distances or a reachable negative cycle. The small checker independently verifies the output edge inequalities or the closed cycle; trust in the search algorithm is unnecessary for acceptance of that finite artifact.

### Theorem 3: a negative cycle refutes any finite debt at that rate

Suppose a reachable cycle z has sum a(e)=-epsilon<0. Traverse a path to z and repeat z k times. Relative to delta H, its accumulated gain tends to minus infinity as k grows. Consequently no finite D can make the all-path inequality hold. This includes zero-demand negative cycles: repeated maintenance can destroy a bound without completing any further task. QED.

A cycle in an overapproximating abstraction may be spurious. It refutes the certificate in that model; a concrete software impossibility result additionally needs a realizable path to the cycle and repeatable concrete traversals. The code never labels an abstract countercycle a proof about deployed software.

### Corollary: maximum uniform rate

Provided every zero-demand cycle has nonnegative gain, the maximum feasible rate is

`inf_{cycles z: sum d(e)>0} sum g_w(e) / sum d(e)`.

For a finite graph with a positive-progress cycle the infimum is attained on a simple cycle. Decomposing a cycle into simple cycles gives a demand-weighted average over positive-demand components, plus nonnegative zero-demand gain, proving the formula. With unit demand on every edge this is the minimum cycle mean problem [2]. If there are no positive-demand cycles, report no sustained-rate conclusion. The present implementation verifies a supplied rate; it does not claim to implement Karp's optimization algorithm.

## 5. Concrete-to-abstract transfer is the critical missing bridge

The preceding theorems are about G. To obtain a software theorem, establish a relation R between concrete paired states and abstract states such that:

- initial concrete paired states relate to s0;
- every admissible concrete paired transition has a matching edge, including all exceptional and lifecycle transitions;
- that edge preserves the protected observation K and paired progress d;
- its abstract gain is a **lower bound** on the concrete gain;
- all omitted fixed deployment cost is at most F; no recurring cost is hidden in F.

For instance c_P(e) can be a sound lower bound on the parent's actual cost and c_A(e) a sound upper bound on A's actual cost. Two unrelated *upper* bounds cannot safely be subtracted to lower-bound the gain. Relational cost reasoning [3] can retain cancellations that separate bounds would lose.

### Theorem 4: transfer to software

Under these simulation conditions and (1), induction over a concrete run constructs its matching abstract path and preserved protected observations. Sum the concrete-gain lower bounds and apply Theorem 1. The same delta H-D inequality follows for the concrete run. QED.

A measured mean or one timing observation is not a worst-case transition bound. A source hash is not the relation R. Passing native tests is evidence on exercised paths, not a proof of universal coverage. The native bridge in this directory deliberately does not construct R or export measured timings as theorem costs.

## 6. Strong parents, architecture attribution, and composition

### Theorem 5: finite parent-family certificate

For each P_j suppose `C_Pj-C_A >= delta_j H-D_j`, for the same lifetime, objective and K. Set delta=min_j delta_j and D=max_j D_j. Since H>=0, each bound is at least delta H-D. Taking the minimum over parents proves the family bound. A positive rate requires positive rates against *all* parents in the stated family. QED.

### Emulation obstruction

If an allowed parent implements the same primitive sequence, learning algorithm, state reuse, and required lifecycle work at no greater cost than A, then A cannot strictly beat that parent by virtue of its architectural label. This is direct cost comparison, not a claim about universal simulation overhead. To claim an integration advantage, identify the actual reduced duplication, cheaper maintenance, better lawful decisions, or new amortized capability that the matched parent lacks, and allow the parent to implement conventional alternatives.

The native probe uses the same arithmetic learner/solver outside OCM as a kernel correspondence parent. Equal answers and search counters are expected. Its purpose is to prevent re-crediting ordinary fragment learning as an unexplained architecture residual. It is not an independently implemented, durably persistent whole-machine parent.

### Composition counterexample

Let a base task cost10. Two isolated mechanisms each save4. If combining them introduces9 of joint validation/synchronization work, the combined task costs10-4-4+9=11. Thus two local wins imply no whole-system win. The complete paired graph must charge cross-layer effects rather than add isolated headline improvements.

## 7. Exact authored controls: success and failure regions

These are transparent mathematical examples, not measurements of OCM.

**Stable reuse.** Cold discovery costs P10 versus A16, then each warm demand costs P10 versus A3. A rate delta7 has phi(cold)=0 and phi(warm)=-13. The exact lifetime gain is7H-13 for H>=1: one demand loses6; two demands gain1. Adding fixed overhead10/3 gives debt49/3 and first strict guaranteed benefit at H3.

**Unrestricted invalidation.** Add warm->cold with zero demands and gain-2. Immediate invalidation followed by rediscovery creates a cycle with gain-8 per demand. No nonnegative uniform rate is certified, no matter how long the nominal lifetime is.

**Minimum reuse before invalidation.** If the *actual environment contract* guarantees at least k warm uses between builds, a rebuild cycle has k+1 demands and gain7k-8. With k1 the rate is negative; with k2 the limiting rate is2 per demand. This is a provable break-even condition, not permission to exclude inconvenient resets after observing them.

**Matched learning parent.** If a parent pays16/3 for cold/warm steps while A pays17/4, the warm cycle loses1 per demand. Reuse cannot repay permanent extra overhead against a parent that reuses equally well.

**Price conflict.** Saving5 arithmetic units while writing10 additional bytes improves priced cost only where5*w_arithmetic>10*w_write. It is not Pareto dominance. Raw vectors and a prospectively registered objective must remain visible.

The tests additionally check zero-demand cycles, unreachable cycles, ties, stale fingerprints, malformed costs, iterator preservation, all short paths in a dwell model, and625 complete two-state integer-weight graphs against an independently enumerated cycle formula. Executable examples do not replace the proofs above.

## 8. Probabilistic alternatives are separately scoped

A stochastic statement may replace (1) with a conditional expected drift inequality under an explicit filtration and integrable variables. Summing expectations yields the same expected bound at a deterministic transition count. At a bounded stopping time T, multiply each conditional inequality by the predictable indicator that its transition occurs before T, then sum; the expected bound follows. Extending to unbounded T requires additional integrability/uniform-integrability conditions and is not claimed here.

This is not automatically a high-probability guarantee. Conservative baseline constraints [5] and time-uniform confidence sequences [6,7] are appropriate parent literatures for future empirical admission, but their assumptions must be checked. They do not turn statistical coverage into exact output authority. No bandit or confidence-sequence implementation is introduced here.

## 9. Scientific admission gates

This tranche closes a *mathematical certificate design* gap, not the architecture claim. The next admissible evidence must bind:

1. concrete A and strong P implementations to an agreed contract and costs;
2. naturally sourced, complete lifetimes with lawful demand/lifecycle observations;
3. training/discovery, development/admission, and protected evaluation roles separated by mathematical task identity and source custody;
4. both steady reuse and naturally occurring reset/drift regimes, without selecting only profitable survivors;
5. repeated independent lifetimes, not many correlated queries counted as independent replicates;
6. all data-dependent researcher choices disclosed, including previous access to the existing142-target polynomial population.

A fresh evaluation must allow PARENT_SUFFICIENT, COST_BOUND_REFUTED, and CANNOT_CHECK_MODEL_COVERAGE. It must not use a comparator that is denied memory, a compiler, provenance, or the same primitive algorithms merely to create an architectural win. Optimizing that comparator is progress toward a stronger claim, not sabotage of OCM.

## References and reading scope

The targeted reading covered the parent families below. Full-text reading focused on the relevant definitions, algorithms, and theorems where accessible; several publisher sources supplied only abstracts/overviews. This is not a claim of exhaustive literature saturation or independent verification of the authors' proofs. The finite derivations in this note are self-contained.

[1] Sleator & Tarjan (1985), *Amortized Efficiency of List Update and Paging Rules*, CACM28(2). Author-hosted abstract and full text examined. https://www.cs.cmu.edu/~sleator/papers/Amortized-Efficiency.htm

[2] Karp (1978), *A characterization of the minimum cycle mean in a digraph*, Discrete Mathematics23(3). DOI10.1016/0012-365X(78)90011-0. Publisher abstract/formulation accessed; the difference-constraints argument is supplied above rather than represented as a rechecked proof of Karp's algorithm.

[3] Cicek, Barthe, Gaboardi, Garg & Hoffmann (2017), *Relational Cost Analysis*, POPL. DOI10.1145/3009837.3009858. Primary publication overview accessed; its type system is not implemented here.

[4] Acar, Blume & Donham (2011 full version of ESOP2007), *A Consistent Semantics of Self-Adjusting Computation*. arXiv1106.0478. Formal semantics and consistency/correctness theorem sections examined; Twelf proof appendix not independently replayed. https://arxiv.org/abs/1106.0478

[5] Wu, Shariff, Lattimore & Szepesvari (2016), *Conservative Bandits*, ICML/PMLR48. Baseline-uniform constraints and algorithms examined. https://proceedings.mlr.press/v48/wu16.html

[6] Howard, Ramdas, McAuliffe & Sekhon (2021), *Time-uniform, nonparametric, nonasymptotic confidence sequences*, Annals of Statistics49. DOI10.1214/20-AOS1991. Definitions/stitching bound sections examined; not used to claim significance in this tranche.

[7] Karampatziakis, Mineiro & Ramdas (2021), *Off-Policy Confidence Sequences*, ICML/PMLR139. Setup, observation/overlap and sequential-admission sections examined. https://proceedings.mlr.press/v139/karampatziakis21a.html

[8] Russell & Wefald (1991), *Principles of Metareasoning*, Artificial Intelligence49. DOI10.1016/0004-3702(91)90015-C. Publisher abstract accessed; full literature mapping remains in PR154's pinned LITERATURE_SYNTHESIS_V1.md.

[9] Minton (1990), *Quantitative Results Concerning the Utility of Explanation-Based Learning*, Artificial Intelligence42. DOI10.1016/0004-3702(90)90059-9. Publisher/AAAI precursor abstracts accessed. The utility problem motivates charging learned-rule matching and maintenance, not only saved search.

[10] Ellis et al. (2021), *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning*, PLDI. DOI10.1145/3453483.3454080. Primary conference overview accessed; ordinary library-learning parents must remain in comparisons. No comparative experiment with DreamCoder is claimed.
