# OCM_ACQUISITION_V1 — continual language acquisition (M5)

Status: engineering spec for `src/ocm/learning/language/`; theory in ORION-V2 batch 2 (B2 per-input
version-space warrant, B3 gap-learning soundness) and batch 3 (C6 discriminating-interaction
certificate). Obligations: `docs/theorems/OCM_ACQUISITION_OBLIGATION_REGISTRY_V1.json`. No claim.

## 1. The ladder, as built

learn linguistic knowledge (lexemes, senses, morphology, constructions — M3 objects) → learn
communication procedures (M4 acts and gate) → learn language-learning strategies (the active
learner chooses information-seeking actions; morphology compares registered strategies). Every
learned object carries provenance (evidence ids), channel, scope (language / domain / register),
dependencies (⊗ warrant), counterexamples (exceptions, nogoods) and lineage (relearn).

## 2. Regimes, kept separate (`evaluation/m5_acquisition_eval.py`)

| regime | information disclosed | mechanism | receipt (protected 134; held-out lexeme subset 97) |
|---|---|---|---|
| frozen system | — | seed inventory minus the transitive construction; lexicon minus dog/book/find | 22/134 |
| E0 explicit lessons | 6 lessons + 1 checking demo | instruction names SVO (refuted by a contradicting demo); dictionary entries; explicit irregular rule | 134/134; held-out 97/97 |
| E1 aligned demonstrations | 7 demonstrations (1 pins SVO among 6 orders; 3 leakage-checked teacher examples with one unknown token each; 3 paradigm pairs) | version space over {NP,V,NP} orders; exact alignment; hybrid morphology | 115/134; held-out 78/97 (the surface *found* is learned as a past-tense form; its participle reading needs a passive demonstration) |
| E2 raw corpus | 661 words, no annotation | 88 form hypotheses (token / suffix / collocation), 0 consultable | 22/134 — semantic gain exactly 0 |
| E3 grounded interaction | 1 outcome observation | registered outcome function ("entity acted on") eliminates 5 of 6 orders | 37/134 (construction only; no lexemes) |
| E4 curricula | fixed orders | raw→demos→interaction 115; lessons→interaction→raw 134; interaction-first 134; demos-only 115 | learning curves in the receipt |

Retention after E1: new gain 93/112, old loss 0/22, unrelated change 0/22. Negative transfer:
the SOV mini-language under the English inventory is UNKNOWN_CONSTRUCTION; the forced-order
hostile does not give correct roles; SOV is learned from two demonstrations with meaning graphs
intact.

## 3. Learned-object lifecycles

* **Lexeme / sense** (`lexical.py`, KS-T51): align one unknown token to one unaccounted node;
  warrant = the demonstration; second sense = ambiguity set; revoke one sense locally; relearn
  with lineage. Refusals: TOO_MANY_UNKNOWN, NO_UNACCOUNTED_NODE, AMBIGUOUS_ALIGNMENT.
* **Morphology** (`morphology.py`, KS-T52): RULE / ANALOGY / HYBRID over a suffix-rewrite class;
  exceptions under the override law; SPLIT_RECOMMENDED when exceptions exceed the registered
  fraction; ablaut is outside the class and is recorded as such.
* **Construction** (M3 `acquisition.py`, KS-T39): version space over a finite pattern class.
* **Corpus form** (`corpus.py`, KS-T53): UNGROUNDED_FORM_ONLY → CANDIDATE_SEMANTIC_BINDING →
  GROUNDED_CONSTRUCTION only through aligned evidence; CONTRADICTED / REVOKED.
* **Interaction** (`interaction.py`, KS-T54): registered outcome functions; success bits are
  FEEDBACK (behaviour only).
* **Active learning** (`active.py`, KS-T55): expected elimination per cost; gold label prohibited.
* **Transfer / retention** (`transfer.py`, KS-T56/T57).

## 4. Data custody

Project Gutenberg (five public-domain texts, hash manifest, body word counts) and BabyLM
(`CANNOT_CHECK_BABYLM_DATA`: release/terms must be checked at execution time) —
`docs/provenance/*_CUSTODY_MANIFEST_V1.json`. UD EWT, BLiMP, MultiWOZ from M3/M4. No data in
the repo; no result on any of them is claimed (KS-T59 OPEN).

## 5. Hostiles (all detected in `tests/m5`)

co-occurrence treated as grounding; frequency promoted to world truth; success bit laundered as an
observation; general rule overriding a stored exception; gold label requested by the active
learner; English word order relabelled onto SOV.

## 6. Known limits (ledger S17)

Aligned verbs are learned as surface forms with the meaning's tense; relating them to a base form
needs a paradigm pair (E1 morphology) or an explicit lesson (E0). Distributional clustering, idioms,
register/style objects, discourse conventions, CHILDES and BabyLM runs, matched comparators and
the 10M-word sample-efficiency experiment are not attempted here.
