# Planning, goals and stopping — I4 (checklist item 11 / 602 I4)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (DU-1: what is
forced under the declared interface, not what neutral search reaches).
Date: 2026-09-14. Scope: finite deterministic task/world/action problems with
exact costs, plus a finite planning domain with costly simulation `tau`
(declared `1` per expansion). Exact Fractions, CPython 3.8 safe.

## Parent subtraction

- `GMI_GOAL_FORMATION_V1.md`, `GMI_SUBGOAL_DERIVATION_V1.md`,
  `GMI_PLANNING_STOPPING_RULE_V1.md` + `GMI_REPLANNING_UNDER_DRIFT_V1.md`
  (MIM, items 11) already give goal/subgoal/stop/replan at resource-rational
  scope. This unit does not duplicate their constructions.
- `METACOGNITION_THEOREM_V1.md` META-3 (this lane) gives `EVC` with the exact
  `13/35` myopic-optimality condition. This unit **composes** META-3 as the
  planning stop rule and registers the composition.

No new graphical-model principle is claimed beyond the parent
acquisition-value law.

## I4 checklist

- [x] goal formation (picking a reachable `Omega` whose `C(S)` becomes nonempty)
- [x] subgoal discovery (intermediate `S` with `0 < V(S) < V(W)` reusable across 2 tasks)
- [x] model-based simulation cost `tau` and the `EVC <= 0` stop rule (composing META-3)

## System

The planning world reuses the META-1..4 fixture (`n = 6` worlds `0..5`,
actions `{0,1,2}`, `Gamma6`, tests `t0` cost `1` / `t1` cost `2`, `TDA` value
`V(S)`). On top of it:

- **Planning state** `S` is a surviving candidate set (same as `S` in TDA-1).
- **Goals** `Omega_a = { w : a in Gamma6[w] }` for `a in {0,1,2}`. A goal is
  *formed* at `S` when `a` is the max-confidence action on `S` and `C(S)`
  may or may not yet contain `a`: the planner commits to the candidate
  `Omega_a` whose common-action attainment is the search target.
- **Simulation step** `tau = 1` per test expansion (the cheapest test `t0`);
  general test costs are `c(t0)=1, c(t1)=2` as in META-3. Expanding a node
  `S` by `t` pays `c(t)` and branches into `cells(S,t)`.
- **Stop rule** (META-3 composed): at `S` holding candidate action `a`,
  continue with `t` iff `EVC_worst(a,S,t) > 0`; otherwise stop and emit
  `argmax_a conf(a,S)`. Reconsider (switch `a`) iff some `a'` has
  `EC(a',S) < EC(a,S)`. This is exactly META-3 restated as a planning
  expansion rule.

## Witnesses (machine-checked)

All enumerations are over the `63` nonempty subsets of `W = {0..5}`
(`2^6 - 1`). `V(S)` is the TDA-1 optimal worst-case remaining test cost;
`EC` and `EVC` are unit-loss means as in META-2/3.

**Goal formation.** For every nonempty `S`, the max-confidence action
`a*(S)` is unique up to ties and `EC(a*(S),S)` is minimal. The formed goal
`Omega_{a*}` is the unique `Omega_a` of maximal `conf`. On singleton `S`,
`C(S) != empty` so the goal is already attained (`V(S)=0`, `EVC<=0` for
all `t`); on empty-`C(S)` sets the goal is *future*: `V(S)>0` and some
`EVC> -c(t)` may be positive. The witness `S={0,1,2,3,7-cap}` is shown
via the 8-world extension, but within the 6-world core `S={0,1}` already
has `C({0,1})={0,1}` (attained) while `S={2,5}` has `C={empty}` with
`a*=0 or 2` tied — the tie is listed, never silently broken.

**Subgoal discovery.** Call `S_sub` a *subgoal* for root `W` when

```
0 < V(S_sub) < V(W)   and   S_sub is a cell of some TDA-optimal expansion
```

Such `S_sub` is strictly closer to attainment than `W` but still needs
work, and is reusable across tasks when two distinct task roots `T1, T2`
share it as a cell. Machine-checked: `W = {0..5}` has `V(W)=2` (one
`t1` then at most one more test); `S={3,4}` has `V=1` (needs one test);
`S={2,5}` appears as a reusable subgoal for `W` and for `T2={2,3,4,5}`
(both have `V=2` and `V(S)=1`), and `S={3,4}` appears in `W`'s `t1`
cell `{4,5}` sibling chain. Exactly the `V`-strict-between condition
plus reuse threshold (appears in >=2 task cells) defines discovery,
not a heuristic threshold.

**Stopping (EVC <= 0).** For every `S` with `C(S)` nonempty, all
`EVC_worst(a,S,t) <= 0` for the common action `a in C(S)` (emitting beats
any costly expansion, matching TDA-1's `V=0`). For `S` with empty `C(S)`,
the max-`EVC` test coincides with a TDA minimiser in exactly `13` of the
`35` no-common-action subsets that have a splitting test — the `13/35`
greedy-optimality condition from META-3, restated as a planning
expansion-optimality condition. The pair `S={2,5}` (EVC-optimal `t0`)
and `S={3,5}` (TDA-optimal `t1` while EVC-myopic would pick `t0`) are
the agree/disagree witnesses.

## Claim ceiling

Finite deterministic `6`-world scope, exact costs, declared `Gamma6` and
test family, admissible planning search only. No claim that neutral search
reaches any goal/subgoal, that `EVC` is farsighted (it is myopic with the
`13/35` condition), or that drift/replanning beyond the registered `tau`
is covered (see MIM `REPLANNING_UNDER_DRIFT`). Falsifier: any `S` with
`C(S)` nonempty and `EVC>0` for its common action, or any `S` where the
`13/35` counts disagree with the checker (re-run `test_planning_stopping_v1.py`).

Files: [model](planning_stopping_v1.py) -> [controls](test_planning_stopping_v1.py) ->
[receipt](PLANNING_RECEIPT_V1.json: on billy-old py3.14 + laptop-billy py3.8,
normal + optimized).
