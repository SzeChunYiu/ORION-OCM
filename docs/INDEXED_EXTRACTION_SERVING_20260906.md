# Measured extraction locality — bounded engineering result

`PARENT_SUFFICIENT`: conventional incident/outgoing indexes and lazy worklists
explain this result. No OCM-specific scientific residual is established.
The terminal `ACTIVE_SUBSPACE_SCALING_SUPPORTED` applies only to the registered
synthetic sparse-support reaction and greedy extraction operations below.

## Mechanic and validity

Preparation retains the existing KnowledgeSpace adjacency indexes. Cold atom,
incident and outgoing construction, plus accounting-row traversal, are recorded
in `ExtractionIndex.build_work`. Warm calls retain no cached liveness: evidence
revocation and UNKNOWN are re-evaluated per query. A different space object or
atoms/hyperedges tuple refuses with `EXTRACTION_INDEX_SNAPSHOT_MISMATCH`.
Metadata/registry values are not indexed or used to authorize extraction.

The warranted closure uses lazy all-tail pending counts and on-demand liveness;
exploratory closure retains any-tail reachability. Greedy objective, approximation,
candidate count and lexical tie ordering match the incumbent. The bounded exact
PCST reference and its global free-atom bound remain unchanged.

## Registered evidence

One relevant three-atom/two-edge component stays fixed while independent copies
grow the field by 1x, 10x, 100x and 1000x. Warm reaction always inspects 3 atom IDs,
2 distinct edges, 4 incident postings and 2 outgoing postings. Warm greedy always
inspects 3 atom IDs, 2 distinct edges and 23 incident postings, evaluates 5 objectives
and considers 2 candidates. Off-active incidence IDs count as touched even when
an internal-edge test rejects that edge; an unrelated object remains uncounted.

A connected-chain control at 3, 30, 300 and 3000 objects inspects every object and
edge. Dense-seed adaptation inspects N seed entries and receives the separate
terminal `SPARSE_STRUCTURE_NOT_SPARSE_EXECUTION`. Neither control claims locality.

The table reports median microseconds over eleven warm calls on billy-laptop.
The incumbent receives the same already prepared field, warrants and prizes;
dense seed construction is separately recorded. Timings are descriptive on a
shared host; deterministic counters support the locality conclusion.

| Objects | Edges | Indexed reaction | Indexed greedy | Incumbent reaction | Incumbent greedy | Cold index prep |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 2 | 24.45 | 112.11 | 14.62 | 91.00 | 13.97 |
| 30 | 20 | 21.13 | 105.15 | 36.78 | 224.18 | 30.48 |
| 300 | 200 | 21.07 | 104.70 | 290.06 | 1557.25 | 151.25 |
| 3000 | 2000 | 20.39 | 103.42 | 2781.26 | 15087.17 | 1952.26 |

The indexed path is slower on the three-object fixture. This is a measured
workload tradeoff, not a universal speedup or a reason to replace the default
oracle. Full runtime cost, acquisition, persistent storage, revision, external
verification and lifetime amortization remain unmeasured.

## Integration boundary

Use `ExtractionIndex(ks)` once and charge its `build_work` once. Pass that index
to `reacting_subgraph_from_support_indexed` with the exact positive seed IDs, or
to `reacting_subgraph_from_surprise_indexed` when retaining the dense adapter.
Pass it to `pcst_greedy_indexed` for the greedy fallback. `with_work=True` returns
`(result, work)`; `work.as_dict()` is serializable. Explicit preparation is not
charged again inside each query; automatic preparation is included in
`work.cold_build_work`. Rebuild after replacing the KnowledgeSpace snapshot.

The sparse-support API does not certify that a truncated surprise/activation map
is sufficient. It reads every reached rho value, preserving missing-value errors.

## Reproduction

20 focused tests pass after the incidence-accounting correction. Coverage includes
24 randomized hypergraphs across both modes and two revocation states, full
reference-result parity, revocation/revival, UNKNOWN, snapshot refusal, dense-shape
errors, disconnected-read hostiles, 1000x growth and global controls. The hostile
also detects the incumbent global liveness scan, proving the alarm works.

Run on a Linux test host with the pinned development environment:

```sh
PYTHONPATH=src python research/ocm-prototype/indexed_extraction_serving_study.py \
  --output /tmp/extraction-study/RESULT.json --repeats 11
```

[Raw measurement record](../research/ocm-prototype/results/indexed-extraction-serving-20260906/RESULT.json)
records executed source commit `8d727ea1d1a72e0c45fe76b97c21ee9b5fc37d72`,
mechanic-source SHA256s, raw wall/CPU samples, cold work and process RSS scope.
Record SHA256: `3e829f2a3b2befe062444a790cb6f23e743569f979ed8cd7adf6c46604e03e98`.
