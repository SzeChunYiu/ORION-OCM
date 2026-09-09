# HST Literature Ledger V1

Rule: every claimed HST result states what is already parent-owned. Class per row:
**OWNS** (parent theorem covers it; HST only instantiates) · **ADAPTS** (HST adds a
condition/specialization) · **RESIDUAL** (genuinely HST-specific).

| parent | what it owns | class | used by |
|---|---|---|---|
| Wolpert–Macready NFL (IEEE TEC 1997) | no universal best optimizer over closed-under-permutation classes under uniform averaging | OWNS | T14 |
| Levin universal search; Schmidhuber OOPS/PowerPlay | bias-optimal allocation 2^{-L}; incremental reuse; solver/task co-development | OWNS | T04 |
| Solomonoff induction | universal prior and its incomputability | OWNS | T04, T15 |
| Blackwell comparison of experiments | garbling/dominance ⇒ value order for every decision problem | OWNS | T08 |
| Tishby–Pereira–Bialek IB | rate-distortion view of relevant information | OWNS (context) | T08 framing |
| Baxter JAIR 2000 | learnable bias over task environments generalizes under controlled families | OWNS | T09 |
| Maurer et al. JMLR 2016 | multitask representation sample-complexity benefit | OWNS | T09 |
| Alquier–Mai–Pontil AISTATS 2017 | lifelong regret bounds | OWNS | T09 |
| PAC-Bayes meta-bounds | information-theoretic generalization of learned priors | OWNS | T09/D6 |
| Kouvaris et al. PLoS CB 2017 | evolved development as learned inductive bias | OWNS (evidence donor) | T09 bridge |
| #145 transformation semigroup theory | closure `<O>`, generator structure | OWNS | T02 |
| Ashby requisite variety; Conant–Ashby | regulator bound + good-regulator theorem (only with their assumptions) | OWNS | context T03 |
| causal DAG intervention locality | do-calculus descendant effects | OWNS | T06 |
| Rice / Turing / Gödel | semantic undecidability, halting, incompleteness | OWNS | T15 |
| Blum 1967 speedup | no asymptotically optimal program for some computable problems | OWNS | T16 |
| Schmidhuber Gödel Machines | conditional global optimality of proved self-changes | OWNS | T15 |
| Adams et al. 2017; MODES 2019 | formal OEE definitions/metrics | OWNS | T12/T13 |
| DGM / Huxley-Gödel / AI4AI-Bench / HarnessDev | empirical self-improvement evidence | OWNS (evidence, not proof) | bridge only |

**HST residual (the only thing this capsule may claim as its own):** the packaging of
development/self-evolution as transformations of the search-generating state Σ with
resource-vector burden B, the finite evolvability estimator Ev at OCM scope, the
admission-bar/census-ceiling discipline inherited from #221, and the row→measurement
bridge into #145/#151/#217/#221. No new mathematics is claimed where a parent row says OWNS.
