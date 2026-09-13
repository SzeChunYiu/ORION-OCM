# Parity custody repair validation

Date: 2026-09-13. Status: ready for independent integration review.
No timing experiment or candidate evaluation was executed by this correction.

## Controls and source authority

The complete focused suite passed 36 tests normally and 36 tests with an
optimized CPython3.12 parent, with zero failures or skips on laptop billy.
The two exact historical interpreter binaries were installed in an isolated
verification directory; this did not modify the measurement sources.

[The test record](raw/VALIDATION_RECORD_V1.json) identifies the gates.
[The synthetic receipt](raw/SYNTHETIC_COUNTERCONTROLS_V1.json) binds both
old source defects and the repaired implementation. It records:

- Original existing-output failure: the disabled measurement function is
  invoked once before FileExistsError; the old output bytes remain intact.
- Original cross-adjudication failure: false gates, empty timing tables and
  unbound protocol hashes still produce its stable-family terminal.
- Repair: both false packets are rejected; complete synthetic evidence passes.
  Concurrent identical reservations have one winner. A second launch or
  display-label change causes zero new invocations and preserves all bytes.
- Launch failures, source absence and interruption remain reserved. Mac
  execution is refused before reservation.
- Altered traces, checksums, block order, times, resource envelopes, candidate
  identities, capability records and frontier conclusions are rejected.
  The real 3.12.3 packet with a removed block is also rejected semantically
  after its intact positive control passes; this is not only hash checking.

Independent review exposed and repaired an identity-normalization gap: an
extra display_alias field could create a duplicate key after rehashing a
copied attempt. Both audit and cross collection now require the exact
canonical identity. The unchanged-packet/rehashed-alias regression is
rejected after one substituted invocation; the reviewer checked the fix.

Synthetic fixture times are invented for validator controls and are not
empirical deployment observations. The disabled invocation function never
calls the frozen measurement. Mixed-frontier controls still abstain.

## Existing empirical evidence, independently recomputed

The three raw V5 packets are exact imports from main
2ea3a617283bbe0f854f11df2ec4afcd57cbd848, merged through PR #547.
[Their binding record](raw/IMPORTED_V5_PACKET_BINDINGS_V1.json) preserves
the exact original bytes and SHA256 digests.

| Recorded interpreter | Complete content audit | Recomputed conclusion |
|---|---|---|
| CPython3.11.15 | 32 capability cases,64 complete frame traces,128 timing blocks | XOR-only frontier |
| CPython3.12.3 | 32 capability cases,64 complete frame traces,128 timing blocks | XOR-only frontier |
| CPython3.13.12 | Reported instrument-refusal schema retained | No family comparison |

Each complete packet represents 20,480,000 timed candidate calls already
recorded by the original run. This audit does not repeat those calls.
Counts are respectively (512,88,344,136) and (472,88,312,136) in the
registered DNF/XOR/shared-sum/lookup order.
Full derived boxes, dominators and terminals are retained in
[REAL_PACKET_AUDIT_V6.json](raw/REAL_PACKET_AUDIT_V6.json).

The valid recorded envelopes agree. The invalid third packet remains visible.
These are interpreter envelopes on one reported host, not three independent
hosts. First-attempt execution and historical interpreter build hashes were
not recorded by Custody V1 and are not reconstructed retroactively.

## Remaining limits and integration

The V5 expectation was already outcome-informed. This correction also read
the existing V5 outputs before finalizing the evidence auditor; it is not a
new prospective prediction. It changes no raw outcome or measurement rule.

Matching exact release is needed for historical static disassembly.
New custody additionally requires the recorded executable hash. Missing
matching executables produce UNVERIFIABLE rather than a content pass.
Static source and trace consistency cannot independently attest a remote
host, recover unrecorded original failure traces, or exclude a fabricated
self-consistent packet/history.

The first-attempt guarantee assumes one retained, coherent registry and a
stable machine identity. It does not survive deliberate registry replacement
or identity manipulation. Acquisition and custody overhead remain excluded
from V5's registered deployment coordinates.

Only this new modular directory is changed; V5 and the grand-theory files
remain byte-identical to their imported baseline.
