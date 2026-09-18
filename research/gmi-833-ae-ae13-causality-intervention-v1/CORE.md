# gmi-833-ae-ae13-causality-intervention-v1

Section AE13, all six Tier-1 rows: what observational structure can and cannot
tell you about intervention.

**Scope.** Three binary variables, all **25** labelled DAGs, every CPT from the
frozen rational grid `{0, 1/4, 1/2, 3/4, 1}` — **547,625** structural causal
models, enumerated, not sampled. Single-variable atomic interventions by
truncated factorisation. Integer numerators over `64` and `16`, and `Fraction`;
no float anywhere.

| result | numbers |
|---|---|
| `CI-1` non-identification | **11** Markov classes from 25 DAGs; **all 7** multi-DAG classes carry a witness; **80,788,144** cross-DAG disagreeing pairs over **26,601** shared joints of **99,033** distinct joints; the **4** singleton classes **are** identified and are reported with count `0` |
| `CI-2` the named class | `A → C` vs `C → A`: identical joint `(3/16, 1/16, 3/16, 1/16, 1/16, 3/16, 1/16, 3/16)`, exactly **1** reproducing parameterisation, `ACE_A_on_C` `1/2` vs `0`, `ACE_C_on_A` `0` vs `1/2` |
| `CI-3` when required | half-width `> tol`; verified at `31/64` (required), exactly `1/2` (**not**), `33/64` (not); **5,356** of **26,601** groups non-degenerate per query |
| `CI-4` what it is worth | worst-case value `1/2`; **84,980** specifications with value exactly `0`, one of them **named** |
| `CI-5` predictive vs causal state | `INCOMPARABLE` **1,458**, `PREDICTIVE_STRICTLY_REFINES` **486**, `EQUAL` **243**, `CAUSAL_STRICTLY_REFINES` **0 — proved, not unobserved**; **75,938** non-positive models excluded and reported |
| `CI-6` parents | **6** entries with citations, **3** `PARENT_SUFFICIENT`; the computational-mechanics `causal state` explicitly separated from the Pearlian one |

**The quantifier discipline.** The row says *does not generally identify*. It is
easy to close that by exhibiting one confounded pair and easy to over-close it
into *never identifies*. Both counts are here: 7 classes where identification
fails and 4 where it holds, and
`OBSERVATIONAL_DATA_NEVER_IDENTIFIES_CAUSAL_STRUCTURE` is a registered
forbidden promotion.

**A zero that is a theorem.** `CAUSAL_STRICTLY_REFINES = 0` comes with a
structural argument — the causal state separates only the context, so strict
refinement would force the predictive partition to be trivial, which forces the
causal one to be trivial too. It is proved at this scope, not merely unfound.

**Two routes.** Route A enumerates DAGs over directed-edge masks with an
acyclicity peel, decides equivalence by (skeleton, v-structures), and computes
interventions by **truncated factorisation** on integer numerators. Route B
enumerates DAGs over topological orders, decides equivalence by comparing full
**d-separation CI signatures**, and computes interventions by **parent
adjustment** applied to the observational joint in exact `Fraction`s. Neither
the DAG enumeration, the equivalence test nor the do-operator is shared; the
test asserts route B's whole import set is `{fractions, itertools, json, sys}`.

**Hostiles.** Five, each proved to move its quantity before it is proved
detected — including the exact error this section exists to prevent: reading
`P(A|do(C))` off `P(A|C)` in a world where `C` does not cause `A` (true `0`,
hostile `1/2`). One hostile was **initially not potent** (its model had no real
confounding) and that is recorded in the theorem note rather than quietly fixed.

**Null.** **0/729** false alarms on collider models whose Markov class is a
singleton, **20/20** recall on planted models whose `C → A` twin is verified to
exist rather than assumed. An earlier planted family gave `6/81` and was
discarded as not actually planted.

**Row not closed.** *Test whether causal structure changes selected morphology
relative to observational prediction alone* is Tier 2 and is already earned by
`gmi-833-ae-morphology-sweep-v1` `SWEEP-5`. This tranche neither re-closes it
nor depends on it.

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae13-causality-intervention-v1/ae13_causality_intervention_v1.py > /tmp/ae13.json
cmp /tmp/ae13.json research/gmi-833-ae-ae13-causality-intervention-v1/RESULT_V1.json
python3 -I -B  research/gmi-833-ae-ae13-causality-intervention-v1/independent_causal_oracle_v1.py
python3 -I -B  research/gmi-833-ae-ae13-causality-intervention-v1/test_ae13_causality_intervention_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae13-causality-intervention-v1/test_ae13_causality_intervention_v1.py -v
```
