# Hand check — 20 objects read against their pointers

Protocol (FREEZE_V1.md §8): twelve populated objects covering every binding
path, eight that must remain `UNKNOWN` / `UNREGISTERED`. Each source line was
read with `git show 2fffb144:<path> | sed -n <line>p` (the frozen source), each
pointer opened in the named parent artifact, and the register record compared.
Register keys are `source_path:Lnn` in `REGISTER_DELTA_V1.json`.

## Populated (12)

| # | register key | id | path | what the pointer says | what the register says | verdict |
|---|---|---|---|---|---|---|
| P1 | `research/gmi-adaptive-row-confidence-v1/raw/OCM_FOUNDATIONS_CLOSURE_V1.md:L7` | `V0.2` | B1 | v2 row `GMI833_V2_LEGACY_001_V0.2`: `maturity_M` UNKNOWN, `evidence_EV` UNKNOWN; cites this file | `maturity_level` UNKNOWN, `evidence_level` UNKNOWN, both with a pointer; 4 ledgers populated from the registration | faithful. Note: the source line is prose ("The existing V0.2 evolvability theory supplies useful research coordinates…"), so the scoring lane's identity here is a version label, not a theorem; copied as scored |
| P2 | `research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L32` | `P4.BAXTER` | B1 | v2 row `…_130_P4.BAXTER`: M0 / EV0; the line is a collision-matrix row `\| P4.BAXTER \| PARTIAL_TEXT_READ \| …` | M0 / EV0; `assumptions[0]` is the registration's EXTRACTED entry (`COLLISION_MATRIX_V1.md:L3: Rows: parents reconstructed at primary-source depth…`) | faithful. The registered ledger entry is a table caption — thin, and copied as registered; this package does not grade ledger quality |
| P3 | `research/machine-intelligence-morphogenesis-v1/gmi_microscope/tmt.py:L227` | `X-TMT9` | B1 | v2 row `…_173_X-TMT9`: M2 / EV2; `citation_paths` = this `.py` file; the line is `return {"check": "X-TMT9", "theorem": "TMT-9 residual Jacobian identity", …}` | M2 / EV2 | faithful; the census registers code lines as objects and the scoring lane cited exactly this file |
| P4 | `research/gmi-analog-semantics-closure-v1/ANALOG_SEMANTICS_CLOSURE_LEDGER_V1.json:L6` | `ANALOG_SEMANTICS_THEOREM_V1` | B2 | v2 row `…_002_ANALOG_SEMANTICS_THEOREM` (suffix truncated at 24 chars), `theorem_name` = `ANALOG_SEMANTICS_THEOREM_V1`: M0 / EV0; cites this ledger JSON | M0 / EV0; `binding.rule` = `B2_THEOREM_NAME_ID_EXACT` | faithful; B2 exists precisely for the 24-char truncation of legacy suffixes |
| P5 | `research/gmi-delegation-cost-repair-v1/CORE.md:L7` | `TYPED_DELEGATION_COST_THEOREM_V1` | B2 | v2 row `…_008_TYPED_DELEGATION_COST_TH`, `theorem_name` = the full id: M1 / EV1; the line is `- [Positive theorem and exact scope](TYPED_DELEGATION_COST_THEOREM_V1.md):` | M1 / EV1; `assumptions[0]` = `TYPED_DELEGATION_COST_THEOREM_V1.md:L45: Assume the stated CPython3.12 opcode layout…`; `strongest_parents[0]` = the Carbonneaux–Hoffmann–Shao PLDI 2015 entry | faithful |
| P6 | `research/gmi-novel-intelligence-w4-v1/FORMALIZATION_V1.md:L56` | `W4-C` | B1 + v3 delta | v2 row `…_074_W4-C`: M4 / EV3; `SCORES_V3_DELTA.json` record for the same `result_id`: M2 / EV2, `DOWN_GENERATING`; the line is `### Theorem W4-C — W4 at registered finite family scope` | M2 / EV2; `provenance.maturity_level` = [v2 pointer, v3 pointer]; `binding.v3_delta.superseded_v2` = (M4, EV3) | faithful; the correction propagates and the superseded value is kept visible |
| P7 | `research/gmi-adaptive-creation-v1/ADAPTIVE_CREATION_AND_HORIZONS_V1.md:L26` | `AUTO-8E64…` | edge, UNIQUE_ID | `DEPENDENCY_GRAPH_V2.json#edges.file_local[0]`: child `AUTO-8E6409D96BA0AB31944A` → parent `ARC-1`, relation `INHERITS`, citation `…:L29` ("This is inherited from ARC-1, not a new statistical rate.") | `claim_dependencies` = [`ARC-1`]; one pointer | faithful. The provisional id is unique in the census and belongs to the L26 object; the miner's citation names L29 (the relation token) in the same file, which is the miner's declared semantics |
| P8 | `research/gmi-capability-predictor-v1/DESCRIPTOR_V1.md:L45` | `AUTO-5BB2…` | edge, UNIQUE_ID | `edges.file_local[5]`: parent `CSR-1`; the line is `**Strongest parent:** POMDP control/update; …` | `claim_dependencies` = [`CSR-1`]; `strongest_parents` has 1 entry from the edge | faithful |
| P9 | `research/gmi-causal-identifiability-v1/raw/pr570-1277d0e8/CAUSAL_IDENTIFIABILITY_BOUNDARY_THEOREM_V1.md:L3` | `AUTO-1D36…` | edges 8–10, by-name parents | three `file_local` records with `parent_kind` `CORPUS_CLAIM_BY_NAME` (a file name with a stray backtick, `master §1.7`, a directory path) plus one `CORPUS_CLAIM` parent `MINIMAL_AXIOM_FREEZE_V1` | `claim_dependencies` = [`MINIMAL_AXIOM_FREEZE_V1`]; the three names are in `dependency_parents_by_name`, not in `claim_dependencies` | faithful; the by-name strings are low-quality parents lifted verbatim by #949 and are kept out of the id-typed field |
| P10 | `research/gmi-adaptive-row-creation-v1/CORE.md:L7` | `ADAPTIVE_ROW_CREATION_THEOREM_V1` | edges incl. `STRONGEST_PARENT_DECLARED` | `edges.file_local[2]` and `[3]`: relation `STRONGEST_PARENT_DECLARED`, citation `CORE.md:L11` ("Parents: [ARC-1–4]…"); rollup edges add `ARC-6` | `claim_dependencies` = [`ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1`, `ARC-1`, `ARC-6`]; `strongest_parents` = [`ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1 (CORPUS_CLAIM)`, `ARC-1 (CORPUS_CLAIM)`] with the two edge pointers | faithful |
| P11 | `research/gmi-capability-interactions-unified-v1/CORE.md:L13` | `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1` | B2 + rollup edge | v2 row `…_007_CAPABILITY_INTERACTIONS_` (truncated), `theorem_name` = full id: M2 / EV2; `edges.pointer_rollup[1]` gives parent `PVR-3` | M2 / EV2; `claim_dependencies` = [`PVR-3`]; 4 ledgers populated | faithful; the only object reached by both a scored row and an edge in this sample |
| P12 | `research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L32` (same object as P2, checked for the AA24/AA25 pool) | `P4.BAXTER` | evidence mode `STATISTICAL_EXPERIMENT` | registered `assumptions` ledger present | counted in AA24/AA25's 15 evaluable objects | consistent with `DECIDABILITY_V1.json` |

