# Architecture-level net benefit: proof obligations and executable admission gate

Status: research-only. This tranche establishes conditional mathematical results
and tests their finite helpers. It does **not** establish general OCM net benefit.
No percentage-complete estimate is meaningful here. A green test suite is not
scientific admission. Connects issue #152 to the reopened M12 obligation (#14).

Source boundary: `main@138e90b71e80a0310f65fb2c827c2782e92caa8a` and read-only
PR154 snapshot `94f9f3361cec49c8232049e70fbba8662635902f`. No PR154 files,
protected evaluation corpus, historical receipts, or production sources are changed.

## 1. What is being proved?

Fix a workload family E, an initial-information contract C, a set of actual
persistent conventional parents P, a finite lifetime protocol, and a prospective
resource-price region W. Let X denote an exogenous workload/randomness tape.
Each policy A runs on its **own** state trajectory s_t^A. Its complete cost is

    C_w(A,X) = w . [setup_A + sum_t r_A(s_t^A, event_t) + close_A(s_T^A)].

Every computation, failed candidate, exact verification, discovery/validation,
selector lookup, storage maintenance, revocation, checkpoint, replay and required
shutdown belongs in the cost. Peak memory is not additive: use a separately
reported maximum, or augment the state/cost semantics to measure its increments.
CPU time, wall time and resource counts remain separate coordinates.

The empirical target is a **qualified comparative claim**, e.g.

    for every P in the registered comparator set and every w in W,
    E[C_w(OCM,X)] <= (1-eta) E[C_w(P,X)],

with eta fixed before protected evaluation and with independently justified
protected correctness/lifecycle semantics. An initial proposed practical margin
is eta=0.05; that is a protocol choice, not a derived law or current result.

Three different claims must not be conflated:

* mechanism: a particular learned/reused representation saves work;
* implemented system: this OCM implementation beats registered qualified parents;
* necessity: no conventional implementation could achieve the same effect.

The first does not imply the second. We do not need the third to establish a
useful architecture: an integration of conventional techniques can be valuable.
Nor can experiments against a finite parent set establish that third claim.

## 2. Parent map and review tracks

Four review tracks are assigned in this session: formal methods (cost refinement,
STOP and lifecycle observables); online algorithms (own-state comparators and
amortization); systems (complete disjoint cost measurement); sequential statistics
(lifetime-level units, fresh data, optional stopping). These are analytical roles
within one assistant session, **not independently executed agents or peer review**.
Independent review remains an external gate.

The reading map in `LITERATURE.md` records primary sources, relevant sections,
what is reused, and what each source does NOT prove for OCM. In particular:
metareasoning is inherited from Russell/Wefald; cost-refinement is an application
of amortized analysis; efficient reusable libraries have DreamCoder/Stitch parents;
dependency tracking has self-adjusting computation/build-system parents; stateful
comparison needs policy-counterfactual discipline; sequential admission uses
nonnegative test martingales. We are not claiming these ideas as OCM inventions.

## 3. Theorem A: complete relational amortization

