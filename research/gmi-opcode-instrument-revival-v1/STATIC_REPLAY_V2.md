# Portable replay correction, without new measurements

The experiment, freeze, four reservations, four raw executions and V1 receipt
remain byte-identical. The V1 audit's command check required the recorded
absolute script path to equal its present checkout path. That correctly
passes in the original location but refuses relocation.

The active [V2 auditor](opcode_audit_v2.py) checks the complete command structure,
registered interpreter and arguments, one common absolute recorded script
path with the exact instrument filename, all registered source digests,
native disassembly and every raw offset/output/return witness.
It preserves the original execution path as provenance instead of equating
it with the location from which historical evidence is being reread.

The [V2 receipt](OPCODE_REVIVAL_RECEIPT_V2.json) binds the V2 audit source,
V1 receipt, original freeze and all raw evidence digests. Scientific counts
and outcomes are unchanged. This is a post-execution static-audit correction;
no original or repaired candidate was executed again.

Use `test_opcode_revival_v2.py` for active verification: 16 tests include
the original retained evidence and deliberate missing/reordered/duplicate
offsets, wrong outputs, missing returns, unsupported control flow, native
disassembly reconstruction, exact receipt replay and a relocated copy.
The frozen V1 test/auditor remain historical execution controls; their exact
command-location assertion has the recorded-location scope.

Normal and optimized CPython 3.13.12 runs both pass. Other interpreters can
check source and recorded-data mutations; native-offset and exact replay tests
explicitly require the recorded interpreter. Local reservation files and
timestamps are not external host/time attestation or global no-retry proof.
