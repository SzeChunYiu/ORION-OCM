# Exact defects and bounded repair

## Preserved second attempt

Registered source f9c70b3736950c2423a063b0ec204b03e9561277 passed F1:
the two arms independently acquired matching canonical programs before application.
The completed native arm and incomplete OCM arm remain distinct.

At withdrawal, a previously unseen OCM application request had only the dead
descriptor as a parent. Its own request-data warrant was live, so ordinary admission
correctly rejected it as ISOLATED_ATOM_REJECTED before catalogue construction.
The returned CANNOT_CHECK_APPLICATION is not a policy refusal.

The rejection emitted OBJECT_QUARANTINED but did not apply its state reducer live.
Event 338 therefore changed replay state from 8c235b497adf46fe3d29e32c98f33c5dac70d176ae8a30f964feb67e7ae379e3
to 372ab7dfd446bed5531d8a2cc81f266da8e41778466f1da113b9b54c7a0e0226.
Event 339 still expected the former live-state hash.
The final restore process failed during constructor replay, before its queries.
The untouched ledger SHA256 is f0f39dea71d13e1c37390d2f3ae810b3e863fc2e811123c27b77989af83a1a17.

## Changes

- OCMRuntime.admit_object applies its emitted refusal event before reraising.
  The ordinary admission rejection remains; failed atoms never enter knowledge state.
- OCMRuntime.solve applies its separately emitted JUMP_PROPOSED event.
  A real disconnected-target solve reproduces this second defect independently;
  the failed study ledger contains no such proposal. Proposals remain unadopted.
- Application query data retains its original descriptor edge and also connects to
  the existing public ROOT. Both-bound descriptor support, required operator inputs,
  checker, output support, dead host-binding refusal and counters are unchanged.

No global _emit behavior, reducer algorithm, state hash or replay guard changed.
No old event, manifest, oracle, denominator or prospective tuple was rewritten.
Persisted catalogue slots, host-bound code and actual visited calls remain distinct.

## Qualification

The three real regression tests first failed on the original source, then all passed.
The final runtime/N1/G1 suite passed 341 tests in 37.12 seconds, with stable source hashes.
See controls/red*, controls/green* and controls/final* for commands, raw output and XML.
Unused outer test imports were removed after initial green; both test generations
are preserved as text in prior-control-source/ and current-source/.

The new cold-withdrawal request did not exist before the first fresh worker.
Dead bind refuses; all four persisted slots are offered, the dead descriptor is
only exploratory and its apply operator is not composed or visited.
The actual invocation meter records no call and no answer is selected.
A separate fresh worker reinstates the same registration and answers the same request.
The unrelated guard function and public syntax fixture route remain available.

The core refusal and obstruction controls compare live and fresh-process snapshots,
event hashes, ledger head, quarantine/proposal data and resource meter.
Corrected source still refuses a copied original ledger with the exact mismatch.
The historical control first encountered an incorrect diagnostic path before any
state opened; that discovery failure is retained separately.

Two independent source reviewers cleared the three local changes.
Current engineering receipt regeneration and successor study registration are separate gates.
