# Epistemic Structure Discovery — central hypothesis, not established necessity

Programme: #149, empirical #143, theory #145, constitution #144. Related
implementation parent: #115 factorized KnowledgeSpace / epistemic compiler.

**Hypothesis:** learning a useful, validated decomposition of cognition can
reduce the cost of later diagnosis, repair and preservation enough to improve
the lifetime quality/resource frontier. Sparse stable causal structure is one
candidate mechanism. Shared computation, low-rank/global algorithms and other
compressible structure can also help. No necessary-and-sufficient theorem for
all cognitive advantage has been established.

The distinction is material to the completed pilot: it supplied two dispatch
coordinates and a candidate library. OCM selected two existing repairs but did
not discover that decomposition or learn its proposal policy. The E2 counted
work benefit and missing wall-time benefit remain exactly as reported; they
are not retrospective evidence for learned causal factorization.

## External simulation evidence

The user's sparse/dense/drift, periodic-relearning, triggered-reorganization and
cubic-surrogate figures are retained separately in
`EXTERNALLY_REPORTED_FACTORIZATION_V1.json`. Their code, seeds, complete
trajectories, uncertainty and cost definitions were not supplied or found in
the searched repository sources. Status: **UNVERIFIED_USER_REPORTED**, not a
reproduction or an OCM result. The repeated pasted message is one report.

Those observations motivate a phase-diagram hypothesis. They do not establish
that sparsity is necessary, that a quality threshold is an obstruction
certificate, that a surrogate has received its strongest budget/representation,
or that an evaluation count captures optimization compute.

## Formal object and coupling

Fix representation F, externally declared task/epistemic obligations Q, positive
weights w, constitution C, intervention ecology mu, and lifecycle horizon h.
For state s and admitted intervention e define:

\[
A_C(s,e;h)=\{q\in Q: \operatorname{Obs}^h_C(q,s,e)
\ne\operatorname{Obs}^h_C(q,s,\mathrm{id})\}.
\]

Observations include behavior, warrant scope, provenance/dependency, authority,
uncertainty, revocation and reopening. Compare the same environment and external
interventions in both counterfactuals. In stochastic settings declare whether
equality concerns distributions or paired randomness; samples alone do not
certify equality.

\[
\kappa^{\mathrm{aff}}_{F,Q,C,\mu,h}
=\mathbb E_{(s,e)\sim\mu}
\left[\frac{\sum_{q\in A_C(s,e;h)}w_q}{\sum_{q\in Q}w_q}\right].
\]

Also report worst-case coupling and change-size strata. Fixed external Q/w
prevent reducing the score by adding inert atoms, renaming modules or merging
the whole machine into one nominal component. If affected sets are not
identifiable, provide certified bounds or CANNOT_CHECK.

Keep three quantities separate:

1. **Affected obligations:** what actually changes under the registered
   intervention/lifecycle contract.
2. **Possible affected obligations:** the union over currently admissible
   state/structure models; uncertainty may make this much larger.
3. **Actual repair footprint:** the multiset of obligations touched/rechecked by
   the policy, plus routing, discovery, boundary inspection and maintenance.

Repeated checks mean actual normalized work can exceed one. Low affected-set
coupling does not imply the machine can discover that set cheaply. Graph edge
density, cross-module coupling, transitive closure, physical bytes and recheck
work are different observables. Minimize measured future repair cost subject to
quality and C, rather than optimizing an unqualified kappa(M).

The proposed expression M=M1+...+Mk+I is a modeling hypothesis until the state,
interfaces, allowed compositions and interaction remainder are defined. Do not
interpret a diagram of fibres as an already identified causal decomposition.

## Amortization with verification and drift

For a single registered cost coordinate (or explicitly justified objective),
write the incremental lifetime cost of the structured policy as:

\[
C_S(H)=D+I+V_0+\sum_{t=1}^H(R_t+L_t+G_t+M_t+U_t),
\]

where D is structure discovery, I indexing, V0 initial validation, R routing,
L local repair, G preservation/boundary checks, M maintenance and U rediscovery,
false alarms, failed proposals and recovery. Charge the matched parent's setup,
learning/model fitting and adaptation costs as well.

