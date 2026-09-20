# Z11 parent-ownership disclosure

Assimilation-first: IMB-v1 assembles instruments its parents own; the residual
is stated narrowly at the end.

## External parents (nothing here is claimed novel against them)

| parent | what it owns | citation |
|---|---|---|
| Preregistration / registered reports | publishing generation rules and predictions before outcomes | Nosek, Ebersole, DeHaven & Mellor, *PNAS* 115(11):2600–2606, 2018, doi:10.1073/pnas.1708274114 |
| Hash commitments | committing to a hidden seed by its `sha256` and revealing the preimage later | Blum, *Coin flipping by telephone*, CRYPTO 1981; Halevi & Micali, CRYPTO 1996, doi:10.1007/3-540-68697-5_16 |
| Set-valued / conformal prediction and calibration | coverage targets `γ`, sharpness, calibration by declared level | Vovk, Gammerman & Shafer, *Algorithmic Learning in a Random World*, Springer 2005, doi:10.1007/b106715; Dawid, *JASA* 77(379):605–610, 1982, doi:10.1080/01621459.1982.10477856 |
| Permutation / label-shuffle controls | scoring against scrambled truth as a leakage detector | Good, *Permutation Tests*, Springer 2000, doi:10.1007/978-1-4757-3235-1 |
| MDL | two-part code model selection (`T_MDL`) | Rissanen, *Automatica* 14(5):465–471, 1978, doi:10.1016/0005-1098(78)90005-5 |
| SRM | fixed-price structural risk minimisation (`T_SRM`) | Vapnik, *The Nature of Statistical Learning Theory*, Springer 1995, doi:10.1007/978-1-4757-2440-0 |
| Satisficing | the cheapest level meeting an aspiration (`T_SATISFICE`) | Simon, *Q. J. Econ.* 69(1):99–118, 1955, doi:10.2307/1884852 |
| Bounded optimality / decision theory | argmin of the declared cost (`T_DECLARED`) | Russell & Subramanian, *JAIR* 2:575–609, 1995, doi:10.1613/jair.133 |
| Benchmarks with hidden test sets | held-out evaluation, generation rules published, test outcomes hidden | standard practice; no single owner is claimed |

**Not claimed novel:** preregistration, commitments, coverage/calibration
scoring, permutation controls, or any competitor theory.

## On-main parents (pinned by blob sha in `MANIFEST_V1.json`)

| package | what it owns | how this package uses it |
|---|---|---|
| `gmi-833-z-z6-discrimination-v1` (`DS-1`..`DS-6`) | the 13-rule competitor registry and the proof that every declared-cost parent is observationally equivalent to the repaired law while `MDL`/hard-Occam/`SRM` disagree | the registered theories `T_DECLARED`, `T_MDL`, `T_OCCAM_HARD`, `T_SRM`; `B4`/`B5` re-test its finding on a `519`-case benchmark with hidden and empirical cases |
| `gmi-833-z-z12-prediction-scoring-v1` | the exact scoring vocabulary (`COV`, `SHP`, `VAC`, `ABS`, `CAL`) | §4 scoring is that vocabulary applied to five prediction fields |
| `gmi-833-z-z8-hostile-ingredients-v1` (this branch, sibling package) | period-2 aliasing floors, the two-level shift population | the `PERIOD2` law and the seven-law `IID` population are the same objects |
| `gmi-833-capability-predictor-evaluation-v1` (`KE-6`, `KE-7`) | held-out/OOD evaluation of an exact predictor | the hidden-ecology class is the same discipline applied to theories |

## Sibling-branch parents (named results, not on `source_main`; not pinned by blob)

`gmi-833-z-z13-adjudication-v1` `ZA-1` (base ladder floors, re-enumerated here);
`gmi-833-z-z1-master-principle-v1` `IC-1`, `IC-1b`, `IC-1c` (the law `T_GMI_IC1`
implements; the level-valued `Z13-P1` law is `T_LEVEL`).

## The named residual of this tranche

1. **A benchmark whose scored object is a theory**, not a model: each case is a
   public specification, the truth is enumerated and hidden, and every registered
   theory is a committed pure function scored on five fields at once.
2. **Empirical-stream workloads with exact truth**: real byte streams pinned by
   blob sha give non-synthetic input laws whose floors are still enumerable, and
   the closed-form pair-Bayes prediction is tested against them (`9/9`, `3/3`).
3. **Hidden ecologies under a hash commitment** with the draw protocol replayed
   by an independent route to the same `sha256`.
4. **The informative-cell scrambled control** and the published finding that the
   frozen all-cell form is a false-positive instrument (`8/9` clean theories
   alarmed), together with the recorded false alarms of the refined form on
   price-blind theories.
5. **A competitor table on `519` cases** in which `T_DECLARED` is proved
   non-discriminating and reported as such rather than as a win.

Nothing here says any theory is *true* beyond the registered finite scope.
