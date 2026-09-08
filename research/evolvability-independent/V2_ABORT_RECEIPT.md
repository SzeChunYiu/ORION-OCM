# E150 V2 protected abort receipt

Status: **CANNOT_CHECK / INVALID_CONFIRMATORY_RUN**

V2 protected seeds `9101..9140` were opened only after the V2 protocol, implementation audit, M11 bridge, full M11 regression, inherited cognitive-ladder negatives and development smoke all passed.

During an independent code-vs-protocol audit while the V2 protected process was still running and before any protected outcome had been read, the following mismatch was found:

1. `PROTECTED_PROTOCOL_V1.md`, inherited by V2, says non-identifiable target supports are excluded from exact-support accuracy.
2. `exact_support_metrics` removes non-identifiable oracle supports from the target set but leaves a correctly learned non-identifiable oracle support in the precision denominator. Such a correct-but-non-checkable support can therefore be scored as a false positive.

V2's own freeze rule says any protocol/implementation mismatch discovered after V2 starts burns V2. A termination request was issued immediately.

The output file raced into existence during termination. **Its contents were deliberately not opened or parsed.** Only non-outcome custody metadata was recorded:

- path in the isolated scratch workspace: `protected_factorization_v2.json`
- byte length: `6,282,950`
- SHA-256: `f635df9873836f9efc39b17b8cfdd2d7a3c18b1302a101f98b90e83e4d7ff103`

No metric, seed result, summary, favorable comparison or unfavorable comparison from that file is admissible evidence.

The same pre-V3 audit also identified three accounting/comparator defects that must be repaired before another protected run:

- contradiction/invalidation scans used to decide whether a local component must be relearned were unmetered, overstating generic locality amortization;
- the lazy symbolic arm was described as retaining episodes but retained only the current generation;
- the surrogate arm was described as online but reset its learned table each generation.

These are not interpreted using V2 outcomes. They were found from source inspection alone.

V2 protected seeds `9101..9140` are burned and will never be reused for confirmatory V3.

Terminal: `CANNOT_CHECK_PROTOCOL_IMPLEMENTATION_MISMATCH`.
