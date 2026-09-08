# Top-tier journal engineering constitution for the Machine Epistemics programme

**Parent scientific programme:** #143  
**Scientific thesis:** #50  
**Epistemic experience/lifetime learning:** #62  
**Scaling/navigation:** #69 #70 #72  
**Integrated strongest-parent comparison:** #73  
**Corrected acceptance / independent claims review:** #38 / #49  
**Execution roadmap:** #42

## Status and role

**PUBLICATION-QUALITY CONSTITUTION.**

This issue does not create a new scientific claim, unlock a milestone, or make ORION-OCM publication-ready. It defines the evidence, engineering, statistical, reproducibility, editorial and claim-discipline standards that every flagship Machine Epistemics study must satisfy before it may be promoted toward a top-tier journal submission.

The immediate target venue family includes **Nature Machine Intelligence / Nature Portfolio-calibre AI journals**, but the standard is intentionally stronger and more general than one venue's formatting rules. The research should remain scientifically valid if the final venue changes.

Current Nature Machine Intelligence guidance checked on **2026-09-07** emphasizes that:

- the journal publishes high-quality original research across AI, machine learning, robotics, symbolic reasoning, cognitive science and related areas;
- an Article is a **substantial novel research study**, often with a complex story involving several techniques or approaches;
- submissions should be accessible to non-specialists, with titles/abstracts understandable broadly and jargon minimized;
- central newly developed code must be available for peer-review evaluation and Nature Portfolio emphasizes transparent reporting and reproducibility;
- human scholarly accountability is non-transferable when AI assists research/writing, and material AI use requires transparent human oversight.

Official references:

- https://www.nature.com/natmachintell/submission-guidelines/about/aims
- https://www.nature.com/natmachintell/content
- https://www.nature.com/natmachintell/submission-guidelines/writing-and-language
- https://www.nature.com/natmachintell/editorial-policies
- https://www.nature.com/natmachintell/editorial-policies/ai

These venue notes are not scientific authority. The rules below are the programme's internal bar.

---

# 1. Editorial north star

The programme must not lead with ORION vocabulary or architecture inventory.

A top-tier paper should begin from a broad scientific problem that matters even to a reader who has never heard of ORION, KSO, Jump, Fibre or Machine Epistemics.

Candidate flagship question:

> **Can an artificial cognitive system accumulate persistent reusable competence such that prior learning causally reduces the marginal cost of future learning, reasoning and correction, while task-relevant computation remains sparse as lifetime competence grows?**

The programme-level hypothesis is:

> **Persistent epistemically governed computational structure can create a distinct lifetime scaling regime: capability accumulates, relevant cognition stays local/sparse, related future acquisition becomes cheaper, and revision remains localized, without sacrificing task quality relative to the strongest matched alternatives.**

This is stronger and more general than:

- a new knowledge graph;
- a symbolic-vs-neural comparison;
- implementing ORION V1/V2 concepts;
- a parameter-count claim;
- a one-benchmark accuracy win;
- a toy game solver;
- a language demo;
- a self-modifying agent demo.

Every flagship paper must state its scientific question without project-specific terminology before introducing the mechanism.

---

# 2. Top-tier editorial significance gate

Before a paper is allowed to consume expensive protected evaluation, produce an **Editorial Significance Packet** answering all of the following.

## ES-1 — What changed scientifically?

- [ ] State one sentence describing the new empirical law, mechanism, theorem or causal phenomenon.
- [ ] State why the result matters outside ORION-OCM.
- [ ] State the strongest prior scientific object that would make the result unsurprising.
- [ ] State the exact residual after absorbing that parent.

## ES-2 — Why does this need a top-tier journal?

At least one must be true and prospectively defensible:

- [ ] reveals a new general phenomenon/law of machine learning/cognition;
- [ ] provides a strong causal mechanism with broad implications;
- [ ] establishes a new scaling regime or lower/upper-bound frontier;
- [ ] demonstrates prospective cross-domain transfer of a mechanism not reducible to task-specific engineering;
- [ ] changes a widely held assumption about how lifelong machine intelligence must be organized;
- [ ] supplies a rigorous negative/impossibility result that materially redirects a major research direction.

A collection of individually correct engineering improvements is not enough.

