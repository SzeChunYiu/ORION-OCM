# Learning fixed-rule supports for governed repair

**Preliminary internal manuscript — exploratory research, not submission ready.**
Human authors, affiliations, funding and archive information have not been
provided. This draft separates formal reconstruction, exhaustive finite
verification, prior development evidence and the frozen support-learning census.

## Abstract

Persistent learning systems must determine when withdrawing evidence invalidates
an acquired method. Individual deletion tests can miss redundant supports,
whereas indiscriminate invalidation can discard methods that remain justified.
We formulate a narrow learning target: whether a fixed, exactly identified rule
would still be selected from a subset of its original evidence. For a finite
hypothesis language, a fixed preference order and conjunctive consistency,
retention of a rule consistent with the full evidence is monotone. We connect
this elementary property to an actual periodic-rule induction implementation
and to established alternative-support representations. Independent finite
checks examine conservative effect sets, decision sufficiency, support representation
and deletion lifecycle equivalence. In an actual-source census, learned monotone
and antichain representations correctly answered all 256 fixed-rule retention
queries, whereas individual-deletion sensitivity failed on 15. The explicit
version-space learner used fewer source queries than the antichain parent but
more counted operations: 436,199 versus 146,401. Acquired support generalization
survived serialized-state reload; removing it restored source-query costs. An
earlier dispatcher pilot selected two existing repairs but lacked a third
change and wall-time advantage. These results support bounded, parent-owned
repair learning, not a new primitive or general self-evolution mechanism.

## Introduction

Accumulated competence creates a revision problem. A method can remain correct
for an immediate task while losing the evidence or authority required for its
continued use. Conversely, withdrawing one observation need not invalidate a
method when alternative evidence supports the same result. A persistent system
must distinguish these cases while paying for discovery, checking, storage and
future maintenance.

