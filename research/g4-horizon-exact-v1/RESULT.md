# Exact reusable-horizon result

The toy is closed under exact parents. A learned router is not needed on this
state space. Mid-horizon rent vs buy is a price regime, not a feature-selection
residual. Common-action stopping saves the probe when every surviving hypothesis
already licenses `go`.

PR #154 remains the donor for the unmerged 142-target semantic-BFS lifetime.
This capsule fills the missing G4.2 axes and the G4.3 parent list on a finite
noiseless model. It does not speak for production OCM.

## Terminals

```text
EXACT_META_POLICY_SUFFICIENT
EXACT_EARLY_EXIT_VALUE_SUPPORTED
PRICE_REGIME_ONLY
LEARNED_ROUTER_NOT_NEEDED
PARENT_SUFFICIENT
CANNOT_CHECK_UNMERGED_PR154_SEMANTIC_LIFETIME
CANNOT_CHECK_PRODUCTION_OCM_LIFETIME
```

## G4.2 — `H_eff` sweeps

`H_eff` is useful reuse before invalidation/drift/revocation/reset.

**Horizon (constant item, always-buy).** `H_eff = H-1` for `H=1..8`. First query
pays `build=8`; later queries pay `hit=1` each.

**Horizon (same sequence, ski-rental).** Rent for two queries (`rent=6`), buy on
query 3 (`build=8`), then hits. `H_eff = max(H-3, 0)`. Worst summed-unit
competitive ratio against the clairvoyant analytic parent is `1.56 < 2`.

**Reuse density (H=6, unique `U=1,2,3`).** Always-buy `H_eff` is `5,4,3`
(`unused_queries = H-U`). Unique demand yields no hits.

**Query order.** Unlimited always-buy on the multiset `(0,0,1,1,2,2)` is
order-invariant (`H_eff=3`, one vector). Capacity-2 LRU is not:
`H_eff ∈ {0,1,2,3}`.

**Reset vs drift vs revision vs checkpoint** on `(0,1,2,0,1,2,0,1)`, always-buy
(stable `H_eff=5`, `build=24`, `hit=5`):

| kind | interval | `H_eff` | extra raw coordinates |
|---|---:|---:|---|
| reset | 1 | 0 | `build=64`, `invalidation=8` |
| reset | 4 | 2 | `build=48`, `hit=2`, `invalidation=6` |
| reset | 8 | 5 | `build=24`, `hit=5`, `invalidation=3` |
| drift | 1 | 0 | `build=64`, `invalidation=8` |
| drift | 2 | 2 | `build=48`, `hit=2`, `invalidation=4` |
| drift | 4 | 4 | `build=32`, `hit=4`, `invalidation=2` |
| revision | 1 | 3 | `build=40`, `hit=3`, `invalidation=3` |
| revision | 4 | 4 | `build=32`, `hit=4`, `invalidation=2` |
| checkpoint | 2 | 5 | `write=4`, `read=4`, `replay=11` |
| checkpoint | 4 | 5 | `write=2`, `read=2`, `replay=6` |
| checkpoint | 8 | 5 | `write=1`, `read=1`, `replay=3` |

Reset and drift both destroy reuse, but drift drops one survivor rather than the
whole cache, so `H_eff` decays more slowly at the same interval. Revision of item
`0` only is weaker still. Checkpoint/replay preserves `H_eff=5` and charges I/O
and reconstruction separately.

## G4.3 — exact parents

On the mixed sequence, always-rent `(rent=24)` and always-buy `(build=24, hit=5)`
are Pareto-incomparable. Unit-price witnesses: prefer rent if `build` is costly;
prefer buy if `rent` is costly. The known-suffix analytic parent rents (each item
has remaining `(rent-hit)` product `≤ build`). That vector lies on the exact DP
Pareto set (`15` undominated policies). Selector residual after the analytic
parent is therefore `0` in the dominance sense: leftover points are other prices,
not unpaid features.

On the constant sequence of length 8, analytic and DP buy immediately
`(build=8, hit=7, H_eff=7)`. Ski-rental pays the unknown-horizon tax
`(rent=6, build=8, hit=5, H_eff=5)`.

Capacity-2 Belady `H_eff=3` vs LRU `H_eff=0` on the 3-cycle: the cache-admission
parent is exact and material once capacity binds.

Common-action world: `Γ={go}`, STOP, vector `(probe=0, act=1)`. Identify-always
adds `probe=2`. Split world: `Γ=∅`, one noiseless probe then act
`(probe=2, act=1)`; budget-1 DP probes because STOP would pay `act=9`.

## Boxes

**G4.2 can be checked** (toy here; horizon/order/reset/checkpoint also cited from
unmerged PR #154): horizon, reuse density, query order, drift, reset/restart,
revision frequency, checkpoint/replay, raw cost vector.

**G4.3 can be checked** on the toy: static exact strategy, analytic threshold,
rent-vs-buy / ski-rental, cache-admission, common-action stopping, exact
decision-region containment, exact finite-state DP, cost-aware probe policy,
Pareto / price half-spaces.

**G4.4 stays closed.** Multiple Pareto strategies exist, but they are a price
regime. Exact parents leave no residual that would authorize #71.

## Limits

E2 toy calibration. Not a protected #143 run, not native proof, not production
routing, not a merge of PR #154. Analytic threshold uses the named integer rule
`remaining*(rent-hit)>build`; that is a parent, not a replacement for the raw
vectors. Summed-unit ski-rental ratios are diagnostics only.
