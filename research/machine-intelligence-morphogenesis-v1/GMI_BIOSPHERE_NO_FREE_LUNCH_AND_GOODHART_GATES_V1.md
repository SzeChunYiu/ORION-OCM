# GMI Biosphere No-Free-Lunch and Goodhart Gates v1

Status: **NO-GO / EXPERIMENTAL VALIDITY HARDENING**

Status date: 2026-09-12.

Refs:

- `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`
- `GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1.md`
- `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md`
- `GMI_PREDICTIVE_SUFFICIENCY_NO_GO_V1.md`

Purpose:

> Prevent open-ended morphology search from being misinterpreted as a universal optimizer and prevent benchmark/reward optimization from being mistaken for semantic intelligence progress.

---

# 1. No universal best morphology

Classical no-free-lunch results show that, under sufficiently uniform averaging over problem/objective classes, no optimization algorithm is universally superior.

GMI is compatible with this because its central target is not

\[
M^*=\text{one universally best machine},
\]

but a conditional frontier

\[
\mathcal F
=
\mathcal F(\mathcal O,\Xi,P,\mathcal M_{avail},H_{dev},\rho,\ldots).
\]

Therefore every morphology-superiority claim must name the ecology distribution or registered scope.

Terminal prohibited:

```text
UNIVERSALLY_BEST_MACHINE_INTELLIGENCE_SPECIES
```

without additional assumptions that make the problem distribution nonuniform/structured.

---

# 2. No universal best biosphere search algorithm

Likewise no search encoding receives universal privilege.

Evolutionary, gradient, Bayesian, novelty, program-synthesis and other search processes exploit different regularities.

Therefore a candidate form is scientifically stronger when independently recovered under multiple search encodings.

If one species appears only under one grammar/search prior, report:

```text
SEARCH_ENCODING_DEPENDENT_CANDIDATE
```

not a universal morphology law.

---

# 3. Ecology distribution is part of the theorem

Let `mu_E` be the registered distribution over ecologies.

Generalist breadth and expected burden are always conditional:

\[
\mathbb E_{e\sim\mu_E}[Y(M,e)].
\]

Changing `mu_E` can change rankings without changing any machine.

Therefore benchmark composition must be frozen and published; post hoc ecology weighting is outcome leakage.

---

# 4. Goodhart failure mode

Suppose the true semantic target is `S` but search optimizes proxy `Z`.

As optimization pressure on `Z` increases, a machine may exploit degrees of freedom where

\[
Z\uparrow
\quad\text{while}\quad
S\not\uparrow
\]

or even

\[
S\downarrow.
\]

In a biosphere this may appear as rapid “evolution” while actually being metric gaming.

Examples include:

```text
benchmark-specific heuristics
verifier exploitation
judge preference hacking
world-ID leakage
memorized protected tasks
unmetered cache/precomputation
syntactic novelty rewarded as intelligence novelty
co-evolved environments that become easy-to-game but semantically meaningless
```

---

# 5. Semantic obligation gate

Primary admissibility must be defined by the external semantic constitution `O`, not by the search reward.

Search reward may guide development, but final protected evaluation asks whether the required semantic traces/interventions are satisfied.

Whenever exact checking is possible, use it.

Whenever only statistical evaluation is possible, use multiple independent measures and hidden/reminted protected cases.

---

# 6. Metric-diversity gate

Do not permit one judge/metric to be both the sole development objective and sole protected evaluator for strong claims.

Use, where applicable:

```text
independent verifier families
continuous + threshold metrics
behavioral counterexamples
adversarially generated tests
human/external ground truth sampled independently
formal/unit-test checks
causal interventions
resource meters outside model control
```

Agreement of imperfect metrics is stronger than optimization of one.

---

# 7. Hidden-semantic remint gate

Protected worlds should remint nuisance features:

```text
names/IDs
surface vocabulary
ordering conventions
file names
symbol names
irrelevant formatting
random seeds
implementation language
```

while preserving the target semantic structure.

A candidate whose advantage disappears under pure remint is likely exploiting surface identity rather than the claimed mechanism.

