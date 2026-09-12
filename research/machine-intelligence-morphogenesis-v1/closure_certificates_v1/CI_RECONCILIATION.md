# CI reconciliation and test provenance

The first PR #449 CI attempt stopped before running research tests because
`test_gmi_k4_null_frontier_v5.py` was present in open PR #446 but absent on main.
The null-frontier implementation was already on main. This integration copies
that test file UNCHANGED from PR #446 head
`e57a23cdbaa2badd9f798978d1ad39a09ced273d`, Git blob
`0a27424bb2a360816b1a86000e4c27df92278c7a`.
The five tests are upstream work, not new tests authored for this contribution.
No assertion or registered scoring threshold was weakened to obtain a pass.
The four-suite CI command therefore comprises three main-branch suites plus
this imported upstream null suite.

The public development wrapper now loads the hash-checked repository source
before importing V5, so use from the certificate subdirectory does not require
manual PYTHONPATH setup. Additional repository-only checks exercise matching
nulls as target-class members, reject a forged null discount, and execute the
wrapper on an early inconclusive path. These are separate from the 70 local
standard-library tests; only CI execution establishes their result.

Main advanced from the integration base to `4721cb0` while this PR was prepared.
The intervening 19 file changes did not overlap the correction files or the six
pinned scorer modules. GitHub's PR workflow tests the combined merge tree.
