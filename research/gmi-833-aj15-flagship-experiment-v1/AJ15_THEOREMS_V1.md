# AJ15 flagship experiment — named results

Package `gmi-833-aj15-flagship-experiment-v1`; freeze `793e3548`; `source_main f1e150ea`.
Every number below is read from the committed receipts (`RESULT_V1.json` and the five stage
receipts it merges). Exact integers and rationals throughout; no float appears in any receipt.
Claim ceiling: `AJ15_FLAGSHIP_END_TO_END_EXECUTED_WITH_FAMILY_REGISTRY_HIDDEN_AT_REGISTERED_FINITE_B1_AND_B2_SCOPES`,
strictly under the AJ9 aggregate ceiling and `FGS-4`.

## FX-1 — bounded flagship on B1: predictions confirmed on every regime, two routes agree

**Statement.** Over the 260-presentation universe B1 (148 operational classes, 33,670 pair
checks, 1,624 equivalent pairs, canonical atlas SHA-256 `09a99f29d2d349d7…`), with the AJ9a
registry hidden from generation, search and evaluation, every exact solver of every regime is
enumerated and the frozen regime prediction holds: in the three memoryless-realizable regimes
(`identity`, `not`, `const0`) 0 of 29 exact solvers have a reachable-state-dependent output; in
the two non-memoryless regimes (`delay1`, `toggle`) 1 of 1 does. Post hoc, the frozen K02
fingerprint passes on exactly those solvers (0/29, 0/29, 0/29, 1/1, 1/1) and the post-hoc
outcome vector agrees with the prediction table. Route A (tuple presentation, product-state
equivalence) and route B (string presentation, trace signatures on words ≤ 3) return the same
counts, ids, classes, front `[M000, M001, M002, M043, M169]` and digest.

**Scope.** B1 only; the five frozen tasks on words of length ≤ 4; deterministic one- and
two-state step tables over a binary alphabet.

**Quantifiers.** For all 260 presentations and all 5 regimes; for all 31 protected words.

**Assumptions.** Finite value sets and extensional equality of words; classical finite
reasoning; the task family is a value input; the registry blob `6b9ac309…` is the post-hoc
adjudicator and nothing else.

**Dependencies.** `gmi-833-aj11-bounded-completeness-v1` (universe and digest),
`gmi-833-aj9a-known-family-benchmark-v1` (frozen fingerprints), `FREEZE_V1.md` §2.3
(prediction table), `SEARCH_CONFIG_V1.json`.

**Falsifiers.** Any exact solver of `identity`, `not` or `const0` with a reachable-state-dependent
output; any exact solver of `delay1` or `toggle` without one; any disagreement between the two
routes on a count, an id or the digest; a post-hoc fingerprint outcome that differs from the
reachable-state count. Hostile `H3` shows the verdict flips to `FALSIFIED` on an inverted
prediction; `H5` shows a truncated window inflates the `delay1` solver count from 1 to 65 and
that 64 are rejected by the full-window check; `H6` shows one perturbed atlas row changes the
digest.

**Strongest parents.** Deterministic finite transducer equivalence and minimization
(automata theory); the AJ11 exhaustive atlas; the AJ9a holdout contract; `FGS-4`
(`gmi-833-h-family-gate-soundness-v1`) for the boundary on family identity.

