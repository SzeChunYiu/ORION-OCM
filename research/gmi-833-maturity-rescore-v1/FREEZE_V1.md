# GMI #833 A-section maturity rescore — freeze v1

**Parent:** #833 Section A
**Child issue:** #833 (Section A rows "Re-score every major existing GMI result on the maturity ladder" and "Require every result to state scope, quantifiers, assumptions, falsifiers, strongest parents, and forbidden extrapolations")
**Frozen source authority:** `9f90fc4ef961b7e9adccf7438488d1a64b9e68be` (origin/main tip at freeze time)
**Status:** pre-implementation theorem/claim freeze. This file is committed BEFORE the scorer, score records, audit table, or receipt are written, so scores cannot be tuned to inflate any package; the inclusion rule and rubric are frozen first.

## 1. Scientific question

Can every major existing GMI #833 result be placed honestly on the M0–M6 maturity ladder and EV0–EV5 evidence ladder codified in `gmi-833-foundation-v1/FOUNDATION_THEOREMS_V1.md` §2, with each placement justified solely from the package's own registered theorem statements, claim ceilings, and machine receipts — and with every result additionally required to state its scope/quantifier class, assumptions, falsifiers, strongest parents, and forbidden extrapolations?

This is an **audit/registration object**, not a proof that any rescored theorem is true. Re-scoring re-labels evidence; it does not create evidence.

## 2. Ladders (frozen, imported from the foundation; altered definitions are forbidden)

Evidence level (foundation EV0–EV5):

- **EV0** definition/protocol/registration — cannot by itself license theorem truth or empirical effect;
- **EV1** deductive theorem with explicit premises and falsifiers — cannot license reachability, selection, empirical validity;
- **EV2** exact/computer-assisted certificate at a bounded declared universe — cannot license universal extrapolation, held-out prediction;
- **EV3** prospectively frozen held-out experiment — cannot license independent replication, external validity;
- **EV4** disjoint and/or independent implementation replication — cannot license universal real-scale law;
- **EV5** real-scale prospective validation with calibrated uncertainty — cannot license ontological completeness or unrestricted universality.

Maturity ladder (foundation M0–M6):

`M0 concept -> M1 theorem -> M2 exact witness -> M3 architecture-prior-free relative recovery -> M4 frozen held-out prediction -> M5 independent replication -> M6 real-scale prospective validation`.

### Scoring rubric (frozen)

1. **M-level requires the evidence named in the foundation doc.** M0 requires only a registered concept. M1 requires an EV1-or-above deductive theorem with explicit premises and falsifiers. M2 requires an EV2-or-above exact/computer-assisted certificate at a bounded declared universe. M3 requires P3/P4 architecture-prior-free **relative recovery** with the target-family naming/property/operator absent from search-visible inputs and family mapping post hoc (foundation §6). M4 requires a prospectively frozen held-out experiment (EV3). M5 requires disjoint/independent implementation replication (EV4). M6 requires real-scale prospective validation (EV5).
2. **M-level ceiling is bounded by the package's EV.** `maturity_M > evidence_EV` is an automatic `MATURITY_EVIDENCE_MISMATCH` and fails the record. Concretely: an EV2 package can reach at most M2; an EV3/M4-style held-out package can reach M4 but no further; only EV5 evidence can ground M6.
3. **M3 is never awarded to a package whose search saw the target family/name/property vector** (prior disclosure `P<=P2`), even if the package uses the word "derivation." Only `gmi-833-g0-binary-recovery-v1` claims `P3_RELATIVE` in its own ceiling, and the entire §-J package family (`finite-search-budget`, `search-law-morphology-change`, `global-vs-reachable`, `morphology-selection*`, `history-switching`, `heldout-20-transitions`) is derivational but prior-supplied — none can be M3.
4. **Never inflate and never guess.** Most finite-enumeration results are M2 (exact witness/census) at best. If a result's maturity cannot be determined from its registered receipts, score it `"UNKNOWN"` and say so in the justification.
5. **`maturity_M` may be below `evidence_EV`** (a package may hold EXACT/CENSUS evidence yet only claim a theorem); only the upward mismatch is a defect.

## 3. Inclusion rule for "major result"

For the purpose of this rescore, a **major result** is:

