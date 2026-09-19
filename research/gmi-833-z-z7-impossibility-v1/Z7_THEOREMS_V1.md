# Z7 named results — prospective impossibility and failure prediction

Scope for every result: the registered finite universe `U` of `65552`
architecture-name-free binary mechanisms, scored over all `8` length-`3` input
words in both modes at `t = 1, 2` (`N = 16` scored moments per mode), with

```
J(u) = eta * ( (1-p) * e_now(u)/16 + p * e_delay(u)/16 ) + lambda * bits(u),
```

and the `60` registered worlds of `gmi-833-heldout-20-transitions-v1`. Exact
integer and rational arithmetic; no float appears in any statement. Every
hypothesis and ceiling below was committed in `FREEZE_V1.md` before the
enumeration that adjudicates it, and `git log` carries that ordering.

---

## `IM-1` — a capability that cannot be achieved under a stated constraint

**Statement.** Under the constraint `bits = 0`, zero-error delayed recall is
impossible. Stronger: every one of the `16` stateless candidates has
`e_delay = 8 = N/2` exactly, so delayed recall at `bits = 0` is capped at
accuracy exactly `1/2`, the chance rate, and the failure is **uniform across the
whole family** rather than variable.

The impossibility is **resource-dependent, not task-dependent**: the identical
task is solved with `0` errors at `bits = 1`. A GMI impossibility claim is only
meaningful relative to a declared resource budget.

**General-alphabet form.** With symbol alphabet `A`, every `0`-register
candidate has `e_delay >= (1 - 1/A) * N`.

**Quantifiers.** All `16` stateless candidates; all `p, eta`.

**Falsifier.** One stateless candidate with `e_delay < 8`; or no `bits = 1`
candidate with `e_delay = 0`.

**Strongest parents.** That a memoryless map cannot predict an independent
uniform symbol is standard information theory (C. E. Shannon, Bell Syst. Tech. J.
**27** (1948) 379, DOI 10.1002/j.1538-7305.1948.tb01338.x). Nothing there is
claimed novel. The residual is the *uniformity* — the entire family sits at
`N/2`, not merely its optimum — and the exact resource-conditional form.

**Forbidden extrapolation.** `ZERO_STATE_MEANS_ZERO_MEMORY_IN_GENERAL`,
`IMPOSSIBILITY_FOR_REAL_SYSTEMS`.

---

## `IM-2` — exact resource-dependent impossibility regions

**Statement (attainability lattice).** In the `17 x 17 = 289`-cell lattice of
possible `(e_now, e_delay)` pairs:

- at `bits = 0` exactly `3` cells are attained — `(0,8), (8,8), (16,8)` — so the
  impossibility region has exactly `286` cells;
- at `bits = 1` exactly `143` cells are attained, so the impossibility region has
  exactly `146` cells;
- the Pareto-minimal frontier is `{(0,8)}` at `bits = 0` and `{(0,0)}` at
  `bits = 1`.

**Statement (cost grid).** Over the frozen `7680`-cell grid of
`(p, eta, lambda, a_now, a_delay, C, b)`, exactly `3656` cells are infeasible —
no candidate within budget `b` meets both error targets at cost at most `C` —
split `2976` at `b = 0` and `680` at `b = 1`. Feasible cells: `4024`. The
partition is complete.

**Quantifiers.** Exhaustive over `U` and over every grid cell.

**Falsifier.** A candidate realising a pair outside the attained set; a cell
classified infeasible with a witness inside budget.

**Forbidden extrapolation.** `IMPOSSIBILITY_REGION_IS_ARCHITECTURE_INDEPENDENT`.

---

## `IM-3` — prospectively frozen qualitative failure modes

Five failure-mode predictions were frozen before the scan, each labelled with
what the author did and did not know at freeze time.

| id | label | verdict | evidence |
|---|---|---|---|
| `Q1` uniform half-failure of the delay channel at `bits = 0` | `[DERIVED-AT-FREEZE]` | CONFIRMED | stateless `e_delay` value set `= {8}` |
| `Q2` non-uniform copy-channel failure at `bits = 0`, values `{0,8,16}` | `[DERIVED-AT-FREEZE]` | CONFIRMED | stateless `e_now` value set `= {0,8,16}` |
| `Q3` the modal one-state-bit failure profile is `(8,8)` | `[UNCOMPUTED]` | CONFIRMED | `(8,8)` with multiplicity `14664` of `65536` |
| `Q4` **scarcity hypothesis**: no one-state-bit mechanism attains `e_delay = 0` with `e_now = 16` | `[NAIVE]` | **REFUTED** | witness `nxt = 68`, `table = 13`, `(e_now, e_delay) = (16, 0)` |
| `Q5` some one-state-bit mechanism is strictly worse on delay than every stateless one | `[UNCOMPUTED]` | CONFIRMED | witness `nxt = 4`, `table = 64`, `(8, 11)` |

`Q4` was registered `[NAIVE]` so that the row-6 counterexample machinery would be
exercised on a real refutation rather than a planted one.

