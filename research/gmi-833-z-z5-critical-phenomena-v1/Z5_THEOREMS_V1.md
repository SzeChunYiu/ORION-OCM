# Z5 named results — critical phenomena and scaling of the finite morphology transition

Scope for every result below: the registered finite universe `U` of
`65552` architecture-name-free binary mechanisms (`16` stateless output tables
over the index `(mode, cur)`; `65536` one-state-bit `(nxt, table)` pairs over
`(state, mode, cur)`), scored over all `2^L` input words of length `L` in both
modes at timesteps `t = 1..L-1`, with

```
J(u) = eta * ( (1-p) * e_now(u)/N + p * e_delay(u)/N ) + lambda * bits(u),
N = (L-1) * 2^L,   p, eta, lambda in Q,  eta > 0,  0 <= p <= 1.
```

Nothing below is claimed outside this scope. Every number is exact rational
arithmetic; no float appears in any statement.

---

## `CP-1` — the transition has exactly two control parameters

**Statement.** `J` is homogeneous of degree `1` in `(eta, lambda)`. Consequently
the argmin set, and therefore the selected morphology, depends on the world only
through the dimensionless pair `(p, mu)` with `mu = lambda/eta`. `eta` alone is
not a control parameter.

**Quantifiers.** For all `p, eta, lambda in Q` with `eta > 0`, and all `c in Q`
with `c > 0`.

**Evidence.** `0` homogeneity violations over `60` registered worlds x a
`6`-rung rational scale ladder; `15` distinct `(p, mu)` keys among the `60`
worlds with `0` determinism violations.

**Assumptions.** The state cost enters linearly and additively.

**Falsifier.** Any world pair with equal `(p, mu)` and different winner class
sets.

**Strongest parents.** Dimensional analysis of a linear cost; the
`gmi-833-morphology-selection-v1` cost model. Not novel.

**Forbidden extrapolation.** Nothing is claimed about nonlinear or
non-additive resource accounting.

---

## `CP-2` — the stateless family is *uniformly* half-wrong on delay

**Statement.** For every `L >= 2`, every stateless candidate has
`e_delay = N/2` exactly — not on average, but individually. `e_now` over the
same family takes exactly the three values `{0, N/2, N}`. Hence the best
stateless objective is `eta*p/2`, the best one-state-bit objective is `lambda`,
`J* = min(eta*p/2, lambda)` and the critical threshold is exactly
`lambda* = eta*p/2`, i.e. `mu* = p/2`.

**Quantifiers.** For all stateless `u`, all `L >= 2`, all `p, eta`.

**Evidence.** At `L = 3`, attained stateless pairs are exactly
`{(0,8), (8,8), (16,8)}`; the analytic threshold equals the exact crossing of
the two class-restricted minima at all `60` worlds with `0` mismatches; both
routes agree.

**Assumptions.** Input words are drawn from the full product set, so `prev` is
uniform and independent of `cur` at every scored moment.

**Falsifier.** One stateless table with `e_delay != N/2`.

**Strongest parents.** The `lambda* = eta*p/2` boundary law is already frozen on
`main` by `gmi-833-morphology-selection-v1` and validated prospectively by
`gmi-833-heldout-20-transitions-v1`. This package does not claim it. The
residual here is the *uniformity* statement — that the whole stateless family,
not merely its optimum, sits at `N/2` — which is what makes the threshold
derivation a two-line counting argument instead of an enumeration.

**Forbidden extrapolation.** Nothing about non-uniform input distributions.

---

## `CP-3` — the transition is first order with an exact latent-quantity relation

**Statement.** `J*` is continuous and piecewise linear in `lambda` with a kink at
`lambda*`. The order parameter `m` (state bits of the argmin) jumps from `1` to
`0`. The left and right derivatives of `J*` in `lambda` are `1` and `0`, so

```
[ dJ*/dlambda ]_- - [ dJ*/dlambda ]_+  =  1  =  Delta m,
```

the exact finite analogue of a Clausius–Clapeyron relation. At `lambda = lambda*`
exactly, the argmin class set is exactly `{STATELESS, PERSISTENT_STATE}`: an
exact tie in `Q`. The critical window has width exactly `0`.

**Quantifiers.** All `60` registered worlds, three probe offsets
`10^-3, 10^-6, 10^-9`.

**Evidence.** Derivative jump value set `= {1}`; `0` tie violations over the
`20` boundary worlds; `0` critical-width violations; `0` closed-form value
mismatches; both routes agree.

**Assumptions.** Exact rational arithmetic. With floats the tie is not
observable, which is why the programme forbids them.

