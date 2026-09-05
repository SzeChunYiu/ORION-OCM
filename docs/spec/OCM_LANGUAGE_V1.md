# OCM_LANGUAGE_V1 — language understanding as method acquisition (M3)

Status: engineering spec for the modules under `src/ocm/language/`; theory in ORION-V2
`KSO_LANGUAGE_PREREQUISITE_THEOREMS_BATCH2_V1.md` (B1–B4) and `KSO_ONE_DAY_THEOREMS_BATCH1_V1.md`
(T6). Obligations: `docs/theorems/OCM_LANGUAGE_OBLIGATION_REGISTRY_V1.json`. No novelty claim.

## 1. Thesis, in one line

A language is a set of **warranted procedures** (constructions, lexemes, morphology) that map
form to meaning fragments; the machine *acquires* them through the M2 learner from the same
evidence channels as any other method (instruction, demonstration, interaction, experimentation),
interprets by *composing* their warrants, and never returns a meaning it cannot warrant. Nothing
language-specific is constitution: categories, roles, node types and construction inventories are
registry data (`meaning.meaning_registry()`), so a non-human meaning organisation can replace them.

## 2. Objects

| object | module | warrant | theorem |
|---|---|---|---|
| `MeaningGraph` — typed hypergraph fragment; `canonical()` exact for ≤ 7 nodes else CANNOT_CHECK; `seed_from_meaning = seed ∘ can` | `meaning.py` | — | B4 / MEG-24 |
| `Lexeme`, `Sense` — senses are an **ambiguity set**, each with its own interval; never ⊕-merged | `lexicon.py` | per sense | T6 / MEG-26 |
| `MorphRule` PRODUCTIVE / EXCEPTION — a LIVE exception pre-empts the productive rule for its lemma (override law); revoking the exception's evidence reopens exactly the blocked forms | `lexicon.py` | per rule | KS-T22 |
| `Construction` — form pattern of `Slot`s (token or `phrase="NP"` recursive) + meaning template; `produces` for phrase-level constructions; language-scoped | `constructions.py` | learner output (⊗ of pinning demonstrations) | B2, B3 |
| `CandidateMeaning` — `Λ = Λ(construction) ⊗ ⨂ Λ(parts)`; a phrase carries its own ⊗ | `constructions.py` | derived | T6 |
| `Interpretation` — seven verdicts (§3) | `interpret.py` | derived | T6 |
| `SaidRecord` / `DialogueSession` — said(u,p) as OBSERVATION evidence with `speaker` authority and conversation scope; promotion only under the authority meet with a bridge | `interpret.py`, `session.py` | evidence | B1 / MEG-05 |
| `ConstructionFamily` + `acquire()` — finite pattern class, version-space learner, E0 instruction checked against E1 demonstrations | `acquisition.py` | VSW antichain | B2, B3 |
| microworld corpus, protected split by content hash before tuning | `microworld.py` | — | freeze-before-outcome |

## 3. Interpretation verdicts

`interpret(utterance)`: tokens → `Lexicon.analyse` (readings with ⊗ warrants; same-analysis
derivations merged as ⊕) → bottom-up `phrase_table` (NP …) → clause `match_constructions`
(whole-utterance) → candidates deduplicated by canonical digest (⊕) → nogood filter → `select`:

| verdict | condition | next |
|---|---|---|
| INTERPRETED | exactly one LIVE candidate, none UNKNOWN | record / answer |
| AMBIGUOUS | ≥ 2 LIVE or any UNKNOWN; candidates retained, ranked only for the clarification question | CLARIFY (collapse = INTERACTION evidence) |
| UNKNOWN_LEXEME | a token has no live reading (no spelling-similarity guess) | LEARN |
| UNKNOWN_CONSTRUCTION | readings exist, no construction consumes the utterance | LEARN (demonstration) |
| NEEDS_CONTEXT | an underspecified referent has no binding | ask / bind from discourse |
| CONTRADICTION | every candidate dies under a registered nogood | report |
| CANNOT_CHECK | a required check could not run | fail closed |

## 4. Acquisition (E0–E2)

A family registers a **finite** hypothesis class (e.g. the six {NP, V, NP} orders) and a query
family. Each demonstration `(utterance, meaning)` is an example: hypothesis h is consistent iff
parsing under h yields a meaning isomorphic to the demonstrated one. The M2 learner's rules apply
unchanged: no agreement → GAP_AMBIGUOUS (nothing promoted); inconsistent demonstrations →
CONTRADICTION (kept, never averaged); promotion iff agreement on the query family; warrant = ⊗ of
the pinning demonstrations (revoking one reopens exactly what depended on it). An instruction
names a hypothesis and is refuted by a contradicting demonstration.

## 5. Grounding boundary

Parsing success yields `said(speaker, meaning)` — an OBSERVATION with `Authority.of(speaker=1)`;
`world_truth` is 0 by construction and stays 0 under any composition of speakers (B1). Answers cite
the evidence they rest on and say "no independent warrant". Contradictory statements are both
kept. The only promotion is `promote_authority(said, bridge) = said.authority ⊓ bridge`.

## 6. Hostile controls (planted mutants, all detected in `tests/m3`)

`mutant_nearest_spelling` (hallucinated lexeme), `mutant_merge_senses` (⊕-merged polysemy),
`mutant_word_order_swap` (roles swapped), `mutant_drop_negation`, `mutant_force_top1` (ambiguity
collapsed by score), `mutant_promote_said_to_world_truth`, `mutant_transfer_to_other_language`
(scope relabel), `wl1_hash` as canonical form (C6 vs 2·C3 collision).

## 7. Evaluation (`research/ocm-m3/M3_MICROWORLD_EVAL_V1.json`)

Separate numbers, each with its denominator: construction identification, exact canonical-meaning
match, role-edge F1, negation and yes/no accuracy per family; ambiguity candidate-set recall and
false-collapse count; demonstrations required, held-out lexeme generalisation, revocation
locality; active/passive paraphrase equivalence. Authority: synthetic microworld with a given
vocabulary — it measures construction acquisition and interpretation, not real-language coverage.
Real-language custody: UD EWT r2.14 and six frozen BLiMP phenomena are fetched by script with hash
manifests (`docs/provenance/*_CUSTODY_MANIFEST_V1.json`); no data enters the repo; their
evaluators are M3 follow-ups and carry no result here.

## 8. Known limits (self-application ledger S11–S14)

Flat patterns cannot express modifiers (fixed by recursive NP constructions); the construction
inventory beyond the seed six (coordination, relative and embedded clauses, quantifiers,
anaphora) is not yet learned; lexical acquisition from context is not yet implemented (the
vocabulary is given); real-language parsing over UD EWT is not attempted in this milestone.