---

# 8. Verifier gaming gate

For machine/verifier pair `(M,V)`, separate:

```text
true obligation success
verifier acceptance
```

Measure false acceptance on hidden adversarial cases.

Where possible use a second verifier `V'` built by an independent method.

If

\[
P(V=accept\mid failure)
\]

rises under optimization, downgrade the claimed gain.

A verifier is a channel with error, not semantic truth by definition.

---

# 9. Coevolutionary environment validity

A machine-environment coevolution arm may generate challenges, but challenge novelty is not automatically meaningful.

Each generated ecology must pass:

```text
well-formed semantic contract
nontriviality
solvability/feasibility or declared unknown feasibility
no direct machine-ID reward
no hidden access to protected outcomes
novelty beyond surface remint
bounded evaluator complexity
```

Development coevolution does not replace fresh protected ecologies generated outside the coevolution loop.

---

# 10. Quality-diversity descriptor bias

MAP-Elites-like archives depend on chosen behavior descriptors.

Therefore run descriptor robustness:

```text
multiple hand-designed descriptor sets
mechanism-witness descriptor set
random projection / learned descriptor checks
archive-free novelty baseline
```

A “new niche” that exists only because one arbitrary binning scheme created it is weak evidence.

---

# 11. Parent-library incompleteness

Failure to reduce a candidate to the current parent library is not proof of novelty if important parents were omitted.

Before N3 novelty:

1. run literature search for closest known algorithms;
2. invite/construct adversarial parent reductions;
3. expand `P_known` where a plausible parent exists;
4. rerun the reduction tournament.

Novelty is always relative to the registered parent set plus explicit literature search date.

---

# 12. Benchmark contamination gate

For real-world tasks, record whether candidate development may have seen identical or near-identical data through pretraining/retrieval.

Use synthetic remints, time-sliced tasks, private/generated protected cases, or provenance-aware contamination checks where feasible.

Performance with unknown contamination status is not equivalent to clean generalization evidence.

---

# 13. Search-budget equality is not always enough

Equal FLOPs alone can still be unfair when systems consume different resources.

Match or report vectors including:

```text
compute
memory
communication
labels
human feedback
external calls
time/latency
verification
search candidates
pretrained capital
```

Pretrained foundation models carry developmental capital that must be represented, even when amortized over many downstream tasks.

---

# 14. Anti-monoculture gate

If the search ecosystem collapses to one architecture family early, unknown-form discovery becomes prior-limited.

Maintain independent islands / diversity quotas and audit rejected candidates as specified in `GMI_BIOSPHERE_SCALING_AND_TRIAGE_V1.md`.

But diversity pressure is a search tool, not evidence of intelligence value.

---

# 15. No-free-lunch compatible success claim

The strongest legitimate claim is ecology-conditioned:

> given a registered nonuniform ecology/resource distribution, bounded architecture-neutral descriptors predict which mechanism complexes are frontier-useful, and independent search encodings recover those complexes more often in their predicted niches than in negative twins.

This is exactly the kind of structured regularity no-free-lunch theorems leave available.

---

# 16. Kill terminals

```text
BIOSPHERE_PROXY_REWARD_DIVERGES_FROM_SEMANTIC_OBLIGATION
VERIFIER_GAMING_DRIVES_APPARENT_GAIN
NOVELTY_DEPENDS_ON_DESCRIPTOR_BINNING
CANDIDATE_ADVANTAGE_DISAPPEARS_UNDER_SEMANTIC_REMINT
PARENT_LIBRARY_OMISSION_EXPLAINS_NOVELTY
COEVOLUTION_GENERATES_INVALID_OR_TRIVIAL_ECOLOGIES
UNIVERSAL_MORPHOLOGY_CLAIM_WITHOUT_ECOLOGY_ASSUMPTIONS
UNIVERSAL_SEARCH_CLAIM_WITHOUT_PROBLEM_DISTRIBUTION_ASSUMPTIONS
```

These narrow the programme rather than being explained away.
