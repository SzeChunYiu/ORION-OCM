# GMI #833 AE15 — world-model necessity boundary: named results v1

Package `gmi-833-ae-ae15-world-model-necessity-v1`. Every quantity below is an
exact rational computed by two independent routes and recorded in
`RESULT_V1.json`. Claim ceiling:
`GMI_833_AE15_WORLD_MODEL_NECESSITY_BOUNDARY_DERIVED_ON_REGISTERED_FINITE_POMDP_ROSTER`.

The registered roster is three finite POMDPs and one four-member family, all at
`gamma = 1/2`, horizon `3`, `|S| <= 4`, `|O| <= 3`, `|A| <= 3`, with every
probability and reward an exact rational. Nothing here is asserted about
infinite, continuous or asymptotic problems.

## AE15-1 — `world model` is an interface, and the five interfaces are pairwise distinct

A *world model* is not a property of an architecture but of what a stored
object lets an agent do. Five interfaces are registered: `REACTIVE_POLICY`
(a map `O -> A`), `CACHED_SKILL` (a registered context to a fixed action
sequence, replay only), `VALUE_REPRESENTATION` (a map `O -> Fraction` used
greedily with the registered observation-level one-step lookahead, with no
access to `T` or `Z`), `PREDICTIVE_STATE` (a statistic of history sufficient
for future observations, with no reward semantics), and
`EXPLICIT_GENERATIVE_MODEL` (the tables `T` and `Z`, usable for counterfactual
rollout under a changed reward with no new data).

Seven coordinates are computed on the registered roster, none asserted as
prose: `c1_emits_an_action`, `c2_observation_closed_loop`,
`c3_time_or_history_varying`, `c4_predicts_future_observations_exactly`,
`c5_stores_reward_derived_rationals`, `c6_probe_reoptimizes`,
`c7_realizes_every_memoryless_action_map`. The five coordinate vectors are
pairwise different; of the 20 ordered pairs, 18 carry a coordinate on which the
first interface is strictly above the second and 2 are recorded as dominated
(`CACHED_SKILL` and `PREDICTIVE_STATE` against `EXPLICIT_GENERATIVE_MODEL`),
with the dominating direction named rather than a coordinate invented to fill
the cell.

The operational separator is the registered reward-swap probe: `R` is replaced
by `R_ALT` on `K_SWAP` and each stored object is re-queried with no further
interaction. `EXPLICIT_GENERATIVE_MODEL` alone re-optimizes, reaching `3/4`
under `R_ALT`; `REACTIVE_POLICY`, `CACHED_SKILL` and `VALUE_REPRESENTATION`
each fall to `0` against a class best of `3/4`, an exact shortfall of `3/4`.
`PREDICTIVE_STATE` returns no action at all and its stored object is
bit-identical under `R` and `R_ALT`, which is why it cannot signal the swap.

**Assumptions.** The registered interface definitions of `FREEZE_V1.md`; the
registered one-step lookahead uses only observation-level statistics
(`rhat`, `Phat`) derived from the uniform-action occupancy, never `T` or `Z`;
the registered tie-break is lexicographic by name, ascending.

**Dependencies.** `PROSPECTIVE_REGISTER_V1.json` (classes, tie-break,
reward-swap probe); `K_MODEL_NEEDED`, `K_SWAP`, `K_REACTIVE_OPT`; exhaustive
enumeration of each finite class; route B's independent recomputation.

**Falsifiers.** Two interfaces sharing a coordinate vector; any of the three
model-free interfaces re-optimizing under the probe; a probe shortfall other
than `3/4`; `PREDICTIVE_STATE`'s stored object changing under the reward swap;
an ordered pair with no separating coordinate in either direction.

**Strongest parents.** Astrom (1965), doi:10.1016/0022-247X(65)90154-X;
Smallwood and Sondik (1973), doi:10.1287/opre.21.5.1071; Kaelbling, Littman and
Cassandra (1998), doi:10.1016/S0004-3702(98)00023-X; Littman, Sutton and Singh
(2001), NIPS, and Singh, James and Rudary (2004), arXiv:1207.4167 for
predictive state; Sutton (1991), doi:10.1145/122344.122377 and Daw, Niv and
Dayan (2005), doi:10.1038/nn1560 for the model-based versus model-free contrast.
The taxonomy is theirs. What is added here is the exact finite instantiation
and the machine-checked coordinate table.

