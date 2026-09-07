# Qualification and research protocol

## Build and source freeze

Pin lean4export15f6055e299ad5b89345e533cc2192f4cc00f659 and
Comparator3927ad383f208ae977c340a91c48ac9b497d2097, retaining Apache-2.0 sources
and licenses. Compile with Lean4.33.1. Native adaptations are attributed separately;
qualification of the upstream package is not automatically qualification of ours.

Capture toolchain/build inputs, generic checker transitive imports, link inputs,
ELF loader/needed libraries and actual isolated execution. Keep fixture modules out
of the generic checker link closure. A static Lean link does not imply a static
system executable or absence of embedded fixture knowledge.

Development changes and failures are retained outside old frozen experiments.
Before final commissioning, freeze production sources, native fixtures, controls,
runtime and independently registered input bytes. Changes require a successor
identity and rechecking affected controls. Historical receipts remain immutable.

## Required positive controls

Every required positive must execute through the actual fresh native checker:

- Allowed declaration replay with exact membership and identity comparison.
- Independent composition proof against the registered target.
- Polymorphic universe/type transport and checked application.
- Opaque body identity and legitimate application.
- Custom, mutual and nested inductive families; constructors and recursor behavior.
- Projection and Nat/String literal dependencies.
- Registered quotient primitives and regenerated auxiliary declarations.
- Repeated cold checking without source/import/compiled fixture caches.

An unsupported form is a research obstruction, not a passing positive. Authored
proof terms receive no proof-search or learned-method credit.

## Required falsifying controls

Register each semantic variant intact, including its expected hashes, so a stale
digest cannot masquerade as the intended native refusal. Retain the offending
dependency path or exact changed object and the refusal stage.

- Withheld declaration and direct/indirect alias or helper dependencies.
- Hidden dependencies in types, values, instances, opaque bodies and inductive groups.
- Independently changed target/type/universe registration and cross-prepare swaps.
- Same-type axiom replacement and counterfeit familiar primitive identities.
- Missing declarations, incomplete/extra generated families or altered recursor RHS.
- Unsafe/partial declarations and malformed metadata/name/level/expression indices.
- Private unreachable expression/name canaries absent from all emitted allowed tables.
- Changed executable/runtime/source bytes; extra/partial native output and stderr.
- Real checker mount profile without original source, private `.olean`, export or
  route-history access; clean environment, read-only data and complete PID cleanup.

The future proposer receives its own actual profile qualification. It is not
qualified by the checker's containment result.

## Native response contract

The native program is called with exactly `REQUEST.json OUTDIR`; the output
directory must not exist. Its request operation is fixed by the host driver.
Structured native outcomes exit0; unhandled/process failure cannot receive native
proof credit. Stdout is one JSON object identical to `result.json`; stderr is empty.

Result schema `ocm.proof-environment.result.v1` has exactly `schema`, `operation`,
`terminal`, `stage`, `reason`, `stats`, `dependencies`, `axioms`, `files`.
Stats are finite nonnegative numeric counters. The last three fields are unique
string arrays; `files` names the complete output set, including `result.json`.
Successful preparation outputs `permitted.ndjson`, `target.ndjson`,
`registration.json`, `inventory.json`, `result.json`. Failed preparation retains
and declares any partial subset of these files, including `result.json`; it issues
no reusable environment. Inspection/checking output only `result.json`.

## Cost and evidence

Retain exact commands, source/input/runtime hashes, raw stdout/stderr, native result,
host receipt, terminal denominator, named controls and independently verified scope.
Measure outer wall time including final hashing/sealing; driver inner time is
nested and must not be added again. Report CPU/RSS as unmeasured unless collected
with an explicitly stated process/aggregate scope.

Separate acquisition/export, compilation, copying, cold preparation/replay, checking,
index/closure work and retained bytes. Preparation can inspect a large environment;
packet filtering or a small checker namespace is not active-subspace scaling.
Build/control failures remain part of the development/lifetime record.

The current audit driver rehashes the full retained preparation inventory when
authenticating an issued environment, including its evaluator-only source export.
This makes custody work depend on that retained source size even though the native
checker cannot access it. Count this work; a later serving path needs a qualified
immutable/versioned snapshot contract before it can replace full audit per request.

## Next scientific gate

First audit real-corpus semantic coverage with this qualified mechanism. Then freeze
permitted libraries, targets, masks, generic search mechanisms, cost accounting and
matched symbolic parent baselines before scored mechanical reconstruction.

Subsequent acquisition must close the loop: verified episode → explicit method →
checked admission → persistence/restart → causal consumption on held-out tasks.
Measure harmful transfer and equally adaptive parents. Only that evidence can
support the central thesis that persistent executable knowledge improves future
cognition. FLT route-free generation and open-ended language remain later claims.
