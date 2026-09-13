# The memory-regime partition, derived — checklist item 6

Date: 2026-09-13. Status: **DERIVATION + EXACT WITNESS**. Closes the remaining half of item 6, which the
coverage audit recorded as: *"memory = temporal semantic cut is derived, but there is no derivation of the
working/episodic/semantic/procedural partition, no retrieval policy, no forgetting law as distinct derived
systems."* The forgetting law is now in `GMI_CONSOLIDATION_FORGETTING_THEOREM_V1.md`; this supplies the
partition.

## 1. The partition is not posited — three already-derived conditions each name a different thing to store

| what the accounting says to store | why | regime |
|---|---|---|
| the **retention-equivalence quotient** | CSR-1: exact retention needs `N_t` states, `⌈log₂ N_t⌉` bits, and the quotient theorem makes that the unique minimum | **semantic** |
| **raw experience**, as CSR-1's side channel | when `N_t` exceeds capacity, a distinction not held persistently must be re-derived on demand | **episodic** |
| **compiled sub-quotients** above the PVR-3 threshold | a recurring sequence clears `r > 1 + S/(C−U)` | **procedural** |
| **within-event state**, never persisted | the execution/development cut: state that does not have to cross it is not stored | **working** |

Nothing here is a new posit. Each row is a condition already proved elsewhere in the corpus, and the
partition is what you get by asking *what object* each condition tells you to keep.

## 2. The claim that makes it a partition rather than a relabelling

If these are genuinely distinct regimes rather than four names for one store, they must have **different
growth laws in experience**. They do:

| regime | what sets its size | growth in experience |
|---|---|---|
| **episodic** | one record per obligation encountered | **linear** |
| **semantic** | `⌈log₂ N_t⌉`, and `N_t` stops growing once new obligations are functions of old ones | **sublinear, saturating** |
| **procedural** | count of patterns whose recurrence clears the PVR-3 threshold | **step-wise, threshold-gated** |
| **working** | within-event state only | **constant** |

## 3. Exact witness (`gmi_microscope/memory_regime_witness.py`)

Twelve obligations over 16 histories, complete enumeration. PVR-3 threshold: recurrence > 2.00.

| `t` | `N_t` | semantic (bits) | episodic (records) | procedural (chunks) | working |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 1 | 1 | 0 | 1 |
| 3 | 8 | 3 | 3 | 0 | 1 |
| 7 | 8 | 3 | 7 | 0 | 1 |
| 8 | 8 | 3 | 8 | **1** | 1 |
| 10 | 8 | 3 | 10 | **2** | 1 |
| 12 | 8 | 3 | **12** | 2 | 1 |

Growth over the stream: semantic **1 → 3** (saturates when `N` stops growing at task 3), episodic
**1 → 12** (linear), procedural **0 → 2** (fires at `t = 8` and `t = 10`, only when recurrence clears the
threshold), working **1 → 1** (constant). **Four distinct growth laws, none of which is a rescaling of
another.**

## 4. An instrument correction worth recording

The first run of this witness reported procedural chunks as **0 throughout**, and the partition looked
three-way. The cause was the *stream*, not the theory: it contained no repeated obligations, so the one
condition the procedural regime responds to was absent. A witness that cannot exercise the feature it is
meant to demonstrate proves nothing. The stream now contains recurrence, and the regime fires exactly
where the threshold says it should.

## 5. Scope, and what is deliberately not claimed

**Functional, not anatomical.** These four regimes are forced by the accounting, and they match the
*functional roles* the four biological memory systems are usually given. **No claim is made that they
correspond to any biological structure**, and nothing here bears on checklist items 25–28, which remain
absent.

**Still missing from item 6:** a *retrieval policy* — the partition says what to keep and how each store
grows, not which item to fetch when. That is a decision rule over the charged meter and is the natural
next step, alongside the replay *dynamics* left open by the consolidation theorem.

**Falsifier:** exhibit an experience stream in which two of the four sizes obey the same growth law under
this accounting, or a regime whose size is not determined by the condition assigned to it above. Either
would collapse the partition back to a relabelling.