Scope: the registered roster only. Quantifiers: for all five registered
interfaces and all 20 ordered pairs. Forbidden extrapolation: this says nothing
about which interface any real system uses, and it does not license
`WORLD_MODEL_ALWAYS_REQUIRED` or `WORLD_MODEL_NEVER_REQUIRED`.

## AE15-2 — a registered task solved exactly optimally with no explicit model

On `K_REACTIVE_OPT`, a two-state fully observed MDP whose observation map is
the identity, the model-based optimum is exactly `3/4` and the best member of
`REACTIVE_POLICY` attains exactly `3/4`. The difference is exactly `0`.

The task is not myopically trivial: the greedy action at `s0` takes the
immediate reward `1/4` and yields only `7/16`, while the optimal action takes
`0` now to reach the rewarding state, so a genuine planning problem is solved
exactly by a memoryless map. Route B verifies this by enumerating all
`|A|^|O| = 4` reactive policies and taking the maximum, independently of route
A's belief recursion.

**Assumptions.** `gamma = 1/2`, horizon `3`, the registered initial state `s0`,
and rewards as frozen; the identity observation map.

**Dependencies.** `K_REACTIVE_OPT`; route A's belief-point backward recursion;
route B's alpha-vector enumeration and its exhaustive reactive enumeration.

**Falsifiers.** A non-zero difference; any reactive policy exceeding the
model-based optimum; disagreement between the two routes; the myopic value
differing from `7/16`.

**Strongest parents.** Bellman-optimality for fully observed finite-horizon
MDPs is standard and is not claimed here; the residual is the exact registered
instance and its two-route certification.

Scope: `K_REACTIVE_OPT` only. Quantifiers: for all four members of
`REACTIVE_POLICY` on this task. Forbidden extrapolation: one task on which a
model is unnecessary does not make models unnecessary in general.

## AE15-3 — a registered task where a model is necessary at the registered scope

`K_MODEL_NEEDED` is a four-state, three-observation, three-action POMDP in
which `s0` and `s1` emit the same observation `oa` while the optimal action at
them differs, and in which the transition out of `s0` is a fair coin whose
outcome is revealed only through the next observation. The model-based optimum
is exactly `1/2`. Exhaustive enumeration over each finite class gives a best
value of exactly `1/4` for `REACTIVE_POLICY` (all 27 maps), exactly `1/4` for
`CACHED_SKILL` (all 27 context-indexed action sequences) and exactly `1/4` for
`VALUE_REPRESENTATION`, so every member of all three is strictly suboptimal and
the gap is exactly `1/4`.

`Necessary` is claimed only at this registered scope and only because each
finite class was enumerated in full; no appeal to computational hardness is
made anywhere. The `VALUE_REPRESENTATION` figure is doubly grounded: the class
induces a memoryless map `O -> A` under any lookahead rule that does not track
history, so its best value is at most the memoryless best `1/4` whatever the
lookahead semantics; and the registered lookahead attains `1/4`, so the value
is pinned exactly. Independently, at `oc` all three actions share the same
`rhat` and `Phat` rows, so no value function can separate them and the
registered tie-break fixes the action there; the number of memoryless maps the
class can realize is therefore at most `6` of `27`.

**Assumptions.** The registered constants; deterministic emissions; the fair
coin out of `s0`; the registered context set for `CACHED_SKILL` is the initial
observation; the registered lookahead for `VALUE_REPRESENTATION`.

**Dependencies.** `K_MODEL_NEEDED`; enumeration of all 27 reactive maps, all 27
cached skills and the realizable greedy policies; route B's alpha-vector value
and trajectory-enumeration class values; bound `AE15-B2`.

**Falsifiers.** Any member of any of the three classes reaching `1/2`; a
model-based optimum other than `1/2`; a class best other than `1/4`; the two
routes disagreeing; the de-aliased variant still showing a positive gap.

