# M2-P3 stage 2b: package B, authored and gated under freeze V2 (2026-09-11)

Freeze: [v2/M2P3_FREEZE_V2.json](v2/M2P3_FREEZE_V2.json), merged as #417 (8313c699) at 22:01:01Z, **before** this
author session. Package A's separate terminal (`CANNOT_CHECK_EMITTER_REJECTED` under V1) stands in
[STAGE2.md](STAGE2.md); package A is not re-scored and its worlds are not reused.

## Author unit

A fresh **claude-haiku-4-5** session (no conversation inheritance), spawned after the freeze was confirmed on main
(22:05:41Z, finished by 22:09:40Z; 238.6 s, 14 tool uses), received the frozen spec verbatim
(sha256 `6a25c7f3…439bd`, **re-verified at prompt-build time**) in a fresh, empty, neutrally named studio. The prompt was
**byte-identical to package A's except the studio path** (verified: exactly one differing line) and carried **no hint
about the entry gate**. It produced **6 worlds**. Label: `HUMAN_GATE_BYPASSED__MODEL_PROXY`. The package is recorded
verbatim in [authored_b/](authored_b/) with per-file sha256 and [authored_b/PROVENANCE.json](authored_b/PROVENANCE.json).

The emitter was reviewed line by line before first execution: imports `itertools`, `json`, `typing` only; its single
`open()` is the spec-mandated write of `worlds.jsonl` to the current directory; no `os`/`sys`/`subprocess`/socket/
environment/thread/`eval`/`exec`. **ACCEPT.** Note: V1's guard would have rejected this emitter too, for the same
literal-spelling reason that rejected package A, so the V2 correction was necessary rather than cosmetic.

## Entry gates (V2 orchestrator, laptop billy, 83.8 s)

Receipt: [stage2b/M2P3_B_STAGE2_RECEIPT.json](stage2b/M2P3_B_STAGE2_RECEIPT.json) (sha256 `9556a488…`). The repo tree came
from `git archive` of main at 8313c699 (sha256 verified both ends); `methods.py` is the registered unit (`e0a05654`);
orchestrator `m2p3_check_v2.py` (`1b8c5c5c`) and guard `guard_v2.py` (`d7b3c480`) are byte-identical copies of the merged
V2 files. Only the author's three files were scanned, as in M2-P2's receipt.

| gate | result |
|---|---|
| taxonomy-disjointness hostile | **CLEAN** (0 hits on all three files; both controls passed) |
| static emitter guard (V2) | **ACCEPT** |
| determinism (two sandboxed runs) | **DETERMINISTIC** (byte-identical `worlds.jsonl`) |
| authoring floors | **MET**: 6 worlds ≥ 6; 6 distinct shapes ≥ 2; 6 unique chunk sets |
| compilation, G1/G2/G3, viability | **4 viable / 6**; 2 retained as `CANNOT_CHECK_WORLD`, never dropped |
| G-SURF (blocking, per world) | **PASS 4 / 4** — no viable world is surface-derivable |

**Stage-2b verdict: `ENTRY_GATES_PASS`.**

| world | train | tuning | future (scored) | members | viability |
|---|---|---|---|---|---|
| world_1_basic_add_dbl_sub | 25 | 10 | 14 | 49 | CANNOT_CHECK_WORLD (below the 90-member floor) |
| world_2_mixed_cross | 2 | 0 | 1 | 3 | CANNOT_CHECK_WORLD (below the floor) |
| world_3_varied_lengths | 106 | 28 | 57 | 191 | **viable** |
| world_4_six_chunks | 56 | 23 | 34 | 113 | **viable** |
| world_5_nonlinear_focus | 212 | 160 | 157 | 529 | **viable** |
| world_6_full_palette | 92 | 46 | 43 | 181 | **viable** |

**Consequence for the registered terminal.** The freeze requires at least 4 viable worlds and at least 80 % of them
passing the 50 % effect-size test. With exactly 4 viable worlds, 80 % means **all four must pass**: three passing gives
`C2_NOT_REPLICATED`. That is the bar as registered, and it is not adjusted now that the count is known.

## Independence from M2-P2 and from package A (reported next to the terminal, per the freeze)

| measure | vs M2-P2 (10 worlds) | vs package A (7 worlds) |
|---|---|---|
| world shapes equal to a reference shape | **0 / 6** | **0 / 6** |
| chunk sets identical to a reference chunk set | **0 / 6** | **0 / 6** |
| median Jaccard to the nearest reference chunk set | **0.333** | **0.333** |

Per-world figures: [stage2b/M2P3_B_OVERLAP.txt](stage2b/M2P3_B_OVERLAP.txt) (script `stage2b/m2p3_overlap_b.py`). The
second author reproduced neither the first author's designs nor its own earlier package: no shape and no chunk set
recurs in either direction.

## Stage 3

The four viable worlds were pushed to LUNARC (sha256 verified both ends) and the frozen scored run was submitted
(job 3600810): a fresh dev phase per world, then RESET, `PARENT_GF_D4` (primary), `SHUFFLED_HISTORY`, `CONTINUED_OCM`,
`PARENT_WITH_MDL`, `PARENT_GFQ_D3` and `PARENT_GFQ_D4`, with runner `7d790905` and `methods.py` `e0a05654`.
