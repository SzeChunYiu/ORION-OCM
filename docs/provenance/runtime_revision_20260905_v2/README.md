# Second runtime revision custody

The twelve original milestone receipts and twelve first runtime successor receipts remain
historical evidence. V2 verifies their custody against the exact source revision
`479e78165fb455481cadcf03fd8e3a99ba79c5af`; it never runs the old recipes against the new
engine and never transfers an old protected result to current code.

`PARENT_MANIFEST_V2.json` binds a 256-file, 694,208-byte compressed snapshot. It contains
the original Git commit object and complete Git tree objects. Verification checks the
commit, tree and selected blob object identities, exact archive entry inventory, file
sizes and SHA-256 digests. The selected snapshot includes all parent runtime source,
all original provenance, and recursively bound source/evidence/config/test/recipe
files. Verification reads archive members in memory and extracts no paths. It works
without network access or a local copy of the parent Git history.

Every first successor's source bindings are checked against archived parent bytes.
Historical documents, results and receipts must also remain byte-identical in the
working tree. Current source is independently inventoried: every runtime source and
packaged resource under `src`, Python files under `tests` and `tools`, and `pyproject.toml`.
Adding, deleting or modifying a current source/resource invalidates the active receipt
and engineering replay. Bytecode caches are excluded.

`ENGINEERING_REPLAY_V2.json` separately identifies executed engineering commands,
validation artifact hashes and their exact current source inventory. Two named gates
are mandatory: the complete OCM pytest suite and the seven-file final regression suite
declared in the fixed config. Their normalized commands must match exactly; parsed
JUnit reports must agree with actual testcase counts, contain no failures/errors, and
not consist entirely of skipped cases. The full suite must include at least the 613
cases established at the parent revision. These are recorded-run attestations, not
cryptographic proof that a command executed. Its schema refuses
protected reevaluation, scientific promotion or independent replication labels. The
report records authored regression evidence; passing it does not close the historical
M11 adoption-cell or M12 protected-reevaluation limitations.

The active command is `PYTHONPATH=src python tools/m12_receipt.py --verify`. All twelve
milestone wrappers explicitly dispatch to V2. Missing predecessors, the archive, new
receipts, replay evidence or dependency receipts refuse verification; none fall back to
historical receipts. `--write-current` exclusively creates a previously absent receipt.
Repeating it is idempotent only when the existing bytes still verify. A later source
change requires another revision, not overwriting either earlier generation. Calling a
wrapper without arguments refuses all writes.

The immutable config and snapshot manifest are pinned by the verifier. These are local
custody and engineering assertions anchored in the reviewed repository, not an external
signature or an independent evaluator's endorsement.