**Strongest parents.** Singh, Jaakkola and Jordan (1994),
doi:10.1016/B978-1-55860-335-6.50042-8, own the result that memoryless policies
are strictly suboptimal under observation aliasing, and Littman (1994) owns the
companion analysis; no novelty is claimed against them. The residual is one
world at `|S| = 4`, `|O| = 3`, `|A| = 3`, `H = 3`, `gamma = 1/2` on which the
memoryless, open-loop cached and greedy-value interfaces are *simultaneously*
strictly suboptimal with exact rational values, each class closed by exhaustive
enumeration, together with the reward-swap probe that separates the explicit
generative model from a predictive state on the same roster.

Scope: `K_MODEL_NEEDED` at the registered constants. Quantifiers: for all
members of the three named finite classes. Forbidden extrapolation: this does
not license `WORLD_MODEL_ALWAYS_REQUIRED`, and AE15-2 is the counterexample on
the same roster.

## AE15-4 — the exact phase boundary between the model-based and model-free choice

`K_PHASE[G]` carries `G` goal tokens, each worth exactly `1`, collected on the
rewarding transition of `K_MODEL_NEEDED`. For `G` in `{1,2,3,4}` the
model-based value is `G/2`, the best model-free value is `G/4`, and the
boundary is the exact rational `c*(G) = G/4`, taking the values
`1/4, 1/2, 3/4, 1`. The boundary is strictly increasing over the registered
range. Because `D(c) = (V_mb(G) - c) - V_mf(G) = c*(G) - c` is exactly linear in
`c` with slope `-1`, the flip is strict on both sides: at `c*(G) - 1/8` the
margin is `+1/8` and the model-based class is chosen; at `c*(G) + 1/8` the
margin is `-1/8` and the model-free class is chosen; at `c*(G)` the margin is
exactly `0` and the registered lexicographic tie-break picks `CACHED_SKILL`.

The boundary is emitted as bound `AE15-B1` on the advantage per goal token,
`A(G)/G <= 1/4`, over the definitional range `[0, 7/4]`, attained at every
registered `G` and violated by the explicitly relaxed class `RELAXED_DISCOUNT`
(`gamma = 1` instead of the registered `1/2`), where the advantage per token is
`1/2`.

Disclosure: the registered family scales one token linearly, so `c*(G) = G/4`
is linear in `G` by construction. The registered range does not separate linear
from nonlinear growth of the boundary, and no growth law beyond `G <= 4` is
claimed.

**Assumptions.** The registered phase family and cost semantics
(`V_mb(G) - c` against `V_mf(G)`); the registered probe offset `1/8`, which is
smaller than `c*(1) = 1/4`; the registered tie-break.

**Dependencies.** `K_MODEL_NEEDED` and AE15-3; the class enumerations at every
`G`; route B's independent recomputation of `V_mb`, `V_mf` and the difference;
bound `AE15-B1`.

**Falsifiers.** A `c*(G)` differing from `G/4`; a non-monotone boundary over the
registered range; a non-strict flip on either side; a margin at `c*(G)` other
than `0`; the relaxed-discount witness failing to exceed `1/4`.

**Strongest parents.** The model-based versus model-free arbitration question
and its cost framing are owned by Sutton (1991),
doi:10.1145/122344.122377; Daw, Niv and Dayan (2005), doi:10.1038/nn1560; and
Keramati, Dezfouli and Piray (2011), doi:10.1371/journal.pcbi.1002055. The
residual is the closed-form exact rational threshold on a registered finite
family with the flip certified on both sides.

Scope: `G` in `{1,2,3,4}` on the registered family. Quantifiers: for all four
registered `G`. Forbidden extrapolation: the registered roster cannot support
`ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER`, and nothing here licenses
`MODEL_BASED_DOMINATES_MODEL_FREE` — above `c*(G)` the model-free class wins.

## AE15-5 — recovered latents may be predictive coordinates rather than world factors

