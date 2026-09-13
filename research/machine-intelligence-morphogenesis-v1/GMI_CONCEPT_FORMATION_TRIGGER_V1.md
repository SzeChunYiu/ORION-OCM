# The concept-formation trigger, and where category boundaries fall — item 9 (#592) / I2 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS**. Closes the gap the coverage audit recorded as:
*"this is a necessity/minimality result, not a trigger law — no account of when experiences get compressed
into a named concept, nor of category boundaries."*

Both halves were already proved, separately, and never joined.

## 1. The two halves

**Boundary — the developmental quotient theorem.** Two experiences belong to the same concept iff they
license the same future responses. The coarsest such quotient is the unique minimal exact representation,
so the category boundary is **response-equivalence**, not similarity, not clustering, and not a
free parameter.

**Trigger — PVR-3.** Naming and retaining an abstraction costs `S` once and saves `C − U` per later use,
so it pays iff the class recurs

> **`r > 1 + S/(C − U)`**

**A concept is therefore a retained equivalence class**, and the two halves answer different questions:
the quotient says *where the lines fall*, PVR-3 says *which of those classes are worth naming*.

## 2. Exact witness (`gmi_microscope/concept_formation_witness.py`)

Fifteen experiences over 16 histories, `C = 5`, `S = 3`, `U = 1`, so the threshold is `r > 1.75`.

| class | members | recurrence | named? |
|---|---|---:|---|
| A | 0, 3, 5, 8, 11 | 5 | **yes** |
| B | 2, 4, 7, 9, 10 | 5 | **yes** |
| C | 1, 6 | 2 | **yes** |
| D, E, F | one each | 1 | **no** |

| scheme | cost |
|---|---:|
| no concepts at all | 75 |
| **the triggered set** | **48** |
| naming *every* class | 57 |

## 3. The result that makes it a trigger rather than a licence

**Naming every class costs 9 more than naming the triggered set.** The law does not merely permit
abstraction where it helps — it **actively excludes** abstraction where it does not. Over-abstraction is
penalised, and the penalty is exactly the storage spent on classes that never recur.

That asymmetry is the content. "Compress when you can" would name all six classes and lose 9; the trigger
names three and saves 27.

**Boundary verified exactly:** every within-class pair licenses identical responses, and every cross-class
pair licenses different ones. The quotient is doing the work the theorem says it does.

## 4. An instrument correction

The first run of this witness had **every** class clearing the threshold, so the trigger excluded nothing
and its selectivity was untested — the "name everything" comparison came out identical. The stream had no
class below threshold. Three one-off experiences were added, and only then does the law discriminate.
This is the second witness in this lane to need that fix; a witness must contain the feature it is meant
to test.

## 5. Scope

**Derived:** the trigger and the boundary, jointly, with over-abstraction penalised.

**Not derived:** concept *naming* in any linguistic sense — this is retention of an equivalence class, and
nothing here connects it to a symbol or a communicable label. That link would run through the
compositional-language theorem (item 17) and is not made here.

**Load-bearing assumptions:** PVR-3's own — no invalidation, stable validity, constant costs — plus exact
response-equivalence. Under approximate equivalence the boundary blurs into a rate-distortion choice, the
same relaxation the consolidation theorem flags.

**Falsifier:** an experience stream where naming a class *below* the threshold lowers total charged cost,
or where two response-inequivalent experiences must share a concept for the minimal representation.

## 6. This is the fifth application of one law

`PVR-3` now governs: consolidation against replay (item 7), skill chunking and the shallowness of
hierarchies (item 10), teaching and imitation (item 18), cultural accumulation (item 19), and concept
formation (item 9). The reuse count is respectively later occurrences, contexts, the population,
generations, and **instances of an equivalence class**. One accounting, five cognitive phenomena.
