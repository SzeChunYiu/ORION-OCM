# gmi-833-execution-controls-v1

Issue #859 (child of #833 Section D). Freeze: `FREEZE_V1.md`, commit `3682a045`, committed before any code in this directory.

Claim ceiling: `GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE`.

## What this package delivers

A reusable, fail-closed admission gate for derivation claims, plus a full run of that gate on one registered result family. The family is the #901 package `gmi-833-heldout-20-transitions-v1`: 65,552 binary sequential candidates, the frozen law `lambda* = eta*p/2`, and 20 cases giving 40 endpoint worlds and 20 boundary worlds.

- `robustness_record_v1.py` holds the `DerivationRobustnessRecord` schema (`GMI833DerivationRobustnessRecordV1`) and its validator. It is stdlib-only and has no link to the substrate, so later Section H/J packages can load it by path. It returns `ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE` only when all five admission conditions hold. Otherwise it returns `CANNOT_ESTABLISH_D_ROBUSTNESS_<CONTROL>` together with the full ordered list of per-control typed terminals. The validator checks itself first: it must pass a toy record with no alarm, and it must fire on each toy corruption.
- **D-X1, matched mechanism-removal twin.** The mechanism `K` is data-dependent internal state. The twin `G-` ablates the state register in place: every next-state table becomes the constant-0 table. This keeps all nine non-K capacity coordinates equal (65,552 candidates each). The K-free scored behaviour collapses onto the same 16 classes, and the multiplicity change from 33 to 4097 per class is reported. The #901 law holds 20/20 on `G+` and gives STATELESS at all 60 worlds on `G-`. Hostiles H1a (stateful block deleted), H1b (`READ_PREV` macro), H1c (half the sequence set) and H1d (half the budget) are all `UNMATCHED_MECHANISM_TWIN`. H1a is refused even though the objective gets worse at 20/20 low endpoints. The ecology twin `E-` swaps the lag target for a second current-symbol target and matches on every other descriptor coordinate. Its two hostiles are unmatched.
- **D-X2, alternate encoding.** E2 is a separate rule-list encoding with its own evaluator: symbols `P,R,U,V,a,b`, Gray-ordered rules, `W`-prefixed base-26 ids. The registered bijection covers all 65,552 candidates, and 0 candidates differ after the canonical projection `rho = (s, en, ed)`. Winner ids map correctly at all 60 worlds. Terminal: `ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE`. Hostiles: a map that drops one candidate and a delay-cost rescale are both `ENCODING_NOT_SEMANTICALLY_EQUIVALENT`, and a tie-break on lexicographic surface ids is `ENCODING_SENSITIVE`.
- **D-X3, alternate search.** Three procedures run: S1 exhaustive enumeration (#901 code), S2 risk-frontier branch-and-bound (#901 code), and S3 best-first with an optimality certificate and a mandatory tie sweep (new). Each has a verified completeness certificate. Distinctness is certified mechanically from canonical evaluation traces and acceptance sequences. Search cost is reported separately from candidate resource cost. Terminal: `SEARCH_ROBUST`. Hostiles: a first-accept early stop is `SEARCH_SENSITIVE`, with each disagreeing world listed. S2 run over relabelled ids and declared as a third procedure is `SEARCHERS_NOT_MATERIALLY_DISTINCT`.
- **D-X4, Pareto relation and scalarizations.** The exact Pareto set is `{(en,ed,s) = (0,8,0), (0,0,1)}`. There are 30 preregistered strictly positive scalarizations and 20 boundary probes. Wording is split three ways: price-conditional claims are consistent, universal-winner wording is `SCALARIZATION_SENSITIVE` (on the census pair and on the issue's literal `(1,4)`/`(4,1)` fixture), and the frontier invariants hold. The metric perturbation control derives each world's bound from its own phase margin. Across 1,008 perturbed worlds the winner-state partition is stable in all three encodings. The partition ties exactly at the boundary and flips at the mirrored price at 40/40 endpoints.
- **Admission census.** 22 records, each matching its exact typed terminal: the positive witness, five single-control deletions, the targeted hostiles, and cross-control combinations.

## Routes

Route A is made of the modules listed in `MANIFEST_V1.json`, with S1/S2 reused from #901 and the #855 auditor run unchanged on every compared arm. Route B is `independent_oracle_v1.py`. It uses only the standard library and imports no route-A module, no #901 code and no #855 code. It parses the frozen case grid from the #901 freeze text and recomputes every shared fact on its own. The two receipts agree on every shared fact.

## Reproduce

```bash
python3 -I -B research/gmi-833-execution-controls-v1/independent_oracle_v1.py --check
python3 -I -B research/gmi-833-execution-controls-v1/execution_controls_v1.py --check
python3 -I -B research/gmi-833-execution-controls-v1/test_execution_controls_v1.py -v
python3 -I -O -B research/gmi-833-execution-controls-v1/test_execution_controls_v1.py -v
```

## Boundaries

- This package does not reconcile any #833 row. The four Section-D rows named by #859 were closed through #863, and the four rows named in the freeze are closed by other packages. The receipt records `reconciliation.emitted = false`.
- Every result holds at the registered finite scope: the #901 family, its 60 worlds and its registered encodings, searchers and weights. Forbidden promotions are listed in `MANIFEST_V1.json`.
- `deviations_from_freeze` in `RESULT_V1.json` lists each reading this package had to fix where the freeze left a choice open.
