# GMI #833 Section Z / Z7 — prospective impossibility and failure prediction, freeze v1

Source `main`: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

Committed **before** any executor, oracle, receipt, register or test in
`research/gmi-833-z-z7-impossibility-v1/` exists. `git log` must show this commit
strictly preceding the first implementation commit of this package, and the
package workflow gates on exactly that ordering. Every hypothesis and every
ceiling below is registered **before** the enumeration that adjudicates it; the
whole point of Z7 is that the prediction precedes the evaluation.

## Claim ceiling

```
GMI_833_Z7_EXACT_RESOURCE_DEPENDENT_IMPOSSIBILITY_REGIONS_AND_PROSPECTIVELY_FROZEN_CAPABILITY_CEILINGS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## The exact rows this tranche may reconcile

Section Z lives in issue comment `5684819296`, subsection
`### Z7 — Prospective impossibility and failure prediction`. The six rows are,
verbatim:

1. `- [ ] Require GMI to predict not only winners but tasks/capabilities that cannot be achieved under specified constraints.`
2. `- [ ] Derive resource-dependent impossibility regions.`
3. `- [ ] Freeze qualitative failure-mode predictions.`
4. `- [ ] Freeze quantitative capability ceilings before evaluation.`
5. `- [ ] Test broad candidate families against those predictions.`
6. `- [ ] Record any counterexample as a theorem/assumption failure requiring recursive repair.`

**No neighboring row is earned here.** Nothing in Z1–Z6, Z8–Z18, nothing in the
issue body, nothing in any other comment.

## Registered universe, task and accounting (pinned, not rebuilt)

As in `gmi-833-heldout-20-transitions-v1`: `|U| = 65552` architecture-name-free
binary mechanisms — `16` stateless output tables over the index `(mode, cur)`,
and `65536` one-state-bit `(nxt, table)` pairs over the index
`(state, mode, cur)`. Scored over all `8` input sequences of length `3`, both
modes, at timesteps `t = 1, 2`: `N = 16` scored moments per mode. `e_now(u)` and
`e_delay(u)` are the exact integer error counts in `mode 0` (copy current input)
and `mode 1` (emit previous input). `bits(u) ∈ {0, 1}` is the declared state-bit
count.

```
J(u) = eta * ( (1-p) * e_now(u)/16 + p * e_delay(u)/16 ) + lambda * bits(u)
```

`p, eta, lambda ∈ Q`, `eta > 0`. Registered worlds: the `60` worlds of
`gmi-833-heldout-20-transitions-v1`.

## Labelling convention

`[DERIVED-AT-FREEZE]` — the author derived it algebraically before writing this
freeze; the run replicates it by two independent routes.
`[UNCOMPUTED]` — the author does not know it at freeze time; no file of this
package existed and no enumeration had been run when this freeze was committed.
`[NAIVE]` — a hypothesis the author expects to be **refuted**, registered
deliberately so that row 6 has a real counterexample to record rather than a
manufactured one.

## Row 1 — a capability that cannot be achieved under stated constraints

- `IM-1a` `[DERIVED-AT-FREEZE]` **Prospective impossibility.** Under the
  constraint `bits = 0`, zero-error delayed recall is impossible. Stronger: every
  one of the `16` stateless candidates has `e_delay` exactly `N/2 = 8` — the
  failure is not merely nonzero, it is the same for the entire family. Delayed
  recall at `bits = 0` is therefore capped at accuracy exactly `1/2`, which is the
  chance rate.
- `IM-1b` `[DERIVED-AT-FREEZE]` The impossibility is **resource-dependent, not
  task-dependent**: the identical task is achieved with `0` errors at `bits = 1`.
  A GMI impossibility statement is only meaningful relative to a declared
  resource budget.
- `IM-1c` `[DERIVED-AT-FREEZE]` General-alphabet form: with symbol alphabet `A`,
  `e_delay >= (1 - 1/A) * N` for every `0`-register candidate.

## Row 2 — resource-dependent impossibility regions (frozen definitions)

Two regions are computed exactly.

**Region R1 — the attainability lattice.** For each budget `b ∈ {0, 1}`, the
exact set `S_b ⊆ {0..16}^2` of `(e_now, e_delay)` pairs attained by some
candidate with `bits = b`. The impossibility region at budget `b` is exactly the
complement `{0..16}^2 \ S_b`, of size `289 - |S_b|`.

- `[DERIVED-AT-FREEZE]` `S_0 = {(0,8), (8,8), (16,8)}`, so `|S_0| = 3` and the
  `bits = 0` impossibility region has exactly `286` cells.
- `[UNCOMPUTED]` `S_1` and `|S_1|`, and the Pareto-minimal frontier of `S_1`
  under componentwise `<=`.

