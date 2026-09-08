# Machine Epistemics Evolvability Theory V0
## Causal factorization, bounded cognitive operators, and governed self-evolution

**Status:** PROVISIONAL THEORY + EXPLORATORY SYNTHETIC FALSIFICATION.  
**Claim authority:** NO OCM SUPERIORITY CLAIM. NO NEURAL-NETWORK SUPERIORITY CLAIM. NO UNIVERSAL COGNITIVE BASIS CLAIM.  
**Programme:** #143 empirical cognitive ladder; #144 publication constitution; #145 operator/field theory bridge; #93 General Epistemic Field; #13 M11 self-reorganisation.  
**Source baseline:** ORION-OCM `main@3430919fd7614589e4fcfb9756dfaffb6ef1b3b4` when this V0 was written.  
**Synthetic evidence:** `research/evolvability-theory-v0/SYNTHETIC_RESULTS_V0.json`; reproducible with `synthetic_evolvability.py`.

---

## 0. Why this theory exists

The current Machine Epistemics programme has accumulated a repeated pattern.

Mechanisms look distinctive while useful structure is supplied:

- a family/relevance key makes sparse lookup easy;
- an authored failure cause makes scoped failure memory easy;
- an authored dependency graph makes exact local revision easy;
- a benchmark generator's intended defect class makes minimum-escalation diagnosis easy;
- an authored operator/representation catalogue can make a supposed cognitive primitive look necessary.

When those gifts are removed, much of the apparent OCM residual can collapse into strong classical parents.

That is not a reason to abandon Machine Epistemics. It changes the central object.

> **The core scientific problem is not operating over explicit epistemic structure. It is discovering, maintaining, exploiting, and when necessary reorganising the right epistemic structure.**

The central theory proposed here is therefore about **epistemic evolvability**:

> A machine can obtain a distinct lifetime advantage when it learns a sufficiently accurate and sufficiently sparse causal factorization of its own knowledge, methods, representations, control and learning processes, so that future cognition and future self-improvement can usually operate on a small affected substructure rather than globally re-optimising the whole machine.

The theory is deliberately conditional. Dense coupling, expensive diagnosis, rapid structural drift, or a stronger parent may erase the advantage.

---

# 1. Machine object

Use the current programme factorization:

```text
M_t = (F_t, O_t, Π_t, C)
```

where:

- `F_t` = persistent epistemic field/state;
- `O_t` = executable operator algebra, including learned methods/macros;
- `Π_t` = executive/navigation/composition policy;
- `C` = protected constitution / authority / checking / adoption boundary.

For self-evolution we require one more derived object:

```text
S_t = SelfModel(M_t)
```

`S_t` is not an authority oracle. It is evidence-grounded state about components, dependencies, costs, failures, predictions, revisions and lineage.

The critical distinction is:

```text
machine state
!=
machine model of machine state
!=
authority to change machine state
```

`S_t` may propose and predict. `C` remains external.

---

# 2. The causal-factorization object

Let the machine contain a finite registered set of cognitive components:

```text
V_t = {
  representations,
  operators,
  methods,
  routers,
  indexes,
  learning policies,
  support objects,
  checkers/interfaces,
  ...
}
```

Define a directed typed hypergraph:

```text
H_t = (V_t, E_t)
```

where a hyperedge represents a registered causal/epistemic dependence relevant to at least one observable machine obligation.

Examples:

- evidence set -> learned method validity;
- representation coordinates -> operator applicability;
- operator + router -> task execution;
- method schema + scope -> reusable invocation;
- index/router -> active-subspace selection;
- learning policy + episodes -> acquired method;
- checker version -> admitted correctness warrant.

`H_t` must distinguish at least:

```text
support dependency
execution dependency
representation dependency
routing dependency
learning dependency
authority/check dependency
resource dependency
```

A string-level call graph is not sufficient.

---

# 3. Effective cognitive coupling

For an intervention/failure/change `z`, let:

```text
Closure_H(z)
```

be the minimal registered set of components whose correctness, warrant, applicability, cached state or execution may need reconsideration after `z`.

Define the normalized effective coupling:

```text
κ_H(z) = |Closure_H(z)| / |V|
```

