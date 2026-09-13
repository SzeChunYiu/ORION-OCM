# V4 execution registration, preserving unexecuted V3

V3 was committed before timing in PR #527. Publication recorded content commit
`6ee679f4ff108bfab9817fda3c8d95b26edb6356`, followed by empty merge commit
`7eff0a4b8f53903a0799ff81ef422fafb3b6f931`. GitHub's run API reported no V3
measurement run for either SHA when checked before this registration. The
path-filtered measurement therefore supplied no outcome. We do not infer the
reason for the missing event or fabricate a hosted measurement.

Review also found that V3's inherited `scientific_scope` string still said
"two" although its actual candidate register, code, selection rule and design
correctly specified four. V4 corrects that description and creates a new
execution identity. V3's source, registration and workflow remain unchanged;
V3 is unexecuted evidence, not a failed prediction or a measured negative result.

The complete V3 construction and proof in `PARITY3_CANDIDATE_EXPANSION_V3.md`
apply unchanged. Candidate IDs and AST hashes, all arithmetic and tracing code,
32-block schedule, resource coordinates, family-neutral robust-frontier rule,
development exclusions and expectation are identical. Tests check this complete
instrument identity modulo version labels and validate the corrected registration.
No timing outcome was observed or used to choose this recovery.

Only V4's first main-push attempt may supply its registered timing. Its complete
packet will be retained regardless of family winner or abstention. The existing
V1/V2 outcomes and V3 registration remain addressable. Independent optimization,
prospective replication, population resource bounds and universal family claims
remain outside this finite expansion.

The source-bound theorem workflow now watches V3 and V4 workflow paths directly,
closing a separate trigger omission: a change to one of those bound workflows
must invoke the capsule even when no research file changes.
