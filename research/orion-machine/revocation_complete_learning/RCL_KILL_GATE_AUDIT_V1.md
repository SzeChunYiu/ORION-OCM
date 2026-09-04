# RCL pack — authoring-side audit against the #245 kill-gate

Date: 2026-09-04 · Review issue: #245 (unreturned) · Sibling: #199 (unreturned) · Umbrella #194 · Master #197

**This is not the #245 terminal.** The authoring session may answer defects but may not supply the
independent terminal (#245 "Completion evidence"). This audit records, row by row, what the
authoring side now believes survives each section of the gate after the V1 checker repair and the
lane #200/#203 collapses, so that a reviewer inherits a stated position rather than an implied one.
No terminal from #245's allowed set is issued here. **NO NOVELTY OR BREAKTHROUGH CLAIM.**

## A. Packet custody and executable replay (RCL-R01–R05)

| item | authoring-side state |
|---|---|
| R01 bytes/hashes | V0 packet carries two `rebound_at: 2026-09-04` entries with `superseded_binding` retained; `RCL_FAILURE_AND_PARENT_COLLAPSE_LEDGER_V0.md` stays `DRIFT_RECORDED_NOT_BLESSED` (never existed at 4,751 bytes). Not touched here. |
| R02 replay | `tests/unit/test_revocation_complete_learning.py` (16) + `tests/unit/test_rcl_checks_v1.py` (8) pass under Python 3.12.13; `rcl_checks_v1.py --self-test` exit 0. |
| R03 controls | **V0's three controls are `VACUOUS_CONTRAST` and remain so** (hash-bound; not repaired in place). `rcl_checks_v1.py` is the versioned successor: storage/query frontier withholds bits and charges queries (64 collision pairs below `S+Q >= N`, 28,863 reconstructions on/above); five mutations asserted applied then detected; no-alarm compares three distinct complete updaters (2,688/2,688) with a planted incomplete updater disagreeing on 485. The reviewer tests V0 as chartered; V1 is offered as the repair, not as a substitute for that test. |
| R04 finite enumeration as authority | `authority.all_size_theorem_proved_by_enumeration: false` in the V1 result; every all-size statement is a hand proof or a parent. |
| R05 toolchain/exit codes | recorded in `receipts/OCM_RCL_V1_AND_LANES_200_201_RECEIPT_V1.json`; `2 = CANNOT_CHECK` never reported as pass. |

## B. Theorem reconstruction (RCL-R10–R19) — authoring-side disposition per row

| row | claim | survives as | strongest parent | note |
|---|---|---|---|---|
| RCL-0 | canonical antichain ⇔ revocation signature | calibration | monotone Boolean function ⇔ unique minimal DNF; **ATMS label uniqueness** (de Kleer 1986) | the profile *is* an ATMS label (lane #203 §3) |
| RCL-1 | zero-query summary lower bound | calibration | distinguishability counting | |
| RCL-1b | `2^(C_n − 1)` future signatures under one current certificate | calibration | Sperner's theorem (middle layer) | elementary |
| RCL-1c | `S + Q >= C_n − 1` exact frontier | **hand proof retained; V0 finite construction withdrawn; V1 finite construction green** | decision-tree / INDEX counting | withdrawal scope stated in `OCM_FAILURE_LEDGER.md` |
| RCL-1d | direct sum over independent skills | calibration | additivity of `H_0` (lane #200 Thm A, WL-4) | |
| RCL-2 / 2a / 2b | positive-witness omission; bounded witnesses insufficient; single-proof over-retraction | calibration | closed-world vs open-world (Reiter 1978); ATMS label completeness | S3's positive-only store abstains on 485 cells — the same fact on the substrate |
| RCL-3 | one-warrant information bound | calibration | counting | |
| RCL-4 | full antichain sufficient | `PARENT_OWNED` | ATMS label completeness; TMS | |
| RCL-5 | false-retain / false-retract / abstain trilemma | calibration | KWIK-style abstention; two-world indistinguishability | |
| RCL-6 | semantic-learning / revision separation | **reduces to lane #200 Thm D**: separation ⇔ rectangularity, i.e. a product of two parent problems | Blackwell sufficiency; INDEX | the "separation" is additivity |
| RCL-7 | NP-complete LIVE + short extinction certificates ⇒ `NP = coNP` | conditional, standard | Cook 1971; Stockmeyer 1976 | `PARENT_OWNED` |
| RCL-8 / 9 | compilation escape; two-sided trilemma | parent-owned statement of the trade | knowledge compilation (Darwiche–Marquis 2002) | |
| RCL-E | RSD = fibre-wise VC dimension | demotion to notation | VC dimension | answers R33/R34 from the authoring side |
| RCL-D | blindness ⇔ rectangularity on WPL V1/V2/WGPL | collapse | Blackwell; product learners | 2,048 worlds; 3 planted coupled classes fail as required |

R19 attacks (empty warrant, empty profile, duplicates, non-antichain, restricted families,
randomized summaries, approximate decisions, adaptive queries, correlated skills): empty profile is
now given a semantics on the substrate (certified-empty = dead; endpoint-only = abstain); duplicates
and non-antichains are canonicalised by `rcl_model.canonical_profile`; the remaining attacks are the
reviewer's and are not pre-empted here.

## C. Strongest-parent reconstruction (R20–R29)

Not done from complete proofs by this session; `search_limitations` in
`RCL_NOVELTY_SEARCH_AND_RESIDUAL_V0.json` still holds. One **material addition** since the V1
packet: the ATMS identification (de Kleer, *An assumption-based TMS*, AIJ 28, 1986) — the RCL
formal object is an ATMS label, its liveness is label survival after assumption retraction, and
label combination is the composition rule S2. Consequence for R47: the strongest parent product
gains a member that owns the *object*, not only the maintenance. Post-material clean search count
remains **0**.

## D. Dimension collision (R30–R34)

RSD is the maximum over transcript fibres of the VC dimension of the liveness class restricted to
the admitted revocations (lane #200 Thm E; `verify_rsd_is_fibrewise_vc`, equal at n=4, value 5).
Authoring-side answer to R34: demote to notation; every dependent claim already reads it as such
(`RCL_THEOREM_LEDGER_V1.json` row RCL-E). R30–R32 (relations to Littlestone, eluder, star,
teaching, certificate, decision-tree, communication, query dimensions) are not worked here beyond
"it is a VC dimension on a fibre".

## E. Joint residual kill-gate (R40–R49)

`RCL-C` (`04_POSTFREEZE…` §6) requires a natural compositional family on which the joint learner
cannot be decomposed at equal resources. Lane #200 Thm D shows every registered class *is*
decomposable (rectangular). Authoring-side state: **`OPEN_NOT_PROVED__NO_REGISTERED_CLASS_QUALIFIES`**
— neither `JOINT_RCL_RESIDUAL_SURVIVES` nor `THEOREM_FAMILY_REFUTED`; the obstruction is the absence
of a non-rectangular class, and its construction would be a new object. R48 (compile into a
recurrent Transformer) is moot until a class exists; R43 (Pareto impossibility) has only cardinality
components.

Under the operator directive RCL is the authority-preservation constraint on self-revision (c),
and the constraint as stated is owned by the Gödel machine × ATMS product
(`OCM_DIRECTIVE_RESCOPE_V1.md` §3). The residual, if any, is a lower bound *against* that product
at equal information, which is the same missing object.

## F. Novelty search discipline (R50–R54)

No new search run. `clean_post_material_passes: 0` after the ATMS addition. No priority statement.

## What the authoring side asks of the reviewer

Test V0's three controls as chartered (they should fail R03); test V1's; reconstruct RCL-0 as ATMS
label uniqueness and decide whether the elementary pack is anything but ATMS arithmetic; and return
one of `THEOREM_DEFECTS_FOUND` · `PARENT_SUFFICIENT` · `NEW_THEORETICAL_RESIDUAL_CANDIDATE` ·
`CANNOT_CHECK`. The authoring side's own expectation, stated so that it cannot be read back as the
reviewer's: `PARENT_SUFFICIENT` for the pack as it stands.