Version spaces retain hypotheses
consistent with observations, while assumption-based truth maintenance represents
alternative assumption environments supporting conclusions. Neither maintaining
a hypothesis set nor storing alternative supports is itself a new cognitive
operation. [Mitchell](https://www.ijcai.org/Proceedings/77-1/Papers/048.pdf),
[de Kleer](https://dekleer.org/Publications/An%20Assumption-Based%20TMS.pdf).

Likewise, a learner need not identify a complete hidden structure before making
an acceptable decision. Decision-region determination already studies tests
that place every remaining hypothesis within a region permitting a common
decision; its regions may overlap. This is the direct parent of the
decision-sufficiency formulation used here. The open engineering question is
whether a machine can acquire the relevant decision and lifecycle constraints
economically, rather than receiving them as a supplied table.
[Javdani et al.](https://arxiv.org/abs/1402.5886).

We focus on fixed-rule retention because its semantics can be made exact. The
target is a Boolean predicate over original evidence subsets: does the specified
inducer return the same rule representation? This differs from identifying the
replacement rule, recovering every causal dependency, or proving that an
extrapolation remains universally correct. Those broader tasks require additional
observations and contracts.

We ask whether learning this retention
predicate improves revision decisions relative to equally informed conventional
parents, once acquisition and maintenance are charged. The current contribution
is a source-specific formal mapping, finite reconstruction checks and an exposed
support-learning census. Original algorithmic novelty and a general empirical
advantage are not established.

## Results

### A fixed-rule retention property in the source learner

Let a finite rule language have a data-independent strict preference order.
The learner selects its first rule consistent with every supplied observation.
Fix a rule that is consistent with the complete original evidence. If this rule
is selected from one subset, adding more original evidence cannot remove it:
the rule remains consistent, and a preferred competitor already excluded by an
observation cannot become consistent when additional constraints are added.
Thus its retention predicate is monotone.

The investigated source implements periodic Grundy rules using a bounded
preperiod, period and value table. Induction minimizes a fixed description-length
score, resolves shape ties by period then preperiod, and fills unconstrained
table entries with zero. These operations implement a fixed preference over a
finite language. Evidence blocks are combined by sorted, deduplicated union.
The retained identity is the full `(preperiod, period, values)` representation.
The argument does not cover data-dependent hypothesis generation, changing
ranking, inconsistent full evidence or arbitrary replacement-rule identity.

For a monotone retention predicate, minimal sufficient evidence subsets provide
a complete alternative-support representation: a live subset retains the rule
exactly when it contains one minimal support. This is the established antichain
representation underlying the comparison, not a new epistemic object. Explicit
antichains can grow combinatorially; compactness and useful acquisition cannot
be assumed from monotonicity alone.

### Finite verification separates decisions, structure and lifecycle

Two independently implemented algorithms agreed across 87,808 finite
decision systems combining three hypotheses, three non-abstaining actions,
two binary probes and positive probe costs. Explicit action-labelled trees
and version-space dynamic programming returned the same optimal worst-case
probe cost and feasibility. In 40,000 configurations an acceptable decision
was possible without complete model identification. These are census counts
in a supplied finite universe, not frequencies of successful machine learning.

The support checks covered all 20 monotone Boolean predicates on three evidence
variables. Eleven had a relevant variable missed by individual deletion from
the fully live state. For example, either of two observations can independently
support a rule: deleting either alone changes nothing, while deleting both
removes support. The result demonstrates the inadequacy of that particular
discovery procedure; it does not imply that alternative supports are generally
expensive or that all pairwise interventions fail.

Lifecycle checks further distinguished immediate answers from future revision
behavior. A deletion-only system with 160 states and 480 transitions had two
immediate-answer classes but 20 continuation-equivalence classes. Independent
partition refinement and complete deletion-subset signatures agreed. Restoration,
new evidence and authority-changing transitions were outside this alphabet.
These checks validate finite constructions, not external-model realizability
or learning efficacy.

### Learned supports restore exact retention, with a parent cost advantage

The source and registration were published before execution. The census covers
16 original development method occurrences, each with four supplied evidence
blocks and all 16 masks. Source induction and its independent scorer agreed; no
monotonicity violation occurred. Correctness concerns exact baseline-rule
retention, not future-game accuracy. Counted operations are a registered proxy
combining learner steps, observation reads and shape checks.

| Arm | Correct retention answers | Source queries | Counted operations |
|---|---:|---:|---:|
| Active monotone version space | 256/256 | 133 | 436,199 |
| Antichain parent | 256/256 | 164 | 146,401 |
| Exhaustive table | 256/256 | 256 | 165,538 |
| Lazy reinduction/cache | 256/256 | 256 | 163,066 |
| Individual-deletion ablation | 241/256 | 80 | 75,262 |

All 15 ablation errors falsely retained the baseline rule. The active and
antichain learners generalized correctly to 123 and 92 masks unqueried at
restart, respectively, without additional source calls. Removing extrapolation
while retaining acquired observations required exactly 123 and 92 source
queries. Acquired constraints therefore supplied information beyond an exact
cache within these given block universes.

Fewer probes did not mean cheaper learning. Active version-space construction
alone used 232,334 learner operations. The antichain parent used the fewest
counted operations among correct arms; active learning used fewer queries.
Lazy caching had smaller acquisition checkpoints, but service-time additions
were not repersisted, preventing a final-storage comparison. Process timings
include recording, removal audits and scoring, not deployment advantage.

The active learner identifies the complete four-bit retention function. This
study does not test decision-region early stopping, hidden grouping discovery,
arbitrary replacement-rule learning or a new OCM generation.

### Prior governed-repair evidence provides context and limits

An earlier development pilot connected measured component alternatives to the
OCM M11 proposal, shadow-check, external-adoption, restart and rollback APIs.
The controller selected two existing dispatcher changes: a relevance index and
lazy dependency processing. A third cycle found no candidate satisfying its
registered improvement requirement. The available alternatives and incident
sequence were supplied; the machine selected configurations from measurements.

That pilot spent 686,855 counted work units during development. A separately
frozen 24-episode continuation first repaid this expenditure at episode 12.
Including development, evolved work was 1,024,703 units versus 2,613,144 for the
initial dispatcher, a 60.8% reduction in that accounting model. Complete
five-revision episodes were exact in 24/24 evolved cases and 0/24 initial cases;
the latter does not mean every individual revision failed. Wall time including
development was 4.46 s versus 4.22 s: no wall-time advantage was demonstrated.

A conventional finite search over the same alternatives implements the
controller. Its mechanism is therefore parent-sufficient by construction.
Only the dispatcher configuration and M11 history persisted; donor fields and
libraries were reconstructed per task. These findings establish bounded
engineering adaptation, not discovery of a factorization, learned proposal
generation or a persistent whole-field self-evolution mechanism.

## Methods

### Formal scope and conservative decisions

Models predict the outcomes of declared probes and lifecycle effects of
registered actions. A version space retains models consistent with live,
scope-compatible evidence. Soundness requires the true model to lie in the
language and observations to be valid. A nonempty version space does not verify
these assumptions; an empty one causes refutation or refusal, not vacuous
authorization.

The union of surviving models' affected-obligation sets is the least
conservative footprint in the full powerset of fixed external obligations.
This is not the cheapest executable repair plan: boundary reads, shared checks
and authority conditions can require additional work. An action is robustly
acceptable when it meets the declared requirements in every surviving model.
External authority receipts remain necessary; a prediction cannot authorize
itself.

The exact probe recurrence assumes finite, deterministic, noiseless, resettable
tests. It minimizes worst-case physical probe expenditure, not the computation
needed to build an optimal policy. State-changing probes require expanded
state semantics. With material final-repair costs, stopping at the first common
acceptable action need not minimize total expense. No noisy-test guarantee is
inherited without the corresponding assumptions and algorithmic comparison.
[Golovin, Krause and Ray](https://arxiv.org/abs/1010.3091).

### Source study, comparators and preservation

The support study uses pinned development source rather than protected programme
outcomes. Four-block membership and the monotone hypothesis class are declared
information gifts. Baseline consistency is checked and charged. Semantic
identities bind source, language, evidence and exact baseline representation;
renaming a mask does not create a fresh task.

Each arm runs separately; learner restart reconstructs serialized state within
that process. Learners persist before service queries. The removal comparison
retains acquired observations and removes extrapolation, allowing an exact
fallback rather than erasing all useful memory. An independent scorer evaluates
the full mask universe after arm-local acquisition and prediction. Its result
table is unavailable to the learner. This scorer checks the registered
implementation and scope, not an independently discovered model of cognition.
The support learner is a separate adapter; this study does not demonstrate a
new M11 adoption or transfer of epistemic authority.

### Resource and evidence accounting

Results retain source counters, wall and process CPU time, storage, restart and
scoring overhead separately. The earlier pilot's source work counter excludes
common donor catalogue construction and M11 host operations; their effects
remain in wall/storage receipts. Counted-work payback therefore does not imply
repayment of every computational cost. Preservation failures cannot be traded
for speed through a favorable weighted score.

Exact enumerations require no invented population confidence interval. The
development families, masks and nested continuation episodes are not independent
domain replications. Support outcomes have their own frozen source,
registration and raw receipts. Neither a local pre-outcome freeze nor several
AI-assisted checks converts exposed development evidence into confirmatory or
external replication.

## Discussion

The useful distinction is between learning a complete internal account and
learning a justified answer to a particular repair question. Decision-region
determination supplies the general decision principle. Fixed-rule retention
provides a narrower, executable target whose monotonicity can be justified for
the investigated source. Alternative supports then become an acquired object
with explicit scope, rather than an assumed complete dependency graph.

The candidate blocks are supplied, so success
would not demonstrate hidden dependency discovery. Retaining a baseline rule
does not identify a correct replacement or establish its extrapolation validity.
Complete support learning may cost more than lazy reinduction over short
lifetimes. Even accurate local structure can lose its advantage after validation,
storage or drift handling. The previous pilot's negative wall-time result shows
why an operation-count improvement alone is insufficient for a whole-system
claim.

The antichain parent's lower counted cost supports adoption with parent
sufficiency. Explicit version-space overhead is an engineering bottleneck, not
evidence against all active-learning methods. A residual claim requires
fresh consequence prediction, complete resource accounting, functional removal
and disjoint replication under matched information. Broader operator learning,
equational abstraction and cost-aware routing remain separate research targets;
adding their names cannot enlarge the present evidence.

This preliminary study is therefore a bounded methods and falsification effort.
It does not establish a universal operator basis, general cognitive superiority,
autonomous invention or readiness for a flagship journal submission.

## Availability and declarations

Formal statements, exact-check source/results and the preliminary support
implementation are in `research/cognitive-learning-theory-v1/`. Prior pilot
registrations, source manifests, raw trajectories and M11 receipts are in
`research/self-evolution-v1/`. Support-study source freeze:
[`613ac75492734c5f2a239673759ffd2b20a637c6`](https://github.com/SzeChunYiu/ORION-OCM/commit/613ac75492734c5f2a239673759ffd2b20a637c6).
The [registration](SUPPORT_DEVELOPMENT_REGISTRATION_V1.json) SHA256 is
`651ea38bc2d619decece6b1bd0148e53ececee3e8024a1b1a78a0519bbaa86f6`.
[Summary and per-arm raw receipts](results/support-development-v1/) retain
all outcomes and resource coordinates. A persistent archive identifier, complete
license/environment audit and clean-host reproduction remain unprovided.

Human author responsibility, contributions, affiliations, funding and competing
interest declarations must be supplied by the accountable researchers. AI
sessions materially assisted formalization, implementation, analysis and this
draft. Their internal reviews are not external peer review; the eventual
disclosure and all manuscript claims require human verification and approval.