## ES-3 — What would an editor understand in 90 seconds?

Freeze a one-page editor view containing:

```text
problem
one central hypothesis
one central mechanism
one decisive causal result
one generalization/scaling result
strongest-parent result
one limitation that remains
```

If the result cannot be explained without a long ORION glossary, the paper is not ready.

## ES-4 — Non-specialist communication test

Before submission:

- [ ] title tested with researchers outside the project/domain;
- [ ] abstract tested for comprehension by at least two scientifically literate non-specialists;
- [ ] project-specific abbreviations minimized;
- [ ] main figures intelligible without reading Supplementary Information;
- [ ] every coined term earns explanatory value beyond standard terminology.

---

# 3. Scientific contribution hierarchy

Each paper must declare exactly which level it claims.

```text
L0 ENGINEERING FUNCTION
L1 CONTROLLED MECHANISM
L2 CAUSAL MECHANISM
L3 PROSPECTIVE TRANSFER / GENERALIZATION
L4 SCALING LAW / MULTI-REGIME PHENOMENON
L5 HETEROGENEOUS CROSS-DOMAIN SIGNATURE
L6 FIELD-LEVEL COMPUTATIONAL PRINCIPLE
```

Rules:

- L0/L1 results may be valuable infrastructure but do not justify L5/L6 prose.
- A paper may contain several levels but must identify one primary contribution.
- No later level may be inferred merely from benchmark breadth.
- Every claimed level needs an explicit falsifier.

Candidate programme progression:

```text
exact games: L2
sequential/planning: L2-L3
cross-game transfer: L3
formal math: L2-L3
controlled language transfer: L3-L5
lifetime scaling: L4-L5
integrated OCM vs strongest parents: L5
Machine Epistemics field principle: L6 only if the preceding evidence converges
```

---

# 4. Evidence ladder — exploratory is not confirmatory

Every study row must be classified before execution as exactly one of:

```text
E0 THEORY / PROTOCOL DESIGN
E1 ENGINEERING CALIBRATION
E2 EXPLORATORY PILOT
E3 PROSPECTIVELY FROZEN CONFIRMATORY STUDY
E4 DISJOINT REPLICATION
E5 INDEPENDENT EXTERNAL/SECOND-IMPLEMENTATION REPLICATION
```

## E1/E2 rules

Development/pilot work may:

- identify broken instrumentation;
- choose feasible scales;
- discover unexpected phenomena;
- identify missing parents;
- refine the next protocol.

It may not become confirmatory evidence merely because results are favorable.

## E3 rules

Before protected outcomes:

- [ ] primary hypothesis frozen;
- [ ] primary endpoints frozen;
- [ ] task-family generator/version frozen;
- [ ] protected seeds/splits frozen;
- [ ] comparators/configuration policy frozen;
- [ ] information/tool/memory permissions frozen;
- [ ] compute/resource budgets frozen;
- [ ] stopping/exclusion rules frozen;
- [ ] statistical analysis frozen;
- [ ] non-inferiority/superiority margins frozen;
- [ ] ablations frozen;
- [ ] negative terminals frozen.

## E4/E5 rules

A flagship positive does not become field-level evidence without a disjoint replication.

Where feasible require:

- different protected seeds/families;
- fresh process/host;
- different task order;
- second model family for broad neural comparisons;
- independent scorer/reimplementation of the key measurement;
- ideally another researcher/operator or scripted blind reproduction.

Replication failure is retained and narrows the claim.

---

# 5. One decisive causal claim per paper

A top-tier manuscript should not rely on twenty correlated weak improvements.

For every paper, freeze one **Decisive Causal Question** of the form:

```text
Treatment mechanism M
versus strongest faithful parent/ablation P
under matched information/resources
causes outcome Y
on protected independent units U
with effect size/uncertainty E
and predicted negative/control behavior C.
```

Examples:

## P1
Removing a learned persistent method after restart eliminates the fresh-task search advantage.

## P2
Scoped failure knowledge prevents repeated compatible dead ends but reopens after a registered regime change.

## P3
A frozen domain-general operator learned in one task family improves a materially different family and the benefit disappears when the operator is removed.

