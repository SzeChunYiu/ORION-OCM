# G4.2/G4.3 effective reusable horizon — exact parents

This capsule answers the G4 reusable-horizon question with exact parents and raw
cost vectors. It does not train a router and does not scalarize resources.

`H_eff` is the number of queries served from reusable state that has survived
since admission, before reset, drift, revocation, or capacity eviction.

## PR #154 disposition

PR [#154](https://github.com/SzeChunYiu/ORION-OCM/pull/154) on
`codex/residual-strategy-regime-20260908` at
`86a5ad1d0387d0ad0a7022d6385284229bc36f6e` already sweeps, on the 142-target
semantic-BFS vs inverse lifetime:

- horizon `1..142` (i.i.d. static arms);
- query order (eight frozen permutations);
- reset/restart intervals `1,2,4,8,16,32,64,142`;
- checkpoint/replay intervals `4,8,16,32,64,71`;
- raw phase coordinates and a Pareto band `H=4..8`;
- static exact strategies, analytic expected-cost threshold, finite DP oracle,
  and online switch/investment parents.

That branch is **not merged** into this tree. This capsule does **not** copy or
rerun those engines.

PR #154 does **not** independently sweep reuse density, drift as distinct from
full reset, or revision frequency. Those axes, plus the G4.3 parent list on a
tractable state space, are executed here.

In-tree donors reused by citation, not rewrite:

- `research/paid-decision-region-correction-v1/` — paid decision-region / early exit;
- `research/decision-core-successor-repair-v1/` — common-action / finite meta-DP;
- `research/metareasoning-parent-review-v1/` — parent-assumption review of PR154;
- `research/machine-epistemics-lifetime-v1/` — raw vector / no-scalarization contract.

## Toy

Finite noiseless cache with items `{0,1,2}`, `rent=3`, `build=8`, `hit=1`.
Buying constructs the reusable entry and answers the current query. Renting
answers without retention. Integer vectors on

```text
rent, build, hit, probe, act,
checkpoint_write, checkpoint_read, replay, invalidation
```

plus separately recorded `H_eff` and peak storage.

Exact parents:

- static always-rent / always-buy;
- known-suffix analytic threshold `remaining*(rent-hit) > build`;
- per-item deterministic ski-rental;
- capacity-2 LRU vs Belady;
- common-action / contained decision-region stopping with a budget-1 probe DP;
- known-sequence Pareto DP over cache subsets.

No ML. Unit-price analytic comparison is a named parent; published objects remain
the raw vectors and price half-spaces.

## Reproduction

```sh
python research/g4-horizon-exact-v1/horizon_exact.py
python research/g4-horizon-exact-v1/test_g4_horizon_exact.py
```

[Result](RESULT.md) · [machine-readable summary](SUMMARY.json)
