# AJ7 — requirements/value are an independent provenance branch

## 1. No-go: dynamics do not determine a unique objective

Let the frozen process world contain one state `s` and two actions `a0,a1`, with identical dynamics

`P(s | s,a0) = P(s | s,a1) = 1`.

Define one reward/requirement relation preferring `a0` and another preferring `a1`. The physical/computational transition law is identical while the optimal action sets are disjoint. Therefore:

`world dynamics alone ->/ unique objective / requirement / normative ordering`.

The checker strengthens the witness by exhausting all nine reward pairs `(r(a0),r(a1))` over `{0,1,2}`. The same dynamics support three distinct optimal-action sets `{a0}`, `{a1}`, and `{a0,a1}`, each for three rewards; nine unordered reward pairs have disjoint optimal-action sets.

This is a simple deductive underdetermination theorem, not a claim that values can never have causal histories in physical systems.

## 2. Objective-source provenance is separate from process/information provenance

Register an objective provenance record

`Pi_Q = (source_type, source_instance, transformation_history, effective_Q, evidence, authority_scope)`.

At minimum distinguish:

- `DISTAL_VIABILITY`: evolutionary/selection/continued-existence pressures;
- `INTERNAL_DRIVE`: endogenous reward, preference or control signal implemented in the machine;
- `EXTERNAL_SPECIFICATION`: scientist/user/designer task, utility, verifier or formal specification;
- `SOCIAL_INSTITUTIONAL`: requirements imposed by other agents, institutions or collective processes;
- `EFFECTIVE_Q`: the downstream requirement family actually used in a GMI decision/capability statement.

These layers need not coincide. The same `effective_Q` can be produced by multiple source types, and a single source can be transformed into different downstream requirements.

Machine/process provenance such as `(substrate, organization, development history, external data channels)` cannot silently fill a missing objective-source record. Conversely, an objective provenance record does not establish that the machine has learned or internally endorsed the requirement.

## 3. Reward/goal identifiability parent boundary

The stronger observational statement is already parent mathematics. In inverse reinforcement learning and reward learning, multiple rewards can be compatible with the same observed policy/behaviour; reward functions are generally only partially identifiable without additional assumptions/data. Policy-invariant reward transformations are another classical source of ambiguity.

AJ7 therefore does not claim novelty for IRL reward ambiguity. It uses that literature as a stronger parent for the epistemic statement

`behaviour ->/ unique latent reward`.

The new placement needed by the GMI spine is narrower: **even before inference from behaviour, the operational world law itself does not supply a unique normative objective.** Objective-source assumptions must enter explicitly or be derived from a separately declared selection/viability/social model.

## 4. What may be derived

A particular objective can be derived conditionally from additional premises, for example:

- a frozen external specification;
- a declared viability functional;
- an internal reward circuit and its update rules;
- a social choice/governance process;
- an evolutionary model plus an explicitly defined fitness/continuation criterion.

But then the conclusion is relative to those premises. It is forbidden to erase them and report the objective as a consequence of world dynamics alone.

## 5. Connection to AJ3/AJ6

AJ3 determines which distinctions are physically/operationally accessible and which matter **after** a requirement family is registered. AJ6 determines developmental reach under a `Sigma` that includes ecology/evaluator context. AJ7 supplies the independent provenance branch explaining where the effective `Q`/utility/verifier ordering came from.

Thus the spine has two inputs that must remain distinct:

`what can happen` — operational/substrate/process law;

`what counts as success` — requirement/value provenance.

## Strongest parents

- inverse reinforcement learning / reward learning identifiability and ambiguity;
- Ng–Harada–Russell policy invariance under reward transformations;
- modern partial-identifiability analyses such as Skalse et al.;
- classical decision/utility theory for conditional choice once preferences/utilities are supplied.

These parents own their exact reward-identifiability and invariance theorems.

## Claim ceiling

`AJ7_OBJECTIVE_UNDERDETERMINATION_AND_SOURCE_PROVENANCE_AT_REGISTERED_FINITE_SCOPE`

Forbidden: `OBJECTIVE_DERIVED_FROM_DYNAMICS_ALONE`, `OBSERVED_POLICY_IDENTIFIES_UNIQUE_REWARD`, `EFFECTIVE_Q_IDENTIFIES_ITS_SOURCE`, `PHYSICS_SUPPLIES_UNIQUE_NORMATIVE_ORDER`.
