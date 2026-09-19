# Z13-P3 named results (Z13 rows 9-10, Z16 chain)

All results are stated at the scope fixed by `FREEZE_V1.md` §1 and
`FREEZE_V1_AMENDMENT_1.md`: the three-mode extension of the registered binary
transducer universe at sequence lengths `L in {5, 6}`, uniform independent
inputs, canonical initial state `0`, state budget `b in {0, 1, 2}`,
mode-indexed output and next-state tables, scored window `t in {2, .., L-1}`
(`96` scored moments per mode at `L = 5`, `256` at `L = 6`), exact rational cost
`C = eta*(p0*r_now + p1*r_delay1 + p2*r_delay2) + lambda*b`.

Nothing below is claimed beyond that scope. `L outside {5, 6}`, `b > 2`,
non-uniform input laws, larger alphabets and any real or trained system are all
outside it. Every number is in `RESULT_V1.json` (Route A) and
`ORACLE_RESULT_V1.json` (Route B); the two routes agree on every one of them.

---

## `ZP-1` — the one-bit delay-2 floor moves with `L` exactly as the Markov closed form says

With `R0(d2 | b=1, L) = 1/3 - (1 - (-1/2)^(L-2)) / (18*(L-2))`:

```
L = 5:  R0(d2 | b=1) = 5/16      (predicted 5/16;   per-t errors 1/4, 3/8, 5/16)
L = 6:  R0(d2 | b=1) = 41/128    (predicted 41/128; per-t errors 1/4, 3/8, 5/16, 11/32)
```

Exhaustively over the `16` next-state functions at `b = 1`, the floor is attained
by **exactly two** functions at each `L`, the copy-then-reset pair
`(0, 1, 0, 0)` and `(1, 0, 0, 0)`; the two copy-then-**set** functions that tied
at `L = 4` drop out (`(0, 1, 1, 1)` scores `17/48` at `L = 5`, `ZP-5`). All other
floors are as predicted: `R0(now | b) = 0` for every `b`; `R0(d1 | 0) = 1/2`,
`R0(d1 | 1) = R0(d1 | 2) = 0`; `R0(d2 | 0) = 1/2`, `R0(d2 | 2) = 0`, at both `L`.

**Quantifiers.** For all next-state functions at `b <= 1` (exhaustive, both routes) and for the `b = 2` floors, witnessed at their lower bound `0` by a two-bit shift register (Route B) and by exhaustive enumeration of the `65,536` next-state functions (Route A).

**Assumptions.** Uniform i.i.d. binary inputs; the declared window; initial state `0`; per-address majority outputs (`MAJORITY-OPTIMALITY`, re-verified by Route B over all `51` `(mode, next-state)` pairs at `b <= 1`, `L = 5`, against every output table).

**Dependencies.** The one-bit Markov chain `pi_k = (1 - pi_{k-1})/2` of `FREEZE_V1.md` §3.1; Route B's exact propagation of the joint law of `(state, x_{t-1}, x_{t-2})`.

**Falsifiers.** A next-state function at `b = 1` below `5/16` at `L = 5` or below `41/128` at `L = 6`; a third function attaining the floor; a per-t error off the closed form.

**Strongest parents.** Finite-memory prediction (Hellman & Cover 1970); finite-state machine minimisation (Mealy 1955; Moore 1956); the parent adjudication's `ZA-1` at `L = 4`.

**Forbidden extrapolations.** `FLOORS_HOLD_AT_OTHER_L_OR_WINDOW_OR_INPUT_LAW`; the limit `1/3` is a property of the closed form, not a verified floor at any `L > 6`.

---

## `ZP-2` — both thresholds are marginals at every world and both `L`

On the `135`-world eighths grid at each `L`: the lower endpoint of the one-bit
niche is `lambda_2* = E(1) - E(2) = eta*p2*R` in `135/135` worlds and the upper
endpoint is `lambda_1* = E(0) - E(1) = eta*(p1/2 + p2*(1/2 - R))` in `135/135`
worlds, `R = R0(d2 | b=1, L)`; numerically `eta*(p1/2 + 3*p2/16)` at `L = 5` and
`eta*(p1/2 + 23*p2/128)` at `L = 6`. Route B confirms the endpoints without
differencing: scanning an exact `lambda` grid, every grid point strictly inside
`(lambda_2*, lambda_1*)` has budget `1` as the unique minimiser and every grid
point outside does not, `135/135` at both `L`. `0` of `200` seeded coefficient
pairs `(a, b)` in `k/128`, drawn from the grid minus the marginal pair, reproduce
the upper endpoint on all `135` worlds (best `27/135`); the marginal pair scores
`135/135`.

