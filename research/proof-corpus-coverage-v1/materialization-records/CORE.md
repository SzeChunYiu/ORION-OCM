# Materialization records

Read [the component note](../MATERIALIZATION.md) first.

- Six archives retain 9,428 regular files / 14,201,890 raw bytes.
- Each archive has an exact member map and original directory/symlink metadata.
- All 222 symlinks are metadata-only; packaging follows none of their targets.
- [INDEX.json](INDEX.json) binds archives, original roots and source scripts.
- [READBACK.json](READBACK.json) records actual archive/original byte comparison.
- [SOURCE_FREEZE.json](SOURCE_FREEZE.json) separates current 18 production/helper
  files and four portability test/helper files from earlier executed closures.
- [OMISSIONS.json](OMISSIONS.json) names unretained temporary fixtures and the
  metadata-only boundaries. No absent fixture was reconstructed.
- [EXTERNAL_INPUTS.json](EXTERNAL_INPUTS.json) gives external runtime and material
  references; this package does not establish their present live custody.
- `SEAL.json` binds the complete retained package except itself.

The 26, 47 and narrow nine-control records are separate, overlapping engineering
qualifications. The actual continuation stopped at headroom scheduling before
phase entry. No real source materialization or semantic build is recorded here.
