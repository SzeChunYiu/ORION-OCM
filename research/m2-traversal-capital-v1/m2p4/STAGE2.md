# M2-P4 stage 2: the second-grammar package passes every entry gate (8 / 8 viable)

`ENTRY_GATES_PASS`. The authored package is admitted to scoring. No arm has run and
nothing is claimed here about whether the OCM benefit replicates in this grammar.

Run on laptop billy, never the Mac. Orchestrator `m2p4_check.py`, compiler
`m2p4_compile.py` (bounds identical to the spec), V2 static guard unchanged.

## Verdicts

| gate | result |
|---|---|
| taxonomy hostile (219 tokens) | **CLEAN**, 0 overlaps — scanner validated in the same run (no-alarm control passed, tamper control alarmed) |
| static pre-execution guard (V2) | **ACCEPT** — 1 required write, no forbidden module or call |
| determinism double-run | **DETERMINISTIC**, byte-identical |
| authoring floors | **FLOORS_MET** — 8 worlds (floor 6), 7 distinct shapes (floor 2), 8 unique chunk sets |
| compilation | **8 / 8 VIABLE** |
| G-SURF (blocking) | **8 / 8 PASS**, 0 surface-derivable |

## The worlds

| world | chunks | mbl | members | initial / tuning / future |
|---|---|---|---|---|
| brass_lantern | 12 | 4 | 135 | 68 / 29 / 38 |
| tin_orchard | 12 | 4 | 135 | 68 / 29 / 38 |
| deep_well | 10 | 8 | 100 | 38 / 25 / 37 |
| leaky_seam | 13 | 4 | 130 | 77 / 17 / 36 |
| long_and_short | 14 | 7 | 158 | 89 / 20 / 49 |
| narrow_gauge | 16 | 6 | 224 | 98 / 42 / 84 |
| shallow_shelf | 11 | 4 | 105 | 43 / 29 / 33 |
| twin_roots | 12 | 6 | 144 | 53 / 41 / 50 |

**The feasibility bound is confirmed against an independent author.** #424 derived
`members ≤ f + k²`, so k ≥ 10 is required to clear the 90-member floor, and predicted
viability only from k = 13 upward in random sampling. Every authored world sits at
k = 10..16 and every one clears the floor — including `deep_well` at exactly k = 10 with
100 members, close to the bound's `10 + 100 = 110` ceiling. A deliberate author reaches
the floor where random sampling did not.

## G-SURF: a wider no-false-fire margin than either calibration set

| world | verdict | capture | chance | free | oracle | best history-free ordering |
|---|---|---|---|---|---|---|
| brass_lantern | PASS | 0.0000 | 110 | 110 | 135 | ANCHOR_ASC |
| deep_well | PASS | 0.0000 | 81 | 81 | 81 | FS0_constant |
| leaky_seam | PASS | 0.0000 | 87 | 87 | 117 | ANCHOR_ASC |
| long_and_short | PASS | 0.0000 | 107 | 107 | 135 | ANCHOR_ASC |
| narrow_gauge | PASS | 0.0000 | 289 | 289 | 344 | ANCHOR_ASC |
| shallow_shelf | PASS | 0.0000 | 97 | 97 | 110 | ANCHOR_ASC |
| tin_orchard | PASS | 0.0000 | 105 | 105 | 119 | ANCHOR_ASC |
| twin_roots | PASS | 0.0000 | 112 | 112 | 153 | ANCHOR_ASC |

Capture is **0.0000 on all eight** against the 0.5 majority line: no feature family beats
the trivial ordering anywhere. The band-2–3 controls reached 0.2451 and the lane's own
band-3–4 calibration worlds 0.1053, so the margin here is wider than either. On
`deep_well` chance equals oracle (81), so there is no headroom for a surface rule to
capture at all.

## The assay history, recorded because it nearly produced false findings

Stage 2 took **eight attempts**. Every failure was in the harness or its invocation, not
in the package, and two of them produced verdicts that would have been wrong about the
authoring:

1. `ModuleNotFoundError: p1e3_taxa` — an import path outside the shipped archive.
2. `FileNotFoundError: ATOM_REGISTRY_V1.json` — a **data file** that import reads. Mapping
   imports was not enough; data reads had to be mapped too.
3. **`AUTHORSHIP_CONTAMINATED`** — 1 hit, `LANE_M2_TRAVERSAL_CAPITAL_OPUS`, in the
   `PROVENANCE.json` the *ingest tool* writes into the scanned directory. The author's
   three files scored 0 / 0 / 0. Fixed in the tool, which now self-scans its manifest and
   refuses; an unloadable scanner is fatal rather than recorded as `NOT_CHECKED`.
4. **`ASSAY_DEFECT_NONDETERMINISTIC_EMIT`** — both sandbox runs exited rc=2
   `can't open file`: the emitter never executed, because a relative `--authored-dir`
   does not resolve inside the orchestrator's scratch cwd. Run directly, the emitter is
   deterministic — two runs give `abeb3025…`, identical to the ingested file.
5. `ASSAY_DEFECT_GSURF_RUN_FAILURE` — all 8 G-SURF subprocesses rc=2: the orchestrator
   **spawns** G-SURF by `HERE / m2p2_gsurf.py`, and `HERE` is `m2p4/`. An import-probe
   cannot catch this, because the dependency is a subprocess spawn by path.

**No authored byte was ever modified and the package was never re-authored** — the freeze
forbids repeating an author session to obtain a different gate outcome, and re-authoring
would have "repaired" defects that were never in the package. Ledger row 64.

## Next

Stage 3, which needs its own registration frozen **before** the scored run: the registered
arms per world via `m2p1_runner.py`, then `m2p4_score.py` (terminal
`C2_REPLICATED_SECOND_GRAMMAR`, no point prediction carried over).

## Raw records

`stage2/` — 8 compiled worlds, 8 G-SURF verdicts, `M2P2_STAGE2_RECEIPT.json`.
sha256-verified on transfer from billy (bundle `0a849295…`).
