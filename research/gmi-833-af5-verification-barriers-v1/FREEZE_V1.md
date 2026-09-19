# AF5 pre-implementation freeze — verification barrier displacement

Status: **FROZEN BEFORE EXECUTOR / RESULTS / SELECTION OUTCOMES**

Issue authority: #833 AF addendum comment `5693269426`, section AF5.

Base `main`: `ed736cd332eabfc8d60965e53fce8881627bbdc0`.

This tranche targets AF5 only. AF6+ remains open.

## Expert lanes

1. **Computability / semantic verification** — exact unrestricted no-go assumptions stay parent-owned (Rice/halting and the repository HST-T15 boundary).
2. **Static analysis / abstraction refinement** — sound incomplete abstract interpretation and CEGAR are imported with false-alarm/refinement semantics intact.
3. **Certificates / model checking / property testing** — proof-carrying certificates, bounded checking and randomized approximate decisions are distinct output/interaction contracts.
4. **Resource/hostile review** — construction/checking/failed-refinement cost is explicit; false positives, false negatives, nontermination and abstention cannot be laundered into one success bit.

## Frozen parent authorities

Repository parents:

- `research/gmi-833-af-barrier-context-v1/GMI_BARRIER_PARENT_LEDGER_V1.json` blob `8089a47975ae6ca0489c5198b6a56c14da8d9b65`.
- `research/gmi-833-af-barrier-context-v1/FORMALIZATION_V1.md` blob `de2f2552bb6d5787317921f9c42c82dab2df1952`.
- `research/heritable-search-transformation-v1/HST_THEOREM_REGISTRY_V1.json` blob `5b94d66a8d8d2196a518fd7ac8d1da83663e42a4`.

External anchors:

- Rice/Turing and Baldan–Ranzato–Zhang 2022 `Intensional Kleene and Rice Theorems for Abstract Program Semantics`, Information and Computation 289, 104953: nontrivial semantic classification keeps exact parent assumptions visible.
- Cousot/Cousot abstract interpretation: sound approximation can terminate and prove properties without missed concrete behaviours, but incompleteness/false alarms remain under undecidability.
- Clarke–Grumberg–Jha–Lu–Veith, CAV 2000 / JACM 2003 CEGAR: spurious abstract counterexamples trigger refinement.
- Necula, POPL 1997 Proof-Carrying Code: certificate producer supplies evidence checked against a trusted safety policy/checker.
- Biere/Cimatti/Clarke/Fujita/Zhu 1999 bounded SAT model checking: finite-bound exploration is a bounded contract, not unrestricted proof.
- Goldreich property testing: randomized approximate decision distinguishes property membership from being far from the property using partial access.

## AF5-P1 — unrestricted semantic-verification no-go [PARENT_OWNED]

At the registered classical scope, no automatic terminating procedure can correctly decide every nontrivial semantic property for every unrestricted program. AF5 does not re-prove or rename this theorem.

A transition from this status is scientifically legitimate only by changing a registered axis: restricted fragment/domain, semidecision, certificate/witness, sound incomplete approximation, bounded horizon/model, probabilistic approximate contract, interaction/refinement, list/set output, or explicit abstention.

## Verification guarantee lattice

Define atomic guarantees:

```text
SOUND_ACCEPT
SOUND_REJECT
TERMINATES
COMPLETE_AT_REGISTERED_SCOPE
CERTIFICATE_CHECKED
BOUND_EXPLICIT
EPS_DELTA_EXPLICIT
ABSTENTION_EXPLICIT
```

The full powerset ordered by subset is the formal finite guarantee lattice. Named verification statuses are registered points in this lattice; no total ranking is implied.

Required named statuses:

```text
UNRESTRICTED_UNDECIDABLE
DECIDABLE_RESTRICTED_FRAGMENT
SEMI_DECISION_BUG_WITNESS
CERTIFIABLE
SOUND_INCOMPLETE_APPROXIMATION
CEGAR_REFINED_CERTIFIABLE
BOUNDED_MODEL_CHECKED
PROBABILISTIC_PROPERTY_TEST
UNKNOWN_ABSTAIN
```

Every result record must state domain/horizon, soundness, completeness, termination, possible false-positive/false-negative semantics, and resource vector.

## Frozen exact fixtures

### V1 — finite restricted exact decision

Finite transition systems with at most four states are exhaustively reachable by BFS. Registered safety is exact: bad reachable => REJECT, otherwise ACCEPT. This demonstrates a domain restriction, not defeat of unrestricted Rice/halting.

