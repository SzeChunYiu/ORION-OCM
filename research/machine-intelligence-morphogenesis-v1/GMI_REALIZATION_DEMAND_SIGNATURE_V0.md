# GMI Realization Demand Signature v0

Status: **CANDIDATE CROSS-PARADIGM HYPOTHESIS — NOT ESTABLISHED**

This document asks whether GMI can move above family-specific architecture selection without inventing architecture labels into the predictor.

The target is not:

```text
if image task -> neural
if logic task -> symbolic
```

That is taxonomy/algorithm selection.

The target is:

> Can a compact pre-outcome description of a cognitive obligation predict the resource/organizational properties that an efficient realization must have, and therefore predict morphology-frontier transitions across materially different machine families?

---

# 1. Obligation-side object

For registered obligation

\[
\Omega=(\mathcal E,D,J,V,C,H,\mathcal R),
\]

define a candidate **realization demand signature**

\[
\Xi(\Omega)
=
(\sigma,\delta,\gamma,\nu,\chi,\eta,\lambda,\pi).
\]

The coordinates are not assumed independent or complete.

They are candidate measurable functionals of the obligation/ecology, not architecture labels.

---

# 2. Candidate coordinates

## 2.1 `sigma` — semantic state complexity

Question:

> How many future-relevant distinctions must an admissible realization preserve?

Possible finite/exact measures:

```text
log2(number of exact semantic developmental equivalence classes)
minimal automaton / quotient state count
minimal sufficient predictive-state dimension where parent theory applies
```

Possible approximate/statistical measures require an explicitly frozen distortion contract.

Interpretation:

- high `sigma` means a large semantic distinction burden;
- low `sigma` means aggressive state merging may be possible.

This is task/obligation relative, not physical memory size.

Parents: automata minimization, predictive-state representations, epsilon-machines, information bottleneck.

---

## 2.2 `delta` — dependency / intervention locality

Question:

> When one semantic coordinate/evidence/source changes, how local is the true affected future consequence set?

Candidate measures:

```text
expected descendant-closure fraction
separator / treewidth-like structure
conditional-independence factorization
intervention support size
local repair cone / total semantic state
```

Interpretation:

- small/local `delta` favors realizations that exploit sparse factorization and local update/revision;
- dense/global `delta` reduces the benefit of explicit locality.

Parents: graphical models, factored MDPs, sparse dependency systems, TMS/incremental computation.

---

## 2.3 `gamma` — usable credit-information density

Question:

> How informative is feedback about which internal changes improve the registered objective?

Candidate operational measures may include:

```text
number/fraction of internal degrees receiving informative local feedback
mutual information between legal update/proposal choices and outcome signal
availability of differentiable/local gradient information
counterexample localization strength
verifier feedback granularity
```

Interpretation:

- dense/high-quality credit may favor highly distributed trainable realizations;
- sparse delayed/binary verification can shift burden toward search, decomposition, explicit constraints or donor solvers.

Important: `gamma` is not “gradient exists yes/no”. It is an obligation/feedback property measured before the protected target outcome.

Parents: optimization, credit assignment, information theory, active learning.

---

## 2.4 `nu` — ecology drift / invalidation rate

Question:

> How quickly do assumptions, task distributions, APIs, evidence or semantics change relative to reuse?

Candidate measures:

```text
hazard of representation/method invalidation
expected version lifetime
regime-switch rate
support withdrawal frequency
```

Interpretation:

High `nu` reduces the effective horizon of expensive amortized structures and increases the value of cheap/local revision.

Parents: nonstationary learning, change detection, cache invalidation, continual learning.

---

## 2.5 `chi` — verifier / admissibility structure

Question:

> How expensive, strong and informative is external verification?

This is a structured object, not one number. Candidate coordinates:

```text
cost per verification call
binary vs graded feedback
proof/counterexample witness availability
false-positive/false-negative bound
coverage of the actual semantic obligation
incremental/local verification availability
```

Examples:

```text
Lean kernel: strong exact formal check for a formal statement
software tests: execution evidence relative to registered test strength
science: graded/statistical evidence, not theorem truth
```

