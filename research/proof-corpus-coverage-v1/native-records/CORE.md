# Native evidence

Read [the qualification note](../NATIVE-QUALIFICATION.md), then
[the portable archive command](../NATIVE-ARCHIVE.md).

- development-history.tar.gz retains all 1,203 originally inventoried raw files,
  including failures and superseded attempts, byte for byte.
- native-qualification.tar.gz retains all 123 files in directory 032, including
  its source snapshots, build metadata, original inventory and seal.
- independent-review.tar.gz retains the unmodified additive review JSON.
- Each .members.json maps exact relative names to original byte length/SHA256.
- SOURCE_BINDINGS.json binds current registered sources without laptop paths.
- EXTERNAL_INPUTS.json identifies ELF/toolchain/compiled artifacts retained
  hash-only, as in the original freeze. No additional raw file was omitted.
- SEAL.json binds this complete flat archive package. The trusted SHA appears
  in NATIVE-ARCHIVE.md; the audit does not silently trust a replacement seal.

Compression normalizes container metadata only (sorted regular members,
mode 0644, uid/gid/mtime zero, empty gzip filename). File content is unchanged.
The same writer produced byte-identical repeated archives on this host.
The portable audit reads members in memory and never extracts to the filesystem,
runs a proof, selects a corpus target or follows archived external paths.
