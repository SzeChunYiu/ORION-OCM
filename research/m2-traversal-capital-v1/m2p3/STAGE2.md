# M2-P3 stage 2: author session and entry gates (2026-09-11)

Freeze: [M2P3_FREEZE_V1.json](M2P3_FREEZE_V1.json), merged as #414 (bd9589f7) at 2026-09-11T20:31:28Z,
**before** the author session. Nothing in the freeze, the spec, the token list, the gates or the arm set was
touched.

## Author unit

A fresh general-purpose model session (no conversation inheritance), **claude-haiku-4-5** set explicitly
(the M2-P2 author was claude-fable-5-1), received the frozen neutral spec verbatim (sha256 `6a25c7f3…439bd`,
matching the freeze) inside a four-rule wrapper: work only in a neutrally named studio outside the repository,
produce the three files, run the emitter from the studio, and reply with a summary. The wrapper was checked to
contain no lane vocabulary. The session ran after the freeze was on main and finished by 20:35:15Z (agent
wall time 176.7 s). It produced **7 worlds**. Label: `HUMAN_GATE_BYPASSED__MODEL_PROXY`.

The package is copied verbatim into [authored/](authored/) with per-file sha256 and the isolation note in
[authored/PROVENANCE.json](authored/PROVENANCE.json). Isolation is by instruction, not enforcement, exactly as
the freeze states. The emitter was reviewed line by line before it was first run: it imports `json` only, its
single `open()` is the required write, and all seven worlds are static hand-written data.

## Independence from M2-P2 (reported next to the terminal, per the freeze)

| measure | M2-P3 vs M2-P2 |
|---|---|
| world shapes equal to an M2-P2 shape | **0 / 7** |
| chunk sets identical to an M2-P2 chunk set | **0 / 7** |
| median Jaccard to the nearest M2-P2 chunk set | **0.300** (range 0.111–0.667) |

The second author did not reproduce the first author's designs: no shape and no chunk set recurs. The closest
pair (`quadratic_entry` against hc02-square-shift, Jaccard 0.667) shares its squaring-with-shift theme.
Per-world figures: [stage2/M2P3_OVERLAP_WITH_M2P2.txt](stage2/M2P3_OVERLAP_WITH_M2P2.txt).

## Entry gates

`m2p2_check.py` (unchanged from M2-P2) was run on laptop billy against a directory holding only the author's three
files. The lane's `PROVENANCE.json` was excluded, as it was in M2-P2's receipt, because the taxonomy hostile scans every
byte it is given. The repo tree came from `git archive` of this branch (sha256 verified on both ends); `methods.py` is the
registered unit (`e0a05654`). Receipt: [stage2/M2P3_STAGE2_RECEIPT.json](stage2/M2P3_STAGE2_RECEIPT.json) (sha256 `62819c76…`).

| gate | result |
|---|---|
| taxonomy-disjointness hostile | **clean**: 0 hits on all three files; no-alarm and tamper controls passed |
| static guard on the emitter | **REJECTED_CANNOT_CHECK**, forbidden-call pattern `\bopen\s*\(\s*['"][^'"]*['"]\s*,\s*['"][wax]` |
| determinism (two sandboxed runs) | not run (skipped after the guard rejected) |
| authoring floors | met: 7 worlds ≥ 6; 7 distinct shapes ≥ 2; 7 unique chunk sets |
| compilation, G1/G2/G3, viability, G-SURF | not run |

**Stage-2 verdict for this package: `CANNOT_CHECK_EMITTER_REJECTED`.** Under the frozen rules a rejected emitter is never
patched and the package is never re-scored under a changed guard. No world in it was compiled or scored.

**Diagnosis: the guard enforces spelling, not the rule it states.** The rule is "no filesystem access beyond the one
required write". The spec requires exactly one write: `emit_worlds.py` must write `worlds.jsonl` into the current
directory. The frozen guard's pattern rejects any `open()` whose first argument is a literal string and whose mode is a
write. So it rejects the spec-mandated write when the filename is spelled literally, as this author did
(`open("worlds.jsonl", "w")`), and accepts the same write through a variable, as M2-P2's author did
(`open(OUT_NAME, "w", …)`). Checked directly: the pattern matches the M2-P3 emitter and does not match the M2-P2 emitter.
The neutral spec never tells an author about this spelling requirement. The defect was latent in M2-P2; it did not
invalidate M2-P2, whose emitter passed, but it made acceptance depend on how the one permitted write is spelled.

## What carries forward, and the route

**Package A is CANNOT_CHECK, not discarded.** Its taxonomy scan was clean, it met every authoring floor, and the
independence result above (0 / 7 shapes, 0 / 7 chunk sets, median Jaccard 0.300) is genuine evidence about a second
author and **stands**. Only the scored replication is not measurable on this package.

**Route (registered before any new author session).**
1. This stage-2 record lands first, with package A's terminal, the diagnosis and the overlap result.
2. A **V2 freeze corrects the guard's implementation, not its rule.** The rule stays identical to V1: no filesystem
   access beyond the one required write. The V2 guard permits exactly one write whose target resolves to
   `worlds.jsonl` in the current directory, however it is spelled, and forbids every other write. Before the V2 freeze
   merges, the new guard is calibrated against real emitters: M2-P2's must ACCEPT, package A's must ACCEPT on its write,
   and a tamper control (a second write, or a write to another path) must REJECT.
3. Only after V2 is on main, a **fresh author session** runs, with the same model, the same spec (sha re-verified at
   prompt-build time) and the same wrapper, and **no hint about how the write is spelled**. That would leak gate
   knowledge to the author, and the corrected guard makes it unnecessary.
4. Package A is never re-scored under V2, and no author session is repeated under V1 in the hope of a different
   spelling. Either would be selection on the gate's outcome.

**M2-P2 is unaffected.** Its emitter passed the V1 guard, its worlds compiled, and its terminal
(`CANNOT_CHECK_NO_ADMITTING_WORLD`) and every M2-P2 table stand as recorded.


