# Recorded costs

[Counts and costs](review/outcome/COUNTS.json) retain the exact floating values;
[child/observer](records/observation-01/PROCESS.json) and [caller](records/caller-01/PROCESS.json)
receipts define the process windows.

| Window | Seconds |
|---|---:|
| Driver | 55.570827 |
| Screen child | 55.650049 |
| Observer | 55.740074 |
| Caller | 55.764397 |

These windows are nested and must not be added. The driver starts before its
request/source/input reads; repeated history reads and fresh cache construction
are charged. Outer setup, authoring, review and packaging are not a complete
lifetime cost. Fresh process/cache construction does not mean OS cache eviction.

Child CPU: 55.595482 s user and 0.044005 s system. Peak RSS: 102,056 KiB,
for the process as a whole, not the cache alone.

Current cache requests cost 42.405149 s: 15.168265 s compute plus 27.236884 s
management. Parse/emission (16,178 calls; 15.093649 s) is nested in compute.
Grammar construction was 0.143558 s; library preparation was 0.094916 s.
These overlapping counters are not additional independent wall windows.

Logical storage telemetry records 21,608 entries, 363,757 stored key tokens,
2,923 stored proof labels, a 1,729,292-byte serialized library snapshot and an
82-byte context key. It does not measure full Python object or lifetime storage.
The 1,085,595 returned proof labels count successful returns; discarded copy-out
work remains in wall time. Aggregate telemetry has no per-key content/query log.

The earlier uncached screen completed 4 rows and left 72 UNKNOWN in 60.004043 s;
this cached attempt completed 76 in 55.570827 s. Its fresh parser work was lower,
but completed work differs. This single pair does not estimate matched-work
speedup, general reliability or lifetime advantage.

The original opportunity driver (0.377159 s), first screen and their complete
outer/caller/work records remain unchanged inside the result and in the exact
[upstream archive references](UPSTREAM.json). Prior preparation and partial
attempts have not been erased or silently counted as zero.
