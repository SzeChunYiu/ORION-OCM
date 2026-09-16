# Governed self-change theorems v1

## Expert review lanes

- **Formal transition semantics:** active/pending/consumed state and version lineage.
- **Assurance / authority:** externally minted, digest- and base-bound receipts.
- **Developmental systems:** accepted proposals become explicit versioned successors; rejection is inert.
- **Hostile verification:** replay, staleness, candidate swap, forged authority/signature/decision and rejection laundering.

## PROP-1 — proposal inertness

`PROPOSE(candidate)` appends a pending proposal bound to the current active version and candidate digest. It does not change the active behavior or active version. Exhaustive certificate: all 27 maps over `Z3` preserve the base active machine exactly at proposal time.

## VER-1 — external verification boundary

The frozen external verifier applies `candidate[0]==0`, yielding exactly 9 ACCEPT and 18 REJECT receipts over the complete 27-candidate space. The receipt binds authority ID, proposal ID, candidate digest, base version and decision. Proposal objects contain neither a signature field nor verifier secret.

The HMAC-style signature is only an executable authority-separation fixture; no cryptographic-security theorem is claimed.

## ADOPT-1 — verifier-gated single-use adoption

For every accepted candidate from version 0, a correctly bound ACCEPT receipt installs exactly that candidate, increments version exactly once, and consumes the proposal. All 9 accepted candidates pass. Reapplying the same proposal/receipt returns `PROPOSAL_ALREADY_CONSUMED` with exact state preservation.

For every rejected candidate, adoption returns `REJECTED_BY_VERIFIER`; all 18 preserve active behavior/version exactly.

## ADOPT-2 — base-version freshness

A proposal/receipt bound to base version `v` may not modify an active machine at version `v+1`. The exact hostile creates two accepted proposals at base 0, adopts one, then proves the second fails `STALE_BASE_VERSION` against active version 1 without mutation.

## ADOPT-3 — binding integrity

Authority mismatch, signature corruption, decision tampering, digest/base mismatch and candidate substitution are machine-distinct fail-closed terminals. A forged ACCEPT for a candidate the verifier policy rejects fails before adoption. No failure path writes active behavior or version.

## DEV-1 — finite versioned development

A two-generation control establishes a genuine versioned successor path:

`identity v0 -> (0,2,1) v1 -> (0,2,2) v2`.

The second proposal is created only after v1 and its receipt binds base version 1. This establishes finite governed developmental transition semantics, not recursive self-improvement or optimal development.

## RES-1 — raw governance resources

Resource vector:

`(proposals_written, verifier_calls, candidate_checks, adoption_attempts, active_writes, version_increments)`.

- PROPOSE `(1,0,0,0,0,0)`
- VERIFY `(0,1,1,0,0,0)`
- ADOPT success `(0,0,0,1,1,1)`
- ADOPT failure `(0,0,0,1,0,0)`

## Falsifiers

Any proposal-time active mutation, accepted replay, stale adoption, rejected active mutation, candidate/receipt swap acceptance, proposal-minted authority, or version increment without successful adoption makes the tranche RED.
