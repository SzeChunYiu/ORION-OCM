# Runtime lifecycle continuation V3

This continuation fixes additional gaps found after commit `479e78165fb455481cadcf03fd8e3a99ba79c5af`. It preserves every historical receipt and evaluation file. The earlier V2 report remains the record of the earlier implementation; the data-only recovery contract below supersedes its unconditional cold-restart artifact limitation for the registered data subset.

## Assurance and comparison custody

The previous assurance path could approve a proposal after its target or preserved suite was omitted. Missing resource coordinates counted as zero; impossible success counts and nonpositive sample sizes were accepted. It also trusted a supplied prediction event index, accepted revoked prediction evidence and let a runner mutate the incumbent or the next comparison's task list. These were reproduced before correction.

The current path requires every discriminator, improvement, preservation, unchanged-invariant and declared-regression family in both arms, with positive equal integer sample sizes and integer success counts within the sample. Every budgeted resource coordinate must have an explicit nonnegative finite measurement. Exact Python integers remain valid numeric inputs without a lossy float conversion. Each arm and suite receives independent artifact/task copies.

Prediction receipts now bind the actual admission event, source and payload, the shadow's actual starting ledger head, ordering and current evidence liveness. The M12 phase-G harness now registers this receipt before executing its shadow and checks held-out task identifiers. The legacy digest-only compatibility path remains explicitly labeled weaker; it is not independent custody evidence.

`SelfChangeProposal.fingerprint()` now uses the `ocm.self_change.declarative.v2` schema and binds the complete declared contract, including scope, expiry, target layer, preservation/reopening obligations, development tasks, rollback plan and provenance. Previous fingerprints omitted these fields. This is a declaration binding; callback executable identity remains `HOST_SUPPLIED_UNVERIFIED`.

## Data-only restart recovery

`ocm.selfmodel.rollback_data` registers `ocm.rollback.data.v1`: only exact built-in dictionaries with string keys, lists, strings, integers, finite floats, booleans and null. Tuples, arbitrary instances, callable objects and subclasses are excluded. Limits are 8 MiB encoded data, 100,000 tree nodes and depth 64. There are no object tags, import hooks, code loaders or pickle deserialization.

Before recording completed adoption, the ledger stores an immutable SHA-256-addressed snapshot of the prior artifact, component table, cache and state identity. The adoption event binds its digest, proposal, target and predecessor. Unsupported artifacts retain the explicit `HOST_ARTIFACT_UNAVAILABLE` classification and only their existing process-local recovery path. Missing or changed blobs fail before revocation. A snapshot written before a failed adoption append can remain an unused blob; it does not establish adoption.

Rollback has three distinct facts:

| Stage | Meaning |
|---|---|
| Adoption stamp revoked | Support is withdrawn; this alone does not restore any host state. |
| `rollback()` prepares and returns data | Exact prior data is available, a plain dictionary cache is restored, and a durable preparation record permits idempotent re-delivery after restart. No executable installation is claimed. |
| `acknowledge_rollback_installation()` | The host reports installation, supplying the exact prepared component table and cache. The ledger validates their bindings and records `HOST_REPORTED_INSTALLED`. This is a host acknowledgment, not a proof of executable identity. |

Predecessor rollbacks remain blocked until the successor installation is acknowledged. New adoption is blocked while prepared restoration awaits acknowledgment. Completion records bind the exact adoption evidence, component digest, revoked state at the event and reverse adoption order; incomplete imported records cannot discharge this obligation. An acknowledgment cannot use the adoption stamp's current liveness as a substitute for restoration. The controlled M11/M12 harnesses acknowledge only after exercising the returned restored object and checking its expected controlled result.

Independent review found a flaw in the first uncommitted draft: calling a preparation record "completed" before delivering or installing its result could strand recovery after a crash. The final implementation separates preparation and acknowledgment, retains re-delivery, and refuses custom cache mappings before durable mutation. It does not claim an atomic transaction with arbitrary external host memory or executable systems.

## Validation and remaining scope

- The initial new assurance suite reproduced 18 failures, with one valid restart control. The initial data recovery suite reproduced five failures.
- The final new suites contain **32 passing cases**, including independent-review regressions for delivery recovery, malformed completion metadata, custom cache callbacks, exact host acknowledgment data and large integer resources.
- The broad M2/M4/M11/M12 run completed **205 passing cases** before the last large-integer regression was added; the final 32-case run includes that regression and its correction.
- The independent knowledge/runtime reviewer rechecked preparation, restart re-delivery, LIFO order, cache handling and acknowledgment bindings. Internal review does not replace an external scientific evaluator.

The evidence supports bounded lifecycle correctness. It does not restore the validity of old predecessor fixtures, supply new protected evaluation, recover arbitrary executable host artifacts after restart, certify backend code identity or resolve an external action whose effect occurred without a durable receipt. Such action intents remain durably visible and cannot be silently executed again under the same ID.
