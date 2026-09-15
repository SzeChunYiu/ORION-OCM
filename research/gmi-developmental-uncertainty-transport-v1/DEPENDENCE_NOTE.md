# Dependence control

The finite probability certificate uses 200 equiprobable atoms. Source failure occupies 10 atoms, relation-1 failure 2 different atoms, and relation-2 failure 1 further atom. The three failure sets are pairwise disjoint, so their union has exact mass `13/200`; the joint-good event has exact mass `187/200` and attains the union-bound lower bound.

The corresponding success events are **not independent**: their product-of-marginals value would be `374319/400000`, which differs from `187/200 = 374000/400000`.

This is the concrete finite hostile for any implementation or prose that tries to justify the developmental uncertainty bound by multiplying success probabilities.
