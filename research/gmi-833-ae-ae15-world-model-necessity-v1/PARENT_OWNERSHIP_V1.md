# Parent ownership — gmi-833-ae-ae15-world-model-necessity-v1

Nothing in this package is claimed novel against the parent literature. The
parents below own the concepts; this package owns one exact finite
construction and its machine-checked verification.

## What the parents own

**Partially observed decision problems, belief states and sufficient
statistics.** Astrom (1965), *Journal of Mathematical Analysis and
Applications* 10(1):174-205, doi:10.1016/0022-247X(65)90154-X. Smallwood and
Sondik (1973), *Operations Research* 21(5):1071-1088,
doi:10.1287/opre.21.5.1071 — the alpha-vector backward construction that route
B uses is theirs verbatim. Kaelbling, Littman and Cassandra (1998),
*Artificial Intelligence* 101(1-2):99-134, doi:10.1016/S0004-3702(98)00023-X.

**Predictive state representations.** Littman, Sutton and Singh (2001), NIPS.
Singh, James and Rudary (2004), UAI, arXiv:1207.4167. The idea that a statistic
of history sufficient for future observations is a representation in its own
right is theirs.

**Model-based versus model-free control and the arbitration question.** Sutton
(1991), *SIGART Bulletin* 2(4):160-163, doi:10.1145/122344.122377. Daw, Niv and
Dayan (2005), *Nature Neuroscience* 8(12):1704-1711, doi:10.1038/nn1560.
Keramati, Dezfouli and Piray (2011), *PLoS Computational Biology* 7(5):e1002055,
doi:10.1371/journal.pcbi.1002055 — the speed/accuracy cost trade-off that the
registered phase family instantiates is theirs.

**Memoryless-policy suboptimality under observation aliasing.** Singh, Jaakkola
and Jordan (1994), ICML, doi:10.1016/B978-1-55860-335-6.50042-8. Littman
(1994), ICML. The result that a memoryless policy is strictly suboptimal when
two states requiring different actions share an observation is entirely theirs.
AE15-3 does not reprove it and does not improve on it.

**Latent-variable identifiability.** Hyvarinen and Pajunen (1999), *Neural
Networks* 12(3):429-439, doi:10.1016/S0893-6080(98)00140-3. Locatello, Bauer,
Lucic, Ratsch, Gelly, Scholkopf and Bachem (2019), ICML, arXiv:1811.12359.
Khemakhem, Kingma, Monti and Hyvarinen (2020), AISTATS, arXiv:1907.04809.
Non-identifiability of a latent from observational behaviour is theirs.

## What is NOT claimed novel

The taxonomy of representations; belief-state optimality; the alpha-vector
algorithm; predictive state representations; the model-based/model-free cost
trade-off; memoryless suboptimality under aliasing; latent non-identifiability.
None of these is offered as a contribution of this tranche. No asymptotic,
continuous or real-system claim is made anywhere, and the forbidden promotions
listed in `MANIFEST_V1.json` are refused rather than softened.

## The residual

1. One registered world at `|S| = 4`, `|O| = 3`, `|A| = 3`, `H = 3`,
   `gamma = 1/2` on which the memoryless, open-loop cached and greedy-value
   interfaces are **simultaneously** strictly suboptimal, each class closed by
   exhaustive enumeration over the whole finite class, with exact rational
   values `1/4` against an optimum of `1/2`. The parents give the aliasing
   mechanism for the memoryless case alone; combining it with a stochastic
   branch that also defeats open-loop replay, on one world, at exact rational
   values, is the added piece.
2. The reward-swap probe as an executable separator rather than a description:
   replacing `R` by `R_ALT` and re-querying with no further interaction turns
   "only an explicit generative model supports counterfactual re-planning" into
   an exact number — a shortfall of exactly `3/4` for each of the three
   model-free interfaces and `0` for the model.
3. The exact rational threshold `c*(G) = G/4` with the flip certified strictly
   on both sides at every registered `G`, emitted as a falsifiable bound with a
   violating witness from an explicitly relaxed class.
4. A non-identifiability pair whose observational and predictive joints are
   exactly equal and whose interventional profiles differ exactly, shipped with
   an exactly recoverable case on the same roster, so the distinction between
   an identifiable world factor and a merely predictive coordinate is decided
   by computation rather than by argument.
