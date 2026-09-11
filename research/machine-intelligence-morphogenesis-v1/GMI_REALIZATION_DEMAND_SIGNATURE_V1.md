# GMI Realization Demand Signature v1

Status: **HARDENED CANDIDATE CROSS-PARADIGM HYPOTHESIS — NOT A LAW**

Supersedes the variable semantics of `GMI_REALIZATION_DEMAND_SIGNATURE_V0.md` for future work.

The v0 signature mixed two different things:

```text
what information / structure the obligation makes available
vs
how well a particular morphology can exploit that information / structure
```

This v1 separates them.

---

# 1. Core decomposition

For a registered obligation

\[
\Omega=(\mathcal E,D,J,V,C,H,\mathcal R),
\]

define an **obligation-side demand description**

\[
\boxed{
\Xi_\Omega
=
(\sigma,\tau_{\mathcal L},\delta,\phi,\nu,\chi,\eta,\omega,\pi)
}
\]

and, separately, a morphology response functional

\[
\boxed{
\mathcal R_M(\Xi_\Omega)
}
\]

that describes how morphology `M` realizes those demands.

The scientific object is therefore an interaction:

\[
\text{realization burden/frontier}
=
F(\Xi_\Omega,\mathcal R_M)
\]

rather than a claim that an obligation alone names the winning architecture.

---

# 2. Obligation-side coordinates

## 2.1 `sigma` — semantic distinction burden

`σ` measures how many future-relevant semantic distinctions the registered obligation requires.

Finite exact examples:

\[
\sigma=\log_2 |S_\Omega|
\]

or a declared minimal-state dimension/count under an applicable parent formalism.

Important boundary:

`σ` measures distinction burden, not constructive regularity.

Two obligations can have the same number of exact cases/states but radically different compact descriptions or realizations.

---

## 2.2 `tau_L` — structural / constructive description complexity

The v0 signature omitted a crucial quantity:

> How compactly can the registered semantic mapping/dynamics be described in a prospectively fixed constructive language `L`?

Define provisionally

\[
\tau_{\mathcal L}(\Omega)
=
\min_{p\in\mathcal L:\,p\models\Omega}
L_{\mathcal L}(p),
\]

when this minimum is exactly computable at the registered finite scope.

For real expressive systems, use a bounded/upper-bound/profile measurement rather than pretending the Kolmogorov minimum is computable.

### Why `tau_L` is needed

State count alone cannot distinguish, for example:

```text
an 8-row truth table implementing parity
an 8-row truth table implementing an irregular function
```

although parity may have a very short constructive expression in one language.

### Why `tau_L` is dangerous

`τ_L` is **reference-language dependent**.

A language chosen to make one morphology compact can smuggle the answer into the signature.

Therefore every serious use must freeze:

```text
constructive language / code basis before protected outcomes
prior-information content of that language
at least one alternative-language / encoding sensitivity check where material
```

Parents: MDL, circuit/formula complexity, grammar/program compression, Kolmogorov complexity as an uncomputable ideal limit.

No claim of a unique representation-invariant computable `tau` is made.

---

## 2.3 `delta` — semantic dependency/intervention locality

`δ` describes how local the true future-consequence changes are under registered interventions.

Candidate finite measures:

```text
expected affected closure / total semantic coordinates
separator / graph-width statistics
conditional-independence structure
intervention support size
```

This is defined from the obligation/semantic dependency structure, not from how many implementation variables a chosen architecture happens to touch.

Morphology-side update locality is a response to `δ`, not `δ` itself.

---

## 2.4 `phi` — external feedback / teaching channel structure

This replaces v0 `gamma` as the obligation-side object.

`φ` describes what information can legally reach the learner/search process after proposals/actions.

Examples:

```text
binary success/failure
counterexample witness
localized compiler/type error
full supervised target
scalar reward
per-step labels
formal proof-state feedback
gradient oracle explicitly supplied by the problem contract
```

Possible descriptors:

```text
alphabet / observation space
noise model
latency
cost
conditional information about registered hidden target variables
localization/granularity
adaptivity / intervention availability
```

### Critical separation

The same feedback channel can be easy for one morphology to exploit and hard for another.

Therefore **usable credit-information density is not purely an obligation coordinate**.

For morphology `M`, define a response term such as

\[
\zeta_M(\phi)
\]

