# Exact recovery

[RAW.zip](RAW.zip) holds the exact new caller source/history, gate/request, observations, transport/member/claim bindings, native log/receipt and full library manifest. [RAW-MEMBERS.json](RAW-MEMBERS.json) binds every member to its original bytes. Absolute paths inside retained records identify the historical execution, not a relocated runnable installation.

One 1,806,915-byte base prefix appears as `base/PREFIX.mm`. The actual 5,286-byte transported suffix is preserved. [RECONSTRUCTION.json](RECONSTRUCTION.json) specifies base + one newline + suffix; the resulting 1,812,202 bytes matched both retained `JOINED-PREFIX.mm` and `native-01/database.mm`. Those duplicate blobs are represented by that exact recipe. All original local files remain intact.

The seven unchanged bridge/native source/license files and the complete historical cohort packet are referenced by verified immutable Git blobs at commit `848a7c1370f749494d57400bcedb9e20a206dc82` in [UPSTREAM.json](UPSTREAM.json). The prior native-authority metadata is recoverable from its exact published raw-archive member; archive and member hashes were read back. No full prior runtime/source trees are duplicated.

`LIBRARY-ARTIFACT.json` distinguishes canonical manifest identity (3,541,834 bytes, `879aac45…`) from the stored manifest file (3,541,835 bytes, `e93aa075…`, with trailing newline). The receipt binding intentionally identifies its stored 394,423-byte file, `76e6b27c…`. [Exact artifact bindings](records/qualification-01/LIBRARY-ARTIFACT.json) preserve the complete digests.

Packaging performed byte comparison, hashing and archive readback only. It did not import the caller or rerun the constructor, native verifier, Library, search or any training/evaluation procedure. The original source-only/pregate status documents remain historical; the current outcome review supplies the result scope.
