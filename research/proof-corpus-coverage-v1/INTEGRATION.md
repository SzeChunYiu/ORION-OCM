# Portable integration and independent review

**PORTABLE_INTEGRATION_PASS.** On billy-laptop, 180 tests passed, seven privileged
host cases were skipped, and two exact-interpreter registrar CLI cases were
deliberately deselected. Those nine cases retain their separate prior host
qualification; they are not new portable passes.

The same integration ran all three real retained-evidence guards:

| Guard | Observed custody result |
|---|---|
| Registration | 29,511 ordered pairs; four assignments; cursor 4; 18 current bindings; four raw inputs explicitly not revalidated |
| Native | 1,327 archived members; 41,861,955 raw bytes; 47 current source bindings |
| Resource | 380 archived members; 9,583,009 raw bytes; 19 current source bindings; omitted host inputs not revalidated |

[Raw result](integration-records/RESULT.json), [process records](integration-records/PROCESSES.json),
[source freeze](integration-records/SOURCE_FREEZE.json) and
[complete retained integration inventory](integration-records/INVENTORY.json) preserve
the exact commands, interpreter, explicit environment overrides, streams and JUnit.
The 63 source/test/workflow files captured before this integration were unchanged
afterward. Integration records added afterward are not retroactively part of that freeze.

Independent reviews checked original registration custody/order and native archive
members against retained originals, in addition to the guards' no-alarm behavior.
Resource production/profile review and subsequent archive-guard review remain distinct.
The integrated source hash checks cover the registered bindings, not every host file.

Two registration-guard edge cases were repaired before its final qualification:
an appended tar member after an end marker, and source directories resolving
outside the supplied tree. Actual fixed archive hashes remained intact. The
original registration, population, four assignments and seal were not changed.
Guard tests include clean data and malformed/tampered fixtures; failure history
is retained in the component records.

No registrar, native proof controls, privileged resource workload or assigned
corpus row was dispatched by this integration. Its terminal concerns portable
engineering controls and byte custody. It does not establish semantic coverage,
new proof success, learned benefit, neural absence throughout OCM or novelty.
