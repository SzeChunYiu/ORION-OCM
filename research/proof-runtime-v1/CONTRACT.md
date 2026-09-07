# Proof support and recovery contract

## Correctness, provenance and applicability

Discovery/request evidence A warrants the procedure's eligibility. It does not
become a necessary formal correctness premise after an independent kernel check.
A checked route carries `{B,S}`: fresh checked-run assumption B and shared
checker/environment assumption S. A second execution contributes `{C,S}`.
The alternatives are `{B,S} OR {C,S}`; they share S.

Withdraw A: formal support can remain LIVE while applicability becomes false.
Withdraw B: route C can survive. Withdraw B and C: the theorem becomes OPEN,
not false. Withdraw S: both routes become unavailable. Reinstatement reuses the
same checked evidence and never runs another check implicitly.

Support is evaluated after both OCM and evidence-registry nogoods. UNKNOWN is
CANNOT_CHECK. Certificates, metadata, role labels and proof hashes alone cannot
satisfy the authenticated proof subview.

## Atomic object admission

`rt.admit_batch(items)` validates the entire ordered batch in local immutable
states before emitting one event. Invalid final objects expose no admitted prefix.
The event body is explicitly versioned `ocm.object-admission-batch.v1`; old
readers refuse its new event kind. Existing single-object and historical event
behavior is retained.

The reducer validates full bodies, envelopes and resources before replacing the
runtime state. During batch admission, an uncertain write or post-append interruption
requires successful replay before further writes. Atomicity covers this one OCM event; it does not
create a transaction across OCM and the issuer journal.

## Issuer protocol

The host owns a separate hash-chained `LedgerStore` with REGISTERED, PREPARED and
COMMITTED rows. Never mix these private rows into the runtime's event ledger.

PREPARED binds the exact run, proposal/check artifacts, descriptor, full evidence
policy, serialized object/edge bodies, support bounds and authorized OCM
predecessor. The planned suffix is exactly two evidence events and one object
batch. Only a complete matching COMMITTED route is served by this subview.

An explicit `recover(run_id)` can complete that exact authorized suffix after a
crash. It refuses intervening events, changed objects, altered evidence policy or
missing artifacts. Repeated recovery is idempotent. `proof_status` never recovers,
rechecks, searches or fabricates substitute evidence.

The atomic proof batch is complete if a crash occurs before issuer COMMITTED;
authenticated serving still waits for explicit recovery. Quarantine is used only
for a root anchor's admission convention, never as a global visibility barrier.

Evidence identity excludes scope/authority/derivation in the underlying registry.
The adapter therefore binds that policy inside the payload and compares the full
existing record and its original admission event before reuse. Full object bodies
are compared; the short `Atom.content_hash()` is insufficient.

## Custody and limits

The journal establishes consistency under trusted host/filesystem custody. It
is not a digital signature or a defense against an administrator rebuilding a
valid ledger or rolling back all trusted storage together.

Restart requires the same exact host source, registration, event log and bound
artifact bytes. Historical proof data stays data. New executable callbacks come
from explicit host registration and a newly bound live session.

Source/runtime inventory hashing, raw record fsync, ledger replay, status scans,
full-field navigation and admission validation are real costs. This version makes
no locality claim; a versioned incremental successor must earn that separately.

The inherited OCM JSON serialization of an unbounded scope epoch includes
Infinity. That storage contract is preserved. Task/term JSON is separately
validated by the strict closed-session encoding and fixed signature contract.
