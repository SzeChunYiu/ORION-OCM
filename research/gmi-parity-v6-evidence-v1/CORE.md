# Retained parity V6 evidence

This unit independently reconstructs the complete **measured records** in the
three V6 packets published at `243c2a12c0c385497b6ee43d5c60bfe8ebda270d`.
It executes no candidate, priming session, warmup or timed block.

Read [the contract](PROTOCOL_V1.md), then [operations](OPERATIONS_V1.md).
[The full receipt](FULL_RETAINED_AUDIT_RECEIPT_V1.json) contains each exact-runtime
result. [Input bindings](FROZEN_INPUTS_V1.json) identify original bytes;
[the manifest](MANIFEST.json) binds this complete unit.

Each packet retains 64 measured call traces and 128 timed blocks. The static
audit checks every recorded output, return flag and opcode offset, the complete
four-candidate universe, source parents, schedule, checksums, cost envelopes,
and the resulting robustly-undominated candidate set. That set contains XOR and
lookup for 3.11.15, and XOR alone for 3.12.3 and 3.13.12. Under independently
chosen values inside the observed intervals, lookup has possible, not necessary,
Pareto membership in 3.11.15; this is not a uniquely identified point frontier.

The forward priming traces were **not retained**: only summaries survive.
Their consistency is checked separately. Historical binary identity, first
attempt, host identity, prospective priority and priming causality are not
authenticated. Three interpreter packets do not establish three independent
hosts. Missing exact audit interpreters produce **UNVERIFIABLE**, never a pass.

This is retrospective evidence recovery and audit, not a new measurement,
prospective prediction, general architectural result or completed GMI theory.