> the one primary theorem/claim object of a `research/gmi-833-*` package that (i) owns the package's registered `claim_ceiling` (or, failing that, its `terminal`/`verdict`), (ii) is stated in that package's `*_THEOREMS_V1.md`-style registered theorem document, and (iii) is grounded by the package's machine receipt (`RESULT_V1.json` or equivalent `ORACLE_RESULT_V1.json`/`ROBUSTNESS_RESULT_V1.json`).

Additional mechanical rules (frozen):

- **One primary theorem per package.** A package may register many theorems; the inclusion is the theorem that anchors the claim ceiling. Every other theorem is cited in `statement_excerpt` context and parents as needed, but only the primary is scored. This keeps the table one row per package.
- **Package must exist at the frozen source SHA, in the `research/` tree, with the `gmi-833-` prefix.** A package missing or renamed after freeze is `FAIL_CLOSED` (the scorer errors; it does not silently skip).
- **Excluded packages**: any `gmi-833-*` directory that has no registered claim ceiling and no registered theorem document is LISTED as excluded with a typed reason (see §7), never silently omitted.
- The identical-name sibling directories that are NIETHER package nor claim (e.g. `.github/workflows` entries, and the `gmi-833-corpus-census-v1/AUDIT_V1.json` corpus audit object) are data, not primary theorems.

## 4. Record schema (each row, `THEOREM_SCORES_V1.json`)

One record per included package:

