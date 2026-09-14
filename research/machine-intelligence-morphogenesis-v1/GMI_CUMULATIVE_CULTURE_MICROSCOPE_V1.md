# An exact cumulative-culture microscope — I9 (#602)

Date: 2026-09-14. Status: **MICROSCOPE + DERIVATIONS**. Closes four boxes of I9: the cultural ratchet
versus loss, division of cognitive labour, when collective culture exceeds any individual's rediscovery
budget, and the microscope itself. The transmission law it rests on is
`GMI_TEACHING_AND_CULTURE_THEOREM_V1.md`.

Deterministic recursion over expected counts — **no sampling**, so every number is exact given the model.

## 1. The ratchet condition

`n = 5` agents, capacity `K = 8`, pool `M = 40`, 40 generations, swept over transmission fidelity `p`:

| `p` | first six generations | final | outcome |
|---:|---|---:|---|
| 0.03 | 4.00, 3.57, 3.50, 3.49, 3.49, 3.49 | 3.49 | **LOSS** |
| 0.08 | 4.00, 4.36, 4.49, 4.53, 4.54, 4.55 | 4.55 | ratchet |
| 0.15 | 4.00, 5.23, 5.91, 5.29, 5.94, 5.30 | 5.31 | ratchet |
| 0.40 | 4.00, 5.69, 7.25, 7.68, 8.09, 8.46 | 12.58 | ratchet |
| 0.90 | 4.00, 6.00, 8.00, 9.00, 10.00, 11.00 | **40.00** | ratchet, saturates the pool |

**The transition sits between 0.03 and 0.08.** Below it, transmission loses skills faster than derivation
replaces them and the culture decays to a floor set by what each cohort can rediscover. Above it, culture
accumulates — and at high fidelity it saturates the entire available pool.

## 2. Division of cognitive labour, and the ceiling it breaks

A **solo** agent is bounded by its own capacity: `min(K, G·⌊B/C⌋) = min(8, 160) = 8`. Living longer does
not help once capacity binds.

| agents `n` | population capacity `nK` | culture holds | solo ceiling | exceeds? |
|---:|---:|---:|---:|---|
| 1 | 8 | 5.00 | 8 | no |
| 2 | 16 | 5.56 | 8 | no |
| 3 | 24 | 7.51 | 8 | no |
| **5** | 40 | **12.58** | 8 | **yes** |
| 10 | 80 | **39.59** | 8 | **yes** |

> **Division of labour is what breaks the individual capacity ceiling.** No individual can exceed `K`
> however long it lives or how well it is taught. A population can hold up to `n·K`, but only realises it
> when fidelity sustains the ratchet *and* `n` is large enough — here from `n = 5`.

That is the answer to "when does collective culture exceed any individual's rediscovery budget": **not when
transmission is cheap, but when the population's aggregate capacity exceeds one agent's, and fidelity is
above the ratchet threshold.** Both conditions are necessary; `n = 1` with perfect fidelity still cannot
exceed `K`.

## 3. Two corrections recorded

**The first run could not exhibit the effect at all.** It compared a capacity-bounded culture against an
*unbounded* solo baseline (`G·⌊B/C⌋ = 24` with no capacity cap), so culture "failed" to exceed a number no
agent could reach either. It also starved the derivation budget so culture never accumulated past 7. Both
were fixed — the solo baseline is now capacity-bounded and the horizon long enough for accumulation.

**An artifact to flag, not a finding:** at `p = 0.15` the trajectory oscillates (5.23, 5.91, 5.29, 5.94).
That is the integer floor in the derivation term interacting with fractional survival, **not** a predicted
cultural cycle. Reporting it as a dynamic would be wrong.

## 4. Scope

**Derived:** the ratchet/loss threshold in fidelity, the two necessary conditions for collective knowledge
to exceed individual capacity, and a reusable microscope.

**Evidence class:** deterministic expected-value recursion — exact given the model, but a *model*, not the
exhaustive enumeration used for the memory and chunking results. Stochastic transmission would add
variance that this cannot show.

**Assumptions:** uniform skills, capacity as a hard cap, transmission independent across learners, and no
skill-to-skill dependency. Dependent skills would change the ratchet, since losing a prerequisite costs
more than losing a leaf.

**Falsifier:** a fidelity above the threshold where culture still decays, or a population with `n·K > K`
and sustaining fidelity that cannot exceed the solo ceiling.

## 5. I9 status

| box | where |
|---|---|
| inter-agent knowledge transmission | teaching theorem — `n > 1 + S/(C−U)` |
| retention across generations | teaching theorem — per-agent cost → `U` |
| cumulative improvement condition | teaching theorem |
| **cultural ratchet vs loss** | **here** |
| **division of cognitive labour** | **here** |
| **collective exceeds individual budget** | **here** |
| **exact cumulative-culture microscope** | **here** |
| persistent external/social memory as a defined object | partial — treated as the population's held set, not separately formalised |
