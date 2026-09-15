# Known morphology phase-prior atlas v1

Status: **parent-derived hypothesis atlas, not an empirical Track-B phase law.**

Purpose: prevent “new morphology” claims that merely rediscover known machine-intelligence organizations under different names, and identify ecology/resource variables that a future prospective phase law must explain.

## 1. Dense differentiable neural morphology

### Characteristic organization

```text
distributed numeric parameters
composed affine/nonlinear transformations
gradient / optimizer based credit assignment (often)
large offline training -> cheap repeated inference
```

### Parent-owned strengths

- end-to-end differentiable credit assignment;
- shared/distributed representations;
- empirical scaling with data/model/compute in many regimes;
- heavy hardware/software co-design around dense tensor operations;
- meta-learning / learned optimizers / continual-learning extensions.

### Candidate ecology pressures favoring this region

```text
large data volume
smooth/statistical regularity
many repeated inference uses after training
highly optimized matrix hardware
moderate tolerance for distributed/implicit knowledge
```

### Pressure against

```text
frequent exact local revocation
extreme distribution shift / plasticity loss
very small data when strong structure is available
formal exactness / proof obligations when external verification dominates
training cost not repaid by reuse horizon
```

These are hypotheses/known tradeoffs, not universal anti-neural claims.

---

## 2. Reservoir / fixed-dynamics morphology

### Characteristic organization

```text
rich recurrent/nonlinear dynamical reservoir
reservoir largely fixed
train a simpler readout layer
```

Reservoir computing reviews emphasize temporal/sequential processing, high-dimensional dynamical embedding, and comparatively cheap training because only the readout is adapted.

### Candidate ecology pressures favoring

```text
temporal signals
useful physical dynamics already available
training/update budget small
hardware reservoir cheap / naturally embodied
fast readout adaptation important
```

### Pressure against

```text
required representation not present in fixed reservoir
large task-specific structural adaptation needed
readout insufficient for target computation
```

### Parent anchors

- Lukoševičius & Jaeger, reservoir-computing training survey;
- Tanaka et al., physical reservoir computing review.

This family is a strong counterexample to any claim that intelligent learning must adapt every internal component.

---

## 3. Hyperdimensional / Vector-Symbolic morphology

### Characteristic organization

```text
high-dimensional distributed representations
binding / bundling / permutation-like algebraic operations
structured symbolic content represented in distributed vectors
```

HDC/VSA surveys explicitly position the family as combining advantages of structured symbolic and distributed vector representations.

### Candidate ecology pressures favoring

```text
robust distributed representation
simple algebraic composition
fast approximate similarity/retrieval
hardware where high-dimensional simple operations are cheap
```

### Pressure against

```text
collision/interference at insufficient dimension
exact identity/warrant requirements without an external canonical layer
complex tasks requiring expensive clean-up/search
```

### Parent anchors

- Kleyko et al., ACM Computing Surveys HDC/VSA Part I and II;
- Kleyko et al., Proceedings of the IEEE VSA/emerging-hardware review.

Any future “vector-symbolic hybrid intelligence form” must subtract this mature family.

---

## 4. Spiking / neuromorphic morphology

### Characteristic organization

```text
event-driven spikes
sparse temporal communication
hardware co-locating computation/state in neuromorphic structures
```

### Candidate ecology pressures favoring

```text
energy/latency constraints
sparse asynchronous event streams
real-time temporal processing
hardware that rewards spike/event locality
```

### Pressure against

```text
training/tooling maturity relative to dense neural stacks
workloads with poor event sparsity
conversion overhead from dense models
```

### Parent anchors

- Roy, Jaiswal & Panda, Nature 2019 perspective on spike-based machine intelligence;
- Nature Machine Intelligence work on fast/energy-efficient neuromorphic deep learning and spike-based recurrent memory.

Hardware/resource regime is therefore a first-class morphology variable, not an implementation afterthought.

---

## 5. Local-rule / cellular developmental morphology

### Characteristic organization

```text
shared local transition rule
spatially distributed state
emergent global organization through repeated local updates
growth / regeneration possible
```

Growing Neural Cellular Automata are a direct parent example where learned local rules generate and regenerate global structure.

### Candidate ecology pressures favoring

```text
strong locality
repeated spatial motifs
self-repair / growth
parallel local hardware
```

### Pressure against

```text
global coordination not compressible into local interactions
long credit-assignment chains
search/training difficulty for local rules
```

