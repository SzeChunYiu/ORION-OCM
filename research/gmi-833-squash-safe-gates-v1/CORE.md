# gmi-833-squash-safe-gates-v1 — CORE

Parent: PR #1053 freeze (`FREEZE_V1.md` of this package, branch
`codex/1049-squash-safe-gates-v1`, issue #1049); doctrine of #1042
(`research/gmi-833-blind-recovery-v2-v1/check_v2.py`, `FREEZE_COMMIT_UNREACHABLE`).
Claim ceiling (inherited): `SQUASH_SAFE_CUSTODY_..._REPAIR_FOR_REGISTERED_GMI_833_GATES`.
Closes no scientific row. Forbidden: `SQUASH_COMMIT_PROVES_PRE_IMPLEMENTATION_REGISTRATION`,
`FREEZE_FILE_PRESENT_IMPLIES_FREEZE_FIRST`.

## The rule

"Freeze precedes implementation" is a theorem of the commit graph on a linear
history: the freeze file's add-commit is a proper ancestor of every implementation
file's add-commit. A squash merge collapses both into ONE `(#N)` commit on main, so
the theorem can no longer be re-derived there, and every branch that merges main
afterwards inherits the same shape. Eight gates went red on main for this reason.

`squash_safe_freeze_check_v1.py` (stdlib, `python3 -I -B`) returns exactly one of:

| state line | exit | meaning |
|---|---|---|
| `FREEZE_ORDER_OK:<freeze-add-commit> checked:<list>` | 0 | strict ordering proof holds |
| `FREEZE_ORDER_NOT_REDERIVABLE:<squash-commit> checked:<list>` | 0 | ONLY the ordering assertion is withheld |
| `FREEZE_ORDER_VIOLATION:<reason>` | 1 | a check that could run, failed |
| `FREEZE_ORDER_COULD_NOT_CHECK:<reason>` | 2 | not a git repo / shallow clone / no HEAD |

NOT_REDERIVABLE is granted only when the shared commit has one parent, a `(#N)`
subject, and a parent holding neither the freeze nor any implementation artifact
(and, for the package's first commit, nothing of the package at all — freeze rule 2).
Everything still derivable is checked and listed: freeze present at HEAD; frozen
artifacts present; `--freeze-blob` bytes; and, when the package pins its source freeze
commit and `git cat-file -e` reaches it, that its tree holds the freeze, none of the
implementation/outcome patterns, and the same freeze bytes as HEAD. An unreachable pin
is recorded as `freeze_tree:UNREACHABLE:<sha>`, never passed. A shared commit that is
not squash-shaped stays the #976 POST_HOC shape and fails.

## Files

- `squash_safe_freeze_check_v1.py` — the checker (`--pkg`, `--freeze`, `--impl` patterns,
  `--present-at-freeze`, `--freeze-commit | --freeze-commit-file`, `--freeze-blob`).
- `test_squash_safe_freeze_check_v1.py` — 18 tests on throw-away git repos: linear OK,
  impl-before-freeze, squash NOT_REDERIVABLE, squash with freeze missing, planted
  publishing commit without freeze, planted parent with implementation, non-squash and
  merge-commit sharing, later revival squash, pinned blob/commit mismatch, source freeze
  tree holding implementation, unreachable pin, not-a-repo, shallow clone, empty pattern.
- `check_registered_packages_v1.sh` — runs the 14 registered invocations (mirrors the
  gates); used by `gmi-833-squash-safe-gates-v1.yml` as the real-history proof.

## Gates now calling it

`gmi-833-capability-interaction-partition`, `-capability-predictor-evaluation` (4 runs),
`-developmental-reuse`, `-maturity-rescore-v3-w4-v1`, `-update-law-regimes-v1`,
`-z-z12-prediction-scoring`, `-z-z15-decisive-falsifiers` (2 runs), and
`research/gmi-833-real-developmental-validation-v1/check_freeze_order_v1.py` (3 freezes).

## Reproduce

```
python3 -I -B research/gmi-833-squash-safe-gates-v1/test_squash_safe_freeze_check_v1.py -v
python3 -I -O -B research/gmi-833-squash-safe-gates-v1/test_squash_safe_freeze_check_v1.py
bash research/gmi-833-squash-safe-gates-v1/check_registered_packages_v1.sh .   # full clone only
```
