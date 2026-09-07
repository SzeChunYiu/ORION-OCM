# Authority and custody contract

## Trusted evaluator boundary

The host evaluator approves input and runtime digests before invocation. Python,
its standard library, the host OS, build tools and approved programs remain trusted.
The driver binds its selected interpreter executable and actual module origins;
the qualified entry compiles its driver/helper source bytes directly, ignoring
timestamp-based bytecode caches rather than treating them as source evidence.
It does not establish an independently sandboxed Python implementation or defend
against an adversarial same-user process modifying the host during execution.

The native checker is isolated with the existing, unchanged mechanical-proof-v1
helper. Its namespace contains individually approved regular files, a fresh writable
output directory, temporary storage, proc/dev and a clean environment. The host
source tree, full evaluator export and compiled fixture caches are never checker
mounts. Binary/import/link review must also exclude fixture code from the executable.

## Native packet authority

The parser format is the pinned native NDJSON format3.1.0. It retains Lean names,
universes, expression graphs, definitions, opaque values and inductive families.
Kernel-relevant reconstruction is claimed; original annotations omitted by the
parent exporter are not claimed to survive byte-for-byte.

Separate exports can choose different alpha-equivalent expression representatives:
the parent interner ignores binder names and binder annotations. Declaration
comparison follows that kernel-term normalization while preserving non-expression
fields, ordered universe parameters, constant/literal/projection identities and
full type/value structure. Raw authorized packet bytes remain exact. This does not
claim equivalence of source-level implicit/explicit binder interfaces.

The target comes from an independently registered expression-only packet and
ordered universe parameters. Preparation compares the source target header against
that registration. A candidate cannot replace the goal, assert extra axioms or
provide a carrier declaration. Its packet must contain no declarations.

Primitive declarations/families and allowed axioms are independently pinned.
An overlap must agree in complete checked content, not merely familiar name/type.
Types, values, opaque bodies, inductive groups, recursor rules, projections and
implicit literal dependencies participate in closure accounting. Exclusion follows
actual dependencies. This is not an algorithm for every logical equivalence.

## Host file records

Every file record has exactly `path`, `sha256`, `bytes`. Paths are absolute regular
files without symbolic-link components; byte counts are nonnegative integers.
The externally authorized manifest digest binds the record. JSON duplicate keys,
nonfinite values, missing fields and undeclared operation roles are refused.

Preparation freeze:

```json
{
  "schema": "ocm.proof-environment.freeze.v1",
  "operation": "prepare",
  "inputs": {
    "source_packet": {"path": "...", "sha256": "...", "bytes": 0},
    "registered_target_packet": {"path": "...", "sha256": "...", "bytes": 0},
    "primitive_packet": {"path": "...", "sha256": "...", "bytes": 0},
    "policy": {"path": "...", "sha256": "...", "bytes": 0}
  }
}
```

The example is a schema sketch, not an executable authorized registration.
An `inspect` freeze instead has exactly one input role, `source_packet`.
Native policy names the target, allowed roots, excluded declarations and approved
axioms; `target_root` indexes the independent expression table and
`target_level_params` indexes its ordered universe names. Native checking also
receives the policy's registered heartbeat/recursion envelope through registration.

A check freeze has exactly `schema`, `operation: "check"`, `prepared_receipt`
(file record), `environment_id`, `candidate_packet` (file record), `candidate_root`.
The evaluator authorizes the exact successful preparation receipt, environment ID
and current candidate. A self-consistent replacement receipt is not sufficient.
The checker runtime digest must equal the preparation's registered runtime digest.

## Runtime record

Schema `ocm.proof-environment.runtime.v1` has exactly:

- `executable`, `bwrap`, `host_python`: independently approved file records.
- `libraries`: individual `{ "guest": "/lib/...", "file": <record> }` mounts;
  loader and transitive library closure must be measured from the actual executable.
- `driver_sources`: exact production driver/helper file hashes and sizes.
- `build`: bound `record` plus named source file records in `sources`.

The runtime record includes build provenance; hashing that record does not prove
the build was correct. Final import/link inspection and native controls establish
the qualified scope. No entire toolchain, source directory or `.olean` cache is
needed by a checker that parses packets and reconstructs an empty environment.

## Acceptance and persistence

Preparation success issues one environment ID bound to authorized inputs, runtime
and derived output bytes. The host retains the full provenance outside the checker.
Check dispatch copies only the five fixed input roles into fresh mounts, validates
pre/post custody, complete raw process evidence and exact native output shape, and
rechecks the issuing environment before sealing a passing receipt.

Unexpected stderr, nonzero exit, timeout, truncation, partial/extra output, failed
cleanup, identity drift and ambiguous JSON cannot issue a passing result.
Catchable interruption records surviving artifacts as incomplete and re-raises.
The helper's unreturned local process buffer cannot then support a cleanup/work
claim. Catastrophic host termination is outside this recorder's completion promise.

Inspection/preparation diagnostics and original target identity remain evaluator
records. A future proposer requires a separate reviewed profile that redacts route
identifiers and private diagnostics. This package does not qualify that proposer.
