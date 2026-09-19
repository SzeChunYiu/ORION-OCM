# CORE — `gmi-833-mtg-enriched-geometry-v1` (issue #833, programme comment 5687604615)

**Rows.** Two MTG-4 rows (indices 23, 24 of `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json`): metric/topology
stability under relabeling controls and resource-coordinate perturbations; quantale/ordered-monoid enrichment keeping the
primary geometry resource-vector valued.

**Claim ceiling.** `GMI_833_MTG_ORDERED_MONOID_ENRICHMENT_AND_TOPOLOGY_STABILITY_AT_REGISTERED_FINITE_SCOPE`

| result | statement | numbers |
|---|---|---|
| ENR-1 | Pareto antichain algebra is a finite ordered monoid; closure obeys the lax enrichment law `H(M,N)⊛H(N,P) ⊑ H(M,P)`, `I ⊑ H(M,M)` | preorder 20/400/8,000; monotone 7,000; join 800 + 8,000; enrichment 125/125 triples, 5/5 nodes; terminal `FINITE_ORDERED_MONOID_ENRICHMENT_VERIFIED`, completeness not claimed |
| STAB-1 | closure and topology transport-equal under every node relabeling | 120/120 and 120/120; null (misaligned transport) 0/200 closure, 1/200 topology; automorphisms 1 |
| STAB-2a | positive rescaling commutes with closure; same topology when budgets rescale alike; fixed grid changes it | 75/75; 3/3; 2 of 3 rescalings differ (18 → 24 open sets) |
| STAB-2b | membership sandwiched by the `±e` extreme closures; frozen non-membership rule refuted by counterexample, replaced by the box criterion | 113,600 sandwich checks; 1,544/1,600 box-stable; 0 flips / 109,127; counterexample budget `(155/16,1)` |
| STAB-2c | `|d_w − d_w'| ≤ max_v |(w−w')·v|`; `+∞` preserved | 51/51 finite; 24/24 infinite |

**What was corrected.** The frozen STAB-2(b) non-membership criterion (every frontier vector exceeds the budget by
more than `L·e`) is unsound: a dominated longer path can gain more than the frontier's own `L·e`. Exact 4-node
counterexample recorded on both routes; attribution to that one stage; lever = box criterion (compare with all
edges `+e` and all edges `−e`), proved sound and re-tested on every registered pattern. The freeze is not edited;
`MANIFEST_V1.json` discloses `s6_instruction_followed: false` for that clause.

**Two routes.** `enriched_geometry_v1.py` (Floyd–Warshall closure, basis generation) and
`independent_oracle_v1.py` (simple-path enumeration, explicit union closure; imports nothing from route A).
81 shared quantities agree. 8 hostiles, each applicable and detected. Null 200 draws, true law excluded.

**Reproduce (laptop or CI, never the Mac mini).**

```
python3 -I -B  research/gmi-833-mtg-enriched-geometry-v1/enriched_geometry_v1.py
python3 -I -B  research/gmi-833-mtg-enriched-geometry-v1/independent_oracle_v1.py
python3 -I -B  research/gmi-833-mtg-enriched-geometry-v1/test_enriched_geometry_v1.py
python3 -I -O -B research/gmi-833-mtg-enriched-geometry-v1/test_enriched_geometry_v1.py
```

Receipts are byte-identical between the two modes (`RESULT_V1.json` md5 `198ddf2f25e935c48b292d8c3c56f453`,
`ORACLE_RESULT_V1.json` md5 `086f05e5e2a3f1ec235f0ec1912523bd`, Python 3.8 on billy-laptop).

**Not claimed.** Complete quantale enrichment, any infinite graph, stability under arbitrary perturbation,
Hausdorff or manifold structure, universal price vectors, complete GMI.
