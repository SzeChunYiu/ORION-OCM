# Language KSO Architecture V0

**State date:** 2026-09-04  
**Status:** prospective executable architecture; controlled V0 implementation follows.  
**Authority:** no claim of open-domain fluency, human-level language, lower sample complexity than LLMs, or novelty.

## 1. Thesis

Treat **speaking as a task family** learned by the same OCM machinery used for any other task.

The machine should not define language as next-token prediction. It should learn reusable structures that map communicative intentions and meanings to utterances, while retaining the ability to revise those structures.

The strongest candidate generation shape is **coarse-to-fine and incremental**:

```text
communicative goal
  -> message/content plan
  -> semantic/concept frame
  -> construction/sentence sketch
  -> phrase/role refinement
  -> lexical choice
  -> morphology/agreement
  -> linearization
  -> surface realization
  -> semantic/grammatical/pragmatic check
  -> utter / repair
```

This is the user's drawing analogy made operational: first sketch the composition, then refine local structure, then add lexical/morphological detail. A stage may reopen an earlier stage when it discovers that the current sketch cannot express the intended meaning.

The plan need not be completed globally before words are produced. Incremental realization is permitted: commit a warranted prefix only when later obligations remain satisfiable or repairable.

## 2. Language is not only grammar

A grammar-only machine can produce grammatical nonsense. Human-like speech requires several coupled fibres:

```text
K_language
  semantics / concepts
  discourse + pragmatics
  constructions / syntax
  lexicon
  morphology
  idioms / multiword constructions
  style / register
  conversational repair
  phonology/articulation (later; text V0 stops before audio)
```

These are provisional useful decompositions, not constitutional cognitive modules. OCM may later split/merge/reorganize them.

## 3. Core objects

### 3.1 CommunicativeIntent

What social/cognitive act is being attempted.

```text
CommunicativeIntent.v1
  act: ASSERT | ASK | REQUEST | EXPLAIN | CORRECT | ACKNOWLEDGE | ...
  target_listener
  intended_effect
  content_obligations
  discourse_context
  register/style constraints
```

### 3.2 MessagePlan

Selects **what information to express**, what is given/new, what can be omitted, and ordering across clauses. The MessagePlan must come from cognitive/task state; the renderer may not invent task answers.

### 3.3 SemanticFrame

A language-neutral proposition/event representation, initially frame-like:

```text
SemanticFrame.v1
  predicate/concept
  roles: agent, patient, experiencer, recipient, location, time, ...
  tense/aspect
  polarity
  modality
  quantity/reference
  modifiers
  discourse links
```

This is not claimed to be a universal semantic ontology. Frames are learned/extensible structures.

### 3.4 Construction

A learned pairing between a semantic/pragmatic configuration and a structured realization procedure.

```text
Construction.v1
  construction_id
  applicability
  semantic-role interface
  phrase/syntactic sketch
  ordering constraints
  morphology/agreement obligations
  optionality/variation
  discourse/register scope
  examples + counterexamples
  evidence/warrant
  dependencies
```

Examples include declarative transitive SVO, intransitive SV, copular, passive, interrogative, relative clause, coordination, idioms, and discourse constructions. Construction inventory is learned; it is not fixed to a school grammar list.

### 3.5 Lexeme

```text
Lexeme.v1
  lemma
  category/features
  concept/denotation links
  argument/selection constraints
  morphology/paradigm
  usage/register
  collocations/constructions
  evidence/warrant
```

Lexical meaning and syntactic category are distinct obligations. Raw co-occurrence is proposal evidence, not proof of denotation.

### 3.6 MorphologyRule

A scoped transformation from lemma/features to word form with exceptions and counterexamples. Productive regular rules and lexical irregulars may coexist; the more specific warranted rule wins.

### 3.7 SentencePlan / GenerationTrace

The machine should expose an inspectable intermediate structure:

```text
SentencePlan.v1
  intent
  semantic_frame
  selected_construction
  role_to_phrase mapping
  lexical choices
  feature unification
  morphology obligations
  linearization constraints
  unresolved slots
```

