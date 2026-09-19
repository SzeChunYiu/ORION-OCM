# gmi-833-ae-ae14-generalization-taxonomy-v1

Section AE14 of issue #833 asks that memorization, interpolation,
extrapolation, systematic generalization, analogy, planning/inference and
reasoning not be collapsed into one another by rhetoric. This package defines
all seven as exact predicates over `(task, learner class, training support)`,
evaluates them on one consistent finite roster in exact rational arithmetic,
and shows by exhaustive class enumeration which of them a prediction-only
learner can realize and which need composition machinery. The supports of the
three hard specifications were constructed by exhaustive search; the provenance
of every one is disclosed in the assumptions block of AE14-2.

Input space `X = {0,1}^4`, blocks `{x0,x1} | {x2,x3}`, junta arity `2`, tree
depth `2`, composition depth cap `3`, order-4 coordinate-rotation group,
`200` null trials. Every quantity is a `Fraction` or an `int`.

## The load-bearing table

At each mode's registered home specification, the best accuracy attainable over
the **whole** of each enumerated prediction-only class, against the composition
class at the registered depth cap:

| structure type | mode | constraint points | `L0` | `L1` | `L_lin` | `L_mod` | `L_search[3]` | least class that realizes it |
|---|---|---|---|---|---|---|---|---|
| `LOOKUP_ONLY` | memorization | 16 | **13/16** | 11/16 | 13/16 | 13/16 | 13/16 | `L0` |
| `JUNTA` | interpolation | 8 | 3/4 | **1** | 3/4 | 1 | 7/8 | `L1` |
| `AFFINE` | extrapolation | 12 | 2/3 | 7/12 | **1** | 1 | 3/4 | `L_lin` |
| `BLOCK_FACTORIZED` | systematic generalization | 16 | 7/8 | 3/4 | 3/4 | **1** | 7/8 | `L_mod` |
| `GROUP_ORBIT` | analogy | 15 | 11/15 | 11/15 | 11/15 | 13/15 | **1** | `L_search` |
| `COMPOSITION_DEPTH_GE_2` | planning/inference | 10 | 4/5 | 4/5 | 4/5 | 4/5 | **1** | `L_search` |
| `DEDUCTIVE_CLOSURE` | reasoning | 10 | 4/5 | 9/10 | 4/5 | 9/10 | **1** | `L_search` |

`L0` is every function constant off the support, `L1` every 2-junta computable
by a depth-2 decision tree (70 functions), `L_lin` all 32 GF(2)-affine
functionals, `L_mod` every block-modular composition (520 functions). Each is
enumerated whole, so the three bottom rows are not a survey: **no** member of
any prediction-only class is exact on those constraint sets, and an
`L_search[3]` learner is exact on all of them. Depth 1 is not enough for any of
the three.

**Four modes reduce to prediction** at their registered specification
(memorization, interpolation, extrapolation, systematic generalization);
**three require the additional machinery** (analogy, planning/inference,
reasoning). Which machinery is named exactly: analogy and planning are realized
by transport members (`lookup|pi2+rho|d`, `lookup|pi1+pi2|d`), reasoning only by
a derivability readout (`atom|tau|5`) — the transport readout realizes no
reasoning member at all.

## The other rows

**Matched predictive pair.** `T_MATCH_COMPOSITIONAL` and `T_MATCH_LOOKUP` agree
on the whole shared training view, so their Bayes predictive accuracy on the
registered test distribution is **exactly equal, `3/4` versus `3/4`**. On the
two held-out block recombinations the shortest-code model consistent with that
view (index 0, `3` bits) scores **`0` on the compositional task and `1` on the
lookup task**.

**Matched compression pair.** `T_CODE_A` and `T_CODE_B` sit at indices `16` and
`20` of the frozen model order, so both have description length **exactly `11`
bits** under the Kraft-compliant integer code (whole-space Kraft sum
`523273/2097152 <= 1`). Their exact transfer accuracy to the registered target
task differs: **`3/8` versus `3/4`**.

**Mechanism predictor.** The frozen table maps all `7` registered structure
types to the class that actually turns out to be least: **`7/7`**, against a
largest hit count of **`4`** over the `200` registered uniform null trials
(rate at or above the predictor: `0/200`). The `LOOKUP_ONLY` cell is
guaranteed by the definition of the base rate and is declared as such; the six
evidential cells score `6` against a null maximum of `4`. Beyond the seven
registered instances, an exhaustive family sweep over every function whose least
structure type is the swept one gives hit rates `1` (affine, 10 members), `1`
(junta, 48), `1` (block-factorized, 432), `1` (composition-depth, 2) and
`26/27` (group-orbit, 54).

**Null controls.** A uniformly random relabelling of the input space is applied
to all three hard specifications at once, `200` times. The primary magnitude is
conjunctive — the number of the three specifications on which the detector fires
— because a single specification is not by itself a rare event under the
control: the planning specification fires on `20` of the `200` controls and the
reasoning specification on `14`, while the analogy specification fires on `0`.
The witness scores `3`; the largest control scores `2`; the rate at or above the
witness is `0/200`, and the detector stays silent on all four known-clean
specifications.

**Forbidden blanket claim.** The registered promotion is blocked: a reduction
theorem would need a prediction-only learner realizing every mode, and the
enumeration exhibits three specifications where none does. An executor check
scans every artifact of the package and reports `0` assertions of the blanket
string; the checker is validated in both directions.

## Reported refutation

`AE14-P1` predicted a complete pairwise distinctness table. `41` of the `42`
ordered pairs are separated by a registered witness, all of them with a
non-empty structure on both sides. The remaining pair cannot be separated at any
support whose recombination structure is non-empty: that constraint set is
contained in the interpolation constraint set for **every one of the 65310 such
supports**, so interpolation implies systematic generalization there. The prediction
is reported as `REFUTED` with that certificate rather than edited (AE14-8).

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae14-generalization-taxonomy-v1/test_ae14_generalization_taxonomy_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae14-generalization-taxonomy-v1/test_ae14_generalization_taxonomy_v1.py -v
python3 -I -B  research/gmi-833-ae-ae14-generalization-taxonomy-v1/ae14_generalization_taxonomy_v1.py
python3 -I -B  research/gmi-833-ae-ae14-generalization-taxonomy-v1/independent_taxonomy_oracle_v1.py
```

The executor writes `RESULT_V1.json` to stdout. It was verified byte-identical
under `-I -B` and `-I -O -B` on CPython 3.8 and on CPython 3.9; the workflow
re-runs it on CPython 3.12 in both modes and compares against the committed
file.

## Claim ceiling

`GMI_833_AE14_GENERALIZATION_MODES_OPERATIONALLY_SEPARATED_ON_REGISTERED_FINITE_TASK_ROSTER`

The classification of a mode as reducible or as needing composition machinery is
stated **at its registered home specification**, not in general: the receipt also
reports that off its home task, extrapolation on the analogy task is itself
realized only by the composition class. Nothing here extrapolates beyond
`n = 4`, the registered budgets, or the registered roster.
