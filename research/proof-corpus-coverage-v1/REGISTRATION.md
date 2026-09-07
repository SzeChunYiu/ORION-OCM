# Fixed corpus registration

Read the original [design](F1-CORPUS-COVERAGE-DESIGN.md) and
[execution policy](F1-CORPUS-COVERAGE-EXECUTION.md) first. These documents remain
unchanged prospective records. This registrar makes their assignment concrete.

## Entry and authority

On billy-laptop, use the independently pinned CPython 3.11.14 interpreter:

```text
<python> -I -S registration_envelope.py <inventory> <bare-git> <new-run> <new-envelope>
```

The envelope records actual process exit, raw streams, elapsed wall time including
the registrar's seal, child CPU and nonaggregate child maximum RSS. It is a process
record, not an independent acceptance checker. Registration has no network or
proof dispatch. Its local metadata-reader dependencies are trusted host tooling;
this is not the separately enforced native workload profile.

The production CLI exposes no seed, filter, population size or replacement option.
`coverage_policy.py` fixes all raw input/document identities, the complete
29,511-pair denominator, four assignments and prospective execution constraints.
Changing that source creates a successor policy, not a continuation of this run.

## Custody and ordering

1. Create a new output directory and bind the launch record.
2. Load parent/current Python modules from actual source bytes, ignoring cached
   bytecode. Bind and snapshot the loaded bytes and prospective documents.
3. Snapshot all four historical input files against fixed raw hashes and sizes.
   Parse source/graph/solution metadata with duplicate-key refusal. WRAPPERS is
   copied and hashed, including its source strings, but is not parsed or used
   as an assignment feature.
4. Validate every pair, graph edge and duplicate identity. Independently recheck
   commit/tree/file membership and blob types/sizes in the pinned Git store.
   This metadata check does not reopen proof Git blob bodies. Historical blob
   SHA256s must still be checked against actual bytes before future compilation.
5. Recheck original and copied inputs, executed source snapshots, documents and
   Git evidence before computing the fixed identity-only full order.
6. Store every ordered pair, four assignment records, all planned stages and
   continuation cursor 4. Initial stage costs are unknown, not zero.
7. Recheck expected bytes for every output and reject extra files. The final seal
   binds the complete pre-seal directory; the seal excludes itself and the outer
   process envelope. The returned seal hash binds the seal itself.

Known outputs are bound from their intended bytes before writing. A final
directory inventory cannot silently adopt a changed population or stale
assignment reference. Interrupted Git calls retain available partial streams and
mark missing evidence explicitly. A failed registration retains partial files
and a CANNOT_REGISTER record, including when an incomplete seal exists.

The design assumes a controlled registrar process and trusted interpreter/host.
Content bindings detect persistent custody drift; they do not claim immunity to
an adversarial kernel or arbitrary concurrent process-memory modification.

## Interpretation

Only a verified complete seal authorizes `REGISTERED_NO_DISPATCH`.
REGISTRATION.json is explicitly provisional on its own. All assigned stages
remain `NOT_DISPATCHED` until separately recorded execution. No semantic check,
proof reconstruction, useful learning, FLT result or novelty follows from a
successful registration. Failed assigned rows may never be replaced by easier
ones. Revisions preserve this population and original outcomes in new records.

The resource/profile and native capture components have separate source and
qualification records. Their later source changes do not retroactively change
this registration's assignment policy or qualify an older workload receipt.
