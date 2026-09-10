# L1 linguistic G2 v3 — SOV hostile and held-out families

**v1 frozen:** `research/l1-linguistic-g2-v1/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. Adj–Noun intersective construction.
That capsule is not retuned and its `RESULT.json` is not overwritten.

**v2 frozen:** `research/l1-linguistic-g2-v2/` terminal
`COMPOSITIONAL_LANGUAGE_LEARNING_ONLY`. Operator-scope / typed NP / polysemy.
That capsule is not retuned and its `RESULT.json` is not overwritten.

**Root cause of the two remaining OPEN/CANNOT_CHECK boxes:** v1 taught one
English-order Adj–Noun family; v2 taught every clause family it later probed.
Neither ran an SOV hostile, and neither trained one construction family then
tested a disjoint family. Those L1 (#43) boxes stayed
`CANNOT_CHECK_NOT_RUN_SOV_HERE` / `CANNOT_CHECK_FAMILIES_TAUGHT_EXPLICITLY`
even though they are microworld-checkable.

**v3 mechanism (changed, not a salt retune):** the production version-space
construction learner (`ocm.language.acquisition`) over the finite {S,V,O}
order class.

1. **Artificial / non-English structure.** English-order (SVO) constructions
   are acquired from SVO demonstrations. An SOV utterance under that inventory
   is `UNKNOWN_CONSTRUCTION` (detected, not forced into English roles). The
   planted word-order relabel hostile does not yield the gold meaning.
   The same hypothesis class acquires SOV from SOV demonstrations; meaning
   graphs stay intact; each order rejects the other.
2. **Held-out construction families.** Train only the transitive order family.
   Probe a disjoint negation family (`S not V O`) that is not in the {S,V,O}
   class. Transfer fails: the learner does not invent a new family. The
   negation family is separately acquirable from its own demonstrations, so
   the miss is transfer, not unlearnability. This is recorded as
   `NO_CROSS_FAMILY_TRANSFER` — mechanism, not a salt.

New salts; v1 and v2 content surfaces excluded. Not corpus-scale N1. UD
alignment and open-weight LM remain `CANNOT_CHECK`. L2/L3 remain locked.
