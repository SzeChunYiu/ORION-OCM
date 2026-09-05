# Complete the missing historical OCM migration

Audit of V2's remaining open PRs found that the stacked source migrated into OCM
did not include the sibling exact-checker branch #300. One original recursive-KSO
test from #302 was also missing. This package recovers all 38 changed files of
#300 plus that test, preserving their original Git blobs and SHA-256 identities.

Source heads are `0a18777e8ed3de84c73948616fc428468a9da03b` (#300) and
`51bf66ece0c5388e5916d499a875a523359ba83c` (#302). `MANIFEST_V1.json` maps every
original path to its archived copy. The existing migration record and frozen
runtime/receipt inventory remain unchanged. Archived ledgers and results retain
their historical status; they are not current programme verdicts.

## A real integration defect, preserved and repaired

The original four relevant test files returned **33 passed, 1 failed**. The
checker/oracle agreement test guessed a two-argument generator API, while the
actual function requires `(split, seed, per_family)` and returns
`(instance/oracle pairs, rejection counts)`. The original log and JUnit XML are
retained under `history/`.

The versioned adapter uses the actual API, retaining 30 development instances
across six families. It also fixes a second incorrect test premise: adding one
to a root can yield the other valid root. The repaired control instead chooses
an exact rational point with a nonzero polynomial residual, and requires
`INVALID`. A separate test explicitly preserves the valid adjacent-root case.
No-equation cases must remain `CANNOT_CHECK`.

The successor replay passes **35 tests**, with no errors, failures or skips.
It reconstructs the inherited dependency tree from OCM Git base
`3039e233486252c5092728ab5fbdcdac0aa61ab4` in a new temporary directory, overlays
the exact recovered sources, and replaces only the declared test adapter. It
does not rewrite original sources, outcomes or tests in place. The replay
requires pytest and SymPy; missing dependencies are not accepted as skipped
verification. The validated environment uses pytest 8.3.5 and SymPy 1.14.0.

The inherited SymPy parser is replayed only on these trusted authored fixtures.
It is archived research code, not a public parser for untrusted expressions and
not installed into the active OCM command interface.

```sh
python research/migration-completion-v1/replay.py --verify-only
python research/migration-completion-v1/replay.py --out /tmp/new-migration-replay.json
```

Exit 0 means the requested custody/replay checks completed; unavailable evidence
or a failed replay returns 2 with a reason. The output distinguishes the source
custody check from actual execution. The manifest digest is pinned in the
checker; byte identities establish custody under a trusted reviewed repository,
not issuer authenticity, semantic proof or scientific adoption.

This package completes the missing historical migration obligation for V2
#300/#302 after merge. It does not establish general algebra learning, a new
proof kernel, frontier mathematics or restoration of M11/M12 scientific claims.
