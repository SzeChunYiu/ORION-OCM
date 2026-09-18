# PARENT_DISCLOSURE_V1 — what this tranche owes, and what is new here

Assimilation first: every idea below is absorbed as a strongest parent, and the
residual contribution is stated at the end. Nothing in this package claims
novelty for any of it.

## 1. The in-corpus parent this package consumes

**`research/gmi-833-capability-predictor-v1` (PR #1012).** The entire predictor
is parent-owned: the exact total deterministic `C_hat = F(M,E,R,H,D,U)`
(KP-1A/1B/1C), the ten-mode prospective failure taxonomy (KP-2A/2B/2C), the
total typed-uncertainty attachment through a single proved `emit` site
(KP-3A/3B/3C), and the two boundaries KP-1D (soundness is unconditional only
over *consistent* worlds) and KP-2D (first-crossing attribution is
order-dependent on 6,347/8,640 inputs). This package **does not modify `F`** and
proves it two ways per run (git blob sha of the parent file; a sha256 over the
`co_code` of all 138 code objects, before and after every installation). The
load-bearing parent design decision — scoring a resource-inadmissible candidate
`UNSATISFIED` *inside the image* rather than deleting it — is preserved, and its
hostile is replayed here on held-out data as HE3.

Also consumed: `gmi-833-global-uncertainty-v1` (#851) for the U-1 constructor
semantics, the U-2B dependence-safe union bound and U-4A/U-4B query
identification; `gmi-833-heldout-20-transitions-v1` (#901) and
`gmi-833-real-transition-receipts-v1` (#903) for the custody protocol — predictions
frozen and pushed before any outcome oracle exists, deterministic CI replay from
committed receipts, and the V2-amendment pattern for a registered revival;
`gmi-833-aj9a-known-family-benchmark-v1` for the post-hoc family-fingerprint
discipline that motivates the blindness enforcement here.

## 2. External parents

**Partial identification.** The identified-set machinery — a point only when the
image is a singleton, otherwise a set and an abstention — is Manski's.
Manski, C. F. (1990), "Nonparametric Bounds on Treatment Effects",
*American Economic Review* 80(2):319–323; Manski, C. F. (2003), *Partial
Identification of Probability Distributions*, Springer.

**Selective prediction / reject option.** Abstention as a first-class decision
terminal is Chow's. Chow, C. K. (1970), "On optimum recognition error and reject
tradeoff", *IEEE Transactions on Information Theory* 16(1):41–46,
doi:10.1109/TIT.1970.1054406. El-Yaniv, R. & Wiener, Y. (2010), "On the
foundations of noise-free selective classification", *JMLR* 11:1605–1641. The
observation that a predictor which abstains whenever unsure has trivially good
coverage — which is why every calibration figure here is reported next to its
abstention rate — is theirs, not ours.

**Arbitrary-dependence probability bounds.** The `1 - alpha - sum(beta)`
composition is Boole's inequality with Fréchet-style dependence freedom.
Boole, G. (1854), *An Investigation of the Laws of Thought*; Fréchet, M. (1935),
"Généralisations du théorème des probabilités totales", *Fundamenta Mathematicae*
25:379–387.

**Calibration.** The notion of empirical coverage against a nominal level is
Dawid's. Dawid, A. P. (1982), "The Well-Calibrated Bayesian", *Journal of the
American Statistical Association* 77(379):605–610,
doi:10.1080/01621459.1982.10477856. Finite-sample distribution-free coverage is
conformal prediction: Vovk, V., Gammerman, A. & Shafer, G. (2005), *Algorithmic
Learning in a Random World*, Springer, doi:10.1007/b106715. Modern
miscalibration of neural predictors: Guo, C. et al. (2017), "On Calibration of
Modern Neural Networks", *ICML*, arXiv:1706.04599.

**Out-of-distribution failure.** Quiñonero-Candela, J. et al., eds. (2009),
*Dataset Shift in Machine Learning*, MIT Press; Hendrycks, D. & Gimpel, K.
(2017), "A Baseline for Detecting Misclassified and Out-of-Distribution Examples
in Neural Networks", *ICLR*, arXiv:1610.02136.

**Prospective registration.** Freezing predictions before outcomes exist is the
Registered Report discipline. Chambers, C. D. (2013), "Registered Reports: A new
publishing initiative at Cortex", *Cortex* 49(3):609–610,
doi:10.1016/j.cortex.2012.12.016.

**Automata expressivity and the held-out architecture families.** The
state-equivalence view behind the expressivity coordinate is Myhill–Nerode:
Nerode, A. (1958), "Linear automaton transformations", *Proceedings of the AMS*
9(4):541–544, doi:10.2307/2033204. The counter/stack/feed-forward separation and
the well-known difficulty of parity for trained recurrent networks: Weiss, G.,
Goldberg, Y. & Yahav, E. (2018), "On the Practical Computational Power of Finite
Precision RNNs for Language Recognition", *ACL*, arXiv:1805.04908; Merrill, W.
(2019), "Sequential Neural Networks as Automata", arXiv:1906.01615. Our V1
registered law over-predicted parity learnability for exactly the reason this
literature documents; we did not anticipate it, and the falsification is recorded
rather than smoothed.

## 3. Explicitly NOT claimed novel

The predictor, the taxonomy, the uncertainty type system, the union bound, the
identified-set semantics, abstention-as-terminal, the calibration concept, the
OOD concept, the freeze-before-outcome protocol, the architecture families, and
the difficulty of learning parity. Every one is a parent's.

## 4. The residual contribution of this tranche

1. **Universe injection as the test instrument.** A 23-name registration surface
   that substitutes a held-out universe into the parent's `F` with two
   independent machine-checked proofs that no line of `F` changed — so "tested on
   held-out data" means the same function, not a re-implementation.
2. **Four pairwise-disjoint populations with a one-coordinate separating
   certificate** (`rho[3] ∈ {0} / {1,2} / {3,4} / {5,6} / {7,8}`), each backed by
   an exhaustive pairwise descriptor comparison.
3. **A second route that reproduces the frozen prediction stream by sha256**
   rather than by field comparison: 51,840 rows × 18 fields per universe,
   recomputed from frozensets of realization records by code that imports
   nothing from this package or the parent.
4. **An exactly computable empirical calibration statistic** for a predictor
   whose parent proved only exact finite coverage: coverage under the registered
   arbitrary-dependence fault law, enumerated over all 32 fault patterns with
   exact rational weights, reported beside the abstention rate and with an
   inflated-fault-law hostile that breaks it.
5. **A structural OOD boundary** that separates the two things the literature
   conflates: where `F` abstains on unregistered worlds, and where it emits a
   point that is wrong because the world was never registered — the latter being
   the parent's KP-1D restated, not a new soundness failure.
6. **A quantified bridge failure on real trained systems**, with `F`-soundness
   and registration truthfulness reported as two separate numbers, and a
   registered revival tested on a newly frozen population.
