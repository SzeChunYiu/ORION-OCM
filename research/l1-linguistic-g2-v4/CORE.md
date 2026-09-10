# L1 linguistic G2 v4 — morphology, planted UD, curves, tree bound

**v1 frozen:** `research/l1-linguistic-g2-v1/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. Adj–Noun intersective construction.
That capsule is not retuned and its `RESULT.json` is not overwritten.

**v2 frozen:** `research/l1-linguistic-g2-v2/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. Operator-scope / typed NP / polysemy /
negation / quantifier. Those boxes are **cited, not reticked**. That capsule is
not retuned and its `RESULT.json` is not overwritten.

**v3 frozen:** `research/l1-linguistic-g2-v3/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. SOV hostile + held-out families
`NO_CROSS_FAMILY_TRANSFER`. Those boxes are **cited, not reticked**. That
capsule is not retuned and its `RESULT.json` is not overwritten.

**Root cause of remaining OPEN/CANNOT_CHECK boxes:** v1–v3 never induced
morphology, never planted a UD-like treebank, never recorded an acquisition
curve with N>2, never measured a meaning graph above `MAX_EXACT_CANONICAL=7`,
and never froze/learned lexical realization. Those L1 (and microworld-checkable
L2-listed) boxes stayed `CANNOT_CHECK` even though they are honestly
microworld-checkable with production `ocm.language.acquisition`,
`ocm.learning.language.morphology`, `ocm.learning.language.ud` (CoNLL-U reader +
gold mapping), `ocm.language.meaning_tree.canonical_any`, and
`ocm.language.realize._form`.

**v4 mechanism (changed, not a salt retune):**

1. **Morphology / agreement.** Finite suffix-rule version space
   (`ocm.learning.language.morphology`, HYBRID) from (lemma, form) pairs.
   Productive `-ed` / `-s` plus warranted exceptions. Number-agreeing present
   constructions (sg/pl) reject mismatch. Exception override law: live
   irregular wins; `mutant_rule_overrides_exception` is the planted collapse.
2. **Planted UD-like treebank.** Tiny CoNLL-U files read by production
   `ud.read_conllu`. Alignment is teacher-annotated: `ud.gold_meaning` maps
   `nsubj→ROLE:agent`, `obj→ROLE:patient` on `is_simple_clause` sentences.
   Held-out 3-token clauses match after construction acquisition. An amod
   clause is gold-mapped but uninterpreted without an NP helper
   (incomplete mapping). A non-simple `aux` clause is `is_simple_clause=False`.
   **No UD parser** (no Stanza/spaCy/udpipe): trees are planted, not predicted.
   Corpus UD is not claimed.
3. **Acquisition curves.** Held-out regular-form accuracy vs number of past
   pairs `{0,1,2,4,8}`. Irregulars in training become exceptions; held-out
   irregulars are over-regularised by the productive rule. Miniature N, not
   a corpus developmental curve.
4. **Exact canonicalization.** `|V|≤7` still uses `meaning.canonical`.
5. **Meaning graphs beyond the historical bound.** Production
   `meaning_tree.canonical_any` is exact for rooted trees (AHU). This study
   registers a **finite** tree bound `EXPLICIT_TREE_CANONICAL_BOUND=12` and
   measures trees with 9 and 11 nodes. Non-trees above 7 remain
   `CANNOT_CHECK`. The interpret pipeline is not claimed above 7.
   `MAX_EXACT_CANONICAL` in `src` is not edited.
6. **Realization bootstrap frozen / lexical realization learned.** Seed
   realizer templates in `realize.py` / `seed_constructions` are enumerated
   and charged as prior. Lemma→form uses induced `MorphRule`s; every surface
   is reverse-read. Neural realizer is `CANNOT_CHECK_NO_NN_LIBRARY`.
7. **Questions and modality** acquired as new construction families (`ASKS`,
   `MODALITY`). Negation is cited from v2, not copied.

New salts; v1–v3 content surfaces excluded. Not corpus-scale N1. No open-weight
LM. L2/L3 remain locked (`l2_started=false`): microworld checks of
morphology/realization/questions are not N2 learned speaking.
