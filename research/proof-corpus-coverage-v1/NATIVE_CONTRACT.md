# Native reference capture contract

This package supplies the missing evaluator association/export step. It does not
search, propose a new proof, admit knowledge, or perform a fresh kernel check.
Only authored fixtures have been used during development.

## Fixed command and input

`ocm_coverage REQUEST_JSON NEW_OUTPUT_DIR` takes canonical compact sorted UTF-8
JSON (optional final newline), with exactly:

```json
{"schema":"ocm.coverage.capture.v1","operation":"capture","module":["Theorems","Thm_registered"],"source_path":"/inputs/source.lean","range":{"start":{"line":1,"column":0},"end":{"line":2,"column":10}},"selection_range":{"start":{"line":1,"column":8},"end":{"line":1,"column":18}}}
```

Positions are Lean Position: line 1-based, column 0-based Unicode codepoints.
They are not byte offsets or UTF-16 LSP positions. `range` is the registered
core declaration span; `selection_range` is its exact declaration-name token.
The compiled full range must have the same end and selection. An earlier start
is accepted only when the intervening original source parses as declaration
modifiers attached to a fixed synthetic parser probe. That probe is never
elaborated, compiled, returned as a candidate or sent to the checker.

`native_ranges.prepare_selector(raw, record, source_path)` constructs this
request from the retained lexical wrapper record after verifying raw SHA/size,
all four segment hashes and exact segment reconstruction. It uses the inventory's
registered ASCII declaration-name grammar; unsupported layouts refuse.
The complete header token checks the source selection; it does not choose the
elaborated theorem. The old inventory regex can clip trailing apostrophes. Only
that demonstrated legacy parse is corrected here: provenance retains both names
and CORRECTED_LEGACY_NAME_BOUNDARY. Historical inventories are never rewritten;
unrelated name mismatches refuse.
The helper returns `{request, provenance}`; the caller binds both.

The native importer requires explicit LEAN_SYSROOT and LEAN_PATH. No fallback
`lean --print-prefix` subprocess is permitted. The host must independently bind
these paths, actual native binary/library imports, source bytes, compiled module
artifacts, compiler/options and transitive source/build provenance.

## Association and transport

- Enumerate constants by exact imported module origin, core/full range and exact
  selection range. Require one match and require it to be a theorem.
- Use exact declaration range entries directly, never the convenience function
  that redirects recursor names to parent ranges or uses builtin fallbacks.
- Import private/server metadata with `loadExts=false`. Do not enable imported
  initializer execution. The builtin extension entries are available without
  initializing source-defined extension state.
- Separately export the original target type plus ordered universe parameters,
  and the original theorem proof Expr, before exporting the source packet.
- Use the pinned parent exporter and existing packet validation. The parent
  normalization contract remains metadata erasure, let-nondep normalization and
  expression alpha interning. Raw output packet identity is recorded separately.
- Export original target and complete support closure, with type/value/opaque,
  projection/literal, inductive and recursor dependencies. Verify exact exported
  membership and full ConstantInfo equality for every support declaration after
  the pinned parent's expression normalization. Every non-expression field stays
  exact. Separately verify target/type/universe/proof roundtrip.
- Record every source declaration's name/kind/origin/universes, dependency edges,
  reached axioms and original proof dependencies. Capture reports axioms; only
  the independently authorized prepare/check path may approve their use.

Success creates exactly `goal.ndjson`, `reference.ndjson`, `source.ndjson`,
`association.json` and `result.json`. The goal/reference descriptors each
provide the parent expression root and ordered level-name indices.
The source packet remains evaluator-only and contains exposed original support.
The preparation policy excludes the original target and selects the registered
reference dependencies plus goal support. Original solutions are deliberately
available in this coverage arm; no packet is a masked learner task.

## Results and process contract

Stdout is exactly the JSON written to result.json. Complete structured outcomes
exit 0. Request/association/import/transport failures return CANNOT_CHECK with
their reached stage and retained declared partial files. Unique source matching
runs in association; after it succeeds, closure and all packet writes run in
export, preserving the first failing stage. Existing output
directories, invalid CLI shape and unhandled process failures exit nonzero;
a caller must not interpret nonzero as a checked semantic result.

Success terminal is REFERENCE_CAPTURED, stage capture, reason
EXPOSED_REFERENCE_CAPTURE_NO_KERNEL_CHECK; kernel_check is always NOT_RUN.
No result here is KERNEL_PASS. The independently qualified environment runtime
checks the separately frozen target and expression packet afterward, producing
new receipts rather than reusing the historical 47-control receipt.

## Trust and scope

Declaration range metadata can be authored or overwritten by source code.
Unique metadata plus a pinned module is not cryptographic source attestation.
The actual source/compiled-artifact correspondence relies on the registered
trusted compiler, exact source and import/build profile. Header consistency is a
refusal control; it must not be promoted to universal adversarial source proof.

Source compilation can execute tactics, plugins or run_cmd and needs its own
offline executable/resource profile. Reading compiled constants without running
initializers does not retroactively qualify their build. Imported source/compiled
metadata are evaluator-only; future proposers require separate masking/redaction.
The upstream AI-authored corpus remains exposed reference material, never labelled
mechanically acquired OCM knowledge. No whole-OCM no-neural, learning, scaling,
theorem reconstruction or FLT result is established by this adapter.
