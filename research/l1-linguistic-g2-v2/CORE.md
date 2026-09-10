# L1 linguistic G2 v2 — operator-scope microworld

**v1 frozen:** `research/l1-linguistic-g2-v1/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. Adj–Noun intersective construction,
restart, revocation, held-out combo. That capsule is not retuned and its
`RESULT.json` is not overwritten.

**Root cause of remaining OPEN/CANNOT_CHECK boxes:** v1's mechanism was a
single intersective Adj–Noun skill. It could not host negation, quantifier
scope, warrant-separated polysemy, or sortal selection, so those L1 (#43)
boxes stayed `CANNOT_CHECK_NOT_IN_MICROWORLD` / `OPEN` even though they are
honestly microworld-checkable.

**v2 mechanism (changed, not a salt retune):** exact clause constructions
over typed NP phrases, using first-class `NEGATES` and `SCOPES_OVER` edges.
A small lexicon keeps two senses of one lemma as an ambiguity set; evidence
selects, `mutant_merge_senses` is the planted collapse. Correction/revocation
is extended: dependent interpretations reopen, unrelated constructions stay,
alternate support restores. Restart reloads the persisted lexicon; it does not
re-teach from source. New salts; v1 surfaces excluded.

Not corpus-scale N1. UD alignment and open-weight LM remain
`CANNOT_CHECK`. L2/L3 remain locked.