## P4
A mechanically acquired proof method causally reduces verifier/search work on fresh theorem families without answer retrieval.

## P5
A method frozen before language exposure causally reduces information/search required for a controlled language family.

## P6
As total lifetime competence N grows, matched-quality OCM active/query/revision cost follows a different empirical scaling regime than strongest persistent neural parents.

Every secondary experiment should support, constrain or attack the decisive claim.

---

# 6. Strongest-parent doctrine

The paper fails scientifically if the comparator is obviously weak.

## Required parent classes

Depending on the claim, first-right-of-refusal may include:

- exact classical algorithms/search/planning;
- database/index/materialized-view systems;
- TMS/ATMS/nogood/CEGAR/CEGIS;
- library learning/program synthesis/DreamCoder/Stitch-class systems;
- continual learning/meta-learning/meta-RL;
- model-based RL/neural planning;
- Transformer / recurrent sequence model;
- Transformer + RAG;
- Transformer + persistent memory;
- Transformer + tools/checkers;
- Transformer + adaptation/skill memory;
- domain-specialized theorem-proving/coding/planning systems;
- strongest faithful composition of the above.

## Comparator fairness checklist

For every headline comparison:

- [ ] same task-relevant information;
- [ ] same post-freeze examples/demonstrations;
- [ ] same tool/checker access;
- [ ] same persistent-memory permission;
- [ ] same feedback availability;
- [ ] same protected-split access;
- [ ] explicit hyperparameter/search budget policy;
- [ ] compute/test-time budget recorded;
- [ ] neural pretraining disclosed/characterized where possible;
- [ ] OCM authored code/operators/priors disclosed and charged conceptually;
- [ ] no privileged evaluator-private structure supplied only to OCM unless it is the registered treatment.

If a stronger parent becomes available before submission, rerun or explicitly narrow the claim.

`PARENT_SUFFICIENT` is a successful scientific terminal.

---

# 7. Prior-information and intelligence-laundering audit

Top-tier reviewers will attack where the intelligence really comes from.

Create a machine-readable **Prior Information Manifest** for every arm.

For OCM record:

```text
immutable core source/bytes
hand-authored operator catalogue
hand-authored representations/types
initial domain rules
preloaded methods
external solver/checker semantics
index structures
training/curriculum information
persistent learned state
```

For neural parents record where available:

```text
model identity/version
parameter count/bytes
pretraining description
post-training/adaptation data
retrieval corpus
memory state
prompts/system rules
tools/checkers
```

Hostile checks:

- [ ] benchmark solution not encoded in operator hypothesis language by construction;
- [ ] task IDs/filenames/order do not leak labels;
- [ ] exact checker does not synthesize the answer;
- [ ] language codec does not perform the cognition credited to OCM;
- [ ] cross-domain transfer map does not encode target-domain solution structure;
- [ ] neural parent not denied equivalent state/memory powers.

A small parameter count does not establish a small or efficient system.

---

# 8. Scaling and Cognitive Productivity gate

Top-tier scalability evidence should be a curve/frontier, not a single CP score.

Define and instrument at least:

```text
N = total persistent logical competence/state
B_N = persistent bytes
k = active/touched task-relevant state
B_k = active bytes
D = task complexity
Q = verified capability/task-quality vector
C_acquire
C_query
C_verify
C_revision
C_maintenance
C_lifetime
```

## Required growth study

Prospectively freeze scale points such as:

```text
1x / 3x / 10x / 30x / 100x where feasible
```

At each point:

- [ ] same probe families retained;
- [ ] unrelated distractor competence added;
- [ ] related competence added separately;
- [ ] N, k, k/N measured;
- [ ] hidden index/global work measured;
- [ ] query/search/checker work measured;
- [ ] next-related-family acquisition cost measured;
- [ ] unrelated-family acquisition cost measured;
- [ ] local and global revision hostiles measured;
- [ ] retention/negative transfer measured;
- [ ] complete lifetime costs accumulated.

Candidate field-level signature:

```text
Q stays comparable or rises
N grows strongly
k/N remains small or decreases
marginal related-task acquisition decreases
local revision work grows much slower than N
whole-lifetime Pareto frontier improves relative to matched parents
```

Do not assume power laws; compare plausible functional forms and report uncertainty/model diagnostics.