---

## `IM-4` — prospectively frozen quantitative capability ceilings

Six bounds were frozen before evaluation. Each is classified by whether it can be
violated at all, because tightness-as-attainment detects vacuity only for a
*lower* bound: for an upper bound sitting at the top of its quantity's a priori
range, attained and vacuous coincide and the check goes silent. The classifier is
validated on real data — it must fire on `C4` and on the `H2`/`H6` hostiles and
stay silent on `C1`, `C2`, `C6` — and both the recall and the no-alarm case are
gated.

**Three genuine forbidding ceilings**, each valid (no violation on the exhaustive
scan) and tight (attained by an exhibited witness):

| id | family | ceiling | valid | tight |
|---|---|---|---|---|
| `C1` | `bits = 0` | `e_delay >= 8` | `0` violations | minimum `= 8` |
| `C2` | `bits = 0` | weighted risk `>= p/2` for every `p` | `0` violations over the `5`-rung `p` ladder | equality at every rung |
| `C6` | whole universe | `min J = min(eta*p/2, lambda)` | `0` violations over `60` worlds | exact |

**Three retained but not counted as ceilings:**

| id | claim | classification | why |
|---|---|---|---|
| `C3` | weighted risk `>= 0` | `NON_BINDING` | the bound sits at the range minimum; what survives is the attained minimum, exactly `0` |
| `C4` | `min(e_now, e_delay) <= 16` | `NON_BINDING` | both error counts lie in `[0, 16]` by construction, so no candidate in any universe can violate it; its `0` violations were guaranteed before the enumeration ran |
| `C5` | `\|S_1\| = 143` | `MEASURED_IDENTITY` | the right-hand side is defined as the measured quantity |

`C4` was reported valid-and-tight by the first receipt and the gate passed. It is
reclassified in `FREEZE_V1_AMENDMENT_2.md`, committed before the corrected
receipt. Row 4 closes on `C1`, `C2` and `C6` — three ceilings that could have
failed and did not — not on a count that includes a tautology.

## `IM-5` — broad families, and a structural impossibility inside one of them

**Statement.** Every prediction is tested against the entire universe
(`65552` candidates) and against six structurally defined named families:
`F_STATELESS` (`16`), `F_DEAD_TABLE` (`4096`), `F_FROZEN_STATE` (`512`),
`F_MOORE` (`4096`), `F_MEALY_PURE` (`61440`), `F_IDENTITY_STATE` (`256`).
`F_MOORE` and `F_MEALY_PURE` partition the stateful half.

**The structural finding.** A *named architecture family can carry its own
impossibility*. The Moore family — whose output does not read the current input
symbol — cannot reach fewer than `8` copy-channel errors, with Pareto frontier
`{(8,0)}`, while the complementary Mealy family reaches `0`, frontier `{(0,0)}`.
The two families have the same state budget and the same universe; the
separation is structural, not resource-driven.

**Falsifier.** A Moore machine with `e_now < 8`.

**Strongest parents.** The Moore/Mealy distinction and its expressive consequences
are classical (Mealy 1955; Moore 1956, cited above). Nothing there is claimed
novel. The residual is the exact frontier separation inside this registered
universe and its role as a resource-independent impossibility.

**Forbidden extrapolation.** Nothing here transfers to MLP/CNN/Transformer
families or to any trained system.

---

## `IM-6` — counterexample register and recursive repair

**Statement.** `COUNTEREXAMPLE_REGISTER_V1.json` records the refutation of `Q4`
with its explicit witness, the assumption that failed, the repair, and the
claim-ceiling consequence.

- **Assumption that failed:** one bit of persistent state is a shared scarce
  resource, so accuracy on one channel must be paid for with accuracy on the
  other.
- **Repair:** the state index carries the mode bit, so the two channels address
  disjoint output and next-state entries. A single state bit is *not* shared
  between them, and perfect delay is compatible with maximal copy error.
- **Claim-ceiling consequence:** no impossibility statement in this universe may
  be derived from "one bit must be shared"; every such statement must be derived
  from the per-mode index structure.

The witness is re-scored independently by both routes in the test suite, so the
register is verified rather than asserted.

**Falsifier.** A register entry whose witness does not violate its hypothesis; a
refuted hypothesis with no register entry.

---

## `IM-7` — the null, and why tightness is the discriminator

**Statement.** Over `200` seeded random impossibility claims of the form *no
candidate with `bits <= b` attains `e_now <= x` and `e_delay <= y`*:

- **witness soundness `153/153`**: every claim the scan declared false came with
  an explicit counterexample candidate, and every one of them was re-verified.
- **tightness discrimination**: `47/200` random claims are true, but only
  `6/200` are true *and* tight, against `3/3` for the frozen forbidding ceilings.

Tightness, not truth, is what separates a registered ceiling from a random one: a
random true claim is usually slack, and a slack bound is not a capability ceiling.

**Falsifier.** Witness soundness below `100%`; random claims as tight as the
frozen ones.
