# Receipts run log — gmi-833-developmental-reuse-v1

## Authority and order

| item | value |
|---|---|
| source main | `bfb7d8c296a60c0bc76632ed69551540644e74e6` |
| pre-implementation freeze commit | `01c6a820` (`FREEZE_V1.md` + `FROZEN_FIXTURES_V1.json` only) |
| branch | `research/833-l-dev` |
| worktree | `/Users/billy/Desktop/projects/ORION-OCM-wt-833/l-dev` |

The freeze commit contains **no** executor, oracle, test, receipt, manifest,
reconciliation or workflow. CI re-verifies the ordering with
`git merge-base --is-ancestor <freeze> <first implementation commit>` and
`test "$FREEZE" != "$IMPL"`.

## Hosts

- **All compute on `laptop-billy`** (`hostname: billy`, 16 cores, CPython
  3.8.10). No executor, oracle, test or census was run on the Mac mini; the Mac
  was used only for `git`/`gh` and single-file edits, per the standing rule.
- Transfers by `rsync -a`; both directions md5-verified (never `cat | ssh` —
  the rtk proxy corrupts binary pipes).
- Scratch: `~/ocm-scratch/l-dev` on laptop-billy, `/tmp/claude-501` on the Mac.

## Commands (exactly as run)

```bash
python3 -I -B  developmental_reuse_v1.py       > RESULT_V1.json          # ~59 s
python3 -I -B  independent_oracle_v1.py        > ORACLE_RESULT_V1.json   # ~9 s
python3 -I -B  ci_gate_v1.py
python3 -I -B  test_developmental_reuse_v1.py -v                         # ~64 s
python3 -I -O -B test_developmental_reuse_v1.py -v
```

Determinism: both executables were re-run and `cmp`-compared against their
committed receipts byte-for-byte. Seeds are the frozen integer LCG only; no
`random`, no `time`, no environment reads.

## Defects found in this package's own instruments, before reporting findings

Recorded because "validate the checker first" is not optional.

1. **LCG low-bit degeneracy.** The frozen LCG has modulus `2^31`; a
   power-of-two-modulus LCG has period `2^j` in its low `j` bits, so the first
   draft's `next() % k` for `k ∈ {3, 8}` was degenerate — the mutation walk
   visited **11 distinct states in 6,561 draws**. Fixed by extracting the high
   15 bits (`(next() >> 16) % k`); the extraction rule is documented at the call
   site. Had this shipped, every stochastic dynamic's row would have been
   meaningless.
2. **Vacuous target-independence comparison.** The first version of the SD-2d
   check used targets at enumeration indices `0` and `|X|−1`; `ENUM` and `META`
   hit on query 1 for the index-0 target, so their comparison prefix was
   **empty** and the check passed *vacuously*. Fixed by moving the two targets
   to indices `(|X|−1)/3` and `2(|X|−1)/3`, and by flagging any vacuous
   comparison as a failure rather than tolerating it. Comparison prefixes are
   now 932–6,561 symbols.
3. **REP-1 incompleteness at 4 boundary cells.** The registered second route's
   extreme-rank check reported 4 census cells the frozen three-way rule leaves
   in `RANK_DECIDED` even though their sign is rank-free in the weak sense. The
   frozen rule is sound (0 wrong strict signs) but incomplete; `REP-1b`
   completes it five-way. Recorded with provenance; the frozen statement is
   reported unchanged.
4. **Two silent freeze deviations, found and corrected (not merely recorded).**
   The first complete build (a) ran the SD census over 7 dynamics with `NAS`
   filtered out and `RAND` substituted, although `FREEZE_V1.md` §3 and
   `FROZEN_FIXTURES_V1.json:sd_frame.dynamics` register **8** dynamics including
   `NAS`; and (b) never used `sd_frame.ell_scaling = [6, 8, 10]`, reporting only
   `ell_primary = 8`. Both were deviations from the freeze that nothing in the
   receipt disclosed. Corrected rather than excused: `NAS` now runs inside the
   same charged frame (one unit per enumerated program's expansion, `K_total`
   charged up front before its inner search may run), and `SD-2b` now emits the
   closed-form scaling row at every registered `ell` with route B sweeping all
   start points exhaustively wherever that is within the registered exhaustive
   budget. A test now asserts `set(SD_CENSUS_DYNAMICS) − {RAND}` equals the
   frozen dynamics list, so this class of drift cannot recur silently.
5. **An inverted-grep CI gate that could never fail.** Two `! grep …` lines ran
   under `set -eu`; bash does not exit on a command whose status is inverted
   with `!`, so the stdlib-only check and the route-independence check were
   no-ops whose step status came from the last line only. Replaced by explicit
   `if grep …; then exit 1; fi` in separate steps. In a package whose discipline
   is "validate the checker first", this was the one checker that had not been
   validated.
6. **Stale receipts produced by the verification workflow itself.** Syncing the
   package directory Mac → laptop after a code change also pushed the *previously
   committed* `RESULT_V1.json` / `ORACLE_RESULT_V1.json` over the laptop's freshly
   generated ones, so a subsequent gate + test pass validated the new code against
   **stale** receipts. Caught by md5-comparing the pulled receipts against the run
   that produced them. Fixed by regenerating both receipts on the laptop from the
   current code as the first step of a single `ldev_regen.sh` pass, and never
   syncing receipts in the Mac → laptop direction afterwards. CI's byte-for-byte
   `cmp` of a fresh executor run against the committed receipt is the standing
   guard against this exact drift.
