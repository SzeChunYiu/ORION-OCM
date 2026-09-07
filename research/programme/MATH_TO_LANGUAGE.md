# Reusing mathematical cognition in language

[Programme](CORE.md) · [Proof curriculum](PROOF_CURRICULUM.md) · [ORION mechanisms](ORION_CONCEPTS.md)

Design decision, 7 September 2026. This is a prospective experiment, not a transfer result.
Develop the small language bridge alongside mathematical learning. Full FLT success is
not a prerequisite. All scored acquisition, selection, reasoning and realization remain non-neural.

## What can transfer

The strongest route is shared executable reasoning, with explicit mappings into each domain.
Mathematics supplies useful content and procedures; language supplies ways to express and
request meanings. A larger theorem collection alone does not supply grammar or conversation.

| Reusable structure | Mathematical use | Language use | Required boundary |
|---|---|---|---|
| Checked content | An order, counting or optimization theorem | Answer a quantities, schedule or allocation question | Show that the task's objects satisfy the theorem's assumptions |
| Decomposition and composition | Solve subgoals and combine proofs | Combine several stated rules into an answer and explanation | Preserve variable binding, scope and each supporting premise |
| Case analysis | Prove a conclusion in every case | Answer a common consequence of several live interpretations | Cover every registered interpretation; incomplete retrieval cannot establish coverage |
| Constraint propagation | Eliminate inconsistent mathematical assignments | Resolve a bounded reference or scheduling ambiguity | Linguistic/domain constraints need their own justification |
| Failure diagnosis | Identify a missing lemma or unsuitable representation | Ask a discriminating clarification or retrieve missing knowledge | A search failure is not evidence that a statement is false |
| Verified abstraction | Reuse a sufficient summary or invariant | Give a short answer while retaining relevant qualifications | The summary must preserve the requested meaning and commitments |

There are three different achievements: applying a known theorem to a formalized language
task; verbalizing a checked solution; and acquiring a method from mathematics that improves
new language reasoning. Record them separately. Only the third demonstrates learned transfer.

## Small mechanical architecture

```text
mathematical episodes → checked traces → candidate executable methods
                                             ↓
text ↔ grammar + lexical meanings ↔ typed task → retrieval/search → checked result
                                             ↑                        ↓
                                 domain-specific bindings      message plan → text
```

Use a small shared method interface, not one universal mathematical ontology. A retained
method has typed inputs/outputs, applicability conditions, executable steps, a correctness
contract, cost observations, discovery provenance and revision dependencies. Domain-specific
payloads and checkers remain distinct. Search scores determine priority, never warrant.

Mechanically propose candidates by typed anti-unification of successful subtraces, factoring
repeated compositions and specializing existing procedures. Preserve binders and side conditions.
Replay/prove each candidate, normalize against existing methods, then test fresh-use benefit.
Candidate generation itself is authored initial machinery; the particular acquired method
must be produced by OCM and traced through actual search after persistence and restart.

For language, begin with an explicit bounded grammar, lexical entries, dialogue state and
message plans. Every answer clause must map to a supported proposition or an explicitly
marked question/assumption. A parse/generate round trip is a useful consistency check, but
the same mistaken grammar can agree with itself; use separately specified meaning tests too.

