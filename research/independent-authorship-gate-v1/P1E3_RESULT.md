# Result

Fail-closed policy is in force. P1E3 executes the E3 clause `P1-world-authorship`: world families authored by a FRESH model session that received only the neutral interface spec (Implication Systems) — never the repo, the mechanism taxonomy, the oracle, or any prior family. Truth is recovered only by this pipeline's independent exact checker; author intent is audit-only and refused as a cause label on attempt.

On the authored package `p1e3_authored/` (frozen verbatim copy, sha-bound in the receipt):

| | n | floor |
|---|---:|---:|
| Families (each >= 5 instances, >= 1 recovered) | 10 | 10 |
| Instances | 60 | 50 |
| Independently recovered truth | 60 | — |
| `CANNOT_CHECK` | 0 | — |
| Intent AGREE (audit-only comparison) | 60 | — |
| Intent DISAGREE (ladder findings) | 0 | — |
| Hostiles passed | 5 / 5 | 5 / 5 |
| Determinism re-run of `emit_all.py` | byte-identical | — |

Families (6 instances each, all recovered): Cascade Ladders, Forkjoin Lattice, Guild Overlap, Ledger Tradeoffs, Loop Spinup, Near-Miss Keys, Quorum Gates, Redundant Rails, Toll Routes, Trap Vaults. Comparison dimensions exercised on all 60 rows: closure size, reachable-goals set, minimum-seed cost (spread 0–17 plus deliberate price-99 direct seeds; several rows have empty reachable-goal sets).

Hostiles:

| Hostile | Result |
|---|---|
| H-P1E3-1 taxonomy disjointness | 0 overlaps across all 16 authored artifacts (13 `.py` including every `families/*.py` module, 2 `.md`, `instances.jsonl`) against 125 frozen tokens in 5 tiers (79 atom ids, 9 abbreviations, 10 ME-X1 family names, 20 ResidualKind/Responsibility, 7 distinctive module identifiers) |
| H-P1E3-2 intent-label leakage | generator-intent cause label REFUSED by policy; unrecovered cause target fails closed to `CANNOT_CHECK` |
| H-P1E3-3 known answer | 4 hand-computed fixtures, 4/4 match the independent oracle |
| H-P1E3-4 no-alarm control | pristine spec scans 0 hits while planted-token control matches — scanner alive |
| H-P1E3-5 tamper sensitivity | planted taxonomy token into an artifact copy alarms |

The taxonomy scan initially covered only top-level artifacts; it was extended to every `families/*.py` module before the final receipts (both runs exit 0; final scan = 16 files).

## What 60/60 AGREE is, and is not

It is NOT the ME-X1 artifact case, where 17 agreements were rejection-sampled against the oracle inside a shared taxonomy. Here the author unit never saw the oracle, the checker, or the taxonomy; it computed its expectations with its OWN implementation of the frozen public semantics (`families/_common.py`); and no rejection sampling occurred — every emitted instance is in the receipt unfiltered. The agreement is therefore a cross-implementation replication: two independently written exact implementations of the frozen neutral semantics agree on closure, reachable goals, and minimum-cost seed for all 60 instances. This is the E5 rung's test at P1 scope, and it is the strongest authorship evidence available without a human author.

## Honest limitations (preserved, not laundered)

- Authorship is MODEL-PROXY (`HUMAN_GATE_BYPASSED__MODEL_PROXY`): a fresh session of the same model family on the same host, isolated by instruction, not by enforcement. Isolation is certified only mechanically — taxonomy disjointness (0 overlaps) plus static code review. A human author remains unbypassed.
- No `IMPOSSIBLE` terminal occurs in the 60 instances; all 60 minimum seeds are possible. The author's documented workaround prices goal atoms at 99 so direct seeding is technically possible while the interesting minimum avoids it. The `IMPOSSIBLE` branch of the oracle is exercised only by the hand-computed known-answer fixture, not by any authored instance. The exclusion-constraint branch (forbidden atom in joint closure) IS exercised by Trap Vaults and Ledger Tradeoffs.
- Spec deviations, non-blocking and recorded: `intent_role` sits inside the `intent` dict rather than top-level; intent carries no separate min-seed possibility boolean (nothing lost — all 60 possible); the author computed intent via its own implementation rather than hand-computing expectations.
- The author session died once mid-run (output-length limit, zero files written) and was resumed with small-piece instructions; the resume introduced no repo/taxonomy content (recorded in `p1e3_authored/PROVENANCE.json` `recovery_event`).
- Authored code was executed only as a sandboxed subprocess after line-by-line static review (no network/filesystem/exec/env/thread tokens; `open(` legal only in `emit_all.py` for its own `instances.jsonl`). Any review rejection would have produced `CANNOT_CHECK`, never a patched artifact.

## Effect on the frozen protocol files

`E3_PROTOCOL_FREEZE_V1.json` clause P1 status -> `SATISFIED__P1E3`; `MEASUREMENT_VALIDITY_V1.json` H-MV-05 -> `EXECUTED`, gate passed. This grants NO execution rights: per `promotion_rule`, a study is E3-authorized only when P1 authorship exists AND the owning lane's entry gates (e.g. `FLAGSHIP_EXPERIMENT_V1.json`) are SATISFIED. Clauses P2–P9 remain in force.

Receipts: [P1E3_RECOVERY.json](P1E3_RECOVERY.json), [P1E3_FAMILY_TABLE_V1.json](P1E3_FAMILY_TABLE_V1.json). Checker: `p1e3_recover.py` / `p1e3_taxa.py` / `p1e3_check.py` (exit 0; known-answer + no-alarm + tamper controls green). Freeze: [P1E3_AUTHORSHIP_FREEZE_V1.json](P1E3_AUTHORSHIP_FREEZE_V1.json); spec: `p1e3_author_spec.md`. Wall time 0.44 s. No novelty claim.