### V2 — certificate-producing/checking machine

Concrete system `s0 -> s1 -> s2`, with unreachable `bad`. A safety certificate is an inductive invariant set containing `s0`, closed under transitions, and excluding `bad`. Construction and checking resources are separate. Tampered certificates fail closed.

### V3 — sound incomplete abstraction

The same safe concrete system is abstracted by merging `s2` with `bad`. The abstract analyzer is sound but cannot prove safety because the over-approximation reaches the merged bad block. Terminal: `UNKNOWN_FALSE_ALARM_POSSIBLE`, never `UNSAFE`.

A second exact abstraction separating `bad` proves safety and returns `SOUND_INCOMPLETE_APPROXIMATION` with a successful proof at this fixture.

### V4 — CEGAR refinement

Start from the V3 coarse abstraction. Detect that the abstract bad trace is spurious against the concrete system, refine the block by separating `bad`, then prove safety. Record one refinement, failed/spurious-path cost, and final certificate/check cost. No universal CEGAR termination claim.

### V5 — bounded model checking

A deterministic path reaches `bad` first at step 4. Bound `k=3` returns `NO_BUG_FOUND_WITHIN_BOUND`, not VERIFIED; `k=4` returns an exact bug witness. Bounded no-bug is not a proof beyond the bound.

### V6 — probabilistic property testing

Property: an 8-bit object is all-zero; negative promise: object has at least four ones. Tester samples 3 distinct coordinates without replacement and rejects if any sampled bit is one. For a frozen exactly-four-ones negative, rejection probability is `13/14` by exact subset enumeration. This is an approximate randomized contract and does not decide arbitrary bitstrings exactly.

### V7 — semidecision and abstention

Witness search is sound for bugs and terminates when a bug witness is found; absence may remain `UNKNOWN`. `UNKNOWN`/abstention is machine-distinct from SAFE/UNSAFE.

## Verification-resource selection microscope

Two verification organizations satisfy the same finite safety contract:

```text
DIRECT_REPLAY: nonverification base cost 3, verification burden 8
CERTIFICATE_EMITTER: nonverification base cost 5, proof-construction+check burden 6
```

For frozen scalarized diagnostic `base + w_v * verification`:

- `w_v=1/10`: DIRECT_REPLAY wins (`19/5 < 28/5`);
- `w_v=1`: tie (`11=11`);
- `w_v=2`: CERTIFICATE_EMITTER wins (`17 < 19`).

Raw resource vectors remain primary. This fixture shows that making verification a protected priced coordinate can change selected organization; it is not a universal morphology law.

## Frozen hostile battery

At least these must fail closed:

1. unrestricted no-go relabeled false after restricting to a finite fragment;
2. abstract false alarm relabeled concrete UNSAFE;
3. unsound abstraction accepted as proof;
4. certificate with missing initial state;
5. certificate not closed under transition;
6. certificate containing bad state;
7. proof construction and checking cost collapsed into free verification;
8. CEGAR spurious trace counted as concrete bug;
9. CEGAR refinement claimed universally terminating;
10. BMC k=3 no-bug result promoted to unbounded safety;
11. probabilistic tester promoted to exact decision;
12. missing epsilon/delta or sample contract in property-test receipt;
13. semidecision unknown promoted to safe;
14. abstention counted as success;
15. morphology/organization winner forced at the registered tie `w_v=1`;
16. parent/source/pin drift.

## Deliverables

Post-freeze: formalization, parent ledger, deterministic executor, independent oracle, 16+ hostiles under normal/optimized Python, result receipts, open gaps, check-only AF5 reconciliation, README, dedicated CI.

## Claim ceiling

`GMI_AF5_VERIFICATION_CONTRACT_DISPLACEMENT_AND_RESOURCE_SELECTION_AT_REGISTERED_FINITE_SCOPE`.

Forbidden: `RICE_THEOREM_FALSE`, `UNRESTRICTED_SEMANTIC_VERIFICATION_SOLVED`, `SOUND_AND_COMPLETE_AUTOMATIC_VERIFICATION_UNIVERSAL`, `FALSE_ALARM_IS_BUG`, `BOUNDED_NO_BUG_IS_UNBOUNDED_PROOF`, `PROPERTY_TEST_IS_EXACT_DECIDER`, `CERTIFICATE_CONSTRUCTION_FREE`, `CEGAR_ALWAYS_TERMINATES`, `UNIVERSAL_VERIFICATION_MORPHOLOGY`, `COMPLETE_GMI`.