**Falsifier.** Any derivative jump other than `1`; any non-singleton class set
away from `lambda*`; any singleton class set at `lambda*`.

**Strongest parents.** Ehrenfest's classification of phase transitions; the
Clausius–Clapeyron relation. The analogy is *structural*, not physical: there is
no thermodynamic limit here and none is claimed.

**Forbidden extrapolation.** `CONTINUOUS_PHASE_TRANSITION`,
`UNIVERSAL_CRITICAL_EXPONENTS`, `THERMODYNAMIC_LIMIT_ESTABLISHED`.

---

## `CP-4` — zero finite-size drift

**Statement.** `lambda*(L) = eta*p/2` for every `L >= 2`. The finite-size drift
of the critical point is identically zero, and the transition is sharp at every
rung: there is no finite-size rounding either.

**Quantifiers.** Proved for all `L >= 2` by `CP-2`, which is `L`-uniform;
verified exhaustively over the full `65552`-candidate universe at
`L in {2,3,4,5}`.

**Evidence.** `0` drift violations at every rung; stateless delay values
`{2}, {8}, {24}, {64}` against `N/2 = 2, 8, 24, 64`; distinct `sigma` classes
`28, 146, 440, 444`; both routes agree.

**Assumptions.** The candidate universe is held fixed as `L` grows; only the
scoring interface grows.

**Falsifier.** Any rung with a shifted threshold or a non-singleton class set
away from `lambda*`.

**Forbidden extrapolation.** Growing the state budget is a different ladder and
is not covered.

---

## `CP-5` — the registered threshold does **not** extrapolate across alphabet size

**Statement.** With symbol alphabet `A` and state cost charged in **registers**,

```
lambda*(A) = eta * p * (1 - 1/A),
```

which equals `eta*p/2` only at `A = 2`. The naive extrapolation of the
registered law — `lambda*` independent of `A` — is **false** for every `A >= 3`.

**Quantifiers.** Proved for all `A >= 2` by a two-sided argument: any
`0`-register candidate has delay error at least `(1-1/A)*N` (counting argument,
with equality attained), and any candidate with at least one register costs at
least `lambda`, with a `0`-error one-register witness exhibited. Verified
exhaustively over the full `A`-ary stateless family for `A in {2,3,4}`
(`16`, `729`, `65536` tables).

**Evidence.** Enumerated minimum stateless delay fractions
`1/2, 2/3, 3/4` against the derived `(A-1)/A`; the one-register witness scores
`(0, 0)` at every `A`; the product form is licensed only because the delay
fraction is *constant* across the stateless family and `e_now = 0` is attainable,
and both conditions are checked rather than assumed.

**Assumptions.** State cost in registers. The bits convention
(`log2 A` per register) is excluded because it makes the threshold irrational at
`A = 3`, which the programme's exact-arithmetic rule forbids in a claim. The
scaling law is therefore convention-dependent, and the convention is part of the
claim.

**Falsifier.** An `A`-ary stateless table with delay error below `(1-1/A)*N`;
or a `0`-register candidate matching the one-register witness.

**Strongest parents.** The chance rate of predicting a uniform symbol from an
independent one is standard information theory; nothing there is claimed novel.
The residual is the *statement about this programme's own threshold*: that the
registered `eta*p/2` was an `A = 2` special case all along.

**Forbidden extrapolation.** `REAL_SUBSTRATE_SCALING`,
`PHYSICAL_SUBSTRATE_INVARIANCE`, `ALPHABET_LADDER_COVERS_ARCHITECTURES`. Alphabet
size is this package's *registered scoped reading* of a substrate change; it is
not a compiler, a device, or a physical medium.

---

## `CP-6` — the failure is published, not refitted

**Statement.** `FAILED_SCALING_PREDICTION_REGISTER_V1.json` carries every
registered scaling prediction with its adjudicated verdict — one refutation
(`SP-3`, the alphabet-independent threshold) alongside four confirmations and one
parent negative control — and, for the refutation, the exact claim-ceiling text
retired and the text that replaces it. Each entry pins a repository path, a git
blob sha and a verbatim anchor that must occur exactly once in the pinned file.

**Falsifier.** A register entry whose pin or anchor count does not check out; a
refuted prediction absent from the register; a claim ceiling that still states
`lambda* = eta*p/2` without the `A = 2` qualifier.

**Consequence adopted here.** The forbidden promotion
`LAMBDA_STAR_IS_ETA_P_OVER_TWO_IN_GENERAL` is added to this package and to every
downstream statement of the boundary law.
