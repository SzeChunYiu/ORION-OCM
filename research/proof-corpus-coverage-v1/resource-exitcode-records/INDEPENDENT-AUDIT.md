# Exit-code correction: independent retained-record review

Verdict: **RETAINED_RECORD_AUDIT_PASS**.

The current runner preserves exit codes observed in both the monitor and cleanup
loops. Actual paired exit-0/exit-7 receipts and the resource-stop/exit-minus-15
receipt retain those codes when a later controller snapshot fails. They continue
to report CLEANUP_INCOMPLETE and do not claim reaping or controller removal.

- Fresh host matrix: 12/12 intended outcomes.
- Focused controls: 65/65, zero failures, errors or skips.
- Frozen/current sources: 23; prior change is one runner plus one new three-control file.
- Source occurrence/raw custody: 108 loaded bindings, 36 raw streams, 11 host-input hashes.
- All 12 recorded host-case PIDs and controller paths were absent at review.
- Original 19-source and previous 22-source packages and guards remain unchanged.
- Complete qualification tree: 496 regular files, unchanged during this audit.

Four retained development runs include the original paired failures and the
review-discovered cleanup-poll failure. Their outer time plus the fresh matrix
and focused outer times totals 13.019591085 seconds. Nested case times are not
added again. This excludes editing/packaging and prior acquisition/build work.
The spool control retains 4,103,093 bytes of sampled-stop overshoot.

COSTS.json's phrase “no new native work” means no native mathematical proof run:
the authored native C fixture cases did execute. This is an additive scope
clarification; the original raw record is preserved.

AUDIT.json is the independently generated binding/outcome record. This review
performed no test, resource, native-proof or corpus execution. The new portable
guard was reviewed as source only; its executed no-alarm has separate authority.
