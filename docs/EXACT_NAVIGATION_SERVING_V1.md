# Exact navigation serving: bounded engineering result

The serving path accepts a matrix-free result only when its rational residual is
exactly zero, then otherwise uses the unchanged dense solver. On one authored
128-row comparison, C process wall fell from **71.894 s to 17.522 s** (4.103×).
All 128 paired answers and normalized decision traces matched. This measures a
serving improvement against the previous OCM implementation.

## Mechanism and compatibility

[The serving helper](../src/ocm/runtime/navigation_serving.py) uses the existing
[exact matrix-free matvec](../src/ocm/kso/navigation_matrix_free.py).
Two restart steps form a candidate; a third matvec checks its exact residual.
Ordinary nonnegative rational weights, frozen structural denominators and
0 < alpha <= 1 make the supported operator substochastic with a unique fixed
point. A zero residual therefore identifies the dense reference result.
The attempt assumes neither an acyclic graph nor finite-step convergence.

Eligibility is restricted to plain supported object/weight/seed/evidence types
and relevance=None. Other inputs go directly to the reference, preserving
stateful relevance evaluation. Seed validation follows warrant gating, without
renormalizing. Nonzero residuals, however small, and failed attempts fall back.
The existing dense API, including its explicit matrix argument, is unchanged.

[The runtime](../src/ocm/runtime/solve.py) computes WARRANTED and EXPLORATORY query
and uniform-background vectors separately. No operator is cached or shared across
those calls. Ranking, tie order, liveness, refusals and answer authority remain
the same. The intervention adds no scalar-hoist or direct-routing policy.

## Observed comparison

The same retained authored A and 128-row C arrays ran through both actual project
trees, with separate source-bound acquired stores. Both A calls selected the same
one-rule library. Call order was A-dense, A-serving, C-dense, C-serving, with the
same pinned Python 3.11.14 and observed CPU affinity [0]; no profiler was used.

| C observation | Dense | Exact serving |
|---|---:|---:|
| Process wall, launch through reap and stream persistence (s) | 71.894384389 | 17.521761028 |
| Waited child user + system CPU (s) | 66.188918 | 11.672020 |
| Retained post-C store bytes | 3,574,526 | 4,280,531 |
| Parent completions | 64 | 64 |
| Evaluated rows | 128 | 128 |

The added diagnostics increased retained store size by 706,005 bytes (19.75%).
Readback checked 256 rows in total: 128 paired identities, answers and normalized
traces. Normalization excludes the new diagnostics and source-specific evidence
IDs. Shared semantic, checking, preparation, matching, index and dispatch work
matched. All 512 serving fixed-point calls had exact zero residual: 1,536 matvecs
and zero dense fallback calls. Cyclic fallback is qualified by separate controls.

The encompassing four-child observation was 91.14 s wall, 76.71 s user and
2.69 s system CPU, with 80,160 KiB maximum RSS. Per-child and service/solve spans
are nested; they must not be added to that outer observation. Preparation of this
comparison and subsequent review are outside it. One fixed-order pair establishes
neither general speedup nor lifetime economics, learning benefit, local execution,
superiority over an equally adaptive symbolic parent, or novelty.

## Accounting and qualification

exact_navigation covers FOUR_FIXED_POINTS_ONLY, with explicit whole-field
eligibility/index/denominator atom, edge and tail work, completed incidence counts,
restart/residual entries and fallback calls. Target-specific N.navigate calls
remain outside this detail and are counted separately. The historical
ResourceVector proxy is preserved; it is not a measured arithmetic total.
Fraction/warrant internals and dense internal arithmetic are not instrumented.
Failed partial matvec work is explicitly unavailable; completed attempt work stays.

The focused serving qualification passed 58 controls: 33 new and 25 inherited,
including exact equivalence, both modes, weighted conjunctive/dangling cases,
tiny nonzero residuals, cyclic fallback, gated invalid raw seeds, stateful
relevance, reused counters, actual OCM calls, revocation and cold restart.
The recorded engineering gates passed 133 focused and 1,336 full tests with zero
failures/errors/skips. Both M1 and M2 receipt --verify commands passed.
[The current selector](provenance/engineering_revisions/CURRENT_ENGINEERING.json)
binds the new 357-file source archive and immutable gate records; historical
scientific receipts remain unchanged.

## Evidence identities

External raw records remain under /home/billy/orion-director-work/20260908/:

- exact-navigation-serving-qualification-v1/HANDOFF.json:
  4a6821e888355cc87be21b35324934624baffe675d8b6a140e3547c3bf9823fa.
- exact-navigation-serving-qualification-v1/ENGINEERING-READBACK.json:
  25865b859a6bda355c9f5b37c85c6e0d352af5897e4b07109635791807fa9db3.
- exact-navigation-root-review-v1/REVIEW.json:
  20e61dda998de45c24c9626553eca6c699c5b2b4ece56eadad8f147b3abfa573.
- exact-navigation-comparison-v1/readback-v1/READBACK.json:
  45cb5f1dad9a7931130630684488fc8d3f1b6f612b7137ef8ae06b6d8ac71325.
  It binds the original four PROCESS records and the observed source map.

Dense source: f07c68e2c980f7b183d066107e7ba470f7b10438,
tree 3ceba538349bdb2c1f6aa8039ba69bae7f310d38.
Qualified serving source: 3543051e732aa54555183c4eb4e3a71dedfb6057,
tree a60133261187fb6683b572149b746be92529358e.
Broader engineering source ID:
e5f7c5c40b64f09f3538ecf4fc33ed3f8fd77129d454c50f52bfb14878c1a628.

A separate next question is whether navigation earns its cost when a task already
has one complete applicable checked route. A sufficient direct router would be a
different policy intervention; it is not implemented here.