**Forbidden extrapolations.** `NAMED_FAMILY_RECOVERED` — the fingerprint is satisfied at scope,
the historical family as such is not recovered; `FAMILY_IDENTITY_FROM_OPERATIONAL_EQUIVALENCE`;
`PREDICTED_SELECTED` (the AJ9 contract's terminal is not claimed for any family); any
statement about universes other than B1.

## FX-2 — the UNKNOWN channel is live in the same run and every UNKNOWN candidate is parent-reduced

**Statement.** The same run produces both registered-fingerprint recovery (2 solvers at B1,
2 at B2) and non-registered outputs: 88 exact solvers (29 + 29 + 29 at B1 and the B2 `identity`
solver) match no registered fingerprint, enter the `UNKNOWN` channel with `registered_family:
null`, and after strongest-parent review all 88 are `PARENT_REDUCED_KNOWN` (a literal one-symbol
Boolean map or constant, or such a map with an inert reachable state). No novel form is
claimed; the replication gate is `NOT_TRIGGERED_NO_NOVEL_CLAIM`.

**Scope.** The exact solvers of the nine regimes actually run (five at B1, four at B2).

**Quantifiers.** For all 88 non-matching solvers; for all 10 registered families whose
fingerprints are not definable in a step-table universe, the reason is recorded per family.

**Assumptions.** Only K02's fingerprint clauses are operationally definable over step tables;
the other ten require structure (multiple sites, expressions, distributions, populations,
queries, self-change) that no presentation of B1 or B2 possesses — recorded, not assumed
silently.

**Dependencies.** `POSTHOC_RESULT_V1.json`; the AJ10 protocol (`gmi-833-aj10-prospective-unknown-v1`)
whose five-step post-hoc order this package follows.

**Falsifiers.** A solver placed in `UNKNOWN` that a registered fingerprint in fact matches; a
`PARENT_REDUCED_KNOWN` verdict without a named parent; a `NOVEL_AT_REGISTERED_SCOPE` outcome
(which would have required independent replication before any claim).

**Strongest parents.** Truth tables and constant functions; non-minimal automaton
presentations; the AJ10 UNKNOWN protocol.

**Forbidden extrapolations.** `NOVEL_MI_DISCOVERED`; `GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE`;
`M5`; any reading of "UNKNOWN" as "novel".

## FX-3 — repeat at the larger, non-enumerated universe B2 with two independent search implementations

**Statement.** In the 4-state universe B2 (`8^8 = 16,777,216` presentations, not enumerated),
search `S1` (random-restart single-entry hill-climb, seed 20260919, budget 300,000 evaluations
per regime) returns `RECOVERED` for `identity` after 23 evaluations, `delay1` after 53 and
`delay2` after 273, and `NOT_RECOVERED_AT_SCOPE` for `delay3` after the full 300,000
evaluations and 135 restarts (best mismatch 40 of 127 words). Search `S2` (residual
right-congruence construction) independently returns the same four terminals, with 1, 2, 4
and 8 residual classes — the `delay3` failure is structural (8 > 4 states). Every `S1` solver is
certified exact on **all** words by route B's product-state check, and the reachable-state
dependence per regime matches the frozen prediction (absent for `identity`, present for
`delay1`/`delay2`). The honest failure terminal is therefore exercised on a live regime, not
only in a hostile.

**Scope.** B2 under the registered budget and the two named implementations; the remainder
of B2 is not characterized.

**Quantifiers.** For all four B2 regimes; for all words (certification), for the 127-word
window (search objective).

**Assumptions.** The seed and budget frozen in `SEARCH_CONFIG_V1.json`; the shift-register
reference transducer for `delay-k`.

**Dependencies.** `BLIND_OUTCOME_V1.json#B2`, `ORACLE_RESULT_V1.json#B2_S2` and
`#S1_solvers_certified_by_route_B`.

**Falsifiers.** A `RECOVERED` terminal on one route and `NOT_RECOVERED_AT_SCOPE` on the other;
a found solver that fails all-words certification; a `delay3` solver with 4 states (impossible
by the residual count, which is the proof of the boundary). Hostile `H4` shows a starved budget
reports failure rather than a fake success; null `N3` shows 0 of 200 random B2 tables solve
`delay2`.

**Strongest parents.** Nerode right-congruence / minimal automaton construction; stochastic
local search; the AJ9h two-route requirement.

**Forbidden extrapolations.** `REAL_SCALE_VALIDATION`; `INDEPENDENT_TEAM_REPLICATION` (the two
implementations are independent code within one programme); any claim about presentations of
B2 that the searches did not visit.

## FX-4 — the falsifier is live, and the outcomes beat their nulls

**Statement.** All 8 registered hostiles are applicable (each moves the quantity it perturbs)
and detected: `H1` a planted family name raises source-audit violations from 0 to ≥ 1; `H2`
dropping the reachable-state clause raises `identity` fingerprint passes from 0 to 12; `H3` an
inverted prediction flips the verdict to `FALSIFIED`; `H4` budget 1 yields
`NOT_RECOVERED_AT_SCOPE`; `H5` a truncated window inflates solvers 1 → 65, 64 rejected; `H6` a
perturbed atlas row breaks the digest; `H7` a bare `REPLICATED` flag does not earn badge 5;
`H8` adjudication before a blind outcome exists is refused. Nulls: `N1` the state-dependence
test passes on 111/200 uniformly random B1 tables (strictly between 0 and 1, so 0/29 and 1/1
are regime properties, not a stuck test); `N2` exactly 1 of the 10 two-present assignments at
B1 and 1 of 8 at B2 match the observed vector (joint chance `1/80`), and the frozen prediction
is that one; `N3` 0/200 random B2 tables solve `delay2`.

**Scope.** This package's registered hostiles and nulls.

**Quantifiers.** For all 8 hostiles; 200 draws per randomized null; exact enumeration for `N2`.

**Assumptions.** `random.Random(20260919)`, `getrandbits`/`choice` (no low-bit reads of a
power-of-two LCG).

**Dependencies.** `BLIND_OUTCOME_V1.json#hostiles,#nulls`, `POSTHOC_RESULT_V1.json#hostiles`,
`LADDER_RESULT_V1.json#hostiles`.

**Falsifiers.** A hostile whose `applicable` flag is false (vacuous) or whose `detected` flag
is false; a null rate of 0 or 1 for `N1`; more than one matching assignment in `N2`.

**Strongest parents.** Pre-registration and planted-positive validation practice
(`gmi-833-aj9-holdout-source-audit-v1`, `gmi-833-body-residual-akl-v1`).

**Forbidden extrapolations.** Reading a detected hostile as evidence for the scientific
content of the rows; reading `1/80` as a significance claim beyond the registered enumeration.

## FX-5 — AJ13 and AJ14 applied to the run; independent oracle for the AJ11/AJ13/AJ14 receipts

**Statement.** The AJ13 stopping predicate evaluated on the flagship's base satisfies all
6 conjuncts (tagged assumptions; no named mechanism in the base; AJ1's six loss witnesses
consumed; presentation invariance from AJ5, AJ12 and the route-A/route-B agreement of this
run; parent ownership; descent boundary) with terminal
`FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE`. The AJ14 ladder recomputed from the
run earns badges 1–4 and does not earn badge 5 (no novel form survives parent review) or
badge 6 (issue #903 open); `full_gmi_supported_now: false`. Route B re-derives the same six
conjuncts and the same four badges from separate code, and both routes reproduce the
committed AJ11 receipt (260/148, histograms, front, digest) and the committed AJ13/AJ14
receipts (`criteria_satisfied: 6`, the four earned badges) — the independent oracle those
three packages lacked.

**Scope.** The flagship evidence and the three parent receipts as committed at `source_main`.

**Quantifiers.** All 6 conjuncts; all 6 badges; every pinned parent field.

**Assumptions.** The AJ13 conjunct vocabulary and the AJ14 ladder order as stated in the
issue rows; badge 5 additionally requires a claimed novel form and a replication receipt (a
bare flag is refused — stricter than the parent checker, and shown reachable by a positive
control).

**Dependencies.** `gmi-833-aj1-operational-process-base-v1#relative_irredundancy_removals`,
`gmi-833-aj11-bounded-completeness-v1`, `gmi-833-aj13-stopping-rule-v1`,
`gmi-833-aj14-establishment-criterion-v1`, `LADDER_RESULT_V1.json`, `LADDER_ORACLE_RESULT_V1.json`.

**Falsifiers.** A conjunct that fails on the flagship base; a badge earned by one route and
not the other; a pinned parent number that differs; badge 5 or 6 earned.

**Strongest parents.** The AJ13 and AJ14 packages own the rule and the ladder; this package
applies them and audits them.

**Forbidden extrapolations.** `FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE`; `AJ16_EARNED`;
`ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN`.

## FX-6 — custody: the registry is read only after the blind outcome, and the blind sources are audited

**Statement.** The blind stage records `registry_read: false` on both routes; the post-hoc
stage refuses to run without `BLIND_OUTCOME_V1.json` and pins that file's SHA-256 in its own
receipt. The blind artifacts (`aj15_flagship_v1.py`, `independent_oracle_v1.py`,
`SEARCH_CONFIG_V1.json`, `BLIND_OUTCOME_V1.json`) carry 0 hits of the registry vocabulary
derived from blob `6b9ac309…` (11 ids, 11 names, name tokens, 92 clauses, 25 anchors), while
the same scanner finds 27 + 2 + 4 hits in the post-hoc artifacts where the vocabulary is
permitted, and detects 8 of 8 planted positives, one per forbidden class. The universe B1 was
constructed at `83d79b44` (2026-09-16 11:07:50 +0200), before the registry was frozen at
`aec01b0e` (2026-09-16 11:59:03 +0200); both timestamps are re-read from git by the executor.

**Scope.** Lexical and structural custody of this package's artifacts; not a proof that no
information reached the search by an untraceable route.

**Quantifiers.** All four blind artifacts; all eight forbidden classes.

**Assumptions.** The AJ9a holdout contract's eight forbidden classes; the generic-token
exemption list validated by `gmi-833-aj9-holdout-source-audit-v1`.

**Dependencies.** `POSTHOC_RESULT_V1.json#source_audit`, `#blind_outcome_sha256`;
`gmi-833-aj9-holdout-source-audit-v1` (scanner design and the aj9g custody gap, which is not
load-bearing here).

**Falsifiers.** Any registry vocabulary in a blind artifact outside a declaration line; a
planted positive the scanner misses; a post-hoc receipt whose pinned blind digest differs
from the committed blind outcome; a git timestamp order that reverses.

**Strongest parents.** The aj9 holdout-source audit (route design, exemption rules).

**Forbidden extrapolations.** `ALL_HOLDOUTS_PROVEN_BLIND`; `NO_LEAKAGE_OF_ANY_KIND`;
`LITERAL_HISTORICAL_IGNORANCE_PROVED`; `FAMILY_INEVITABILITY`.
