# GMI #833 presentation-relabeling equivariance v1 — freeze

Parent issue: #833. Programme comment: 5687604615.  
Base main: `115145b60bae9d066d583a4c5d877ee59eb527ab` (TRANS-1/DIST-1 and TRANS-2 merged).

## Frozen theorem target: GAUGE-1A

At a finite deterministic registered scope, represent a mechanism by architecture-name-free semantic structure:

- finite reachable state set and initial state;
- finite action alphabet;
- protected output labels;
- deterministic transition law;
- registered intervention-response labels;
- developmental/reachability edges;
- raw lifecycle resource vector.

A **presentation relabeling** is a bijection on state identifiers that transports every state-indexed semantic component and leaves the external action/output/intervention alphabets and raw resource vector unchanged.

Prove/check:

1. valid relabelings form a finite groupoid under identity, inverse, and composition;
2. a canonical presentation-independent mechanism fingerprint is invariant under every valid relabeling;
3. two pure relabelings therefore land in the same registered mechanism quotient class;
4. a finite transformation graph whose endpoints are relabeled mechanisms and whose transform burdens are unchanged has the same quotient-level directed shortest-burden matrix after canonicalization;
5. non-bijective maps, resource mutation, output mutation, transition mutation, intervention mutation, developmental-edge mutation, and state-image escape fail the relabeling-preservation audit;
6. syntax/name cleanliness is insufficient: a neutral rename coupled to any semantic mutation is RED;
7. relabeling invariance does **not** imply search/reachability invariance when proposal order, encoding length, optimizer trajectory, or budget changes; that remains a separate gate.

## Frozen proof boundary

The canonical fingerprint may use exhaustive state permutations because this tranche is explicitly finite. The analytic invariance proof must explain why transport by a bijection permutes the candidate canonical encodings without changing their minimum; enumeration is a certificate, not the universal proof.

Expected claim ceiling if GREEN:

`GMI_FINITE_SEMANTIC_REMINT_EQUIVARIANCE_AT_REGISTERED_SCOPE`

Forbidden promotions include universal grammar neutrality, search-prior invariance, P3 recovery, unrestricted topology invariance, and complete GMI.
