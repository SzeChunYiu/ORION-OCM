# AE10 parent-ownership disclosure

Assimilation-first. **Nothing below is claimed novel.** The machine-readable
form of this disclosure is `USE_5_terminology_crosswalk` in `RESULT_V1.json`,
so the crosswalk is a checked artifact rather than prose.

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Predictive V-information | the notion that extractable information is relative to a predictor family; `U` is an instance with `V = H_R` and 0-1 loss | Xu, Zhao, Song, Ermon, Finn, "A Theory of Usable Information Under Computational Constraints", ICLR 2020. arXiv:2002.10689 |
| Bounded rationality | the resource axis itself: that optimality is relative to a computational budget | Simon, Quarterly Journal of Economics 69 (1955) 99-118. doi:10.2307/1884852; Russell and Subramanian, JAIR 2 (1995) 575-609. doi:10.1613/jair.133 |
| Resource-rational analysis | the programme of conditioning behavioural predictions on resource budgets | Lieder and Griffiths, Behavioral and Brain Sciences 43 (2020) e1. doi:10.1017/S0140525X1900061X |
| HILL pseudoentropy / computational entropy | information that exists but is not extractable by a bounded party | Hastad, Impagliazzo, Levin, Luby, SIAM Journal on Computing 28 (1999) 1364-1396. doi:10.1137/S0097539793244708 |
| Rate-distortion and the data-processing inequality | the full-information ceiling of USE-2 | Cover and Thomas, *Elements of Information Theory*, 2nd ed., Wiley (2006). doi:10.1002/047174882X |
| Analysis of Boolean functions | the unconditional junta and decision-tree lower bounds for parity, and its exact uniformity on proper coordinate subsets | O'Donnell, *Analysis of Boolean Functions*, Cambridge University Press (2014). doi:10.1017/CBO9781139814782 |

## What is NOT claimed novel

- The idea of usable/accessible information relative to a decoder class.
- That a maximum over a larger class is larger (USE-1's content).
- The full-information ceiling.
- That parity is unconditionally hard for juntas and shallow decision trees.
- Any statement about cryptographic hardness or complexity classes.

## Residual contribution of this tranche

1. A **frozen five-dimensional budget lattice** on which usable information is
   computed exactly, with monotonicity and the ceiling verified over all
   9,000 ordered budget pairs rather than assumed, and with the rule-class
   inclusion premise itself checked.
2. An **equal-Shannon separation on both axes**: a decoding-cost pair carrying
   exactly one bit each with usable information `0` versus `1/2`, and a
   search-cost curve on a **single fixed world**, so its information content is
   identical by identity rather than by a coincidence of two distributions.
3. An **honest lattice**: time and energy are declared dimensions that are not
   instantiated, and the receipt says so in a checked field, so no reader can
   mistake the package for an energetic claim.
4. A **verified rather than assumed** non-bindingness of the communication
   dimension, on which the null detector's notion of `below the top` depends.
