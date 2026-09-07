# ORION concepts in OCM: retain mechanisms, test their contribution

Assessment, 7 September 2026. This is a source and retained-evidence audit, not a new experiment.
OCM pin: `48e6035e5b55944110b200cd81a9bfdf37503a6c`.
ORION V1 pin: `adb97ecce7d8e1fe6effab456b98e653f401dae0`.
ORION V2 pin: `e71513744763b67a0df80ddd4c1bf4a11de62544`.

## Decision

Yes, several ideas are already used, but their presence exceeds their demonstrated benefit.
Keep task-local working views, checked abstraction, reusable subproblem solving, scoped
stopping/reopening and verified representation changes. Treat elaborate organisation and
activation dynamics as optional algorithms that must beat a strong simpler parent.
Ordinary OCM serving does not yet execute one learned fibre → saturation → recursion → Jump loop.
All future OCM cognition and learning must remain mechanical, without neural networks.

We first engineer OCM's initial cognitive machinery: problem representations, retrieval,
composition/search, checking and retention. Its own discovery then extends that machinery.
Older ORION ideas, including undeveloped ones, are an inspiration pool rather than a required
blueprint. Recover their mechanisms, combine them with strong external methods and compare
the resulting capability/cost tradeoffs. Record what we supplied and what OCM actually learned.
Self-discovery must be implemented and demonstrated; it cannot substitute for this initial design.

| Idea | What it should mean operationally | Current OCM evidence | Decision |
|---|---|---|---|
| Fibre | Retrieve a task-relevant view; cross scopes only under explicit correspondence; refine insufficient views. | Scope-based organisation is evaluated in M8, outside default solve/chat. It helps some synthetic cases and over-refuses in language. | Useful candidate, not a mandatory topology. Prefer an exact indexed flat view when it wins. |
| Saturation | Stop after complete registered closure, or report bounded search exhaustion; reopen when assumptions change. | Exact finite reachability and finite method-grammar exhaustion exist. Open-ended cognitive saturation is not established. | Essential distinction for sound stopping. A plateau cannot establish that no solution or idea exists. |
| Recursion | Decompose, solve subgoals, reuse checked results and propagate invalidation. | Recursive KSO reference has authored scopes/macros and revision tests. Finite fragment learning also exists separately. | Important mechanism; learned recursive organisation remains unproved. Avoid compulsory hierarchy. |
| Jump | Propose a new representation or operator, establish transport/preservation, independently check it and measure its benefit. | Finite ceiling demonstration succeeds with a supplied conjunction feature. Runtime records proposals with `adopted=False`. | Promising research organ; autonomous representation invention has not been demonstrated. |
| Dynamics | Allocate search effort or activation using an explicit policy whose cost is charged. | Default solve computes four dense exact restart fixed points. | Compare against exact retrieval and conventional search. Neither diffusion nor dynamical terminology establishes intelligence or speed. |

## “Fibre” currently names different things

1. V1's **development fibre** is a target-conditioned working view over questions, mechanics,
   failures and evidence. Co-retrieval supplies neither semantic compatibility nor authority.
2. An **observational fibre** is a set of states indistinguishable under an observation map.
   An answer is safe on the abstraction only if the answer is constant over that set.
3. OCM's **scope fibres** are overlapping local knowledge spaces with typed correspondences.

