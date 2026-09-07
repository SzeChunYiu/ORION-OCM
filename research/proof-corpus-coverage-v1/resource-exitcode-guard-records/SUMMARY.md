# Exit-code correction guard qualification

The additive 72-line `resource_exitcode_evidence.py` reuses the unchanged prior guard by exact source SHA. No earlier guard or sealed record was modified. The CI resource-custody step now invokes the current correction guard.

`01-red` records eleven expected missing-interface failures; `02-green` records the implemented eleven controls passing. `04-final` repeats the same eleven controls on the final pin-only source, all passed with no skips (0.13 s). Tests use three distinct inert source generations and preserve failures for changed prior/current source, altered old authority, inconsistent archive snapshots, omitted-input bindings, extra historical files and unbound helper source. No archived source executes.

`05-real` records the real default CLI, once, with the selected Python 3.11.14, `-I -S`, `/tmp`, empty environment: exit 0, empty stderr, 0.336466186 s wall, PID 1783451 reaped and process group absent. Source identities agree before/after; all 51 protected earlier guard/helper/test/archive identities remain unchanged.

The actual result is `RESOURCE_EXITCODE_CUSTODY_PASS`: original archive 380 members / 19 historical sources; prior successor archive 1,518 members / 22 prior sources; correction archive 881 members / 5,812,553 bytes / 23 current sources. External host inputs are not revalidated.

`03-pack` and `archive_records.py` retain the exact archive recipe and process. The complete correction package has 42 files / 475,354 bytes, sealed by `9c36d2396ab1ed8f94e54c810d2486488b869174e413d21635ca32d64143b39e`. All 496 qualification and 385 development regular files are archived byte-identically; 55 symlink aliases are represented only as metadata. The independent raw resource audit is copied inside the package.

Final guard SHA256: `c392fc1ae67299bc817e64a3e850f6c34bfb99c234af5fa0ce7d0cc7b888441f`.
Final own test SHA256: `3c9c4ea58a22ad36ef1a7a14b1a4ebbb568b2746cc8a641dc898a0b8fa5b94d4`.
`06-independent-review.json` approves the pin-only source, complete seal, actual streams/current source bindings and 11-pass JUnit without execution by the reviewer.

This lane ran portable evidence tests, archive preparation and archive/source verification only. It ran no resource profile, native fixture, Lean proof, corpus build or registrar. The separately recorded 12-case native C qualification and 65 resource controls belong to the implementation lane and are not new cognitive results.
