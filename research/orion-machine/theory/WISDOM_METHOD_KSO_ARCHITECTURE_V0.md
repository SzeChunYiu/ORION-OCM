# Wisdom + Method KSO Architecture V0

**State date:** 2026-09-04  
**Status:** prospective architecture + finite executable calibration.  
**Authority:** no claim that proverbs are universal truth, that cultural wisdom is reducible to rules, or that the resulting method-space is novel.

## 1. Motivation

Speaking is not merely surface generation. In OCM it should normally be the **externalization of an internal cognitive trajectory**. A useful answer may therefore depend on factual knowledge, procedures, goals, social context, uncertainty, values/heuristics, and the selected problem-solving method before language realization begins.

The Chinese-classics collection linked by the operator is useful because compact sayings often behave like **compressed decision structures** rather than ordinary facts. They can encode heuristics such as epistemic humility, perseverance, restraint, reciprocity, diligence, or perspective shifts. Similar compact forms occur in many cultures through proverbs, maxims, parables, aphorisms, cases, and teaching stories.

The architecture must preserve an important distinction:

```text
famous saying != universal truth
memorized proverb != understood principle
principle != executable method
successful method != authority outside its scope
```

Research on multilingual proverb reasoning supports this separation: systems can memorize sayings yet fail to apply them correctly in conversational context, and cultural transfer can fail even when literal translation is available. Cross-cultural proverb research also finds overlapping functions with culturally different pragmatic emphases.

## 2. Four distinct objects

### 2.1 Quotation / CulturalArtifact

A linguistic/historical object.

```text
CulturalArtifact.v1
  artifact_id
  source/culture/language/period
  original_text
  translations
  provenance/evidence
  genre: proverb | maxim | parable | quotation | case | story | ...
```

It is preserved even if every current interpretation is later rejected.

### 2.2 Interpretation

One context-bound reading of an artifact.

```text
Interpretation.v1
  artifact_id
  interpretation_id
  proposition / lesson candidate
  context
  assumptions
  intended speech act / pragmatic function
  supporting commentary/evidence
  alternative interpretations
  counterevidence
```

One quotation may legitimately have several interpretations. The KSO must not collapse them by majority vote.

### 2.3 PrincipleCapsule

A reusable, defeasible reasoning heuristic induced from one or more interpretations, cases, demonstrations, experiments, or lessons.

```text
PrincipleCapsule.v1
  principle_id
  name
  trigger / applicability conditions
  recommended cognitive/action bias
  intended objective
  known benefits
  known harms / counterexamples
  cultural/historical provenance
  supporting artifacts + cases
  conflicting principles
  warrant + scope
  transfer history
  revision lineage
```

Examples of *types* of principles include:

- epistemic humility: distinguish known / unknown / unverified;
- perseverance: continue when progress remains plausible and costs are acceptable;
- stopping/restraint: stop/escalate when marginal continuation is harmful or evidence is exhausted;
- reciprocity / gratitude;
- perspective-taking;
- diligence/practice;
- smallest sufficient intervention;
- seek disconfirming evidence.

These are not constitutional moral truths. They are candidate decision structures whose applicability must be learned and tested.

### 2.4 MethodCapsule

An executable way of solving a family of problems.

```text
MethodCapsule.v1
  method_id
  task/interface signature
  preconditions
  decomposition / control structure
  operators/tools
  expected effects
  termination/stop condition
  verifier
  resource profile
  warrant/scope
  failure modes
  related principles
  transfer/adapters
  dependencies
  revision lineage
```

A method may be symbolic, neural, procedural code, search policy, hybrid controller, or external-tool workflow. OCM constrains its observable contract, not its internal representation.

## 3. From wisdom to thought to speech

The generation path is therefore not

```text
input text -> likely next text
```

but can be

```text
situation/task
 -> task model + relevant knowledge
 -> candidate methods
 -> relevant principles / constraints
 -> simulate/evaluate alternatives
 -> choose/revise method
 -> derive conclusion/action
 -> communicative intent
 -> language plan
 -> utterance
```

A proverb may enter this path as a retrieved CulturalArtifact, but only a context-compatible live Interpretation/Principle may influence the method choice.

Example:

- `知之為知之，不知為不知，是知也` can support an epistemic-humility principle: unknown remains unknown; do not manufacture certainty.
- `百尺竿頭更進一步` can support a perseverance principle: prior success does not imply the search should stop.

These principles can conflict in a task where further action is expensive and evidence is weak. The system must evaluate applicability, cost, risk, authority, and expected information gain; it cannot choose by quotation popularity.

## 4. Wisdom KSO topology

A provisional recursive picture:

```text
Wisdom
  -> Chinese classical traditions
      -> epistemic conduct
      -> learning/diligence
      -> social relations
      -> governance
      -> resilience/change
  -> Indian traditions
  -> Greek/Roman traditions
  -> Islamic traditions
  -> African traditions
  -> European folk traditions
  -> Indigenous traditions
  -> modern scientific/professional heuristics
  -> cross-cultural correspondences / conflicts
```

This is **not** a final civilization taxonomy. One principle can have many parents, and multiple cultures may independently instantiate related or conflicting heuristics. Topology should ultimately be learned from explanatory/transfer value, not imposed as a world hierarchy.

## 5. Method KSO: the space of ways to solve problems

The Method KSO is more important than a flat tool library.

Let methods be nodes/hypernodes with relations such as:

