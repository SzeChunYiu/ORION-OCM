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

## Result

```text
NO_CHEAP_ACQUISITION_AT_THIS_ECOLOGY
```

**None of the three zero-search selectors agrees with the tournament.** All three pick the
same wrong candidate:

| selector | ρ with utility | chose | utility rank | validation saving | acquisition |
|---|---:|---|---:|---:|---:|
| `MDL_COMPRESSION` | **+0.518** | `dec square` | **13 / 16** | −93,883 | 4,608 token ops |
| `COMPRESSION_PER_TOKEN` | +0.269 | `dec square` | 13 / 16 | −93,883 | 4,608 token ops |
| `FREQUENCY` | +0.101 | `dec square` | 13 / 16 | −93,883 | 16 token ops |
| *tournament* | — | `square dec square` | 1 / 16 | **+92,599** | **9,010,526 attempts** |

On the test stratum the difference is not marginal:

```text
square dec square (tournament)   saving  +275,329   13 strict wins, 13 with macro used
dec square        (every scan)   saving  -609,213   30 strict wins, 30 with macro used
```

The cheap choice **helps more tasks and costs far more**, which is the whole finding.

## The mechanism

The failure is an **argmax failure, not a correlation failure**. Compression reaches
ρ = +0.518 against tournament utility — it orders the pool reasonably well on average —
yet the single candidate it ranks first sits at rank 13 of 16. A selector must pick one
candidate, and being right on average is not the same as being right at the top.

Why the top is exactly where it fails: **support is both the benefit proxy every cheap
selector uses and the cost driver the tournament measures.** `dec square` has the highest
support in the pool (28 of 48 training programs), so it compresses best. But a macro token
widens the search frontier on *every* task and repays only on the tasks where it closes.
The fragment that appears everywhere therefore compresses best and searches worst.

The tournament's own winner has support 12 — below the pool median.

Compression scores the benefit term and is structurally blind to the widening cost term.
That is fine when the objective is description length. It is not fine when the objective
is search work, and this ecology separates the two by 884,542 attempts.

## What this buys the programme

Two numbers that bound what cheap acquisition would be worth **if** it existed:

```text
break-even, tournament acquisition      2,136 length-8 tasks
break-even, zero-search acquisition        41 length-8 tasks
```

A 52× reduction in required horizon. That makes the negative more valuable, not less: it
says precisely how much is on the table, and that the standard parent does not collect it.

## Claim boundary

- **#192's numbers are reproduced independently, not quoted.** Recomputed tournament
  acquisition is 9,010,526 = 8,525,253 (16 candidates) + 485,273 (primitive validation),
  and the tournament choice's test saving recomputes to exactly +275,329.
- **The test stratum is no longer naive** — #192 exposed it. The primary result here is
  *selection agreement*, which depends only on the training corpus and is unaffected. Test
  figures are a comparison between selectors on a fixed, already-seen population, never a
  fresh held-out estimate.
- Same-domain polynomial ecology, one candidate pool, one pool cap. A negative here does
  not say compression-based library learning fails generally; it says it fails *as a
  substitute for measured utility when the objective is search cost*, at this ecology.
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
