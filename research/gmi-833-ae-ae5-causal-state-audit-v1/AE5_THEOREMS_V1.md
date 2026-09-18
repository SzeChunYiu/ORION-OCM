# AE5 theorems v1

Claim ceiling
`GMI_833_AE5_PREDICTIVE_STATE_PARENT_OWNERSHIP_AUDITED_ON_A_REGISTERED_FINITE_DYADIC_PROCESS_FAMILY`.
Freeze `c69062ee7c7c9bee9aa1534fe5c88de58b7f50d5`; source main
`349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

## 0. The registered family, and why it is dyadic

A process of length `L = 3` assigns to each prefix either a fresh fair coin or
a constant. There are `3^7 = 2187` such processes and every atom of the joint is
a power of `1/2` by construction.

A member is **registered** when its causal-state masses are themselves exactly
dyadic; `2,019` are, `168` are not and are excluded with a count. For a dyadic
distribution `H = Σ 2^-a · a`, an exact rational — so **no logarithm is ever
evaluated**, and any non-dyadic mass raises rather than silently degrading to a
float. This is the price of exactness and is declared in the freeze.

`C_μ` is the entropy of the causal-state masses at prefix length `2` with
horizon `1`; `E` is `I(X_0X_1 ; X_2)`, computed only on the `1,527` members where
all three block distributions are dyadic.

## 1. AE5-1 — the exact applicable scope of the identification

**Definition.** Two histories are GMI horizon-`H` equivalent iff they induce the
same conditional distribution over the next `H` symbols.

**Statement.** At horizon `H` this partition is exactly the Crutchfield–Young
causal-state partition truncated to horizon `H`. The sequence is monotone
refining in `H` — verified on all `2,019` members — and stabilises at an `H*`
that is `1` for `1,863` members and `2` for `156`.

**The scope is not optional.** The member `F F F F F 0 0` has `1` class at
horizon `1` and `2` at horizon `2`. So an unqualified identification of GMI
predictive equivalence with causal states, without naming the horizon, is
**false**. `H ≥ H*` is the exact condition.

**Falsifier.** A member whose horizon sequence is non-monotone.
**Forbidden extrapolation.** `INFINITE_HORIZON_EQUIVALENCE_PROVED`.

## 2. AE5-2 — statistical complexity and excess entropy

- The GMI minimal sufficient predictive state coincides with the causal-state
  partition on every registered member (this is Shalizi & Crutchfield Theorem 1,
  verified here, not proved here).
- `E ≤ C_μ` holds on `1,527` of `1,527` members where `E` is exactly computable.
  The bound is Crutchfield & Feldman 2003.
- **Strict crypticity is exhibited**: the member `F F F F F 0 1` has
  `C_μ = 3/2`, `E = 1/2`, `χ = C_μ − E = 1`.
- The same member has causal-state masses `(1/4, 1/4, 1/2)` — **non-uniform**.
  This matters: on a family with uniform state masses `C_μ` would be a
  relabelling of the state count, and the comparison the row asks for would be
  vacuous. It is not vacuous here.

Observed value sets: `|S| ∈ {3,4,5,6}`, `rank ∈ {1,2}`,
`C_μ ∈ {0, 1, 3/2}`, `E ∈ {0, 1/2, 1}`.

## 3. AE5-3 — the parent-ownership verdict

| statement | parent | verdict |
|---|---|---|
| minimality of the predictive state | Shalizi & Crutchfield 2001, Thms 1, 3 | `PARENT_SUFFICIENT` |
| state complexity is an entropy of the minimal partition | Crutchfield & Young 1989 | `PARENT_SUFFICIENT` |
| predictive-information bound | Crutchfield & Feldman 2003; Bialek et al. 2001 | `PARENT_SUFFICIENT` |
| linear rank is not the state count | Jaeger 2000; Hsu et al. 2012 | `PARENT_SUFFICIENT` |
| horizon-indexed refinement + resource-priced selection | no parent located | `RESIDUAL` |

`PARENT_SUFFICIENT` is a **success terminal**: the right answer to "is this
already parent-owned?" is often yes, and the receipt records
`novelty_claimed_for_gmi_state_complexity: false`.

## 4. AE5-4 — the four quantities disagree

Quantities: predictive-state cardinality `|S|`; the rational Hankel
(observable-operator) rank; the causal-state entropy `C_μ`; the registered
generative description length.

**11 of the 12** ordered pairs disagree — two members share the first quantity
and differ in the second — and **6** pairs additionally admit a strict order
reversal. Hence **all six unordered pairs are non-equivalent**.

**The one determined direction is proved, not unexamined.** `C_μ → rank` is
determined because the Hankel rank at split `k` is at most the number of causal
states at prefix length `k` (Carlyle–Paz / Fliess; Jaeger 2000) — verified on
all `2,019` members — and at `L = 3` the registered split admits at most `2`
states, so `rank ∈ {1,2}` and `C_μ = 0` forces `rank = 1`. The reverse direction
`rank → C_μ` still disagrees (`rank = 2` occurs with both `C_μ = 1` and
`C_μ = 3/2`), so the quantities remain non-equivalent. Widening the rank range
requires `L ≥ 4`, which the exhaustive family size forbids at this scope; that
limitation is stated rather than hidden.

## 5. AE5-6 — finite horizon, and the gaps preserved

The claim is finite-horizon only. Extending it would require, and this tranche
does **not** assume: stationarity; ergodicity; measurability of the
semi-infinite future σ-algebra; existence of the causal-state partition as a
measurable partition (Shalizi & Crutchfield 2001, §4); a dominating measure
making conditional distributions well defined almost surely.

`INFINITE_HORIZON_EQUIVALENCE_PROVED` is a registered forbidden promotion and
the gap is **enforced**: `gap_preservation_guard` walks the receipt for any
unqualified infinite-horizon field, reports `0` alarms here, and detects the
planted claim.

That truncation genuinely loses information is **proved**: the member
`F F F F F F 0` has `1` class at horizon `1` and `2` at horizon `2`. Extending
without the assumptions above is therefore unsound, not merely unproven.

## 6. Two routes

Route A propagates the joint forward through the tree, reads dyadic exponents by
repeated division, and computes the rank by rational Gauss–Jordan. Route B
(`independent_process_oracle_v1.py`) computes each word's probability by walking
the tree for that word alone, reads exponents with `bit_length`, computes the
rank by fraction-free **Bareiss** elimination over the integers, and counts the
description length by a queue walk. It imports nothing from Route A. The two
agree on all `2187` joints and on every quantity on the sampled members.

The oracle earned its keep: it caught a slot-ordering discrepancy between the
two enumerations before any result was recorded.

## 7. Hostiles and nulls

| id | perturbation | moves its quantity | detected |
|---|---|---|---|
| `H1_horizon_truncation_passed_off_as_full` | report the horizon-1 partition as the full one | class count moves `1 → 2` | yes |
| `H2_non_dyadic_entropy` | feed `(1/3, 2/3)` to the entropy | the masses are genuinely non-dyadic | yes, raises |
| `H3_infinite_horizon_claim` | plant an unqualified infinite-horizon field | guard alarms rise `0 → 1` | yes |
| `H4_rank_identified_with_state_count` | report the Hankel rank as `|S|` | a member with `rank ≠ |S|` exists | yes |
| `H5_parent_blob_tamper` | corrupt a pinned blob sha | audit flips | yes |

**Null.** The detector is `E ≤ C_μ` on every member. It raises `0` alarms on the
true family — the no-alarm case, asserted directly — while `200` shuffled
assignments of `E` values to members satisfy it in `0` trials. The bound is
therefore a property of the pairing, not of the value multisets.