**Region R2 — the infeasible cells of the finite cost grid.** A cell is the tuple
`(p, eta, lambda, a_now, a_delay, C, b)` over the registered grid

```
p      ∈ {1/5, 2/5, 1/2, 3/5, 4/5}
eta    ∈ {1, 2, 3}
lambda ∈ {1/20, 1/10, 1/5, 1/2}
a_now  ∈ {0, 4, 8, 16}
a_delay∈ {0, 4, 8, 16}
C      ∈ {1/10, 1/5, 1/2, 1}
b      ∈ {0, 1}
```

`19200` cells. A cell is **feasible** iff some candidate with `bits <= b`
satisfies `e_now <= a_now`, `e_delay <= a_delay` and `J <= C`; otherwise it is
**infeasible**, and the infeasible set is the resource-dependent impossibility
region. `[UNCOMPUTED]` the exact infeasible count, its split by `b`, and the exact
set of `(a_now, a_delay)` targets that are infeasible at every `(p, eta, lambda,
C)` in the grid.

## Row 3 — qualitative failure-mode predictions, frozen now

| id | prediction | label |
|---|---|---|
| `Q1` | At `bits = 0` the delay channel fails on exactly half the scored moments, identically for every member of the family — a *uniform*, not a *variable*, failure mode. | `[DERIVED-AT-FREEZE]` |
| `Q2` | At `bits = 0` the copy channel failure is *not* uniform: `e_now` takes exactly the three values `{0, 8, 16}`. | `[DERIVED-AT-FREEZE]` |
| `Q3` | The modal failure profile of a one-state-bit mechanism — the most frequent `(e_now, e_delay)` pair among the `65536` — is `(8, 8)`: a mechanism drawn without selection is half-wrong on both channels. | `[UNCOMPUTED]` |
| `Q4` | **Scarcity hypothesis.** One bit of state is a scarce resource that must be *shared* between the two channels, so no one-state-bit mechanism attains `e_delay = 0` while `e_now = 16`: perfect delay cannot be bought by sacrificing copy entirely. | `[NAIVE]` |
| `Q5` | Some one-state-bit mechanism is strictly worse on the delay channel than every stateless mechanism, i.e. attains `e_delay > 8`: adding state can make the delay channel worse, not merely fail to help. | `[UNCOMPUTED]` |

## Row 4 — quantitative capability ceilings, frozen before evaluation

Each ceiling is a statement of the form *no candidate in the named family beats
this bound*. Each must be shown **valid** (no violation on the exhaustive scan)
and **tight** (attained by an exhibited witness). A ceiling that is valid but not
tight tests nothing and is reported as slack, not as a result.

| id | family | ceiling | label |
|---|---|---|---|
| `C1` | `bits = 0` | `e_delay >= 8` | `[DERIVED-AT-FREEZE]` |
| `C2` | `bits = 0` | weighted risk `(1-p)*e_now/16 + p*e_delay/16 >= p/2` for every `p` | `[DERIVED-AT-FREEZE]` |
| `C3` | `bits <= 1` | weighted risk `>= 0`, attained | `[DERIVED-AT-FREEZE]` |
| `C4` | `bits = 1` | `max_u min(e_now(u), e_delay(u)) <= K4` for the exact integer `K4` | `[UNCOMPUTED]` — `K4` is reported, then frozen as the ceiling |
| `C5` | `bits = 1` | `|S_1| = K5` distinct attained error pairs | `[UNCOMPUTED]` |
| `C6` | whole universe | `min_u J(u) = min(eta*p/2, lambda)` at every registered world | `[DERIVED-AT-FREEZE]` |

`C4` and `C5` are ceilings whose *value* is measured and whose *form* is frozen
now. The distinction is stated explicitly so that no reader mistakes a measured
constant for a predicted one.

## Row 5 — broad candidate families tested against the predictions

Every prediction above is tested against the **entire** universe `U` (all
`65552`), and additionally against six named families, each defined
structurally and enumerated exactly:

| family | definition |
|---|---|
| `F_STATELESS` | the `16` declared-stateless candidates |
| `F_DEAD_TABLE` | one-state-bit candidates whose output table ignores the state bit (`16 * 256 = 4096`) |
| `F_FROZEN_STATE` | one-state-bit candidates whose `nxt` is constant |
| `F_MOORE` | one-state-bit candidates whose output depends on the state and the mode but not on `cur` |
| `F_MEALY_PURE` | one-state-bit candidates whose output depends on `cur` and the state |
| `F_IDENTITY_STATE` | one-state-bit candidates whose `nxt` returns `cur` (the natural "store the previous input" family) |

`[UNCOMPUTED]` every family size except `F_STATELESS` and `F_DEAD_TABLE`, and
every family's attained error set. "Broad" is discharged by exhaustiveness over
`U`, not by sampling.

