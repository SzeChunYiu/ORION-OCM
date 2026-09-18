# Z13 — parent ownership disclosure

Assimilation first: the machinery below is not ours, and saying so is what makes
the residual visible.

## What is not claimed novel

- **Exhaustive finite-state machine minimisation.** Choosing the error-minimising
  output for a fixed next-state function by per-address majority vote is the
  standard 0-1 loss Bayes rule applied to a finite partition; it is the same
  argument as decision-stump fitting. Nothing here is a new algorithm.
  Parents: Moore, E. F., "Gedanken-experiments on sequential machines", *Automata
  Studies*, Princeton University Press, 1956, pp. 129-153; Mealy, G. H., "A
  method for synthesizing sequential circuits", *Bell System Technical Journal*
  34(5):1045-1079, 1955, doi:10.1002/j.1538-7305.1955.tb03788.x; Hopcroft, J. E.,
  "An n log n algorithm for minimizing states in a finite automaton", in *Theory
  of Machines and Computations*, Academic Press, 1971, pp. 189-196.
- **Rate-distortion style resource pricing.** The linear trade
  `error + lambda * resource` and the fact that its solutions trace the lower
  convex envelope of the achievable set is Lagrangian scalarisation, known in
  exactly this form in rate-distortion theory and in multi-objective
  optimisation. Parents: Shannon, C. E., "Coding theorems for a discrete source
  with a fidelity criterion", *IRE Nat. Conv. Rec.* 4:142-163, 1959; Berger, T.,
  *Rate Distortion Theory*, Prentice-Hall, 1971; Geoffrion, A. M., "Proper
  efficiency and the theory of vector maximization", *J. Math. Anal. Appl.*
  22(3):618-630, 1968, doi:10.1016/0022-247X(68)90201-1; Everett, H., "Generalized
  Lagrange multiplier method for solving problems of optimum allocation of
  resources", *Operations Research* 11(3):399-417, 1963, doi:10.1287/opre.11.3.399.
- **Memory-limited prediction of delayed inputs.** That `k` bits of state are
  needed to reproduce a `k`-step-delayed symbol, and that fewer bits force a
  strictly positive error floor, is elementary and is the content of the
  finite-window / finite-memory literature. Parents: Hellman, M. E. and Cover,
  T. M., "Learning with finite memory", *Annals of Mathematical Statistics*
  41(3):765-782, 1970, doi:10.1214/aoms/1177696956.
- **The prediction being adjudicated.** `Z13-P1` is not ours. It was frozen by
  `research/gmi-833-z-z13-property-prediction-freeze-v1` on branch
  `research/833-sec-z3` (PR #1039), blob `25febfa6`, commit `0cc617fc`.
- **The registered law it rests on.** `lambda* = eta*p*R0` is
  `research/gmi-833-z-z6-discrimination-v1` `DS-5`; the alphabet form
  `eta*p*(1 - 1/A)` is `research/gmi-833-z-z5-critical-phenomena-v1` `CP-5`; the
  six named families and their address map are
  `research/gmi-833-z-z4-universality-v1` and
  `research/gmi-833-z-z6-discrimination-v1`. All three are on sibling branches,
  not on `main`, and are cited as parents rather than assumed.

## The residual contribution of this tranche

1. The exact one-bit delay-2 floor `5/16` in this universe, and the fact that the
   `4` next-state functions attaining it are disjoint from the `2` attaining a
   zero delay-1 error (`ZA-1`, `ZA-3`).
2. The demonstration that a selection threshold above two resource levels is a
   **marginal** and not a level, with the exact excess `eta*p2/8` by which
   `Z13-P1` overstates it, and the identification of the marginal law as the
   unique member of its declared family reproducing the enumeration (`ZA-2`).
3. The proof that `Z13-P1`'s HIT condition is logically unsatisfiable under the
   registered family lift (`ZA-4`).
4. The exact niche width `eta*(p1/2 - p2/8)` and the consequent correction of the
   matched negative ecology from `p2 = 0` to `4*p1 <= p2` (`ZA-5`).

None of these is a new theory. They are exact facts about a registered finite
universe, and a published refutation of a registered prediction.
