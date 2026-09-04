# Language KSO Parent Research V0

**State date:** 2026-09-04  
**Purpose:** strongest-parent subtraction and architecture constraints for the Language KSO.  
**Authority:** research synthesis only; no novelty or human-language claim.

## 1. Strongest immediate parents

### Computational Construction Grammar / usage-based construction networks

Jonathan Dunn, *Computational Construction Grammar: A Usage-Based Approach* (Cambridge, 2024) explicitly studies how constructions can be represented, learned from corpora, and arranged in a network, including slot constraints learned with the constructions. This directly owns the broad idea that a grammar can emerge as a network of learned form-function patterns.

**OCM consequence:** construction-network learning is parent territory. ORION may contribute only if its warrant/revocation/transfer/recursive-KSO machinery changes a matched discriminator.

### FrameNet + Constructicon / Frame Semantics + Construction Grammar

Borin & Lyngfelt, *Framenets and ConstructiCons* (Cambridge Handbook of Construction Grammar, online 2025) describe semiformally structured computational resources connecting semantic frames and constructions, including cross-linguistic issues.

**OCM consequence:** `SemanticFrame <-> Construction` is a strong existing organizing interface, not a new ORION ontology.

### Computational Construction Grammar for semantic frame extraction

Moerman, Van Eecke & Beuls (2024) evaluate large-scale computational construction grammars on semantic frame extraction and semantic role labeling. Beuls, Van Eecke & Cangalovic previously showed construction-based semantic-frame extraction from newspaper text.

**OCM consequence:** the Language KSO must compare against actual computational construction grammar rather than only against CFGs or LLMs.

### Meaning graph -> synchronous hyperedge replacement grammar -> utterance

Gao & Sun, EMNLP 2025, *A Computational Simulation of Language Production in First Language Acquisition*, is an especially close parent. It formalizes meaning as graphs and the syntax-semantics interface with Synchronous Hyperedge Replacement Grammar (SHRG), induces interpretable statistical grammar knowledge, and evaluates it by generating utterances.

**OCM consequence:** the future Language KSO should treat graph-to-graph/graph-to-string grammar induction and SHRG-like formalisms as a strongest parent for the `meaning -> structured realization` mechanism. A simple SVO sketch is only L0 calibration.

### Grounded/joint grammar induction

Zhao et al., *Artificial Intelligence* 2025, *Grammar induction from visual, speech and text*, argues grammar induction benefits from heterogeneous modalities rather than text alone.

Portelance, Reddy & O'Donnell, *Journal of Memory and Language* 2025, *Reframing linguistic bootstrapping as joint inference using visually-grounded grammar induction models*, reports that jointly learning syntax and semantics improves grammar induction, lexical-category learning and interpretation of novel sentence/verb meanings.

**OCM consequence:** raw books/articles should not be the only acquisition channel. Grounded multi-modal or aligned semantic evidence is a first-class route, and syntax/semantics should be allowed to constrain each other during learning.

### Raw-text grammar induction

Unsupervised grammar induction from raw text remains an active field. Wang & Utiyama (EMNLP 2024) study unsupervised parsing, and Clark & Schuler (LREC-COLING 2024) induce categorial grammar without POS annotations. A 2024 survey also documents a large literature on unsupervised morphology induction from raw text.

**OCM consequence:** `read text -> induce grammar` is not a novel mechanism. We should test whether ORION's evidence, correction and cross-task transfer improve the lifetime system, not claim grammar induction itself.

### Usage-based minimal cognitive grammar induction

A 2024 *Computational Linguistics* study on usage-based grammar induction from minimal cognitive principles shows short flexible sequence memory can discover frequent/informative multi-word chunks and reuse sequential patterns.

**OCM consequence:** chunk/construction emergence from exposure has strong parent ancestry; the KSO needs matched controls against usage-based sequence learners.

### Incremental sentence planning

Cho & Boland (2025), studying English SVO and Korean SOV speakers, report evidence that incremental sentence planning incorporates both hierarchical and linear planning.

**OCM consequence:** do not require a complete global syntax tree before surface production. The architecture should support partial hierarchical sketching plus incremental linear commitment and repair.

### Pipeline/surface realization

Surface realization is an established NLG task: linguistic/semantic representations are converted into well-formed sentences. Prior work reports pipeline models can remain competitive while offering explicit intermediate representations and controllability.

**OCM consequence:** `meaning -> plan -> surface` is parent NLG architecture. OCM's scientific question is whether learned/revisable structures plus evidence/revocation/transfer produce a useful residual.

### Content selection -> sentence planning -> generation

Slobodkin et al., ACL 2024, *Attribute First, then Generate*, explicitly decomposes grounded generation into content selection, sentence planning and sequential sentence generation to improve local attribution.

**OCM consequence:** sentence planning and evidence-bound content selection are not novel, but they fit naturally with ORION's requirement that the renderer cannot invent unsupported task content.

### Grammar-constrained generation

Tuccio et al., Findings ACL 2025, *GRAMMAR-LLM*, integrates formal grammar constraints into LLM decoding and proves efficient LL(prefix)/LL(1)-style processing.

