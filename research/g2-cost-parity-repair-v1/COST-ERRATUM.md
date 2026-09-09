# G2-COST-WORDING-01: bounded index ranks and physical work

This is an additive correction to frozen prose; no old README, accounting code,
source manifest, receipt or aggregate result is rewritten. The source snapshot is
[main7926c3](https://github.com/SzeChunYiu/ORION-OCM/tree/7926c3cc89c383ac4eb02effffc1824db556a6c0),
with exact blob identities in [BASE](BASE.json).

G2 README98 claims that overlong prefixes are pruned before their descendants
are generated. Actual [build_search_index142–184](https://github.com/SzeChunYiu/ORION-OCM/blob/7926c3cc89c383ac4eb02effffc1824db556a6c0/research/g2-macro-operator-v1/experiment.py#L142)
iterates complete token words from itertools.product for each bounded token depth,
expands each word, and then skips words exceeding the primitive-length bound.
It does not perform prefix pruning or avoid generating such descendants.

Use this corrected description:

> Complete token words are generated in token-depth order and expanded. Overlong
> expanded words are then excluded from the admissible enumeration counter.
> Duplicate admissible tokenizations still increment that counter; each distinct
> expanded program receives one normal-form check.

The full bounded index is built before task lookup. Its saved per-task counters
are first-hit positions during index construction, not measured repeated online
searches or serving latency. Generating/expanding rejected words costs actual
work outside the admissible rank counter. Building the whole index also costs
work beyond any particular task's first-hit rank. Consequently G2 README100–102
must not be read as full physical cost accounting.

G3 independently uses the same complete-word expansion/filter structure in
[build_library_index148–179](https://github.com/SzeChunYiu/ORION-OCM/blob/7926c3cc89c383ac4eb02effffc1824db556a6c0/research/g3-independent-composition-v1/experiment.py#L148);
its README166–168 inherits the same accounting language. The same distinction
applies to its saved first-hit ranks and full-index construction.

Existing rank coordinates and recorded equality remain as measured under their
original definitions. A reduction in their sums is not a serving-time speedup.
Whole-study wall time includes construction/filtering, but a registered rank sum
is not complete acquisition, storage, maintenance, verification or lifetime cost.
No index, population, held-out row or aggregate output was recomputed here.
