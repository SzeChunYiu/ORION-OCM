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

@@GATES@@