**OCM consequence:** a future comparison must include hybrid parents where an LLM supplies lexical fluency while formal grammar constrains structure. OCM does not win merely by producing syntactically valid strings.

## 2. Results that support, but do not uniquely justify, the OCM hypothesis

A 2024/2025 Nature Communications study reports that humans, RNNs and an LLM generalize more systematically when exposed to more compositional artificial languages.

A 2025 TACL study shows Transformers can acquire hierarchical generalization under language-model training without an explicit structural tree bias.

**OCM consequence:** explicit structure may improve systematicity, but structure is not exclusive to symbolic systems. Strong LM parents may internally learn hierarchical/constructional structure and must be treated as genuine competitors.

## 3. Critical correction: acquiring language != inducing a grammar

Dupre, *Cognition* 2024, argues that language acquisition should not be reduced to recovering string-generating grammar rules from linguistic input, because observed language is shaped by many non-grammatical systems.

This is a useful hostile control against an over-simple OCM story.

**Architecture consequence:** language competence must include at least semantics, discourse/pragmatics, lexical knowledge, social/communicative goals, memory, contextual inference and repair in addition to grammatical structure.

Therefore:

`GRAMMAR_LEARNED != LANGUAGE_ACQUIRED`.

## 4. Revised strongest architecture hypothesis

The language fibre should be treated as **joint structured inference and generation over several coupled representations**, not as a school grammar engine:

```text
world / cognitive state / discourse
        |
        v
communicative intent + content obligations
        |
        v
meaning / semantic graph <----> lexical/construction hypotheses
        |                              ^
        v                              |
coarse construction sketch -----------+
        |
        v
incremental phrase + morphology + linearization
        |
        v
surface utterance
        |
        v
semantic / grammatical / pragmatic / task checks
        |
        +--> revise semantics / construction / lexicon / discourse policy
```

Future internals should compare at least:

- frame/construction networks;
- categorial grammar;
- synchronous hyperedge replacement grammar;
- dependency/constituency representations;
- learned neural latent structures;
- hybrids where symbolic interfaces constrain neural lexicalization/realization.

No internal formalism is constitutional.

## 5. Why raw books/articles help but are not sufficient

Raw text is powerful evidence for:

- segmentation and token/word-form statistics;
- morphology;
- lexical distributions and collocations;
- recurring constructions;
- syntactic category hypotheses;
- style/register/discourse patterns;
- frequency/productivity/exception structure.

It is weaker for:

- grounded denotation;
- speaker goals;
- reference to the physical/social world;
- causal meaning;
- pragmatic success;
- truth of claims in the text.

Therefore a corpus-only learner can legitimately produce a **form/usage network**, but semantic/communicative authority should remain partial until additional channels provide alignment or grounding.

## 6. Proposed acquisition experiment ladder

### L1A — explicit lesson

Give a small grammar/dictionary lesson, then hold out lexical combinations and constructions.

Measure lesson count, systematic transfer and correction locality.

### L1B — aligned meaning/utterance demonstrations

Provide semantic graphs/frames plus utterances. Compare induced construction and lexicon against grammar-book instruction.

### L1C — raw corpus only

Provide only text. Permit form/morphology/construction candidates but no privileged semantic labels. Test what genuinely emerges.

### L1D — grounded joint learning

Add visual/world/task state aligned with utterances. Test whether syntax, semantics and lexicon become identifiable with fewer examples than isolated induction.

### L1E — mixed curriculum

Grammar lesson + raw corpus + grounded interaction. The machine should learn when each evidence source is useful rather than treating all evidence as interchangeable.

## 7. Required matched comparators

At minimum:

1. recurrent/frontier LM trained/conditioned on the same material;
2. strong unsupervised grammar induction;
3. computational Construction Grammar;
4. graph-to-text/SHRG-like parent;
5. conventional NLG pipeline;
6. grammar-constrained neural generator;
7. identical KSO without explicit structure-learning/revocation mechanisms.

Matched information and resource budgets are mandatory.

## 8. Key discriminators

A useful Language KSO result must show something stronger than grammatical toy strings. Candidate discriminators:

- **systematic compositional transfer:** novel combinations of known concepts/lexemes/constructions;
- **few-lesson acquisition:** a new productive construction becomes usable without global retraining;
- **correction locality:** revoking/correcting one lesson changes exactly its dependent utterances;
- **negative transfer control:** source-language/source-register construction is refused when target scope differs;
- **meaning preservation:** natural variation allowed while intended semantic graph remains invariant;
- **incremental repair:** later conflict can reopen an earlier construction choice without discarding unrelated message content;
- **lifetime improvement:** later related language tasks require less acquisition cost because reusable structure exists;
- **whole-system cost:** count corpus, lexicon, grammar storage, indexing, inference, verifier and interaction cost.

## 9. Main scientific risk

The strongest plausible negative is:

> A matched recurrent/Transformer language model learns the same structures implicitly and achieves better naturalness, transfer and cost, while the explicit Language KSO adds brittleness and engineering overhead.

That would be a successful `PARENT_SUFFICIENT`/negative result. The KSO architecture should survive scientifically by contracting to the parts that remain useful (e.g. correction, auditability, explicit transfer/revocation) rather than preserving a language-superiority narrative.