A `GenerationTrace.v1` records every refinement and checker result so an error can be attributed to content planning, semantics, construction selection, lexicalization, morphology, linearization, or rendering.

## 4. Learning channels

### 4.1 Explicit language lesson

A grammar book/teacher may directly state a procedure such as:

`English declarative transitive clause: SUBJECT -> VERB -> OBJECT`.

This is analogous to instruction in M3. The lesson can create a candidate construction, but its generalization scope is tested on examples/counterexamples and held-out composition.

### 4.2 Aligned demonstration

Input includes a meaning/situation plus an utterance. The learner searches a registered hypothesis space for constructions/lexical mappings that explain several different demonstrations.

This is far stronger evidence for form-meaning mapping than ungrounded text alone.

### 4.3 Raw articles/books

Raw text supplies enormous information about:

- recurring surface constructions;
- lexical distribution and collocation;
- morphology;
- discourse organization;
- style/register;
- probable syntactic categories and phrase boundaries.

But raw text **does not by itself warrant grounded meaning**. A system can infer a distributional/formal regularity while remaining uncertain about denotation, pragmatic intent, or real-world truth.

So book/article ingestion should create typed candidates such as `FORM_PATTERN`, `LEXICAL_ASSOCIATION`, `CONSTRUCTION_CANDIDATE`, or `STYLE_PATTERN`, not magically authoritative semantic facts.

### 4.4 Dictionary / grammar / bilingual / annotated resources

These can provide stronger structured supervision for categories, meanings, argument structure, morphology and cross-lingual correspondence when their source/authority is registered.

### 4.5 Grounded interaction

Dialogue plus environment/task feedback supplies evidence about whether an utterance achieved its intended communicative effect. Endpoint success alone is utility feedback; it does not automatically prove a grammar or semantic theory. Discriminating interactions may, however, identify competing hypotheses.

## 5. Production dynamics

Given cognitive content `C` and discourse state `D`:

1. `PLAN_CONTENT(C,D) -> MessagePlan`
2. `FRAME(MessagePlan) -> SemanticFrame(s)`
3. `SELECT_CONSTRUCTION(frame,D) -> candidate construction set`
4. `REFINE` selected construction into phrase-role obligations
5. `LEXICALIZE` roles using concept/selection constraints
6. `INFLECT` using morphology/agreement rules
7. `LINEARIZE` under construction constraints
8. `REALIZE` punctuation/casing/surface formatting
9. `CHECK` semantic preservation + grammatical obligations + discourse constraints
10. return `PASS(surface, trace)` or a typed gap/reopen terminal.

Useful gap terminals:

- `GAP_UNKNOWN_CONCEPT`
- `GAP_UNKNOWN_LEXEME`
- `GAP_NO_APPLICABLE_CONSTRUCTION`
- `GAP_AMBIGUOUS_CONSTRUCTION`
- `GAP_MORPHOLOGY`
- `GAP_DISCOURSE_REFERENCE`
- `GAP_STYLE`
- `REFINE_REQUIRED`
- `SEMANTIC_CHECK_FAILED`
- `CANNOT_CHECK_PRAGMATIC_EFFECT`

Do not silently call an LLM to fill any of these in the language-mechanism arm.

## 6. Variation rather than one canonical sentence

Fluent language is many-to-many:

`meaning -> {many acceptable utterances}`

and

`utterance -> {possibly several meanings}`.

Therefore evaluation cannot require one reference string. A generation may be valid when it differs from a training sentence if it preserves the intended meaning and satisfies the registered grammatical/pragmatic contract.

Variation policies may choose among constructions based on discourse, register, information structure, rhythm, brevity, convention, and learned preference. These choices should remain separate from semantic correctness.

## 7. Grammar is compositional but includes constructions/exceptions

Do not assume language is generated only from `subject + verb + object` rules. V0 uses simple school-grammar constructions because they are falsifiable calibration objects. Later versions need:

- recursive phrase/clause embedding;
- optional arguments and adjuncts;
- agreement and case;
- tense/aspect/modality;
- negation and questions;
- pronouns/reference;
- coordination/subordination;
- idioms and semi-fixed constructions;
- lexical selection restrictions;
- discourse and pragmatic constructions;
- productive regularities plus lexicalized exceptions.

