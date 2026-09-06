# PR91 current vendored-target binding

The intentional ledger adaptation changed its target blob from
a4e2e6a832410f4c18ef8b82583888f37fa8eb79 to 3306841cbc969c281ba8141b9d8e3ea747c38556.
The first CI target check correctly refused that stale binding.

VENDORED_SOURCE_MANIFEST_V1.json is also frozen predecessor evidence.
An attempted in-place target update passed the 25-target check but was correctly refused
by current engineering predecessor verification. That attempt and the refusal are retained
here; the historical V1 bytes were restored exactly (SHA2560979e368063a5e7ca7fa59ea001449ee5b84080705db41e206a545d48d9c7a90).

The new ../VENDORED_SOURCE_MANIFEST_CURRENT.json is an explicit current-target projection.
It binds the historical V1 path/hash, retains every original source pin and byte_identical
flag, and updates only the adapted ledger target and its change description.
Mode remains ADAPT; source blob08f712c32e4c03e35dab55315706be00612fef58 is unchanged;
byte_identical remains false. No historical scientific requalification is claimed.

CI now passes that manifest through the existing checker's --manifest argument.
The scoped .github/tools/scripts search found only the one active CI invocation.
The checker implementation and its default historical-manifest behavior are unchanged.

Final current projection: all25 targets pass. Source repositories were not consulted by
this --targets-only run. Current engineering verification, all12 milestone wrappers and
separate archived V5 custody verification pass; current source1e87a74d… and receiptdced7c6e…
remain unchanged. No source/test modification, full recorder, or timing rerun was required.
verification.json records exact commands, hashes and wrapper outputs.