Cognitive Productivity may be reported secondarily at matched quality Q*:

```text
CP_advantage_r(Q*) = Resource_parent_r(Q*) / Resource_OCM_r(Q*)
```

but no post-hoc weighted scalar CP score may serve as the primary result.

---

# 9. Cross-domain generality gate

Toy environments are valid for causal identification but insufficient for the strongest claim.

Required progression:

```text
exact finite games
→ sequential/planning/information-gathering worlds
→ formal mathematics/exact proof checking
→ controlled compositional language
→ optional coding/procedural domain
```

A cross-domain result requires:

- [ ] same cognitive mechanism/operator identity frozen before target-domain protected access;
- [ ] target vocabulary/surface reminted where possible;
- [ ] no target solution embedded in correspondence map;
- [ ] reset OCM comparator;
- [ ] task-specific OCM comparator;
- [ ] strong neural/meta-learning parent;
- [ ] harmful and unrelated transfer controls;
- [ ] causal method-removal ablation.

Cross-domain support means a mechanism survived a change in validation semantics, not merely two datasets with different names.

---

# 10. Statistics and uncertainty constitution

Every empirical paper requires a written analysis plan before protected outcomes.

## Independent unit

Define the actual independent unit:

- task family;
- environment/world seed;
- theorem family;
- construction family;
- lifetime sequence;
- model training seed;

Do not treat correlated actions/examples inside one generated world as thousands of independent samples.

## Minimum requirements

- [ ] effect sizes, not only p-values;
- [ ] 95% confidence/credible intervals where appropriate;
- [ ] paired analysis for paired task units;
- [ ] cluster/hierarchical analysis for family-correlated samples;
- [ ] multiple random seeds for stochastic training/evaluation;
- [ ] task-order permutations for lifetime claims;
- [ ] non-inferiority margins frozen before outcomes;
- [ ] multiplicity plan for multiple primary tests;
- [ ] robustness/sensitivity analyses frozen where analytically material;
- [ ] exact finite-family enumeration used when it is stronger than asymptotic statistics;
- [ ] failures/timeouts/abstentions retained in denominator according to frozen rules.

## Power / precision

For expensive studies:

- [ ] prospective power/precision calculation or simulation;
- [ ] declare minimum effect size worth a scientific claim;
- [ ] avoid underpowered “no difference” conclusions;
- [ ] avoid enormous synthetic denominators that create tiny p-values for irrelevant effects.

## Negative results

Report confidence bounds strong enough to distinguish:

```text
no evidence of effect
small effect bounded
parent-equivalent within margin
harmful effect
cannot identify because study underpowered
```

---

# 11. Benchmark engineering constitution

A benchmark designed by the project can easily encode its desired conclusion.

Every new benchmark must ship:

- [ ] benchmark purpose and construct definition;
- [ ] why existing benchmarks are insufficient;
- [ ] generator/source code;
- [ ] independent oracle/checker;
- [ ] shortcut/leakage audit;
- [ ] label/task-ID remint controls;
- [ ] positive cases;
- [ ] negative/no-use cases;
- [ ] adversarial near-misses;
- [ ] parent-favoring cases where simpler methods should win;
- [ ] hidden-protected family generation or source split;
- [ ] external or independently authored validation subset when feasible;
- [ ] benchmark version/hash;
- [ ] explicit statement of what the benchmark cannot establish.

Never make every test environment one in which explicit reuse is optimal by construction.

Include regimes where:

- reset system should be equally good;
- simple search should win;
- neural parent should win;
- transfer should be refused;
- Jump should be unnecessary;
- locality should fail because the true dependency is global.

These controls make the benchmark scientifically credible.

---

# 12. Mechanistic intervention and ablation standard

Ablation must preserve the rest of the system as faithfully as possible.

Every headline mechanism needs:

- [ ] remove mechanism;
- [ ] replace with strongest simple parent;
- [ ] scramble/permute semantics where a shortcut is possible;
- [ ] dose/scale intervention where possible;
- [ ] restore mechanism and recover effect;
- [ ] verify intervention actually changed the intended component;
- [ ] inspect unintended compensatory changes.

Examples:

