# Predictive-state / minimal-state parent analysis v1

Status: **parent subtraction for Track-B Question 1**.

A recurring temptation is to identify a universal “basic cognitive state” by looking for the smallest internal representation. Mature parent theory already gives several precise but **ecology-relative** notions of minimal state.

---

# 1. Computational mechanics — causal states

Shalizi & Crutchfield's computational mechanics defines causal states by grouping histories that induce the same conditional distribution over futures.

Schematically:

\[
h_1 \sim h_2
\quad\Longleftrightarrow\quad
P(Future\mid h_1)=P(Future\mid h_2).
\]

The resulting `epsilon`-machine is minimal among equally predictive representations under the paper's assumptions; causal states are sufficient and have a uniqueness/minimality result relative to prediction.

Primary parent:

- Shalizi & Crutchfield, *Computational Mechanics: Pattern and Prediction, Structure and Simplicity*, Journal of Statistical Physics 104 (2001), DOI 10.1023/A:1010388907793.

Track-B consequence:

```text
minimal predictive state
```

is parent-owned for stochastic processes. A larger OCM state is not more fundamental merely because it carries richer explicit semantics.

---

# 2. Input-output causal states / epsilon-transducers

Barnett & Crutchfield extend computational mechanics to input-output processes, constructing `epsilon`-transducers for stochastic mappings between input and output processes.

Primary parent:

- Barnett & Crutchfield, *Computational Mechanics of Input-Output Processes: Structured Transformations and the epsilon-Transducer* (2015), DOI 10.1007/s10955-015-1327-5.

Track-B consequence:

The move from autonomous prediction to input-conditioned transformations already has a minimal predictive-process parent. “A cognitive unit is an input/output stateful predictor” is therefore not a new ORION idea.

---

# 3. Predictive State Representations

Littman, Sutton & Singh represent controlled-system state using multi-step, action-conditional predictions of future observations rather than latent POMDP state. Their linear PSR construction can require no more predictive coordinates than states in a minimal POMDP model under the stated finite setting.

Primary parent:

- Littman, Sutton & Singh, *Predictive Representations of State*, NeurIPS 2001.

Track-B consequence:

```text
state = predictions of consequences of future action/observation tests
```

is a strong parent for any claim that cognition fundamentally needs an explicit world-state ontology.

---

# 4. Bisimulation / state abstraction for control

Ferns, Panangaden & Precup develop bisimulation-based metrics for MDP states, relating behavioral similarity to value differences and enabling state aggregation.

Parent family:

- Ferns, Panangaden & Precup, *Metrics for Finite Markov Decision Processes* (UAI 2004).
- subsequent continuous/bisimulation-metric work.

Track-B consequence:

The “right” state distinctions for control may be coarser than full world identity and depend on rewards/transitions/action relevance.

This is closely aligned with ORION's earlier “decision-sufficient state” intuition, but the abstraction principle is strongly parent-owned.

---

# 5. Three different minimality questions

Track B must not conflate:

## M1 — minimal generating basis

What primitive process/composition/update structure is sufficient to construct adaptive systems?

## M2 — minimal predictive state

What quotient of interaction history preserves the future distribution relevant to prediction?

## M3 — minimal decision/control state

What quotient preserves the action/value distinctions required by a task/control contract?

They need not have the same answer.

A morphology can use the same primitive basis while adopting very different predictive/control representations.

---

# 6. Ecology relativity

Minimal state is not generally independent of the question being asked.

Changing any of the following can refine/coarsen the sufficient quotient:

```text
future horizon
allowed actions/interventions
observation channel
reward/task objective
verification obligation
uncertainty tolerated
resource bound
```

Thus Track B should avoid searching for one fixed universal state schema.

A more plausible theory is:

\[
State^*(E,task,resource,verification)
\]

or a Pareto family of sufficient representations.

This feeds directly into morphology phase laws: representation complexity itself can be an ecology-dependent variable.

---

# 7. Implication for the fundamental-unit hypothesis

The best current decomposition is becoming:

```text
adaptive process / learner unit       <- strong learner/lens/coalgebra parents
predictive/control state quotient     <- causal-state/PSR/bisimulation parents
organization/topology/update regime   <- morphology
resource/ecology selection            <- morphogenesis phase law
```

This makes a single OCM-specific atom increasingly unlikely to be the scientifically useful answer.

Possible Track-B terminal:

```text
PARENT_PREDICTIVE_STATE_THEORY_SUFFICIENT_FOR_STATE_MINIMALITY
```

while Track B retains the higher-order question:

> How do ecology, feedback, verification and resource constraints determine which predictive state, topology and update morphology jointly occupy the developmental frontier?

---

# 8. New hostile for future morphology search

Any candidate “new representation” must be compared against at least one appropriate predictive/control quotient parent.

If two candidate internal states differ but induce the same relevant future/action distributions and no resource advantage survives, count them as morphology-equivalent at the registered scope rather than as new intelligence structure.
