# Literature synthesis V1 — Minimum Sufficient Cognition parent map

**Status:** literature synthesis / parent adoption / no OCM-specific novelty claim / no ML authorization.

This note records the mature theories that already cover most of the conceptual
surface now exposed by #152/#154.  The goal is not to rename known results.  The
goal is to use the strongest existing parent at each boundary, derive only the
OCM-specific corollaries that are still missing, and make the remaining
experimental questions smaller and falsifiable.

The companion `FORMAL_DECISION_CORE_V2.md` states and proves the finite results
used by this tranche.  `decision_core.py` keeps several of the finite identities
executable.

## Saturation criterion

The search was treated as saturated for this tranche when repeated searches over
five independent lanes returned the same parent structures and no additional
literature family changed the mathematical state variable or the next parent:

1. rational metareasoning / value of computation;
2. decision-region active information acquisition;
3. Blackwell--Le Cam comparison of information for decisions;
4. state abstraction / information states / lifecycle equivalence;
5. online capital investment / unknown lifetime.

Misspecification and ordinary algorithm selection were then checked as boundary
and successor literatures.  This is not a claim that every paper in those fields
has been read; it is a claim that further search was mostly rediscovering the
same parent objects relevant to the current finite OCM questions.

## 1. Rational metareasoning already owns the stop-versus-think problem

Russell and Wefald derive the value of computation from the computation's effect
on external action and explicitly frame metareasoning as resource-bounded
rationality.  Horvitz independently develops decision-theoretic control of
computation by trading improved answers against delay/computation cost.  Hansen
and Zilberstein give a dynamic-programming treatment of when an anytime
algorithm should stop, including uncertainty and monitoring cost.

**Adopt:** cognition is an action with a cost and a distribution over successor
information states.  The correct stop condition is Bellman/value-of-computation,
not entropy thresholding and not `Gamma(V,d) != empty` by itself.

**OCM implication:** DEV5 establishes a *safety stopping opportunity*; DEV6 and
X1 establish that the predicate used to recognize that opportunity has to be
charged.  R0A is a metareasoning problem over verification work.  R0B is a
metareasoning problem whose cognitive action also creates reusable state.

**Important accounting boundary:** a Bellman-optimal metapolicy is a normative
object.  Computing, storing, updating, restoring, or learning that metapolicy is
not free.  If the deployed controller evaluates a dynamic program online, that
work must itself enter the machine resource vector or be charged as offline
compilation plus lifecycle maintenance.

Primary parents:

- S. Russell and E. Wefald, "Principles of Metareasoning," *Artificial
  Intelligence* 49 (1991), 361--395. DOI 10.1016/0004-3702(91)90015-C.
- E. Horvitz, *Computation and Action Under Bounded Resources*, Stanford PhD
  dissertation, 1990.
- E. Hansen and S. Zilberstein, "Monitoring and Control of Anytime Algorithms:
  A Dynamic Programming Approach," *Artificial Intelligence* 126 (2001),
  139--157. DOI 10.1016/S0004-3702(00)00068-0.
- F. Callaway, S. Gul, P. Krueger, T. Griffiths, F. Lieder, "Learning to Select
  Computations," UAI 2018.  Useful as a later approximation parent, not as
  authority for a learned controller.

## 2. Decision Region Determination is the right parent for "know enough to act"

Equivalence Class Determination (Golovin, Krause, Ray) already replaces exact
hypothesis identification with identification of the equivalence class needed
for a downstream decision.  Decision Region Determination (Javdani et al.) goes
further: decision regions may **overlap**, and information gathering can stop as
soon as all surviving hypotheses lie inside at least one region.

This is almost exactly the protected common-action condition.  For protected
action `a`, define

```text
R_a(d) = { m : a is acceptable under model m in context d }.
```

Then for a version set `V`:

```text
Gamma(V,d) != empty
iff
there exists an action a with V subset R_a(d).
```

So the existing active-learning literature already tells us not to optimize
hidden-cause identity when the decision is coarser.

**Adopt:** overlapping decision regions, not an arbitrary operator label, are the
correct object for R0D and other active-diagnosis lanes.

**Correction to earlier OCM wording:** with non-unique acceptable/optimal actions
there need not be one canonical equivalence relation over states.  Overlapping
regions are the safer primitive.  Two distinct traps matter:

```text
A1={a}, A2={a,b}, A3={b}
```

shows that "shares some optimal action" is not transitive, while

```text
A1={a,b}, A2={b,c}, A3={c,a}
```

shows that pairwise overlap does not imply that a whole fiber has one common
action.  The exact representation condition is therefore a **fiber-wide
intersection**, not pairwise similarity.

Primary parents:

- D. Golovin, A. Krause, D. Ray, "Near-Optimal Bayesian Active Learning with
  Noisy Observations," NeurIPS 2010.  Introduces Equivalence Class Determination
  / EC2 with nonuniform test costs and correlated noise.
- S. Javdani, Y. Chen, A. Karbasi, A. Krause, J. A. Bagnell, S. Srinivasa,
  "Near Optimal Bayesian Active Learning for Decision Making," AISTATS 2014,
  PMLR 33:430--438.  Introduces overlapping Decision Region Determination.
