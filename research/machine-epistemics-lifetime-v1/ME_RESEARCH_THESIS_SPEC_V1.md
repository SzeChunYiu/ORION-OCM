# Machine Epistemics lifelong-scaling measurement specification V1

Status: **prospective measurement contract for ORION-OCM #50**. It carries no protected-result authority.

The scientific target is not "OCM is cheaper than an LLM." It is whether a persistent machine with explicit evidence, warrant, dependency and executable competence has a *joint* empirical signature across acquisition, use, revision and reuse that survives strongest faithful parents.

## Four-perspective review

| Perspective | V1 disposition |
|---|---|
| Machine Epistemics theorist | H1–H4 are formalizable, but their mechanisms have strong parents. Novelty cannot rest on skill reuse, indexed retrieval, or truth maintenance alone. The candidate scientific object is their governed lifelong coupling. |
| Systems researcher | Existing KSO state exposes logical object/relation/warrant counts and shallow index resources. The new receipt makes hidden index/global work visible. Production paths still need touch instrumentation before H2 is measurable. |
| Learning researcher | Acquisition is a threshold-crossing vector, not endpoint accuracy. A reuse event requires an actual pre-existing operator execution/composition witness; similarity retrieval alone does not count. |
| Skeptical reviewer | Synthetic calibration can validate counters but cannot validate the thesis. Historical M12 V4 is calibration-only because #38 reopened the lifetime inference. Fresh matched lifetimes are required after N3/N5. |

## D1 canonical definitions

### Total persistent state `N`

For one arm and one declared object grammar at time `t`,

`N_t = sum_c count(persistent identity-bearing objects of class c)`.

For the current KSO grammar, candidate classes include atoms, hyperedges and warrant/dependency entries. Methods, evidence objects, dialogue objects, caches and learned indexes must be counted if they persist and can affect future behavior.

Rules:

1. Report the class vector and bytes, not only `N`.
2. `N` is a within-grammar scaling coordinate. **Do not compare one KSO atom with one neural parameter.** Cross-architecture comparisons use resource/storage/information vectors.
3. Task-specific ephemeral intermediates do not enter `N`, but their compute/memory cost enters the resource vector.
4. Persistent caches and indexes cannot be hidden as implementation detail; storage and maintenance are separate coordinates.
5. If a persistent class can affect behavior but cannot be enumerated or sized, `N` for that run is `CANNOT_CHECK`.

Current implementation bridge: `KnowledgeSpace.resource_counts()` supplies atom/relation/warrant logical counts and `KnowledgeSpace.index_resources()` exposes currently materialized shallow structural-index entries/bytes. The latter is **not** a deep process-memory measure.

### Relevant active state `k`

For a scoped operation `o`,

`k(o) = | union of identity-bearing persistent objects actually semantically touched during o |`.

A touch includes a persistent-object read, liveness/warrant check, dependency traversal, operator execution, modification, or validation. Repeated touches count once in `k`; repeated work remains in resource counters.

`k` explicitly does **not** mean:

- returned retrieval top-k;
- number of non-zero activations;
- number of sparse edges/incidences;
- number of objects in the final explanation;
- an estimated "relevant set" not instrumented at runtime.

Index entries inspected are reported separately. Any uninstrumented global scan makes H2 `CANNOT_CHECK` for that path.

**Current-kernel audit finding.** `src/ocm/kso/navigation_sparse.py` stores sparse incoming incidences, but `sparse_fixed_point_certified` still constructs/updates a value for every seed row on every iteration. Therefore the present kernel must not claim query cost is `O(k)` merely from its incidence counter. Issue #50 instrumentation should count the state-wide row work; a future truly local/frontier kernel is an experimental mechanism, not an assumption.

### Acquisition cost

For task `T` under a frozen competence threshold `theta`, acquisition cost is the pair

`C_acquire(T) = (I_until_theta, R_until_theta)`

where `I` is the information vector (words/tokens/examples/demos/labels/lessons/interactions/grounded observations/source assertions/annotations) and `R` is the resource vector. It is measured at the **first** point the frozen threshold is met.

If no common threshold can be defined, the arm never reaches it, or information channels are not parity-auditable, the corresponding comparison is `CANNOT_CHECK`; do not substitute endpoint accuracy.

### Query/use cost

Resource delta from query start to the committed/checkable outcome, including:

- state/index reads;
- navigation/routing/planning work;
- model inference;
- verifier/tool/external IO calls;
- triggered cache/index maintenance;
- memory/temporary allocation where measurable.

Offline index/preprocessing costs are reported separately and included in lifetime totals. They cannot be moved outside the accounting boundary to create a favorable query curve.

### Revision cone

For a registered support event `r`, the **semantic revision cone** is the set of persistent competence objects whose live/usable epistemic status should change under the declared support semantics. Separately report all objects touched to determine that outcome, including an alternate-supported object that is inspected but correctly remains live.

Primary exactness checks on planted worlds:

- dependency precision = 1;
- dependency recall = 1;
- stale survivors = 0;
- collateral invalidations = 0;
- unrelated change = 0;
- restoration/relearning returns exactly the justified set.

A small changed fraction with missed dependents is failure, not locality.

### Reuse event

A reuse event requires all of:

1. operator/method identity existed before the later task;
2. it was actually executed or composed into the later solution/acquisition path;
3. the event has an execution/causal witness identity;
4. scope/preconditions permit the reuse;
5. its information was available to matched parents when parity requires it.

Retrieving a similar memory without using it does not count. For causal claims, include a withheld/replaced reuse ablation where feasible.

### Resource vector

Never reduce the study to one favorable scalar. V1 records at least:

- wall/CPU/GPU time;
- peak memory;
- persistent reads/writes;
- index reads/writes;
- external IO/tool/verifier calls;
- exact implementation-specific work units where defined;
- preprocessing and maintenance work;
- static model parameters;
- persistent/index storage.

Any later dollar/FLOP scalarization must be separately frozen and must preserve the raw vector.

## Hypothesis-specific strongest-parent rule

The causal parent is hypothesis-specific. A single intentionally weak "matched parent" is not sufficient for all claims.

- H1 needs persistent skill/memory + post-deployment adaptation parents.
- H2 needs indexed retrieval/sparse routing parents.
- H3/H4 need truth/reason-maintenance/dependency parents with alternate support.
- H5 needs a composite parent allowed the same memory, retrieval, tools, verifier access and adaptation route.

A mechanism can be `PARENT_SUFFICIENT` while the joint lifelong architecture remains an open question.

## What V1 can and cannot establish

V1 can establish that counters are exact on planted finite worlds and can detect common accounting/revocation mutants. It cannot establish a new AI scaling law. That requires fresh protected task streams, real N1–N5 mechanisms, strongest parents and a frozen confirmatory analysis.