and over a registered ecology `E`:

```text
κ(M; E) = E_z~E [ κ_H(z) ].
```

Interpretation:

- `κ ≈ 0`: most changes are highly local;
- intermediate `κ`: modular but meaningfully coupled;
- `κ ≈ 1`: most changes potentially require global reconsideration.

This is not graph density. A dense representation can still have a small true causal closure; a sparse stored graph can omit real dependencies and falsely report locality.

Therefore every measured `κ` requires dependency-coverage hostiles.

---

# 4. Evolvability

For a machine generation `g`, define a self-change episode:

```text
failure/opportunity
→ diagnosis
→ candidate proposal
→ challenger construction
→ shadow evaluation
→ assurance
→ external adoption/rejection
→ migration/reopening
→ monitoring/rollback
```

Let the complete cost vector be:

```text
C_evolve =
(
  diagnostic information,
  counterfactual probes,
  candidate generation,
  challenger executions,
  checker calls,
  storage,
  migration,
  preservation testing,
  rollback,
  wall/CPU/GPU/energy
)
```

A machine is more **epistemically evolvable** in ecology `E` if, at matched post-change capability and preservation, it reaches warranted useful adaptations with a better Pareto resource vector.

Do not collapse this into one scalar for headline claims.

A secondary coordinate may be:

```text
ECP_r(Q*) =
  Resource_parent,r(to reach Q*)
  /
  Resource_machine,r(to reach Q*)
```

but the primary result is the multi-objective frontier.

---

# 5. Local-evolution hypothesis

Suppose a failure has true affected closure `D` in `H`, with:

```text
d = |D|
N = |V|.
```

If:

1. the causal factorization is sufficiently accurate;
2. the target obligation decomposes over the registered closure;
3. the checker/assurance interface can validate the local change;
4. hidden global maintenance is charged;
5. the candidate change space is localized by the same evidence;

then the candidate Machine Epistemics regime predicts:

```text
C_repair ≈ C_diagnose + f(d)
```

rather than:

```text
C_repair ≈ g(N)
```

for a global search/retraining parent.

This is a scoped empirical prediction, not a universal complexity theorem.

A formal theorem may be possible only under much stronger assumptions about complete dependency semantics and decomposable validation.

---

# 6. The diagnosis-value inequality

Diagnosis itself costs resources.

Let:

```text
C_D = cost of diagnosis/probes
C_L = expected local repair search after diagnosis
C_G = expected global/blind repair search
```

Then diagnosis has positive immediate value only if:

```text
C_D + C_L < C_G.
```

This simple inequality is load-bearing.

The synthetic falsification harness demonstrates both regimes:

- with low-noise, cheap probes, diagnosis-guided repair beats blind search;
- when probes are expensive or noisy, diagnosis becomes more expensive than blind search.

Therefore:

> **Self-modeling is not automatically useful. It must earn its cost by reducing downstream uncertainty/search sufficiently.**

---

# 7. Factorization amortization

Learning and maintaining `H_t` has a cost.

Let:

```text
C_F       = initial factorization-discovery cost
C_M(t)    = factorization maintenance/audit cost at episode t
C_local(t)= local cognitive/repair cost
C_global(t)= global parent cost
```

Over lifetime horizon `T`:

```text
C_structured(T)
  =
  C_F + Σ_t [ C_M(t) + C_local(t) ]

C_global(T)
  =
  Σ_t C_global(t).
```

Structured cognition has a lifetime resource advantage only if:

```text
C_F + Σ_t [C_M(t)+C_local(t)]
<
Σ_t C_global(t).
```

Under an approximately stationary ecology:

```text
T* ≈ C_F / (C_global - C_local - C_M)
```

is the crossover horizon when the denominator is positive.

If the denominator is non-positive, no lifetime crossover exists.

This explains why explicit epistemic machinery may lose on early tasks yet become competitive later, but it also provides a hard falsifier: if the registered lifetime does not reach the crossover, the claimed advantage is not present at that scope.

---

# 8. Structural drift

The factorization itself can become stale.

Let:

```text
δ_H(t) = structural drift of the true causal organization.
```