```text
SPECIALIZES
GENERALIZES
DECOMPOSES_TO
COMPOSES_WITH
REQUIRES
PRODUCES
VERIFIES
ALTERNATIVE_TO
DOMINATES_UNDER
FAILS_UNDER
TRANSFERS_TO
ADAPTS_VIA
CONFLICTS_WITH
LEARNED_FROM
REVISED_BY
```

For task contract `τ`, the machine should construct a query-relative method subspace

`M(τ) ⊂ MethodKSO`

then solve a constrained selection/composition problem rather than retrieving one similar method.

The selected program may be

`m* = m_k ∘ ... ∘ m_2 ∘ m_1`

with each composition checking interface, warrant, resources, authority, and applicability.

## 6. General weak methods and compiled strong methods

Old cognitive-architecture work already studies a useful parent idea: solve unfamiliar problems with weak/general methods, then compile repeated successful traces into stronger domain-specific skills. DreamCoder/LAPS and modern agent-skill systems similarly learn reusable libraries and search/control structure. Recent agent work also shows that subtask-level skills can transfer better than whole-task skills and that harmful transfer is common.

OCM should therefore maintain at least two levels:

```text
WeakMethod
  broad applicability
  higher search/reasoning cost
  e.g. decomposition, means-ends search, hypothesis-test, enumerate-and-check

CompiledMethod
  narrower applicability
  lower execution cost
  learned from successful/failed episodes and verified transfer
```

A CompiledMethod is not promoted merely because its source episode succeeded.

## 7. Principle-guided method selection

Principles should mostly act as **biases/constraints on cognitive control**, not as direct answer generators.

For task `τ`, method `m`, and principle set `P`:

`Score(m | τ, P)` may depend on:

- task/interface compatibility;
- estimated success;
- expected information gain;
- cost/risk;
- prior transfer performance;
- negative-transfer evidence;
- authority constraints;
- principle compatibility.

Hard constitutional constraints remain outside this score and cannot be outweighed.

Example:

```text
principle: EPISTEMIC_HUMILITY
  -> penalize methods that require unsupported assumptions
  -> prefer CANNOT_CHECK over fabricated closure

principle: PERSEVERANCE
  -> resist premature stopping while a valid information-acquisition action remains

principle: RESTRAINT
  -> stop/escalate when continuation has low decision value or excessive risk
```

The last two can conflict. OCM should preserve the conflict and resolve it from the task state rather than declaring one proverb globally correct.

## 8. Wisdom acquisition channels

A cultural-wisdom item can be learned from:

1. original text / historical source;
2. scholarly commentary;
3. explicit teacher explanation;
4. aligned situation -> saying demonstrations;
5. stories/cases showing success and failure;
6. cross-cultural analogues;
7. real interaction/experience;
8. hostile counterexamples.

Raw quotation text can warrant the existence/form of the artifact, but not by itself the universal validity of the derived principle.

## 9. Stress tests

### Wisdom understanding

- same proverb, different contexts -> different applicability;
- same quote, multiple historically plausible interpretations -> preserve plurality;
- two cultures with analogous sayings -> transfer only the common structure;
- translated proverb with lost pragmatic force -> detect/retain mismatch;
- proverb memorized but contextually wrong -> reject application;
- counterexample -> narrow principle scope;
- revoked source/interpretation -> reopen dependent principle/method choices.

The MAPS multilingual proverb benchmark is a useful parent diagnostic because it tests proverb application in conversational context rather than only recognition.

### Method space

- identical problem/new instance -> reuse;
- changed parameters -> adapt;
- shared subproblem -> partial transfer;
- superficially similar task -> refuse harmful transfer;
- two methods must compose -> verify interfaces;
- method fails -> diagnose whether problem is parameter, operator, representation, router, or evidence;
- no existing method applies -> weak-method search / learn / Jump;
- representation ceiling -> governed Jump;
- evidence supporting a method revoked -> dependent methods reopen;
- environment drift -> revalidate.

## 10. Self-ORION / method of methods

Eventually one region of the Method KSO contains methods for:

- learning methods;
- choosing methods;
- evaluating transfer;
- discovering representations;
- consolidating skills;
- diagnosing failures;
- redesigning the Method KSO itself.

This is the modern place for the old `ORION of ORION` idea.

The recursion is:

`method -> method-learning method -> method-learning-policy -> representation/topology learning -> cognitive-architecture learning`.

As always, OCM may propose modifications to its own cognitive machinery but cannot authorize its own constitutional/evaluation changes.

## 11. Immediate implementation target

Finite V0 should demonstrate:

1. artifacts and interpretations are separate;
2. principles are scoped/defeasible;
3. conflicting principles remain simultaneously live;
4. task context selects different principles;
5. principle choice biases method selection but does not directly mint task answers;
6. methods compose through typed pre/postconditions;
7. harmful transfer is explicitly penalized/refused;
8. revocation of interpretation evidence disables only dependent principles/method decisions;
9. unrelated cultural/technical knowledge remains live;
10. one thought trace is rendered into language only after method selection.

## 12. Parent subtraction / non-consequences

Parent areas include cognitive production systems/skill compilation, case-based reasoning, program/library learning, hierarchical skills/options, agent skill libraries, decision theory, argumentation, defeasible logic, knowledge graphs, cultural/proverb reasoning, pragmatics, moral/value learning, and cognitive architectures.

Therefore this architecture does not claim novelty for:

- storing proverbs;
- representing defeasible rules;
- hierarchical skill libraries;
- program composition;
- using values/heuristics in decisions;
- learning reusable procedures from experience.

The candidate ORION residual, if any, is their coupling inside a recursive warranted KSO with exact revocation, scoped cultural interpretation, cross-domain transfer, governed representation change, and one self-extending method ecology.
