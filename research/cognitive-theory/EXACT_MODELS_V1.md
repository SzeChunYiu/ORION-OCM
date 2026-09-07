# Exact foundational calibration models V1

Evidence: E0 formal specifications with E2 exact computational checking. Contribution ceiling: L0 apparatus; no new cognitive mechanism. Primary theorem routes are V1 (elementary arguments); execution supplies supporting V2. These models are authored, not learned, and are not #143 protected families.

## Custody and scope

Base: ORION-OCM `f9d2ff21e066328495638e8d3010107d8b91f018`; separate branch `research/foundational-theory-cell-20260907`. Current #143/#144/#145 bodies and comments were read before research. Their published pilot summaries were therefore exposed. No protected raw outcomes or cross-domain tasks were opened. T5 also executed preliminary checks of Z5/Z6 and support signatures before this specification was committed. This is a reproducibility freeze, **not a pre-outcome E3 registration**. Preserve that exposure even where T1/T4 independently derived counts analytically.

The latest user instruction and #145 place this bridge packet here. ORION-V2 #304/#358 remain the canonical science donors; this packet does not transfer ownership or change a machine adoption gate. No `src/ocm`, existing empirical protocols, outcomes or issue bodies are changed.

## Apparatus under (F,T,B,C)

Bind representation schema/encoder/decoder; instantiated global machine state; operator syntax and parameter encoding; composition/interpreter semantics; controller grammar; observations and their authority; admissible recodings; resource accounting; starting-state and environment quantifiers. The tuple `M=(F,O,Pi,C)` is provisional organization, not an identifiable mechanism by itself.

For a contract K, bounded reach means there exists **one admissible policy** p that satisfies K and C on every registered input/environment history with its cost vector within B. A different policy chosen using evaluator-private state for each case is not a witness. Stochastic/adversarial quantifiers must be registered separately. Charge synthesis, compilation and execution independently.

Distinguish target contract family T, candidate operator pool U and generated monoid S. A target subset need not be closed under composition. Minimum cardinality over subsets of U differs from inclusion-minimality and from unrestricted rank. State reach from one start differs from a transformation acting uniformly on all starts.

Endpoint equality is insufficient where intermediate authority/observation events matter. Use C-observable trace/context equivalence. An 'epistemic' obstruction to answer-preserving replacement is ordinary simulation/generation failure under the finer lifecycle semantics; retain it as an assessment axis, not a new absolute mathematical species.

## W1: cyclic transformation laboratory

X=Z6. For a=1,...,5, r_a(x)=(x+a) mod 6. U={r1,r2,r3,r4,r5}; restricted U0={r1,r2,r3}. T contains all six rotations including identity, each required uniformly on all six starts. S is exactly the six rotations, not all 6^6 maps. All intermediate states are admissible; C preserves a fixed external authority context and requires exact outputs. No observation, branching, arguments, program mutation or new state is available. Programs are straight-line words. Applying f then g is g composed with f. Empty word is identity at cost zero.

Primary resource: one unit per **native dispatch**, with all operators explicitly treated as separately admitted native transformations. This is an abstract cost model, not measured CPU time or whole-lifetime optimality. Record catalogue cardinality, minimum dispatch length and compiler effort separately.

Predicted lengths by target exponent 0,...,5:

| Basis | Lengths |
|---|---|
| {r1} | 0,1,2,3,4,5 |
| {r5} | 0,5,4,3,2,1 |
| {r2,r3} | 0,3,1,1,2,2 |
| {r1,r5} | 0,1,2,3,2,1 |
| {r1,r2,r3} | 0,1,1,1,2,2 |

Rank is 1, attained by {r1} and {r5}. Inclusion-minimal full-pool generators are {r1}, {r5}, {r2,r3}, {r3,r4}; restricted-pool generators are {r1} and {r2,r3}. The pair r2,r3 generates r1 as r2;r2;r3. Neither member alone generates all rotations.

| Dispatch budget | Full-pool minimum cardinality | Restricted-pool minimum cardinality |
|---:|---:|---:|
| 0 | infeasible | infeasible |
| 1 | 5 | infeasible |
| 2 | 3 | 3 |
| 3 | 2 | 2 |
| 4 | 2 | 2 |
| 5 | 1 | 1 |

Proof: a generating singleton has order 6 and needs five calls for one target. At budget 2, each candidate pair has reachable exponents contained in {0,a,b,2a,a+b,2b}; none of the ten pairs covers Z6. A triple {1,2,3} covers it. At budget 3 the pair {2,3} covers it. Budget 1 requires every nonidentity target as a native operator. These are parent-owned finite generation/word-cost facts.

Compensation ablation removes an operator and exhaustively recompiles all target maps over the remaining candidate pool. Missing a generator in one implementation is not a necessity certificate. All 32 full-pool and 8 restricted-pool subsets are inspected.

Negative twin: if r2 and r3 are macros expanding to two and three r1 events, charge weights 2 and 3. The weighted lengths over {r1,r2,r3} remain 0,1,2,3,4,5. An API-call-only meter creates a spurious reach advantage. A genuine native speedup is a different treatment.

### W1a: nontransitive fixed-overhead similarity