## Must stay unpopulated (8)

| # | register key | id | why it must stay | what the register does |
|---|---|---|---|---|
| N1 | `research/gmi-adaptive-row-confidence-v1/raw/OCM_FOUNDATIONS_CLOSURE_V1.md:L208` | `FC-T2` | in a file a scored row cites, but no scored row has this id | absent from the delta: `UNKNOWN` / `UNREGISTERED` |
| N2 | `research/machine-intelligence-morphogenesis-v1/GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md:L569` | `B2.3` | in a cited file; the id is declared 10 times; no scored row named `B2.3` | absent |
| N3 | `research/gmi-capability-ceilings-f2-tranche3/FORMALIZATION_V1.md:L47` | `F2-S` | one character from the scored `F2-U` / `F1-S`; a similarity binder would take it | absent (H3 shows the binder refuses `_V2` and prefix plants) |
| N4 | `research/gmi-adaptive-creation-v1/CORE.md:L5` | `ARC-6` | the id is declared 10 times across packages; it is a *parent* in propagated edges, never a bound child | absent; `ARC-6` appears only inside other objects' `claim_dependencies` and as a gap `claim_id` with descendants |
| N5 | `research/machine-intelligence-morphogenesis-v1/LITERATURE_LEDGER_V2.md:L671` | `FAC-CTW` | 6 declarations, 3 at the cited path, none at the cited line: the edge is refused `AMBIGUOUS_CHILD_IDENTITY` | absent for all 6 declarations (checked) |
| N6 | `research/gmi-architecture-emergence-v1/raw/pr575576-ef5be973/ARCHITECTURE_EMERGENCE_THEOREM_V1.md:L51` | `CAU-1` | 17 declarations; the five rollup edges are refused | absent for all 17 declarations (checked) |
| N7 | `research/gmi-capability-ceilings-v1/F2_CEILINGS_V1.json:L109` | `AUTO-30CB…` | provisional id in a scored package; nothing binds a provisional id except a resolved edge, and none names it | absent |
| N8 | `research/gmi-novel-intelligence-w4-v1/CORE.md:L14` | `RESULT_V1` | a receipt-class line in the W4 package; only `W4-C` (P6) is the scored object there | absent |

## Observations carried to the report

- Every populated value opened to exactly the pointed content (12/12), and
  every must-stay object is absent from the delta (8/8), including all 23
  declarations behind the two refused ambiguous ids.
- The identities are faithful but not all are *good*: P1 binds a prose line,
  P2's registered ledger entry is a table caption, P9's by-name parents are
  verbatim junk from the miner. The register copies what `main` carries and
  says where; grading those inputs is the parents' business and the next
  lane's.