```text
learned method removed → advantage falls
failure knowledge removed → dead ends recur
fibre/index replaced by global scan → scaling changes
representation-change operator disabled → true obstruction remains unresolved
Jump threshold loosened → false escalation rises
explicit dependency graph removed → revision becomes broader/stale
```

Ablation-induced catastrophic incapacity is not automatically evidence that the mechanism is scientifically unique; compare against a functional replacement.

---

# 13. Reproducibility and software engineering standard

Treat the paper as a computational scientific instrument.

## Before protected execution

Freeze:

- [ ] exact git commit/tree;
- [ ] dependency lock/environment/container;
- [ ] OS/hardware identity where relevant;
- [ ] tool/checker versions and hashes;
- [ ] model/provider/checkpoint identities;
- [ ] dataset/corpus versions and licenses;
- [ ] benchmark generator/checker identities;
- [ ] seeds/splits/order manifests;
- [ ] prompts/configs;
- [ ] analysis code;
- [ ] expected output schema;
- [ ] resource-meter version.

## After execution

Retain:

- [ ] raw predictions/actions/traces;
- [ ] raw resource counters;
- [ ] failures/crashes/timeouts;
- [ ] exact stdout/stderr/logs where material;
- [ ] machine-readable result receipts;
- [ ] immutable figure-source tables;
- [ ] every exclusion with reason;
- [ ] checksum manifest.

## Reproduction

Before submission:

- [ ] clean-clone install succeeds;
- [ ] one-command reproduction for headline tables/figures;
- [ ] fresh-host rerun of headline rows;
- [ ] independent figure regeneration from raw receipts;
- [ ] no manuscript number manually transcribed if machine derivation is possible;
- [ ] second implementation/scorer for the most novel key metric where feasible;
- [ ] central code packaged for reviewer access;
- [ ] public archive/release plan consistent with licenses and security constraints;
- [ ] Code Availability and Data Availability drafts prepared before submission.

A green CI badge alone is not independent reproduction.

---

# 14. Human accountability and AI-assisted research integrity

Because AI sessions materially contribute to programme design and implementation, explicitly preserve human scholarly accountability.

- [ ] Every scientific conclusion has a named accountable human owner before submission.
- [ ] AI-generated hypotheses/analysis/code are independently checked to the standard appropriate to their role.
- [ ] AI-generated citations are never accepted without source verification.
- [ ] AI cannot serve as the sole independent reviewer/verifier of its own proposed result.
- [ ] Material AI use in research/writing is documented for transparent disclosure according to the target venue's current policy.
- [ ] Manuscript responsibility, authorship, interpretation and final claims remain human.
- [ ] Protected/confidential third-party review material is never provided to unauthorized AI systems.

AI assistance is a tool, not scientific authority.

---

# 15. External validity and independent replication

Before any L5/L6 claim:

- [ ] at least two materially different validation regimes;
- [ ] at least one disjoint replication family not used for architecture choice;
- [ ] fresh-host reproduction;
- [ ] second model family for broad Transformer/neural conclusions where feasible;
- [ ] different task order for lifetime conclusions;
- [ ] independent scorer/analysis reconstruction;
- [ ] at least one reviewer/operator who did not design the key benchmark checks the protocol/result correspondence;
- [ ] external domain expert review for claims requiring domain significance (especially mathematics/language);
- [ ] unresolved discrepancies retained.

The strongest programme-level claim should ideally survive an external or independently developed reproduction, not only another internal rerun.

---

# 16. Paper architecture for a flagship Nature Machine Intelligence-calibre submission

The main paper should tell one compact story.

Candidate five-figure spine:

## Figure 1 — Scientific principle and machine

Show:

```text
experience
→ persistent epistemic competence
→ selective active cognition
→ reuse / learning / revision
→ verified result
```

Explain the treatment without internal ORION jargon.

## Figure 2 — Causal mechanism

Exact worlds:

```text
learn → persist → restart → fresh reuse → ablation
composition
scoped failure learning
minimum escalation
```

## Figure 3 — Lifetime scaling law

Plot against total persistent competence `N`:

```text
Q
k/N
query work
marginal acquisition cost
revision work
maintenance cost
```

with strongest matched parents.

## Figure 4 — Transfer ladder

