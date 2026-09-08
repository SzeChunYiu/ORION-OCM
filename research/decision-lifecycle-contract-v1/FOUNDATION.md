# Decision and lifecycle foundation: a bounded completion

Status: hand-proved conditional propositions plus exposed executable finite checks.
This is a supplement to #145 and #152, not a replacement for ORION-V2, #165,
or the repository constitution. No general-intelligence, useful-learning,
minimal-vessel, physical-efficiency, or protected-evaluation terminal is awarded.

## 1. The machine and the missing implication

Keep the existing machine `M_t = (F_t, O_t, Pi_t, C)`: a persistent epistemic
field, an operator inventory, an executive policy, and an externally governed
Check/Authority/Meter/Commit constitution. A proposal is not an authorized
transition. Its acceptance must remain outside the mechanism proposing it.
A physical view of F is a representation, not an additional authority.

For a registered environment, construct a state space S that includes everything
needed to predict the declared future observations. This includes relevant
support state, scope, operator versions, and restart-visible state. Omitting an
influential dependency makes the model inadequate even if its tables are internally
consistent. A finite checker cannot establish that an omitted variable is irrelevant.

The invalid shortcut is:

    same current answer -> same decision -> same future behavior -> safe compression

Each arrow needs its own assumptions. The construction below establishes a
sufficient condition for the final implication inside an explicit finite model.
It does not infer the finite model from the production runtime.

## 2. Declared finite contract

