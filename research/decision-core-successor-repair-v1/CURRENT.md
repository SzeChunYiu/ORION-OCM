# Exact decision-parent correction — current result

**Accepted within the bounded helper scope.** Read the independent
[review](independent-review/REVIEW.md), then the [helper](decision_core.py),
[erratum](MATH-ERRATUM.md) and [patch](integration.patch).

The correction uses exact rational costs and transition masses, validates kernels,
preserves iterator inputs, compares action sets independent of order, and corrects
the finite adaptive-information identity. Combined quotient/decision use must also
preserve STOP outputs and costs. Fraction serialization and arithmetic costs remain
explicit integration obligations.

The first repair passed 16 regressions and 10 original helper controls. Independent
review then found a remaining action-iterator defect. Its correction passed the two
affected controls with the actual imported source recorded. These are distinct runs;
the complete 17-test successor file was not rerun. All failures and preimages remain.

This is an isolated helper and reviewable patch. It has not been applied to PR154,
does not qualify that changing branch, and establishes no new research result or
novelty. [The root source comparison](ROOT-LIVE-SOURCE-MATCH-01.json) records the
four unchanged patch-base blobs at its observed head; application to a later head
requires matching those blobs again.

The frozen [source landing page](CORE.md) and qualification receipt retain their
pre-review wording. This page and the final independent review record closure.
The sibling [historical review](../decision-core-successor-review-v1/CORE.md)
describes the original source. Existing SHA256SUMS files remain unchanged;
PUBLICATION-SHA256SUMS binds the complete published copies and this page.
