# Formal learning and memory theory V1 — LMT-1–8

Status: **CORRECTED DEFINITIONS + CONDITIONAL THEOREMS**, 2026-09-13.

This repairs the learning/memory contribution at PR568 commit
6e879c5f7c0fa59e8bdded6dcb1b67d16a86d5ac. It retains the declaration
\(\mathcal G=(\mathcal I,\mathcal E,\mathcal O,\mathcal R,\mathcal D)\)
from MINIMAL_AXIOM_FREEZE_V1.md. It does not alter existing frozen formal,
semantic-state or reuse/invalidation evidence.

The detailed proof modules are:

- [Risk, one-sided regret and proper fixed-class PAC](LEARNING_RISK_AND_REGRET_V1.md):
  LMT-1, LMT-3 and their countermodels.
- [Complete-view identification and forgetting](LEARNING_IDENTIFIABILITY_V1.md):
  LMT-5 and LMT-7 with policy and continuation quantifiers.
- [Pinned repairs, parents and finite validation](LEARNING_MEMORY_REPAIR_CONTEXT_V1.md).

## Learning state

At development time \(t\), let \(X_t=(W_t,K_t,\Gamma_t)\): working state,
retained epistemic state, and provenance/dependency state. An admitted causal
update is \(X_{t+1}=U_t(X_t,Z_t,\xi_t)\), with \(U_t\in\mathcal D\).
Evidence acquisition, computation, storage and update costs belong in
\(\mathcal R\). A state change is not automatically learning.

Working state can contain information needed by a later decoder. A theorem
about \(K_t\) alone must either exclude that extra information or include it
in the complete declared decoder view. Calling information “private” or
“external” does not remove it from an identifiability argument.

## LMT-1 — different learning claims

For a fixed evaluation law and bounded measurable loss, PAC learning is a
high-probability comparison with a declared hypothesis family's population
risk. Online no regret is a one-sided comparison with the best fixed
comparator; outperforming it is permitted. Semantic consistency instead
requires convergence to an identifiable protected target. The detailed module
states the quantifiers and explains why these claims cannot be exchanged.

## LMT-2 — improvement

An evaluation improvement satisfies \(R_P(K')<R_P(K)\) for a fixed declared
population/interface. Other claims may use worst-case, Bayes or vector risk
if specified in the obligation. With resources, use either a jointly attained
Pareto improvement or a decrease in a declared scalar risk/resource objective.

Lower training loss, a larger state change or a new representation alone
does not prove improvement. The coordinatewise minima of attainable costs
\((1,3),(3,1)\) give \((1,1)\), which is not a jointly attainable design.

## LMT-3 — a known finite learner

The fixed-class proper ERM theorem and its approximate-optimization extension
are proved in LEARNING_RISK_AND_REGRET_V1.md. The hypothesis/loss family is
fixed before the scored iid sample; the returned hypothesis belongs to it.
Post-sample cardinality alone does not establish its uniform bound.

## LMT-4 — convergence is claim-specific

Distinguish risk consistency, one-sided no regret, semantic/parameter
consistency, and convergence of the retained state in a declared metric.
Two parameter states may implement the same answer, so state convergence is
not necessary for risk convergence. A constant misspecified state shows that
it is not sufficient for reaching the desired population risk.

A convergence theorem must identify its target, sampling/adversarial protocol,
capacity, exploration, optimization and resource premises. An expected-regret
claim must state its expectation convention explicitly. There is no inference
from repeated updating to identification, stationarity or eventual success.

## LMT-5 — impossibility without identifiable complete views

Equality of the joint complete view under a fixed learner and common terminal
decoder bounds its two-world success. Marginal observation equality does not
suffice, and a statement about every learner requires the corresponding
universal policy quantifier. LEARNING_IDENTIFIABILITY_V1.md gives the proof,
an abstention-safe bound and a private-action counterexample.

## LMT-6 — retained memory, revision and conflict

A retained claim may be represented by
\((statement,scope,status,evidence,parents,cost)\). Its dependency graph must
preserve protected source identities, distinguish retraction from replacement,
and reopen every conclusion requiring a revoked parent unless independently
supported. Rebuilding and reverification are charged. Incompatible claims
remain explicit conflicts until a declared resolution rule applies.

Recency alone is not a truth rule. Bayesian conditioning, statistical evidence
updates, AGM revision and truth maintenance have different premises.
This is the existing certified-reuse discipline applied to learning memory,
not a newly proved universal belief-revision algorithm.

## LMT-7 — forgetting under a complete continuation contract

Forgetting is a map \(F\) on retained states. A protected distortion condition,
such as \(\sup_{K\in S}d_Q(K,F(K))\le\varepsilon\), states behavioral safety
at the declared continuation interface. A resource improvement is a separate
condition for selecting that compression, not part of the distortion bound.

A collision prevents exact recovery of distinct unique answers only when
the complete later decoder views also coincide in law. Fresh revealing
observations can restore the distinction. The proof and constructive repair
are in LEARNING_IDENTIFIABILITY_V1.md.

## LMT-8 — failure taxonomy

| Failure | Missing condition | Concrete repair route |
| --- | --- | --- |
| Nonidentifiability | Complete views cannot distinguish the target | Intervene, change access, or retain an equivalence class |
| Misspecification | Admitted class cannot reach the required risk | Enlarge or change the realization class |
| Estimation error | Population uncertainty remains too large | Supply valid fresh evidence or a concentration contract |
| Optimization error | Empirical/objective solution remains inadequate | Improve optimization or use a stated approximation |
| Exploration failure | Relevant consequences are never observed | Use an admitted paid exploration policy |
| Drift | The claimed fixed law/target does not persist | Register a changing-target guarantee |
| Forgetting damage | A protected continuation loses necessary information | Retain it or reacquire it with charged access |
| Invalid revision | Revoked support still certifies a descendant | Reopen or rebuild its dependency proof |
| Resource infeasibility | Required execution cannot be afforded | Change the admitted representation or obligation |

These definitions and conditional repairs make claims precise. They establish
neither a new empirical learner nor universal convergence or physical adequacy.
