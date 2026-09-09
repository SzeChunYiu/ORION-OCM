# Exact recovery without executing target code

[Public FILES.json](FILES.json) binds this package, excluding itself.
The outside PACKAGE.json pins that manifest. These are packaging identities;
the unchanged original ledgers are [ORIGINAL-FILES.json](records/ORIGINAL-FILES.json)
and [ORIGINAL-SOURCE-FREEZE.json](records/ORIGINAL-SOURCE-FREEZE.json).

[RAW.tar.gz](RAW.tar.gz) contains exactly 126 regular files under original/.
Strip that prefix to reconstruct the complete original source capsule.
Every original document, historical source generation, authored input,
outcome/process/stdout/stderr record and full pre/post pin ledger is preserved.
[RAW-MEMBERS.json](RAW-MEMBERS.json) gives every original relative name, member
identity and readable public copy. [COPY-MANIFEST.json](COPY-MANIFEST.json)
binds all exact direct copies, including the four independent-review files.

The [Lark archive](runtime/LARK-1.3.1.tar.gz) contains exactly the 46 files in the
[original runtime manifest](runtime/ORIGINAL-RUNTIME.json), under lark-runtime/.
It includes the [MIT license](runtime/LICENSE), grammar resources and distribution
metadata. [LARK-FILES.json](runtime/LARK-FILES.json) pins every member.
This archives already pinned bytes; it does not requalify or execute the runtime.

For byte recovery only, extract each archive into a new empty directory using
a standard tar reader, then compare every relative name, byte length and SHA256
to its member manifest. The original FILES manifest binds 125 members; its own
bytes are additionally bound by RAW-MEMBERS. No import or test is needed.
[RECONSTRUCTION.json](RECONSTRUCTION.json) specifies the exact prefix mapping
and deterministic USTAR/gzip encoding (sorted members, zero times/owner IDs,
0644 regular-file modes, empty owner names and gzip filename, compression 9).
Every archived member was read back and compared to its original; a second
metadata-only archive build produced identical bytes.

Recovery preserves file bytes, not inode metadata or a live environment.
Original absolute import/source/runtime paths remain unchanged in receipts.
The pinned Python executable and whole standard library are not archived;
their historical identities remain in the raw pre/post ledgers. Relocation
or a future invocation still requires its own concrete source/runtime binding.
There is no actual 22-member packet, joined prefix, H1 input or native/scientific
outcome in this source capsule.

[Readback receipt](READBACK.json) records the packaging checks only.
