# Language KSO Real-World Stress Protocol V0

**State date:** 2026-09-04  
**Status:** prospective stress/evaluation protocol; no protected outcome has been run.  
**Purpose:** move Language KSO from finite SVO calibration to real language evidence without losing attribution, matched-parent comparison, or fail-closed semantics.

## 1. Central question

Can one long-lived Language KSO learn reusable linguistic structures from several evidence channels, generate meaning-preserving utterances on held-out real language, correct/revoke local knowledge without global retraining, and avoid harmful transfer — under matched data, interaction, memory, verifier and compute budgets against the strongest language-model and grammar-induction parents?

A positive answer is not assumed.

## 2. Evidence regimes — run separately before mixing

### E0 — explicit lesson

Structured grammar/dictionary lesson. Measures direct procedural acquisition and correction locality.

### E1 — aligned meaning <-> utterance

Semantic frame/graph plus sentence. Measures form-meaning construction induction and systematic recombination.

### E2 — raw text only

Books/articles/dialogue text with no privileged semantic labels. May create form/morphology/construction/style hypotheses but **must not silently acquire grounded denotation from an external model**.

### E3 — grounded interaction

World/task state plus utterance/action outcome. Used to discriminate semantic/pragmatic hypotheses. Endpoint task success remains utility feedback unless the interaction is genuinely discriminating.

### E4 — mixed curriculum

Combine E0–E3 after their individual information contributions are measured. The router should learn which evidence source is useful for which uncertainty rather than pooling them indiscriminately.

## 3. Public/real data candidates

Dataset use is gated by current license/access verification at experiment freeze.

### BabyLM 2026

Current challenge target: sample-efficient language learning under human-scale word budgets.

- Strict: <=100M words.
- Strict-Small: <=10M words.
- Multimodal and interactive/teacher-feedback evidence are permitted within the current strict tracks.
- New multilingual track includes English, Dutch and Chinese evaluation.

Use: matched whole-system sample-efficiency comparator. OCM storage/index/grammar/lexicon bits count in addition to immutable code.

### BLiMP

67 English grammatical phenomena datasets x 1,000 minimal pairs, covering morphology, syntax and syntax-semantics/semantics; CC BY.

Use: fine-grained **diagnostic only** for whether induced language structure respects agreement, argument structure, binding, control/raising, determiner-noun agreement, ellipsis, filler-gap constraints, etc. BLiMP success is not communication competence.

### Universal Dependencies — English EWT

Real English treebank over blog/social/review/email/web genres; current UD English EWT page states CC BY-SA 4.0.

Use:

- held-out structural analysis;
- construction/category discovery checks;
- real non-toy morphology and dependency patterns;
- genre transfer.

Do not give gold dependency trees to a raw-text arm.

### CHILDES / TalkBank

Real child/caregiver language with corpus-specific access/citation conditions. Current TalkBank access distinguishes open, registration-required and controlled resources. Most transcript/media data require registration; controlled subsets require additional approval.

Use:

- developmental/curriculum language exposure;
- dialogue adjacency;
- reference/repair/questions;
- child-directed language distribution;
- later speech/prosody channel when license permits.

Never copy a restricted corpus into the repository. Store content hashes, retrieval receipts and derived permitted statistics instead.

### Public-domain books

A curated public-domain literature set can test the user's `read books -> learn form/style` hypothesis. Project Gutenberg states that the vast majority of its ebooks are unrestricted by U.S. copyright, but use outside the U.S. must check local law and automated collection should use the documented mirrors/offline catalogs rather than roboting the main site.

Use: raw E2 form/style/discourse evidence only. Do not score memorized continuation of the same books as language intelligence.

## 4. Frozen train/development/protected separation

For each evidence regime freeze:

- exact corpus/item identities and content hashes;
- licensing/access receipt;
- token/word counting rule;
- vocabulary availability;
- annotations visible to each arm;
- training/induction split;
- development split;
- protected held-out constructions/lexemes/documents/speakers/genres;
- task and interaction budget;
- whole-system storage/compute accounting;
- comparators and their access.

No protected utterance or answer may tune thresholds, grammar inventories, routers, lexical maps or representation choices.

## 5. Stress matrix

### S1 — known construction, unseen lexical combination

The machine has seen the grammar but never the exact subject/predicate/object combination.

Expected: systematic composition, not memorized string retrieval.

### S2 — known lexicon, unseen construction

The words are known but a new grammatical construction is taught/demonstrated.

Expected: acquire the construction locally without relearning the lexicon.

### S3 — productive rule + exception

Regular morphology plus lexical exceptions.

Expected: productive generalization on unseen regular items, specific exception override, exact correction when exception evidence changes.

### S4 — ambiguity

Evidence is compatible with several constructions/lexical meanings.

Expected: preserve a hypothesis set or ask for discriminating evidence; do not collapse uncertainty to one arbitrary rule.

### S5 — negation/question/passive/relative clause

Move beyond SVO transitive calibration. Each added construction must have held-out examples and hostile near-misses.

### S6 — recursive embedding and long dependencies

Nested clauses and filler-gap/binding dependencies. Track work/depth, not only correctness.

### S7 — discourse/reference

Pronouns, discourse entities, given/new information, ellipsis and clarification.

Expected: use dialogue/world state rather than grammar alone.

### S8 — idiom/construction exception

