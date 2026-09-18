# gmi-833-ae-ae10-usable-information-v1

Section AE10 asks what `usable information` means once computation, memory,
communication, precision, time and energy are budgeted, and demands exact
examples where Shannon information is identical but achievable performance is
not. This package defines it, bounds it, and separates it on both cost axes.

**Definition.** `U(W, T, R)` is the achievability gap at budget `R`: the best
expected score over the rules admissible at `R`, minus the best score with no
observation. The frozen lattice is `(k, d, m, p, c)` — junta arity, decision
tree depth, labelled-sample budget, observation precision, communication bits —
ordered componentwise, with **128** decoder-side cells. **Time and energy are
declared dimensions that are NOT instantiated in v1**, recorded as a checked
field so the omission cannot pass as a measurement.

| result | numbers |
|---|---|
| `USE-1` monotonicity | **9,000** ordered budget pairs across 3 worlds, **0** violations; rule-class inclusion checked separately |
| `USE-2` full-information ceiling | **0** violations; equality attained at the top for every world |
| `USE-3` decoding cost | two worlds, `I(X;Y) = 1` bit **exactly** for both, `U = 0` vs `1/2` at the identical budget `k1_d1_p3_c2` |
| `USE-3` search cost | one **fixed** world, information identical by identity, accuracy `5/8 → 43/64 → 383/512 → 3463/4096` as `m` goes 0→3 |
| `USE-4` unconditional fixture | all `7` proper coordinate subsets exactly uniform, **0** violations; `U = 0` at arity 2, `1/2` at arity 3 |
| `USE-5` crosswalk | 4 parent mappings, each with a citation, in the machine-readable receipt |

**Why the search-cost example is a fixed world.** Comparing two candidate sets
would compare two *different* worlds with different mutual information. Holding
one world fixed and moving only the sample budget makes the equal-information
premise true by identity. The two-candidate comparison is still reported, and
is explicitly labelled as *not* an equal-Shannon comparison.

**Unconditional, not cryptographic.** The `USE-4` separation rests on the
machine-checked fact that `(x_S, y)` is exactly uniform for every proper
coordinate subset `S`. No hardness assumption is invoked; the receipt records
`cryptographic_assumption_used: false` and
`is_a_complexity_class_separation: false`.

**Two routes.** Route A uses a subcube dynamic program and a closed-form
`GF(2)` coset argument for the learning curve. Route B builds every admissible
decision tree explicitly and enumerates every `(secret, training tuple, test
point)`. They agree over the whole 128-cell lattice and at every sample budget.

**Null.** Detector: one exact bit of Shannon information with zero usable
information outside the top face of the binding dimensions, with the
communication dimension first *verified* non-binding. Fires on the planted
3-parity, not on the dictator or the two-bit xor, and on `0` of `200` random
deterministic worlds.

**Row not closed.** *Determine whether GMI morphology selection is better
predicted by raw information, usable information, or a vector of
resource-conditioned sufficient statistics.* That needs pinned morphology
receipts and is deferred to the morphology sweep in the section map.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae10-usable-information-v1/test_ae10_usable_information_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae10-usable-information-v1/test_ae10_usable_information_v1.py -v
python3 -I -B research/gmi-833-ae-ae10-usable-information-v1/ae10_usable_information_v1.py
```
