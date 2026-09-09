# Conventional memoization and its boundary

The prototype adopts Python 3.11.14 `functools.cache`. The installed source/binary identities and the distinction between the Python fallback read and the accelerated wrapper exercised by authored controls are recorded in [SOURCE-READS](records/original/SOURCE-READS.json). It introduces no custom cache or eviction algorithm. Lark's separate grammar-analysis cache does not memoize these Earley syntax requests.

Each pool owns a detached canonical full-parent snapshot and read-only matcher view. One private callable per exact parameter descriptor binds the library/context; exact requested type and token tuple form its lookup key. The namespace digest identifies that scope and does not enable cross-pool sharing.

Only completed structural syntax proofs or supported nonmembership are cacheable. UNKNOWN raises an internal exception before a successful cache return. Valid positive witnesses remain usable under incomplete grammar without establishing complete coverage. Proof lists and exposed metadata are copied on return.

The original uncacheable branch returned the engine's mutable unsupported-contract list. Caller mutation could change fixed-context coverage and make a repeated refusal look like complete nonmembership. The [one-line repair](PATCH.diff) rebuilds the result dictionary and decodes that list from the Context's frozen JSON. Cached payload, status, proof, deadline and accounting behavior are otherwise unchanged.

Deadline checkpoints run before lookup and after materialization, including hits. A cached logical result may survive a deadline refusal, but that refused request returns no proof. The surrounding wrapper/counters are single-threaded. Its unbounded cache is scoped to a finite attempt and released with its context/process; this is not an unbounded-serving policy.

The nine other current source files are unchanged from the initial cache prototype. The matcher, screen and reviewed syntax sources remain exact inherited components. This is conventional parent engineering, not an acquired method or a new algorithm.