These can connect, but are not interchangeable. Each needs an explicit data structure,
interface and correctness condition. Category-theoretic language alone supplies none of these.
The practical objective is a small sufficient working view, not a prescribed fractal layout.
Sources: [V1 development fibre](https://github.com/SzeChunYiu/ORION/blob/adb97ecce7d8e1fe6effab456b98e653f401dae0/src/orion/self_orion/development_fibre.py),
[OCM recursive architecture](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/research/orion-machine/theory/RECURSIVE_KSO_ARCHITECTURE_V1.md),
[V2 finite safe quotient](https://github.com/SzeChunYiu/ORION-V2/blob/e71513744763b67a0df80ddd4c1bf4a11de62544/src/orion_v2/structural.py).

## What the retained experiments actually show

M8 language uses 167 atoms and 18 tasks. Flat organisation answers 18/18 with mean
4.5556 visits. Scope fibres answer 6/18 with mean 3.2222 visits, twelve `REFINE_REQUIRED`
and zero transports. Needed language material crosses the authored topic boundaries.
Refusal protects correctness, but fewer visits with lower coverage is not matched-quality speedup.
The next repair is query-driven cross-scope retrieval/refinement, then an untouched evaluation.
[Raw language fibre row](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/research/ocm-m8/M8_ORGANISATION_EVAL_V1.json#L66).

In M8's overlapping synthetic world, the learned arm selects one merge and reduces visits
from 32 for the community parent to 18.286; a fibre arm achieves 13.714.
The merge is genuinely data-selected, but its move grammar and task families are authored.
Both development and so-called heldout tasks influence adoption, so neither is an untouched
final test. This is an exploratory improvement, not established general learned organisation.
[Raw learned overlap row](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/research/ocm-m8/M8_ORGANISATION_EVAL_V1.json#L611).

**Additive erratum:** the frozen M8 report says the learned arm “never beats the community
parent”. Its own overlap row contradicts that sentence. The correct interpretation is one
exploratory improvement over that parent, without a general or strongest-parent advantage.
The original report and its receipt remain unchanged to preserve historical custody.
[Bound historical report](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/docs/M8_ORGANISATION_REPORT.md#L75).

Finite explicit method learning is real: the retained `inc,square` experiment mines a repeated
fragment, consumes it during search, persists/restarts and refuses reuse after revocation.
Two declared fresh-task search-slot counts fall 35→15 and 37→19. This is evidence for a small
executable library-learning mechanism, not general cognitive growth or full lifetime savings.
[Retained method-learning record](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/docs/provenance/runtime_revision_20260905_v3/METHOD_LEARNING_REFERENCE_V1.json).

## Saturation, recursion and Jump need disciplined boundaries

Finite exact closure, bounded absence of new findings and resource exhaustion are different
outcomes. V1's saturation contract is explicitly scoped and reopenable; its runtime assesses
recorded flat-round and route-coverage evidence. It does not enumerate all possible knowledge.
[V1 saturation contract](https://github.com/SzeChunYiu/ORION/blob/adb97ecce7d8e1fe6effab456b98e653f401dae0/docs/01-engine/saturation/README.md).

Our recursive research process is not evidence that OCM can improve itself. V2's recursive
development architecture explicitly separates reference architecture from protected outcomes.
The relevant machine test is checked episode → acquired structure → persistence → restart →
causal use on a fresh task, including failure and revocation.
[V2 development architecture](https://github.com/SzeChunYiu/ORION-V2/blob/e71513744763b67a0df80ddd4c1bf4a11de62544/research/foundation-saturation/ORION_V2_RECURSIVE_DEVELOPMENT_ARCHITECTURE_V1.md).

OCM M4 refutes eight incumbents in a finite Boolean class and validates a supplied extension.
That establishes the finite obstruction and checked expansion, not invention of the extension.
For hard mathematics, permit cost-guided speculative representation proposals without first
proving global impossibility; reserve necessity claims for actual witnesses. Every adopted
proposal still needs its own admissibility and verification. Jump level is not execution cost.
[Authored M4 alternatives](https://github.com/SzeChunYiu/ORION-OCM/blob/48e6035e5b55944110b200cd81a9bfdf37503a6c/research/orion-machine/reference/kso_m4_jump_v1.py#L110),
[V2 Jump contract](https://github.com/SzeChunYiu/ORION-V2/blob/e71513744763b67a0df80ddd4c1bf4a11de62544/research/frontier-jump/JUMP_RESEARCH_PROGRAMME_V0.md).

V1 also contains LLM fallback routes in its fibre solver. Importing its contracts is useful;
importing that execution closure wholesale would violate this OCM programme's no-neural rule.
[V1 fibre solver](https://github.com/SzeChunYiu/ORION/blob/adb97ecce7d8e1fe6effab456b98e653f401dae0/src/orion/engine/fibre_solver.py).

## What would make the research important

Recursive proof search already has strong mechanical parents such as
[Aesop](https://github.com/leanprover-community/aesop). Fixed-point reasoning and abstraction
have established foundations in [abstract interpretation](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml);
[egglog](https://arxiv.org/abs/2304.04332) combines Datalog and equality saturation.
[Soar's chunking](https://soar.eecs.umich.edu/soar_manual/04_ProceduralKnowledgeLearning/)
already learns executable rules from subgoal solutions for later reuse.
Absorb these mechanisms faithfully before claiming an OCM-specific improvement.
This is a targeted parent comparison, not a complete novelty clearance.

The candidate contribution is an executable combination: sufficient local retrieval,
revision-safe reusable methods and checked representation changes that improve future solving.
Test each addition against the same facts, operators, verifiers and resource allocation.
Include an equally adaptive parent and a control receiving the same new theorems without the
learned method. Charge acquisition, compilation, maintenance, search, revision and verification.
Measure answer quality and refusals alongside work; keep evaluation tasks untouched by selection.

Priority: repair local retrieval/refinement; make finite checked reuse work on harder fresh
tasks; then add obstruction-driven representation proposals. More protocols, topology or
terminology do not substitute for this experiment. Novelty and paper readiness remain open.
