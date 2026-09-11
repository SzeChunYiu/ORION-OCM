# M2-P2 stage 2 — author session and entry gates (2026-09-11)

Freeze: [M2P2_FREEZE_V1.json](M2P2_FREEZE_V1.json). Stage 1 merged as #358. Nothing in
the freeze, the spec, the token list, the gates or the arm set was touched.

## Author unit

A fresh general-purpose model session (no conversation inheritance) received the frozen
neutral spec verbatim (sha256 `6a25c7f3…439bd`, matching the freeze) and an instruction to
write only into a studio directory outside the repository. It produced `emit_worlds.py`,
`worlds.jsonl` (one emitter run) and `AUTHOR_NOTES.md`: **10 worlds, 10 distinct shapes**.
Label: `HUMAN_GATE_BYPASSED__MODEL_PROXY`. The package is copied verbatim into
[authored/](authored/) with per-file sha256 and the isolation note in
[authored/PROVENANCE.json](authored/PROVENANCE.json) — isolation is by instruction, not
enforcement, exactly as the freeze states; the mechanical guarantee is the hostile below.

## Entry gates (m2p2_check.py on laptop billy, 204 s; receipt [stage2/M2P2_STAGE2_RECEIPT.json](stage2/M2P2_STAGE2_RECEIPT.json))

| gate | result |
|---|---|
| taxonomy-disjointness hostile (219 frozen tokens, no-alarm + tamper controls) | **clean** — zero alarms on every authored byte; controls passed |
| static guard on the emitter | ACCEPT — imports `json` only; the single `open()` is the required write |
| determinism (two sandboxed runs) | byte-identical, sha256 `24111a94…3fdf8` |
| authoring floors | 10 worlds ≥ 6; 10 distinct shapes ≥ 2; 10 unique chunk sets |
| compilation, G1/G2/G3 | PASS on all 10 |
| viability floor | **8 viable**; hc04-seven-triads (31 members) and hc07-drawn-lot-a (77) retained as CANNOT_CHECK_world |
| G-SURF surface-derivability (blocking, per world) | **PASS on 8 / 8** — no authored world is surface-derivable |

**Stage-2 verdict: `ENTRY_GATES_PASS`.** One reading to keep in view: hc05-long-form pins the
minimum builder length at 8, so every member has the same length and the oracle ordering
has **zero headroom** — G-SURF is vacuous there (the frozen rule records PASS at headroom 0)
and the scored-stage G4 is the only surface test that can bite on that world.

| world | chunks | min length | initial | tuning | future | viability | G-SURF |
|---|---|---|---|---|---|---|---|
| hc01-binary-ladder | 6 | 4 | 100 | 49 | 46 | viable | PASS (free capture 0.00, headroom 21) |
| hc02-square-shift | 6 | 4 | 523 | 224 | 447 | viable | PASS (free capture 0.13, headroom 258) |
| hc03-shift-runs | 8 | 5 | 304 | 203 | 303 | viable | PASS (free capture 0.25, headroom 253) |
| hc04-seven-triads | 7 | 6 | 16 | 8 | 7 | CANNOT_CHECK_world (below floor) | not run (non-viable) |
| hc05-long-form | 7 | 8 | 99 | 22 | 55 | viable | PASS (free capture 0.00, headroom 0) |
| hc06-decoy-pair | 7 | 4 | 127 | 63 | 146 | viable | PASS (free capture 0.08, headroom 115) |
| hc07-drawn-lot-a | 5 | 5 | 39 | 15 | 23 | CANNOT_CHECK_world (below floor) | not run (non-viable) |
| hc08-drawn-lot-b | 8 | 4 | 80 | 46 | 55 | viable | PASS (free capture 0.00, headroom 31) |
| hc09-negative-ladder | 6 | 5 | 122 | 59 | 58 | viable | PASS (free capture 0.00, headroom 22) |
| hc10-quartic-climb | 6 | 6 | 164 | 108 | 163 | viable | PASS (free capture 0.00, headroom 113) |