`SCM_LATENT_A` has a two-valued latent `U` with `U -> X` and `U -> Y`.
`SCM_LATENT_B` has a four-valued latent `V` with `V -> X` and `X -> Y`. Every
observational and predictive quantity coincides exactly: the joint over `(X,Y)`
is `1/2` on `(x0,y0)` and `1/2` on `(x1,y1)` in both, both marginals are
uniform, and every conditional `P(Y|X)` and `P(X|Y)` is exactly `1` on the
matching value. The latent factorizations differ in both cardinality (`2`
against `4`) and graph, so a latent reproducing all observable and predictive
behaviour is not thereby a recoverable world factor. The two are separated only
by intervention: `P(Y = y1 | do(X = x1))` is exactly `1/2` in `SCM_LATENT_A` and
exactly `1` in `SCM_LATENT_B`.

`SCM_LATENT_ID` has a three-valued latent `L` with an injective emission, so
the recovery map `x0 -> l0, x1 -> l1, x2 -> l2` recovers `L` exactly. Recovery
is exact up to relabelling: all `6` permutations of the latent labels leave the
observable profile unchanged and are each recovered exactly by the
correspondingly renamed map.

The registered inverted hostile `H_LATENT_RELABEL` relabels `SCM_LATENT_B`. The
stored object changes, and the checker — which compares observable behaviour
only — stays silent, as it must: a pure renaming is not a difference. That
silence is asserted rather than assumed.

**Assumptions.** The three registered structural models with exact rational
latent distributions; interventions implemented by replacing the structural
equation for `X`; the checker compares observable behaviour only.

**Dependencies.** Route A's functional evaluation and route B's exhaustive
enumeration of the latent by `X` by `Y` product space; `H_LATENT_RELABEL`.

**Falsifiers.** Any observational or predictive quantity differing between the
pair; equal latent factorizations; equal interventional profiles; a permutation
of `SCM_LATENT_ID` that changes the observable profile or breaks recovery; the
checker flagging the pure relabelling.

**Strongest parents.** Non-identifiability of latent variables from
observational behaviour is owned by Hyvarinen and Pajunen (1999),
doi:10.1016/S0893-6080(98)00140-3; Locatello and colleagues (2019),
arXiv:1811.12359; and Khemakhem and colleagues (2020), arXiv:1907.04809. No
novelty is claimed against them. The residual is the exact rational pair with
identical predictive joints and an interventional separator, shipped alongside
an exactly recoverable case on the same roster.

Scope: the three registered structural models. Quantifiers: for all `6` label
permutations of `SCM_LATENT_ID` and for every observable and predictive
quantity of the pair. Forbidden extrapolation: this bounds what behaviour can
determine; it is not a claim about any particular learned representation.

## AE15-6 — the forbidden promotion, closed on machine-checked evidence

The registered forbidden promotion `LATENTS_ARE_HUMAN_INTERPRETABLE` — the
claim that successful intelligence necessarily reconstructs
human-interpretable latent variables — is refused, and AE15-5 is its
machine-checked evidence rather than its rhetorical support: two models with
different latent factorizations reproduce every observational and predictive
quantity exactly, so behavioural success does not pin the latent down even up
to cardinality, let alone to an interpretable one.

The executor scans every shipped artifact of this package and requires that
each occurrence of any registered forbidden promotion lies inside a
forbidden-promotion declaration — an element of a `forbidden_promotions` array
in JSON, or a block under a heading that names the refusal in prose. The scan
reports zero assertions. The scanner is validated in both directions: a line
that does assert the string with no declaration guard is caught, and a guarded
declaration is not.

**Assumptions.** The registered forbidden-promotion list of `FREEZE_V1.md`,
de-duplicated for the receipt without editing the freeze; the registered
definition of a declaration context.

**Dependencies.** AE15-5; the shipped artifact set; the scanner and its
two-direction validation in the test.

**Falsifiers.** Any shipped artifact asserting a forbidden promotion outside a
declaration context; the scanner failing to catch a planted assertion; the
scanner firing on a guarded declaration; AE15-5 being refuted.

**Strongest parents.** The interpretability critique is owned by the
identifiability literature cited in AE15-5; nothing is claimed novel here.

Scope: the artifacts of this package. Quantifiers: for all registered forbidden
promotions and all scanned artifacts. Forbidden extrapolation: refusing the
promotion is not the opposite claim that latents are never interpretable;
`SCM_LATENT_ID` is the registered case where one is recovered exactly.
