# Section D, audited: every morphology class has been observed to win — which is not the same as having a phase law

Date: 2026-09-15. Bears on checklist section **D**, the six boxes of the form *"demonstrate at least one phase
law where X wins"*.
Witness: `gmi_microscope/phase_win_audit.py`. Receipt: `microscopes/results/STAGE_PHASE_WIN_V1.json`.

**Section D is actively being derived by another lane** (PRs #680, #685, #703). This audits what the corpus
already demonstrates and derives no new phase law.

## 1  Result

Across **319 winner records** in 459 derivation receipts, with **38 distinct winner values**:

| class | occurrences | example winners |
|---|---:|---|
| memory / retrieval | 17 | `exemplar`, `prototype`, `store` |
| symbolic / programmatic | 16 | `compile`, `rule`, `symbolic` |
| neural-like | 13 | `gated`, `parametric`, `register` |
| probabilistic | 11 | `simulate` |
| search / planning | 10 | `act&observe`, `search` |
| **hybrid** | **3** | `differentiated` |

**All six classes have been observed to win somewhere.**

## 2  What this does **not** establish

Section D's boxes ask for a **phase law**, and a winner value is not one. It shows a class won in *some
cell*. A phase law additionally requires the **boundary** to be derived and frozen — which is precisely the
work the other lane is doing.

So the honest reading is: *"has been observed to win"* is satisfied six times over; *"has a phase law"* is a
strictly stronger claim this audit does not touch, and **these boxes should not be ticked on this evidence.**

## 3  Why the assignment is deliberately incomplete

Classifying all 38 winner values into six buckets would be judgement-heavy and contestable. It is also
unnecessary: the question is **existence**, so only unambiguous winners need assigning.

**24 of 38 values are left unassigned** — `dynamic`, `expand`, `forward`, `generators`, `maintain`,
`modularize`, `history` and others whose class is genuinely arguable. An unassigned value **cannot create a
positive finding**; at worst it hides one, which is the safe direction to err. A pin asserts the unassigned
set stays non-empty, because an assignment that classified all 38 would be straining, and straining is how a
positive finding becomes an artefact.

This is the same lesson as the three pattern bugs earlier in this corpus, applied before rather than after:
where a mapping is contestable, do not make it and say so.

## 4  Hybrid is the thinnest, and stays flagged

Hybrid rests on **3 occurrences of a single winner value** (`differentiated`), against 10–17 for the other
five. It clears the existence bar but does so on the least evidence, and a pin fails if that quietly grows
without the document being updated — so the weakness cannot decay into an unexamined "all six are equally
supported".

## 5  Scope

Winner records are read from receipt keys matching `winner|wins|cheaper|best|dominant|argmin|winning`.
Corpus-audit receipts are excluded by their `corpus_audit` declaration, so this audit does not count other
audits' outputs. Presence of a win says nothing about the size of the region in which the class wins, nor
about whether that region was predicted in advance.