## Row 6 — counterexample register and recursive repair

`COUNTEREXAMPLE_REGISTER_V1.json` records, for every refuted hypothesis:

- the hypothesis id and its verbatim frozen text,
- the explicit witness candidate (surface id, `nxt`, `table`, `e_now`, `e_delay`),
- the **assumption** that failed, stated as a sentence,
- the **repair**: the corrected statement that replaces it,
- and the claim-ceiling consequence.

The register is machine-checked: every witness is re-verified independently by
route B, and a register entry whose witness does not actually violate its
hypothesis fails the run. A register that is empty when a hypothesis was refuted,
or that contains an entry for a hypothesis that in fact survived, also fails.

`Q4` is registered `[NAIVE]` precisely so this machinery is exercised on a real
refutation rather than on a planted one. If `Q4` unexpectedly survives, that is
itself the reported result and the `[NAIVE]` label is retired in an amendment.

## Two materially independent routes

- **Route A** `z7_impossibility_v1.py`: simulates every candidate over the `8`
  sequences in both modes, accumulates `(e_now, e_delay)` directly, and evaluates
  every hypothesis, ceiling, family and grid cell by scanning the resulting list.
- **Route B** `independent_impossibility_oracle_v1.py`: never simulates a
  sequence. It derives each candidate's error counts from a combinatorial
  occupancy argument over the `(state, mode, cur, prev)` index — computing, for
  each candidate, the exact number of scored moments reaching each table index by
  a state-reachability recurrence — and then rebuilds `S_0`, `S_1`, every family,
  every ceiling, every grid cell and every counterexample witness from that
  construction. It imports nothing from route A and nothing from the Z3, Z5, Z12
  or Z15 packages.

Agreement is required on every reported integer, every witness and every verdict.

## Null the true result must beat

`200` seeded random impossibility claims of the form

```
no candidate with bits = b attains  e_now <= x  and  e_delay <= y
```

with `(b, x, y)` drawn from the registered ladder `b ∈ {0,1}`,
`x, y ∈ {0..16}`, excluding the frozen true claims. Each is adjudicated by the
exhaustive scan. Two quantities are reported:

- **witness soundness**: for every claim the scan declares false, an explicit
  counterexample candidate must be produced and independently re-verified by
  route B. Target `100%`; anything less means the adjudicator is guessing.
- **tightness discrimination**: the count of random claims that are *both* true
  *and* tight (i.e. true, and false for the immediately weaker target
  `(x+1, y)` or `(x, y+1)`). The frozen ceiling set must score `k/k` on
  tightness; the random set scores `X/200`, reported. If `X/200` is not clearly
  worse, the frozen ceilings are not special and the result is diagnosed rather
  than declared green.

## Hostiles, each with the quantity it must move

| hostile | quantity | required movement |
|---|---|---|
| `H1_WRONG_CEILING` | violation count for `C1` restated as `e_delay >= 9` | must move from `0` to exactly `16` (every stateless candidate violates it) |
| `H2_VACUOUS_CEILING` | tightness flag for `C1` restated as `e_delay >= 0` | must move from tight to slack, i.e. the ceiling must be reported non-binding |
| `H3_TRUNCATED_UNIVERSE` | `|S_1|` and the infeasible-cell count | dropping the stateful half must change both |
| `H4_SCORER_OFFSET` | stateless `e_delay` | scoring `t = 0` as a delay moment must move `e_delay` off `8` for at least one table |
| `H5_FAKE_WITNESS` | register integrity | a counterexample register entry whose witness does not violate its hypothesis must fail the check |

A hostile that cannot move its quantity is a defect: the run fails. `H2` is
included because a ceiling that cannot be violated is exactly the failure mode
the prior Z lane's mis-specified calibration instrument had — a check that cannot
fire.

## Forbidden promotions

`UNIVERSAL_IMPOSSIBILITY`, `IMPOSSIBILITY_FOR_REAL_SYSTEMS`,
`CAPABILITY_CEILINGS_TRANSFER_TO_TRAINED_MODELS`,
`COMPLETE_ENUMERATION_OF_FAILURE_MODES`,
`RESOURCE_ACCOUNTING_IS_SUBSTRATE_INDEPENDENT`,
`IMPOSSIBILITY_REGION_IS_ARCHITECTURE_INDEPENDENT`,
`ZERO_STATE_MEANS_ZERO_MEMORY_IN_GENERAL`.

## Falsifiers of this package itself

- Route A and route B disagreeing on any integer, witness or verdict.
- Any hostile that cannot move its named quantity.
- Any frozen ceiling that is valid but not tight, reported as if it were a result.
- A counterexample register entry whose witness does not violate its hypothesis,
  or a refuted hypothesis with no register entry.
- Witness soundness below `100%` on the null.
