# GMI #833 E6 — governed self-change freeze v1

**Parent:** #833 Section E  
**Child:** #889  
**Source main:** `88d8ac811f80dd3f5c0b1a20f53fdf7259e3ca9c`  
**Status:** pre-implementation theorem/evidence freeze

## Boundary

This tranche formalizes finite proposal/verification/adoption transitions only. It does not prove recursive self-improvement, autonomous authority, verifier infallibility, arbitrary-code safety, self-change optimality, unbounded development, or self-editable constitution.

## Registered machine

Active behavior is a deterministic map `f:Z3->Z3`, represented by a length-3 tuple with values in `Z3`, plus integer `version>=0`.

Base machine: identity map `(0,1,2)`, version 0.

Candidate space: all `3^3=27` maps.

## Typed transitions

- `PROPOSE(candidate)`: create `Proposal(candidate,digest,base_version,pending=True)`; active map/version are unchanged.
- `VERIFY(proposal)`: an external verifier applies the frozen predicate `candidate[0]==0` and emits an externally typed receipt `(digest,base_version,decision,authority_id)`. The proposal cannot construct this receipt through the proposal API.
- `ADOPT(machine,proposal,receipt)`: succeeds iff proposal is pending, receipt authority equals frozen `VERIFIER_V1`, decision is `ACCEPT`, receipt digest equals proposal digest, receipt base version equals proposal base and current active version, and current proposal candidate still hashes to the bound digest. Success installs candidate, increments version exactly one, and consumes proposal/receipt.
- Any rejection, mismatch, stale receipt or replay fails closed without active mutation.

The verifier predicate is a finite witness policy, not a universal safety criterion.

## Exact finite certificate

1. Enumerate all 27 candidates: exactly 9 satisfy `candidate[0]==0`; exactly 18 reject.
2. Proposal inertness: for all 27 candidates, PROPOSE leaves active map/version exact.
3. Accepted adoption: all 9 accepted candidates adopt once from base version 0 and produce version 1 with exact candidate behavior.
4. Rejected adoption: all 18 rejected candidates cannot adopt and leave base exact.
5. Replay: after successful adoption, the same receipt/proposal cannot adopt again.
6. Staleness: after one accepted adoption, any receipt bound to version 0 is rejected against version 1.
7. Candidate swap: a receipt for candidate A cannot authorize candidate B.
8. Forged ACCEPT for verifier-rejected candidate is rejected because receipt authenticity/decision is externally validated.
9. Two-generation control: identity v0 -> accepted swap(1,2) v1 -> accepted map `(0,2,2)` v2, each with its own receipt bound to its own base version.

## Receipt authenticity

The external verifier uses a deterministic HMAC-like fixture signature `sha256(secret || authority_id || base_version || digest || decision)` with a secret held only by the verifier object. The proposal API never receives that secret. This is an executable authority-separation fixture, not a cryptographic-security claim.

## Raw resource vector

`(proposals_written, verifier_calls, candidate_checks, adoption_attempts, active_writes, version_increments)`.

- PROPOSE `(1,0,0,0,0,0)`
- VERIFY `(0,1,1,0,0,0)`
- ADOPT success `(0,0,0,1,1,1)`
- ADOPT failure `(0,0,0,1,0,0)`

## Hostiles

Reject: malformed candidate, negative version, forged authority id, forged signature, decision tampering, digest mismatch, candidate mutation/swap, base-version mismatch, current-version mismatch, rejected decision, replay, double adoption, consumed proposal, proposal-created fake receipt.

## Claim ceiling

`GMI_FINITE_GOVERNED_SELF_CHANGE_AND_VERIFIER_ADOPTION_AT_REGISTERED_SCOPE`

Forbidden: `RECURSIVE_SELF_IMPROVEMENT_PROVED`, `AUTONOMOUS_SELF_AUTHORITY`, `VERIFIER_INFALLIBLE`, `ARBITRARY_CODE_SAFE`, `SELF_MODIFICATION_OPTIMAL`, `UNBOUNDED_DEVELOPMENT`, `CONSTITUTION_SELF_EDITABLE`, `COMPLETE_GMI`.

## Reconciliation

Only after exact-head PR CI is green may this child change:

- `Add self-modification/development operators.`
- `Add verifier-gated adoption operators.`
