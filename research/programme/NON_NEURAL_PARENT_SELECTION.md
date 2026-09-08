# Non-neural premise selection: corrected parent eligibility

[Programme](CORE.md) · [execution contract](NO_NEURAL_CONTRACT.md).

Source review, 9 September 2026. This corrects a literature classification,
not an experimental result or a qualification of an installed prover.

## Decision

Explicit nearest-neighbour and statistical learning are eligible mechanisms when
their features, stored examples, updates and scoring require no neural network.
The existing contract already permits numeric statistics and symbolic policies.
A learned selector is not excluded merely because it learns or uses vectors.
Neural feature extraction, neural embeddings and neural teaching remain excluded.

The historical [lemma-reuse review](../g2-lemma-reuse-literature-v1/CORE.md)
and its [gap table](../g2-lemma-reuse-literature-v1/GAP.md) overexclude k-NN,
HOL(y)Hammer and learned predictors by grouping them with neural extraction.
That exclusion is superseded here. Their frozen files, experiments and outcomes
remain unchanged. This does not qualify every version or dependency of those
systems, nor resolve every other disposition in the historical ledger.

## Primary mechanism and implementation

Gauthier and Kaliszyk's [HOL4 paper, sections 3.3–3.4](https://arxiv.org/html/1509.03534v1#S3.SS3)
uses explicit statement features, nearest neighbours and weighted proof dependencies
for premise ranking. Its feature-to-theorem association list reduces candidate
work. This is a non-neural learned retrieval parent; its scores do not prove a goal.

Kaliszyk and Urban's [lemma-mining paper, section 6](https://arxiv.org/html/1402.3578#S6)
uses k-NN with chronological proof dependencies. Its distinction between full-graph
selection and selection using only earlier proofs remains essential for preventing
future information from influencing a scored task.

The paper's old repository redirects to HOL4. In the official source at
commit `e395eb6e69054ff6f7cef9d1107fd1a04dd5848f`:

- [holyHammer.sml:177–187](https://github.com/HOL-Theorem-Prover/HOL/blob/e395eb6e69054ff6f7cef9d1107fd1a04dd5848f/src/holyhammer/holyHammer.sml#L177)
  invokes theorem-neighbour selection before the ATP call.
- [mlNearestNeighbor.sml:25–75](https://github.com/HOL-Theorem-Prover/HOL/blob/e395eb6e69054ff6f7cef9d1107fd1a04dd5848f/src/AI/machine_learning/mlNearestNeighbor.sml#L25)
  scores feature intersections, ranks candidates and adds known dependencies.
  This version maps over the supplied candidate list; do not attribute the
  paper's indexed locality or a measured OCM speedup to this code by assumption.
- [mlFeature.sml:89–114,140–150](https://github.com/HOL-Theorem-Prover/HOL/blob/e395eb6e69054ff6f7cef9d1107fd1a04dd5848f/src/AI/machine_learning/mlFeature.sml#L89)
  derives and hashes symbolic features and computes frequency-based weights.

The inspected nearest-neighbour file is 5,204 bytes, SHA256
`c5686f634e4179e0f2c3da98576f5f9355341fde6e0fe71edea040e8bf895d46`;
the feature file is 5,586 bytes, SHA256
`817b5da556a1870ff8b8b84297a337ed52f81e70d2bb5e1a5bfc2f7da53e0d25`.
This was a source read, with no imports, execution or code transplantation.
The repository also contains neural modules. A future integration must select
and qualify its actual dependency path; neither filenames nor this review
establish a neural-free whole-repository guarantee.

## Engineering consequence

When method selection becomes the measured bottleneck, compare exact applicability
indexes and SInE with an explicit feature/dependency selector. Reuse the documented
mechanism before inventing a new routing policy. Keep retrieval ranking separate
from current applicability, evidence, scope and final proof checking.

Train and choose settings only from permitted earlier experience. Charge feature
extraction, example/index storage, scoring, maintenance, failed searches and final
verification. Include harmful transfer and a no-use option. Give the conventional
parent the same selector, examples and persistence. A retrieval miss still cannot
establish non-existence; retain refinement or CANNOT_CHECK.

This expands the eligible parent pool without changing the current frozen native
control or launching a selector study. A concrete implementation and measured
benefit are still required before adopting a selector into OCM serving.
