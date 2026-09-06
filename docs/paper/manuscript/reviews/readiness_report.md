# Readiness report (pipeline round 2, 2026-09-05)

Manuscript: docs/paper/manuscript/main.md, draft V3.1 (V3 plus the round-2b repairs). Pipeline: academic-paper-pipeline v1.23.0 with the always-load contracts (execution kernel, context routing, iteration pipeline, paper-existence gate, ethics) and the atomic-claim, statistical-inference, editor-reviewer, acceptance-readiness, venue-decision and surface-QA contracts; prose craft under the vendored nature-writing, nature-polishing, nature-citation, nature-figure and nature-data skills and PAPER_WRITING_SKILLS_PROTOCOL_V1. This report is a simulation of readiness; it does not predict an editorial outcome and carries no acceptance probability.

## 1. Archetype and venue contract

Archetype: methods and evaluation paper with a pre-registered matched comparison and a negative-results section; secondary: system-and-theory coupling. Reader: cross-domain AI engineers and researchers. Evidence level: L2 (protected synthetic holdout inside one authored world), replicated on a second host.

Target ladder (fit-first; details and provenance in reviews/venue_contract.md): stretch Nature Machine Intelligence Article (needs a 3,500-word main text, six displays, Methods and SI split; the current draft is long-form), best fit JMLR long-form article (scope check pending), robust fit TMLR Research Paper (claims-and-evidence model), specialist fallback Artificial Intelligence Journal with the theory batches as a companion paper. Registered Report: not eligible (outcomes accessed). No live official-source venue resolution was performed this round; the NMI and TMLR rows rest on maintained snapshots, the others are labelled non-exact fallbacks.

## 2. Gate-by-gate status

