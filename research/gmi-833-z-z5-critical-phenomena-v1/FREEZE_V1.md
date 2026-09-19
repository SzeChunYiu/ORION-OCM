# GMI #833 Section Z / Z5 — critical phenomena and scaling, freeze v1

Source `main`: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

Committed **before** any executor, oracle, receipt, register or test in
`research/gmi-833-z-z5-critical-phenomena-v1/` exists. `git log` must show this
commit strictly preceding the first implementation commit of this package, and
the package workflow gates on exactly that ordering.

## Claim ceiling

```
GMI_833_Z5_EXACT_FIRST_ORDER_MORPHOLOGY_TRANSITION_ZERO_FINITE_SIZE_DRIFT_AND_THE_REFUTED_ALPHABET_INDEPENDENT_THRESHOLD_AT_REGISTERED_FINITE_SCOPE
```

## The exact rows this tranche may reconcile

Section Z lives in issue comment `5684819296`, subsection
`### Z5 — Critical phenomena and scaling`. The six rows are, verbatim:

1. `- [ ] Identify control parameters producing morphology phase transitions.`
2. `- [ ] Derive critical thresholds analytically where possible.`
3. `- [ ] Predict behavior near transitions before measurement.`
4. `- [ ] Test finite-size scaling.`
5. `- [ ] Test whether transition laws extrapolate across problem size and substrate.`
6. `- [ ] Preserve failed scaling predictions and update claim ceilings rather than refitting silently.`

**No neighboring row is earned here.** Nothing in Z1–Z4, Z6–Z18, nothing in the
issue body, nothing in any other comment.

## Registered universe and objective (pinned, not rebuilt)

As in `gmi-833-heldout-20-transitions-v1`: `|U| = 65552` architecture-name-free
binary mechanisms (`16` stateless output tables over `(mode, cur)`; `65536`
one-state-bit `(nxt, table)` pairs over `(state, mode, cur)`), scored over all
`2^L` input sequences of length `L` in both modes at timesteps `t = 1..L-1`, so
`N(L) = (L-1) * 2^L` scored moments per mode. The registered corpus value is
`L = 3`, `N = 16`.

```
J(u) = eta * ( (1-p) * e_now(u)/N + p * e_delay(u)/N ) + lambda * bits(u)
```

with `p, eta, lambda ∈ Q`, `eta > 0`, `0 <= p <= 1`. Registered worlds: the `60`
worlds of `gmi-833-heldout-20-transitions-v1`.

## Labelling convention for every prediction below

`[DERIVED-AT-FREEZE]` — the algebra was carried out by the author before this
freeze was written; the run *verifies* it and its value as evidence is
replication by two independent routes, not prospective surprise.

`[UNCOMPUTED]` — the author does not know the number at freeze time. No file in
this package existed when this freeze was committed, and no enumeration had been
run.

Mislabelling either way is the `POST_HOC_SUSPECT` defect this corpus has already
had to correct once. The labels are part of the frozen record.

## Row 1 — control parameters (frozen now)

- `CP-1a` `[DERIVED-AT-FREEZE]` The objective is homogeneous of degree `1` in
  `(eta, lambda)`, so the argmin — and hence the selected morphology — depends on
  the world only through the **two dimensionless controls**
  `p` (delay density) and `mu = lambda / eta` (price ratio). `eta` alone is not a
  control parameter.
- `CP-1b` The **order parameter** is `m(p, mu) = ` the state-bit count of the
  argmin, taking values in `{0, 1}` and `{0, 1}` jointly at a tie.
- `CP-1c` `[DERIVED-AT-FREEZE]` The transition is **first order** in the
  Ehrenfest sense: `m` jumps, while the minimum value `J*` is continuous.

## Row 2 — analytic threshold (frozen now)

- `CP-2a` `[DERIVED-AT-FREEZE]` **Every** stateless candidate has
  `e_delay = N/2` exactly, for every `L >= 2`. Reason: a stateless output depends
  on `cur` only, while the target is `prev`; over the scored moments, `prev` is
  uniform and independent of `cur`, so each of the two possible outputs is wrong
  in exactly half of the moments with that `cur` value. The stateless family is
  therefore *uniformly* half-wrong on delay — not merely half-wrong on average.
- `CP-2b` `[DERIVED-AT-FREEZE]` `e_now` over the stateless family takes exactly
  the values `{0, N/2, N}`.
- `CP-2c` `[DERIVED-AT-FREEZE]` The best stateless objective is
  `eta * p / 2`; the best one-state-bit objective is `lambda` (a machine storing
  the previous input attains `e_now = e_delay = 0`). Hence
  `J*(p, eta, lambda) = min(eta*p/2, lambda)` and the critical threshold is
  exactly `lambda* = eta*p/2`, i.e. `mu* = p/2`.
- `CP-2d` `[UNCOMPUTED]` the exact set of `(e_now, e_delay)` pairs attained by
  the `65536` one-state-bit candidates, and its cardinality. Reported, not
  predicted.

