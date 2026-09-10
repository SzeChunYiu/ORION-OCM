# G2 acquisition economics — can a scan replace the tournament?

**Status:** research-only / no production change / no ML / no routing change.

## Why

#192 established bounded causal macro reuse and, in the same receipt, why it cannot pay
for itself:

```text
selected path through test   12,520,017 enumeration attempts
test saving vs primitive        275,329
```

Acquisition is ~45× the thing it buys, and **8,525,253** of those attempts are a single
protocol line: run all sixteen frozen candidates over all thirty-two validation tasks and
keep the best. That is a *utility tournament*, and a tournament costs a full search per
candidate.

The library-learning parents do not pay that. DreamCoder and Stitch pick an abstraction by
**compression over the training corpus** — a scan, not a search. #192's own closing note
names attacking acquisition cost as the next step. So this study asks the question those
parents raise:

> Does a zero-search selector, reading only the training programs #192 had already solved,
> choose the same macro the tournament chose?

## Result — the first negative, then its overturning

**v1 answer: `NO_CHEAP_ACQUISITION_AT_THIS_ECOLOGY`.** None of the three zero-search
selectors agreed with the tournament; all three picked the same wrong candidate.

**v2 answer: `CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE`.** A fourth
selector, derived from the diagnosis of the first negative, picks the tournament's macro
exactly — at zero enumeration attempts.

| selector | ρ with utility | chose | utility rank | acquisition |
|---|---:|---|---:|---:|
| `FREQUENCY` | +0.101 | `dec square` | 13 / 16 | 16 token ops |
| `COMPRESSION_PER_TOKEN` | +0.269 | `dec square` | 13 / 16 | 4,608 token ops |
| `MDL_COMPRESSION` | +0.518 | `dec square` | 13 / 16 | 4,608 token ops |
| **`SEARCH_AWARE`** | **+0.531** | **`square dec square`** | **1 / 16** | 4,608 token ops |
| *tournament* | — | `square dec square` | 1 / 16 | **9,010,526 attempts** |

```text
square dec square (tournament and SEARCH_AWARE)   test saving  +275,329
dec square        (every compressor)              test saving  -609,213
```

## Why compression fails and what fixes it

The failure was an **argmax failure, not a correlation failure** — and the fix proves it
from the other side. `SEARCH_AWARE`'s correlation is barely different from compression's
(+0.531 against +0.518) while its argmax moves from **rank 13 to rank 1**. Fixing an argmax
needs the right *term*, not a better fit.

The missing term is **grammar widening**, and it needs no search at all. A token word with
`m` macro tokens and `d − m` primitives expands to `m·L + (d − m)` primitives, so the number
of valid words at each depth is a sum of binomial terms — closed form:

```text
depth-7 word count, 4 primitives, budget 7
  primitives only          21,845
  + a length-2 macro       30,348      (+39%)
  + a length-3 macro       23,451       (+7%)
  + a length-4 macro       22,158       (+1%)
```

A macro token widens the search at **every** depth and repays only where it closes. Short
frequent fragments compress best and widen most — `dec square` has the pool's highest
support (28 of 48) and costs +39% width for a 1-token saving per firing. Compression scores
the benefit term and is **structurally blind** to the width term. Adding it is arithmetic.

## What this buys the programme

Two numbers that bound what cheap acquisition would be worth **if** it existed:

```text
break-even, tournament acquisition      2,136 length-8 tasks
break-even, zero-search acquisition        41 length-8 tasks
```

A 52× reduction in required horizon — and `SEARCH_AWARE` **collects it**. Acquisition at
this ecology is a scan, not a search. The standard library-learning parent does not reach
it; a parent that prices its own search width does.

## Claim boundary

- **#192's numbers are reproduced independently, not quoted.** Recomputed tournament
  acquisition is 9,010,526 = 8,525,253 (16 candidates) + 485,273 (primitive validation),
  and the tournament choice's test saving recomputes to exactly +275,329.
- **The test stratum is no longer naive** — #192 exposed it. The primary result here is
  *selection agreement*, which depends only on the training corpus and is unaffected. Test
  figures are a comparison between selectors on a fixed, already-seen population, never a
  fresh held-out estimate.
- Same-domain polynomial ecology, one candidate pool, one pool cap. This does not say
  compression-based library learning fails generally; it says compression alone is the
  wrong objective when the cost being optimised is **search work**, and that the correction
  is cheap and closed-form.
- **The withdrawn negative is the more useful record.** v1 concluded no cheap acquisition
  exists. That was never established — what was established is that the three selectors
  tried were inadequate. A negative of the form *"no cheap X exists"* is only ever *"no
  cheap X that was tried"*, and this study is a worked example of the difference.
- No OCM-specific claim of any kind. Every arm is a conventional parent.
- #192's frozen populations, candidate pool, search index, expansion rule and attempt
  accounting are **imported from its module**, not reimplemented, so the comparison cannot
  drift from the incumbent.

## Files

```text
experiment.py     three zero-search selectors, the recomputed tournament, the analysis
test_protocol.py  23 hostile tests
```

The tests attack the *selectors*, not the conclusion — a silently broken compression score
would manufacture exactly this negative. They caught two real defects while being written:
a rank correlation that scored a constant vector at 1.0 (the real scores contain a
three-way tie, so tie handling decides the number rather than decorating it), and an
overlap-counting rewriter that would have inflated compression for self-overlapping
fragments — precisely the short repeated fragments under test.
