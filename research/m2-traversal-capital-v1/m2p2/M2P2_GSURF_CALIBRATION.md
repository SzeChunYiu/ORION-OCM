# G-SURF calibration record (pre-author instrument validation)

All runs below happened BEFORE the author session, on m2p1 public artifacts and a
synthetic validation package authored by this lane (never by the author unit). No
scored arm ran; no authored package existed. Host: billy-laptop-old, repo at
origin/main. Purpose: validate the frozen entry-gate instrument against ground
truth before it can void an authoring — the validate-the-checker-first rule.

## What was tested

`m2p2_gsurf.py` (probe machinery: FS0..FS5, `_dev`/`_free` dual fits, ORDER-mode
ladder, budgets 1000/4000/16000/64000/200000) applied to m2p1's own compiled
ecologies and to seven synthetic worlds (`VAL-A`..`VAL-H`) built by the lane as a
fake author.

## Defect found and repaired

The originally frozen #349-letter rule — PASS iff free-gain <= 2 AND dev-gain >= 5
ladder points vs the FS0 constant cell — is miscalibrated in BOTH directions on
hidden-family worlds:

| world | free gain | dev gain | letter verdict | ground truth |
|---|---|---|---|---|
| m2p1 E5 | 0 | 0 | CANNOT_CHECK_NO_RECOVERABLE_SIGNAL | recorded positive (HISTORY_INDUCED_SEARCH_PRIOR, scored-G4 PASS) |
| m2p1 E6 | 4 | 0 | SURFACE_DERIVABLE | recorded positive (HISTORY_INDUCED_SEARCH_PRIOR, scored-G4 PASS) |

Mechanism: the developmental signal in family worlds lives in fragment structure,
which no explicit feature cell expresses — so dev-fit gains ZERO even when the
scored arms show a large history-induced effect; and fine cells (FS2/FS5) win
small numbers of ladder points over the constant cell on sparse-target worlds
without approaching what the scored arms measure. "Both at chance" therefore does
NOT mean "no recoverable signal", and small free gains do NOT mean "surface
derivable".

## Recalibrated rule (now frozen in M2P2_FREEZE_V1.json)

- CHANCE = best zero-history ordering (FS0 constant, ascending, descending)
- FREE   = best history-free ordering (chance family + FS1..FS5 free fits)
- ORACLE = true-length ordering (ceiling of any length-class ordering)
- fires SURFACE_DERIVABLE iff `(FREE − CHANCE) >= 0.5 · (ORACLE − CHANCE)`

Parameter-free apart from the pre-registered majority line; dev fits are reported
as evidence and never gate; the decisive surface test remains the scored-stage G4
exactly as m2p1.

## Calibration results under the repaired rule

| world | capture | verdict | note |
|---|---|---|---|
| m2p1 E5 | 0.00 | PASS | recorded positive respected |
| m2p1 E6 | ~0.02 | PASS | recorded positive respected (old rule falsely fired) |
| VAL-A (linear pairs) | 0.42 | PASS | max capture observed anywhere |
| VAL-B (sqr pairs) | 0.11 | PASS | |
| VAL-C (mixed, mbl 6) | 0.14 | PASS | |
| VAL-D (7 chunks, mbl 5) | 0.03 | PASS | |
| VAL-H (8 all-sqr chunks, 2433 members) | 0.15 | PASS | most surface-exposed authoring tested |
| VAL-E / VAL-F / VAL-G | — | CANNOT_CHECK_WORLD | 9 / 44 / 45 members, below floors |

No authorable firing world was found in calibration (max capture 42%); the
majority line is retained as a guard against pathological authorings, not an
expected branch. The gate's no-false-fire property is proven on both recorded
positives.

## Instrument checks passed in the same session

- taxonomy hostile (219 tokens): CLEAN on every authored artifact, no-alarm and
  tamper controls both pass;
- static pre-execution guard: ACCEPT (no forbidden modules/calls);
- determinism double-run: byte-identical worlds.jsonl (sha256 equal);
- stream construction byte-verified against m2p1_ecology.py (quotas, hashed
  ordering, leftover-to-train, G1/G2/G3 definitions);
- non-viable worlds retained as CANNOT_CHECK_WORLD, never dropped;
- failed G-SURF subprocess runs are ASSAY_DEFECT, never a silent pass.