## Row 3 — behaviour near the transition, predicted before measurement (frozen now)

Registered *before* any scan; each is adjudicated by the exhaustive run.

- `CP-3a` `[DERIVED-AT-FREEZE]` `J*` is continuous at `lambda*` and piecewise
  linear in `lambda`, with a kink and no jump.
- `CP-3b` `[DERIVED-AT-FREEZE]` **Exact latent-quantity relation.** The jump in
  `dJ*/dlambda` across `lambda*` equals exactly the jump in the order parameter:
  `dJ*/dlambda = 1` for `lambda < lambda*`, `= 0` for `lambda > lambda*`, so the
  derivative jump is `1 = Delta m`. This is the finite exact analogue of a
  Clausius–Clapeyron relation and is the sharpest content of row 3.
- `CP-3c` `[DERIVED-AT-FREEZE]` At `lambda = lambda*` **exactly**, the argmin
  class set is exactly `{STATELESS, PERSISTENT_STATE}` — an exact tie in `Q`, not
  a numerical coincidence.
- `CP-3d` `[DERIVED-AT-FREEZE]` **Zero critical width.** For every world and
  every `L`, the set of `lambda` at which the class set is not a singleton is the
  single point `lambda*`. There is no rounded critical window at any finite size.
- `CP-3e` `[UNCOMPUTED]` the exact gap `J_stateless_best - J_stateful_best` at
  each of the `60` registered worlds, and the exact number of candidates attaining
  the minimum at each. Reported.

## Row 4 — finite-size scaling (frozen now)

Size ladder: sequence length `L ∈ {2, 3, 4, 5}` at fixed universe `U`
(`|U| = 65552` for every `L`; only the scoring interface grows).

- `CP-4a` `[DERIVED-AT-FREEZE]` `lambda*(L) = eta*p/2` for every `L >= 2`:
  **zero finite-size drift**, finite-size exponent `0`. Proof is `CP-2a`, which
  is `L`-uniform; verification is exhaustive re-enumeration at `L ∈ {2,3,4,5}`.
- `CP-4b` `[DERIVED-AT-FREEZE]` the transition stays sharp at every `L`
  (`CP-3d` holds at every rung), so there is no finite-size rounding exponent
  either.
- `CP-4c` `[UNCOMPUTED]` `N(L)`, the attained `(e_now, e_delay)` sets, and the
  number of distinct objective values at each rung. Reported.

## Row 5 — extrapolation across problem size and substrate (frozen now)

**Scoped reading of "substrate", registered here.** The corpus has no single
registered substrate notion for this universe. This package registers
*input/output alphabet size* `A` as its scoped reading of a substrate change:
the same task, the same accounting, a wider symbol alphabet and an `A`-ary
register in place of a bit. The forbidden promotion below makes explicit that
this does not cover physical substrates, compilers, or hardware.

**Resource accounting convention, registered here.** State cost is charged in
**registers** (one `A`-ary register costs `1`). The alternative convention — cost
in bits, `log2(A)` per register — is *excluded*, and for a stated reason rather
than for convenience: it makes the threshold irrational at `A = 3`, which the
exact-arithmetic rule of this programme forbids in a claim. The scaling law below
is therefore convention-dependent, and the convention is part of the claim.

Two rival hypotheses are registered now; the exhaustive enumeration adjudicates
between them.

- `S4-naive` — the registered law's literal extrapolation: `lambda*` is
  independent of `A`, i.e. `lambda*(A) = eta*p/2` for every `A >= 2`.
- `S4-derived` `[DERIVED-AT-FREEZE]` — this package's derivation:
  `lambda*(A) = eta * p * (1 - 1/A)`, which reduces to `eta*p/2` exactly at
  `A = 2`.

The derivation of `S4-derived` is two-sided and needs no enumeration of the large
`A`-ary stateful universe: (i) any `0`-register candidate has delay error at
least `(1 - 1/A) * N` because its output depends on `cur` only while `prev` is
uniform and independent of `cur`, with equality attained; (ii) any candidate with
at least one register costs at least `lambda`, and a `0`-error one-register
candidate exists. Hence `J* = min(eta*p*(1-1/A), lambda)`.

Side (i) is checked exhaustively over the full `A`-ary stateless family for
`A ∈ {2, 3, 4}` (`A^(2A)` tables: `16`, `729`, `65536`). Side (ii) is checked by
exhibiting the machine.

The two hypotheses disagree for every `A >= 3`. Whichever loses is recorded in
the failed-prediction register under row 6. The author's stated expectation is
that `S4-naive` loses; if instead the enumeration refutes `S4-derived`, that is
the published failure and the claim ceiling is rewritten accordingly.

- `CP-5c` `[UNCOMPUTED]` the exact minimum stateless delay-error fraction at
  `A = 3` and `A = 4`, by enumeration.