Under explicit stationary assumptions, let P be mean parent cost per episode,
delta drift frequency and U mean rediscovery cost:

\[
b=P-(R+L+G+M+\delta U),\qquad
H>\frac{D+I+V_0-C_{P,0}}{b}.
\]

This usual break-even form assumes **b>0**. With a positive extra setup cost
and b<=0, repetition does not repay the investment in that model. If setup
differences have another sign or the regime drifts, evaluate the original
inequality directly. Forecast payback only while the structure remains valid;
report realized horizon, errors and intervals. Apply cost comparisons per
coordinate or under frozen budgets. Preservation violations cannot be traded
for speed in a weighted score.

## Three exact counterexamples constrain the hypothesis

1. **Anchored pairwise probing can miss interaction.** On three Boolean inputs,
   f=xyz and f0=0 agree at 000 and every change of at most two coordinates.
   They disagree at 111. Pairwise probes over all backgrounds would detect xy
   when z=1, so the counterexample is specifically against the incomplete
   anchored procedure. Observational pairwise independence is weaker still.

2. **Sparse stable graphs can have global repair.** A path x1=u, xi=x(i-1)
   has bounded degree and n-1 edges, yet changing u changes all n obligations.
   With a constitution requiring eagerly materialized current values, repair
   requires n writes. A sparse authority star can invalidate every warrant
   without changing any task answer. Low edge count alone licenses no locality
   claim; lazy representations move costs and must be charged over the lifetime.

3. **Low affected-set coupling is not necessary for compute savings.** For
   n>=4 Boolean inputs, let yi be the parity of all inputs except xi. One
   input change affects n-1 outputs, so coupling tends to one. Separate
   evaluation uses n(n-2) XORs; shared parity followed by yi=P XOR xi uses
   2n-1. Shared computation therefore improves work despite dense influence.

`verify_structure_counterexamples.py` exhaustively checks the finite instances.
These are elementary parent-owned reductions, not new self-evolution fixtures,
scientific novelty or OCM adaptation successes.

## Operational trigger: alarm is not obstruction

A quality drop, failed prediction or drift signal may trigger paid diagnosis.
It is not a proof that local repair or the current factor language is
insufficient. A bounded obstruction receipt must specify the admissible local
change set, complete checked alternatives/closure, resources, exact failed
obligation, live support and an independently checked witness. Unchecked or
unbounded alternatives remain UNKNOWN. Exploratory broader proposals in
development must retain that uncertainty; they cannot acquire adoption
authority by calling a threshold an obstruction.

## Next decisive experiment

Begin with actual #143 failure traces and M11 measured interventions. Keep true
responsibility labels, module grouping and dependency graph out of proposer
inputs; declare any intervention handles and observability already supplied.
Learn an effect/interaction model with alternative structures and uncertainty,
including higher-order and epistemic lifecycle effects. It must predict which
new contracts are affected before new interventions are observed.

Compare on the same candidate/configuration/task space:

| Arm | Structure information |
|---|---|
| Unstructured adaptive parent | Same observations/probes; free to learn structure |
| Supplied true decomposition | Gifted information ceiling only |
| Learned factorization | Pays discovery, validation and maintenance |
| Wrong/shuffled factorization | Negative twin with information budget matched |
| Frozen learned factorization | Removes drift handling |
| Periodically refreshed factorization | Pays every rebuild |
| Alarm-triggered factorization | Threshold policy, not called proof |
| Witness-triggered factorization | Additional exact bounded certificate costs |

Include the strongest feasible structured/surrogate optimizer, not just random
or evolutionary search. Charge feature construction, polynomial-basis search,
linear algebra/model fitting, acquisition optimization, exact probes, memory,
checking and state migration. Match quality floors and full budget curves;
two points with different cost and quality do not establish dominance.

Cross interaction strength/order, propagation depth, drift rate/type, reusable
exposure count and validation coupling. Distinguish missing data, absent
operator, wrong representation, inaccurate factor model, uncertain authority
and mere insufficient search. Use independent full trajectories as statistical
units and freeze architecture/history/comparators/budgets before protected
evaluation. No protected output trains the structure learner.