Interpretation:

Morphologies that rely on cheap repeated verification may be poor under expensive sparse verification; exact proof domains may favor different search/representation regimes than noisy empirical ones.

---

## 2.6 `eta` — effective reuse horizon

Question:

> How many useful applications occur before invalidation, drift, reset or retirement?

Define, where measurable,

\[
\eta = E[H_{eff}].
\]

This is not chronological age.

It is expected useful reuse under the registered ecology.

Interpretation:

High `eta` can repay expensive training/index/library construction; low `eta` favors cheap per-task computation.

Parents: amortization, rent-vs-buy, caching/materialized views.

---

## 2.7 `lambda` — retention/plasticity constraint

Question:

> How strongly must old competence be retained while new competence remains learnable?

Candidate measures:

```text
allowed old-task degradation
new-task acquisition rate after accumulated history
interference matrix across task families
relearning burden after update
```

Interpretation:

A realization that is efficient on one stationary task but loses plasticity over a lifetime may be dominated under developmental obligations.

Parents: continual learning, stability-plasticity theory, meta-learning.

---

## 2.8 `pi` — physical/resource price regime

A prospectively declared vector over raw resource coordinates, for example:

```text
compute
latency
memory/storage
communication
energy
verification
human input
```

No universal phase prediction can ignore hardware/resource prices.

The same semantic realization may switch rank when `pi` changes.

---

# 3. Why these coordinates are not yet a theory law

The signature is provisional.

It may fail because:

- important structure is omitted;
- coordinates are not identifiable before outcome;
- morphology rankings depend on high-dimensional details;
- family-native predictors dominate;
- two ecologies with the same measured signature have different realization frontiers;
- the signature merely re-encodes architecture labels indirectly.

Therefore current terminal:

```text
REALIZATION_DEMAND_SIGNATURE_CANDIDATE_ONLY
```

---

# 4. Realization-side response functions

For a morphology `M`, define a response profile

\[
\mathcal R_M(\Xi)
\]

that predicts capability/resource burden under a demand signature.

Examples of morphology-side properties include:

```text
semantic capacity / admissible distortion curve
build/acquisition cost curve
serving cost curve
update/revision locality curve
credit-signal utilization
verification integration cost
storage/communication structure
plasticity/interference curve
parallelism/hardware utilization
```

Do not encode labels such as `NEURAL=1` or `SYMBOLIC=0` into the scientific predictor.

The architecture family is used only after or alongside the response characterization.

---

# 5. Realization Sufficiency Conjecture

Candidate conjecture `GMI-RSC-1`:

> There exists a bounded-dimensional obligation signature `Xi` and morphology response profile `R_M` such that, over a registered family of ecologies and candidate morphologies, the ordering/near-frontier status of realizations can be predicted prospectively to useful accuracy from `Xi` and `R_M` without target-specific architecture labels or protected outcomes.

This is intentionally empirical/conditional.

It is **not** a universal theorem over arbitrary computable systems.

---

# 6. Stronger cross-paradigm version

Candidate `GMI-RSC-2`:

> A nontrivial subset of the same obligation coordinates predicts frontier transitions in at least two materially different morphology families after each family's native strongest predictor receives first refusal.

Examples of materially different families:

```text
program/library search
probabilistic inference
neural/differentiable learning
symbolic/production/search
```

A positive requires the *same coordinate meaning* in every family.

Renaming family-native variables to the same English word does not count.

---

# 7. Falsifiers

## F1 — signature collision

Construct two obligations `Omega_1`, `Omega_2` with matched measured `Xi` but opposite realization ranking.

Terminal:

```text
REALIZATION_SIGNATURE_INSUFFICIENT__COLLISION
```

## F2 — hidden architecture label

A predictor loses power when architecture/family identity or proxy identifiers are removed.

Terminal:

```text
ALGORITHM_SELECTION_ONLY
```

## F3 — family-native parent suffices

Each family-native parent predicts its own frontier, while the shared signature contributes no out-of-family value.

Terminal:

```text
FAMILY_NATIVE_REALIZATION_THEORIES_SUFFICIENT
```

