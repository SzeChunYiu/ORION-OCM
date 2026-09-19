# Reported, not fixed (owned by successor lanes)

This tranche's scope is claim-discipline registration (#833 line 34). The following
rescore-v2 findings were flagged to this tranche and are REPORTED ONLY - fixing them
belongs to the named lanes. Nothing here was edited.

## 1. Census proof-mode disagreements

MATURITY_RESCORE_V2.md ("Reclassifications found by verification") states: "Census
proof-mode disagreed with actual support on 62 objects (table in THEOREM_SCORES_V2.json
`census_proof_mode` vs `support_kind`)."

Independent recount from the same two columns (this tranche):

- Raw string-level disagreement: 172 of 173 legacy objects (the census's
  ANALYTIC_DEDUCTIVE label maps onto five different observed support kinds:
  61 ANALYTIC_PROOF, 29 LEDGER_ENTRY, 10 EXACT_FINITE_CERTIFICATE, 10
  ANALYTIC_PROOF_PLUS_EXACT, 5 FROZEN_HELDOUT; plus COMPUTER_ASSISTED_EXHAUSTIVE ->
  EXACT_FINITE_CERTIFICATE 10, FINITE_EXECUTABLE_CERTIFICATE -> FROZEN_HELDOUT 4, and
  12 smaller pairs).
- Under a natural label-equivalence map (ANALYTIC_DEDUCTIVE==ANALYTIC_PROOF,
  COMPUTER_ASSISTED_EXHAUSTIVE==FINITE_EXECUTABLE_CERTIFICATE==EXACT_FINITE_CERTIFICATE,
  STATISTICAL_EXPERIMENT==SAMPLED_STATISTICAL, EMPIRICAL_EXPERIMENT==EMPIRICAL_UNFROZEN):
  99 disagreements remain.

The scorer's reconciled count of 62 is therefore produced by a finer per-object
reconciliation rule (24 rows were individually adjudicated in the v2 verification
protocol) that is not reconstructable from the two columns alone. Disposition: the
authoritative table is the scorer's own (THEOREM_SCORES_V2.json per-object
census_proof_mode vs support_kind); the count discrepancy 62 vs 99 vs 172 is flagged
to the rescore/depgraph successor lane for a stated reconciliation rule. No maturity
score depends on this tranche's reading.

## 2. M0-M6 terminology collision inside machine-intelligence-morphogenesis-v1

FREEZE_V2 gap G4: the tokens M0..M5 inside MIM matrix/ledger/ecology files
(README.md L202, DEFINITIONS_V2_EXACT.md L94, MORPHOLOGY_ATLAS_V1.md L133,
SIGNATURE_HOLE_CENSUS_V1.md L19) are morphology-signature row names, never maturity
levels. This tranche registered one such object (DISCRETE_FINITE, whose occupant
row's final field is the signature token M0) without touching the collision.
Disposition: owned by the terminology lane's successor tranche (post #947).

## 3. Two quantifier-overreach crosshands (consumed; adjudication lives in #949's lane)

TT-1 ("every Boolean task" on an n=3..8 receipt) and S0002-9947-1965-0188316-1
(universal Krohn-Rhodes assertion from a NOT_ACCESSIBLE primary, unverified DOI) were
crosshanded by the rescore lane to the Section-B adjudication lane (PR #949, merged:
overstrong adjudication of 283 GAP-FIN2UNIV flags, all PROPER). This tranche consumed
the crosshands by registering both objects' quantifier boundaries as
forbidden-extrapolation entries (CROSSHAND_APPEND in authored_overrides_v1.py,
visible in REGISTRATIONS_V1.json with crosshand markers).
