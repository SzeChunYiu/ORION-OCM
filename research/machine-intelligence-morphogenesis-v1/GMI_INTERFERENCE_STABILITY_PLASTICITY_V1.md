# Interference and the stability-plasticity tradeoff (I1, last box)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/interference_witness.py`.
Receipt: `microscopes/results/STAGE_INTERFERENCE_V1.json`.
Reproduced in CI by `test_gmi_derivation_witness_reproduction.py`.

Closes the one box left open when section I of the closure checklist was
audited: *derive interference / stability-plasticity tradeoff*. The audit found
it genuinely missing — `GMI_CONSOLIDATION_FORGETTING_THEOREM_V1.md` derives
capacity-forced **forgetting**, which is a different thing from new learning
degrading what is already held.

No learning rule appears anywhere below. CSR-1 says a machine must hold one
state per distinction it is still obliged to tell apart; everything here is
what that constraint alone forces.

```
stability    fraction of OLD distinctions still separated after learning
plasticity   fraction of NEW distinctions acquired
```

## There is a tradeoff only sometimes

| regime | old | new | shared | capacity | must separate | forced to trade |
|---|---:|---:|---:|---:|---:|---|
| A. capacity ample | 4 | 4 | 0 | 16 | 8 | **no** |
| B. capacity binds, new independent | 4 | 4 | 0 | 4 | 8 | **yes** |
| C. capacity binds, new overlaps entirely | 4 | 4 | 4 | 4 | 4 | **no** |
| D. capacity binds, partial overlap | 4 | 4 | 2 | 5 | 6 | **yes** |

**B and C are the pair that matters.** They have *identical* capacity, identical
task sizes, and capacity binds in exactly the same sense in both. They differ
only in whether the new distinctions are already separated by an old one. Only
B is forced to trade.

> **Interference is not caused by capacity being small. It is caused by the new
> distinctions being genuinely new.** A machine learning something its existing
> quotient already separates suffers no interference at any capacity.

That is the same redundancy quantity that decides whether consolidation saves
anything in `GMI_CONSOLIDATION_FORGETTING_THEOREM_V1.md` — regime
`A_independent` against `B_redundant` there, cases B against C here.

## The frontier belongs to capacity, not to a rule

Holding the task fixed at 4 old and 4 independent new distinctions:

| capacity | max(stability + plasticity) | forced |
|---:|---:|---|
| 4 | 1 | yes |
| 5 | 5/4 | yes |
| 6 | 3/2 | yes |
| 7 | 7/4 | yes |
| 8 | **2** | no |

Monotone in capacity, saturating at 2 exactly when capacity reaches the number
of distinctions that must be separated.

> Because no rule enters the derivation, **every rule faces this frontier**. A
> learning algorithm cannot be blamed for interference at a capacity where the
> frontier forbids doing better, and cannot be credited for avoiding it at a
> capacity where the frontier permits both.

This is the standing constraint against which any claimed remedy — replay,
regularisation, parameter isolation — has to be measured. Such a method can
only help by changing one of the three inputs: raising capacity, increasing
redundancy between old and new, or reducing what must still be told apart.

## Interference is exactly the excess

Holding plasticity at 1 (the new task fully acquired):

| must separate | capacity | excess | stability |
|---:|---:|---:|---:|
| 8 | 4 | 4 | 0 |
| 8 | 5 | 3 | 1/4 |
| 8 | 6 | 2 | 1/2 |
| 8 | 7 | 1 | 3/4 |
| 8 | 8 | 0 | **1** |

The stability lost equals the excess over capacity, exactly, at every capacity
checked — the witness asserts this rather than reporting it.

> **Catastrophic forgetting is not a pathology of a learning rule. At full
> plasticity it is the excess of required distinctions over capacity, and it is
> zero the moment that excess is zero.**

## Scope

- Capacity is counted in **distinguishable states**, as in CSR-1. Translating a
  state count into parameters or bits needs a representation assumption that is
  not made here.
- The frontier is over allocations of a fixed capacity. A machine that can
  *grow* capacity is outside this statement, and growing capacity is precisely
  one of the three escapes named above.
- `shared` is treated as known. Deciding which new distinctions an existing
  quotient already separates is itself work, and is not charged here.
- Graded degradation of a retained distinction is not modelled: a distinction
  is separated or it is not.

**Falsifier.** Exhibit a machine that, at fixed capacity with independent new
distinctions, achieves stability plus plasticity above the frontier — or one
that suffers interference when the new distinctions are entirely shared.
