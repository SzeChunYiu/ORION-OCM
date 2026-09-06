# Runtime callback state boundary

`OCMRuntime.solve` refuses a candidate if its backend or required checker changes
runtime state during that callback. The previous loop captured `revoked` once;
a callback could call `runtime.revoke(support)` and still return a checked,
committed answer against the earlier evidence state.

The two actual-runtime revocation controls first returned `ANSWER`. They now
return `CANNOT_CHECK`, with no answer/candidate and no commitment. Revocation
remains recorded and survives restart. The guard also runs when the callback
raises, so mutation followed by an exception cannot downgrade this to an ordinary
candidate failure and allow a later stale candidate to pass.

## Boundary and trace

The runtime installs a callback guard in the solver's selected backend/checker
call sites. It does not wrap or enumerate the supplied operator catalogue.
A backend violation aborts composition and skips checking. A checker violation
invalidates earlier checker passes from the same solve and stops later checkers.
Normal query events are outside these callback intervals and remain recorded.

Each checkpoint retains identities of the runtime state, immutable field,
revocation set, evidence registry and operator registry, plus field/evidence/
registry transition epochs and local event position. Epochs advance through the
runtime reducer; host operator rebinding also advances the registry epoch even
when its declared manifest is unchanged. Replay reconstructs the epochs along
with a new state identity.

This is an **API-mediated state contract**, not a Python sandbox. It does not
qualify arbitrary in-place edits to mutable internals or undo callback effects.
The text adapter's separate content-digest checks remain in place.

## Cost and qualification scope

Each invoked callback adds two constant-size checkpoints. The task trace records
callback and checkpoint counts, the API-mediated contract, and zero full-state
hashes/catalogue traversals performed by this guard. Existing ledger emission
still computes state digests; navigation and other global work remain unchanged.
No end-to-end locality or speedup follows from this fix.

Focused controls cover backend/checker revocation, field/evidence admission,
manifest-preserving executable rebinding, audit-only writes, mutation then crash,
earlier-pass invalidation, durable revocation, and repeated pure callbacks.
A prepared 1,001-operator index is exercised while full iteration is forbidden;
only one structurally applicable operator is considered. Guard checkpoints are
also exercised with global state-digest properties forbidden, while ordinary
query audit events remain enabled.
