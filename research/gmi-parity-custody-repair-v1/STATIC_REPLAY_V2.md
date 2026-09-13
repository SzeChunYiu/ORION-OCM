# Archived-parent countercontrol replay V2

Incoming PR #550 changes the live V5 cross-adjudicator to accept newer packet
schemas. The historical V1 countercontrol intentionally requires the original
97bbda75 bytes. Reading that changing live path would prevent replay of the
original demonstrated defect.

The active countercontrols_v2.py changes only the source location and adds
versioned provenance fields. It reads raw/HISTORICAL_CROSS_ADJUDICATOR_V5.py,
whose SHA256 must still equal the original frozen binding. The exact historical
source was retrieved from commit97bbda75ee56d740875a8929e350f26bc11d1e72.
There is no weakened hash check and no substitution of the revised algorithm.

The original countercontrols_v1.py, its receipt and MANIFEST.json are retained
unchanged as V1 provenance. MANIFEST_V2.json binds both that imported V1 record
and this extension. Its field inventory is the current complete unit inventory.
The original manifest continues to describe the originally imported payload.

Run countercontrols_v2.py for the active old-defect replay. Its V2 receipt
contains the same actual results and zero-measurement counters, plus the
archived-source hash, original receipt hash and active replay-source hash.
The synthetic durations remain validator controls, never empirical data.
No instrument measurement, candidate body, timing loop or first attempt runs.

The three frozen measurement inputs (V4 parent, V5 harness and V5 registration)
remain live unchanged authority and are hash-checked as before. The revised
upstream cross-adjudicator is separate authority and is neither edited nor
used to explain the old defect. V1 operational custody commands are unchanged.

Focused extension tests check the complete V2 receipt, replay with an invalid
live adjudicator path, and rejection of a corrupted archived source. Both
normal and optimized integration runs retain explicit historical interpreter
availability reporting. No historical measurement is executed again.