7. **A route-independence gate that fired on its own documentation.** Once the
   inverted-grep no-op (defect 5) was fixed, the gate ran for real in CI — and
   failed the build on `independent_oracle_v1.py`'s **docstring**, which names
   the Route A module precisely to state that it must not import it. A substring
   grep cannot express "does not import". Replaced by an `ast`-based check in
   `ci_gate_v1.py` that inspects `Import` / `ImportFrom` nodes and `__import__` /
   `importlib.import_module` calls, and fails closed on an unresolvable dynamic
   import. The checker is validated in both directions by tests: recall on four
   planted positives (plain import, from-import, dynamic import, unresolvable
   dynamic import) and the no-alarm case on the real oracle and on a
   docstring-only mention. This is the "a false positive costs more than a miss"
   rule caught in the act, on the checker's first real run.
8. **META evaluation accounting.** The first draft charged portfolio arms with
   placeholder evaluations. Replaced by `_ArmView`, which forwards every arm
   evaluation to the single shared charged oracle exactly once and cuts the arm
   off at its own share. No evaluation is free, and the audit counter confirms
   `audit_calls == charged` on every cell.

## Registered criterion that was NOT met, reported verbatim

`FREEZE_V1.md` §5 froze: *"`OPAQUE`: guided dynamics must NOT beat the RAND
control."* Measured over 200 registered targets: `MUT` 136, `LS` 133, `GRAD`
133, `EVO` 7, `GP` 4 against `RAND` 129. **Not met as specified.**

Single-stage attribution: the criterion measured a *hit count*. Under `OPAQUE`
the objective is constant off the target, so no dynamic can use guidance at all
(SD-2d proves every query sequence is target-independent) and the hit count is a
pure coverage lottery in which 133-vs-129 out of 200 carries no information
about guidance. The criterion was mis-specified, not the theory. The replacement
— identical query sequences for the same dynamic and seed under two different
targets, non-vacuously compared — is exact, mechanical and strictly stronger; it
passes for all 8 dynamics. Both the failure and the replacement are in
`RESULT_V1.json` under
`SD_2_mechanism.null_two_sided.freeze_criterion_disposition`.

## Determinism of the reported ranking

Ties in the census ranking are broken by the frozen dynamics-list order, not
arbitrarily. In `OPAQUE`, `LS` and `GRAD` produce byte-identical runs (133 hits,
355,914 evaluations each): with a constant objective neither has an improver, so
both degenerate to seeded restart sampling off the same seed stream. That
coincidence is a consequence of SD-2d, not a collision in the frame.

## Two routes

| | Route A (`developmental_reuse_v1.py`) | Route B (`independent_oracle_v1.py`) |
|---|---|---|
| burdens | segmentation DP + `n`-ary rank closed form | **literal** breadth-by-length program enumeration + expansion |
| `Φ` | accumulating loop | geometric closed form `n(n^ℓ−1)/(n−1)` |
| REP-1 | band arithmetic | verification against the **extreme** rank assignments |
| NOV-1 | expressibility via segmentation | explicit construction of the expansion set |
| SD-2b / SD-2c | 200-seed census | **exhaustive** sweep of all 6,561 start points |

Route B does not import Route A (CI-enforced by grep). Agreement is asserted on
every registered integer, including the 4 REP-1b boundary cells being found
independently by both.

## Nulls

- **`GRADED`**: 200-seed `RAND` control beaten — `GRAD` 200/200 in 3,075 total
  evaluations vs `RAND` 129/200 in 378,620.
- **`OPAQUE`**: replaced by the exact target-independence test (above).
- **`DECEPTIVE`**: the accident channel is not a null but an exact
  characterisation — Route B's exhaustive sweep finds the hitting start-point
  set is *precisely* the predicted 3-element set out of 6,561.

## Hostiles

All nine are exercised and reported, but they are **not all of the same kind**,
and saying so is part of the record:

**Six substantive detections** — each could fail and would fail if the thing it
guards were broken:

- `H-NEARMISS` — the REP-1 classifier must refuse to guarantee a sign at the
  overlapping-bracket instance, and does (`RANK_DECIDED`).
- `H-CYCLE` — a cyclic library must return `RECURSIVE_LIBRARY_CYCLE` with the
  grammar unchanged, on both routes.
- `H-UNCHARGED` — an evaluation that skips the charge counter is caught by an
  *independent* audit counter (`audit_calls != charged`).
- `H-CAPITAL` — the solution-capital library must be accepted per target and
  rejected on the distribution (`−36,890` vs `+18,139`).
- `H-NOREUSE` — a library whose body occurs in no target must yield
  `Saving = 0` and `ΔNet > 0` (`+437,558`).
- `H-RANKFLIP` — dropping the rank term must produce a two-route disagreement.

**Three constructive demonstrations, honestly labelled** — `H-BUDGET`,
`H-TARGET` and `H-ORACLE-PEEK` construct an over-budgeted oracle, a
wrong-target oracle and a direct target read, then assert the resulting
inequality. Those assertions are arithmetic identities of the construction: they
show *what the frame forbids* and cannot themselves fail. They are recorded as
demonstrations, not as detectors, and they are not what `all_detected` rests on.
Turning them into real detectors means a shared `validate_frame(oracle,
registered)` guard inside the executor, which would regenerate both receipts;
that is a queued improvement, not a silent claim. The six substantive hostiles
above carry the hostile obligation.

**No-alarm obligation:** the checker is asserted silent on every clean
registered instance (`no_alarm_ok`), and the route-independence checker is
validated in both directions by six dedicated tests.