**Quantifiers.** For all `135` worlds `eta in {1,2,3}` x `(p0,p1,p2)` over eighths, at `L = 5` and `L = 6`.

**Assumptions.** The declared linear budget price; `MODE-INDEPENDENCE` (re-verified by Route B by brute force over the full `256^3` joint product of per-mode `(output, next-state)` pairs at `b = 1`, `L = 5`, and over `4^3` at `b = 0`).

**Dependencies.** `ZP-1`; `IC-1` of `gmi-833-z-z1-master-principle-v1` (the envelope-vertex criterion); `DS-5` of `gmi-833-z-z6-discrimination-v1` (the two-level case).

**Falsifiers.** One world where a marginal form misses the observed endpoint; a seeded pair reaching `135/135`.

**Strongest parents.** Lagrangian scalarisation over a lower convex envelope (Everett 1963; Geoffrion 1968); the parent's `ZA-2` at `L = 4`.

**Forbidden extrapolations.** `REPAIRED_LAW_IS_UNIVERSAL`; `ENVELOPE_MATHEMATICS_CLAIMED_AS_NOVEL`.

---

## `ZP-3` — the prospective niche (row 9)

The one-bit class is the unique cost minimiser exactly on `(lambda_2*, lambda_1*)`,
non-empty **iff** `p1 > p2*(4R - 1)`: `4*p1 > p2` at `L = 5`, `32*p1 > 9*p2` at
`L = 6`. On the eighths grid the niche is non-empty in **`96` of `135`** worlds
at both `L` (the rule matches the enumeration `135/135` at both `L`). Inside the
niche the unique minimisers use the copy-then-reset pair on the delay-2 channel
and an identity-type next-state (`(0, 1, 0, 1)` or `(1, 0, 1, 0)`) on the delay-1
channel; witness world `eta = 1`, `p = (0, 1/4, 3/4)`, `lambda = 1/4`. All of
this was written in `FREEZE_V1.md` §3.3 before any `L = 5` or `L = 6`
enumeration existed (custody: `ZP-7`).

**Quantifiers.** For all `135` grid worlds at each `L`; for the minimisers, at every niche world with `p1, p2 > 0`.

**Assumptions.** As `ZP-2`.

**Dependencies.** `ZP-1`, `ZP-2`.

**Falsifiers.** A grid world whose niche emptiness disagrees with `p1 > p2*(4R-1)`; a niche minimiser off the copy-then-reset pair.

**Strongest parents.** The parent's `ZA-5` (niche width `eta*(p1/2 - p2/8)` at `L = 4`) and `ZA-6` (the recovered class is `F_MEALY_PURE`).

**Forbidden extrapolations.** `NEW_ARCHITECTURE_FAMILY_CLAIMED` — the minimisers are Mealy machines; `W4_STATUS_CLAIMED`.

---

## `ZP-4` — the matched negative ecology moves with `L`, and one world flips (row 10)

The advantage disappears exactly on `p1 <= p2*(4R - 1)`, coefficient `1/4` at
`L = 5` and `9/32` at `L = 6`. The five frozen probe worlds behave as tabled at
all three `eta`, on both routes:

| world `(p0, p1, p2)` | `L = 5` | `L = 6` |
|---|---|---|
| `(0, 17/81, 64/81)` flip world | non-empty, width `eta/162` | **empty**, width `-eta/162` |
| `(0, 9/41, 32/41)` boundary world | non-empty | empty at exact equality, width `0` |
| `(0, 1/4, 3/4)` control | non-empty | non-empty |
| `(0, 1/8, 7/8)` control | empty | empty |
| `(1/4, 3/4, 0)` retired ecology `p2 = 0` | non-empty, width `eta*3/8` | non-empty, width `eta*3/8` |

The flip world is a change of the selected class driven by sequence length
alone, at fixed `(eta, p, lambda)`-family: a phase boundary in `L` that the
retired level-valued law (`Z13-P1`, collapse at `p2 = 0`, no `L` dependence) and
the registered `CP-4` (zero finite-size drift of the **two-level** boundary)
cannot express. `0` of `200` seeded collapse coefficients `c in k/64`, drawn from
the grid minus `18/64`, classify all `156` worlds of the amended grid (best
`153/156`); the predicted `9/32` scores `156/156`. The two null-discriminating
worlds of the amendment behaved as predicted before their enumeration (`18/82`:
empty, width `0`; `19/83`: non-empty).

