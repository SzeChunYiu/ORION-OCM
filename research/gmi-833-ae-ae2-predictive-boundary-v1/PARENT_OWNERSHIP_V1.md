# AE2 parent-ownership disclosure

Assimilation-first. The parent mathematics is absorbed and credited; the
residual of this tranche is stated afterwards. **Nothing below is claimed
novel.**

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Shannon information theory | mutual information, its vanishing exactly at independence, entropy of a uniform alphabet | Shannon, Bell System Technical Journal 27 (1948) 379-423. doi:10.1002/j.1538-7305.1948.tb01338.x |
| Statistical decision theory | Bayes risk, optimality of the constant rule under independence, the convexity reduction of randomized to deterministic rules | Wald, *Statistical Decision Functions*, Wiley (1950); Berger, *Statistical Decision Theory and Bayesian Analysis*, 2nd ed., Springer (1985). doi:10.1007/978-1-4757-4286-2 |
| Csiszar-Kullback-Pinsker inequality | `KL(P‖Q) >= ‖P-Q‖_1^2 / 2` in nats, the step turning an L1 dependence bound into a mutual-information bound | Csiszar, Studia Scientiarum Mathematicarum Hungarica 2 (1967) 299-318; Kullback, IEEE Transactions on Information Theory 13 (1967) 126-127. doi:10.1109/TIT.1967.1053968 |
| Analysis of Boolean functions | decision-tree depth lower bounds for parity; the exact uniformity of parity restricted to any proper coordinate subset | O'Donnell, *Analysis of Boolean Functions*, Cambridge University Press (2014). doi:10.1017/CBO9781139814782 |
| Resource-bounded / usable information | that the extractable content of an observation is decoder-class-relative | Xu, Zhao, Song, Ermon, Finn, "A Theory of Usable Information Under Computational Constraints", ICLR 2020. arXiv:2002.10689 |
| Computational mechanics and symbolic dynamics | the doubling map's symbolic dynamics and its finite-precision predictability horizon | Crutchfield and Young, Physical Review Letters 63 (1989) 105-108. doi:10.1103/PhysRevLett.63.105 |
| Series expansions of the logarithm | the `atanh` and Mercator expansions and their remainder bounds | standard analysis; no attribution of novelty |

## What is NOT claimed novel

- That independence implies no learner can beat the base rate.
- The Csiszar-Kullback-Pinsker inequality or any strengthening of it.
- That parity is hard for shallow decision trees.
- That the doubling map has a finite-precision predictability horizon.
- That mutual information does not measure extractable value.
- Either logarithm series or its remainder bound.

## Residual contribution of this tranche

1. A **float-free** instantiation: mutual information is handled through exact
   rational brackets certified by two independent series plus containment in a
   crude analytic bracket, so no claim in the package depends on floating-point
   arithmetic.
2. An **exhaustive** verification of `gain <= D/2` over 670,396 grid cases with
   0 violations and 15,328 equality cases, with route B verifying each **step**
   of the proof separately rather than only its conclusion.
3. An **unconditional** Shannon-versus-accessible separation: one full bit of
   mutual information with exactly base-rate accuracy at every decoder depth
   below three, resting on a machine-checked proper-subset uniformity fact
   rather than on a hardness assumption — paired with a same-information world
   (the dictator) that is decoded perfectly at depth one.
4. A **registered fixture roster** whose four defining properties are
   machine-checked, including the pooled-independence property of the drifting
   source, which is the sharpest available statement that historical dependence
   can become not merely useless but harmful.
