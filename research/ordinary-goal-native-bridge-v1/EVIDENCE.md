# Accepted source and authored-control evidence

The [independent review](review/CORE.md) found no blocking defect in the
four modules, donor deltas and retained authored controls.
Its [review identities](review/HASHES.json) and [raw bindings](review/BINDINGS.json)
are copied unchanged. The original [review request](records/ORIGINAL-SOURCE-REVIEW-REQUEST.json)
and [source freeze](records/ORIGINAL-SOURCE-FREEZE.json) retain their original
pending-status text; this current landing page records the later acceptance.

| Generation | Cases | Source | Observations | Process | Child PID | Child wall s |
|---|---:|---|---|---|---:|---:|
| 01 | 8 | [control](source/check_goal.py) | [record](records/qualification-01/CONTROLS.json) | [receipt](records/qualification-01/PROCESS.json) | 2643702 | 0.144272769 |
| 02 | 1 | [control](source/check_revision.py) | [record](records/qualification-02/CONTROLS.json) | [receipt](records/qualification-02/PROCESS.json) | 2648252 | 0.097884402 |
| 03 | 1 | [control](source/check_namespace.py) | [record](records/qualification-03/CONTROLS.json) | [receipt](records/qualification-03/PROCESS.json) | 2652593 | 0.023756702 |
| 04 | 2 | [control](source/check_transport.py) | [record](records/qualification-04/CONTROLS.json) | [receipt](records/qualification-04/PROCESS.json) | 2667710 | 0.105339142 |

These are 8 + 1 + 1 + 2 affected controls across preserved source generations,
not twelve tests rerun on the final source. Each generation's exact source
snapshots and complete pre/post ledgers are in RAW.tar.gz at
original/qualification-NN/source/ and original/qualification-NN/PINS-*.json.
The current authored control files are byte-identical to their executed versions.
[Source mapping](RAW-MEMBERS.json) identifies every original and direct copy.

Generation 01 covers exact arm emission, composite/repeated substitution,
oracle-field refusal, ordered library custody, bounded/UNKNOWN outcomes,
claim binding and native-boundary refusal. Generation 02 covers finite wall,
proof-derived consumption and full-view accounting; generation 03 checks
reserved-label collisions. Generation 04 checks ABC/ABV hint transport and
two scoped members sharing a local essential name with collision refusal.
[Authored inputs](records/qualification-01/AUTHORED-INPUTS.json) and the
[fixture](source/authored_fixture.py) are included.

All four children exited 0 and were reaped. Their historical pre/post pins
and imported paths reconcile. Native-call guards and native-shaped fixtures
are test doubles: zero native calls and no retained cohort/task reads occurred.
The [original qualification](records/ORIGINAL-QUALIFICATION.json) is unchanged.

Child process costs include that process's work; qualifier windows contain
pinning/readback and are nested with child intervals. They are not additive
within a generation and are not acquisition, lifetime or scientific timing
results. Solver counters include syntax, grounding, search, emission and full
library-view decoding; the concrete outer invocation remains unqualified.
Packaging performs only reads, byte copies, hashes and archive recovery checks.
