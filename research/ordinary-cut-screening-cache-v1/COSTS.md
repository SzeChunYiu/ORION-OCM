# Accounting and scope

The original control window was 0.13292637298582122 seconds wall, 0.121942 user seconds, 0.008128999999999999 system seconds and 41,364 KiB peak RSS. The three affected controls recorded 0.09626499196747318 seconds wall, 0.08795 user seconds, 0.007995 system seconds and 41,264 KiB RSS. Both windows are Popen through log closure/wait4; source/import custody and observer setup/serialization are excluded. Different control populations make these unsuitable as a speed comparison.

The cache interface separates requests, hits/misses/entries, bypasses and refusals. Key/proof payload lengths and canonical snapshot bytes are logical storage measures; resident Python overhead is not equal to them and remains visible through process RSS. No eviction is implemented.

Actual parser work advances only on a miss computation. A hit does not recharge its historical parser duration. Request, miss-computation and management timers are nested attribution windows, not independent costs to add. Post-computation refusal retains its incurred parse time; prelookup refusal records no parser invocation.

The corrected wording is precise: `cache_returned_proof_labels` counts successfully returned proof-list labels. Copies built and discarded after a deadline are excluded from that counter; request/management wall includes their work. The original counter implementation is unchanged. Internal Earley chart operations and interrupted label work remain uninstrumented.

A future actual attempt must retain both prior attempts' full cost history and charge new cold preparation, lookup, materialization and storage. This source capsule contains no such attempt, actual speedup or lifetime-cost result. [Original accounting record](records/original/COSTS.md) · [successor clarification](records/current/README.md)
