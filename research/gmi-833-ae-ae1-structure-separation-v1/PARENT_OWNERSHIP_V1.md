# AE1 parent-ownership disclosure

Assimilation-first: the parent mathematics below is absorbed and credited, and
the residual contribution of this tranche is stated afterwards. **Nothing in
the list is claimed novel.**

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Shannon information theory | mutual information, the product characterization of independence, entropy | Shannon, *A Mathematical Theory of Communication*, Bell System Technical Journal 27 (1948) 379-423. doi:10.1002/j.1538-7305.1948.tb01338.x |
| Statistical decision theory | Bayes risk, the optimality of the posterior-mode rule under 0-1 loss, the reduction of randomized to deterministic rules by convexity | Wald, *Statistical Decision Functions*, Wiley (1950); Berger, *Statistical Decision Theory and Bayesian Analysis*, 2nd ed., Springer (1985). doi:10.1007/978-1-4757-4286-2 |
| Value of information | that an observation's decision value depends on the utility, not only on the posterior | Howard, "Information Value Theory", IEEE Transactions on Systems Science and Cybernetics 2 (1966) 22-26. doi:10.1109/TSSC.1966.300074 |
| Causal inference / do-calculus | the distinction between `P(y \| x)` and `P(y \| do(x))`, the back-door criterion, confounded-triple non-identifiability | Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed., Cambridge University Press (2009). doi:10.1017/CBO9780511803161 |
| Boolean function complexity | that parity on `n` variables is not computed by any decision tree of depth below `n`, and that any junta on a proper subset of the coordinates has exactly zero correlation with it | O'Donnell, *Analysis of Boolean Functions*, Cambridge University Press (2014). doi:10.1017/CBO9781139814782 |
| Statistical learning theory | PAC learnability, the sample complexity of learning parities, the gap between asymptotic learnability and finite-sample performance | Kearns and Vazirani, *An Introduction to Computational Learning Theory*, MIT Press (1994); Shalev-Shwartz and Ben-David, *Understanding Machine Learning*, Cambridge University Press (2014). doi:10.1017/CBO9781107298019 |
| Resource-bounded information | that the usable content of an observation depends on the decoder class, the ancestor of the budget-indexed object used here | Xu, Zhao, Song, Ermon, Finn, "A Theory of Usable Information Under Computational Constraints", ICLR 2020. arXiv:2002.10689 |

## What is NOT claimed novel

- That mutual information can be positive while the Bayes gain is zero.
- That parity is hard for shallow decision trees and for juntas.
- That observational association is not causation.
- That the value of an observation depends on the utility.
- That finite-sample performance lags the asymptotic optimum.
- The definition of usable information relative to a decoder class.

## Residual contribution of this tranche

1. A **single consistent finite roster** on which all five separations of the
   AE1 checklist are evaluated simultaneously, in exact rational arithmetic,
   with both a closed-form route and an independently written enumeration
   oracle agreeing on every value.
2. **Minimality certificates** for the distributional separations: an exhaustive
   sweep of every joint on every shape up to `4x4` with probabilities that are
   multiples of `1/8` (16 shapes), yielding the minimal shape for each
   separation pattern and the exhaustive confirmation that `PRED` without `DEP`
   is realized on **no** shape of that grid.
3. An explicit, quantified refutation of the **budget-independent scalar**
   hypothesis, with three named candidate scalars refuted individually, paired
   with the positive disjunct: the monotone, full-information-bounded
   budget-indexed profile object.
4. A **validated detector**: the accessibility-gap detector reported with
   recall on a planted positive, the no-alarm case on known-clean worlds, and a
   published unthresholded null rate whose seven hits are diagnosed as genuine
   small gaps rather than suppressed.
