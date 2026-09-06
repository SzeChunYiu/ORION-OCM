# N1 phase G — attachment evidence with refutation (ledger S43), 2026-09-06

Files: `N1_UD_INDUCTION_V4_ATTACHMENT.json` (gate over all three evidence classes) and `N1_UD_INDUCTION_V4_ATTACHMENT_STRICT.json` (LEXICAL class only); billy-old, no other job, 600 s per split; the same induction as phase F.

Evidence table (training split): 100,386 lexical (head lemma, relation, dependent lemma) triples, 81,525 attested once; 47,035 head-class and 31,374 dependent-class triples.

| gate (test split) | reached | refused outright | cap | cap share | ambiguous | exact derivations | gold among unpacked | INTERPRETED |
|---|---|---|---|---|---|---|---|---|
| none (phase F chart) | 404 | 37 | 79 | 20% | 16 | 1,176,931 | 1 | 0 |
| all three classes | 684 | 71 | 114 | 17% | 42 | 657,343 | 1 | 0 |
| LEXICAL only | 1372 | 174 | 213 | 16% | 60 | 9,673 | 4 | 0 |

Reading. Refutation works as designed: the strict gate cuts the exact derivation total by two orders of magnitude (1,176,931 → 9,673), refuses 174 sentences outright (an attachment attested nowhere) and lets the parser reach more sentences inside the budget. But no sentence receives a unique reading under any gate. The residual ambiguity is not attachment choice any more; it is the rule inventory's structural ambiguity — the same attested attachments can be grouped by different memorised rules (dependent order families, phrase-versus-clause variants of the same rule), and no attachment evidence distinguishes those. Whenever the gold tree is among the unpacked derivations the evidence-ranked first reading is it (4/4 on test, 11/11 on dev), which locates the remaining obstruction in the inventory, not in the evidence.

Terminal for phase G: NEGATIVE, reported as such; the S41 Jump was adopted (S43) and its outcome bounds what a finer *attachment* class can do. What batch 11 K1 (ii–iv) leaves as the only positive-data routes now reads as: (i) a finer *rule* class — one construction per (head, ordered dependents) family with the family's variants merged so that grouping is not a free choice — or (ii) a negative or membership channel. N1 stays NEGATIVE at its stated scope; N2 stays locked.