Fix a finite nonempty S. For every s, supply a finite ordered list A(s) of distinct
action IDs. STOP is separate and always available; it ends this modeled episode.
Every action has a deterministic protected observation K(s,a), a nonnegative
rational additive-cost vector r(s,a), and an exact rational probability kernel
P(s,a,s'). STOP has K_stop(s) and r_stop(s). The kernel is total over S and sums
exactly to one. Invalid or missing entries, including zero-mass foreign successors,
are rejected rather than interpreted as unsupported negative evidence.

The observation schema explicitly contains answer, status, warrant, scope,
authority, polarity, support, dependencies, historical receipt, and failure.
These are exact JSON observations, not measured semantic truth. The caller must
choose and justify their projection. A list ordering or a receipt difference is
observable unless a separately justified normalization removes it. JSON `true`
and `1` are distinct; arbitrary Python equality is not used for observations.

Registered events such as evidence withdrawal, restoration, operator installation,
and restart must appear as modeled transitions to be covered. A field named
`restart` is not a real process restart experiment. Nondeterministic emitted
observations/costs require a richer joint-outcome kernel or an augmented state;
this implementation covers deterministic observations/costs conditional on (s,a).
Concurrency, crashes, external tools, or unbounded histories are not silently added.

The model identity binds the complete normalized table, resource axes, source
commit, and constitution/operator/projection/ecology identities. These IDs are
supplied provenance labels. Hashing them authenticates neither their source nor
their authority. The receipt also binds the actual checker bytes and partition.
Revalidation recomputes the result, not just the hash. An external adopter still
needs independent evidence that the model corresponds to the runtime.

## 3. Propositions and proofs

### P1. Nonempty decision sufficiency is conditional on realizability

Let G(s) be the acceptable actions in hypothesis s and V be a nonempty subset of S.
Define Gamma(V) as the intersection of G(s) over V. If the actual state s* lies
in V, every a in Gamma(V) is acceptable at s*.

Proof: membership in the intersection implies membership in every G(s), including
G(s*). No unique hypothesis is required. This is the ordinary decision-region
principle [R2], not a new OCM mechanism.

Neither nonempty V nor nonempty Gamma(V) proves s* is in V. For G(s)={a},
G(t)={b}, V={s}, actual state t, the singleton prescription a is wrong. An empty
V is a model/data inconsistency or uncovered case; it must not authorize all
actions by vacuous containment. The pinned helper's `contained_decision_actions`
returns all region labels on empty V while `common_actions` rejects it. The new
`common_actions_checked` closes that operational boundary without rewriting the
historical capsule. It does not solve hypothesis-class adequacy.

### P2. Ordered contract bisimulation preserves modeled finite traces

For a partition q:S->B, require for any s,t with q(s)=q(t):

1. K_stop and r_stop agree.
2. A(s) and A(t) agree as ordered lists.
3. For each corresponding action, K and r agree.
4. For every block b, sum_{q(u)=b} P(s,a,u) = sum_{q(u)=b} P(t,a,u).

Then the quotient is well-defined. For any common policy that depends only on
abstract observation/action/block history (and uses the same randomization law),
states in a block induce the same distribution of finite protected traces and
accumulated additive costs, including terminal STOP observations.

Proof by induction on remaining actions: at zero only STOP occurs, and condition
1 gives equality. For a longer trace the policy chooses the same action law from
the same abstract history. Conditions 2 and 3 preserve its availability, immediate
observation and cost. Condition 4 gives equal next-block probabilities; apply the
induction hypothesis conditionally in each block and sum. This is a specialization
of ordinary labeled stochastic bisimulation/model reduction [R1]. It is not
claimed for policies that inspect hidden concrete-state identity.

### P3. Finite metareasoning preserves selected actions, not just values

For any fixed nonnegative rational price vector w and finite integer h>=0, let

    V_0(s) = w . r_stop(s)
    V_h(s) = min(w . r_stop(s),
                 min_a [w . r(s,a) + sum_u P(s,a,u) V_(h-1)(u)])

Break equal minima by STOP first, then the supplied action order. Under P2's
conditions, both V_h and the chosen action ID are block-constant for every h.

Proof: the zero case follows from STOP equality. If V_(h-1) is block-constant,
each continuation sum can be grouped by blocks. Conditions 3 and 4 make each
corresponding candidate value identical. Condition 1 preserves the STOP candidate,
and condition 2 preserves the same tie ordering, so both the minimum and selected
ID agree. Induction completes the proof. The implementation translates inputs to
the existing `finite_meta_dp`, rather than constructing a second solver.

Counterexample to omitting STOP: two states with no actions and STOP costs 0 and
1 satisfy an action-only bisimulation vacuously, but V_0 differs. Counterexample
to omitting order: at s and t, STOP costs 2; actions a,b both cost 0 and lead to a
zero-cost terminal. Orders [a,b] and [b,a] give equal value 0 but select different
IDs. Both boundaries are reproduced against the exact pinned parent. Its action-only
helper explicitly excludes STOP and ignores action order; the latter behavior is
not a bug in its narrower equivalence definition. It is insufficient for the
stronger integrated selection contract. Bounded metareasoning is a conventional
parent [R3], not grounds to unlock learned routing.

### P4. Refinement terminates at the coarsest declared-contract partition

Start with the universal partition. Replace each block equivalence by equality
of signatures containing STOP, ordered immediate contracts, and next-block masses.
The sequence refines monotonically: equality of masses to finer blocks implies
equality to their unions. A strict refinement increases the number of blocks, so
there are at most |S|-1 strict refinements. At the fixed point all P2 conditions
hold. Any P2-stable partition refines the initial partition and, inductively, every
subsequent one; therefore it refines the fixed point. That point is the coarsest
partition satisfying the declared relation.

This is not a smallest sufficient cognitive machine, a minimum value-equivalent
model, or a proof of production speedup. Whole-table refinement and rational
arithmetic have costs. Integer bit lengths and observation sizes matter. No
constant-time arithmetic, locality guarantee, or asymptotic resource win is inferred.

### P5. Self-extension invalidates an old equivalence without a new proof

P2 quantifies over the current action inventory and projection. Add a new action
whose observation distinguishes previously merged s,t. The old relation no longer
satisfies condition 3. Altering STOP, scope, constitution, kernel, cost, or projection
can similarly break it. Therefore old validation cannot be inherited solely because
the old actions still agree. Exact extension checks or a separately established
contextual preservation theorem are required. The checker recomputes after every
model change and rejects stale receipts; manifest changes invalidate identity even
when a table happens to be unchanged. This is an invalidation rule, not proof that
a learned operator was successfully installed in OCM.

### P6. Support semantics requires more than current liveness

For a finite acyclic support circuit over evidence liveness variables, use AND
for conjunctive premises and OR for alternative derivations. For any valuation,
circuit evaluation gives the declared support status by structural induction on
the circuit. With all reverse incidences present, updating affected gates in
topological order after a leaf change produces the same result as full reevaluation:
unaffected gates retain unchanged inputs, and affected gates are recomputed from
already correct predecessors. This is conventional provenance/TMS territory [R6].

The result does not cover omitted incidences, cycles without a chosen fixed-point
semantics, missing upper-bound supports, or authority/scope changes not represented
as inputs. It preserves alternative support only when the original circuit does.
Formal proof acceptance, empirical warrant, source testimony and active authorization
must not be collapsed into a single number. No probability or universal confidence
calibration is implied by Boolean liveness. The finite table checker treats all
these declared observables distinctly but does not implement the production circuit.

### P7. Conservative learned macros need not increase expressivity or utility

Suppose every learned operator m has an exact expansion into existing operators,
with the same declared preconditions, effects and observations. Replacing each m
call by its expansion proves equality of the resulting denotation by induction on
program syntax. Thus adding m can be a conservative extension of unbounded
expressivity while changing bounded reachability and search cost.

A shorter representation can increase branching, matching, verification, indexing
or maintenance cost. It therefore does not prove lower total cost on fresh tasks.
The mechanism must be compared with the ordinary parent using the same learned
object. Library induction and its compression objectives are established parents
[R4,R5]; correctness, compressivity, consumer use and causal usefulness are distinct.
Inlining that changes authoritative trace IDs is not an exact protected-contract
preservation unless that difference is explicitly allowed. This paragraph supplies
no positive G2 result. It does not retune #189/#191. The separately merged #192
reports bounded causal macro reuse with ordinary-parent parity and no full-cost
payback at its horizon; that scoped result does not establish an OCM-only residual.

### P8. Lifetime crossover is conditional, coordinate-specific, and paid

For a matched-capability parent with recurring scalar cost p and a learned system
with fully charged extra setup C>=0 and recurring cost m, the learned system wins
strictly after n uses exactly when n(p-m)>C. If p>m, the first positive integer
horizon is floor(C/(p-m))+1. If p<=m there is no strict positive-horizon win under
these assumptions. This follows by subtracting C+nm from np. Setup is the net
extra setup relative to the parent; common costs may be canceled only symmetrically.

Charge unsuccessful acquisition candidates, validation tournaments, checks,
materialization, persistence, retrieval, revision, deletion, metareasoning and
migration where they occur. Nonstationary costs require actual cumulative sums,
not the stationary formula. Resource vectors a,b satisfy w.a<=w.b for every
nonnegative w iff a<=b coordinatewise: one direction follows from nonnegative
sums; the other uses each coordinate's unit vector. Crossing coordinates therefore
have no price-independent ordering. Peak memory is a maximum, not a sum; either
augment the state with the peak and model its terminal charge or report it
separately. No wall-time or peak-memory advantage follows from search-slot savings.

### P9. Bounded search failure is not task impossibility

A search that exhausts its registered finite universe U establishes absence only
inside U, assuming complete enumeration and a correct decision procedure. A
budget-stopped search that has inspected U' subset U establishes even less. Extend
the universe with a valid witness not inspected by the search: every observed
failure is unchanged but the global impossibility claim is false. Thus outcomes
must retain method, environment, scope and budget. `UNKNOWN`, `CANNOT_CHECK` and
verified negation must remain separate. Exact finite table rejection is a witness
against that proposed partition, not a theorem that compression or OCM is impossible.

### P10. External admission preserves only invariants actually checked

If the initial state satisfies invariant I, every accepted transition preserves I,
and only externally admitted transitions can commit, then every committed state
satisfies I by induction on commits. A self-proposal cannot alter C under these
assumptions. The proof says nothing about completeness or correctness of the actual
checker, atomicity, bypass paths, or crash recovery; these are implementation proof
obligations. Writing the invariant in a manifest does not satisfy them. A source-
bound finite receipt here must never become the authority that admits itself.

## 4. Proof-to-programme boundary

P1-P5 have executable exposed controls here; P6-P10 are scoped derivations and
integration obligations, not new runtime implementations or kernel-checked proofs.
The census covers all 1,728 deterministic three-state, one-action models specified
in the test generator, all five partitions per model, and horizons 0..4. A separate
bounded trace oracle checks the coarsest relation; a direct all-pairs oracle checks
partition acceptance. These differently structured authored algorithms do not
supply independent authorship. Rational stochastic examples and hostile schema,
mutation, STOP, ordering and stale-receipt cases are additional controls, not an
exhaustive census of all stochastic models.

The next implementation obligation is a source-bound extractor from the actual
OCM transition/lifecycle surface, followed by differential original-versus-view
traces across real process restarts and evidence withdrawal/restoration. It must
bind full observation and operator inventories, authority, dependency changes,
resource meters, crash behavior and source revisions. Unsupported extraction must
return a reasoned CANNOT_CHECK, not a smaller silent table. No such extractor is
implemented in this capsule. #71 and #46 remain gated; M11/M12 claims are not renewed.

The remaining programme gates are recorded in GAP_MAP.json. Positive theory results
cannot substitute for actual fresh method consumption, independent capability
measurements, full lifetime economics, persistent cross-domain development,
strongest-parent comparisons, or protected replication.

## 5. Review perspectives used in this contribution

These are four review roles applied by one author, not four external experts.
The formal-methods perspective checked quantifiers, empty sets, fixed points and
finite-horizon induction. The runtime perspective checked STOP, ties, identity,
mutable observations and version invalidation. The learning perspective separated
conservative compression from fresh utility and accounted for strong library
parents. The skeptical experimental-design perspective kept the finite census
separate from independent review, real restart evidence and protected outcomes.
The cross-check changed the implementation to preserve ordered actions and exact
JSON types and the economics statement to exclude additive treatment of peak memory.

## References and exact reuse boundary

R1. Givan, Dean, Greig. *Equivalence notions and model minimization in Markov
    decision processes*. Artificial Intelligence 147, 2003.
    https://engineering.purdue.edu/~givan/papers/mm.pdf
    Adopt: stochastic bisimulation and partition refinement. No novelty claimed.
R2. Javdani et al. *Near Optimal Bayesian Active Learning for Decision Making*.
    AISTATS/PMLR 33, 2014. https://proceedings.mlr.press/v33/javdani14.html
    Adapt: common decision regions. No HEC competitive guarantee is imported.
R3. Hay, Russell, Tolpin, Shimony. *Selecting Computations: Theory and Applications*.
    2012. https://arxiv.org/abs/1207.5879
    Adopt: computation costs and explicit STOP. Only bounded DP is used here.
R4. Ellis et al. *DreamCoder: Growing generalizable, interpretable knowledge with
    wake-sleep Bayesian program learning*. https://arxiv.org/abs/2006.08381
    Comparison: library growth and search guidance; no neural mechanism imported.
R5. Bowers et al. *Top-Down Synthesis for Library Learning*.
    https://arxiv.org/abs/2211.16605
    Comparison: corpus-guided library compression. No compression-to-utility theorem.
R6. Green, Karvounarakis, Tannen. *Provenance Semirings*. PODS 2007.
    https://doi.org/10.1145/1265530.1265535
    Author-uploaded text consulted:
    https://www.researchgate.net/publication/221559651_Provenance_Semirings
    Adopt: distinguish alternative and joint provenance. P6 is restricted to
    finite acyclic Boolean support, not all semiring/Datalog/negation semantics.

Publication metadata and accessible primary text were checked on 2026-09-08.
These references establish intellectual parents, not evidence of an OCM residual.
