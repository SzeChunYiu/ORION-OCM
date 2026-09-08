# Indexed weighted deduction — source-first donor decision

Source inspection dated 8 September 2026. No package was installed and no donor,
OCM, native checker, solver or protected study was executed during this review.

**Decision:** implement a small faithful Knuth/Nederhof scheduler over the existing
finite action arrays. Retain the old scheduler as oracle. This adopts a conventional
algorithm; it is not a new algorithm or an OCM novelty result.

## Primary mechanism

[Nederhof 2003, §§3–4](https://aclanthology.org/J03-1006.pdf) separates deduction rules
from minimum-derivation scheduling, recommends priority queues/antecedent indexes,
and permits weight functions monotone in each argument and no smaller than any
argument. The current nonnegative `1 + sum(ordered premise costs)` satisfies this.

[Eisner 2023, §§2.5,7](https://aclanthology.org/2023.tacl-1.54.pdf) discusses efficient
incidence access, duplicate antecedents and cyclic systems. Its acyclic two-pass
result is not directly applicable to the present cyclic bank. No SCC pass is needed
to justify the narrower positive-cost Knuth scheduler proposed here.

## Inspected implementations

| Candidate and exact source | Useful mechanism | Why not import directly |
|---|---|---|
| [HALP `directed_paths.py`](https://github.com/Murali-group/halp/blob/4da616230db70a173b1235a69742fa45b1e65db4/halp/algorithms/directed_paths.py), lines319–417 | `_shortest_x_tree`: forward-star incidence, readiness counters, weighted heap and predecessor edge. Its additive sum path is a close algorithmic donor. | The graph adapter changes required semantics; see below. |
| [dyna-pi ground `solver.py`](https://github.com/timvieira/dyna-pi/blob/50333f9666d3354883d370dd62717c212331cfca/dyna/execute/solver.py), lines43–109 | Driver indexes retain body positions; ground agenda propagation handles repeated occurrences explicitly. | This is delta/fixpoint evaluation. Default priority follows insertion order; a weight-finalizing Knuth policy and current proof provenance would need adaptation. |
| [hypergraphs `hypergraph.py`](https://github.com/timvieira/hypergraphs/blob/96c5a3fca6ffc3d5c34e59407bfcfaeb3d2eea9a/hypergraphs/hypergraph.py), lines18–23,37–50,91–100 | Ordered body tuples preserve repeated tails and empty bodies. | `inside()` makes one DFS-derived topological pass. It is not a cyclic minimum-deduction scheduler. |

HALP's [graph storage](https://github.com/Murali-group/halp/blob/4da616230db70a173b1235a69742fa45b1e65db4/halp/directed_hypergraph.py#L503-L548)
keys edges by frozen tail/head sets and updates an existing edge for identical sets.
That loses parallel action identity. It retains the original tail object, while its
forward-star contains each edge once per distinct node: passing a repeated-tail list
can leave its readiness counter below the stored tail length. Empty-tail edges are
not seeded by `_shortest_x_tree`, whose initial queue contains only the source node.
These are API/model mismatches for ordered proof ports and parallel provenance,
not library defects under HALP's set-hypergraph contract.

## Availability, licenses and dependencies

- HALP commit `4da616230db70a173b1235a69742fa45b1e65db4`, 26 January 2021; repository
  not archived. [License](https://github.com/Murali-group/halp/blob/4da616230db70a173b1235a69742fa45b1e65db4/LICENSE): GPLv3.
  [PyPI](https://pypi.org/project/halp/) reports 1.0.0, uploaded 22 October 2014.
  Its requirements file pins older NumPy/SciPy/NetworkX and test tools; the inspected
  shortest-tree module imports its graph/queue helpers and standard-library `queue`;
  the priority-queue helper uses `heapq`. Importing the whole environment is unnecessary.
- dyna-pi commit `50333f9666d3354883d370dd62717c212331cfca`, 26 June 2026; not archived;
  [MIT](https://github.com/timvieira/dyna-pi/blob/50333f9666d3354883d370dd62717c212331cfca/LICENSE).
  [Manifest](https://github.com/timvieira/dyna-pi/blob/50333f9666d3354883d370dd62717c212331cfca/pyproject.toml)
  declares Python>=3.8 and 13 dependencies including Git-sourced arsenal/semirings,
  parser, symbolic solver and notebook/UI packages. [PyPI package `dyna`](https://pypi.org/project/dyna/)
  exists at0.9; its dependency metadata differs. The GitHub commit, not an assumed
  PyPI/source equivalence, is the inspected implementation.
- hypergraphs commit `96c5a3fca6ffc3d5c34e59407bfcfaeb3d2eea9a`, 24 April 2026;
  not archived. GitHub license metadata is null; no license file/declaration found
  in its returned tree and inspected setup. Its manifest requires arsenal, NLTK,
  NumPy, pandas and Git-sourced semirings. Runtime suitability was not tested.

## Required faithful adaptation

1. Keep every existing grounded action and its ID; do not merge parallel rules with
   equal head/tail. The bank, type/DV validity, permitted methods and compiler stay fixed.
2. Retain ordered tail occurrences for additive tree cost and proof ports. For
   readiness, index each distinct tail once and count distinct unfinalized tails;
   alternatively use occurrence counts consistently. Never silently deduplicate cost.
3. Supplied facts start at0; zero-premise rules enter at1. Finalize each fact only
   when popped with its best current key. Ignore stale heap entries explicitly.
4. Use original action-order rank for equal-cost predecessors, not arrival order.
   Here every parent is strictly cheaper than its head; all equal-cost candidates
   are therefore available before head finalization. This preserves the reference tie.
5. Preserve positive cycles: unseeded cycles remain unreachable; a seeded cycle
   cannot improve its own predecessor cost. These assertions rely on the fixed cost1.
6. Stop at8 only under that positive-cost contract; report bounded incompleteness.
   Reconstruct through original action/ordered-parent records and native-check output.
7. Count cold index construction, all stored incidences, heap activity, ready-rule
   evaluations, reached facts, output work and unchanged cold grounding separately.
   An indexed scheduler does not remove full grounding or establish active locality.

The optimized objective is minimum abstract rule-tree decisions, including repeated
subtrees. It is not minimum shared-DAG size, expanded native proof size or lifetime
cost. These distinctions and the exact native verifier remain authoritative.

Raw repository metadata, fixed-commit source files and PyPI metadata are retained
beside this memo; FETCHED-SOURCES.json records source URLs and byte hashes.