As drift rises:

```text
C_M ↑
false locality risk ↑
required refactorization frequency ↑.
```

Blind periodic rebuild is not the desired solution because:

```text
rebuild cost may dominate the entire advantage.
```

The candidate control law is:

```text
local operation
→ audit/prediction
→ detect mismatch/obstruction
→ refactorize only when required.
```

This turns ORION's obstruction/Jump idea into a narrower statement:

> **A high-level representation/organization change is justified when the incumbent factorization makes a registered prediction that fails in a way no allowed local repair can explain or satisfy.**

Timeout, low score, novelty and saturation alone are insufficient.

---

# 9. Obstruction-triggered refactorization

Define an obstruction certificate for factorization `H_t`:

```text
incumbent identity
registered local repair family
attempted local alternatives
resource bound
observed failure/prediction mismatch
evidence that local closure is insufficient
candidate higher-level change
preservation obligations
```

Then:

```text
H_t
→ local repair attempts
→ obstruction
→ propose H'_t
→ pre-outcome prediction
→ shadow evaluation
→ external adoption
→ H_{t+1}.
```

The theory predicts that **rare** justified refactorization can dominate either extreme:

- never reorganize;
- reorganize periodically/global-by-default.

This remains to be tested in the real OCM without oracle cause labels.

---

# 10. The capability–evolvability tension

Maximum modularity is not the objective.

A field/operator organization can be highly modular but unable to represent the necessary computation. Conversely, a fully entangled representation may fit tasks well but be expensive to diagnose, revise or extend.

The target is therefore a Pareto frontier over:

```text
task capability
acquisition cost
query/reasoning cost
revision cost
self-change cost
storage
maintenance
robustness
transfer
```

The V0 synthetic NK study demonstrates the expected phase behavior:

- sparse interactions: factorized local search can reach nearly the same quality as a much more expensive evolutionary parent, and strongly beats it at roughly matched cost;
- dense interactions: the high-budget evolutionary parent attains materially better quality and the local-factorization advantage is not established.

Thus:

> **Machine Epistemics predicts a regime advantage, not universal domination.**

---

# 11. Synthetic falsification results V0

These results are **E2 exploratory synthetic evidence only**. They are not an OCM experiment and the evolutionary parent is not the strongest possible learned optimizer.

## 11.1 Diagnosis phase boundary

Eight hidden fault classes, six noisy probes and twelve repair candidates were used.

Illustrative results:

| probe noise | probe cost | blind/guided cost ratio | guided fault accuracy |
|---:|---:|---:|---:|
| 0.05 | 0.05 | 1.55 | 0.857 |
| 0.05 | 0.20 | 1.15 | 0.850 |
| 0.05 | 0.80 | 0.59 | 0.858 |
| 0.15 | 0.05 | 1.24 | 0.622 |
| 0.15 | 0.20 | 0.89 | 0.609 |
| 0.30 | 0.05 | 0.98 | 0.346 |

Ratio > 1 favors diagnosis-guided search.

Result:

```text
cheap + informative diagnosis
→ useful

expensive/noisy diagnosis
→ parent/blind search can dominate
```

This falsifies any unconditional "self-modeling helps" claim.

## 11.2 Lifetime factorization versus high-budget evolutionary search

Synthetic NK-style binary architectures used `N=10` components for 30 adaptation generations.

The factorized arm:

- discovers an intervention structure;
- uses local component evaluation;
- audits one random component each generation;
- refactorizes when the audit exposes structural drift.

The high-budget evolutionary arm gets 48 full evaluations per generation.

| K | drift | factor quality/opt | evolutionary quality/opt | factor cost | evo cost |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.973 | 0.975 | 400 | 1440 |
| 2 | 0.00 | 0.951 | 0.956 | 473 | 1440 |
| 2 | 0.03 | 0.948 | 0.952 | 548 | 1440 |
| 2 | 0.10 | 0.954 | 0.960 | 607 | 1440 |
| 5 | 0.00 | 0.882 | 0.908 | 516 | 1440 |
| 5 | 0.03 | 0.877 | 0.913 | 654 | 1440 |
| 5 | 0.10 | 0.884 | 0.913 | 744 | 1440 |

