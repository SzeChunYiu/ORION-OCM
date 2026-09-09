# G3.3 representation improvement · G3.4 insufficiency diagnosis

**Status:** research-only / no production change / no ML / no routing change.

Converts the remainder of #165's `G3` from unmeasured.

## What a representation is here

A **state abstraction used to prune search**. In prefix-extending BFS, two prefixes with
the same abstract state are treated as interchangeable and only one is extended. Under
`EXACT` that is de-duplication; under anything coarser it is a *bet*, and the bet is what
this study prices.

Registered before any protected outcome:

| representation | state | expectation |
|---|---|---|
| `EXACT` | full coefficient tuple | sound by construction — the reference |
| `DEGREE` | degree only | coarse, expected misleading |
| `LEADING` | degree + leading coefficient | intermediate |
| `PARITY` | coefficients mod 2 | coarse, expected misleading |
| `MOD_997` | coefficients mod 997 | a hash; collides rarely |
| `TRUNCATED_3` | degree + three lowest coefficients | feature truncation |

`EXACT` is the reference, **not a candidate** — selecting it would make the study vacuous,
and a test enforces that selection ranges only over coarser candidates.

## Result

```text
REPRESENTATION_PRIOR_DOMINATES
```

| | fits training | later saving | sound later |
|---|:--:|---:|:--:|
| `EXACT` (reference) | — | — | — |
| `MOD_997` **(selected)** | ✓ | **0** | ✓ |
| `TRUNCATED_3` | ✗ (loses 2/10) | — | — |
| `DEGREE` / `LEADING` / `PARITY` | ✗ (lose 10/10) | — | — |

Selected representation saves **0** extensions against a charged discovery cost of 60.

### The mechanism, which is the actual finding

`MOD_997` is sound and *behaviourally identical* to `EXACT` — it never collides at this
scale, so it merges nothing and saves nothing. Meanwhile every representation coarse enough
to merge anything destroys solutions outright (`DEGREE` cuts extensions from 19,179 to 280
and solves 0 of 10).

That gap is the result: **in this domain the coefficient tuple is very nearly a bijection
with the program prefix, so the exact state space has almost no redundancy for a coarser
abstraction to merge.** A representation can only pay where equivalent states are actually
revisited, and here they are not. There is no useful middle between "identical to exact"
and "unsound".

## G3.4 diagnosis

An unsolved task is diagnosed by **re-running under changed conditions**, never by guessing
from the failure:

```text
solved under EXACT at the same budget    -> REPRESENTATION_INSUFFICIENT
solved under a larger budget             -> SEARCH_MORE
solved only with the macro operator      -> MISSING_OPERATOR
frontier exhausted, nothing above works  -> RESOURCE_BOUND
otherwise                                -> CANNOT_CHECK
```

#165 states the rule: *"Timeout alone cannot license JUMP."* Here that means an exhausted
budget maps to `RESOURCE_BOUND`, and `REPRESENTATION_INSUFFICIENT` may only be returned on a
**positive re-run** — `EXACT` solving the same task at the same budget — never on an
absence. A test asserts the ordering in the source.

Observed on this population: `SEARCH_MORE`.

## Invalidation, which G3.3 asks for by name

*"Invalidate representation when a newly admitted operator distinguishes previously
equivalent states."* Directly executed: #192's macro `square → dec → square` is admitted
into the grammar and the selected abstraction is re-checked against `EXACT`. Not triggered
here — consistent with `MOD_997` merging nothing in the first place.

## A prior version, kept

v1 registered only `EXACT`/`DEGREE`/`LEADING`/`PARITY` and returned
`CANNOT_CHECK_NO_COARSER_REPRESENTATION_FIT_TRAINING`: all three coarse candidates lose
solutions on *training*, so none was ever selected. `MOD_997` and `TRUNCATED_3` were added
on **training evidence only** — which G3.3 explicitly permits ("learn/select representation
from valid evidence") — with no protected later outcome consulted for either.

## Boundary

Same-domain polynomial ecology, one grammar, budget 6, 10 training and 10 later tasks. The
finding is about *this* state space's redundancy; a domain where search genuinely revisits
equivalent states could give the opposite answer, and this study says nothing about that.