Primary residual sought: **lower total acquisition and future repair cost from
learned, preserved structure at matched task quality and information, beyond
equally adaptive parents**. If the parent learns the same useful structure at
equal or lower cost, retain PARENT_SUFFICIENT. If only supplied structure wins,
retain STRUCTURE_GIFT_REQUIRED. If lifecycle checks erase locality, retain
EPISTEMIC_COUPLING_DOMINATES.

## Prior-art reduction

Modularly varying goals promoted modular networks and rapid adaptation in
Kashtan and Alon's studied evolutionary settings. This supports a conditional
donor hypothesis, not a theorem about all cognitive architectures.
[Spontaneous evolution of modularity and network motifs](https://pubmed.ncbi.nlm.nih.gov/16174729/).

Clune, Mouret and Lipson found that selection including connection costs
produced greater modularity and evolvability in their computational experiments.
This makes cost-driven modularity parent-owned.
[The evolutionary origins of modularity](https://arxiv.org/abs/1207.2743).

Automated agent design and workflow search already operate over agent code,
building blocks and execution feedback. Architecture modification itself is
therefore insufficient for an OCM novelty claim.
[Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435),
[AFlow](https://arxiv.org/abs/2410.10762).

These sources do not validate the external simulation numbers or establish
OCM's proposed residual. Sparse causal discovery, interventional system
identification, dynamic slicing/incremental computation, change-impact analysis,
ATMS, modular program/library learning and learned optimization remain required
parents for the next source-specific saturation review.

## Checkpoint

- THEORY QUESTION: Does learned cognitive structure lower complete future diagnosis, repair and preservation cost beyond matched adaptive parents?
- CURRENT HYPOTHESIS: Reusable and discoverable structure can produce a conditional lifetime advantage; graph sparsity alone is neither a locality guarantee nor necessary for computational savings.
- STRONGEST PARENT: Causal/system identification, incremental computation, change-impact analysis, ATMS, structured optimization and automated architecture search; source-specific saturation remains open.
- FORMAL OBJECT: Constitution-relative affected obligations and repair footprint over fixed external contracts, paired interventions and a declared lifecycle horizon.
- PREDICTION: ESD-01 through ESD-04 specify prospective directions; executable protocols and statistical gates remain unfrozen.
- FALSIFIER: No paid learned-structure benefit beyond parents, structure gifts required, incorrect effect predictions or preservation cost erasing savings.
- VERIFICATION ROUTE: V2 for elementary finite countermodels; V3 proposed, NOT RUN, for learned OCM structure.
- EMPIRICAL RUNG: Failure/composition, representation discovery and lifetime scaling; no new rung exit.
- RESULT: Anchored probes cannot distinguish xyz from zero; four sparse paths have global effects; exhaustive parity checks for n=4..10 confirm shared-computation savings under dense influence.
- NEGATIVE / COUNTEREXAMPLE: Low edge density does not bound transitive repair; incomplete pairwise probing can miss higher-order effects; high coupling can coexist with work savings.
- WHAT WAS REMOVED OR MERGED: Necessary-sparsity claim; unqualified kappa(M); quality-threshold-as-obstruction language; treating supplied dispatch factorization as discovered structure.
- WHAT SURVIVES: Conditional learned-structure payback hypothesis and a governed route for testing it.
- CLAIM CEILING: Elementary exact counterexamples and prospective theory specification. Neither external simulations nor the earlier dispatcher pilot validate learned-factorization superiority.
- EXACT ARTIFACTS: verify_structure_counterexamples.py; results/structure-counterexamples-v1.json; STRUCTURE_DISCOVERY_REGISTRY_V1.json; EXTERNALLY_REPORTED_FACTORIZATION_V1.json.
- NEXT DECISIVE TEST: On actual-source disjoint development incidents, learn effects without supplied grouping/diagnoses, predict unseen intervention consequences, then compare complete repair costs against equally informed adaptive parents. Freeze that executable protocol before outcomes.