On Z5, compare A={r1}, B={r2}, D={r4}. Let d(U,V) be the maximum of both directed shortest generator-expansion lengths. The three distances d(A,B),d(B,D),d(A,D) are 3,3,4. Thus d<=3 is not transitive. Use costed directed simulations with composed overhead or a composition-closed overhead class before claiming equivalence classes. Equality of registered reach sets is transitive but is a weaker property.

### W1b: controller and initial-state negative twin

On {0,1}, flip generates only identity and flip. The orbit of 0 is nevertheless both states. A free conditional 'if x=1 then flip else stop' produces constant-zero, outside word closure. This is a specification counterexample; branching belongs in the grammar and cost model.

## W2: alternative-support lifecycle

Fixed accepted rules a=>q and b=>q. X=P({a,b}); all four states are allowed starts. Events ra and rb are externally authorized revocations, deleting their named token. Output is VERIFIED_UNDER_CURRENT_SUPPORT iff the set is nonempty, otherwise UNKNOWN. No support for not-q exists. No history/requery channel, hidden controller memory, mutable specialized code or uncharged side storage exists. The four states describe only this finite future-behavior quotient; append-only provenance/audit histories are outside the contract. CANNOT_CHECK is unreachable in this base world.

| E | ra(E) | rb(E) | output(E) |
|---|---|---|---|
| empty | empty | empty | UNKNOWN |
| a | empty | a | VERIFIED |
| b | b | empty | VERIFIED |
| ab | b | a | VERIFIED |

Current-output partition has 2 classes; all-future-revocation partition has 4. Every pair is distinguished by the current output or one event. Therefore any deterministic exact implementation needs four distinguishable **global** machine states, at least 2 bits across all accessible channels. An answer-only two-state Markov implementation preserving current labels makes at least 2 successor-label errors over the 8 state/event pairs. These eight are an exhaustive finite denominator, not independent statistical units.

Generate the deletion monoid by full map composition: identity, ra, rb, ra;rb, cardinality 4, rank 2 over its nonidentity pool. Removing either named deletion cannot be compensated by the other. This is ordinary algebraic non-generation, not evidence REVISE is a cognitive primitive.

The strongest parent is an ordinary support set / ATMS-style label Lq={{a},{b}}. Validity is existence of a live sufficient support. Revoking a from ab changes available warrants but not q's warranted output. The potentially affected reverse-dependency cone is not the invalidation set. C here permits exact substitution of alternate support; certificate-specific reopening is not scored.

Negative twins: query-only ecology needs only the two current-output classes; blindly invalidate after either dependency withdrawal causes collateral invalidation at ab; never revoke a cached VERIFIED answer causes stale survival after both events. Restoring retained input history would allow replay compensation, but adds an explicitly charged channel and changes the two-state impossibility assumptions.

## W3: observationally indistinguishable diagnosis

Hidden h in {0,1}, equally weighted for the accuracy calculation. h=0 means incorrect candidate with faithful checker; h=1 means correct candidate with defective checker. Initial visible observation is FAIL in both. Hidden state is invariant under every action and is never supplied as controller input. The evaluator's full model is not learner evidence.

Actions: retry costs 1 and returns FAIL in both worlds. Audit costs 2 and returns h through an independently trusted information channel. Stopping with diagnosis 0 or 1 costs 0. Abstention costs 0. Evaluate all deterministic adaptive decision trees at remaining budgets B=0,1,2; randomness cannot beat the best deterministic policy under the declared equal prior. Histories are bounded by these costs/horizons. Policy actions depend only on their visible history and remaining budget.

Prediction: maximum forced-binary exact-diagnosis accuracy is 1/2 at B=0 or 1 and 1 at B=2. Under C requiring zero false cause commitments uniformly over both worlds, maximum committed coverage is 0 below B=2 and 1 at B=2. Abstentions remain in the denominator for unconditional correct-diagnosis rate; selective accuracy is not used.

Negative twin: replace audit by an equally costly uninformative constant observation. Maximum forced accuracy stays 1/2 and zero-error committed coverage stays 0 at all three budgets. No amount of retries separates observationally identical worlds. Audit success is additional information access, not operator invention or a new cognitive theory. UNKNOWN/ABSTAIN is warranted under the stated zero-error C; without a loss/constitution abstention is not universally optimal.

The complete registered system is the hidden two-state world plus the finite belief/remaining-budget transition graph. Enumeration exports all reachable belief states and feasible action/observation transitions. Exact policy search is performed on information sets, never separately optimized with hidden h input.

## Verification obligations and claim ceiling

Two separately authored algorithms: transformation-table BFS/weighted shortest paths and policy enumeration; independent pair-composition/bounded-layer closure, logical support signatures and decision-tree reconstruction. They may share this specification but not implementation code. Cross-check exact tables, counts and witnesses. Shared specification and internal AI authorship remain common-mode risks; this is not E5 external replication.

All contradictions between predictors/checkers must be retained. A computational mismatch reopens the corresponding exact statement or checker. No rank claim applies beyond the candidate pool, declared grammar and registered states. These worlds do not establish learning, OCM performance, field scaling, novel primitives, cross-domain transfer or publication readiness.
