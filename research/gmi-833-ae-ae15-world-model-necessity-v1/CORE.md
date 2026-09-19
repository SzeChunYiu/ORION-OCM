# gmi-833-ae-ae15-world-model-necessity-v1

Section AE15 of issue #833 asks when an agent needs a world model. This package
answers it operationally on one registered roster of finite POMDPs, in exact
rational arithmetic, with two independent computational routes and every class
closed by exhaustive enumeration.

`World model` is defined as an interface, not an architecture class. Five
interfaces are registered and separated: `REACTIVE_POLICY`, `CACHED_SKILL`,
`VALUE_REPRESENTATION`, `PREDICTIVE_STATE` and `EXPLICIT_GENERATIVE_MODEL`.

| question | witness | the exact numbers |
|---|---|---|
| the five interfaces are distinct | 7 computed coordinates | all 5 vectors differ; 18 of 20 ordered pairs strictly separated, 2 recorded as dominated |
| what separates a model from the rest | reward-swap probe on `K_SWAP` | only `EXPLICIT_GENERATIVE_MODEL` re-optimizes, reaching `3/4`; the other three fall to `0` against a class best of `3/4` |
| a task needing no model | `K_REACTIVE_OPT` | optimum `3/4`, best reactive `3/4`, difference exactly `0`; the myopic reactive policy gets only `7/16` |
| a task needing a model | `K_MODEL_NEEDED` | optimum `1/2`; best of `REACTIVE_POLICY`, `CACHED_SKILL`, `VALUE_REPRESENTATION` all exactly `1/4`; gap exactly `1/4` |
| where the choice flips | `K_PHASE[G]`, `G` in `{1,2,3,4}` | `c*(G) = G/4`, so `1/4, 1/2, 3/4, 1`; margin `+1/8` below, `0` at, `-1/8` above |
| are latents world factors | `SCM_LATENT_A` vs `SCM_LATENT_B` | every observational and predictive joint identical; latent cardinality `2` against `4`; `P(Y=y1 \| do(X=x1))` is `1/2` against `1` |
| when a latent *is* recoverable | `SCM_LATENT_ID` | recovered exactly, invariant across all `6` label permutations |

**Row 3 is the load-bearing one.** On `K_MODEL_NEEDED` the observation `oa` is
emitted by both `s0` and `s1`, which need different actions, and the branch out
of `s0` is a fair coin revealed only through the next observation. All 27
reactive maps, all 27 context-indexed cached skills and every realizable greedy
value policy were enumerated; the best in each class is exactly `1/4` against a
model-based optimum of exactly `1/2`. `Necessary` is asserted only at this
registered scope and only by that enumeration — never by an appeal to hardness.
Singh, Jaakkola and Jordan (1994) own the underlying aliasing result; the
residual here is one world on which three model-free interfaces fail at once,
with exact values.

**Two routes.** Route A computes the optimum by a memoised backward recursion
over reachable belief points and class values by forward propagation of a state
distribution. Route B computes the optimum by Smallwood-Sondik alpha-vector
backward enumeration over the whole belief simplex with exact pointwise-
dominance pruning, and class values by enumerating every complete
state-observation trajectory with its exact path probability. Route B contains
no executable import of route A; the test parses route B with `ast` and asserts
it.

**Bounds.** Three, each with the full vacuity record and a `violated_by`
witness from an explicitly relaxed class: `A(G)/G <= 1/4` over `[0, 7/4]`,
broken at `1/2` when `gamma` is relaxed to `1`; model-free value on
`K_MODEL_NEEDED` `<= 1/4` over `[0, 7/4]`, broken at `1/2` by a policy allowed
one step of history; post-probe shortfall `>= 3/4` over `[0, 7/4]`, broken at
`0` when the probe is relaxed to permit a re-fit.

**Hostiles.** Five, potency asserted before detection. `H_MEMORY_LEAK` moves
the model-free best `1/4 -> 1/2` and is flagged. `H_ALIAS_BREAK` moves the gap
`1/4 -> 0` and is flagged. `H_HORIZON` moves the model-based optimum on
`K_MODEL_NEEDED` `1/2 -> 0` and on `K_REACTIVE_OPT` `3/4 -> 1/4`, and is
flagged. `H_COST_SHIFT` flips the chosen class at every registered `G` and is
flagged. `H_LATENT_RELABEL` is the register's inverted hostile: the stored
object changes, and the checker's silence is asserted.

**Null.** Detector: the model-based optimum strictly exceeds the best value any
of the three model-free interfaces attains. It fires on `K_MODEL_NEEDED`
(magnitude `1/4`) and does not fire on the known-clean `K_REACTIVE_OPT` or
`K_SWAP` (both exactly `0`). The registered sampler — a 64-bit generator seeded
from the register's own `self_digest_sha256` — fires on `90` of `200` random
POMDPs, largest magnitude `99/512`, so the witness strictly exceeds every null
magnitude with no threshold. A second, structure-matched control randomizes only
the observation map of `K_MODEL_NEEDED`: it does **not** beat the witness
(`86/200` positive, largest magnitude `1/4`, equal to the witness), because a
redrawn observation map often rebuilds an aliasing of equal strength. Reported
as mechanism attribution instead: of the 200 controls, every one of the `86`
positive gaps has an optimal-action conflict at a shared observation and the
largest gap without such a conflict is exactly `0`, so the conflict is
necessary; it is **not** sufficient (`63` controls have a conflict and a zero
gap), and that is stated rather than hidden.

Claim ceiling:
`GMI_833_AE15_WORLD_MODEL_NECESSITY_BOUNDARY_DERIVED_ON_REGISTERED_FINITE_POMDP_ROSTER`.
The registered forbidden promotions are listed in `MANIFEST_V1.json`; both
`WORLD_MODEL_ALWAYS_REQUIRED` and `WORLD_MODEL_NEVER_REQUIRED` are among them,
and AE15-2 and AE15-3 are the paired counterexamples that refuse each.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae15-world-model-necessity-v1/test_ae15_world_model_necessity_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae15-world-model-necessity-v1/test_ae15_world_model_necessity_v1.py -v
python3 -I -B research/gmi-833-ae-ae15-world-model-necessity-v1/ae15_world_model_necessity_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical in both modes
and on CPython 3.8 and 3.12.