| Gate | Status | Evidence / remaining action |
|---|---|---|
| paper existence and scientific mass | WRITE_FULL_PAPER, long-form; top-tier route not yet earned | surviving object: a matched-comparison discipline (hash-bound pre-registration, matched information and acceptance discipline, exact tests with named scales, kill gates, hostile mutants, second-host replication) producing a mixed terminal table over twelve milestones, plus one replicated lifetime-level residual on one family; effective independent N for that residual is 8 paired lifetimes whose differences take two values; parent-sufficient results are results; G9 designer's-advantage risk stated in §9 |
| study protocol and conduct | passed with recorded deviations | pre-registration hashes bound before outcome; V1 runs relabelled development calibration (ledger S22–S24, S27, S31–S33); custody gap S36 and rule defect S37 disclosed; post-freeze runtime defect (adoption binding) disclosed and its cells reopened |
| data integrity and stewardship | passed for the frozen receipts; one design obligation open | receipts unchanged and hash-bound; dataset custody manifests present with licences; cross-domain transfer cells unequal (6 vs 4) recorded as an evaluation-design obligation; no persistent archive identifier yet (R3-6) |
| statistical inference and uncertainty | passed for the reported surfaces | see §3 below |
| atomic claim verification | passed | claims_map.md 246 rows; tools/paper/verify_claims.py: 246 OK, 0 MISMATCH, 0 MISSING_FILE, 0 PHRASE_MISSING, 0 UNCHECKABLE (claims_verification.txt); checker validated on real data with planted defects (one wrong number, one wrong phrase, one missing file, one wrong string: all four caught, exit 1); 9 rows carry a documented derivation beside machine checks; the single [NOT MEASURED] cell (Table 2, E4 held-out) has a row saying why |
| figures, tables and displays | plan only | figures.md: 8 main and 2 supplementary figure contracts bound to receipt fields, no plot executed, backend not chosen; 10 tables in the manuscript with unit, test and verdict tokens defined in captions; a six-display venue needs the fold described in figures.md |
| references | passed | 44 references; 37 DOIs verified against CrossRef, the Qwen2.5 report verified on arXiv (v2, 2025-01-03), the Biba report (MTR-3153, 1975; ESD-TR-76-372, 1977), the Kemeny–Snell 1976 Springer reprint (ISBN 978-0-387-90192-3), the Kish 1965 Wiley edition (ISBN 978-0-471-48900-9) and the Bar-Hillel–Perles–Shamir 1961 article verified by bibliographic search; the UD 2.14 handle resolved by redirect to LINDAT (landing page not retrieved, timed out twice); reference [1] (Bommasani et al.) removed as unnamed by any repository document; two references ([1], [15]) are repository documents and may need footnote form at some venues |
| editorial triage (five lenses) | repair_before_review for a short-form venue; send_to_review for a long-form venue after the two open publication-criteria items | reviews/editor_synthesis.md |
| independent review and editor synthesis | done | three blind reports (validity; contribution and positioning; reproducibility and clarity), 17 concerns classified, must-address items repaired or narrowed in round 2b, targeted re-review recorded in revision_log.md |
| revision closure | partial | closed: R1-1, R1-3, R1-4 (reporting), R1-5, R1-6, R2-2, R2-4, R3-2, R3-3, R3-5; narrowed: R1-2; open: R2-1, R2-3 (decision), R2-5 (optional), R3-1 and R3-4 (deferred clarity), R3-6 (archive) |
| manuscript budget | passed for the plan's bound; short-form venue not met | body prose 8,726 words (plan bound 6,000–9,000); 9,417 with headings, table captions and the header note; 11,528 excluding references with tables; 12,401 total |
| surface QA | draft state | no repository paths in prose outside Data availability; internal identifiers (obligation ids, batch items, ledger rows) remain by design in Sections 2, 7 and 8 and are glossed at first use elsewhere (R3-1 partial); header note is an author-facing line to remove at submission; no placeholders; en dashes used for ranges only; no em dashes |
| AI-use disclosure | stated | Methods summary discloses language-model drafting and editing assistance under the receipt-bound claim discipline and human accountability |
| human gates | closed by labelled proxy | reviewer simulation and editor synthesis are model proxies (HUMAN_GATE_BYPASSED__MODEL_PROXY); the blinded human rating protocol is reported as not run; no human evaluation is claimed |
| release-integrity binding | not done | no SHA256SUMS of the manuscript package bound to the receipt chain yet; the package (main.md, claims_map.md, claims_verification.txt, figures.md, README.md, reviews/*) exists on the paper branch only |

## 3. Statistics audit

| Item | Pre-registered | Manuscript | Verdict |
|---|---|---|---|
| M7 / V2 paired families | exact McNemar-style test on discordant pairs; δ = 0.05 on the paired rate difference; two one-sided tests at α = 0.05; residual iff one-sided test rejects and difference > δ; minimum n = 40 | Table 3, Table 6, §4; sub-40 families labelled descriptive with the receipt verdict INCONCLUSIVE defined in the Table 3 caption | matches the receipt and M7 pre-registration |
| unit of inference for V2 | items within one lifetime; O2/O3 descriptive only (S32) | §4, §5.9 | matches; block-dependence size (65/256 at block 6, n = 54) now reported from batch 6 F2 |
| V3 | exact two-sided sign test over 8 lifetime differences, ties dropped, α = 0.05; decision "≥ 1 family rejects" | Table 7, §5.10 | matches the V3 pre-registration; the S37 caveat (size 1/128, power 0.43, family bound ≤ 6, Bonferroni over 16) is reported and V3 is presented as a frozen record, not as the inference |
| V4 | one primary family, one-sided exact sign test, rejects iff ≥ 7 of 8 (size 9/256, power 0.81 at p = 0.9); six secondaries at α/6 (reject only at 8/8); collapsed-one-coin flag; decision on the primary alone | Table 8, §4, §5.11 | matches the V4 pre-registration and receipt; all six secondaries flagged; the primary family's differences take two values (0.3704 ×6, 0.3889 ×2), stated |
| equivalence claims | TOST at δ = 0.05 on the rate scale; discordant-scale equivalence needs n_d ≥ 76 (D1) | §4, §5.4 (ablations EQUIVALENT), §5.6 (n = 9 EQUIVALENT reported as undetermined under the minimum n) | scales named; no P > α read as equivalence |
| replication | second host, deterministic block byte-identical | §5.9, §5.10, §5.11 | MATCH in all three replication receipts; block hashes cited by prefix |
| reference arm | descriptive only, never in a decision (F8) | §6, Table 9 | no test applied; grader disagreement (7 vs 3 licensed unknowns, 4 items) reported |
| multiplicity outside V4 | none pre-registered for the M7/V2 descriptive families | reported as descriptive | no confirmatory claim rests on them |

No asymptotic approximation is used; all sizes and powers are exact binomial values reproduced by the theory checkers (D1, F2, G8).

## 4. Remaining blockers, named honestly

Real blockers (no manuscript edit can close them):

1. **Protected re-evaluation of the self-repair cells under the corrected adoption gate** (M11 S1–S7; M12 V2 phase G; by shared harness also V3 and V4 phase G). Until then every self-repair number is a frozen receipt value under a reopened gate, as the manuscript now says. `blocked_on_author_evidence`.
2. **Prospectively matched cross-domain transfer cells** (currently 6 machine cells vs 4 parent cells). `blocked_on_author_evidence`.
3. ~~Positioning against contemporary systems with verified citations (R2-1)~~ closed in round 2 (Section 1.1); replaced by the mechanical blocker **R2-r2-1: one citation system** (author–year keys in 1.1 must be folded into the numbered References). Needs a literature pass; this round's web access was limited to verifying existing references. `research_literature`.
4. **Archived release with a persistent identifier** for code, data and receipts (R3-6). A pre-submission action.
5. **Venue-specific manuscript form** if a short-form venue is chosen (R2-3): a 3,500-word main text with Methods and SI. A target decision.
6. **Release-integrity binding**: SHA256SUMS of the manuscript package bound to the receipt chain, then a fresh verification pass in the mirror location.

Repository-state item for the lead: the paper branch (HEAD a08a864 plus this round's uncommitted edits) sits on 8e3df44, while origin/main is at 5352984 and later; the claim map reads the seven changed files from origin/main with the `main:` prefix, and the branch must be rebased before merge so that those sources are in the checkout.

Not blockers: the frontier-parent, human-rating and external-benchmark boundaries are structural and are reported as undetermined; the one-coin collapse of the secondary families is a reported result with a named next study; novelty is not claimed.

## 5. Terminal state

`current_claims_partly_established`: the primary-family lifetime residual, the language, dialogue, acquisition, organisation and work results are established at their stated scope and verified against receipts; the self-repair and cross-domain transfer results are reported but not established pending author evidence. Decision-ready for a long-form venue once items 3 and 4 close; not `simulated_publication_ready_for_target`; not `submission_ready`.

## V5 addendum (2026-09-06)

Blocker 1 (protected re-evaluation of the self-repair cells): the historical M11 V1 and M12 V2 phase-G cells remain reopened and are reported as such; the V5 self-repair family is pre-registered as categorical, so no inferential self-repair claim rests on them. Blocker 2 (prospectively matched transfer cells): closed by V5 (6 vs 6 cells, categorical). The lifetime residual now has a study of record on the corrected runtime (V5: OCM_LIFETIME_RESIDUAL_SUPPORTED, replication MATCH). Terminal state unchanged in kind, `current_claims_partly_established`, with the primary residual established at its stated scope on both the historical (V4) and the corrected (V5) runtime.

Acceptance-lane correction (2026-09-06, ORION-OCM #82): current scientific promotion of V5 is NOT_ESTABLISHED under the repository's acceptance ledger; the manuscript reports V5's pre-registered decision with that label and the freeze/replication evidence, and does not call it a promoted terminal. Terminal state unchanged: `current_claims_partly_established`.
