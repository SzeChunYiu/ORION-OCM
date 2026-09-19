# Parent ledger — gmi-833-h-real-scale-revival-v1

Assimilation first. Everything below is somebody else's result, absorbed and
cited. What this package adds is stated at the end and is small.

## 1. In-repository parents, and exactly what is taken from each

| parent | what is taken | what is NOT taken |
|---|---|---|
| `research/gmi-833-h-real-scale-classical-v1` | the shape of an eleven-coordinate ledger; the idea of a post-hoc structural classifier that reads expression trees; the charged-cost model shape; the registered definition of real-scale (its section 7, adopted unchanged in substance so the definition does not move with the package it certifies); and the three single-stage failure attributions this package answers | every number. No gate certificate, no held-out quantity, no control outcome, no scope. Its `SIGMA_H02`/`SIGMA_H03`/`SIGMA_H04` certificates are not composed with anything here |
| `research/gmi-833-h-neutral-four-family-v1` | the observation that ten of the eleven coordinates are reachable on a finite state space | its `SIGMA_4F` certificates. `FGS-2` forbids gluing them to a real-scale coordinate and they are not glued |
| `research/gmi-833-h-family-requirement-ledger-v1` | the per-row residual map, and `HRL-1`, which names `CROSS_SCOPE_GATE_COMPOSITION` | nothing else; it closes no checkbox and emits no certificate |
| PR #997 `FGS-2`, `FGS-3`, `FGS-4` | the scope-gluing no-go that governs section 2 of the freeze | — |

## 2. External parents, with citations

Least squares and linear prediction are not novel here and are not claimed to
be. Neither are generalized linear models, basis and kernel methods, symbolic
regression over an expression grammar, or description-length model comparison.

- A. N. Legendre (1805) and C. F. Gauss (1809) — least squares. No DOI.
- J. A. Nelder and R. W. M. Wedderburn (1972), "Generalized Linear Models",
  *Journal of the Royal Statistical Society A* 135(3):370–384.
  DOI `10.2307/2344614`. The log link on a count response, the canonical link,
  and iteratively reweighted least squares are theirs.
- P. McCullagh and J. A. Nelder (1989), *Generalized Linear Models*, 2nd ed.,
  Chapman & Hall. The admissibility argument — a count mean must be
  non-negative, so an identity link on counts is inadmissible — is standard
  there and is not this package's observation.
- A. C. Cameron and P. K. Trivedi (2013), *Regression Analysis of Count Data*,
  2nd ed., Cambridge University Press. Over-dispersion, exposure, and the
  multiplicative structure of counts.
- M. A. Aizerman, E. M. Braverman and L. I. Rozonoer (1964), "Theoretical
  foundations of the potential function method in pattern recognition
  learning", *Automation and Remote Control* 25:821–837. The lifted feature
  map. No DOI.
- B. Schölkopf and A. J. Smola (2002), *Learning with Kernels*, MIT Press.
- C. K. I. Williams and M. Seeger (2001), "Using the Nyström method to speed up
  kernel machines", *NeurIPS 13*; A. Rahimi and B. Recht (2007), "Random
  features for large-scale kernel machines", *NeurIPS 20*. Landmark and random
  feature approximations, and their cost trade-off. The landmark arm of
  `SIGMA_R04` is an instance of theirs.
- J. Makhoul (1975), "Linear prediction: A tutorial review", *Proceedings of
  the IEEE* 63(4):561–580. DOI `10.1109/PROC.1975.9792`. Linear prediction of
  a sampled waveform, which is what `F02` is.
- S. T. Piantadosi (2014), "Zipf's word frequency law in natural language: A
  critical review and future directions", *Psychonomic Bulletin & Review*
  21(5):1112–1130. DOI `10.3758/s13423-014-0585-6`. The heavy-tailed,
  over-dispersed count structure `F03` exhibits is a property of the corpus,
  long documented, not a discovery here.
- J. R. Koza (1992), *Genetic Programming*, MIT Press; M. Schmidt and
  H. Lipson (2009), "Distilling free-form natural laws from experimental data",
  *Science* 324(5923):81–85, DOI `10.1126/science.1165893`;
  S.-M. Udrescu and M. Tegmark (2020), "AI Feynman: a physics-inspired method
  for symbolic regression", *Science Advances* 6(16):eaay2631,
  DOI `10.1126/sciadv.aay2631`. Search over an expression grammar to recover a
  functional form from data is theirs. The enumerative, semantically
  quotiented, family-blind variant used here is an implementation choice within
  their frame.
- J. Rissanen (1978), "Modeling by shortest data description", *Automatica*
  14(5):465–471. DOI `10.1016/0005-1098(78)90005-5`. Description length as a
  model-comparison quantity; the charged cost model is a coarse, explicitly
  registered stand-in and is not offered as an advance on it.

## 3. What is NOT claimed novel

- No statistical method here is new. No estimator, link, kernel, or cost model
  is new.
- Recovering a linear predictor from audio, a log link from counts, or a lifted
  basis from an additive per-input functional is not new, is not surprising,
  and is not the contribution.
- The lower grammar, the enumeration, the semantic quotient, the post-hoc
  classifier and the eleven-coordinate ledger are the in-repository parents'
  forms, re-implemented here rather than imported.

## 4. The residual contribution of this tranche

Three things, all small and all methodological.

1. **A control with an applicability certificate.** The parent's control for
   the linear row refitted least squares on a permuted design and compared it
   with the best constant arm. That control *nests* the arm it is compared
   with, so its outcome carries no information in either direction. Here the
   response is permuted instead, and the control is *certified* by requiring
   every one of the 200 refits to land in a registered band around the constant
   arm — the run fails if they do not. The certificate, not the outcome, is the
   contribution: it is what distinguishes a control that bit from one that
   could not.
2. **An ecology admissibility condition asserted before any arm is fitted.**
   The parent's count response was zero on most rows, which is a legitimate
   source of over-dispersion but makes a per-row closeness criterion
   uninformative. Here the response is bounded below by one *by construction*
   and the condition is checked in exact arithmetic on the fit slice before any
   arm exists, failing the run rather than permitting a second ecology.
3. **A mapped boundary rather than a repaired classifier.** The parent's
   basis/kernel row failed because its response — the energy of the next window
   — is not additive in any per-input non-affine transform, and a squared
   affine score approximates it well. That is recorded as a counterexample
   (`RSR-5`) delimiting where lifted-basis recovery holds, and the classifier
   is neither re-read nor re-ordered.

Everything else in this package is an unoriginal application of the parents
above, executed at a registered scale with exact arithmetic.