This has strong existing parents. [Grammatical Framework](https://www.grammaticalframework.org/doc/gf-refman.html)
separates abstract syntax from concrete language realizations and supports reversible parsing
and linearization. Its [mathematics prototype](https://www.grammaticalframework.org/~aarne/gf-hott/)
already explores English/type-theoretic notation. [ACE-in-GF](https://github.com/Attempto/ACE-in-GF)
is an existing controlled-language implementation. Qualify and reuse the relevant grammar
mechanisms instead of claiming that meaning-to-text conversion is a new OCM invention.

## First causal transfer experiment

**Question:** can a method acquired solely from checked mathematical episodes lower the
complete cost of solving fresh, controlled-language tasks without reducing warranted accuracy?

1. Use set/order proofs and rule composition as the initial mathematical family.
   Freeze the proof episode split and allowed primitive methods before candidate selection.
   Extract actual proof/search traces; do not supply the desired learned macro as an answer.
2. Supply every arm the same controlled grammar over unary predicates, Boolean noun phrases,
   and “every”, “no”, “some”, “not every”, mapped into set constraints. Exclude pronouns and
   unstated world knowledge initially. This mapping is authored infrastructure, explicitly
   excluded from the claim that OCM discovered the correspondence.
3. Learn candidate methods from the mathematics training partition. Select using a separate
   development partition, then freeze the library and restart before target evaluation.
4. Evaluate on new language worlds, with fresh identifiers, held-out semantic compositions,
   negation/quantifier contrasts, missing premises, empty predicates and contradictory inputs.
   Reworded copies of a training proof are near-transfer controls, not the main transfer set.
5. Count actual method retrieval and invocation, generated subgoals, checker calls, failures,
   refusals, acquisition/compilation/storage/update costs and end-to-end cold/warm time.
   Include removal of a supporting rule and correction/reinstatement during a task stream.

Illustrative task: “Every violinist is a musician; no musician is asleep. Is any violinist
asleep?” Under the stated premises, the answer is no. This does not establish that a
violinist exists. A reusable set-inclusion/disjointness method can derive the answer and
produce an explanation from those premises.

Check consistency first. For this unary Boolean fragment, use an independently qualified
exact solver over predicate-membership regions. Entailed/contradicted answers need checked
certificates; unknown needs models for both polarities. Inconsistent premises are separate.
Later scheduling extensions must distinguish possibility from entailment: possibility needs
a satisfying schedule, impossibility a checked contradiction. A shared method cannot erase
these differences in the question's meaning.

This elementary case will likely be solved very cheaply by conventional methods. Its purpose
is to establish and falsify the acquisition-to-language path before harder families; it is
not a plausible breakthrough claim on its own.
With supplied logic bindings, the first result establishes reuse through a controlled-language
presentation. Broader cross-domain cognition requires tasks beyond isomorphic reformulations.

## Controls and publication decision

| Arm | What it isolates |
|---|---|
| Strong exact Boolean-set/BDD or SAT parent with simplification, memoization and incremental updates | Conventional solving with the same facts, grammar, mappings and checks |
| Equally adaptive parent trained on the same episodes | Improvement obtainable through ordinary rule/program learning |
| OCM with acquired methods disabled, but the same added theorems | Extra knowledge versus acquired executable procedure |
| OCM with the frozen acquired methods | Proposed acquisition and reuse contribution |
| Shuffled rankings of valid methods, or independently warranted unrelated methods matched for cost | Benefit from specific method selection/content versus extra candidates or selection effort |

Pin the parent implementations, target generator/splits, accounting and analysis before the
untouched evaluation. Choose sample sizes from a separate pilot; do not tune them to achieve
a positive result. Report per-family quality, refusal, cost and harmful transfer, paired
differences with uncertainty, and the cumulative break-even point if one is actually reached.
Report supplied engineering, grammar and teaching material separately; do not count them
as OCM discoveries or invent their original production cost.

[LangPro](https://aclanthology.org/D17-2020/) supplies another established symbolic entailment
parent. Give it the matched logical forms/derivations through a qualified non-neural input
route; its external parsing pipeline must not silently enter the OCM mechanism. Compare
parents on separate development tasks and preserve all results.

If only verbalization works, report a useful mechanical language interface. If equally
adaptive parents reproduce the gain, report `PARENT_SUFFICIENT`. If genuine transfer fails,
locate the failing stage—extraction, transport, retrieval, applicability or economics—make
a targeted repair and evaluate on fresh data. Preserve every earlier result.

The candidate scientific contribution is revision-safe, causally used cross-domain method
learning with a measured lifetime advantage. It is not “mathematics is language”, broad
conversational competence, or novelty merely from avoiding neural networks.

## What mathematics cannot supply automatically

A checked derivation establishes its conclusion under the registered assumptions and logic.
It does not certify that a speaker meant the formalized statement or that an empirical
premise is true. Everyday defaults, uncertain facts, reference, intent, politeness and
audience-appropriate explanation need explicit language/world learning and evaluation.
Keep uncertainty and source attribution in the language result; preserve genuinely different
meanings. A shared schema proposes a useful computation, never an unearned semantic identity.