Form whose interpretation or realization is not compositionally predictable from ordinary lexical rules.

Expected: learn scoped lexicalized construction; do not corrupt general grammar.

### S9 — register/style

Same meaning in formal/informal/technical/narrative styles.

Expected: style varies while semantic content remains invariant.

### S10 — cross-language transfer

Known semantic structure, new word order/morphology language.

Expected: transfer semantic roles/invariant task structure only where correspondence is warranted; refuse English-specific order/morphology transfer.

### S11 — code-switch / mixed register

Requires scoped selection from multiple language/register fibres without silently collapsing their grammar.

### S12 — contradictory sources

Two grammar/dictionary/corpus sources support incompatible rules.

Expected: preserve source/warrant distinction; a higher-frequency source cannot erase a live contradiction by vote.

### S13 — diachronic/environment drift

A usage pattern changes over time/register/community.

Expected: specialize scope or reopen the rule; do not globally overwrite historical validity.

### S14 — adversarial/malformed text

Noise, OCR-like corruption, ungrammatical forum text or malicious demonstrations.

Expected: proposal/uncertainty, not immediate grammar warrant.

### S15 — renderer laundering

Give a target surface string to a boundary component that is not authorized to supply semantic content.

Expected: reject/ignore answer injection; surface generator cannot smuggle task knowledge.

### S16 — evidence revocation

Revoke one grammar, lexicon, semantic or style item.

Expected: exactly dependent utterances/macros reopen; unrelated language abilities remain live.

### S17 — harmful transfer

A source construction is superficially similar but operationally wrong in target language/domain.

Expected: transfer refused or negative-transfer evidence lowers future routing; no silent persistence.

### S18 — real conversation lifetime

Long-lived dialogue with clarification, correction, topic shift, pronoun reference and learned vocabulary.

Measure whether future related turns become cheaper/better because reusable structure was learned.

## 6. Generation evaluation — never one-reference exact match alone

Separate at least:

- semantic/task fidelity;
- grammatical well-formedness;
- discourse/pragmatic appropriateness;
- lexical adequacy;
- morphology;
- construction applicability;
- naturalness/style;
- diversity without semantic drift;
- correction/revocation locality;
- trace attribution;
- resource cost.

For formal/controlled meaning graphs, use semantic equivalence or exact task consequence where possible. For open language, use multiple independent evaluators/human judgments and preserve `CANNOT_CHECK` when meaning/pragmatic fidelity cannot be decided reliably.

## 7. Acquisition-efficiency measures

For a capability family `f`, report a vector rather than one score:

`A_f = (examples, words, interactions, immutable_bits, mutable_bits, index_bits, train_work, inference_work, verifier_work, IO, errors, negative_transfer)`.

Primary lifetime question:

`cost_to_acquire_related_skill_{t+1} < cost_to_acquire_skill_t`

when reusable structure genuinely exists, while unrelated/superficially similar tasks should not receive false transfer.

## 8. Strongest comparator suite

Information- and budget-match at least:

1. current recurrent/frontier language model;
2. BabyLM-style LM trained under the same word budget;
3. computational Construction Grammar;
4. graph-to-text / synchronous hyperedge replacement grammar parent;
5. unsupervised grammar induction parent;
6. conventional NLG pipeline;
7. grammar-constrained neural generation;
8. KSO ablation without explicit evidence/revocation/transfer mechanisms.

A language-model parent may use neural internal structure; OCM does not get credit merely because its grammar is inspectable.

## 9. Representation tournament inside Language KSO

On the same semantic/generation tasks compare:

- school-grammar slot sketch;
- dependency representation;
- constituency representation;
- categorial grammar;
- Construction Grammar network;
- semantic graph + synchronous hyperedge-replacement grammar;
- learned latent/neural construction object behind the same KSO interface;
- hybrids.

The machine may eventually learn which representation to use. No representation wins by elegance.

## 10. Phase gates

```text
L0 controlled finite grammar             IMPLEMENTED on PR #302; CI authority pending
L1A explicit lesson real-data pilot       NOT_RUN
L1B aligned meaning/utterance pilot        NOT_RUN
L1C raw corpus induction                  NOT_RUN
L1D grounded joint induction              NOT_RUN
L1E mixed curriculum                      NOT_RUN
L2 dialogue/reference/repair               NOT_RUN
L3 multi-sentence/document planning        NOT_RUN
L4 cross-language/negative transfer        NOT_RUN
L5 open-domain grounding to general KSO    NOT_RUN
L6 naturalness/style                       NOT_RUN
L7 audio/prosody                           NOT_RUN
HUMAN_LEVEL_LANGUAGE                       NOT_ESTABLISHED
LANGUAGE_SUPERIORITY_OVER_MATCHED_LM       NOT_ESTABLISHED
GENERAL_NOVELTY                            NOT_ESTABLISHED
```

## 11. Kill conditions

Contract the language thesis if:

- corpus/grounded induction does not scale beyond toy hypothesis classes;
- explicit construction representations become brittle under real ambiguity/variation;
- matched LM/CxG/SHRG parents learn equivalent capability more efficiently;
- semantic checking requires an oracle as strong as the language system;
- naturalness gains require reintroducing an LLM that secretly does the core language task;
- hierarchy/transfer produces more negative transfer than benefit;
- revocation/correction becomes globally expensive at realistic scale.

A negative is a successful scientific outcome.