- `result_id` — stable slug, e.g. `GMI833_RESULT_12_FSB` (package index rank is by lexicographic package name);
- `package` — exact directory name (`gmi-833-...`);
- `theorem_name` — registered theorem anchor in the package's theorem doc;
- `statement_excerpt` — verbatim/close excerpt that states the load-bearing claim (with `[…]` elisions);
- `scope_quantifier_class` — one of the foundation domain tags or a faithful paraphrase: `forall[D]`, `forall_fin[U]`, `heldout[F]`, `sample[P,n]`, or `CONDITIONAL_AT_REGISTERED_SCOPE` with the scope named;
- `assumptions` — nonempty list of load-bearing premises (from the theorem doc);
- `falsifiers` — nonempty list of registered falsifying events (from the theorem doc's falsifier section);
- `strongest_parents` — nonempty list of parent owners named in the package (literature DOI/anchors AND repository pin refs);
- `maturity_M` — `M0..M6` or `"UNKNOWN"`;
- `evidence_EV` — `EV0..EV5` (union over the package's registered machine receipts);
- `justification` — why the M/EV pairing, citing file paths;
- `citation_paths` — nonempty list of relative file paths under `research/<package>/` that support the score;
- `forbidden_extrapolations` — nonempty list (verbatim/abridged from the package's own forbidden-promotion block; this is the "forbidden extrapolations" requirement of issue §A).

Missing/empty required list field ⇒ the record fails (hostile control). Unknown fields stay the literal string `"UNKNOWN"`.

## 5. Claim ceiling

Earned at the registered scope only if the scorer, tests, `-O` byte-compare and CI are all green:

`GMI_MATURITY_RESCORE_AT_FROZEN_MAIN_SCOPE`

Forbidden promotions (this package alone may not assert): `M3_THROUGH_UNSUPPLIED_PRIORS`, `ONTO_COMPLETENESS_IMPLIED_BY_MATURITY`, `MATURITY_PROMOTED_BY_EXISTENCE_OF_SCORE_RECORD`, `CORPUS_WIDE_MATURITY_CLOSURE`, `RESCORED_THEOREMS_REPROVEN`, `COMPLETE_GMI`.

The score record is a *label* on registered evidence; creating the record does not change any underlying theorem's truth or its registered freeze.

## 6. Hostile controls (must fail closed)

The scorer `rescore_v1.py` must hard-fail (non-zero exit, typed error) rather than silently continue on:

1. **unknown package** — scoring a package not in the frozen inclusion list;
2. **an M-level above the ceiling implied by the EV** — `MATURITY_EVIDENCE_MISMATCH`;
3. **missing required field** — any record missing `scope_quantifier_class`/`assumptions`/`falsifiers`/`strongest_parents`/`forbidden_extrapolations`;
4. **missing/renamed package dir** — `FAIL_CLOSED`, never a silent skip;
5. **post-freeze drift** — the frozen inclusion list stem SHA or package list differing from what the freeze documents.

## 7. Frozen inclusion list (package → primary theorem anchor)

Included packages (32 packages, one row each; lexicographic order):

| # | package | primary theorem anchor | scope/quantifier | EV evidence (registered receipts) |
|---|---|---|---|---|
| 1 | `gmi-833-axiom-core-v1` | AX-1…AX-6 conjunctive finite satisfiability (`AXIOM_CORE_THEORY_V1.md` §6) | `forall_fin[registered 128-mutation universe]` | EV2 (executable finite witness + 2^7 hostile hypercube) |
| 2 | `gmi-833-developmental-naturality-v1` | trajectory preservation (TRANS-2A composition; §4) | `forall_fin[registered deterministic finite dev systems]` | EV2 (126-trajectory receipt) |
| 3 | `gmi-833-finite-search-budget-morphology-v1` | FSB-4 exact global-recovery threshold (§6) | `forall_fin[registered finite schedules]` | EV2 (1,448,631 budget-point census) |
| 4 | `gmi-833-foundation-v1` | BS-1 legacy-obligation map (§3) | `CONDITIONAL_AT_REGISTERED_SCOPE` (same instances/traces/predicate) | EV1/EV2 (analytic proofs + finite hostiles; census evidence) |
| 5 | `gmi-833-g0-binary-recovery-v1` | RECOVER-1A unique P3-relative DELAY1 recovery (§4) | `forall[registered 260-candidate classes]` (all-length induction) | EV2 (510-sequence + 260-candidate exhaustive; robust UD controls) |
| 6 | `gmi-833-g0-cost-privilege-v1` | LABEL-1 family-label blindness (§2) + BIAS-1 (§5 boundary) | `forall_fin[registered 6-presentation/180-point universe]` | EV2 (180-point + 720-bijection certificates, oracle) |
| 7 | `gmi-833-g0-governed-self-change-v1` | ADOPT-1 verifier-gated single-use adoption (§3) | `forall_fin[registered 27-candidate universe]` | EV2 (27/9/18 census + hostile matrix, oracle) |
| 8 | `gmi-833-g0-grammar-bias-v1` | BIAS-1 finite description bias (§1) | `forall_fin[registered 126-presentation slice]` | EV2 (126-presentation exact enumeration, oracle) |
| 9 | `gmi-833-g0-interaction-channels-v1` | COMM-2 FIFO explicit application (§2) | `forall_fin[registered channel/message universe]` | EV2 (24/24 + 72 checks, oracle) |
| 10 | `gmi-833-g0-local-graph-ops-v1` | EQ-1 vertex-relabeling equivariance (§6) | `forall_fin[registered 3-site/3^3-state universe]` | EV2 (3,888 checks, oracle) |
| 11 | `gmi-833-g0-register-core-v1` | COMP-1 exact Mealy compiler (§5) | `forall[finite deterministic total Mealy M]` (induction) | EV2 (3,840 comparisons + second interpreter) |
| 12 | `gmi-833-g0-stochastic-update-v1` | STOCH-2 composition/sequential equality (§2) | `forall_fin[registered 216-kernel family]` | EV2 (139,968 comparisons, oracle) |
| 13 | `gmi-833-global-uncertainty-v1` | U-2B dependence-safe confidence composition (§4) | `forall_fin[registered probability spaces/budgets]` | EV2 (4,096-case Boole census + 1,024-composition) |
| 14 | `gmi-833-global-vs-reachable-morphology-v1` | GVR-2 exact optimum-recovery condition (§4) | `forall_fin[registered finite worlds]` | EV2 (1,434 + 5,826 + 500 + 130 cases) |
| 15 | `gmi-833-heldout-20-transitions-v1` | frozen threshold law `lambda*=eta·p/2` + 20/20 held-out transitions (§3-§4) | `heldout[F]` (20 frozen cases, freeze ddb3df7) | EV3 (prospectively frozen outcomes; 40/40 endpoints; independent-search replication of procedure) |
| 16 | `gmi-833-history-switching-hysteresis-v1` | HIST-2 symmetric two-form hysteresis band (§3) | `forall_fin[registered kappa/delta grid]` | EV2 (21 exact contexts) |
| 17 | `gmi-833-morphcap-v1` | CAP-1 morphology invariance (§4) | `CONDITIONAL_AT_REGISTERED_SCOPE` (deterministic finite microscope) | EV2 (finite witness, fingerprint canonicalization) |
| 18 | `gmi-833-morphology-selection-schema-v1` | PHASE-1A argmin constancy between crossings (§5) | `forall_fin[registered 84-triple affine family]` | EV2 (507 exact cell checks + 2,044 SEL comparisons) |
| 19 | `gmi-833-morphology-selection-v1` | NICHE-1a sufficient coexistence (§2) | `forall_fin[registered 243-world census]` | EV2 (243 worlds + 1,024 repricing tuples) |
| 20 | `gmi-833-no-smuggling-audit-v1` | cross-audit CLEAN conjunctive theorem (§A-cross) | `CONDITIONAL_AT_REGISTERED_SCOPE` (registered audit record) | EV2 (exact hostile certificate on finite fixtures) |
| 21 | `gmi-833-parent-equivalence-v1` | MN-1 Myhill–Nerode exact specialization (§2) | `CONDITIONAL_AT_REGISTERED_SCOPE` (deterministic total finite language recognizer) | EV2 (5,832-machine exhaustive certificate) |
| 22 | `gmi-833-pareto-topology-v1` | TOPO-1A forward budget-ball topology basis (§5) | `forall_fin[registered finite morphology graphs]` | EV2 (20-frontier algebra + 32,000 triple laws) |
| 23 | `gmi-833-real-transition-protocol-v1` | fail-closed real-system transition protocol (CORE.md) | `CONDITIONAL_AT_REGISTERED_SCOPE` (protocol; NOT scientific evidence) | EV1 (protocol formalized; zero qualifying real receipts, `scientific_row_earned=false`) |
| 24 | `gmi-833-remint-equivariance-v1` | canonical fingerprint invariance (§3) | `forall_fin[registered finite presentations]` | EV2 (6-remint + 9-quotient-pair certificates) |
| 25 | `gmi-833-robustness-controls-v1` | R1 background-opportunity preservation (§2) | `forall_fin[registered control masks]` | EV2 (16-mask completeness certificate) |
| 26 | `gmi-833-search-law-morphology-change-v1` | SLM-4 unique-optimum law-erasure (§6) | `forall_fin[registered two-law schedules]` | EV2 (237,282 budget points) |
| 27 | `gmi-833-stochastic-predictive-v1` | LR-2 rank-attaining core-test factorization (§4) | `forall_fin[registered finite predictive block]` | EV2 (81-block census, two rank paths, 256 assignment hostile) |
| 28 | `gmi-833-transform-geometry-v1` | DIST-1A directed shortest-transform burden (§3) | `forall_fin[registered transform graphs]` | EV2 (25 pairs/125 triangles exact rational Dijkstra) |
| 29 | `gmi-833-update-law-nfl-v1` | NFL-I1 exact equality under uniform completions (§3) | `forall[D]` (any normalized law on finite completion space) | EV2 (136-case census + exact rational control) |

Excluded packages, with typed reasons (each is listed, none silently dropped):

| package | typed exclusion reason |
|---|---|
| `gmi-833-corpus-census-v1` | NO PRIMARY THEOREM — a corpus/provenance audit object (EV0-grade registration), not a result with a claim ceiling; its own audit discloses 22,553 objects of which only 237 are structurally GREEN and its maturity/evidence fields are wholesale UNKNOWN (per its frozen AUDIT_V1.json). |
| `gmi-833-tranche-ab-ac-lit` | NO PRIMARY THEOREM — terminology authority / crosswalk package (`REGISTERED_TERMINOLOGY_AUTHORITY_V1`), registered receipts are terminological counts, not scientific theorems. |
| `.github/workflows/gmi-833-*.yml` | NOT A RESEARCH PACKAGE — CI workflow definitions. |

## 8. Falsifiers

The rescore claim is RED if: any package on the frozen inclusion list is omitted from the generated score records; any score's M/EV pairing is unjustified by the cited receipts; any record is missing a required field; the scorer silently skips a renamed/missing package directory; normal and optimized execution produce different canonical output; or any forbidden promotion is emitted.

## 9. Verification contract

- The scorer is stdlib-only and deterministic (frozen list embedded; sorted iteration).
- `python -I -B rescore_v1.py` and `python -I -O -B rescore_v1.py` must produce byte-identical `THEOREM_SCORES_V1.json` and `RESULT_V1.json` (redirect to files and `cmp`).
- Package-scoped pytest runs on laptop billy (`billy-laptop:~/rescore-verify/`) — never on a Mac runner or this worktree's parent checkout.
