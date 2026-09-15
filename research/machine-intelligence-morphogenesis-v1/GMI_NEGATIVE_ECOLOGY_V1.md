# A negative ecology for every learning law — constructed, and one result that containment does not explain

Date: 2026-09-15. Addresses checklist section **C**, box 12 (*for each law, construct a negative ecology where
it loses*).
Witness: `gmi_microscope/negative_ecology_witness.py`. Receipt: `microscopes/results/STAGE_NEGATIVE_ECOLOGY_V1.json`.

Because `GMI_UPDATE_OBJECT_V1` makes paradigms subsets of one enumerated space, "loses" becomes computable
rather than rhetorical: a task on which a paradigm's **best member** scores below another paradigm's best.

## 1  The ecology

Evidence sequences of length 2 over `{0,1}` — four of them. Every update runs from a fixed initial state and
yields a **behaviour**: a 4-tuple of final states. A **task** is a required behaviour, one of `4^4 = 256`. A
paradigm's score is the best match any member achieves, 0–4.

## 2  Every law loses somewhere

| law | loses on |
|---|---:|
| state-only | 218 of 256 |
| additive | 190 |
| overwrite | 182 |
| insertion-monotone | 82 |
| keep-or-replace | 78 |
| idempotent-on-repeat | 32 |

Each with an **exhibited** task, not just a count — e.g. `additive` scores 2 on task `[0,0,1,1]` and is beaten
by `insertion-monotone` at 3.

Pins assert every law loses **somewhere but not everywhere**: a law that never lost would dominate the space
and make the box unsatisfiable for it, and a law that always lost would be a different and much weaker claim
than the box asks for.

## 3  Three laws are never *uniquely* best

| law | uniquely best on |
|---|---:|
| idempotent-on-repeat | 20 of 256 |
| insertion-monotone | 18 |
| additive | 14 |
| **overwrite** | **0** |
| **keep-or-replace** | **0** |
| **state-only** | **0** |

For two of them there is a theorem: **a paradigm strictly contained in another can never be uniquely best**,
because whenever it is optimal its superset holds the same member and ties. `overwrite` is strictly inside
both `idempotent-on-repeat` and `keep-or-replace`; `keep-or-replace` is strictly inside `idempotent-on-repeat`.
The witness asserts the implication holds for every contained law, so containment and uniqueness are checked
against each other rather than assumed consistent.

## 4  The case the theorem does not cover

**`state-only` is never uniquely best and is contained in nothing.**

Its zero has no explanation here. It is reported as unexplained and pinned as such, because folding it in with
the other two would hide the only thing in this microscope that is not understood. A plausible reading is
that a law ignoring evidence entirely is always *matched* by some evidence-using law that happens to agree —
but that is a conjecture, and this witness does not test it.

## 5  Scope

Length-2 evidence sequences from one fixed initial state, four states, exhaustive over all 256 tasks and all
65 536 updates. A law losing here is a **constructed instance**, not a claim that it loses in general, and
"best member" is best on the task rather than cheapest — **no cost is charged in this microscope**, so these
are capability comparisons and not resource-optimality comparisons.

Section C's box 11 (*assumptions under which each law is resource-optimal*) therefore remains open: it needs
the cost coordinates, and this microscope deliberately has none.