```text
games/planning
→ formal reasoning
→ controlled language
```

show positive transfer, no-transfer and harmful-transfer refusal.

## Figure 5 — Whole-lifetime Pareto frontier

Capability versus cumulative resource vectors, including training/acquisition, query work, storage/indexing, verification and revision.

Do not force all results into one scalar score.

The paper should be understandable from these figures plus captions before the reader enters Methods.

---

# 17. Editorial self-rejection simulation

Before submission, run at least four independent red-team reviews.

## R1 — Nature editor simulation

Question:

> Is there one broad, surprising and well-supported advance, or only a complex project with many pieces?

## R2 — Neural/continual-learning expert

Attempts to show a stronger neural/memory/meta-learning system already explains the result.

## R3 — Symbolic/formal/classical-systems expert

Attempts to reduce OCM to known database, TMS, planner, program-synthesis, CEGAR or cognitive-architecture mechanisms.

## R4 — Statistical/reproducibility reviewer

Attempts to invalidate independence, denominators, effect sizes, task-order controls, leakage, compute accounting, or reproducibility.

For every criticism create:

```text
attack
severity
existing control
evidence
remaining vulnerability
paper wording consequence
additional experiment required? yes/no
```

Do not use AI-generated reviewer praise as evidence of readiness.

---

# 18. Editorial kill / narrow rules

Do not submit the flagship claim if any of these remain true:

- [ ] OCM materially underperforms the strongest comparator on core capability without a compelling scoped reason.
- [ ] primary effect exists only on project-designed toy tasks.
- [ ] causal advantage disappears under functional replacement ablation.
- [ ] strongest parent product has not been attempted.
- [ ] lifetime advantage disappears when full maintenance/storage/verification cost is included.
- [ ] cross-domain transfer depends on target-specific hand mapping that carries the solution.
- [ ] scaling range is too small to distinguish competing models.
- [ ] result depends on one task order/seed/model family.
- [ ] statistical independent unit is unclear.
- [ ] protected benchmark has been repeatedly tuned after outcome access.
- [ ] central code/data cannot be evaluated by reviewers.
- [ ] headline figure cannot be reproduced from immutable raw evidence.
- [ ] novelty claim depends mainly on ORION terminology rather than an empirical/theoretical residual.

Allowed disposition:

```text
NARROW_PAPER
SPECIALIST_VENUE
METHODS_PAPER
NEGATIVE_RESULT_PAPER
MERGE_WITH_OTHER_PAPER
DO_NOT_SUBMIT_YET
```

Top-tier ambition must not corrupt the science.

---

# 19. Submission-readiness gate

A paper may enter `TOP_TIER_SUBMISSION_CANDIDATE` only when all are checked.

## Scientific

- [ ] one primary contribution frozen and supported;
- [ ] strongest parent comparison complete/current;
- [ ] causal ablation complete;
- [ ] disjoint replication complete;
- [ ] negative/control regions retained;
- [ ] claim boundary explicit;
- [ ] current literature/novelty audit refreshed near submission.

## Statistical

- [ ] independent units correct;
- [ ] effect size + uncertainty reported;
- [ ] predeclared primary analysis executed;
- [ ] multiplicity handled;
- [ ] sensitivity/robustness analyses complete;
- [ ] exclusions fully accounted.

## Scaling/generalization where claimed

- [ ] registered scale range complete;
- [ ] full lifetime cost accounting complete;
- [ ] cross-family/cross-domain transfer complete;
- [ ] task-order robustness complete;
- [ ] second parent/model-family replication where required.

## Reproducibility

- [ ] clean-clone reproduction;
- [ ] fresh-host replay;
- [ ] immutable raw evidence;
- [ ] figure regeneration;
- [ ] code/data availability plan;
- [ ] reviewer software package/checklist ready.

## Editorial

- [ ] title understandable outside project;
- [ ] abstract states general problem/result, not architecture inventory;
- [ ] main paper fits one coherent story;
- [ ] limitations explicit;
- [ ] jargon minimized;
- [ ] five-figure evidence map complete;
- [ ] red-team editor simulation passed or criticisms explicitly dispositioned.

## Integrity

