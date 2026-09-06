# Contract, repairs and custody

## Fixed scope

The three quoted-v2 public requests remain byte-identical: implicit primitive,
explicit primitive, full manual macro. Each retained native 5,000 ms, outer
20 s plus 2 s kill grace, CPU 0 and 4 GiB address space. The forced route is not
assigned here. The existing supervisor has a 24 s emergency watchdog.

Executed source was frozen at b03b74905a331bf40af16f1531bb5f2b58821ba2.
Publication starts from main 131c55d5a4954f316963dadd64d134b0b12e3581;
the trees were identical before these additive evidence files. No core,
worker or environment was changed during publication.

The observer records parse, metadata, invoke, statistics collection and
serialization separately in flushed JSONL. Command outputs, native stderr and
markers are separate. Requested native tags add options-auto, sygus-grammar
and sygus-enumerator while preserving sygus-sol-gterm.

## Preserved corrections

V4 preparation retains seven initial stub controls and two actual native setup
failures: getOption(output) is ungettable, and getCommandName rejects a null
command. The final recorder labels the output getter unavailable and checks
isNull first. Seven final stub controls and exactly three native setup commands
then pass, including full internal/defaulted statistics and clean EOF.

The registered V4 run encountered NaN in native statistics after the fourth
completed command. Its failing snapshot was not serialized: the exact counter
name/count cannot be reconstructed from that raw capture.

V5 changes only statistics encoding. NaN, +Inf and -Inf become explicit tagged
values; keys, finite values, signed zero and statistic flags remain. Reserved
tag collisions refuse. A harmless native constant definition produced four NaNs:
the original strict serializer failed, and the tagged form round-tripped the
actual native snapshot. Native repr was saved first. Those names describe the
control, not the missing V4 snapshot. Synthetic nonfinite/finite controls and
seven boundary controls also pass. No task search was used for qualification.

## Interpretation and cost

V5 proves the timed-out route reached an unfinished Command.invoke(check-synth).
A SMART enumerator registration is visible. Neither observation isolates the
cost among internal enumeration, constraints, reconstruction or other work.
The pre-call statistics are not timeout statistics; there is no final snapshot.

Statistics getters and output logging can alter execution time. Per-case wall,
worker self CPU/RSS and root UTC launch records retain their exact scopes.
Complete process-tree CPU/RSS and a comparative efficiency conclusion are not
established. Native SOLUTION text is not an external checker result.

## Records and reuse

[RAW-INDEX.json](RAW-INDEX.json) lists capture seals; [COPY_MAP.json](COPY_MAP.json)
binds every copied original. SHA256SUMS binds this publication. Historical
absolute paths and prospective NOT_EXECUTED labels are preserved as evidence.
Actual root-launch folders establish what later executed.

All scratch scripts are included, including the transparent
[outer launch wrapper](raw/root-run-frozen-launch.py). Runtime binaries and
caches are excluded; manifests retain their original hashes and availability
requirements. Existing repository source is identified by pinned commits.
The packet supports inspection, not automatic relocated execution.

[V4 freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560004928) ·
[V5 freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5560079544)
