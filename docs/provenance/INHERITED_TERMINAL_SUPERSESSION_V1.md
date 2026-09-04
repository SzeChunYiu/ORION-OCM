# Inherited terminal supersession and migration-defect record (M1)

The migrated tree `research/orion-machine/**` is byte-frozen at ORION-V2 `42b1b0d` and is **not
edited**. Several frozen artifacts therefore carry terminals, counts or references that were
superseded on ORION-V2 before the freeze or that dangle in this repository. This note is the
single place that records the current reading. It supersedes nothing scientifically: every
inherited terminal keeps its authority; only stale *bookkeeping* is resolved here.

| # | frozen artifact | what it says | current reading | authority |
|---|---|---|---|---|
| C1 | `CONVERGENCE_MAP_V1.md:39,176`, `theory/KSO_ARCHITECTURE_V1.md` C5, `theory/KSO_M2_SOLVE_DESIGN_V1.md:113`, `results/KSO_M0_FREEZE_V1.json` `ledger_audit` | audit against a repository-root `FAILURE_LEDGER.md` | that file is the ORION-V2 root ledger; it is now materialised byte-identically at `docs/provenance/ORION_V2_FAILURE_LEDGER_42b1b0d.md` (blob `4394f4b6f066b83cb65aaa19d969f2debdde70c9`, 43,985 bytes) and bound in CI (`ledger-materialization` job) | unchanged |
| C2 | class counts 26+8 / 28+7 / 26 | three tallies | `OCM_FAILURE_LEDGER.md` has **8** retained classes (recounted); the root ledger's own class count is whatever the materialised file states — cite the file, not the tallies | unchanged |
| C3 | `theory/KSO_SUBSTRATE_CONTRACT_V1.md:793` vs `:1036` | `M1_KSO_INSTANCE = NOT_RUN` (Part I §22) vs `GREEN_DEV_SPLIT` (Part II §36) | Part II supersedes Part I §22 (Part I was frozen byte-identical to PR #290 and Part II appended by #295); the current inherited value is `GREEN_DEV_SPLIT (ME-X1, 50 worlds; protected NOT_RUN)` | unchanged |
| C4 | `CONVERGENCE_MAP_V1.md:127-131` "absent" table | M2 solve / M3 gap / M4 Jump / M5 codec absent | present as `reference/kso_m{2,3,4,5,6}_*` with receipts under `results/`; the map was frozen at #290/#295/#296 before #298/#301 landed | the receipts' own terminals (`M2_EXACT_ON_DEV` with mechanic `38/50`, `PARENT_SUFFICIENT`; M3–M6a calibration-only) |
| C5 | `README.md:16` vs `theory/OCM_DIRECTIVE_RESCOPE_V1.md:93` | RCL-C two terminals | the lane-200 revival (`OCM_NONRECTANGULAR_CLASS_V1.md:3`) is the latest: `NATURAL_NONRECTANGULAR_CLASSES_EXIST__ONE_NATURAL_NONDECOMPOSABLE_INSTANCE_REGISTERED__PARENT_OWNED`; RCL-C itself remains `NOT_EARNED`, parent-owned | unchanged |
| C6 | `README.md:11` vs `CONVERGENCE_MAP_V1.md:23` | #203 semantics freeze adopted vs `CANNOT_CHECK` | the freeze is **withheld** (`theory/OCM_OPERATIONAL_SEMANTICS_V1.md:5-8`, audit unreturned); the object is adopted, the freeze is `CANNOT_CHECK` | unchanged |
| C7 | `OCM_TASK_LEDGER_V1.json` D07 | falsifier register "11 rows" | `theory/OCM_FALSIFIER_REGISTER_V1.json` has **22** rows (recounted) | unchanged |
| C8 | `CONVERGENCE_MAP_V1.md:181-184` | `ABSORBED_AS_CONSTRAINT` 9 | recount over the 29 rows: CONSTRAINT **7**, CODE 2, BENCHMARK 1, PARENT 2, NOT_TRANSFERABLE 4, PENDING 12 | unchanged |
| C9 | `OCM_TASK_LEDGER_V1.json` D01 | spine README 1,076 bytes at `d4eb281` | historical binding; current `research/orion-machine/README.md` is 5,054 bytes (fourth rebind, unrecorded in the frozen ledger); the structural fix the failure ledger owes (freeze the review question, bind the spine elsewhere) is applied here: M1 binds **only** committed bytes through `docs/provenance/M1_RECEIPT_V1.json` | unchanged |
| C10 | `OCM_SNAPSHOT_V1.json` custody claim | "no file under `research/orion-machine/` exists on main" | true on ORION-V2 at snapshot time; void in this repository (129 files on `main`) | unchanged |
| C11 | four object models, three evidence-id schemes, two warrant implementations, three navigation implementations | duplicate definitions | resolved in `src/ocm/kso` (`space.py`, `ids.py`, `warrant.py`, `navigation.py`); parity with the frozen `kso_math_v1` asserted by `tests/m1/test_equivalence_reference.py`; the RWR comparator's *undirected* walk (`kso_m2_comparator_v1.py`) is recorded as a comparator mechanism gap for M2 | unchanged |
| C12 | `results/KSO_M2_SOLVE_RECEIPT_V1.json` `terminal` | `M2_EXACT_ON_DEV` | the mechanic's number is `headline.mechanic_terminal = M2_NAVIGATION_EXACT_38_OF_50__EXTRACT_ATTRIBUTED`; 38/50 is non-significant vs RWR (32/50) and CBR (34/50) at n = 50 and below the B5 ceiling; the comparator outcome is `PARENT_SUFFICIENT` | unchanged |

## Inherited terminals restated (authority anchors)

```text
M2_SOLVE_COMPARATOR        PARENT_SUFFICIENT          (KSO_M2_COMPARATOR_OUTCOME_V1.md)
M2_NAVIGATION_ONLY         38/50, NOT_SIGNIFICANT     (n = 50; vs RWR p = 0.31, CBR p = 0.52)
M5_CHAT                    CONTROLLED_CODEC_ONLY
M6A_FORMAL_MATH            VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT ; frontier_math_discovery = false
LANGUAGE_KSO_L0            CONTROLLED_GREEN ; open_domain_language = false
KSO_NOVELTY                NOT_ESTABLISHED
KS-P1 (retraction law)     PARENT_PRODUCT_OWNED
```

## Migration-closure amendment

`docs/DEPENDENCY_AUDIT_V1.json` scoped its policy to *runtime* dependencies; the ledger the
immune-system row audits against is a *document* dependency. M1 adds it as dependency row
`ROOT_FAILURE_LEDGER` with disposition `MATERIALIZED_BYTE_IDENTICAL` and a CI binding.