A construction can be symbolic, neural, probabilistic, executable code, or hybrid. The KSO contract constrains its observable interface, evidence, scope, and tests—not its internal representation.

## 8. Language KSO as a recursive KSO

The language system is itself a fibred KSO:

```text
Language
  -> English
      -> syntax/constructions
      -> morphology
      -> lexicon
      -> discourse/pragmatics
      -> style registers
  -> Chinese
      -> ...
  -> cross-lingual transfer/translation correspondences
```

A construction or morphology rule is scoped. English SVO cannot be transferred to another language simply because a semantic frame is similar. Transfer requires an explicit correspondence/adapter and held-out validation.

This gives a natural negative-transfer experiment.

## 9. First executable calibration (L0)

The first implementation should learn and expose, rather than hide:

- a transitive clause order from aligned demonstrations over all six permutations of S/V/O;
- a noun-phrase sketch with determiner/adjective/noun roles;
- a productive present-3sg morphology rule;
- a productive regular-past rule;
- lexical irregular override (`go -> went`) as a more-specific rule;
- composition on unseen noun/verb/adjective combinations;
- exact evidence revocation/reinstatement;
- scope protection against applying an English construction to a registered SOV language;
- an explicit `SentencePlan` before surface realization.

Stress tests must include:

1. before lesson -> gap;
2. incomplete demonstrations -> ambiguity/refusal;
3. complete demonstrations -> learned construction;
4. unseen lexical combination -> grammatical transfer;
5. regular morphology to unseen regular verb;
6. irregular exception overrides general rule;
7. construction revocation -> generation gap;
8. reinstatement -> exact recovery;
9. wrong-language transfer -> refused;
10. supplied surface answer not present in the semantic/message input -> codec/renderer cannot launder it.

## 10. Real-language progression

After L0:

- **L1 corpus ingestion:** sentence segmentation, lexical candidates, recurring construction mining, morphology candidates, distributional neighbourhoods; no grounded-semantics claim.
- **L2 annotated/grounded lessons:** meaning-utterance pairs; induce construction inventory and lexical mappings; systematic held-out composition.
- **L3 dialogue:** references, questions, negation, clarification, repair and discourse state.
- **L4 multi-sentence planning:** paragraph/document structure and long-range coherence.
- **L5 open-domain grounding:** connect language forms to the general KSO/world/task state so language expresses knowledge rather than becoming a separate text predictor.
- **L6 naturalness/style:** learn optional variation, idioms, register and fluency preferences under a meaning-preservation gate.
- **L7 speech/audio:** phonology/prosody/articulation as another realization layer.

## 11. Strongest comparator

Any claim that this is a better way to learn language must compare against at least:

`frontier/recurrent language model + same corpus/lessons + same tools + same memory + same interaction budget + same verifier/test access`.

Also compare against strong grammar induction, program induction, construction/semantic parsing, neuro-symbolic generation, and conventional NLG pipelines where applicable.

Useful metrics are not only perplexity/BLEU:

- semantic/task success;
- grammaticality;
- systematic composition on unseen combinations;
- number of lessons/interactions required;
- negative transfer;
- correction/revocation locality;
- trace attribution;
- style/naturalness;
- whole-system bits/memory/compute/IO;
- ability to learn a new construction without retraining the entire language system.

## 12. Central falsifier

The language approach contracts if a matched language-model parent learns the same new constructions/lexicon with equal or better data efficiency, transfer, correction, naturalness and whole-system cost, or if the explicit structural decomposition causes brittleness that a less structured parent avoids.

The valid scientific terminal is then `PARENT_SUFFICIENT` or a narrower engineering/interpretability result.

## Non-consequences

- Reading several books is not expected by itself to produce human-level language.
- Learning grammar is not sufficient for world knowledge or communicative competence.
- A sentence sketch is not assumed to match human psycholinguistic processing exactly.
- Symbolic structure is not assumed universally superior to neural representations.
- L0 success does not establish a post-LLM language paradigm.