This family directly threatens any OCM claim that “local adaptive units generating complex structure” is novel by itself.

---

## 6. Symbolic production / cognitive-architecture morphology

### Characteristic organization

```text
explicit discrete working state
condition-action productions/operators
agenda / preference / operator selection
explicit procedural learning/chunking in mature systems
```

Soar explicitly hypothesizes deliberate goal-oriented behavior as operator selection/application over state and uses working, production and preference memory plus learning.

### Candidate ecology pressures favoring

```text
sparse explicit rules
exact compositional manipulation
transparent state distinctions
local rule revision / explanation
strong prior symbolic structure
```

### Pressure against

```text
large noisy perceptual/statistical domains
rule acquisition/search explosion
brittle representation choices
```

### Parent anchor

- Soar architecture manual and procedural-learning literature.

---

## 7. Probabilistic / generative-program morphology

### Characteristic organization

```text
explicit stochastic generative model
uncertainty represented in distributions/latent variables
conditioning/inference as core operation
```

Church is a direct universal probabilistic-programming parent: stochastic generative processes expressed in a Lisp-like language with generic exact/approximate query mechanisms.

### Candidate ecology pressures favoring

```text
partial observability
small/noisy data where uncertainty matters
costly experiments / need explicit belief state
strong generative causal structure
```

### Pressure against

```text
inference/sampling cost
poorly specified priors/models
high-dimensional posterior complexity
```

### Parent anchor

- Goodman et al., Church: a language for generative models.

---

## 8. Programmatic / synthesis / library morphology

### Characteristic organization

```text
explicit executable programs
search/synthesis over program space
reusable abstractions/libraries/macros
exact external verifiers where available
```

### Candidate ecology pressures favoring

```text
algorithmic/compositional regularity
strong exact checker
high reuse of discovered subprograms
small concise programs relative to raw data
```

### Pressure against

```text
combinatorial search
weak/noisy feedback
large perceptual/statistical front ends
library acquisition cost exceeding future reuse
```

### Parent families

```text
DreamCoder
Stitch
CEGIS/program synthesis
OOPS/PowerPlay
FunSearch/AlphaEvolve-style evaluator-guided evolution
```

---

## 9. Explicit epistemic / OCM-like morphology

### Characteristic organization

```text
persistent explicit knowledge/method objects
provenance / warrant / scope / dependency
external verification/authority
local revision/revocation
explicit developmental search/control state
```

### Candidate ecology pressures favoring — unproven programme hypotheses

```text
frequent evidence/source revision
strong exact verifier availability
long reuse horizons for verified methods
need for explicit provenance/authority
heterogeneous tools/donors
local correction economically important
```

### Pressure against

```text
acquisition/index/verification overhead
very high-dimensional noisy perception
weak reusable structure
short lifetime/reuse horizon
maintenance dominates savings
```

Track A/#323 evidence supplies bounded developmental examples; this morphology does not get privileged status in Track B.

---

## 10. Hybrid morphology

Hybrid systems combine multiple non-equivalent developmental geometries behind interfaces, e.g.:

```text
neural perception + programmatic exact reasoning
LLM proposal + external theorem prover
vector similarity + explicit canonical state
probabilistic belief + symbolic planner
OCM explicit state + neural donor modules
```

Because mature systems already do this, `hybrid` itself is not novelty.

The interesting question is whether a particular coupling creates a new developmental/resource region not reproduced by the strongest parent product.

---

# Cross-cutting ecology coordinates suggested by parents

A future morphology phase law should at minimum consider:

```text
data volume
noise / stochasticity
smoothness of feedback / credit assignment
algorithmic/compositional regularity
temporal dependence
partial observability
verification strength + cost
reuse horizon
revision/drift frequency
plasticity requirement
communication/locality constraints
energy/latency/hardware prices
parallelism
memory/storage prices
search/acquisition budget
```

These are candidate explanatory coordinates, not a proven sufficient statistic.

# Scientific use

The atlas is a **prior/falsifier source**.

A future new-form claim must ask:

1. Is the candidate actually one of these known families under developmental equivalence?
2. Is its apparent advantage just the known ecology/resource region of that family?
3. Does a strongest hybrid parent already occupy the region?
4. Did Track-B theory predict the region/candidate properties before search?

Current terminal:

```text
KNOWN_MORPHOLOGY_PHASE_PRIOR_ATLAS_REGISTERED_V1
NO_PHASE_LAW_INFERRED_FROM_ATLAS_ALONE
```