With a hypothetical prospectively frozen non-inferiority margin `δ=0.01`, the `K<=2` rows would be capability-noninferior to this parent while using approximately 2.4–3.6x fewer full-evaluation-equivalent resources. The `K=5` rows fail that capability margin.

This `δ` is descriptive only here; it was not preregistered and is not a scientific terminal.

## 11.3 Approximately matched-cost comparison

The evolutionary parent is reduced to 18 evaluations per generation.

| K | drift | factor quality/opt | evolutionary quality/opt | factor cost | evo cost |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.00 | 0.981 | 0.918 | 411 | 540 |
| 2 | 0.00 | 0.962 | 0.889 | 479 | 540 |
| 2 | 0.03 | 0.953 | 0.892 | 537 | 540 |
| 5 | 0.00 | 0.880 | 0.866 | 509 | 540 |

This supports the qualitative prediction that causal factorization can improve the quality/resource frontier in sufficiently sparse regimes.

It does **not** establish superiority over neural/learned surrogate optimization, AutoML, Bayesian optimization or other stronger parents.

---

# 12. The central phase diagram

The theory predicts four broad regimes.

## Regime A — sparse, stable, observable

```text
low κ
low structural drift
cheap discriminating probes
reusable causal structure
```

Prediction:

```text
factorization investment amortizes
local cognition/revision/self-change dominates global work
```

This is the most favorable Machine Epistemics regime.

## Regime B — sparse but drifting

```text
low/moderate κ
meaningful structural drift
```

Prediction:

```text
obstruction-triggered refactorization can preserve advantage
until maintenance cost dominates
```

## Regime C — dense/entangled

```text
high κ
many high-order interactions
```

Prediction:

```text
local diagnosis loses predictive sufficiency
global/statistical optimization gains relative value
```

Machine Epistemics may still contribute warrant/revision/governance but no efficiency superiority should be presumed.

## Regime D — unobservable/non-identifiable

```text
insufficient probes
hidden evaluator defects
ambiguous responsibility
```

Prediction:

```text
SELF_DIAGNOSIS_NOT_IDENTIFIABLE
or CANNOT_CHECK
```

No self-change escalation is warranted merely because performance is poor.

---

# 13. Implication for neural systems

The theory does not predict "OCM beats neural networks."

It predicts a division of labor.

Neural/statistical systems are naturally attractive when:

```text
representation is distributed
dependencies are dense
large coupled parameter updates are useful
many examples amortize training
```

Explicit Machine Epistemics is potentially attractive when:

```text
dependencies can be discovered and localized
corrections must be exact
evidence/source changes frequently
new information is scarce
task families reuse methods
self-change must preserve unrelated capability
```

A likely mature system may be hybrid:

```text
explicit epistemic field
+ learned/parametric proposal/routing modules
+ exact authority/check/revision semantics.
```

The scientific question is which functions should remain explicit and which should be parametric under each regime.

---

# 14. The field/operator co-design law

Operator minimality cannot be studied independently of field structure.

For field `F`, operator basis `O`, executive `Π`:

```text
Complexity(F)
↔ Complexity(O)
↔ Complexity(Π)
↔ coupling κ
↔ lifetime cost.
```

A richer field may make operators simpler but increase storage and maintenance.

A poorer field may require expensive operators to rediscover structure every time.

The target is not:

```text
minimum |O|
```

but:

```text
minimum useful lifetime Pareto cost
subject to registered capability and epistemic correctness.
```

---

# 15. Grand Unified operator hypothesis

An absolute minimal operator set is not meaningful because a single unrestricted universal transform can simulate all computation.

The scientifically meaningful target is:

> **A small resource-bounded, representation-relative, epistemically preserving generating basis.**

Begin overcomplete with candidate families:

```text
SELECT / FOCUS
DECOMPOSE
EXPAND / GENERATE
COMPOSE
DISTINGUISH / PROBE
RE-REPRESENT / ABSTRACT / REFINE
CHECK / VERIFY
REVISE / REOPEN
CONSOLIDATE / GENERALIZE
```

Then recursively attempt to remove or compile each operator.

