# gmi-833-ae-ae1-structure-separation-v1

Section AE1 of issue #833 asks for `exploitable structure` to be defined without
handwaving and separated from five things it is routinely confused with. This
package does that on one consistent finite roster, in exact rational
arithmetic, with two independent computational routes.

| separation | witness | the exact numbers |
|---|---|---|
| nonuniform marginal is not dependence | `W_IND_SKEW` | marginal `(3/4, 1/4)`, L1 dependence exactly `0` |
| dependence is not predictive dependence | `W_DEP_NOPRED` | L1 dependence `1/5`, Bayes gain exactly `0` (`acc_obs = acc_base = 4/5`) |
| prediction is not control relevance | `W_PRED_NOCTRL` / `W_CTRL_NOPRED` | gain `1/2` with control gain `0` under a non-constant utility; gain `0` with control gain `1/4` |
| prediction is not causation | confounded `Z -> X`, `Z -> Y` | observational gain `3/20`, interventional gain exactly `0` |
| existence is not accessibility | `W_PARITY3` | full-information accuracy `1`, base `1/2`, yet exactly `1/2` at `(k,d)=(2,2)` **and** at `(3,2)` |
| finite-sample is not asymptotic | 8-secret parity family | expected accuracy `9/16`, `79/128`, `723/1024`, `6715/8192` at `m = 0,1,2,3`; asymptotic `1` |

`PRED` does strictly imply `DEP`: over all 16 shapes of the frozen
denominator-8 grid, **no** shape admits a predictive world that is
independent.

**Row 7 is closed on both disjuncts.** No *budget-independent* scalar can
determine available structure: `W_PARITY3` scores `1/2` against
`W_NOISY_DICT`'s `3/4` at budget `k1_d1` and `1` against `3/4` at `k3_d3`, an
order reversal. Three named candidates are refuted individually
(full-information gain `1/2` vs `1/4`, L1 dependence `1` vs `1/2`, chi-squared
`1` vs `1/4`). The positive disjunct is the budget-indexed profile object
`S(W) : R -> max_{h in H_R} acc(h, W)`, monotone with 0 violations over the
16-cell lattice and bounded by the full-information optimum with 0 violations.

**Two routes.** Route A computes accuracies from the argmax identity, class
membership from essential arity plus a memoised decision-tree-depth recursion,
and the learning curve from a span/rank argument. Route B enumerates every
deterministic rule, decides independence by the rank-1 minor test, builds every
decision tree bottom-up by explicit composition, and enumerates every
`(secret, training tuple, test point)`. Route B has no executable import of
route A; the test asserts this by parsing route B's AST. The two agree on every
value, including the entire 16-shape realizability map.

**Minimality (row 8).** Every separation in rows 2-6 carries a two-sided
certificate — a witness at the claimed minimum, and none strictly below — with
route B verifying both sides independently. Distributional: 16 shapes to `4x4`
on the denominator-8 grid. Control: shapes to `(3,3,2)`, denominator-6 joints,
every 0/1 utility, **45,748** cases, minimal `(2,2,2)` and `(2,3,2)`, both
matching the shipped witnesses. Causal: minimal `(2,2,2)`, matching. For
accessibility and finite-sample the sweep reports **against** the shipped
witnesses: two coordinates already suffice for the plain accessibility gap and
one for the zero-sample gap, so `W_PARITY3` and the 3-coordinate family are
declared non-minimal in the receipt. `W_PARITY3` is minimal for the strictly
stronger pattern where every coordinate is reachable within the depth budget
and the rule is still at the base rate — the property AE1-5 actually uses.

**Null.** Detector: full-information gain positive while every rule at junta
arity `k <= 2` attains exactly the base rate. It fires on the planted positive
(`W_PARITY3`, gap `1/2`), does **not** fire on the known-clean `W_DICT` or
`W_NOISY_DICT`, and fires on `7` of `200` random worlds — all seven genuine but
tiny gaps (largest `3/16`), listed individually in the receipt. The primary
comparison is threshold-free: the witness's `1/2` strictly exceeds the largest
null magnitude `3/16`. A `1/4` threshold, at which `0` of `200` fire, is
reported as illustration only — it was chosen after the magnitudes were seen.

Claim ceiling:
`GMI_833_AE1_TASK_RELATIVE_EXPLOITABLE_STRUCTURE_SEPARATED_ON_REGISTERED_FINITE_WITNESS_ROSTER`.
Minimality is claimed only over the frozen grids listed above and under the
stated product orders. The budget lattice is the frozen `(junta arity, tree depth)` pair;
memory, precision, communication, time and energy budgets are **not**
instantiated here.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae1-structure-separation-v1/test_ae1_structure_separation_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae1-structure-separation-v1/test_ae1_structure_separation_v1.py -v
python3 -I -B research/gmi-833-ae-ae1-structure-separation-v1/ae1_structure_separation_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical in both modes.
