# Contracts and custody

## Original three routes

[The frozen proposal](raw/PROPOSAL.json) assigns fresh implicit primitive,
original explicit primitive and exact printed-native-grammar replay processes.
The two parent input files remain unchanged. The replay replaces only the
synth-fun grammar with the actual printed A_Int_489/A_Bool_491 grammar.
The max3 specification, source, checker and envelopes remain fixed.

Nine retained structural controls qualify input construction; they ran no
native synthesis or Z3. All three actual assignments remain in
[the capture receipt](raw/capture-v1/receipt.json), including both timeouts.
The existing checker then runs once over the sealed capture; only the
implicit response supplies a candidate for an actual Z3 obligation.

## Separate SI-all successor

[The successor proposal](raw/single-invocation-successor/PROPOSAL.json)
assigns another unchanged implicit parent and the same exact explicit grammar.
The latter adds only (set-option :sygus-si all) and
(set-option :sygus-si-rcons all), after the original three setup commands.
Worker, capture, checker, grammar, max3 spec and resources are unchanged.
Nine structural controls precede this separately registered capture.

The two options are configured input, not proof of the internal route actually
taken. [SOURCE-NOTE.md](raw/single-invocation-successor/SOURCE-NOTE.md) retains
the source-based rationale. The observed timeout does not locate its cause.
No retry or alternative grammar is substituted into either capture.

## Resource and authority boundary

Each assigned worker has CPU0 affinity, 4 GiB virtual address space, a 5,000 ms
native setting and 20 s external timeout with 2 s cleanup grace; the supervisor
watchdog is 24 s. Post-seal checks retain 5,000 ms native / 10 s external bounds.
Saved case wall times and per-check metrics have their original scopes.
Complete process-tree CPU/RSS, energy, acquisition/installation and lifetime
cost are UNKNOWN. These single public captures establish no timing advantage.

The ordinary worker and fixed checker sources are copied from execution head
7e45ecb22ad975def3b3157bbd925e41169da1d5. This publication adds evidence only.
Preparation labels such as NOT_RUN remain historical bytes; actual
root-launch/root-checker completions establish subsequent execution.

All preparation, inputs, source, controls, raw outputs, checker receipts and
actual root launch metadata are copied without rewriting. Empty timeout
outputs are evidence and remain empty. Runtime binaries and generated Python
caches are excluded; dependency bindings are retained. Historical absolute
paths are unchanged and do not promise automatic relocated execution.
Publication performed static byte/hash checks only: no actor, test or regrade.