For candidate `o`, test:

### Algebraic residual
```text
o not generated by O \ {o}
```

### Resource residual
```text
replacement exists but exceeds registered resource bound
```

### Epistemic residual
```text
replacement matches immediate answers
but fails warrant/scope/dependency/revision behavior
```

If none survive, merge/delete `o`.

Multiple equivalent bases are expected.

---

# 16. Primitive pressure

Let:

```text
P_j =
number of genuinely new primitive operators required
after adding domain/rung j.
```

Competing hypotheses:

### H-CLOSURE
```text
P_j -> 0
```
after sufficient heterogeneous experience; later competence grows mainly through composition/macros.

### H-OPEN
```text
P_j remains materially nonzero
```
because cognition requires an open-ended primitive language.

### H-PHASED
`P_j` is low within validation/representation regimes and spikes at regime transitions.

No short sequence of zeros establishes closure.

---

# 17. Epistemic structure discovery

The theory implies a common acquisition problem across current failures:

```text
episodes
→ infer reusable methods
→ infer applicability/scope
→ infer dependencies/support alternatives
→ infer useful representation
→ infer relevance/navigation structure
→ infer failure responsibility
```

These should not be separate hand-authored gifts.

A mature OCM should increasingly learn:

```text
H_t
F_t organization
O_t macros/methods
Π_t routing policy
```

from experience, while `C` stays externally governed.

---

# 18. Self-evolution

A serious self-evolution claim requires at least:

```text
M_0
→ evidence
→ diagnosis
→ proposal
→ shadow
→ adoption
→ M_1
→ new disjoint experience
→ second diagnosis/proposal
→ M_2
```

One successful repair is adaptation, not recursive self-improvement.

For each generation record:

```text
machine fingerprint
field/operator/executive delta
proposal origin
development evidence
prediction
shadow result
preservation result
resource delta
rollback artifact
fresh protected result
```

Imported human/ORION/LLM solutions are not autonomous invention.

---

# 19. The evolvability objective

Do not optimize only current task score.

A candidate machine can be better today and much harder to improve tomorrow.

Therefore evaluate both:

```text
current capability
future adaptation burden.
```

One conceptual regularizer is:

```text
minimize expected κ(M;E)
```

subject to capability and correctness constraints.

But minimum coupling itself is not the objective; artificial decoupling can destroy useful computation.

The actual target is the **Epistemic Evolvability Frontier**:

```text
Pareto(
  task quality,
  new information burden,
  query work,
  revision work,
  self-change work,
  storage,
  maintenance,
  regression risk
)
```

over a declared lifetime ecology.

---

# 20. Predictions for the empirical ladder

## CL-1 exact games
Prediction: learned reusable methods should reduce future search only if method identity/scope are discovered rather than task-keyed.

## CL-2 composition/failure
Prediction: structured negative knowledge matters only after failure responsibility is inferred; otherwise TMS/nogood parents dominate.

## CL-3 representation
Prediction: useful representation change should reduce effective coupling or bounded reach/search cost on held-out worlds.

## CL-4 planning
Prediction: reusable subgoal structure should reduce future acquisition/search and induce localized responsibility.

## CL-5 DISTINGUISH
Prediction: diagnostic probes help only when their information value exceeds their cost.

## CL-6 lifetime scaling
Prediction: query/revision/self-change cost can track local active/affected structure only after charging factorization/index/maintenance.

## CL-7 cross-family
Prediction: a genuine cognitive method should transfer with its operator identity frozen before target-family access.

## CL-8 formal math
Prediction: exact proof environments make support/dependency/method structure measurable and provide strong local-revision tests.

## CL-9 controlled language
Prediction: ambiguity and correction test whether the same DISTINGUISH/REVISE mechanisms survive a different validation semantics.

## CL-10 heterogeneous lifetime
Primary test: whether the learned factorization/operator basis remains useful as domains accumulate and whether its construction cost amortizes.

---

# 21. Formal-theory obligations

The following are promising theorem targets, not established theorems:

