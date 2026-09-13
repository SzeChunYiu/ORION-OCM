# Where the learner family is admissible, and why the coefficient class is rarely recovered

Date: 2026-09-13. Hand-built rows measured under the six V1 interventions; no search, no adjudication.
Turns the `RV-377-180` gradient finding from a negative into a boundary that explains one.

## The map

`zoo.gradient_net` at the four registered configurations, best minimum over the six interventions per
ecology, against θ = 0.85 and the rule-40 line of ≥ 1 fx over the best constant:

| ecology | best constant | best learner (min over six) | config | margin (fx) | admissible |
|---|---:|---:|---|---:|---|
| `E_wit1` | 0.7083 | **0.8646** | h3 lr1 | **+3.751** | **yes** |
| `E_sym3` | 0.8750 | 0.8594 | h3 lr1 | −0.374 | no |
| `E_sym5` | 0.7917 | 0.8333 | h3 lr2 | +0.998 | no |
| `E_smooth1` | 0.8333 | 0.8281 | h3 lr1 | −0.125 | no |
| `E_parity` | 0.8333 | 0.8177 | h3 lr1 | −0.374 | no |
| `E_smooth3` | 0.8125 | 0.8073 | h3 lr2 | −0.125 | no |

**A registered gradient net is admissible on 1 of 6 ecologies.** On four of the six it scores *below* the
best constant — a learner does worse than emitting a fixed number.

## The pattern, and the mechanism it suggests

The single ecology that admits a learner is the one where the **constant baseline is weakest**: `E_wit1`'s
best constant is 0.7083, while every other ecology's sits between 0.7917 and 0.8750. Everywhere the
constant is strong, the learner lands within ±0.4 fx of it and cannot clear the 1 fx margin the rule-40
line demands.

So the learner family's admissibility here is **not** governed by whether the target is learnable in the
abstract. It is governed by how much room the constant baseline leaves. Where a fixed number already
reaches 0.79–0.875, an adaptive machine has almost nothing to win and must pay for its adaptation.

## What this explains

**The corpus invariant.** `COEFFICIENT_CLASS_NOT_NEUTRALLY_RECOVERED_AT_20K__0_OF_43` is usually read as a
search failure. On five of these six ecologies **there is no admissible registered learner to recover**,
so neutral search cannot be faulted for not finding one. That is a capability boundary, not a search one.

**The class-rate law's `C` clause, which already encodes this distinction empirically.** `C` reads
"coefficient class ≤ 1/3 on witness-free ecologies; no bound where witness-bearing". This map supplies a
mechanism for it: `E_wit1` is the witness-bearing case, and it is exactly where the constant is weak
enough for a learner to clear the margin. The clause's empirical split and this measured boundary are the
same fact seen twice.

**The `RV-377-210` packet's one coexistence verdict.** That packet returned `FAMILY_COEXISTENCE` on
`E_wit1` alone, because a coefficient row joins the Pareto set there. Independently measured, `E_wit1` is
the single ecology in this registry where such a row is admissible at all. Two instruments, one boundary.

## Scope, stated once

Four hand-built configurations, six registered ecologies, one basis, θ = 0.85, the V1 intervention family.
By the `M′` rule a hand-built row licenses **presence, never absence**, so "no admissible learner" here
means no *registered* learner, not that none exists. The positive half is firmer than the negative half:
`E_wit1` admitting one at +3.751 fx is an existence result and needs no such qualification.