for the effective extractable learning/search signal under that morphology and legal update process.

Parents: credit assignment, sufficient statistics, information theory, experiment design, optimization.

---

## 2.5 `nu` — drift / invalidation process

`ν` describes how quickly task semantics, evidence, APIs, regimes or correspondence assumptions change relative to useful reuse.

Examples:

```text
version-change hazard
support withdrawal process
task-distribution drift
regime-switch process
```

This is ecology-side.

The actual update/retraining burden caused by `ν` is morphology-side.

---

## 2.6 `chi` — verifier / admissibility channel

`χ` is a structured description of external checking:

```text
cost
strength / coverage
granularity
false-positive / false-negative guarantees or estimates
incrementality
counterexample/witness availability
```

Formal proof, execution tests and empirical/statistical evidence retain distinct semantics.

---

## 2.7 `eta` — effective useful reuse horizon

`η` is the expected number/distribution of useful applications before invalidation, reset, retirement or regime change.

It is not chronological age.

This is the obligation/ecology opportunity for amortization.

The amount of saving per reuse is morphology-side.

---

## 2.8 `omega` — retention/plasticity requirement

This replaces v0 `lambda` to avoid collision with the scalar price functional used elsewhere in the realization principle.

`ω` states what the obligation demands about retention and continued learnability, e.g.:

```text
maximum allowed old-task degradation
minimum new-family acquisition performance
relearning budget
allowed interference
```

The realized retention/plasticity curve is morphology-side.

---

## 2.9 `pi` — physical/resource price regime

`π` is a prospectively declared valuation/constraint regime over raw resources, e.g.:

```text
compute
latency
storage
communication
energy
verification
human input
```

When no scalar price vector is scientifically justified, retain the raw Pareto relation instead of forcing `π` to a scalar.

---

# 3. Morphology response profile

The response of a morphology is not merely its architecture name.

Candidate response components include:

```text
semantic capacity / admissible-distortion curve
constructive compiler overhead from the registered obligation language
build/training/acquisition cost
serving/inference/search cost
update/revision/invalidation cost
zeta_M(phi): effective feedback/credit extractability
locality response to delta
verification integration cost
storage/communication scaling
parallelism/hardware response to pi
retention/plasticity response to omega
morphogenetic discovery cost
```

Architecture labels may be recorded for interpretation, but are not scientific predictor inputs in the cross-paradigm test.

---

# 4. Demand-response sufficiency conjecture v1

`GMI-RSC-1-v1`:

> Over a prospectively registered bounded family of obligations and realizations, a compact obligation signature `Xi_Omega` plus morphology response profiles predicts near-frontier status materially better than trivial task identifiers, while preserving the same coordinate meanings across morphology families.

This is an **empirical compression conjecture**.

It is not a universal theorem.

---

# 5. Cross-paradigm version

`GMI-RSC-2-v1`:

> At least one nontrivial obligation coordinate has predictive value for realization-frontier movement in two or more materially different morphology families after family-native parent predictors receive first refusal.

A valid positive cannot arise by:

```text
renaming condition number as gamma in neural systems
renaming prior mass as gamma in Bayesian systems
renaming code length as gamma in program search
```

unless a formal common measurement object actually maps to all of them.

---

# 6. New exact hostile: coarse-signature collision

The v0 signature can fail even at tiny finite scope.

Consider two exact 3-bit Boolean obligations with matched:

```text
number of input cases
all three inputs semantically relevant
same verifier
same no-drift ecology
same reuse horizon
same retention requirement
same physical prices
same full-output feedback channel
```

but different constructive regularity:

```text
PARITY_3
MAJORITY_3
```

Under a prospectively frozen affine-XOR constructive language:

```text
PARITY_3 has a short affine realization
MAJORITY_3 is not affine and requires another realization in the registered candidate set
```

Therefore a signature omitting constructive regularity can collide while the realization frontier differs.

This does **not** prove `tau_L` is universal; it proves the coarse signature was insufficient.

---

# 7. Signature-completeness lower bound

Let a finite registered obligation set contain `K` distinct realization-ranking equivalence classes under a fixed candidate set and comparison rule.

For an exact sufficient signature `Xi`:

\[
\Xi(\Omega_1)=\Xi(\Omega_2)
\Rightarrow
Ranking(\Omega_1)=Ranking(\Omega_2).
\]

