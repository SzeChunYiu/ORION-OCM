# N1 phase E — evidence-licensed derivation ranking and the chart cap (2026-09-06)

Files: `N1_UD_INDUCTION_V2_RANKING.json` (cap 300,000 items) and `N1_UD_INDUCTION_V2_CAP1M.json` (cap 1,000,000 items; peak resident memory 789 MB, wall 40 min), both on billy-old with no other job, 600 s budget per split, same induction as `N1_UD_INDUCTION_V1.json`.

Ranking rule: a derivation scores the minimum demonstration count over the constructions it uses; the best score is kept across packings; AMBIGUOUS results are reported ranked. The rule is a report and never a licence (AMBIGUOUS stays AMBIGUOUS).

| Split (cap 300k) | reached | AMBIGUOUS | ranked | top unique | gold among unpacked | top is gold |
|---|---|---|---|---|---|---|
| dev | 1,539 | 31 | 31 | 29 | 6 | 6 |
| test | 1,606 | 37 | 37 | 35 | 4 | 4 |

Reading: whenever the gold tree is among the unpacked derivations, the evidence-ranked first reading is the gold one (10 of 10). But the gold tree is among the unpacked derivations in only 10 of 68 ambiguous sentences; in the other 58 the ranking selects a unique top derivation that is not the gold tree (or the gold tree is outside the eight unpacked). Evidence ranking therefore does not resolve attachment ambiguity on web English; it orders readings the grammar already admits. INTERPRETED remains 0.

Cap study: raising the cap from 300,000 to 1,000,000 items lets each sentence consume more time, so fewer sentences are reached inside the budget (test 571 vs 1,606) and the cap is still hit on 127 of 571 (22% vs 25%). The attachment blow-up is not a cap artefact; it is the learned grammar admitting every attachment (single-order families with no selectional or lexical preference). Memory stays under 0.8 GB at the 1M cap.

Terminal for phase E: NEGATIVE, reported as such. Next lever named: the grammar, not the parser — lexicalised attachment evidence (which head attaches which dependent, learned from the demonstrations as per-lexeme evidence) so that most attachments are refuted rather than ranked; that is a representation change and goes through the Jump interface (ledger row to follow).
