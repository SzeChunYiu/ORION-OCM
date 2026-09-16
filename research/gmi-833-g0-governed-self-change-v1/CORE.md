# GMI #833 E6 — governed self-change and verifier-gated adoption

This capsule separates **proposal**, **external verification**, and **adoption** into distinct typed transitions.

A proposal cannot alter the active machine. Verification binds a candidate digest and base version to an external authority receipt. Adoption is single-use and succeeds only for a current, pending, accepted, correctly bound receipt. Rejection, forgery, staleness and replay leave the active machine unchanged.

The finite verifier predicate `candidate[0] == 0` is only a semantic fixture for authority separation; it is not a universal safety rule and the HMAC-style fixture is not a cryptographic-security claim.

Claim ceiling:

`GMI_FINITE_GOVERNED_SELF_CHANGE_AND_VERIFIER_ADOPTION_AT_REGISTERED_SCOPE`
