# Structural signature atlas v1

Status: **parent-saturated map of candidate structure -> developmental-burden predictors.**

Purpose: test whether Track B has discovered a genuinely cross-paradigm invariant, or merely renamed mature paradigm-specific complexity measures.

## 1. Programmatic / library search

Candidate structural predictors already owned by parents include:

```text
program/code length
prefix probability / grammar probability
branching factor
library compression / reusable substructure
enumeration order / Levin-style time-bias
search-tree depth
verification cost
```

Typical burden relation:

\[
\text{proposal burden} \sim 1/Q(program)
\]

or, on a logarithmic scale,

\[
-\log Q(program)
\]

acts as search surprisal. Library learning changes this geometry by changing grammar/prior mass and reusable description length.

Strong parents: algorithmic probability / Levin search, MDL, DreamCoder/Stitch/library learning, program synthesis/search.

## 2. Probabilistic / Bayesian inference

Candidate structural predictors:

```text
prior odds / prior mass
KL divergence / expected log-likelihood ratio
Fisher information
posterior concentration rate
graphical-model factorization / treewidth
mixing time / effective sample size
```

For repeated informative evidence, a posterior-threshold burden is naturally controlled by an initial log-odds gap divided by expected information gain per observation.

Strong parents: Bayesian asymptotics, information theory, information geometry, probabilistic graphical models, MCMC theory.

## 3. Neural / differentiable learning

Candidate structural predictors:

```text
initialization / pretraining-induced distance to useful solutions
loss curvature / Hessian spectrum
condition number
Fisher information geometry
gradient signal-to-noise
spectral gap / contraction factor
NTK / feature kernel regime
effective dimension / margin
optimizer state / learned optimizer bias
```

For a quadratic local model, convergence time is controlled by contraction/condition number. Natural-gradient work explicitly shows that parameter-space geometry changes learning dynamics; modern loss-landscape work studies curvature/connectivity/multiscale structure.

Strong parents: convex optimization, information geometry/natural gradient, dynamical-systems analyses of SGD, NTK/loss-landscape theory.

## 4. Symbolic / production / theorem-proving systems

Candidate predictors:

```text
rule/premise branching factor
match/index selectivity
proof depth / subgoal depth
heuristic rank of useful rule/premise
constraint propagation strength
rewrite/e-graph saturation size
clause width / treewidth-like structure
memoization / learned lemmas/chunks
```

Strong parents: heuristic search, automated theorem proving, production-system indexing, SAT/SMT complexity, proof search, e-graphs.

## 5. Evolutionary / population search

Candidate predictors:

```text
fitness-distance correlation
mutation neighborhood
selection pressure
neutral network connectivity
basin volume
expected one-step drift
population diversity
recombination accessibility
```

Drift analysis already turns a chosen progress potential plus expected local progress into hitting-time bounds. Evolvability/fitness-landscape theory studies how representation changes accessible variation.

Strong parents: evolutionary-computation runtime analysis, fitness landscapes, evolvability/QD.

## 6. OCM-like explicit developmental search

Current measured/available structural quantities include:

```text
library vocabulary size T
selected probe depth D
probe budget beta_D
motif/fragment coverage
validation hit rate
pre-solution guided rank
baseline rank
history-induced proposal ordering
liveness/stand-down state
re-mining horizon
```

#323's direct behavioural receipt measures one geometry consequence rather than a universal invariant:

```text
29 worlds
2741 fresh targets
history proposes the eventual verified solution earlier on 92.5 %
median 1.91 bits search saved
```

The next OCM test is prospectively frozen in `S2G_OCM_PROSPECTIVE_V1.md`; old outcomes may calibrate but cannot validate that predictor.

## 7. What is common?

Across all families, one can write a generic stochastic-development process:

\[
Z_{t+1}\sim K_M(\cdot\mid Z_t,e_t),
\]

with target set `A`, resource cost `c_M`, and a first-hitting burden.

Given a good potential `Phi_M` and expected progress/drift `delta_M`, mature drift / stochastic-shortest-path theory can relate local dynamics to expected hitting cost.

Therefore the following common form is **parent-owned and too generic**:

```text
state space
+ update/proposal kernel
+ target set
+ transition cost
+ potential / progress
-> expected hitting burden
```

## 8. The unresolved cross-paradigm question

What is *not* currently supplied by a common parent theorem is a useful morphology-neutral map

\[
\boxed{
\Psi_{S2G}: (structure, update law, legal history, ecology features)
\to
\text{compact predictive geometry signature}
}
\]

that simultaneously:

1. is computed before protected target outcomes;
2. has bounded information/measurement cost;
3. predicts verified developmental burden/frontier across materially different paradigms;
4. survives representation changes and ordinary compiler wrappers;
5. admits causal intervention: changing the predicted signature changes burden as forecast;
6. does not simply include a complete simulator of the morphology.

## 9. Why a universal scalar is unlikely

The parent measures above are structurally different:

```text
program probability / code length
Bayesian information gain / KL
neural curvature / contraction
symbolic branching / proof depth
evolutionary drift / neighborhood geometry
```

For arbitrary Turing-complete systems an exact universal burden predictor is blocked by computability limits (`UNIVERSAL_GEOMETRY_PREDICTOR_NO_GO_V1.md`).

The scientifically plausible target is therefore either:

- a **restricted invariant family** for declared morphology/ecology classes; or
- a **vector signature** whose components have cross-paradigm interpretations and calibrated transformations.

## 10. Candidate vector, strictly provisional

A useful attack surface—not a novelty claim—is:

\[
G_M=(S_0,\Delta,I,C,U,P)
\]

where:

- `S0`: initial target surprisal / mismatch under the morphology's own proposal representation;
- `Delta`: expected useful progress per legal update/action;
- `I`: information gained per paid observation/evaluation;
- `C`: raw per-update resource vector;
- `U`: update locality / fraction of stored competence touched;
- `P`: retention/plasticity response under repeated updates.

Every component has strong parents. Track B only earns anything if a frozen transformation of such quantities predicts held-out cross-paradigm phase/frontier results better than parent baselines.

## Terminal

```text
PARADIGM_SPECIFIC_STRUCTURE_TO_BURDEN_PARENTS_STRONG
GENERIC_HITTING_TIME_FORM_PARENT_SUFFICIENT
CROSS_PARADIGM_PRE_OUTCOME_SIGNATURE_REMAINS_OPEN
```
