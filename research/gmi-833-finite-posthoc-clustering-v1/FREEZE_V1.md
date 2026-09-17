# Freeze v1 — finite post-hoc clustering quartet

Frozen before implementation for issue #998, parent checklist #833.

## Source scope

This tranche consumes only the complete finite presentation census from merged
PR #966 and the exact morphology records/metric from merged PR #984, at the
registered `(2,2)` structural budget, three-word protected interface, and step
cap 6. It is disjoint from morphology-zoo issues #220/#221 and neural-family PR
#946. It performs no new candidate search.

## Order and noninterference

1. Enumerate all 576 #966 presentations.
2. Evaluate every presentation into its #984 morphology record.
3. Retain every presentation and its record in the candidate membership ledger.
4. Deduplicate only for the 47-node clustering carrier; never discard candidate
   membership.
5. Cluster without importing, reading, or receiving family labels, exemplars,
   reference fingerprints, or taxonomy code.
6. Select deterministic medoids without family information.
7. Only then load the separately frozen reference registry and map medoid
   protected-evaluation fingerprints post hoc.

## Frozen clusterer

On the 47 distinct #984 morphology records, form an undirected graph with an
edge `{x,y}` exactly when the base metric `d_(5,3,2)(x,y) <= 15/2`. Clusters are
the graph's connected components. Within each component, a medoid minimizes the
sum of base distances to all component members; ties use #984's canonical record
serialization. Cluster identifiers are assigned by sorting the medoid
serialization, then the sorted member serializations. No program source string,
opcode name, or family label participates.

## Frozen post-hoc references

The mapper receives only a completed cluster's medoid protected-observation
table. It compares exact fingerprints against these supplied reference entries:

- `INPUT_GATED_STUTTER`: `BLOCKED_INPUT/[]`, `STEP_LIMIT/[]`,
  `BLOCKED_INPUT/[]`;
- `QUIESCENT_TERMINATOR`: three copies of `HALTED/[]`;
- `ZERO_STREAM_LOOP`: three copies of
  `STEP_LIMIT/[0,0,0,0,0,0]`;
- `ZERO_EMITTING_TERMINATOR`: three copies of `HALTED/[0]`.

Exactly one exact match emits that known reference-family label. Zero matches or
multiple matches emits the explicit machine-distinct label `UNKNOWN`. There is
no nearest-family fallback, forced assignment, or manual override.

These are supplied finite-control reference fingerprints, not learned natural
families and not evidence of literal historical ignorance.

## Frozen stability obligations

- Replay all 120 certified #984 surface remints. They must preserve every
  morphology record, hence candidate-to-cluster membership equivariantly.
- Under #984 perturbed weights `(501/100,299/100,201/100)`, every threshold-edge
  decision must retain a strict certified margin around `15/2`; connected
  components must therefore be identical.
- Medoid stability may be claimed only if every unique base medoid has a
  two-sided aggregate-cost margin exceeding its certified perturbation bound,
  while every base tie is shown to have identical aggregate component vectors
  and therefore remains an exact tie. Otherwise partition stability is reported
  without medoid/label stability.
- A semantics-changing pseudo-remint and a deliberately boundary-crossing
  distance perturbation must be detected as hostiles, not certified stable.

## Claim ceiling

`FINITE_POSTHOC_CLUSTERING_BLIND_REFERENCE_MAPPING_UNKNOWN_AND_STABILITY_AT_REGISTERED_966_984_SCOPE`

## Forbidden promotions

- large-scale clustering validity;
- a universal, natural, unique, or unbiased morphology taxonomy;
- known-family derivation/recovery beyond the four supplied exact fingerprints;
- literal historical ignorance or architecture-prior-free discovery;
- cluster truth, uniqueness, or robustness to arbitrary thresholds/metrics;
- arbitrary grammar-remint robustness;
- #220/#221 morphology-zoo completion or #946 neural-family closure;
- a new form of intelligence, complete GMI, or ontological completeness.

Negative results and unmatched clusters remain visible as `UNKNOWN`; the frozen
protocol is not retuned around them.
