# Exact syntax memoization: prospective engineering successor

The completed first screen spent 58.962805 seconds in parse/emission within its
60.004043-second driver interval. Cold grammar construction was 0.077325 seconds.
This attribution comes from retained records supplied by root; it is not a new run.

[Python functools.cache](https://docs.python.org/3.11/library/functools.html) supplies
the mature exact-key primitive. It retains arguments/results and exposes hit/miss/entry
counts. The installed 3.11.14 source and binary are pinned; authored controls check the
actual wrapper's exception behavior. No custom eviction algorithm is introduced.

[Lark's cache option](https://lark-parser.readthedocs.io/en/stable/classes.html#lark.Lark)
stores LALR grammar analysis. It does not memoize the repeated Earley syntax requests
measured here. The existing four syntax modules, matcher and screen remain unchanged.

Each pool owns a detached canonical full-P1 snapshot and read-only matcher view.
Each exact parameter descriptor owns one persistent Context and functools cache.
The callable is private to that immutable library/context; its key is exact wanted type
plus original token tuple. The reported namespace digest is identification, not a
cross-pool lookup: distinct pools never share entries.

Only proved structural syntax or completed supported nonmembership returns normally
from the cached callable. UNKNOWN raises an internal non-ValueError exception before
a cache return. It is never stored, never converted to a negative type result.
A proved witness remains reusable under incomplete grammar without claiming coverage.
Cache payloads are tuples; every returned proof is a fresh list.

Check the shared deadline before lookup and after materialization, including hits.
A value may remain logically valid in the cache after a deadline refusal, but no proof
is returned for that refused request. No warm historical parse time is charged again.
The wrapper is explicitly single-threaded; functools's internal thread safety does not
make the surrounding counters a concurrent serving API.

The cache is unbounded within this finite registered attempt and released with its
context/process. Record retained entry/key-token/proof-label counts, namespace bytes
and process RSS. No claim is made that this policy is suitable for an unbounded service.

All76/order/full4323P1 and2,000,000 matcher states/60seconds/512tokens/4096proof labels
remain unchanged. A future attempt must retain both original audit and first60-second
screen costs. This conventional-parent improvement is not a novelty or acquisition claim.
