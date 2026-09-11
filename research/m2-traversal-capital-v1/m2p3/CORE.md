# M2-P3 second-authoring replication — CORE (read first)

Lane `LANE_M2_TRAVERSAL_CAPITAL_OPUS`. Owner #165, hardening parent #323. Freeze:
[M2P3_FREEZE_V1.json](M2P3_FREEZE_V1.json), registered **before** any author session or scored run.

## The question

M2-P2's frozen terminal is `CANNOT_CHECK_NO_ADMITTING_WORLD`. The C2 benefit that survived the
target-(3) falsification (#411) is simple: the history-mined library, served guided-first, beats
RESET. It has been measured only on worlds from one author model (claude-fable-5-1). This study asks
whether it holds on worlds authored by a **second model** (claude-haiku-4-5), with the neutral spec,
the entry gates and the grammar unchanged.

## What is at risk

On hidden-chunk worlds, beating a no-library control cannot fail: the worlds are built from chunks,
so significance against RESET is guaranteed by construction. `SHUFFLED_HISTORY` is no better: it costs
about 2× RESET, which is the interleave identity again. The primary is therefore an **effect size**:

- **Per world:** `PARENT_GF_D4` (MDL library, depth 4, fixed in #411) is significantly **at least 50 %
  below RESET**. The test is a paired one-sided sign-flip permutation, Holm-corrected across worlds.
- **Terminal:** `C2_REPLICATED_SECOND_AUTHOR_MODEL` if at least 80 % of at least 4 viable worlds pass;
  `C2_NOT_REPLICATED` otherwise.
- **Co-registered point prediction:** median `GF_D4 / RESET − 1` = −88 % ± 8 points. A miss is recorded
  as a miss.

**Calibration on M2-P2's own records under this exact test: 7 / 8 pass.** hc08 (−59.9 %) fails the bar
(Holm p = 0.157). One more failing world in eight would fall under 80 %, so the falsifier can fire.

## What it can and cannot conclude

It can conclude that the C2 benefit is not an artifact of one model's authoring habits. The
shape-overlap and chunk-set overlap with M2-P2 are reported **next to the terminal**: heavy
collision means a small independence gain.

It cannot conclude:
- anything about a different model family (the author is the same Claude family and harness);
- anything about human authorship;
- OCM-specific superiority (target (3) stays FALSIFIED);
- general developmental intelligence.

## Stage status

| stage | state |
|---|---|
| 1 — freeze (this PR) | design and calibration only; no authored content, no scored run |
| 2 — author session + entry gates | **package A: `CANNOT_CHECK_EMITTER_REJECTED`** (the frozen guard rejects the spec-mandated write when the filename is spelled literally; [STAGE2.md](STAGE2.md)); its overlap result (0/7 shapes, 0/7 chunk sets) stands |
| 2b — V2 freeze (corrected guard implementation, calibrated) | **frozen by this PR**: guard 8 / 8 on real emitters and tamper controls; orchestrator reproduces M2-P2's stage-2 receipt in all 16 fields; [v2/M2P3_FREEZE_V2.json](v2/M2P3_FREEZE_V2.json) |
| 2c — fresh author session (package B) + V2 entry gates | **`ENTRY_GATES_PASS`**, 4 viable / 6, G-SURF 4 / 4 ([STAGE2B.md](STAGE2B.md)) |
| 3 — scored run (LUNARC 3600810, scored 3600991) | **`C2_REPLICATED_SECOND_AUTHOR_MODEL` (4 / 4)**, median −92.0 %, point prediction held ([STAGE3.md](STAGE3.md)) |

