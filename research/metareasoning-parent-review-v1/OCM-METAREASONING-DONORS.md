# Established mechanisms for paid computation and reusable state

Read 8 September 2026 to inform the source review of PR154 at
9087971dd3a9847149fa8cf844cb13e84a57cacd. This is literature assimilation,
not a new theorem, executed comparison or claim of an unoccupied research niche.

## Computation selection: a direct mechanism donor

[Hay, Russell, Tolpin and Shimony, *Selecting Computations: Theory and Applications*
(2012)](https://arxiv.org/pdf/1207.5879) model paid observations and a terminal
action in a metalevel decision process. Definition1 and the subsequent model use
bounded utilities and a strictly positive computation cost. Theorem5 bounds the
optimal expected computation count by perfect-information value divided by cost;
this is not a uniform bound on every sample path. Section6.2 explicitly discusses
reuse across future decisions and its additional valuation problem.

**OCM application:** use explicit computation/stop alternatives, charge the selector,
and retain future reuse in the state. This paper supplies an established parent
for those ideas. Its Bayesian utility model does not itself authorize an OCM
answer, establish an admissible model class, or cover a zero-priced cognitive loop.
Read scope: definitions1/3, theorems4/5, example3, and section6.2; no empirical
reproduction or full proof audit of the paper.

## Termination: reuse the proper-policy distinction

[Bertsekas, *Proper Policies in Infinite-State Stochastic Shortest Path Problems*
(2017; corrected 2020 revision consulted)](https://arxiv.org/abs/1711.10129v2)
defines properness at a state by both finite expected total cost and finite expected
steps to termination. It distinguishes optimal cost over all policies from optimal
cost over proper policies.
Under nonnegative costs these values and Bellman fixed points need not coincide.
The paper gives additional function-class and properness conditions for its
characterizations; writing a Bellman equality alone does not provide them.

**OCM application:** PR154's general same-horizon cognitive recurrence needs an
explicit termination contract. For a first finite implementation, retain a finite
cognitive allowance or a well-founded state rank and charge each transition.
The existing two-arm R0B executable already decreases demand horizon on both arms.
Its behavior must not be conflated with the more general note's missing assumption.
Read scope: introduction, proper-policy definition, propositions2/7 and their
stated conditions, example1 and conclusion. Proposition7 in this corrected revision
requires equation16 or finite W in addition to its other conditions; the original
2017 statement is not the version relied on here. No OCM transfer theorem follows.

## Reusable investment: useful comparison, conditional mapping

[Lotker, Patt-Shamir and Rawitz, *Rent, Lease or Buy: Randomized Algorithms for
Multislope Ski Rental* (expanded2010 version; STACS2008)](https://www.eng.biu.ac.il/~rawitzd/Papers/ski.pdf)
studies unknown-duration investment choices with setup prices and constant rental
rates. Its additive model charges differences in setup prices when advancing to
a more expensive, cheaper-to-use state. Section3 decomposes that model into
two-slope problems; section4 develops optimal randomized strategies.

**OCM application:** this supplies a serious conventional parent for unknown-horizon
state investment when the task can be mapped to those assumptions. Query-dependent
inverse costs, irregular frontier benefits, resets and revocations are not a
constant rental-rate model automatically. Qualify the reduction or label a policy
as an adaptation; do not import the competitive guarantee by analogy.
Read scope: introduction, section2 model, section3 reduction and associated proof.
Section4's algorithm is identified for follow-up, not independently qualified here.

## Concrete decisions

- Keep the exact two-arm state model as the first strategy-selection parent.
  Its finite experiment is narrower than a universal cognitive controller.
- Repair the generic termination/stopping statements using the established
  distinctions above. Common safe-action availability and economic stopping
  are separate questions.
- Certify numerical action sets before treating them as exact partitions.
  The source review gives a scaled-integer recurrence for the current uniform,
  integer-cost setting; implementing it requires a separate source-bound run.
- Compare unknown-horizon reuse with a faithfully mapped online investment parent
  before adding a learned policy. All OCM policy learning remains explicit and
  non-neural; external neural systems may be comparison arms only.
- A possible research contribution must still demonstrate a useful mechanism
  beyond these parents under justified revision, retention and complete costs.
  Paid computation, persistence or the Bellman notation alone is inherited.

The foundational [Russell and Wefald paper (1991)](https://doi.org/10.1016/0004-3702(91)90015-C)
also frames computation value through its effect on external action. Its primary
publisher abstract was read; it is background here, not a full-text source audit.
