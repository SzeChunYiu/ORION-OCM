# gmi-833-capability-predictor-v1

#833 Section K: the exact capability predictor `C_hat = F(M,E,R,H,D,U)`, a
prospectively frozen failure-mode taxonomy, and total typed uncertainty
attachment, all at a registered finite scope.

Claim ceiling:
`GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE`

## What is closed

| row | results | headline |
|---|---|---|
| Build `C_hat = F(M,E,R,H,D,U)` | KP-1A/1B/1C (+KP-1D boundary) | exact total deterministic `F` on 51,840 inputs: 10,640 points, 10,960 abstentions, 30,240 inconsistent, 0 exceptions, **0 soundness violations** |
| Derive failure modes prospectively | KP-2A/2B/2C (+KP-2D boundary) | ten modes frozen before the executor; **0 overlaps, 0 gaps, 0 unique-binding-cut violations**; all ten non-empty |
| Attach uncertainty/calibration | KP-3A/3B/3C | single `emit` site (0 bare returns), 0 feasible sets carrying coverage, U-2B budget exact, coverage **100,800/100,800** |

## The load-bearing design decision

`M`, `H`, `D` and the registered search-budget cut decide **candidacy** (which
realizations are consistent with the inputs). `E` and `R` decide the **contract
verdict**: a resource-inadmissible candidate is scored `UNSATISFIED` *inside the
image* rather than deleted from the survivor set. Deleting it would falsify
KP-1B; hostile `H4_resource_prune` exhibits 3,064 soundness violations produced by
exactly that deletion, and `H5_unsatisfied_as_zero` shows 3,516 inputs whose image
changes if `UNSATISFIED` is coerced to `0`.

## Hostiles, all DETECTED

| id | planted defect | detection |
|---|---|---|
| H1 | force the smallest member of a multi-valued image | 10,960/10,960 forced points refuted by a surviving counterexample |
| H2 | one code path returns a bare value | `ast` funnel audit flags the bare return; the true module is clean |
| H3 | `<=` at one taxonomy rung / delete `FM_ALIASING` | 5,184 overlap inputs and 3,529 gap inputs flagged; **0 alarms on the true taxonomy** |
| H4 | prune the survivor set by resource admissibility | 3,064 soundness violations |
| H5 | coerce `UNSATISFIED` to `0` | 3,516 inputs change |
| H6 | independence product instead of the union bound | product `9152473869/10000000000` > union `913/1000`, refused |
| H7 | truncate the identified set | 10,960/10,960 coverage failures |
| H8 | `emit` contract violations (bare value, fabricated coverage, wrong budget, single-valued abstention) | all four refused with `ValueError` |
| H9 | parent result blob mutation | blob sha mismatch |

Null control `NULL_MARGINAL` (emit the modal capability `1/2` always): 51,840 point
emissions, **51,840 soundness violations**. Head to head on the 10,640 inputs where
`F` actually emits a point, the null is unsound on **10,640 of 10,640** and `F` on
**0**; restricted to the 21,600 inputs with a nonempty survivor set the null is
unsound on all 21,600.

## Boundaries, earned by counterexample

- **KP-1D.** Soundness is unconditional over *consistent* worlds. The bridge to an
  actual system needs truthful registration, and that premise is not removable:
  with `K_M = {0}`, budget `(2,1,1)`, `B_dev = 2`, `B = 12` the predictor soundly
  emits `0` while the excluded realization at index 4 has capability `1/2`.
- **KP-2D.** First-crossing attribution is order-dependent: 6,347 of 8,640 inputs
  change label across the 120 cut orders. The sharp counterexample has exactly one
  individually-binding lever (`Res`) yet three distinct labels; 488 inputs are of
  that kind. The unconditional positive that survives is KP-2C.

## Deliberately left open (second tranche)

Held-out synthetic species, held-out known architectures, real trained systems,
pre-evaluation qualitative failure prediction, quantitative resource/capability
curves, empirical calibration error, out-of-distribution failure. The predictor is
parameterised by the registered universe so a held-out universe substitutes
without touching `F`.

## Reproduce

```bash
python3 -I -B  research/gmi-833-capability-predictor-v1/capability_predictor_v1.py > /tmp/route_a.json
cmp /tmp/route_a.json research/gmi-833-capability-predictor-v1/RESULT_V1.json
python3 -I -O -B research/gmi-833-capability-predictor-v1/capability_predictor_v1.py | cmp - /tmp/route_a.json
python3 -I -B  research/gmi-833-capability-predictor-v1/oracle_route_b_v1.py
python3 -I -B  research/gmi-833-capability-predictor-v1/test_capability_predictor_v1.py -v
python3 -I -O -B research/gmi-833-capability-predictor-v1/test_capability_predictor_v1.py -v
```

Stdlib only, exact `Fraction`/`int` arithmetic, no floats in any claim. The
executor takes about 15 s and the 37 tests about 35 s on a laptop-class CPU.
Route A md5: `9f4c0d0c5910fa081fa10dc4e371effc` (both modes, at the pinned parents).

## What the second route does and does not cover

Route B independently reproduces, on all 51,840 inputs: the disposition, the exact
identified set, the failure mode, and the composed confidence budget — plus the
144-case semantics sub-census and the aggregate dispositions, mode counts, coverage
and soundness totals. It is the reason `KP-3B`'s budget number is a two-route
agreement rather than a self-comparison.

Single-route (route A only, and labelled as such): the 120-order census of KP-2D,
the null control, the nine hostiles, and the `ast` emit-funnel audit. The KP-2D
order-sensitivity figures bound a declared limitation rather than support a claim.