- Y. Chen et al., "Submodular Surrogates for Value of Information," AAAI 2015,
  DOI 10.1609/aaai.v29i1.9694.
- S. Chen, A. Choi, A. Darwiche, "Value of Information Based on Decision
  Robustness," AAAI 2015, DOI 10.1609/aaai.v29i1.9684.

## 3. Blackwell--Le Cam comparison is more decision-relevant than generic MI

Blackwell compares experiments by the decision performance obtainable from their
observations.  A channel produced by garbling another observation cannot be more
informative in the Blackwell sense.  Le Cam/Torgersen deficiency asks how much
risk is lost when one experiment is used instead of another, and Torgersen
explicitly allows the comparison to be restricted to a relevant family of
decision problems.

This gives a mature language for the exact issue in #152:

```text
How much protected decision value is lost by restricting the machine to the
prospective observation channel phi(X), relative to full exposed state X?
```

Phase-2A's feature-conditional regret floor is one concrete finite Bayes-risk gap
for one frozen decision problem.  It should be interpreted as a decision-specific
information loss, not as a Shannon-information measurement.

**Adopt:** use Blackwell/deficiency-style decision comparisons when the question
is whether an observation channel is sufficient for action.  Keep mutual
information/Fano only when a precisely defined random target and bounded loss or
probe-information assumptions actually make an information-theoretic lower
bound appropriate.

Two simple counterexamples prevent overusing mutual information:

1. an observation may reveal an arbitrarily large hidden identity while every
   hidden state has the same optimal action; then decision value is zero;
2. with unbounded/scaled loss, an arbitrarily low-entropy rare state may have
   large economic value if observing it avoids a correspondingly large loss.

Primary parents:

- D. Blackwell, "Equivalent Comparisons of Experiments," *Annals of
  Mathematical Statistics* 24(2), 1953, 265--272. DOI
  10.1214/aoms/1177729032.
- E. Torgersen, *Comparison of Statistical Experiments*, Cambridge University
  Press, 1991.  Chapter 6 develops deficiency and relative deficiencies for
  restricted decision classes.
- J. Rauh et al., "Coarse-graining and the Blackwell Order," 2017,
  arXiv:1701.07602.  Useful warning that mutual-information order and Blackwell
  decision order are not equivalent.

## 4. Lifecycle-safe compression belongs to bisimulation / information-state theory

MDP model minimization and stochastic bisimulation already formalize when states
may be merged without changing downstream control.  Dean and Givan construct a
coarsest homogeneous refinement; Givan, Dean and Greig develop equivalence and
model minimization more fully.  Ferns, Panangaden and Precup give quantitative
bisimulation metrics related to value differences.  POMDP theory and later
information-state work make the same structural point from history compression:
a representation is sufficient when it preserves what is needed for immediate
reward/contract evaluation and for predicting/updating its own successor state.

**Adopt:** current-output equality is only a depth-zero relation.  A persistent
OCM policy needs a contract bisimulation/information-state condition over every
transition that can affect future protected value: support withdrawal,
revocation, reset, checkpoint, replay, fallback, authority and retained search
state.

A strong exact finite condition is:

```text
same admissible protected actions / immediate protected contract
+
same probability of moving into each equivalence class under every action.
```

Under that condition finite-horizon values are equal by induction.  This is the
proper parent for the earlier 2-current-answer / 4-future-lifecycle
counterexample.

Primary parents:

- T. Dean and R. Givan, "Model Minimization in Markov Decision Processes,"
  AAAI 1997.
- R. Givan, T. Dean, M. Greig, "Equivalence Notions and Model Minimization in
  Markov Decision Processes," *Artificial Intelligence* 147 (2003), 163--223.
  DOI 10.1016/S0004-3702(02)00376-4.
- N. Ferns, P. Panangaden, D. Precup, "Metrics for Finite Markov Decision
  Processes," UAI 2004.
- L. Li, T. Walsh, M. Littman, "Towards a Unified Theory of State Abstraction
  for MDPs," 2006.
- R. Smallwood and E. Sondik, "The Optimal Control of Partially Observable
  Markov Processes over a Finite Horizon," *Operations Research* 21(5), 1973,
  1071--1088. DOI 10.1287/opre.21.5.1071.
- J. Subramanian, A. Sinha, R. Seraj, A. Mahajan, "Approximate Information State
  for Approximate Planning and Reinforcement Learning in Partially Observed
  Systems," 2020, arXiv:2010.08843.

## 5. R0B unknown lifetime is an online investment problem before it is ML

Classical ski rental is only the two-option edge case.  Multislope ski rental
allows several options with increasing setup cost and decreasing recurring
rental rate.  Online capital investment is even closer conceptually: investment
opportunities arrive over time, each capital expense lowers future production
cost, and both future demand and future investment opportunities may be unknown.

This is a much better parent for reusable machine cognition than "predict the
best algorithm" when the main unknown is how long the state will be reused.

**Adopt:** before per-query learning, try to reduce R0B to an ordinary online
investment problem and use competitive-analysis parents.

