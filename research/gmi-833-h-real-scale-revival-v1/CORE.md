# gmi-833-h-real-scale-revival-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue #833
for the three named-family rows `gmi-833-h-real-scale-classical-v1` left open
with single-stage failure attributions: `Linear regression / linear
classifiers.`, `GLMs.`, `Basis/kernel methods.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates are earned, or reported open, at this package's own three scopes —
`SIGMA_R02`, `SIGMA_R03B`, `SIGMA_R04B` — on sha256-bound real sources, with
exact rational arithmetic and two materially independent routes.
`CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions` and a test asserts
that no gate certificate carries a scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Basis/kernel methods.` | `SIGMA_R04B` | **closed**, 11 of 11 — `RSR-3` |
| `Linear regression / linear classifiers.` | `SIGMA_R02` | **open**, 9 of 11 — `RSR-1` |
| `GLMs.` | `SIGMA_R03B` | **open**, 8 of 11 — `RSR-4` |

One closure and two reported negatives, each diagnosed to a single stage. The
negatives are the more useful part of the tranche and are stated as named
results, not as apologies.

## The three levers, one per open row, and what each did

| row | the parent's single-stage attribution | the lever applied here | what happened |
|---|---|---|---|
| Linear regression / linear classifiers. | `null` — a least-squares control on a permuted design **nests** the constant arm, so the comparison was a coin flip | a response-permutation control that cannot nest its comparison arm, plus an **applicability band**: all 200 refits must land within `[9/10, 11/10]` of the constant arm or the run fails | the control worked and is certified (`RSR-2`), but the row failed on a different, registered prediction: the class was recovered and the head expression was not identified (`RSR-1`) |
| GLMs. | `ecology` — a per-line digit count is zero on most rows, so a per-row closeness criterion rewards an arm that can predict exactly zero | an ecology whose response is `>= 1` by construction, with admissibility asserted in exact arithmetic before any arm is fitted; the criterion carried over unchanged | the criterion the parent failed now **holds**, 22,278 of 37,948; the family-blind search still does not recover a link (`RSR-4`) |
| Basis/kernel methods. | `ecology` — next-window energy is not additive in any per-input non-affine transform, so a squared affine score sufficed | an ecology whose response **is** additive in a per-input non-affine transform; the classifier is not re-read and not re-ordered | recovered, and the row closes (`RSR-3`); the parent's outcome and this package's own first attempt are recorded as the boundary (`RSR-5`) |

## The custody chain

Four files, each committed alone and before the artifacts it governs, with CI
asserting the order:

1. `FREEZE_V1.md` — scopes, ecologies, slice rule, grammar, real-scale
   definition, every prediction. Committed before any implementation exists.
2. `FREEZE_V1_ARITHMETIC_ADDENDUM.md` — fixes the rationalisation operator so
   exact sums are computable. Changes no prediction.
3. `FREEZE_V2_ADDENDUM.md` — the one permitted revival per failed prediction,
   with the two levers and the newly frozen prediction set. The first run's
   receipts stay committed under `REAL_RUNS_V1/`.
4. `FREEZE_V3_ADDENDUM.md` — corrects a defect in the ranking stage: it scored
   in sample, which rewards capacity on a grammar containing a delay cell. The
   correction **cost this tranche a closure** and was registered before the
   re-run, when its direction was unknown (`RSR-7`).

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-revival-v1
python3 -I -B  independent_oracle_v1.py          # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_revival_v1.py          # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_revival_v1.py -v
```

To re-run the real-scale fits from the bound sources (host of record only,
needs numpy, roughly half an hour):

```
OMP_NUM_THREADS=1 REVIVAL_WORKERS=14 python3 -B run_real_scale_revival_v1.py --controls
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + three addenda | the custody chain above |
| `grammar_s_v1.py` | the lower grammar `G_S`, its enumeration, semantic quotient, digest, post-hoc classifier and charged cost model |
| `run_real_scale_revival_v1.py` | the real-scale run driver; the only file that reads the real sources |
| `real_scale_revival_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_revival_v1.py` | custody, scope, slice, classifier, cost and negative-control tests |
| `REAL_SCALE_REVIVAL_THEOREMS_V1.md` | `RSR-1`…`RSR-7` with scope, quantifiers, falsifiers and forbidden extrapolations |
| `PARENT_LEDGER.md` | strongest parents with citations, what is not claimed novel, the residual contribution |
| `SECTION_H_RESIDUAL_OBSTRUCTION_V1.md` | why the five Section-H rows at 7 of 11 are not closed here; closes nothing |
| `REAL_RUNS_V1/`, `REAL_RUNS/` | the first run's receipts and the corrected run's receipts, both kept |
| `ISSUE_833_RECONCILIATION_H2_V1.json` | the reconciliation artifact; this package never edits the issue body |
