# Bounded source interface
## Modules
hole_match.match accepts the body, its ordinary contracts, exact lemma contract,
target trace/used contracts, one target node, parameter context and work dictionary.
It checks canonical input identities, replays target stack/events using the copied
typed_constructor, validates the body with copied typed_emit, and matches ordered
assertion ports. Pattern float/hole leaves bind whole target subtrees.

replacement.emit_one redoes the exact match and compares the entire binding.
It resolves the supplied child-port occurrence path and functionally emits one
replacement. It emits floating arguments in the lemma contract's order, essential
arguments in slot order, then the lemma label. Other shared occurrences remain
expanded; the original graph is not mutated.

Neither module imports the native verifier, donor REFACTOR, parser or miner.
The caller sets the root and vendor import paths explicitly; qualification binds
the actual imported files. SOURCE-ORIGINS records four unchanged copies:
typed_context, typed_constructor, typed_emit and the authored fixture helper.
The fixture helper is used only by tests.

## Input and output scope
Three homogeneous wff or class parameters; empty source/active/applied DV;
at most 256 target nodes; 2–8 semantic body applications; 4,096 normal proof labels.
The old constructor also rejects zero-arity assertion steps; that transport
interface remains outside this qualification.

Composite and repeated ordinary substitutions are accepted when target subtree
outputs provide the exact syntax witnesses. Atomic renaming is used only for
identity replay of the already-typed target. The body recipe is validated under
its declared native parameter context; no composite renaming is forced through
the older atomic-bijection recipe API.

Repeated variable appearances require equal typed token expressions, not equal
proof-node IDs. Repeated hole slots require equal statements; distinct equal-
statement slots remain distinct and ordered. Every matched node's substituted
output and every essential obligation must agree exactly.
Missing mandatory float witnesses and explicit unsupported DV/float/node scope
return UNKNOWN. A supported pattern/target mismatch returns local NO_MATCH.
Malformed/unreplayed inputs or failed emission return CANNOT_CHECK.
No local mismatch is a certificate covering all patterns, target nodes or proofs.

The context's library/native-authority identities are caller-supplied pins, not
authority issued by this adapter. Native readiness is never inferred from them
or from a saved trace terminal. Structural replay is necessary but insufficient
for native acceptance. Current admission/source/registry liveness and actual
native replacement checking remain the future caller's responsibility.

The binding records substitutions and argument node indices against exact input
identities. Emission returns the original root statement, newly named ordered
external hypotheses, normal proof labels, chosen path, distinct reached target
nodes, expanded source application occurrences and one replacement application.
Those distinct-node and emitted-occurrence quantities are not interchangeable.

## Remaining native boundary
A separately registered call must bind the exact eligible lemma and its proof,
current extended prefix with unchanged axiom inventory, original target statement,
type/essential/DV context and the whole new proof bytes. No original target-label
shortcut or unissued proof label is permitted. Source trace admission must come
from the existing current native transport; this adapter did not recreate it.
The earlier life_native wrapper is usable only within its actual issued context
and freshly bound authority; a wider native wrapper needs separate qualification.
No corpus/native execution is authorized by this source artifact.
