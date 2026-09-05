# Reviewer 3 (reproducibility, reporting, clarity, boundaries, readership)

Written from scratch against manuscript draft V3, the receipts and the claim map; blind to the other reports. Lens: can a reader outside the project reproduce the artifact and follow the argument; are the boundaries visible where the reader needs them; is the reporting complete. Recommendation posture: minor-to-major revision on reporting and clarity; the reproducibility record is stronger than most.

## Overall assessment

The reproducibility record is exceptional for a systems paper: hash-bound receipts, pre-registration hashes read before outcome, byte-identical replication on a second host, a claim map that resolves every number to a receipt field, and a script that checks it. The clarity problems are the mirror image of that strength: the prose is dense with project vocabulary (terminals, families, receipts, rows Sn, batches, obligation ids), the results sections read as number dumps in places, and a reader who has not seen the repository cannot always tell which sentence is the result and which is the audit trail. The boundaries are honest and complete, including the late runtime revalidation.

## Major concerns

**R3-1 (must address, reader-facing vocabulary).** Internal identifiers appear throughout the results: obligation ids (KS-T21, KS-T116), theory item ids (batch 2, B5), ledger rows (S27, S37), phase letters (A to G), arm names (R0 to R6 in the figure plan). Each is defined somewhere, but the reader must hold thirty of them. Resolution test: keep obligation ids in Section 2 (where they are the objects of the theorems) and in Table 10; replace batch-item citations in the prose with the theorem's content ("the budget-bracket theorem") and put the id in parentheses only where a reader would need to find it; replace ledger row numbers in Sections 4 to 6 with a short description and keep the row numbers in Section 7 only.

**R3-2 (must address, standalone surfaces).** The abstract uses "matched parent", "primary family", "one coin", "ties" and "parent-sufficient" before any definition. Resolution test: rewrite the abstract's third and fourth sentences so that each term is glossed on first use in the abstract itself ("the strongest comparator buildable from known components with the same information", "families whose eight lifetime differences are identical and so carry the evidence of one coin").

**R3-3 (must address, table captions).** Tables 6, 7 and 8 have captions that name the receipt field but not the statistical unit, the test or the meaning of the verdict column. Resolution test: each caption states the unit (turn, lifetime), the test (exact McNemar-style paired test; exact sign test, two-sided or one-sided), α and the family role, and defines the verdict tokens once.

**R3-4 (major, results register).** Sections 5.2, 5.7 and 5.8 are lists of counts. A reader needs, per paragraph, the question the counts answer and the one sentence of meaning. Resolution test: open each results paragraph with the question ("Does the frozen system reach exact meaning on protected utterances?") and close it with the bounded meaning; keep the counts, they are the evidence.

**R3-5 (major, the revalidation).** The 2026-09-05 runtime revalidation is reported in Sections 3, 5.8, 5.9, 5.11 and 9, five places. It should be reported in one place fully (Section 9 is right) and referenced from the others in one clause each, so the reader is not told the same fact five times with slightly different wording. Resolution test: one full paragraph in Section 9, one sentence after Table 1, one sentence and the table row in Section 5.8, one clause in Sections 5.9 and 5.11.

**R3-6 (major, availability).** The Data and code availability section lists repository paths but no persistent identifier, release tag or archived snapshot; "canonical repository ORION-OCM" is not resolvable by a reader. Resolution test: name the repository host and an archived release (DOI or tagged commit) before submission; until then, state that the archive is pending. Also state the licence of the code and of the authored datasets.

## Minor comments

- The header note ("Manuscript draft V3 ... Claim authority rests with the receipt chain") is an author-facing note and must be removed from the submitted manuscript.
- Table 1's terminal column uses machine tokens (M0_CANONICAL_REPO_GREEN); a submitted version should gloss each token or replace it with a short phrase and keep tokens in a supplementary mapping.
- "0 of 6,000 BLiMP pairs" uses a thousands separator while "225,792" and "128,000" do too, but "10⁴ atoms" and "10⁵-atom" use exponents; pick one convention for large integers.
- Section 5.5 gives navigation work to one decimal (21.7, 11.4, 5.4, 4.6) while the receipt stores more; state the rounding once.
- Section 6's "asserted an answer to 237 of the 240" is followed by "the summary grader counts 7 honest unknowns"; the reader needs 240 − 237 = 3 spelled out to see the 4-item disagreement.
- The figure plan (figures.md) is not part of the manuscript; if the figures are not produced before submission, the manuscript should not promise "Figure 6" anywhere (it does not, which is correct, but the plan says eight main figures exist "planned").
- Reference [1] and [15] are repository documents; give them stable URLs or move them to Data availability.

## Reproducibility check performed

I ran the claim-verification script over the claim map: 241 rows, 239 checked by machine against receipt fields or document text, 2 with a documented derivation beside machine checks, 0 mismatches, 0 missing files, 0 missing phrases (docs/paper/manuscript/claims_verification.txt). I did not run any evaluation or test suite; the replication claims are taken from the replication receipts, whose two hosts and SHA-256 blocks I read.