## Row 6 — preserving failed scaling predictions (frozen now)

`FAILED_SCALING_PREDICTION_REGISTER_V1.json` publishes every registered scaling
prediction with its adjudicated verdict — failures **and** successes side by side
— and, for each failure, the exact claim-ceiling text that is retired and the
text that replaces it. The register is machine-checked: each entry pins a
repository path, a git blob sha and a verbatim anchor string that must occur
exactly once in the pinned file. A missing file, a changed blob, or an anchor
count other than one fails the run.

Entries registered now, before any executor exists:

| id | prediction | adjudicator |
|---|---|---|
| `SP-1` | `CP-4a` zero finite-size drift in `L` | exhaustive re-enumeration at `L ∈ {2,3,4,5}` |
| `SP-2` | `CP-3d` zero critical width at every `L` | same |
| `SP-3` | `S4-naive`: `lambda*` independent of `A` | exhaustive `A`-ary stateless enumeration, `A ∈ {2,3,4}` |
| `SP-4` | `S4-derived`: `lambda*(A) = eta*p*(1 - 1/A)` | same |
| `SP-5` | `CP-3b` derivative jump equals `Delta m` | exact left/right difference quotients in `Q` at every registered world |

"Rather than refitting silently" is enforced mechanically: the register is a
committed receipt, the workflow re-derives it, and the claim ceiling string in
`MANIFEST_V1.json` must name the surviving hypothesis explicitly.

## Two materially independent routes

- **Route A** `z5_critical_phenomena_v1.py`: simulates every candidate over every
  input sequence at each `L`, scans the universe for the argmin, and computes the
  thresholds and derivative jumps from the scanned values.
- **Route B** `independent_scaling_oracle_v1.py`: never simulates a sequence. It
  computes `(e_now, e_delay)` from per-index occupancy counts derived
  combinatorially (how many scored moments carry each `(state-reachability,
  mode, cur, prev)` pattern), obtains the extremal values in closed form from the
  attained-value lattice, and re-derives every threshold, every finite-size
  number and every alphabet-ladder number from that construction. It imports
  nothing from route A and nothing from the Z3, Z7, Z12 or Z15 packages.

Agreement is required on every reported number.

## Null the true result must beat

`200` seeded randomized scaling laws `lambda*_rand(A) = eta * p * f(A)` with `f`
drawn from a rational ladder, excluding the true `f(A) = 1 - 1/A`. Each must be
**caught** by the adjudicating enumeration over the full ladder `A ∈ {2,3,4}`.

Target: `200/200` caught, `0/200` surviving.

The same `200` are additionally replayed against an **`A = 2`-only** adjudicator.
That restricted run is expected to be blind to a nonzero fraction of them — any
`f` with `f(2) = 1/2` survives — and the blind fraction is reported with its exact
characterization. The point is the prior lane's lesson made mechanical: a null
that is run against too narrow an instrument certifies nothing, and the exact
size of that blindness is published rather than asserted.

## Hostiles, each with the quantity it must move

| hostile | quantity | required movement |
|---|---|---|
| `H1_DOUBLE_BOUNDARY` | mismatch count between prediction and exhaustive argmin over the `40` endpoint worlds | must move from `0` to `> 0` |
| `H2_ALPHABET_BLIND` | claimed `lambda*(A)` at `A = 3` | must differ from the enumerated optimum |
| `H3_SCORER_OFFSET` | stateless `e_delay` | scoring `t = 0` as a delay moment must move `e_delay` off `N/2` for at least one table |
| `H4_TRUNCATED_UNIVERSE` | `J*` and the class set | dropping the stateful half must change the verdict on at least one world |
| `H5_SILENT_REFIT` | register integrity | a register entry whose pinned blob sha or anchor count is altered must fail the check |

A hostile that cannot move its quantity is a defect: the run fails.

## Forbidden promotions

`UNIVERSAL_CRITICAL_EXPONENTS`, `CONTINUOUS_PHASE_TRANSITION`,
`THERMODYNAMIC_LIMIT_ESTABLISHED`, `REAL_SUBSTRATE_SCALING`,
`PHYSICAL_SUBSTRATE_INVARIANCE`, `SCALING_LAW_HOLDS_FOR_ALL_ACCOUNTING`,
`ALPHABET_LADDER_COVERS_ARCHITECTURES`,
`LAMBDA_STAR_IS_ETA_P_OVER_TWO_IN_GENERAL`.

The last one is the point of row 6: after this package, `lambda* = eta*p/2` may
only be stated at `A = 2`.

## Falsifiers of this package itself

- Route A and route B disagreeing on any reported number.
- Any hostile that cannot move its named quantity.
- Any register entry whose pinned blob sha or anchor count does not check out.
- A randomized scaling law surviving the full-ladder adjudicator.
- The `A = 2`-only blindness fraction being reported without an exact
  characterization of which `f` survive.