## F4 — post-outcome measurement

A signature coordinate cannot be measured without using protected target outcomes.

Terminal:

```text
SIGNATURE_NOT_PRE_OUTCOME_IDENTIFIABLE
```

## F5 — resource accounting reversal

A claimed phase law disappears after full build/search/maintenance/verification cost is charged.

Terminal:

```text
INCOMPLETE_COST_CREATED_PHASE
```

## F6 — semantic mismatch

One candidate appears cheaper only because it solves a weaker obligation/verifier.

Terminal:

```text
SEMANTIC_OBLIGATION_MISMATCH
```

---

# 8. Minimal empirical programme

## DS-E0 — exact finite calibration

Use bounded systems where:

- semantic quotient is exact;
- dependency locality is exact;
- verifier cost is exact;
- reuse horizon is controlled;
- realization frontier can be exhaustively enumerated.

Purpose: validate measurement, not claim machine intelligence.

## DS-E1 — within-family prospective prediction

For each family separately, test whether pre-outcome `Xi` adds value beyond trivial baselines.

Strong family-native parent gets first refusal.

## DS-E2 — cross-family transfer

Train/fix the mapping on family A and test the same coordinate meaning on family B, or fit jointly with family-held-out validation.

No architecture identity input.

## DS-E3 — surface remint / ecology collision hostiles

Keep `Xi` approximately fixed while radically changing surface representation and task names.

Then deliberately create near-collision cases differing in a withheld structural property to discover missing coordinates.

## DS-E4 — real math/code comparison

Only after E3 domain measurements exist:

- Lean formal proof ecology;
- execution-verified coding ecology.

Do not scalarize theorem success and code success together.

Ask whether the same demand coordinates explain any part of the observed realization economics.

---

# 9. Relationship to neural networks

This signature gives a cleaner answer to the original question “why can neural networks dominate?”

The theory should not say:

```text
neural networks are fundamentally superior
```

It should attempt conditional statements such as:

```text
high semantic/statistical compressibility
+ high usable credit-information density
+ long reuse horizon
+ accelerator-favorable pi
+ tolerable drift/retraining/plasticity cost
-> distributed differentiable realizations move toward the frontier
```

while other regimes may move the frontier toward explicit/factored/programmatic/hybrid realizations.

Whether this prediction survives data is open.

---

# 10. Relationship to unknown morphology discovery

An unknown-form search is not justified merely because the current best morphology is imperfect.

A theory-predicted **frontier hole** requires:

```text
1. Xi predicts demanded realization properties;
2. registered known/parent morphologies cannot jointly occupy that region;
3. lower-bound/headroom analysis says the region is not impossible;
4. required properties are frozen before search;
5. neutral search is run without target morphology labels;
6. candidate is reduced against all known parent families after discovery.
```

Only then does Track B have a principled reason to search for `M_?`.

---

# 11. Relationship to RSI/meta-morphogenesis

If a developmental system learns better estimates of `Xi`, better response models `R_M`, or a better `Gamma_g` for locating frontier realizations, then meta-development can be measured as reduced burden/regret on fresh ecology families.

This gives a concrete K3 question:

\[
B^{discover}_{g+1}(\text{useful frontier realization})
<
B^{discover}_{g}(\text{useful frontier realization})
\]

under fixed external evaluation/governance.

Again, learned optimizer/AutoML/meta-search parents receive first refusal.

---

# 12. Current decision

Do not call `Xi` a fundamental law.

Use it as a falsifiable compression hypothesis over obligation structure.

Allowed next terminals:

```text
REALIZATION_DEMAND_SIGNATURE_SUPPORTED_AT_FINITE_SCOPE
CROSS_PARADIGM_REALIZATION_SIGNATURE_SUPPORTED_AT_SCOPE
REALIZATION_SIGNATURE_INSUFFICIENT__<reason>
ALGORITHM_SELECTION_ONLY
FAMILY_NATIVE_REALIZATION_THEORIES_SUFFICIENT
SIGNATURE_NOT_PRE_OUTCOME_IDENTIFIABLE
CANNOT_CHECK_<reason>
```
