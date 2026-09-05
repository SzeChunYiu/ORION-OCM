# M8 — learned KnowledgeSpace organisation: study report

Date 2026-09-05. Terminal claimed: **PARENT_SUFFICIENT at this scale** (admissible per issue #10).
Study status: exploratory at the synthetic scale below (the study was run once on frozen-seed
worlds without a separate pre-registration document; a `M8_LEARNED_ORGANIZATION_SUPPORTED`
claim would require a pre-registered residual on held-out tasks, which this study does not
make). R5 (sheaf) and R7 (continuous) are `CANNOT_CHECK` dispositions. No novelty claim.

## 1. Arms (one KnowledgeSpace, identical task/evidence streams)

R0 flat · R1 hand tree from declared labels · R2 deterministic label-propagation communities with
shared-atom overlaps (never duplicated authority) · R3 R2 + macro summaries (`abstraction.summarize`)
· R4 fibred by scope contexts with declared transports · R6 learned: split/merge proposals scored on
dev tasks, adopted only when the predicted improvement is realised on held-out tasks with no
unpredicted regression and no free growth; learner cost counted.

## 2. Synthetic oracle worlds (4 latent regions × 8 atoms; 7 tasks each; exact recovery)

| family | flat work | R0 | R1 hand | R2 comm. | R3 nested | R4 fibred | R6 learned |
|---|---|---|---|---|---|---|---|
| clean hierarchy | 21.7 | 21.7 / 0 | 18.3 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 (0 adopted of 10) |
| overlapping communities | 32.0 | 32.0 / 0 | 21.7 / 1 | 32.0 / 0 | 32.0 / 0 | 13.7 / 1 | 18.3 / 0 (1 adopted of 1) |
| misleading hierarchy | 21.7 | 21.7 / 0 | 5.4 / 0 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 |
| dynamic topology | 21.7 | 21.7 / 0 | 18.3 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 |
| cross-domain bridges | 21.7 | 21.7 / 0 | 18.3 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 |
| revocation events | 21.7 | 21.7 / 0 | 18.3 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 | 11.4 / 4 |

Cells: mean atoms visited per task / latent regions recovered exactly (of 4). Task success is
1.0 for every arm on every family (the worlds are navigable by closure); after revoking the first
task's evidence, success is 0.86 for every arm (the revoked target is unreachable, nothing else
changes). Revocation-through-abstraction commutation: every region's macro liveness computed on
the pruned children equals the expected value; **live macro over dead children: 0** in all 6 × 6
cells (the hard failure of issue #10 §4 never occurs).

Readings. (i) Every organised arm halves flat navigation work on the hierarchical families while
recovering the oracle partition exactly — the parents (communities, summaries, fibres) already
achieve this; the learned arm adopts nothing beyond them (0 of 10 proposals realised an
improvement). (ii) On overlapping communities, label propagation fails (0 exact; recovery 0.27) —
a known parent limit; fibres recover 1 of 4 because scopes are per-region; the learned arm adopts
one merge that lowers its own navigation work from 32.0 to 18.3 without recovering the partition.
(iii) On the misleading family the hand tree's labels cut across regions: it recovers nothing yet
navigates cheaply (5.4) because the frozen tasks' endpoints happen to share labels — organisation
quality is task-ecology relative (issue #10 §9), and partition recovery must be reported beside
navigation work.

## 3. Language lifetime stream (167 atoms: lexemes, constructions, rules, facts; 18 retrieval tasks)

| arm | success | work | regions | overlaps | missed regions |
|---|---|---|---|---|---|
| flat closure | 1.0 | 4.6 | — | — | — |
| R0 | 1.0 | 4.6 | 1 | 0 | 0 |
| R1 hand tree (lexicon / grammar / knowledge) | 1.0 | 5.6 | 3 | 0 | 0 |
| R2 communities | 1.0 | 4.4 | 62 | 21 | 0 |
| R4 fibred (topic scopes) | 0.33 | 3.2 | 14 | 0 | 0.67 |

The stream is small and shallow: flat closure already costs 4.6 visits; communities fragment
(62 regions, 21 shared atoms) with no gain; fibres by topic split lexemes from facts and miss
two thirds of the targets (REFINE_REQUIRED, never a wrong answer) because no transports were
declared between fibres. Commutation holds in every region for every arm.

## 4. Hostiles (planted, detected)

Cached macro liveness (`mutant_macro_cache`), similarity as transport proof
(`mutant_transport_similarity_as_proof`), summary answering outside its certified scope
(`mutant_summary_answers_outside_scope`), complexity rewarded (`mutant_reward_complexity`),
cyclic / inconsistent containment (`containment_consistent`), labels leaked into the oracle
(the generator seeds structure independently of labels).

## 5. Parent subtraction

Communities: label propagation (Raghavan–Albert–Kumara 2007) — recovers hierarchical families
exactly, fails on overlaps (Leiden / ego-splitting are the stronger parents to add). Summaries:
Kemeny–Snell lumpability via `abstraction` (KS-T07b). Fibres: scope-indexed sub-spaces with
declared transports (Grothendieck-style indexing; no residual claimed). Learned topology: a
proposal/held-out loop over split/merge — at this scale it never beats the community parent.
The ORION residual, if any, must be in the evidence-governed coupling (macro liveness from
children, transport ⊗, revocation commutation), which held everywhere but was matched by the
parents' behaviour on these tasks.

## 6. Terminal and backlog

`PARENT_SUFFICIENT` at this scale. Backlog (negatives are leads): larger worlds where flat closure
is expensive and coarse activation can miss; an overlap-aware community parent; declared
transports on the language stream; overlap / promote-macro / drop-macro proposals; a
pre-registered held-out study before any SUPPORTED claim; theory batch 4 (D5 sufficiency
certificate, D7 multiscale coherence, D8 organisation-search admissibility) as the obligations.