Therefore `Xi` must take at least `K` distinct values.

If it is represented by a fixed `b`-bit code:

\[
2^b\ge K
\quad\Rightarrow\quad
b\ge\lceil\log_2 K\rceil.
\]

This is a pigeonhole/counting bound, not a new intelligence theorem.

Consequences:

- no tiny fixed signature can be exactly sufficient if the registered ranking complexity grows beyond its value capacity;
- a useful low-dimensional `Xi` must exploit real regularity and can only be expected to work conditionally/approximately;
- universal exact completeness over arbitrary expressive obligations is not the target.

---

# 8. Falsifiers

## F1 — exact signature collision

Same measured `Xi`, different realization ranking.

```text
REALIZATION_SIGNATURE_INSUFFICIENT__COLLISION
```

## F2 — constructive-language sensitivity

A claimed `tau_L` phase law reverses materially under another equally defensible frozen constructive language.

```text
DESCRIPTION_LANGUAGE_DOMINATES
```

## F3 — morphology contamination

An alleged obligation coordinate uses morphology-internal states/gradients/parameters unavailable before selecting that morphology.

```text
DEMAND_RESPONSE_BOUNDARY_VIOLATED
```

## F4 — architecture-label proxy

Prediction disappears under reminted surfaces and removal of family identifiers/proxies.

```text
ALGORITHM_SELECTION_ONLY
```

## F5 — family-native sufficiency

Shared coordinates add no held-out-family value beyond native theory.

```text
FAMILY_NATIVE_REALIZATION_THEORIES_SUFFICIENT
```

## F6 — post-outcome identification

Coordinate requires protected target outcomes to estimate.

```text
SIGNATURE_NOT_PRE_OUTCOME_IDENTIFIABLE
```

---

# 9. Revised DS programme

## DS-E0a — realization arithmetic calibration

Already covered by exact Pareto/horizon/discovery-cost microscopes.

## DS-E0b — signature-collision calibration

Freeze tiny obligation pairs where coarse coordinates match but realization rankings differ.

Purpose: discover missing coordinates and bound claims.

## DS-E1 — family-native predictor atlas

For each family, identify the strongest native pre-outcome predictors:

```text
program/library: code length, proposal mass, search tree, reuse horizon
probabilistic: prior mass/KL, likelihood information, posterior concentration
neural/differentiable: conditioning/curvature/representation alignment/credit structure
symbolic/search: branching, heuristic error, constraint propagation/locality
```

Do not relabel these as one law prematurely.

## DS-E2 — shared-coordinate transfer

Test only coordinates with a truly common operational definition.

Use family-held-out evaluation and no architecture labels.

## DS-E3 — collision / remint / price / verifier hostiles

Actively construct matched-signature pairs that should break an incomplete theory.

## DS-E4 — real math/code binding

Only after real E3 episodes exist.

---

# 10. Implication for neural networks

The theory should ask two separate questions:

### Obligation side

Does the ecology supply:

```text
large reusable statistical regularity
high-information feedback / labels
long effective horizon
stable semantics
resource prices favoring dense parallel numerical compute
```

### Neural response side

Can the chosen differentiable morphology exploit that channel efficiently?

```text
credit extractability
optimization conditioning
representation learning
parallelism
serving amortization
retention/plasticity
revision cost
```

Only the interaction can explain frontier occupancy.

This is stronger than saying “gradient tasks favor neural networks,” but it remains an empirical conditional theory.

---

# 11. Implication for the ultimate GMI question

A general machine-intelligence theory need not contain one universal winning architecture or one tiny complete feature vector.

A defensible general form can instead consist of:

```text
1. semantic obligation / sufficient-state semantics
2. admissible realization space
3. obligation-side demand structure
4. morphology response functions
5. complete lifetime frontier
6. bounded morphogenetic search
7. development/meta-development of that search
```

The empirical question is how much of steps 3–4 can be compressed into reusable cross-paradigm laws.

If the answer is “very little,” GMI can still be a coherent synthesis while morphology prediction remains family-native.

---

# 12. Current terminal

```text
REALIZATION_DEMAND_RESPONSE_BOUNDARY_HARDENED_V1
COARSE_SIGNATURE_V0_NOT_ASSUMED_SUFFICIENT
CROSS_PARADIGM_REALIZATION_LAW_REMAINS_OPEN
```