**Quantifiers.** For the five probe worlds and the two null-discriminating worlds at `eta in {1,2,3}`; for the rule, over all `135` grid worlds at each `L`.

**Assumptions.** As `ZP-2`; the probe table of `FREEZE_V1.md` §3.4 fixed before enumeration.

**Dependencies.** `ZP-1`..`ZP-3`.

**Falsifiers.** The flip world not flipping; the `p2 = 0` world's width off `eta*3/8`; a seeded coefficient at `156/156`.

**Strongest parents.** Everett 1963 for the envelope; the parent's `ZA-5` repaired ecology `4*p1 <= p2` at `L = 4`, of which the `L = 5` rule is the same and the `L = 6` rule is the first `L`-dependent form.

**Forbidden extrapolations.** `RESULT_EXTENDED_BEYOND_L_IN_5_6`; the limit coefficient `1/3` is not verified at any `L > 6`.

---

## `ZP-5` — a negative control on the mechanism

The copy-then-set function `(0, 1, 1, 1)` attains delay-2 error exactly `17/48`
at `L = 5` (`49/128` at `L = 6`), strictly above the floor, as the split argument
of `FREEZE_V1.md` §3.1 requires. Seven hostiles move the quantity they perturb
(level-for-marginal `27/135`; window `{1..4}` floor `23/64`; skewed input
`q = 1/3` floor `59/243`; identity-family template `1/2`; set-for-reset `17/48`;
accounting `2^b - 1` `27/135`; the `L = 4` window on `L = 6` `5/16` vs `41/128`),
the registered no-alarm control (initial state `0 -> 1`) is silent, and the one
vacuous hostile (the `L = 4` window on `L = 5`, where `(1/4 + 3/8)/2 = 5/16`
coincides with the true floor) is published as vacuous, not counted.

**Quantifiers.** For the named functions and hostiles at the stated `L`.

**Assumptions.** As `ZP-1`.

**Dependencies.** `ZP-1`.

**Falsifiers.** The set variant at the floor; an applicable hostile that does not move; the no-alarm control firing.

**Strongest parents.** Standard planted-defect control design.

**Forbidden extrapolations.** None beyond scope.

---

## `ZP-6` — the verdict

`Z13-P3` is a **HIT** on every named axis (`P3-a1`, `P3-a2`, `P3-a3`, `P3-b`,
`P3-c`, `P3-d`, `P3-e`) at both `L`, on both routes, under the HIT rule of
`FREEZE_V1.md` §3.6 fixed before enumeration. The only recorded miss is of a §5
null-design clause on the frozen world grid (`FAILED_PREDICTION_REGISTER_V1.json`
`NULL2-UNIQUENESS-CLAUSE`), attributed to the grid, repaired by amendment before
the receipt commit, and left on the record.

**Quantifiers.** For the frozen prediction as a whole.

**Assumptions.** The decision rule of `FREEZE_V1.md` §4.

**Dependencies.** `ZP-1`..`ZP-5`; both receipts.

**Falsifiers.** Any `hit_conditions` cell turning false on a re-run, which the workflow's byte-stability gate cannot let pass silently.

**Strongest parents.** The prediction is this package's own (frozen in §3); the mechanism is the parent's copy-then-reset class.

**Forbidden extrapolations.** `INDEPENDENT_REPLICATION_CLAIMED`; `Z16_ROW4_OR_ROW6_CLOSED_BY_THIS_PACKAGE`; `PARTIAL_HIT_CLOSING_A_ROW_ITS_EVIDENCE_DOES_NOT_REACH`.

---

## `ZP-7` — custody

`FREEZE_V1.md` (with §3 in full) was committed at `f9301396` before any
executor existed; `FREEZE_V1_AMENDMENT_1.md` at `465f096a` before the receipt
commit; the executors, receipts and tests follow in a later commit. The test
`test_12_custody_chain_freeze_precedes_receipts` checks the order by git
ancestry, tolerates a squash merge by checking the freeze is in the publishing
commit, and degrades to a distinct `UNREACHABLE` state without history.

**Falsifiers.** A receipt commit that the freeze commit is not an ancestor of.

**Forbidden extrapolations.** Custody proves prospectivity of the text, not the truth of the claim.
