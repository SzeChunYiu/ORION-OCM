# Primary sources and contribution boundary

These notes distinguish inherited mechanisms from the present conditional proofs and executable specification.
They are research notes, not a manuscript or a claim of priority over the cited work.

## Symmetry and representation

[Ravanbakhsh, Schneider and Póczos, 2017](https://proceedings.mlr.press/v70/ravanbakhsh17a.html) directly connects discrete input/output actions to parameter-sharing symmetries.
This is a close mechanism parent for E2 and the compiler. The present support-constrained rational elimination and independent certificates are a scoped realization of that established principle.
[Yeh et al., 2022](https://proceedings.mlr.press/v151/yeh22b.html) studies discovery of interpretable equivariances from data by optimizing parameter-sharing schemes.
Complete-table symmetry extraction in this unit has a different information contract; it is not a new claim to have originated symmetry discovery from data.

[Kondor and Trivedi, 2018](https://proceedings.mlr.press/v80/kondor18a.html) establishes equivariance/convolution relations under explicit compact-group assumptions.
E1–E4 use the elementary finite-permutation affine specialization, proved directly through coefficient equality and orbit indicators.
The mechanism is adopted: symmetry constrains admissible coefficients. No general convolution theorem is claimed as new.

[Cohen and Welling, 2016](https://proceedings.mlr.press/v48/cohenc16.html) develops group-equivariant convolutional networks.
Its group sharing is a parent mechanism; a GMI task must separately warrant a group action and its resource benefit.

[Maron et al., 2019](https://arxiv.org/abs/1812.09902) characterizes invariant/equivariant linear graph layers through bases.
The finite orbit compiler covers explicitly supplied finite actions and support constraints, including partially forbidden orbits.
Its exact-size dimension is calculated rather than importing a stabilized tensor-dimension formula outside its assumptions.

[Zaheer et al., 2017, Deep Sets](https://papers.nips.cc/paper/6931-deep-sets.pdf) is a parent for invariant aggregation.
E4 proves only the affine full-permutation form. It does not inherit an unrestricted nonlinear set-representation theorem from an analogy.

[Xu et al., 2019](https://arxiv.org/abs/1810.00826) analyzes expressive power of graph aggregation architectures.
The independent dependency-radius proof concerns physical local communication; it is not a proof that every graph program has a particular neural expressivity limit.

## Information and memory

[Shannon, 1948, primary reprint](https://www.cs.yale.edu/homes/yry/readings/general/shannon1948.pdf) supplies entropy, information and coding foundations.
M2–M5 apply entropy inequalities to an explicitly frozen independent-bit workload, with adaptive probe transcripts and all data-dependent retained code counted.
The exact three-coordinate cache frontier is proved here as an application; no claim is made that caching, coding lower bounds or the underlying entropy inequalities are novel.
M6 uses the inherited finite residual-state indistinguishability argument; the formal derivation unit contains its finite learning and state-transport treatment.

## Known neural representatives

[Cybenko, 1989](https://papers.baulab.info/papers/Cybenko-1989.pdf) proves approximation under a specified neural activation framework.
The present Boolean detector construction is an elementary exact representative; it neither replaces those analytic assumptions nor makes the representation necessary.

[Hochreiter and Schmidhuber, 1997](https://doi.org/10.1162/neco.1997.9.8.1735) introduces LSTM; [author-hosted paper](https://people.idsia.ch/~juergen/lstm1997-2024head.pdf).
The present HOLD/WRITE identity and leaky-memory bound isolate a persistence mechanism. They do not derive all gates of an LSTM cell.

[Vaswani et al., 2017](https://arxiv.org/abs/1706.03762) defines the Transformer and its attention mechanism.
The finite-logit retrieval error calculation is an elementary bound for one specified softmax average, not a theorem about arbitrary Transformers.

[Jacobs et al., 1991](https://www.cs.toronto.edu/~fritz/absps/jjnh91.pdf) develops adaptive mixtures of local experts.
The present selected-input lower bound concerns necessary data dependence and the difference between fixed and query-dependent reads; neural experts remain one representative.

## Probabilistic, local and retrieval representatives

[Pearl, 1986](https://www.sciencedirect.com/science/article/pii/000437028690072X) develops belief-network structuring and propagation.
Bayesian conditioning and factorization are adopted mechanisms. A factorization must be warranted; GMI does not obtain conditional independence by naming a graph.

[Cover and Hart, 1967](https://isl.stanford.edu/~cover/papers/transIT/0021cove.pdf) is the nearest-neighbor classification parent.
The family note's Lipschitz regression bias/variance calculation is separately proved under explicit mean-zero independent-noise assumptions; it is not attributed as Cover–Hart's classification theorem.

[Lewis et al., 2020](https://arxiv.org/abs/2005.11401) combines nonparametric retrieval with parametric generation for knowledge-intensive tasks.
M1–M4 quantify a simpler independent-bit retrieval workload; they do not establish semantic fidelity or reproduce the paper's neural architecture.

[Bellman, 1954](https://pubmed.ncbi.nlm.nih.gov/16589462/) is a primary dynamic-programming source.
The finite-horizon conditioning proof is inherited. The transition model, objective and exact/certified comparison interface are explicit supplied premises.

## Present synthesis and evidence requirements

E5's orthogonal-projection risk identity follows from second moments and trace algebra; Gaussianity is optional.
The added interface combines it with explicit implementation work, coefficient storage and fully accounted development/reuse costs.
The finite orbit law yields a complete affine solution space from constraints, beyond a catalog of hand-authored architecture examples.
The memory law covers all admitted coded retained states and adaptive probe programs, beyond comparing a few chosen cache templates.
Neither advance supplies missing task symmetries, independent-bit ecology, scalar-price choices or observed reuse for free.
An empirical improvement claim requires registered matched parent implementations, acquisition/validation/invalidation bills, heldout tasks and failure controls.
Novel architectural priority requires a broader literature and reduction audit; the present notes claim an explicit proved synthesis and scoped executable consequences.
