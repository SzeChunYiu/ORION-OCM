# Developmental reachability: representable is not reachable, and the gap has an exact size

Date: 2026-09-15. Addresses checklist section **E**, boxes 1–5 and 8.
Witness: `gmi_microscope/reachability_witness.py`. Receipt: `microscopes/results/STAGE_REACHABILITY_V1.json`.

Section E's premise is that optimality is not enough — the theory must say whether development can *find* the
predicted form. Its opening boxes ask for formal definitions, and a definition is a claim about structure, so
each is **proved by exhaustion** rather than stated.

## 1  The setting

Morphologies are the 8-bit organizational descriptors of `GMI_SPECIES_ALGEBRA_V1` — **256** of them. A
**developmental law** is a set of operators, each flipping a fixed subset of coordinates.

| | |
|---|---|
| **representable** | the descriptor exists in the space — always 256 |
| **reachable** | connected to the start under the law's operators |

## 2  The law

Applying an operator adds its flip-vector mod 2, so the reachable set is the coset
`start + span_GF(2){flip vectors}`. Therefore:

> **|reachable| = 2^rank**, and a target is reachable **iff** `target XOR start` lies in the span.

**The algebra predicts and exhaustive BFS confirms** — the two are computed independently and an assertion
fails if they disagree:

| developmental law | rank | predicted | BFS reached | burden |
|---|---:|---:|---:|---:|
| single-coordinate | 8 | 256 | **256** | 0 |
| paired-coordinates | 7 | 128 | **128** | 1 |
| first-half-only | 4 | 16 | **16** | 4 |
| all-or-nothing | 1 | 2 | **2** | 7 |
| paired + one single | 8 | 256 | **256** | 0 |

That gives section E three of its definitions at once, exactly rather than approximately: **developmental
reachability** is coset membership, **morphology-search burden** is `8 − rank` (the number of dimensions the
law cannot move), and the **sufficient condition for reaching a morphology** is that the difference lies in
the span.

## 3  Representability is not reachability

**Three of the five laws reach strictly less than the representable space** — 128, 16 and 2 of 256.

A morphology can be **representable, optimal, and still unreachable**. That is the separation section E
exists to make, and it now has instances rather than an argument. Pins assert that *some* law reaches
everything and *some* does not: without the first, unreachability could not be attributed to the law rather
than to the space; without the second, the separation would have no instance.

## 4  Local barrier versus global impossibility

Target: flip coordinate 0 only.

* **Reachable** under single-coordinate, first-half-only, paired + one single
* **Unreachable** under paired-coordinates, all-or-nothing

Unreachable under one law and reachable under another is a **local barrier** — a property of the
developmental law, not of the target. Global impossibility would require unreachability under *every* law,
and no target here has that.

**That is the finding, not a gap in it**: what looks like impossibility is usually the search. A theory that
reported "morphology X cannot arise" from one developmental law would be reporting a fact about its own
operator set.

## 5  Adding one operator restores reachability

| | rank | reaches |
|---|---:|---:|
| paired-coordinates | 7 | 128 |
| **+ one single-coordinate** | **8** | **256** |

One added operator raises the rank by exactly one and takes reachability from half the space to all of it.
**Search burden is a property of the operator set and is repairable by enlarging it** — which is what makes
section E's box 8 (*added operators restore reachability*) a constructive claim rather than a hope.

## 6  Scope

One descriptor space, five developmental laws, exact GF(2) arithmetic and exhaustive BFS — no sampling. The
result is about operator sets that flip fixed coordinate subsets; a law whose operators depend on the current
descriptor is not covered, and the coset argument would not apply unchanged to one.

Section E's remaining boxes — comparing generic searchers, charging failed-candidate cost, neutral recovery of
four morphology families, cross-search and cross-grammar replication, and the search-negative terminal — are
**not** addressed here.
