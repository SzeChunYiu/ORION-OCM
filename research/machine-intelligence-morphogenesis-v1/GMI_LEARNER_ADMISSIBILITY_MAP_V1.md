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

---

## The flat-ceiling hypothesis it suggested is NOT supported

The map above showed the learner's capability varying less across ecologies (0.807–0.865) than the best
constant did (0.708–0.875), which suggested a predictive law: **each family has a roughly
ecology-independent ceiling, so which species are admissible where is decided by the constant rather than
by the family.** If true, species occupancy would follow from two numbers.

Tested by measuring six hand-built families across all six ecologies, minimum over the six interventions
(`STAGE_FAMILY_ECOLOGY_MATRIX_CHEAP_V1.json`). The law predicts every family's standard deviation should
be clearly below the constant's.

| row | mean | stdev | spread | flatter than the constant? |
|---|---:|---:|---:|---|
| **BEST CONSTANT** | 0.8090 | **0.0516** | 0.1667 | — |
| `gradient_net_h2` | 0.6788 | 0.0406 | 0.1094 | yes |
| `hamming_knn_k3` | **0.8524** | 0.0435 | 0.1355 | yes |
| `gradient_net_h4` | 0.7335 | 0.0560 | 0.1459 | no (comparable) |
| `soft_retrieval` | 0.8142 | 0.0655 | 0.2083 | **no** |
| `exemplar_table` | 0.6285 | 0.1092 | 0.3333 | **no** |
| `constant_emitter` | 0.6979 | 0.2769 | 0.7917 | **no** |

**Two of six.** The hypothesis fails: for most families, capability varies as much as or more than the
constant does, so occupancy cannot be predicted from a family ceiling plus an ecology constant. Recorded
as a negative because it was my hypothesis and it is wrong — family capability is genuinely
ecology-dependent, which is the same lesson `DU-1` teaches about reachability: these quantities are not
functions of convenient summaries.

(`constant_emitter`'s 0.2769 is a sanity check that the measurement is behaving: it is one *fixed*
constant, while the "best constant" is chosen per ecology, so it should and does vary far more.)

## What the same data does show

**Memory is the broadly admissible family, by a clear margin.** Counting admissibility (θ = 0.85 and
≥ 1 fx over the ecology's best constant):

| family | admissible on |
|---|---|
| `hamming_knn_k3` | **`E_parity`, `E_sym3`, `E_sym5`** — 3 of 6 |
| `soft_retrieval` | `E_smooth3` — 1 of 6 |
| `gradient_net_h2`, `gradient_net_h4`, `exemplar_table`, `constant_emitter` | none |

`hamming_knn_k3` also carries the highest mean of any row measured (0.8524, above the mean best constant
of 0.8090). That is the hand-built counterpart of what the searched population keeps showing — memory
carriers occupy where others do not — and it now has a number attached rather than only a recovery rate.

Note the two `gradient_net` rows here (`h2`, `h4`) are admissible nowhere, while the parametrised
`gradient_net(h=3, lr=1)` measured above **is** admissible on `E_wit1` at +3.751 fx. Different
configurations of one family, and the difference matters: the learner family's admissibility is
configuration-sensitive as well as ecology-sensitive, which is a further reason the flat-ceiling reading
was too simple.
