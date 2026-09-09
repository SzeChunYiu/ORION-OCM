# Recorded costs

| Window | Wall seconds | Scope |
|---|---:|---|
| GNU time | 2.68 | Whole Python process, rounded display; includes startup/final serialization |
| Main | 2.634430219 | Main through post-custody, excluding imports/final RESULT write |
| Native wrapper | 0.984860243 | Nested native invocation through post-custody, excluding final receipt write |
| Library construction | 0.668053015 | Nested existing Library constructor |

The [GNU-time record](records/observation-01/gnu-time.txt) reports 2.57 user seconds, 0.07 system seconds and 166,436 KiB peak RSS. The native wrapper's 143,340 KiB RSS is cumulative process highwater; its difference from final peak is not a measured allocation.

The completed caller, suffix constructor and Library constructor each report two source indexes covering 3,619,117 bytes. Native checking reports two source-index calls, 3,613,830 prefix bytes read, 80,152 source bytes read, and 1,812,202 database bytes both materialized and reread. These counters describe different work stages; they are not interchangeable work units or a full instrumentation claim.

Library snapshot decode counters are zero because no subsequent Library access/query was performed. This does not mean construction, snapshot creation or memory use was free. The retained manifest itself is 3,541,835 bytes.

Nested windows must not be added. Hashing and serialization remain inside the measured process windows where executed; not every internal phase has its own timer/counter. Earlier source preparation, authored controls, reviews, packaging and historical acquisition are outside this native invocation's timing. There is no matched-work performance comparison or lifetime economics result.
