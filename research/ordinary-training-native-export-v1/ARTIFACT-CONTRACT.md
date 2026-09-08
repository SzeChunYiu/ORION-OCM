# Artifact boundary

Canonical object hashes use JSON with sorted keys, compact separators,
ensure_ascii=true, allow_nan=false, UTF-8 and one final newline.
File descriptors are `{path, bytes, sha256}`; canonical object identities omit path.

## Full ordinary inventory

`P1-INVENTORY.json`, schema `ordinary.native-P1-inventory.v2`, exact fields:
`schema, release, native_trace_authority, inventory_policy, base_labels,
released_labels, contracts`.

inventory_policy is
`ALL_PREFIX_AXIOMS_PLUS_P0_THEOREMS_PLUS_RELEASED_TRAINING_THEOREMS`.
contracts is an ordered list of every prefix axiom, original first4095 theorem,
and RELEASED next128 theorem. No excluded theorem enters P1. An ordinary contract
has exactly `label, kind, statement, floating, essential, dv`.
base_labels includes every prefix axiom plus P0 theorems, in source order.
released_labels follows released ordinal order.

`P0-CONTRACTS.json` preserves the separately bound original P0 list.
Additional prefix axioms appear in full P1 and the new authority; they do not
silently alter the original 4191-contract P0.

## Teaching packet and rows

`TEACHING-PACKET-CANDIDATE.json`, schema `ordinary.training-trace-packet.v2`,
exact fields: `schema, release, ordinals, roots, native_trace_authority, P1_inventory`.
It retains all 128 root positions.

Each row has exactly `ordinal, label, source_disposition, whole_contract,
trace_disposition, trace, contracts`.

| Source / trace disposition | Whole contract | Trace / contracts |
| --- | --- | --- |
| RELEASED / TRACE_READY | canonical P1 ordinary contract identity | full donor trace / used-label map |
| RELEASED / TRACE_UNUSABLE | same whole contract identity | null / empty object |
| Either EXCLUDED status / EXCLUDED | null | null / empty object |

Each used `$f/$e` contract has exactly `label, kind, statement, span`.
Each used `$a/$p` contract has the ordinary six fields plus `span`.
Spans come from the exact source index. Every used contract starts before its
source theorem. Referenced ordinary contracts carry no proof bodies or raw
histories. Their six-field projections agree with allowed P1.

TRACE_READY requires an observer-produced trace, 1–256 nodes, no source/active/
used-contract DV, and all used hypotheses to match the source theorem's mandatory
floating/essential lists. These are necessary transport/interface prerequisites,
not a declaration of cut eligibility. The unchanged constructor still checks its
other bounds, typed interface, graph and reconstruction requirements.

Native-valid proofs using extra active floating hypotheses outside the mandatory
list become TRACE_UNUSABLE here. Their whole theorem remains in P1.
Completed such traces are retained only in `CUSTODIAN-UNUSABLE-TRACES.json`,
with reasons, never as learner input. Other absence/error reasons are retained in
authority dispositions and process RESULT. No cut-size search or outcome filter
is used to select packet rows.

## Fresh native authority

`NATIVE-AUTHORITY.json` has schema `ordinary.native-prefix-authority.v2`,
terminal `FRESH_PREFIX_NATIVE_VERIFIED`, proof_ordinal_count 4223 and
verified_labels in exact source order. It binds:
release, prefix, registry_scope, authority_contract, P0_contracts, corpus, python,
verifier and all production sources.

It also records all ordered prefix axioms as `{contract, raw}`,
additional_axiom_labels relative to original P0, and selected_scope_bindings
for every released root: whole contract identity, source/proof raw identities,
active_variables and active_dv.

For each TRACE_READY root, `trace_bindings[label]` contains `trace` and
`contracts` canonical object identities. This covers hypotheses and exact spans.
`trace_dispositions[label]` records `{status, reason}` for every released root.
trace_stage distinguishes COMPLETE from PARTIAL_OR_UNUSABLE.
admission is `SEPARATE_ROOT_QUALIFICATION_REQUIRED`;
old_native_receipt_inherited is false.

The consumer must bind the qualified authority and full P1 independently, match
all release/registry/prefix identities, require exact verified-label order, and
check each ready trace and contract-map identity. Hypotheses compare against the
source mandatory context; ordinary contract projections compare against P1.
Authority binding supplies exact source-span custody; mere source-order
inequalities are not substitutes for matching those hashes.

This packet/authority design grants no theorem discovery, language transfer or
empirical-truth claim. Native checking establishes formal derivability within the
declared new axiom/prefix contract; cut learning is a separate gated apparatus.