Let A and P be deterministic finite input/output cost machines with the same
finite input alphabet. Assume their transitions are total on the declared state
sets, costs are finite nonnegative vectors, and every legal successor is included.
Let Z be the reachable synchronous product of their **own** states. For z=(a,p),
input e, successor z', fixed w>=0 and rho>=0, suppose:

    output_A(a,e) = output_P(p,e)
    w.r_A(a,e) - rho*w.r_P(p,e) + Phi(z') - Phi(z) <= 0.       (A1)

Require equal protected close observations at every reachable pair. Phi is any
finite real-valued function, and is allowed to be negative. Define

    B = w.setup_A - rho*w.setup_P +
        max_{z in Z} [Phi(z0)-Phi(z) + w.close_A(z_A)-rho*w.close_P(z_P)]. (A2)

Then for every finite input word X, including the empty word,

    C_w(A,X) <= rho*C_w(P,X) + B,                              (A3)

and the machines have the same projected protected observation trace.

Proof. Induction on the input word shows the actual pair always belongs to Z;
(A1) supplies equal output at each step. Sum (A1). Consecutive potential terms
cancel, giving running-cost difference at most Phi(z0)-Phi(z_T). Add both setup
and close costs, then apply the maximum in (A2). The close-observation condition
completes trace equality. The empty word uses just setup and close and is also
covered by (A2). QED.

**Net-benefit corollary.** If rho<1, any word satisfying

    (1-rho)*C_w(P,X) > B

has strict net benefit. If B>0 this deliberately does not promise a cold win.
For multiple prices, verify independently at the vertices of a frozen convex
polytope. Use the corresponding weighted combination of bounds for interior
prices; do not take a maximum over resource coordinates and call it a scalar win.

**Scope.** `refinement_certificate` checks (A1)-(A2) exactly for supplied rational
finite machines, including setup and STOP/close. It does not establish that a
finite machine is a sound abstraction of production code. That source-refinement
obligation must bind real state, observations, costs and all lifecycle events.
Finite-word safety also does not prove termination of unbounded computation.

**Useful falsifier.** In the executable control, the parent costs 10 per query
and 1 on close. The investing candidate costs 26 on its first query, 2 thereafter,
and 3 on close. For H>=1 the net saving is 8H-26, hence positive at H>=4, negative
cold. A valid certificate has rho=1/5, Phi(cold)=0, Phi(warm)=-24, B=134/5.
Adding reset invalidates this stable-epoch certificate. A separate rho=3
certificate covers arbitrary reset words. These are authored arithmetic controls,
not OCM measurements or a new competitive-ratio result for the real engine.

### Constructive completion: when does a potential exist?

For a fixed ratio rho, put edge weight
`d(z,e)=w.r_A(z_A,e)-rho*w.r_P(z_P,e)` on the reachable product graph.
There exists a finite potential satisfying (A1)'s cost inequality if and only if
this graph has no positive-total-weight directed cycle.

Proof. Summing (A1) around any cycle cancels the potential, so a positive cycle
is impossible. Conversely, add a zero-weight super-source to every reachable
vertex. Without positive cycles, deleting cycles never decreases path weight;
therefore the maximum path weight to each vertex equals that of some simple path
and is finite. Write it D(z). For each edge, D(z')>=D(z)+d(z,e), so setting
Phi(z)=-D(z) gives (A1). A positive reachable cycle can be repeated arbitrarily,
so finite setup/close charges cannot rescue any fixed additive bound. QED.

`synthesize_refinement` constructs these distances with exact rational graph
relaxation and returns either a checked potential or a positive-cycle rejection.
This is standard difference-constraint/amortized analysis, not new graph theory.
It converts the mathematical gate from "supply a proof-shaped potential" into an
executable proof search for any supplied finite abstraction. Source refinement,
observation matching and adequate event coverage remain separate obligations.

## 4. Theorem B: the whole-lifetime stateful-comparator correction

Replacing C(P,X) by sum_t c_P(s_t^A,e_t) is in general invalid, even if all costs
are measured exactly. The latter charges P from A's history, not P's history.

Proof by counterexample. A costs 26 initially and 2 on subsequent queries. P
builds its own reusable state for 20 and subsequently costs 1. Over ten queries,
ignoring common closing cost, A costs 44 and P costs 29. Resetting P artificially
each query reports cost 200 and reverses the comparison. Every number is exact;
the wrong counterfactual creates the false conclusion. QED.

The dual error is giving a candidate a free shadow parent/semantic index advanced
on queries where that candidate did not run it. Research may run separate full
rollouts to identify counterfactuals, but their states cannot be given to the
candidate policy. Evaluation apparatus cost and deployed per-arm cost are distinct
budgets: charge research calibration separately, and count any calibration used
by the deployed policy as acquisition cost in the declared deployment lifetime.

## 5. Theorem C: valid reuse, not nominal lifetime, repays investment

Consider one fixed initial build/discovery investment costing D, counted once. Let L_t indicate its retained structure
is still valid at t; U_t indicate it is useful on the current request; and d_t be
its gross incremental saving relative to a qualified parent's own trajectory.
Let O be all remaining candidate-only lookup, unsuccessful use, maintenance,
invalidation, checkpoint and close costs, excluding both D and charges already
netted in d_t. Assume every baseline-only saving is assigned to exactly one
validated use; otherwise it needs its own additional benefit term. Provided savings
refer to disjoint baseline work (no overlapping macro credit),

    E[net gain] = sum_t E[L_t U_t d_t] - D - E[O].              (C1)

Proof. For each tape partition complete work into matched work, work uniquely
avoided by the candidate, and candidate-only work. Match each avoided operation
at most once. Subtract costs and take expectations; linearity gives (C1). QED.

For constant saving d and externally established joint probabilities
p_t=Pr(L_t=1,U_t=1), this becomes d*sum_t p_t-D-E[O]. No independence is needed.
Factoring p_t into marginal survival and reuse probabilities requires additional
justification. Under independent constant survival s and demand probability u,
starting from a live investment at opportunity 1, sum_{t=1}^H p_t is
u*(1-s^H)/(1-s), or uH when s=1. Correlated revocation and demand can destroy
that simplification.

This identity is a diagnostic decomposition, not by itself a discovery theorem.
A constructive OCM proof still needs source-derived bounds on D,O,d and evidence
that the relevant demand/validity conditions arise without target leakage.

## 6. Theorem D: transferring components bounds attribution

Suppose a conventional implementation uses the same deterministic miner, legal
training information, fragment order, solver, checker and event-dependent active
library as OCM. By induction on requests, both produce the same search sequence,
search-slot counts and mathematical solutions. Differences then lie in the
surrounding coordination/lifecycle implementation, not in learned search itself.

Proof. Equal active libraries and task inputs produce identical deterministic
solver executions. Equal training traces produce equal miner outputs. Equal
activation/invalidation rules preserve this equality at each lifecycle step. QED.

A component-transplant control does not have to defeat OCM to be useful. It tells
us which part of any advantage remains to explain. If its full protected
lifecycle contract is weaker, it is not yet an admissible full-system baseline.

The native pilot tests this boundary using existing exposed polynomial learning
examples, plus 24 distinct future tasks chosen without using cost outcomes.
It compares primitive search, an ordinary persisted fragment learner, and the
native OCM method/KSO path. It retains training, validation, process startup,
query execution, persistence, restart and support withdrawal costs. Every arm
runs separately; all cells are retained. It does not run the protected corpus.
The ordinary parent's current qualification is single-writer method-lane scope,
NOT full OCM provenance, authority, crash or concurrency semantics.

## 7. Theorem E: anytime evidence for complete-lifetime benefit

Fix J parents and K nonnegative price vectors before evaluation. Fix eta in [0,1),
alpha in (0,1), and positive finite resource caps b, such that every complete arm
cost vector lies coordinatewise in [0,b]. Each trial is an independent draw of a
COMPLETE lifetime, initialized from the same frozen development state. Adaptive
learning within that lifetime is allowed; cross-trial tuning on outcomes is not.
For parent j, price k, define

    X_i,j,k = ((1-eta)*w_k.C_i(P_j) - w_k.C_i(A))/(w_k.b).

Then -1<=X<=1. Under the null that E[X_i,j,k] <= 0, for fixed lambda in [0,1],

    M_n(lambda) = product_{i=1}^n (1+lambda*X_i,j,k)

is a nonnegative supermartingale with initial value 1. Any fixed convex mixture
of such processes is likewise a nonnegative supermartingale.

Proof. The factor is nonnegative. By IID trials and the null,
E[1+lambda X_i | past] <=1. Multiply by past-measurable M_(i-1), take conditional
expectation and induct. A fixed convex mixture preserves this property. QED.

Ville's inequality bounds Pr(sup_n M_n >= JK/alpha) by alpha/(JK). Union bound
over J*K pairs gives simultaneous type-I control <=alpha. Invalid, partial, duplicate or out-of-cap records permanently block a positive
claim from that evidence object; they cannot be discarded after outcome access.
The implementation
uses the equally weighted mixture lambda in {1/8,1/4,1/2}, exact rational arithmetic,
and requires every parent/price pair to cross before reporting conditional
net-benefit evidence. This union-bound gate is conservative, not optimal power.
It is an application of established test-martingale methodology [L8], not a new
statistical theorem. Formalization of the finite helper is not proof of correct
sampling, cost caps or observations in an external experiment.

For prices in the convex hull of the tested vertices, strict positive expected
margin at every vertex implies strict positive margin throughout the hull by
linearity. This is a ratio-of-expectations claim, not the expectation of per-trial
speedup ratios. Zero-cost denominators in individual runs are not divided by.

**Not granted:** population safety from zero observed errors; future benefit under
arbitrary drift; protected-evaluation independence; arbitrary unmeasured resource
benefit; full architecture advantage when a registered parent's contract is weaker.
A contract mismatch is retained permanently. Missing phases, missing parents,
duplicate trial IDs, float costs and cap violations are rejected rather than
silently omitted or clipped. Distinct IDs alone cannot prove independence.

## 8. Achievable architecture target and decisive experiment

The target is not dominance of every conventional algorithm on every workload.
A parent can literally implement the same algorithm, and paying positive
acquisition cost on a lifetime with no reuse can lose. These are explicit
quantifier limits, not grounds to abandon the research.

Use one frozen executive across at least three independently constructed adapters
as a proposed replication target: native proof methods, exact program synthesis,
and dependency-sensitive knowledge revision. This number is a research design
choice, not a venue rule. Renaming a shared synthetic generator three times is
not cross-domain replication.

Register before evaluation: information available at each decision, initial
libraries, primitive grammar, endogenous discovery policy, exact verifier and
refusal semantics, drift/reset events, task-order generator, resource coordinates,
price vertices, caps, margin, comparator implementations and all outcome filters.
Freeze complete lifetimes as units; task families and supporting structures must
be separated between development and fresh evaluation. A checker's source/hash is
not by itself a certificate of its semantic adequacy.

The parent set must include the best relevant domain solver, persistent exact
memoization, an incremental dependency/change-propagation parent, a conventional
library learner (Stitch-style where appropriate), exact regime/investment control,
and a component-transplant control. All receive equally legitimate training data,
persistence, verification and compute opportunities. They need not use the same
representation. Exclude a parent only for a recorded contract mismatch, not for
being too strong. Do not demand proof that every imaginable simpler policy fails.

Required ablations: remove discovery; remove reuse without resetting other useful
state; replace common-action stopping with its exact parent; remove incremental
invalidation; transplant the discovery/reuse component into conventional storage.
Ablation effects can interact and must not be summed as independent savings.

The success claim requires a full evidence chain:

    source-bound protected semantics
    -> endogenous acquisition from legal experience
    -> later non-duplicate useful reuse
    -> complete own-state lifetime comparison
    -> measured margin against qualified strong parents
    -> replication on fresh independently constructed families.

The next implementation work is native adapter qualification and full parent
contract matching, NOT another router or another collection of toy witnesses.
Stitch's corpus compression objective is a useful donor but does not itself
optimize whole-lifecycle OCM cost. Reuse its search machinery only with an explicit
cost/value model and independently checked rewrite/lifecycle contract.

## 9. What this tranche does and does not finish

Finished: conditional pathwise theorem including setup/close; exact rational
finite checker; own-state comparator counterexample; joint-live-use accounting;
component attribution theorem; anytime practical-margin gate; adversarial unit
controls; source-pinned native attribution pilot code and CI.

Open: source-to-abstraction proof for the actual OCM executive; complete native
parent qualification; authentic fresh independently sampled task families; full
machine accounting at scale; positive held-out architecture margin; independent
replication/review. None is promoted by the unit controls or exposed pilot.

Also preserve two earlier corrections: PR154's two-arm oracle cannot bound an
expanded action set (ORACLE_SCOPE_CORRECTION_V1.md); its exact helper repair on
main is isolated and not yet integrated into PR154 (CURRENT.md). The earlier
"<0.08% feature regret" is a restricted cold-entry information-partition result,
not a universal cap on the value of different deployable architecture policies.
