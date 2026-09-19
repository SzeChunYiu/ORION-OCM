# Z6 parent-ownership disclosure

Assimilation-first. Every theory this package scores is a real position with a
real owner; the package absorbs each one as an executable rule, credits it, and
states its own residual afterwards. Nothing here is claimed novel except
section 3.

## 1. Literature parents, and what each owns

| parent | citation | what it owns | what is not claimed |
|---|---|---|---|
| Bayesian decision theory | Savage, *The Foundations of Statistics*, Wiley 1954; Berger, *Statistical Decision Theory and Bayesian Analysis*, 2nd ed., Springer 1985, doi:10.1007/978-1-4757-4286-2 | minimising expected loss under a declared loss function | no Bayesian result is re-proved; the equivalence found here is a property of the argmin, which is Savage's and Berger's |
| Bounded / resource rationality | Simon, *A behavioral model of rational choice*, QJE 69(1):99-118, 1955, doi:10.2307/1884852; Russell & Subramanian, *Provably bounded-optimal agents*, JAIR 2:575-609, 1995, doi:10.1613/jair.133 | utility net of computational cost | as above |
| Algorithm selection | Rice, *The algorithm selection problem*, Advances in Computers 15:65-118, 1976, doi:10.1016/S0065-2458(08)60520-3 | choosing among algorithms by a declared performance measure | as above |
| Neural architecture search | Zoph & Le, *Neural architecture search with reinforcement learning*, ICLR 2017, arXiv:1611.01578; Tan et al., *MnasNet*, CVPR 2019, doi:10.1109/CVPR.2019.00293 | architecture search under a resource regulariser | as above |
| Active inference | Friston, *The free-energy principle: a unified brain theory?*, Nature Reviews Neuroscience 11:127-138, 2010, doi:10.1038/nrn2787 | expected free energy as a selection objective | the registered reading uses an uninformative prior under which the complexity term is constant; this is a *narrow* reading and is labelled as such |
| MDL / compression | Rissanen, *Modeling by shortest data description*, Automatica 14(5):465-471, 1978, doi:10.1016/0005-1098(78)90005-5; Grunwald, *The Minimum Description Length Principle*, MIT Press 2007 | the two-part code and model selection by code length | that MDL is refuted — it is not; it is correct in every world whose declared accounting *is* a code length (all `20` `E-COD` worlds) |
| Information theory | Shannon, *A mathematical theory of communication*, BSTJ 27:379-423, 1948, doi:10.1002/j.1538-7305.1948.tb01338.x | the feasibility constraint: zero-error delayed recall needs at least one bit of state | that information theory makes a price prediction; it abstains, and that is the honest reading |
| Computational learning theory / SRM | Vapnik, *Statistical Learning Theory*, Wiley 1998; Blumer, Ehrenfeucht, Haussler & Warmuth, *Occam's razor*, IPL 24(6):377-380, 1987, doi:10.1016/0020-0190(87)90114-1 | risk plus a class-complexity penalty owned by the learner | the Occam's-razor theorems require a *consistent* hypothesis; no stateless candidate is consistent here, so `T10_OCCAM_HARD` is registered as a **folk rule** and is not a test of Blumer et al. |
| Program synthesis | Alur et al., *Syntax-guided synthesis*, FMCAD 2013, doi:10.1109/FMCAD.2013.6679385 | grammar-restricted search minimising a declared cost | as above |
| RL / optimal control | Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press 2018 | optimal policy under a declared cost | as above |
| Evolutionary / open-ended search | Lehman & Stanley, *Exploiting open-endedness to solve problems through the search for novelty*, ALIFE XI, 2008 | search dynamics and novelty, not the argmin | that open-ended search makes a selection prediction; it abstains |

## 2. In-repository parents (pinned in `MANIFEST_V1.json`)

| package | what it owns |
|---|---|
| `research/gmi-833-heldout-20-transitions-v1` | the `65552`-candidate universe, the objective, the registered boundary `lambda* = eta*p/2`, the `5x4` grid and the `2*lambda*` negative control. Its rows are not touched and its law is not re-derived here — it is **tested**, and it loses outside its own uniform-input assumption |
| `research/gmi-833-z-z5-critical-phenomena-v1` (branch `research/833-sec-z2`, PR #1034, not on `main`) | the first refutation of the unqualified `eta*p/2`, along the alphabet-size dimension, and the failed-prediction register pattern this package reuses |
| `research/gmi-833-z-z7-impossibility-v1` (same branch) | the registered family predicates and the vacuity-classifier pattern |
| `research/gmi-833-z-z2-minimal-prior-v1` (this branch) | the semantic-collapse and invariance machinery; Z6 does not depend on it at runtime |

## 3. The residual contribution of this tranche

1. An **executable registry** of thirteen parent selection rules covering every
   family the Z6 row names, each emitting a prediction for each of `404`
   preregistered worlds before adjudication.
2. **Three environments that separate them**, with the disagreement counts and
   the adjudications measured rather than asserted: `220`, `220` and `226`
   `R1` disagreements for MDL, the folk Occam rule and SRM, each losing exactly
   `40` of `60` `E-LIN` worlds.
3. A **refutation of the programme's own registered law** along a second,
   independent dimension: `108` of `324` skewed-input worlds mispredicted, and
   the unifying repair `lambda* = eta*p*R0` correct in all `404`.
4. A **proved and exhaustively verified observational equivalence** between the
   repaired law and seven declared-cost parents, with a `200`-rule null that
   `0` random monotone rules pass — so the equivalence is a property of those
   parents and not of a coarse readout.
5. An explicit, per-parent **non-distinguishability statement** for the three
   groups where no discriminating experiment exists at this scope.

Everything else is parent property.