1. **Local revision sufficiency:** conditions under which complete support semantics imply exact closure-local invalidation.
2. **Factorized evaluation bound:** conditions under which candidate evaluation cost is proportional to affected component closure.
3. **Amortization bound:** crossover horizon under stationary/recurrent ecologies.
4. **Obstruction soundness:** conditions where failure of all registered local repairs licenses a higher-level representation/operator proposal.
5. **Compilation/equivalence:** bounded-cost equivalence between candidate cognitive operator bases.
6. **Coupling lower bounds:** task families where any correct representation must maintain large interaction closures.
7. **No-free-factorization theorem:** learning a dependency structure requires enough discriminating interventions/information; local scaling cannot be claimed if that acquisition cost is hidden.

---

# 22. Strongest parents

This theory is heavily parent-colliding.

Depending on the row, first right of refusal includes:

```text
ATMS/TMS/minimal support
databases/indexes/materialized views
incremental computation
causal discovery
Bayesian diagnosis
active learning / value of information
CEGAR / CEGIS
program repair
AutoML
Bayesian optimization
evolutionary search
neural architecture search
meta-learning / meta-RL
continual learning
DreamCoder / Stitch / library learning
Soar / ACT-R / NARS
OpenCog / Hyperon
mixture-of-experts / modular neural networks
learned retrieval / RAG / memory systems
Transformer + tools + persistent memory + adaptation
```

If a faithful parent learns the same factorization and obtains the same or better frontier:

```text
PARENT_SUFFICIENT
```

is the correct result.

---

# 23. Hard falsifiers

The theory contracts or fails if, under fair matched studies:

```text
factorization discovery cost never amortizes
local work only looks sparse because global maintenance is hidden
dependency discovery is too inaccurate for safe revision
effective coupling remains near-global across useful domains
high-order interactions make local responsibility non-identifiable
strong learned parents obtain the same frontier
self-change proposal/search costs dominate
structural drift requires near-continuous refactorization
cross-domain transfer requires new task-specific cognitive cores
primitive pressure remains high with no stable reusable basis
```

Valid terminals include:

```text
EPISTEMIC_FACTORIZATION_SUPPORTED_AT_SCOPE
LOCAL_EVOLVABILITY_SUPPORTED_AT_SCOPE
DIAGNOSIS_VALUE_POSITIVE_AT_SCOPE
AMORTIZED_FACTORIZATION_SUPPORTED
OBSTRUCTION_TRIGGERED_REFACTORIZATION_SUPPORTED
TRADEOFF_FRONTIER_ONLY
DENSE_COUPLING_LIMIT
STRUCTURAL_DRIFT_DOMINATES
SELF_DIAGNOSIS_NOT_IDENTIFIABLE
FACTOR_DISCOVERY_COST_DOMINATES
PARENT_SUFFICIENT
NO_SMALL_GENERAL_OPERATOR_BASIS
CANNOT_CHECK
```

---

# 24. Current claim ceiling

The strongest statement licensed by this V0 is:

> **Exploratory synthetic results are consistent with a conditional Machine Epistemics hypothesis: when a machine's adaptive behavior admits a stable, discoverable and sufficiently sparse causal factorization, explicit structure can substantially reduce the resource cost of diagnosis and repeated adaptation at near-matched capability; increasing diagnostic cost, interaction density or structural drift reduces or reverses that advantage.**

Not licensed:

- OCM currently has this advantage;
- OCM will evolve to an optimum;
- OCM beats neural networks;
- a fixed Grand Unified operator basis exists;
- factorization is always beneficial;
- the synthetic crossover transfers to real tasks.

---

# 25. Central research question

The programme can now be condensed to one question:

> **Can a machine learn an explicit causal factorization of its own cognition such that both ordinary cognition and future self-improvement become increasingly local and amortized across a heterogeneous lifetime, without losing capability relative to the strongest adaptive neural and classical parents?**

A positive answer would connect:

```text
persistent epistemic field
+ reusable methods
+ sparse active cognition
+ exact local revision
+ failure diagnosis
+ representation change
+ governed self-reorganization
```

under one mechanism: **learned causal factorization**.

A negative answer would still be important: it would show that explicit epistemic organization does not create a distinct scaling/evolvability regime beyond strong adaptive parents.

That is the theory V0 is intended to test.
