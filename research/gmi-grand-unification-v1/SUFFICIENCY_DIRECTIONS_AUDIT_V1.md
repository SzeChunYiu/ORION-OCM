# Sufficiency and certificate-direction audit V1

Date: 2026-09-13

This iteration repairs three false converse/sufficiency claims and one proof sentence. Each has a separate witness and a bounded corrected conclusion. It does not certify all Grand-GMI claims.

| Audit ID | Location | False implication or direction | Corrected scope |
|---|---|---|---|
| SD-ACL2 | Active Closed-Loop theorem, ACL-2 | An affordable distinguishing probe implies an adequate active policy. | Acquisition necessity is separate from admitted retention, legal terminal action and complete-policy resource feasibility. |
| SD-GEI3 | Generalization Ecology Inference theorem, GEI-3 | Failure of one sufficient upper bound proves the sample evidence insufficient. | That bound does not certify; another valid certificate may succeed, with confidence/adaptivity handled explicitly. |
| SD-GR5 | Reflective Self-Reference theorem, GR5 | Excluding diagonal feedback implies an exact self-predictor exists. | Self-probe identifiability and an admitted exact predictor are also required. |
| SD-ERI5 | Empirical Resource Identification theorem, ERI-5 proof | A coordinate lower envelope can move either way under arbitrary subset refinement. | Nonempty subset refinement cannot decrease any coordinate infimum or increase any supremum. The original universal-domination theorem remains valid. |

## SD-ACL2: acquiring a bit does not retain it

The latent bit is `h`, the required terminal action is `h`, and the probe reveals `h` at cost one. A forced blank step removes that observation. If the complete budget admits only one persistent controller state, every terminal policy sees the same internal state and blank observation in both worlds. The two deterministic policies each succeed on only one world; randomization cannot give success one on both. All four original ACL-2 premises hold while its active-feasibility conclusion fails.

An admitted two-state encoder/decoder restores feasibility. The checker independently varies sensing budget and memory-bit budget over `{0,1}`. Only the budget combination admitting both the probe and one retained bit has an exact delayed policy. The original active-loop microscope already enumerated the two-state positive case; its receipt is preserved.

## SD-GEI3: a failed certificate is not an impossibility theorem

With a single candidate, one zero-loss sample and `delta=1/20`, the raw Hoeffding bound exceeds one. Losses are already bounded by one, so the obligation `risk<=1` holds certainly. Clipping alone repairs that boundary.

For a nontrivial same-data comparison, preregister the two-sample rule `U=.8` if both losses are zero, and `U=1` otherwise. If the true bounded-loss risk `R>.8`, then `Pr(X=0)<=1-R<.2`, so the independent two-zero event has probability below `.04`. If `R<=.8`, the rule always covers. Thus the rule has at least `.96` coverage for every iid loss law on `[0,1]`. Its all-zero output certifies tolerance `.8` at confidence exceeding `.95`, while the raw two-sided Hoeffding upper bound is approximately `.9603` and fails the same tolerance.

This compares valid registered procedures. It does not allow uncalibrated data-dependent selection of the minimum among confidence bounds. The checker computes exact miscoverage for 66 rational probability laws on `{0,1/2,1}`; the general bounded-loss guarantee follows from the analytic argument above. The numerical Hoeffding comparison is far from the threshold and is reported as numerical.

The finite-class Hoeffding bound is parent theory: see Hoeffding, [*Probability Inequalities for Sums of Bounded Random Variables*](https://www.csee.umbc.edu/~lomonaco/f08/643/hwk643/Hoeffding.pdf). The zero-event argument is included directly here; no new statistical-learning result is claimed.

## SD-GR5: non-reactive targets can remain hidden

Two internal states return the same admitted self-probe symbol, but their fixed future target bits are zero and one. No prediction-reactive intervention exists. Nevertheless, every predictor using only the common probe output fails in at least one state. This is an instance of GR6/GIR-2, not a diagonal paradox.

Across the 16 possible binary probe/target maps on two self-states, exactly four non-reactive problems admit no exact predictor. Exhaustive predictor search agrees with target constancy on probe fibers in all 16 problems. Refining the self-probe to identify the hidden state restores a mathematical exact predictor; physical feasibility still requires an admitted implementation. The original positive reflection witness supplies the entire finite target table and identifiable context, so its 2,048 exact context predictions remain valid at that narrower scope.

## SD-ERI5: subset envelopes have fixed signs

For arbitrary nonempty nested profile sets, the infimum of a coordinate over the smaller set is at least its old infimum, and the supremum is at most its old supremum. This does not require box structure. For instance, restricting `{(0,4),(2,1),(3,3)}` to `{(2,1),(3,3)}` raises the first lower envelope from zero to two and lowers the second upper envelope from four to three.

The checker exhausts 65 nonempty nested pairs of subsets of the binary square. A separate test preserves universal strict Pareto domination under all nonempty subset restrictions of a fixed winner/loser pair. The correction only repairs the proof sentence; non-nested evidence and unsupported confidence claims receive no new monotonicity guarantee.

## Verification and limits

The new suite contains 11 tests; the original reflective receipt test and the active-loop, generalization-ecology and empirical-resource checkers are retained. The additive receipt is `GRAND_GMI_SUFFICIENCY_DIRECTIONS_RECEIPT_V1.json`.

```bash
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_sufficiency_directions_v1.py' -v
python -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_reflective_checks_v1.py' -v
python research/gmi-grand-unification-v1/grand_gmi_sufficiency_directions_checks_v1.py --out research/gmi-grand-unification-v1/GRAND_GMI_SUFFICIENCY_DIRECTIONS_RECEIPT_V1.json
```

These results establish the stated finite witnesses and corrected logical directions. They do not prove general controller synthesis, unrestricted reflection, empirical adequacy of a morphology, or confidence validity for an undeclared evidence-generation process.