**Do not overclaim an exact reduction yet.**  Current R0B has target-dependent
costs `R(q), I(q), K(q)`.  Ordinary multislope ski rental has a fixed recurring
rate per slope.  An exact expected-cost reduction is available only after we
freeze a demand model and a restricted prebuild/fallback policy for which:

```text
setup b_f = B(f)
recurring r_f = E_q[cost of answering q at fixed frontier f]
```

with investment decisions not allowed to see future targets, and with slopes
ordered so larger setup buys weakly lower recurring expected cost.  If those
conditions fail, the stronger parent is finite-state online control/capital
investment, not a forced ski-rental analogy.

Primary parents:

- Y. Azar, Y. Bartal, E. Feuerstein, A. Fiat, S. Leonardi, A. Rosén,
  "On Capital Investment," *Algorithmica* 25(1), 1999, 22--36. DOI
  10.1007/PL00009281.
- Z. Lotker, B. Patt-Shamir, D. Rawitz, "Rent, Lease or Buy: Randomized
  Algorithms for Multislope Ski Rental," STACS 2008; later *SIAM Journal on
  Discrete Mathematics* 26(2), 718--736. DOI 10.1137/100794018.

## 6. Misspecification is a representation/authority boundary, not confidence

Berk's classical misspecification result and Kleijn--van der Vaart's later theory
show that Bayesian concentration under a wrong model class is concentration on
an in-class/asymptotic or KL-best surrogate, not proof that the true data
mechanism belongs to the class.  SafeBayes is further evidence that ordinary
Bayesian behavior can be problematic under misspecification.  Agnostic active
learning removes realizability for the goal of finding a best-in-class
predictor, but that still does not certify that the class contains the protected
truth or a safe action.

**Adopt:** separate predictive best-in-class performance from authority.  A
statistical policy may prioritize exact work, but protected action requires a
coverage/adequacy argument or an independent fail-closed checker/abstention
boundary.

Primary parents:

- R. Berk, "Limiting Behavior of Posterior Distributions when the Model is
  Incorrect," *Annals of Mathematical Statistics* 37(1), 1966, 51--58. DOI
  10.1214/aoms/1177699597.
- B. Kleijn and A. van der Vaart, "Misspecification in Infinite-Dimensional
  Bayesian Statistics," *Annals of Statistics* 34(2), 2006.
- P. Grünwald and T. van Ommen, "Inconsistency of Bayesian Inference for
  Misspecified Linear Models, and a Proposal for Repairing It," *Bayesian
  Analysis* 12(4), 2017, 1069--1103. DOI 10.1214/17-BA1085.
- M.-F. Balcan, A. Beygelzimer, J. Langford, "Agnostic Active Learning,"
  ICML 2006 / *JCSS* 75(1), 2009, 78--89.
- R. Gelbhart and R. El-Yaniv, "The Relationship Between Agnostic Selective
  Classification, Active Learning and the Disagreement Coefficient," JMLR 20,
  2019.

## 7. Ordinary algorithm selection is the parent if a payable residual survives

Rice's algorithm-selection framework already separates problem space, feature
space, algorithm space and performance space.  Modern per-instance algorithm
selection (for example SATzilla and ASlib-era work) adds learned selectors, but
its prerequisite is exactly the one #152 now enforces: informative **cheap**
features and a real distribution of instances on which algorithms have
meaningfully different performance.

**Adopt:** if exact stopping, online investment and finite metareasoning leave a
nontrivial residual, the next parent is ordinary algorithm selection.  A tiny
MLP is not a scientific category; it is one implementation candidate after
feature cost, inference cost, training, update, storage and lifecycle cost are
included.

Primary parent:

- J. Rice, "The Algorithm Selection Problem," *Advances in Computers* 15,
  1976, 65--118. DOI 10.1016/S0065-2458(08)60520-3.

## 8. Resulting synthesis: use the smallest mature parent that owns each gap

The literature does not collapse all OCM questions into one heuristic.  It gives
an ordered set of different mathematical objects:

```text
Need only a safe common action?
  -> Decision Region Determination / ECD

Need to decide whether another computation is worth buying?
  -> rational metareasoning / value of computation / DP

Need to compare observation channels for protected decisions?
  -> Blackwell / Le Cam / decision-relative deficiency

Need a persistent compressed state with future-equivalent behavior?
  -> bisimulation / information state

Need to invest under unknown reuse horizon?
  -> online capital investment / multislope ski rental when reducible

Need a predictor after all exact parents leave residual?
  -> ordinary algorithm selection

Truth may be outside the represented class?
  -> misspecification + abstention/checker/coverage boundary
```

This parent map changes the research programme in an important way: many things
previously described as possible "machine epistemics" mechanisms are already
well-studied conventional parents.  That is useful.  We can adopt them and ask a
narrower systems question:

> Can one persistent machine maintain a legally observable, lifecycle-sufficient
> decision state and select/stop/invest with lower **total protected resource
> cost** across heterogeneous tasks, while exact authority, provenance,
> revocation and replay remain intact?

The next experiments should therefore test reductions and accounting, not invent
new router architectures.