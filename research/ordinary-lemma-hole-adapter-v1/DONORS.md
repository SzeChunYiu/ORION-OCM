# Donor mechanism and implementation choice

The adapter follows the argument-hole mechanism documented in
[REFACTOR at 7327ca7](https://github.com/jinpz/refactor/tree/7327ca79f59929d8f8e43b79daeade3a9a6d5aad):
assertion structure is matched recursively while floating/essential leaves accept
whole target subtrees. Repeated variables compare expressions, and emitted
arguments follow mandatory floating then essential order. Structural matching
alone is not a complete type, distinct-variable or native proof certificate.

The [source/design handoff](design/HANDOFF.json) and
[exact upstream read-scope map](design/UPSTREAM-SOURCE-MAP.json) preserve attribution.
The donor's direct imports reach broad graph/scientific packages and torch;
its environment is not the minimal mechanical matcher required here. The earlier
source read established no repository-wide license grant and an inherited GPL
notice in one expansion file. Those scoped observations leave direct source
transplant rights unresolved; no permission or different license is inferred.

The two new modules are independently authored for OCM's existing typed trace
representation. They copy no REFACTOR implementation and import no neural code.
Four existing local files are reused exactly: typed_context, typed_constructor,
typed_emit and a control-only structural fixture. Their original paths/digests
are retained in [the original map](records/original-eight/SOURCE-ORIGINS.json);
[the successor map](records/affected-slot/SOURCE-ORIGINS.json) binds unchanged copies.

Public RAW contains the design documents and source-identity metadata, but omits
all internal donor reading copies and the downloaded upstream tree. Immutable
source URLs and hashes remain available. This is mechanism adaptation with an
explicit future native boundary, not a faithful executable transplant or a new
comparison experiment against the donor.
