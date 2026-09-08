# Issue #165 evidence map v1

Machine-readable companion: [`CHECKBOX_MAP.json`](CHECKBOX_MAP.json).

**Record:** GitHub issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) against `main@b35093a` (`b35093a26e51ccf4829aa1218957827d95db8923`). Mapper branch: `research/issue-165-evidence-map`. This capsule does not edit the issue.

**Rule:** CHECK only with an artifact+terminal on that head. PARENT_SUFFICIENT and negative terminals may CHECK when the box asked for a disposition. Reconstruction and alias-only results do **not** CHECK causal reuse (G2.4, MATH-1 fresh-family reuse, L1 linguistic G2 receipts).

## Counts (662 boxes)

| status | n | meaning |
|---|---:|---|
| CHECK | 29 | earned on `main@b35093a` |
| PARTIAL | 180 | evidence exists; required coordinate missing |
| OPEN | 211 | not done |
| BLOCKED | 198 | locked behind an earlier gate |
| IN_PR | 33 | evidence on an open PR (150/154/158/161/163/132) |
| CANNOT_CHECK | 11 | environment or process-rule, not a historical result |

## Immediately checkable (orchestrator: tick NOW)

| id | checkbox | terminal + citation |
|---|---|---|
| ARCH/007 | neural outputs remain proposals | `NO_NEURAL_CONTRACT` — `research/programme/NO_NEURAL_CONTRACT.md` |
| G1.2/007 | preserve PARENT_SUFFICIENT | `M8_PARENT_SUFFICIENT_AT_THIS_SCALE` — `docs/provenance/M8_RECEIPT_V1.json`; also CLIA `PARENT_SUFFICIENT_FUNCTION_ONLY`, G1-matched `G1_NOT_ADMITTED` |
| G1.2/008 | do not call the machine “minimal” from deletion | `CURRENT_RUNTIME_BOOTSTRAP_NOT_MINIMAL__N1_MINIMAL_TARGET_REGISTERED` + `G1_NOT_ADMITTED` |
| G2.3/002 | retain unnormalized predecessor | Stitch receipts keep `primitive_alias_assessment=NOT_RUN` |
| G2.3/003 | preserve PRIMITIVE_ALIAS | `TYPED_INTERFACE_QUALIFIED_ALIAS_ONLY` + Stitch source-level alias |
| G2.3/004 | preserve NO_NEW_ABSTRACTION | typed eligible methods empty + Stitch `NO_NEW_ABSTRACTION` |
| G2.3/005 | forbid repeated corpus/settings search | Stitch public induction did not retune examples/settings/calls |
| G2.3/006 | independently verify normalized semantics | `WITNESS_QUALIFICATION_PASS` — `stitch-alias-witness-20260906` |
| G4.1/001 | do not train an ML router for compose reordering | `LEARNED_ROUTER_NOT_YET_AUTHORIZED` (#71); no ML compose-router on this head |
| G5.1/002 | evaluate SQLite/WAL | `SQLITE_WAL_PARENT_IMPLEMENTED` — `src/ocm/store/sqlite_ledger.py` + `tests/m2/test_sqlite_ledger_parent.py` (JSONL remains default) |
| L0/001–012,014–015 | bootstrap enumerations + classify/count priors | `CURRENT_RUNTIME_BOOTSTRAP_NOT_MINIMAL__N1_MINIMAL_TARGET_REGISTERED` — `research/ocm-n1/LANGUAGE_BOOTSTRAP_MANIFEST_V1.json` |
| L1/011 | CANNOT_CHECK where mapping is incomplete | UD `TEACHER_ANNOTATED` — `research/ocm-n1/N1_UD_INDUCTION_V1.json` |
| MATH-1/004 | known reconstruction | 4,223 prefix verified + typed seven-claim reconstruction (not causal reuse) |
| MATH-1/009, P1/006, C22.machine/004 | restart / persistent restart reuse | authored lifecycle + typed consumer revival (alias reconstruction in the typed arm) |

## Next blockers (do not tick; these gate later CHECKs)

| blocker | why it is next | status on `main@b35093a` |
|---|---|---|
| **P1 syntax-interface revival** | Ordinary-cut audit recorded 76/76 proposal screens `UNKNOWN` before matching; opportunity question unresolved | `TRAINING_ONLY_OPPORTUNITY_RECORDED` — `research/ordinary-cut-opportunity-result-v1/SUMMARY.json` |
| **G2 causal reuse (non-alias)** | Authored chunking is `CAUSAL_CHUNK_CONSUMPTION_IN_FIXED_AUTHORED_CONTROL`; typed arm is alias-only; later-consumption is `CANNOT_CHECK_CONSUMPTION`. G2.4 stays PARTIAL | do not CHECK G2.4 from reconstruction/alias |
| **G2.1 schemas** | `CognitiveEpisodeV1` / `MethodRecordV1` / … are absent | OPEN (12) |
| **G1.1 vessel freeze** | No `(F,O,Π,C)` implementation manifest | OPEN (7); CINV/ARCH remain PARTIAL until that freeze |
| **P0 exact-parent close** | `EXACT_POLICY_SUFFICIENT` is on unmerged #152 source, not this head | IN_PR **#154** / **#158**; paid-DRD correction capsule on main, integration pending |
| **L0 ablations** | Minimal target registered; reduced-bootstrap ablation not run; current-runtime SOV hostile still a required ablation | L0/016 OPEN; L0/017 PARTIAL |
| **MATH-1 / N4 close** | Reconstruction ≠ `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`; lemma parent is design-only | MATH-2/3 BLOCKED |
| **G3 / P3 / prototype / P6–P8 / L2–L3** | Locked on G2 / N1 / N4 | BLOCKED |
| **M11/M12 science** | Historical terminals reopened after predecessor-binding repair | `M11_ENGINEERING_REVALIDATION__HISTORICAL_ADOPTION_CELLS_REOPENED` |

Open PRs consulted, not main CHECKs: **#150** (evolvability E0/E2), **#154** (horizon / ski-rental / DP), **#158** (paid DRD parents), **#161** / **#163** (`ARCHITECTURE_NET_BENEFIT_NOT_ESTABLISHED`), **#132** (FLT prerequisites; #46 LOCKED).

## What this map refuses to close

- G2.4 fresh-task causal use (authored near-transfer is PARTIAL, not G2 closure).
- MATH-1 fresh theorem-family reuse, unseen composition, lemma reuse.
- G4.1 “preserve current negative terminal” until `EXACT_POLICY_SUFFICIENT` is a `main@b35093a` receipt.
- G5.1 stop whole-file ledger rewrite (evaluated SQLite parent; production JSONL still rewrites).
- Any §22 Final issue terminal (#38–#152 still OPEN).
