# Native wrapper source review

Qualified source acceptance of life_native.py successor f4eac06fa269d775be76d488830a82e6107d5272e77c7516686bb19abd3e91f9
(11,926 bytes). No remaining wrapper-specific blocker was found in this bounded review.
This is not native qualification or full lifecycle/source/apparatus clearance.

The original ec892d139798d39c8a3907b1e23974df735c2baa2e3fdaed53cc759c7cc82881
source is preserved separately. Root's only successor change explicitly rejects
nonempty DV on every proof-token assertion before native interpretation. This closes
the distinction between native validity and the protocol's stricter empty-applied-DV
scope, including mathematically vacuous substitutions.

## Exact request and authority

The wrapper records the canonical request and claims digest before validation.
It requires exact claim fields, ordered hole arity, safe uncompressed proof labels,
the 4,096-label bound, three distinct homogeneous typed parameters and globally
distinct issued labels. It compares the parsed issued theorem's statement, ordered
essentials, proof, mandatory floating rows, source DV and active DV to the request.

It pins the source index, adapter and verifier before executing their read bytes.
The native prefix is independently pinned. Issued labels cannot collide with the
existing library. The suffix permits no additional axiom, variable, floating,
DV or include directives; exact source label and theorem populations must agree.
The source index also rejects duplicate labels and unbalanced scopes.

Proof tokens cannot use any issued theorem shortcut, another claim's holes or an
extra floating hypothesis. The successor rejects applied-rule DV explicitly.
The fixed prefix binds the trusted assertion contents; ordered trusted labels/count
and the complete prefix-plus-issued theorem population are additionally checked.

Each call constructs a fresh native MM instance with no begin/stop shortcut.
The unchanged trace adapter invokes the native superclass verifier, validates native
contracts and stack/provenance correspondence, and records a selected trace only
after native proof acceptance. Successful wrapper output also requires exact verified
theorem order and selected-trace population. No historical PASS is reused as authority.

## Refusals, partial evidence and costs

A native MMError during the actual native-check stage is NATIVE_REJECTED; source,
request, trace-binding and other failures are CANNOT_CHECK. The pending theorem label,
verified prefix and prior selected traces remain visible, so a prefix failure must
not be reported as rejection of an issued target merely from the terminal name.

The field partial_traces contains completed selected traces retained before a failure.
It does not contain the failed proof's interrupted internal trace: the unchanged
adapter clears its active trace in finally. Raw database, suffix, request, log and
pending/error metadata provide the retained failure evidence. Reports must not imply
a complete interrupted-step trace was captured.

Post-custody changes downgrade the whole result to CANNOT_CHECK and clear authoritative
traces/contracts. Consumers must honor that overall terminal; historical partial
trace markers cannot authorize continuation. Current run_a checks the terminal first.

The wrapper charges one native replay when mm.read is actually called, separately
from the verified theorem population. Its timer ends after post-custody; final log
hash/read and receipt persistence are outside that interval. RSS is process-cumulative
highwater. Opening/archive failures or process interruption can leave no final wrapper
receipt; the supervising process record must retain their costs and mark incompleteness.
Those are apparatus responsibilities still awaiting the full source freeze.

## Caller compatibility and open integration item

Current run_a passes training and admission claims through life_common.native with
the correct positional API, fixed authority fields and compatible canonical digest.
It independently compares emitted and admitted-constructor proof/target/holes before
persisting witnesses. This compatibility read does not qualify the unfinished producer.

One actionable caller accounting issue was sent to lead: life_common.py at SHA
8abfba9bfd82b92a04bbd5315580a90b43e3d179821243d8d4e8b9171058b9db increments
native_calls for every wrapper invocation, even pre-native refusals returning zero.
Separate wrapper invocations from actual result.native_calls and retain failure costs.
Lead accepted the correction; its implementation remains to be checked at source freeze.

All work here was source/AST/data reading. No wrapper/module import, native verifier,
bridge, learner, matcher, fixture builder or test was executed. Full request mutation,
tamper/refusal controls, A/projection/B custody and source-stable process qualification
remain for the separately gated frozen lifecycle review.
