# Z12 parent-ownership disclosure

Assimilation-first: the strongest parents are absorbed and named, and the
residual contribution of this tranche is stated narrowly.

## External parents (nothing here is claimed novel against them)

| parent | what it owns | citation |
|---|---|---|
| Conformal / set-valued prediction | set-valued predictors with coverage guarantees, the whole idea of scoring a prediction *set* rather than a point | Vovk, Gammerman & Shafer, *Algorithmic Learning in a Random World*, Springer 2005, doi:10.1007/b106715 |
| Selective prediction / reject option | abstention as a first-class prediction outcome and its risk-coverage trade-off | Chow, *IEEE Trans. Inform. Theory* 16(1):41-46, 1970, doi:10.1109/TIT.1970.1054406; El-Yaniv & Wiener, *JMLR* 11:1605-1641, 2010 |
| Proper scoring rules | Brier score, propriety, the decomposition of a score into calibration and refinement | Brier, *Monthly Weather Review* 78(1):1-3, 1950, doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2; Gneiting & Raftery, *JASA* 102(477):359-378, 2007, doi:10.1198/016214506000001437 |
| Calibration | reliability diagrams, the empirical-frequency-versus-claimed-probability comparison | Murphy & Winkler, *J. R. Statist. Soc. C* 26(1):41-47, 1977, doi:10.2307/2346866; Dawid, *JASA* 77(379):605-610, 1982, doi:10.1080/01621459.1982.10477856 |
| Regret | minimax/decision-theoretic regret as the price of a wrong decision | Savage, *JASA* 46(253):55-67, 1951, doi:10.1080/01621459.1951.10500768 |
| Preregistration | freezing predictions before outcomes so post-hoc widening is detectable | Nosek, Ebersole, DeHaven & Mellor, *PNAS* 115(11):2600-2606, 2018, doi:10.1073/pnas.1708274114 |

**Not claimed novel:** set-valued prediction, abstention, Brier, calibration,
regret, or preregistration as concepts. All six are parent-owned.

## On-main parents (their results are the scored object, not this package's claim)

| package | what it owns | how this package uses it |
|---|---|---|
| `gmi-833-heldout-20-transitions-v1` (#901) | the 20 held-out morphology transitions, the boundary law `lambda* = eta·p/2`, the 65,552-candidate universe, the two source-separated search procedures, the recorded controls | `POP_M` is built from its receipt; route B **re-derives** its controls independently as a cross-check and reproduces all five exactly |
| `gmi-833-capability-predictor-evaluation-v1` (#1022) | the frozen capability prediction sets, the external truth sets, and — importantly — **exact coverage and an exact calibration-error table of its own** (`KE-6`) | `POP_K` is built from its frozen predictions joined to its external truth; its `KE-6` result is credited wherever coverage or calibration is reported |
| `gmi-833-capability-abstention-v1` | an abstention theorem for the capability predictor | credited under `Z12-ABS`; this package adds the executable soundness gate, not the theorem |

## The named residual of this tranche

1. **One instrument, two prediction objects.** A single scoring protocol with
   uniform definitions applied to a *morphology* population and a *capability*
   population, so Z12's nine requirements are answered by one instrument rather
   than by per-lane conventions.
2. **`CAL-LEM`**, the exact finite identity that makes element-level calibration
   the right level for set-valued predictions, together with the diagnosis of why
   the record-level instrument this package originally froze was mis-specified
   (`FREEZE_V1_AMENDMENT_2.md`).
3. **The truth-conditioned vacuity definition** that separates vacuity from
   licensed abstention — without which 20 correct tie predictions on a binary
   morphology alphabet would be flagged as vacuous.
4. **Refusal-as-penalty for post-hoc widening**, demonstrated load-bearing by a
   truth-leaking hostile that would otherwise score perfectly.
5. **Exact regret pricing of morphology selection** with a blind-selection
   hostile that pays `15/2`, proving the observed `0/1` is a property of the
   predictions and not of the scorer.

Nothing in this package claims that any scored prediction is *true* beyond the
frozen scope its own lane established.