- [ ] human accountability bound;
- [ ] AI-use log/disclosure prepared;
- [ ] authorship/contribution ledger;
- [ ] conflicts/funding/related manuscripts documented;
- [ ] no result or citation known to be unverifiable.

Only then may the paper use the internal status:

```text
TOP_TIER_SUBMISSION_CANDIDATE
```

This status means ready to submit, **not likely to be accepted**.

---

# 20. Paper-series engineering under this constitution

This issue governs the #143 sequence without forcing every rung into a standalone top-tier paper.

## P1 — exact causal learning

Publication goal: clean causal-mechanism paper; may be specialist/top ML venue if breadth is not sufficient for NMI.

Top-tier upgrade requires a mechanism/general law beyond one game family.

## P2 — sequential cognition / failure / minimum escalation

Top-tier upgrade requires a general principle or surprising interaction, not a checklist of cognitive features.

## P3 — domain-general operators

High-value if prospective transfer survives materially different task families and strong meta-learning parents.

## P4 — formal reasoning

High-value if learned method structure causally changes proof search beyond retrieval/search parents with exact verification.

## P5 — cross-domain transfer to controlled language

Potential flagship if a method learned before language exposure reduces acquisition/reasoning cost and survives Transformer+memory/adaptation comparisons.

## P6 — lifetime scaling / strongest neural comparison

Primary NMI/Nature-calibre candidate if it establishes a reproducible scaling law or Pareto frontier across heterogeneous domains.

## P7 — governed self-reorganization

Only if repeated prospective generations demonstrate minimum-sufficient self-change beyond AutoML/meta-learning/program-repair parents. Do not let self-modification become a publicity claim unsupported by mechanism.

Paper count is not a goal. Merge or delete papers when the evidence is stronger as one story.

---

# 21. Immediate deliverables

- [ ] **PUB-D1 — Top-tier claim ledger schema.** `Claim → level → hypothesis → parent → experiment → replication → result → limitation → permitted wording`.
- [ ] **PUB-D2 — Editorial significance packet template.** Required before confirmatory protected execution.
- [ ] **PUB-D3 — Prior-information manifest schema.** OCM and all comparator arms.
- [ ] **PUB-D4 — Statistical analysis plan template.** Independent units, power/precision, margins, multiplicity, effect/CI reporting.
- [ ] **PUB-D5 — Reproducibility manifest/checker.** Code/data/environment/seed/raw-output/figure lineage.
- [ ] **PUB-D6 — Benchmark construct-validity checklist.** Shortcut, leakage, parent-favoring, negative/control families.
- [ ] **PUB-D7 — Reviewer attack ledger.** Editor/neural/classical/statistical red teams.
- [ ] **PUB-D8 — NMI-style five-figure evidence map for #143.** Populate prospectively with required evidence, not current desired results.
- [ ] **PUB-D9 — AI-use/human-accountability research log template.** Suitable for eventual venue disclosure.
- [ ] **PUB-D10 — Submission-readiness automated report.** Fail-closed status; no green from missing evidence.

---

# 22. Immediate instructions to active AI research sessions

Any AI session working on #143 or a child study must:

1. read this issue before opening a new result-bearing experiment;
2. classify work as E0–E5;
3. state the claimed contribution level L0–L6;
4. name the strongest parent/product before implementation;
5. state the decisive causal question;
6. state what result would kill/narrow the mechanism;
7. bind prior-information and resource accounting;
8. separate pilot outcomes from confirmatory evidence;
9. preserve every null/harmful/parent-sufficient result;
10. report which future top-tier evidence requirement the work actually discharges.

The session must not optimize for a favorable publication claim. It optimizes for a decisive, reproducible scientific answer.

---

# 23. Completion terminal

This issue never closes because one paper is submitted.

It closes only if the Machine Epistemics programme has a stable reusable publication-engineering system and every active flagship paper has a bounded disposition under it.

Valid programme terminal:

```text
TOP_TIER_PUBLICATION_ENGINEERING_CONSTITUTION_OPERATIONAL
```

This terminal means the scientific programme can reliably distinguish pilot from evidence, mechanism from benchmark fitting, architectural prior from learned competence, and publication ambition from scientific authority. It does **not** mean Nature Machine Intelligence or any other journal will accept the work.
