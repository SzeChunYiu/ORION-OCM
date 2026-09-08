# Source and request contract

## Scope and launch

Entry: `trace_export.py`, Python standard library only.
Sibling modules load explicitly from this directory after byte/hash checks;
isolated startup does not depend on implicit script-directory imports.
The two donor files are unchanged copies. The external mmverify file is pinned
and loaded only after the actual gate, input bindings and source index checks.

The intended future command is:

```text
<bound Python> -I -S -B <capsule>/trace_export.py <bound request.json> <new output directory>
```

The output directory must not exist. The command does not discover corpus files,
invoke a learner or launch the opportunity apparatus.

## Exact request

Schema: `ordinary.training-trace-export-request.v2`.
Exact fields: `schema, ordinals, corpus, python, verifier, prefix, release,
registry_scope, authority_contract, observer_contract, P0_contracts,
gate_path, sources`.

All file bindings except gate_path are `{path, bytes, sha256}`; absolute path,
nonnegative integer byte length and lowercase 64-character SHA256 are required.
`sources` maps exactly the nine production source names in request_contract.py
to `{bytes, sha256}`. The request itself is hash-bound by the gate.
The request template is deliberately invalid until six null fields are supplied.

`ordinals` is exactly the ordered integer sequence 4096 through 4223.
No replacements or winner selection are allowed. The original P0 is a separately
bound list of 4191 ordinary contracts: 96 axioms and the first 4095 theorems.
It must match fresh source contracts and source order exactly.

The corpus, interpreter and verifier identities are fixed in request_contract.py.
Corpus identity is inherited metadata from the release contract; this exporter
reads only the separately released closed prefix, never the corpus path.
The two donor digests are enforced independently of the supplied source manifest.

## Separate prospective authority

The authority-contract input is a new document with schema
`ordinary.native-export-authority-contract.v2` and these exact fields:
`schema, authority_id, status, release, prefix, registry_scope, corpus, python,
verifier, axiom_identities, proof_ordinal_count, base_policy`.

Status is `PROSPECTIVE_NEW_AUTHORITY_CONTRACT`; authority_id is nonempty.
The six file bindings must equal the request. proof_ordinal_count is 4223;
base_policy is `ALL_PREFIX_AXIOMS`. The ordered axiom identities must exactly
equal the release, and the fresh source index must independently match them.
Prefix or axiom drift refuses the run. An older accepted-native flag cannot
replace this new authority contract.

The observer contract is an externally reviewed, exact-bound instrumentation
contract. This entry binds its bytes and requires the gate to bind the same
descriptor; it does not execute that document or self-certify its adequacy.

## Gate

The root-created gate must have authorization
`ROOT_TRAINING_NATIVE_EXPORT_GATE`, request equal to the exact request's
`{bytes, sha256}`, and observer_contract equal to its request descriptor.
It is read only after complete request validation. Missing pins refuse first.
The entry requires the exact interpreter path, isolated/no-site flags and
unoptimized assertions. The gate is a root custody precondition, not a signature
scheme or an automatic qualification of future artifacts.

Registry scope must be `ordinary.registry-scope.v2` with coverage
`DECLARED_REGISTRY_UNIVERSE_ONLY`. The release binds the same descriptor.
The supplied descriptor identifies the lead's 27 metadata records and lineage;
the adapter does not claim a universal allocation census.

## Future stages and retained failures

1. Bind sources, request, gate, runtime, release, registry, original P0 and contracts.
2. Read the exact prefix. Index without include expansion. Check its last theorem,
   closing-scope suffix, all 4223 theorem positions, root identities and dependencies.
3. Run unchanged mmverify over every theorem in the bound prefix with observation
   disabled. Source contracts, selected active variables and DV context must match.
4. In a separate full-prefix native pass, observe released roots with the unchanged
   donor. An observation failure can retry that theorem under unchanged native
   verification with observation disabled; retries and both passes are counted.
5. Build complete P1 before considering trace usability. Bind every ready trace
   and used contract, then recheck every opened input and production source.
6. Emit candidate artifacts requiring separate root qualification.

A native-prefix failure emits no authority/P1/teaching candidate. All known roots
remain in RESULT with failure dispositions. Completed unusable traces and errors
are retained; an interrupted observer need not have a complete trace DAG to save.
A partial observer pass can still produce full P1 because the separate complete
native pass already succeeded. Per-root dispositions make that distinction explicit.

RESULT records actual cwd, PID/PPID, interpreter, entry, argv, helper paths,
input/source custody, native calls, timing and process resource use. Progress
records source-order theorem verification. Retained receipts are part of lifetime
cost accounting; these source controls measure no learning benefit.
