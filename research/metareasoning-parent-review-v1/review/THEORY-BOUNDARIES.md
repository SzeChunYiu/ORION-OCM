# Oracle scope and numerical repair

Frozen commit: `9087971dd3a9847149fa8cf844cb13e84a57cacd`. Source review only.

## What the implemented bound supports

For each single primary resource coordinate, the DP is the standard finite
Bellman optimum for:

- exactly two fixed donor actions: fresh inverse execution, or semantic query
  that advances the semantic frontier to `max(f,R(q))`;
- a cold initial frontier, a known finite remaining demand horizon, and no
  intervening reset, checkpoint, invalidation, or change to the donor engines;
- independent uniform draws, with replacement, from the frozen 142-target
  population;
- free knowledge of the current target's exact `R/I/K` and the build curve;
- additive costs on that primary coordinate, without selector overhead.

The code implements the relevant expectation as a uniform sum followed by
division by `n` and uses only `previous[h-1]` values
([regime_sweep.py 169–215](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/regime_sweep.py#L169)).
Subject to arithmetic certification and the donor reduction, both static
policies are in this action class; the oracle's cost cannot exceed their
minimum. Adding less information or nonnegative selector cost cannot improve
upon that oracle within the same state/action/demand model. Thus its reduction
from the best static cost is a valid selection-value upper bound **at that
coordinate and scope**.

This is not evidence about changed algorithms, an inverse answer cache,
partial/interleaved searches, other demand laws, additional lifecycle actions,
or total runtime. The separate lifecycle permutation sweep does not extend the
oracle to those regimes.

## “Foresight” and resource scope need precise language

The oracle knows the current target's costs and future demand distribution;
it does not know the future realized target sequence. Therefore the phrase
“even perfect free foresight” in [README 145–149](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/README.md#L145) is
broader than the implemented information model. “Free current-target cost
information under the registered i.i.d. demand model” describes it precisely.

The reported per-coordinate percentages are not automatically an 8% bound
under an arbitrary weighted resource sum: both the best static arm and the
optimal oracle policy can differ by coordinate. The document already asks for
price-region discipline; preserve that limitation when stating the conclusion.

By-hand scope example, **not donor data**: for two equally likely targets,
let inverse/semantic cost vectors be respectively
`(1,101)/(2,1)` on target A and `(1,2)/(101,1)` on target B.
In coordinate 1, always inverse is optimal; in coordinate 2, always semantic
is optimal; per-coordinate selection gain is zero.
For equal coordinate weights, either static policy costs 52.5 per demand,
whereas choosing semantic on A and inverse on B costs 3. Coordinatewise
percentages therefore cannot bound that weighted percentage without a new
calculation. This does not assert such a pattern occurs in the frozen study.

## Cold feature regret is a relaxation, not full feature-policy evaluation

The prospective audit limits the first cold decision to one action per feature
bucket, then assigns both actions the **full-information oracle continuation**
([prospective_selector.py 133–149](https://github.com/SzeChunYiu/ORION-OCM/blob/9087971dd3a9847149fa8cf844cb13e84a57cacd/research/residual-strategy-regime-v1/prospective_selector.py#L133)).
Its bucket minimum is exact in that relaxed cold-entry problem if the action
values are exact. It is a lower bound on regret for a policy that must use the
same limited features on future decisions too, not the cost of such a complete
policy. The module's cold-frontier/nondeployable scope is appropriate.

A more explicit output name, such as
`best_cold_action_with_oracle_continuation_expected_cost`, would prevent a
consumer from mistaking the current field for an achievable lifelong policy.

## Exact numerical repair

This specification is algebra only; no implementation or study was executed.

Uniform integer costs admit scaled-integer DP. Write
`V_h(f)=S_h(f)/N^h`, with `S_0(f)=0`.
At horizon `h`, compare the two integer action numerators:

```text
A = I(q) * N^(h-1) + S_(h-1)(f)
B = [B(max(f,R(q))) - B(f) + K(q)] * N^(h-1)
    + S_(h-1)(max(f,R(q)))
S_h(f) = sum_q min(A,B)
```

The action denominators are shared, so comparison and equality are exact.
The cold feature bucket's integer regret numerator is
`min(sum A, sum B) - sum min(A,B)`; summing buckets and dividing by `N^h`
gives exact expected cold regret.

The static semantic expected-cost numerator on denominator `N^h` is
`sum_j [j^h-(j-1)^h] B(R_j) + h*N^(h-1)*sum_q K(q)`.
The inverse numerator is `h*N^(h-1)*sum_q I(q)`.
Hence phase crossings and the 8% comparison can be certified by integer
cross-multiplication; convert to decimal only for presentation.

Any later certification must use the frozen real source/data, preserve the
unresolved-versus-certified distinction, and bind its receipt to this commit.
No frozen numerical result has been independently certified in this review.
