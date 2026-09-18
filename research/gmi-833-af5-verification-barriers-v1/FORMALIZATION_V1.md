# AF5 formalization V1 — verification barrier displacement

Freeze: `397b6bd3e78e59ffb359291c2e9ecb75f7e73061`.
Claim ceiling: `GMI_AF5_VERIFICATION_CONTRACT_DISPLACEMENT_AND_RESOURCE_SELECTION_AT_REGISTERED_FINITE_SCOPE`.

AF5 does not overturn Rice/halting. It asks which registered verification contract is being used and what guarantees/resources it earns.

## Parent no-go

The unrestricted total automatic classifier for every nontrivial semantic program property is parent-forbidden at the classical scope. Finite restriction, semidecision, certificates, abstraction, bounded exploration, randomized approximate testing and abstention are changes in domain/output/interaction guarantees, not contradictions.

## Verification guarantee lattice

Atomic guarantees are `SOUND_ACCEPT`, `SOUND_REJECT`, `TERMINATES`, `COMPLETE_AT_REGISTERED_SCOPE`, `CERTIFICATE_CHECKED`, `BOUND_EXPLICIT`, `EPS_DELTA_EXPLICIT`, `ABSTENTION_EXPLICIT`.

Their full powerset ordered by subset is the formal finite lattice. Named verification statuses are points in that lattice; there is deliberately no total ranking across all methods.

The registered points cover unrestricted undecidable, finite exact, bug semidecision, certificate checking, sound incomplete abstraction, refined CEGAR certification, bounded model checking, probabilistic property testing and explicit unknown/abstention.

## Exact microscopes

The finite system `s0 -> s1 -> s2` has unreachable `bad` and is exactly safe. The invariant `{s0,s1,s2}` is independently checked for initial inclusion, transition closure and bad exclusion; proof construction and checking costs remain separate.

A coarse sound abstraction merges `s2` with `bad`. Because the over-approximation reaches the merged block it returns `UNKNOWN_FALSE_ALARM_POSSIBLE`, not UNSAFE. Refining the block separates `bad`; the same concrete system is then proved safe. This is a one-refinement CEGAR fixture, not a universal termination theorem.

A second path reaches `bad` first at step 4. BMC at `k=3` returns `NO_BUG_FOUND_WITHIN_BOUND`; `k=4` returns a real witness. No-bug at a finite bound is never promoted to unbounded safety.

For property testing, the 8-bit property is all-zero and the frozen negative has exactly four ones. Sampling three distinct coordinates rejects with exact probability `13/14`, so `delta=1/14` at the frozen promise. This remains randomized approximate decision, not exact classification.

Witness semidecision is sound for found bugs but the safe fixture remains explicit UNKNOWN rather than SAFE.

## Verification cost as protected resource

Two candidate verification organizations satisfy the same finite safety contract. Raw vectors are retained:

- `DIRECT_REPLAY=(base=3,direct_verification=8,proof_construct=0,proof_check=0)`;
- `CERTIFICATE_EMITTER=(base=5,direct_verification=0,proof_construct=5,proof_check=1)`.

Under the preregistered diagnostic `base + w_v * verification_burden`, direct replay wins at `w_v=1/10`, the complete argmin set is a two-way tie at `w_v=1`, and certificate emission wins at `w_v=2`. Verification price can therefore change selected mechanism structure at this fixture; no universal architecture law follows.

## Claim discipline

A false alarm is not a bug; an incomplete analyzer's UNKNOWN is not SAFE; a bounded no-bug result is not unrestricted proof; a probabilistic tester is not an exact decider; certificate construction is not free; CEGAR is not asserted universally terminating. AF6+ remains open.
