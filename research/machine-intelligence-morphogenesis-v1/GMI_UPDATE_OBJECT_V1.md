# One update object: learning paradigms as structural restrictions, computed exhaustively

Date: 2026-09-15. Addresses checklist section **C**, box 1 (formal common update object).
Witness: `gmi_microscope/update_object_witness.py`. Receipt: `microscopes/results/STAGE_UPDATE_OBJECT_V1.json`.

Section C's first box is the keystone: without a common update object, "specialization" has nothing to
specialize. The nine boxes after it all depend on this one.

## 1  The object

An update is a total map `U : (state, evidence) → state`. Nothing else — no gradient, no prior, no library.

Over `|S| = 4` states and `|E| = 2` evidence values there are `4^8 = 65 536` such maps, which is small enough
to **enumerate every one**. That is what makes the claims below checked rather than argued.

## 2  Paradigms as predicates

Each paradigm is a structural restriction stated without reference to any implementation:

| paradigm | restriction | matches | of 65 536 |
|---|---|---:|---:|
| additive (gradient-like) | `U(s,e) = s + g(e)` | 16 | 0.02% |
| overwrite (point estimate) | `U(s,e) = h(e)` | 16 | 0.02% |
| insertion-monotone (exemplar/library) | `U(s,e) ⊇ s` | 256 | 0.39% |
| state-only (drift) | `U(s,e) = k(s)` | 256 | 0.39% |
| keep-or-replace (evolutionary) | `U(s,e) ∈ {s, h(e)}` | 841 | 1.28% |
| idempotent-on-repeat (rule induction) | `U(U(s,e),e) = U(s,e)` | 1681 | 2.57% |

Every one is **non-vacuous** and **strictly smaller** than the whole space, and all six are **pairwise
distinct** across 15 checked pairs. A paradigm that matched nothing would be an impossible rule; one that
matched everything would restrict nothing. Both are asserted against.

## 3  The relations are computed, not assumed

> **overwrite ⊂ keep-or-replace ⊂ idempotent-on-repeat**

**Evolutionary selection is a strict special case of consolidation.** That is not a definition — it falls out
of enumerating the space, and it is pinned by name so a change means the computation changed rather than the
prose drifting.

> **additive is DISJOINT from overwrite**

A gradient-like update and a point-estimate replacement share **no** map at all. Revising and replacing are
incompatible in structure, not merely different in spirit.

Eleven pairs overlap partially. Pins assert that containment, disjointness *and* overlap all occur: all-overlap
would carry no information about which paradigm is a special case of which, and no-overlap would make the six
unrelated islands with nothing for "one common object" to explain.

## 4  The object is strictly larger than the named paradigms

Updates matching **at least one** named paradigm: **2 016 of 65 536 — 3.1%**.

**63 520 updates belong to no named paradigm.** Six names do not exhaust learning even on a four-state space.
That gap is the room in which a learning law the corpus has not named would live, and it is measured rather
than hoped for. A pin fails if coverage ever climbs above a quarter of the space.

## 5  What is not claimed

**These predicates are not gradient descent, Bayes, or DreamCoder.** They are the structural signatures those
families share, exhibited on a space small enough to enumerate. Deriving each named algorithm — section C's
boxes 2 through 10 — is not done here, and the containment results say nothing about which algorithm is
resource-optimal in any ecology.

Bayesian updating in particular has **no predicate here**: normalisation needs a numeric state, and a
four-element unstructured state set cannot express it. That absence is a limit of this space, not evidence
about Bayes, and closing it needs a different microscope rather than a broader predicate.

## 6  Scope

Four states, two evidence values, total maps only, exhaustive enumeration, exact arithmetic. Partial updates,
stochastic updates, and updates over structured or continuous state are outside it. The state set is read as
subsets of a two-element set for the insertion-monotone predicate, which is a choice the witness makes
explicit rather than a property of the space.
