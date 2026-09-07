# Proof environment evidence records

The final commissioning passed **47/47 authored controls**. Its complete original seal, matrix, case inputs, native/process results and logs are preserved byte-for-byte. This is transport, custody and kernel-boundary qualification; it is not proof search, learning, corpus reconstruction, FLT or novelty evidence.

Read [MANIFEST.json](MANIFEST.json) for archive identities and original paths, then the archive relevant to the claim. [OMITTED_ELF_FILES.json](OMITTED_ELF_FILES.json) accounts for every omitted ELF payload. No native operation, build or test ran during archival.

## Final qualification authority

- Original seal SHA256: `67476a9394ad8ebe945ca3f1105ad893574ba0712df8a0e7ceb238ae42867fc9`.
- Final matrix SHA256: `e2a0e9d62f06d8bf7b0e6017fd1e41aad38035b264103007656aa37076e8a065`.
- Final archive SHA256: `a7acdf065da95fc10cd6e2e1f00a4dfceb66b38f05a5544aea9033bd35d39fd3`.
- Final member-map SHA256: `f0c2d735fca76fae9e8d6fcbc94ebc3cf039ceb92776a0cb65e9bf1fd59a89de`.
- Exact runtime manifest SHA256: `c9acc789908a216809a509facfc06c5aaf02206197fbc2f9f1531d3ae1c6d4e8`.
- Native final ELF SHA256: `1cf7eca5b692a2783fb95b7256b9836f2c0ab080b33463e86eba0cacfed19fe4`.

The original `result.json` deliberately retains `PROVISIONAL_PASS_REQUIRES_COMPLETE_SEAL`. Success authority comes from the final complete `seal.json`, whose 680-file map exactly matches the archive map excluding the seal itself. The archive contains all **681 files / 66,843,845 bytes**, with no omissions.

## Archive map

Each archive has a sibling `<name>.members.json`: a flat map from exact member name to `{sha256, bytes}`. Names are root-relative, with the declared directory prefixes only in registration-and-envelope. Tar members are regular files only; no extraction is required to inspect or verify them.

| Archive | Files | Raw bytes | Compressed bytes | Scope |
|---|---:|---:|---:|---|
| [final-commissioning.tar.gz](final-commissioning.tar.gz) | 681 | 66,843,845 | 10,579,670 | Complete final 47-control record; no omissions |
| [registration-and-envelope.tar.gz](registration-and-envelope.tar.gz) | 40 | 110,332 | 16,582 | Original registration, freeze and outer process envelope |
| [final-profile.tar.gz](final-profile.tar.gz) | 41 | 3,998,517 | 452,002 | Both exact-final prepare/check profiles, all packets and traces |
| [runtime-authority.tar.gz](runtime-authority.tar.gz) | 10 | 74,164 | 13,311 | Static/profile authority, independent scope review and package seals |
| [native-build-custody.tar.gz](native-build-custody.tar.gz) | 144 | 7,556,965 | 1,428,882 | Frozen sources, parent licenses, handoff, build/link/ELF evidence; ELF payloads external |
| [runtime-package-metadata.tar.gz](runtime-package-metadata.tar.gz) | 42 | 277,280 | 63,707 | Exact runtime manifest, package receipt and all custody sources; ELF payloads external |
| [development-history.tar.gz](development-history.tar.gz) | 3,034 | 155,033,561 | 23,625,024 | Complete retained development directory, including failed and corrected runs; ELF payloads external |

Total: **3,992 retained files / 233,894,664 raw bytes**, compressed into **36,179,178 bytes** across seven archives. Repeated packets and logs remain repeated where the original records repeat them; no outcome-based selection or deduplication changed original member bytes.

## External binaries and prerequisites

The omissions ledger has **57 path-specific ELF records / 378,121,040 bytes**. This total counts duplicate copies at distinct original paths; it is not a unique-binary storage estimate.

- Development history: 23 ELF files omitted.
- Final static build custody: 26 ELF files omitted, including its checker, loader/libraries, bubblewrap and 18 linked object files.
- Qualified runtime package: 8 ELF files omitted.
- Final commissioning, registration/envelope, profiles and authority: zero omissions.

Every omission records original absolute source path, full SHA256, byte size and reason. Those originals remain outside the repository and unchanged. Their retained source/build/ELF metadata remains inside the corresponding archive. No .lake tree, full checkout, release archive, or 125 MB native runtime is included.

[EXTERNAL_PREREQUISITES.json](EXTERNAL_PREREQUISITES.json) preserves the prior audit's canonical host interpreter, release archive and selected toolchain bindings. These are copied provenance, not newly executed, downloaded or fully requalified prerequisites. The exact historical full toolchain inventory is retained inside native-build-custody.

The executable runtime remains at `/home/billy/orion-director-work/20260907/proof-environment-qualified-runtime-20260907-v1/`. Evidence archives intentionally cannot substitute for provisioning that binary and its measured dependencies.

## Verification and costs

[archive_evidence.py](archive_evidence.py) created the archives with sorted members, normalized uid/gid/mtime 0, mode 0644, empty owner names, PAX tar, and gzip mtime 0 with no filename.

For every archive, the helper streamed every extracted member to verify its exact digest and size without writing extracted files; generated a second compressed stream and checked byte-identical archive hash/size; then rehashed every original input, including omitted binaries. No original file content changed. Compression normalizes archive metadata, not original file bytes.

Archival plus these checks took **32.622335895 seconds** inside the helper. CPU/RSS and complete prior lifetime cost are unmeasured. Both compression passes are included; source/script preparation and later documentation are outside that measured interval. The JSON manifest records actual timing and therefore is a run receipt, not claimed to be reproducible byte-for-byte from timing alone.

Historical profile observations remain separate from final commissioning: two exposed mutualRecursor prepare/check operations with fixed mounts and selected syscall traces. Their permitted proc/dev reads, missing outer prepare tracer timing/exit record, and CPU/RSS limitations are preserved in the archived profile audit. The final 47-control seal does not erase that history or promote it into a universal containment claim.

[ARCHIVE_PACKAGE_SEAL.json](ARCHIVE_PACKAGE_SEAL.json) binds the finished records directory, excluding only itself. Raw records and source authority take precedence over this index.
