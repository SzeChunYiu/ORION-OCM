# Archetype and venue contract (pipeline round 2, 2026-09-05)

Scope: this file resolves the paper archetype, the exact target tuple and the target ladder for the OCM manuscript. It carries no acceptance probability and no editor or reviewer favourability judgement; those are outside what a contract may assert.

## 1. Archetype

| Field | Value |
|---|---|
| Dominant archetype | methods and evaluation paper (atlas class D/E): a method (KnowledgeSpace runtime) plus a pre-registered matched-comparison evaluation |
| Secondary archetypes | negative-results / parent-sufficiency reporting; system-and-theory coupling (theory batches as obligations) |
| Publication objective | successful publication of the whole-programme paper (not one immovable venue) |
| Project phase | manuscript; all protected outcomes accessed; no Registered Report route is eligible (Stage 1 ineligible by prior result access; recorded, not backdated) |
| Intended reader | cross-domain AI engineers and researchers who work on knowledge representation, provenance, evaluation methodology and governed self-modifying systems |
| Evidence maturity | L2 on the external-validity ladder (protected synthetic holdout streams inside an authored bounded world); no L3+ evidence |
| Study-conduct state | protocols frozen before outcome (hash-bound pre-registrations); deviations recorded (ledger rows S22–S24, S27, S31–S33, S36–S38); post-freeze runtime revalidation reopened M11 adoption cells and M12 phase G (2026-09-05) |

## 2. Exact target tuple resolution

Resolution order applied: live official-source contract (not performed this round: web access was restricted to bibliographic verification), then an active maintained exact snapshot, then a labelled non-exact fallback.

| Candidate (from the paper plan §5) | Article type | Resolution mode | Hard-format facts available | Fit note |
|---|---|---|---|---|
| Nature Machine Intelligence | Article | maintained snapshot (`nature-shared/journal-formats/nature-machine-intelligence.md`; validity window not re-verified live today) | main text ≤ 3,500 words excluding abstract, Methods, references and legends; abstract ≤ 150 words unreferenced; ≤ 6 display items; ~50 references; Introduction/Results/Discussion/Methods | the current draft (≈ 9,000 prose words, 10 tables) is a long-form paper; an NMI Article would need a main text of ≤ 3,500 words with the methodology, the theory loop and most tables moved to Methods and Supplementary Information, and 4 of the 10 tables merged or dropped |
| PNAS | Research Article (Direct Submission) | non-exact fallback (`profile_is_not_venue_policy`; limits not verified live) | PNAS research articles are short-form with SI | same compression requirement as NMI; fit for a broad-readership venue depends on the significance case, which the manuscript deliberately does not overstate |
| Journal of Machine Learning Research | long-form article | non-exact fallback (`profile_is_not_venue_policy`) | no fixed length limit; theory appendices welcome | the current draft's length and theory appendix fit; JMLR's scope is machine learning, so the fit question is whether a knowledge-representation runtime with a matched-comparison evaluation is in scope; unresolved without live research |
| Artificial Intelligence Journal / Machine Learning (companion for the theory batches) | regular article | non-exact fallback | long-form permitted | the theory batches (89 checked items) could be a companion paper; this would split the programme paper into two, with the runtime paper citing the theory paper |
| Transactions on Machine Learning Research | Research Paper | maintained snapshot exists (`tmlr-research-paper-2026-08-28.json`) | claims-and-evidence review model; claim reduction is an explicit repair route | strong methodological fit for a paper whose central discipline is claim-bounded evidence; the venue's audience-interest bar is low by policy; not in the paper plan's list and added here as a robust-fit rung |

Target ladder (fit-first, not prestige-ordered):

```text
stretch_but_compatible : Nature Machine Intelligence Article (requires the 3,500-word compression and a Methods/SI split)
best_fit               : JMLR long-form article, subject to a live scope check
robust_fit             : TMLR Research Paper (claims-and-evidence model matches the receipt discipline)
specialist_fallback    : Artificial Intelligence Journal (runtime + evaluation), with the theory batches as a companion in Machine Learning or AIJ
alternative_article_type : a Resource/Analysis-type submission that foregrounds the evaluation methodology and the parent-sufficiency table
Registered Report      : not eligible (outcomes already accessed)
```

## 3. Gates the contract exposes

| Gate | State | Note |
|---|---|---|
| scientific / integrity | open for the self-repair families | M11 adoption cells and M12 phase G are reopened by the 2026-09-05 revalidation; the manuscript reports this; protected re-evaluation is the closure test |
| exact target scope / article type | uncertain | no live official-source resolution this round; NMI snapshot shows a hard length mismatch with the current draft |
| novelty / impact / breadth (selective venues only) | not claimed | the manuscript makes no novelty claim by design; a selective broad-interest venue's independent novelty gate is therefore a target-objective mismatch risk, not a manuscript defect |
| burden of doubt | manuscript-side | every undetermined family is reported as undetermined; the paper does not ask the venue to resolve doubt in its favour |
| allowed repair routes | narrow claim, relocate to SI, change article type or venue | all three are open; no new experiment is required for the language results; the self-repair results need a protected re-run (author evidence) |
| review model | unresolved per venue | NMI: single-blind editor-led; TMLR: action-editor claims-and-evidence; others not resolved |
| AI-use policy | satisfied in principle | Methods summary discloses language-model drafting assistance and human accountability; the exact disclosure form is venue-specific |
| certification layer | n.a. | no venue certification is sought or claimed |

## 4. Provenance

Sources consulted: `docs/paper/OCM_PAPER_PLAN_V1.md` §5 (candidate list); `nature-shared/journal-formats/nature-machine-intelligence.md` (maintained snapshot, format facts); `nature-shared/journal-formats/decision-contracts/profiles/tmlr-research-paper-2026-08-28.json` (maintained snapshot); no live venue page was opened this round. Effective dates for the fallback rows are therefore unknown and must be resolved live before submission. This contract does not predict the editorial outcome.
