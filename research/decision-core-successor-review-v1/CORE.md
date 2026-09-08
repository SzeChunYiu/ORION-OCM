# Decision-core successor source review

**Decision:** adopt the bounded stopping model and whole-fiber decision criterion;
repair three source defects before treating this module as exact authority.
No study, imported PR module, verifier, learner, or test was executed.

Reviewed PR154 head: `c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`.
Tree: `05fef3d2bafe7acd6e6a89fbaf610171381b052c`.
The four reviewed blobs are unchanged from the first inspected head
`e7d3cd067510c3a4a69568e5f4cf95554e455eb8`.

- **Resolved within the new finite model:** Theorem 9 spends one cognition step
  per transition and forces stopping at zero. Nonnegative/zero costs no longer
  produce the old unselected fixed-point problem.
- **Corrected within the new text/test:** a common safe action permits acting;
  economic stopping still compares its cost with paid computation.
- **Still unresolved:** numerical exactness, including literal transition-law
  equality and forced float conversion of finite integer costs.
- **New mathematical correction:** Lemma 8 conditions on future adaptive probe
  choices; its displayed chain-rule identity is false under ordinary conditioning.

Read [findings](FINDINGS.md), [resolution and adoption decisions](RESOLUTION.md),
and [read scope](READ-SCOPE.md). Smaller API-contract fixes are explicitly queued
in [follow-ups](FOLLOW-UPS.md). Raw bindings are in [review receipt](REVIEW.json),
[Fetched sources](FETCHED-SOURCES.json), and [closing metadata](CLOSING-METADATA.json).

This qualifies four source files, not the current whole PR, later convergence
claims, a numerical population, or experimental outcomes. Root owns publication.
