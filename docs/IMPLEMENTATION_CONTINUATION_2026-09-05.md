# Implementation continuation — 2026-09-05

This continuation follows local revision `479e781`. It fixes additional executable defects,
exercises installed and persistent runtime flows, and preserves both earlier receipt generations.

| Area | Completed change | Review and verification |
|---|---|---|
| Installed runtime | Package checked vocabulary/resources, remove test-module imports, provide `ocm chat` outside the checkout | 12 isolated distribution cases, including teaching, questioning, restart and resource drift |
| Speech boundary | Check actual emitted clauses, source/polarity/citations, exact proposition binding, decoder and renderer state changes | 17 initially failing regressions plus determiner/graph-identity controls; independent review closed eight concrete findings |
| Assurance | Require complete matched suites and measured resources, bind actual prediction events and complete proposal declarations | Missing suites/resources, invalid counts, contamination, drift and stale prediction evidence rejected |
| Rollback | Recover bounded data snapshots after restart; separate prepared restoration from host installation acknowledgment | Interrupted delivery is retrievable, unsupported executable artifacts remain unavailable, predecessor order enforced |
| Knowledge space | Normalize rational weights before float conversion, snapshot iterators, certify dyadic residuals with integers | 195 targeted tests, 256 exact before/after comparisons and independent 640-system arithmetic checks |
| Evidence | Bind the exact prior Git source/evidence snapshot and the complete current source inventory | Both named validation gates and parsed JUnit results required; old recipes never run on revised code |

Details: [distribution](INSTALLED_RUNTIME_DISTRIBUTION_V1.md),
[speech](SPEECH_BOUNDARY_CONTINUATION_V1.md),
[runtime lifecycle](RUNTIME_LIFECYCLE_CONTINUATION_V3.md),
[knowledge-space measurements](KSO_SPARSE_CONTINUATION_REPORT_V2.md), and
[second successor custody](provenance/runtime_revision_20260905_v2/README.md).

## Complete-flow evidence

The final focused suite passed **136 tests**, including speech, assurance, restart recovery,
distribution, numerical boundaries and successor custody. The final full suite passed **766 tests**
in 348.61 seconds with zero errors, failures or skips, recorded in
[FULL_SUITE.xml](provenance/runtime_revision_20260905_v2/FULL_SUITE.xml); both runs bind the same
unchanged source inventory captured before execution. Receipt verification is recorded separately
after the complete evidence set exists.

Fresh reference replays retain M4's **251/251** expected committed acts and M6's **42/42** scenario
steps with zero registered incidents. The designated M11 summary and M12 deterministic block
also agree with historical values after the corrections. This is authored regression evidence;
the M12 harness's current unreplicated exit gate remains `CANNOT_CHECK`. No new protected result,
external evaluation, independent replication or scientific admission is claimed.

The reference replay caught a defect missed by the unit suite: the new codec dropped the registered
astronomical determiner from `The moon`, reducing M6's exact wording count from 42 to 41 and causing
a corresponding M12 summary change. The grammar now binds the determiner to the same graph identity;
the original scenario expectation was not weakened. Full and focused validation were repeated on
the corrected frozen source before sealing.

An earlier exploratory full run had 704 passing tests and 39 receipt-fixture errors because the
receipt config was being revised after its verifier had been imported. That unsealed run is
preserved in [the diagnostic log](provenance/runtime_revision_20260905_v2/history/UNSEALED_SUITE_LOG.txt)
and is excluded from final receipt evidence. Source stability is now explicitly checked across
the final validation interval. A further review closed acceptance of an arbitrary successful
command as sufficient replay evidence: named full/focused commands and their JUnit gates are mandatory.

## Measured optimization

Against the preceding checked runtime, certified sparse solves improve **1.34×–1.78×** on the
registered 4,096/16,384-atom sparse and conjunctive graphs. Including matrix construction, the
improvement is **1.14×–1.49×**. Rational normalization has a real construction cost. Traced solver
allocations fall about **38%**; this excludes already allocated graphs/matrices and process RSS.
These are separate measurements from the earlier admission speedups, not a multiplied whole-system claim.

## Current boundaries

M11 is `M11_ENGINEERING_REVALIDATION__HISTORICAL_ADOPTION_CELLS_REOPENED`;
M12 is `M12_ENGINEERING_REVALIDATION__PROTECTED_REEVALUATION_REQUIRED`.
All M0–M12 original receipts and all twelve first-successor receipts remain unchanged.

Installed bounded chat, registered interpretation, knowledge-space computation and supported data
recovery are executable. Arbitrary executable backend recovery, atomic external effects, hidden
dependency completeness and unrestricted English are outside these verified contracts. Stronger
matched parents, corrected protected evaluations, external reviewers and broader language evidence
remain programme work. V2's new infinite-threshold theorem supplies a parent-sufficient calibration;
it does not close the separate infinite grammar-learning frontier.

The changes are local repository commits. Remote publication and merge-gate completion are separate
from the local test and custody results.
