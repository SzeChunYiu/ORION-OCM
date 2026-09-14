# Machine species: the definitions, proved rather than asserted

Date: 2026-09-14. Addresses checklist section **G**, boxes 1–6.
Witness: `gmi_microscope/species_algebra_witness.py`. Receipt: `microscopes/results/STAGE_SPECIES_ALGEBRA_V1.json`.

Section G opens with six boxes of the form *"define X"*. A prose definition closes none of them, because
each name carries a claim: **"equivalence relation"** asserts reflexivity, symmetry and transitivity;
**"distance"** asserts identity of indiscernibles, symmetry and the triangle inequality. Those are checkable
by exhaustion on a finite descriptor space, and this document reports them checked.

## 1  The split that does the work

Section G's descriptor is taken as given and divided in two:

| | components |
|---|---|
| **organizational** | state carrier, native operators, control law, update law, memory organization, communication, verification, development law |
| **non-organizational** | resource profile |

**That split is the theory.** It is what makes species identity survive a compiler or substrate change,
because a substrate change moves the resource profile and nothing else. If the split were wrong, recompiling
would speciate — so the witness *checks* substrate invariance rather than assuming it.

The space: 8 binary organizational components (256 descriptors) × 3 resource profiles = **768 descriptors**.
Everything below is exact and exhaustive over that space.

## 2  Species equivalence — checked, not asserted

| axiom | result |
|---|---|
| reflexive | ✔ over 768 descriptors |
| symmetric | ✔ over 589 824 ordered pairs |
| transitive | ✔ |

768 descriptors partition into **256 species**. A pin fails if that partition ever becomes trivial — one
species, or all singletons — since either way the relation would carry no information.

## 3  Within-species variation

Every species has exactly **3** members, and the only dimension that varies within one is the **resource
profile**. Nothing organizational varies inside a species — asserted, because if it did the equivalence would
be misdefined.

## 4  Morphological distance is a metric

Hamming distance on the organizational components.

| property | result |
|---|---|
| symmetry | ✔ |
| `d(x,y) = 0` exactly when conspecific | ✔ |
| triangle inequality | ✔ over **16 777 216** triples |

Distance takes the values **0…8**, so it orders morphologies rather than merely separating them.

## 5  Identity under compiler / substrate change

**2304** substrate changes attempted; **0** changed the species. This is true by construction *and* verified —
the verification is what makes the organizational split falsifiable rather than definitional bookkeeping.

## 6  The speciation threshold is sharp

| | distances |
|---|---|
| within a species | `[0]` |
| between species | `[1, 2, 3, 4, 5, 6, 7, 8]` |

The two sets are **disjoint**, so the threshold is exactly **1** and it is sharp: no distance is attained both
within and between species. *"How far must development diverge before it is a new species"* has an exact
answer rather than a tuned cutoff. A pin fails if the sets ever overlap.

## 7  Hybridization, and the confinement law

A composition is a **new species** exactly when its organizational descriptor equals neither parent's. Over
all 16 711 680 crossovers: **13 483 520** produce a new species, **3 228 160** reproduce a parent. Both
outcomes occur, so the criterion separates cases rather than labelling them all alike.

**The real limit is per pair, and stating it pooled would be a mistake.** Pooled over all parent pairs,
crossover reaches all 256 organizational descriptors — a number that says nothing. Per pair:

> **Parents at morphological distance `k` reach exactly `2^k` children.**

Verified for every `k` from 1 to 8: `{1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128, 8:256}`.

So a hybrid **never leaves the subcube spanned by where its parents disagree**. Composition *recombines*; it
cannot introduce a component value that neither parent had. Novelty beyond the parental subcube requires
something other than composition — which is a constraint on how new species can arise at all, and it is the
part of this section with predictive content rather than definitional content.

## 8  Scope, and what is not claimed

The algebra is proved on an abstract descriptor space: 8 binary organizational components and 3 resource
profiles. Real families have components with more than two values, and the proofs are stated for the space
actually enumerated — the metric and equivalence arguments carry over to larger alphabets unchanged, but that
extension is argued, not enumerated here.

**Nothing in this document classifies the corpus's own families.** It establishes that the section-G
definitions have the properties their names claim. Boxes 7–16 of section G — niche occupancy, coexistence,
competitive exclusion, symbiosis, resource partitioning, abundance, morphology transitions under repricing,
invasion, extinction, and multi-species ecologies — are untouched, and none of them follows from this algebra
alone: they need an ecology, which this does not supply.
