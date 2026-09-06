# Reviewer 1, round 2 (validity, methods, data, inference)

Written against manuscript draft V3.3 and the receipt-bound files it cites, blind to the other round-2 reports. Scope: the text added since V3.1 (Section 1.1, the V4-R paragraph in 5.9, Section 5.10, the batch-8 sentences in Section 8, the revalidation paragraph in Section 9). Round-1 items R1-1 to R1-6 are not reopened.

## Assessment of the additions

**V4-R (5.9).** The paragraph does what the receipt licenses and no more: the same eight frozen streams, the same rule, the corrected runtime, and the decision label CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION read from `deterministic.decision`, with the pre-registered rule reported as a diagnostic. The three difference values (0.370, 0.389, 0.407) match the `diffs` array. The statement that V4-R "confirms that the V4 primary residual survives the corrected gate" is a statement about the engineering regression and is correctly bounded by the sentence that follows. No inferential weight is added; none should be. Accept.

**Open-vocabulary result (5.10).** The negative is stated as a negative and the two-stage attribution is supported by the two receipt blocks (`protected_chart`, `protected_chart_gaps`). One methodological defect: the counts of sentences reached inside the 600-second budget depend on host load (1,839 in an earlier run, 1,664 in the receipt of record), so the absolute verdict counts are not a reproducible measurement. The text now says so, which is honest, but a budget-dependent count should not be the headline number. **R1-r2-1 (major, closable):** report the outcome on a fixed, load-independent unit, either the verdict distribution as proportions of the sentences reached, or a re-run without a time budget on a declared fixed subset (the first N sentences), and keep the absolute counts in the receipt only. Until then the 5.10 numbers are descriptive of one run.

**Batch 8 (Section 8).** The sentence claims four closures "with the same discipline". The batch-8 checker and tests exist in ORION-V2 at the merge commit of PR #359; the ORION-OCM consequence (commitment-gate epoch refusal) has a regression test. Accept. **R1-r2-2 (minor):** name the ORION-V2 commit for batch 8 in the data-availability statement as is done for batches 1 to 7.

**Revalidation paragraph (Section 9).** Correct and now consistent with 5.9: V4-R is engineering evidence; V5 is the only route to a scientific terminal on the corrected runtime. Accept.

## Recommendation
Minor revision. R1-r2-1 must be closed before submission; R1-r2-2 is editorial.
