# Evidence map and scope
This is the complete read-only publication of the bounded native interface
diagnostic and its single-stage repairs, under #62/#50, #71/#73 and #38.
Core/defaults/current adapters and all earlier packets are unchanged.

## Actual sequence
| Phase | Assigned | Observed result |
|---|---:|---|
| v1 frozen raw capture | 4 | All native workers exit0 but return setup CANNOT_CHECK. |
| v1 original checker caller | 4 | Four CANNOT_CHECK; no Z3 on no-candidate fast path. |
| Quoted setup control | old/new | Old fails after2 commands; quoted completes3; no synthesis command is present. |
| v2 frozen raw capture | 4 | Implicit solution; explicit timeout124; two manual macro solutions. |
| v2 unchanged primitive checker | 4 | PASS / CANNOT_CHECK / FAIL / FAIL. |
| v3 additive postprocessing | 2 | Two equivalence +two original-spec Z3 unsat/PASS receipts. |

v1's cause is only SMT-LIB string serialization of output routing.
v2 changes only the quoting. Its two macro outputs retain native fn_0 calls.
The unchanged primitive grammar rejects these calls correctly; that failure
does not say the returned functions are mathematically false.
The additive bridge expands only the frozen manual helper and checks equivalence
with the ORIGINAL macro-call program plus raw helper definition. The original
universal task specification is then checked separately with the fixed checker.
No solver output was rerun, retuned or replaced with a newly searched answer.

## Exact raw locations
- raw/manifest.json, LAUNCH.json, capture.py: original capture source/freeze.
- raw/controls-v1 and controls-final: harmless capture/timeout controls.
- raw/capture-v1: first27-file seal and complete raw inputs/streams/receipts.
- raw/check_outputs.py and check_outputs_v2.py: original root callers, including
  the separate object-schema guard. Neither is silently rebound.
- raw/checks-v1.json and checks-v2.json: original grades, including all FAILs.
- raw/successor-v2: quote-only inputs, setup source/red/green, successor manifest.
- raw/successor-v2/capture-v2: complete second27-file sealed raw capture.
- raw/postprocess-v3: additive source, manual AST controls and exact launch.
- raw/postprocess-v3/checks-v3: six-file seal, preserved original/expanded programs,
  independent equivalence obligations, four native checks and overall receipt.

READOUT.json records exact seals/grades and links all six freeze/result comments.
All scratch scripts and root caller versions are included. Every original raw
byte and each inner seal was checked read-only while copying; no semantic
regrade, runtime test or new actor was used to package the evidence.

## Source and replay boundary
Preparation is commit e91c3837; executed worktree head is ed2ce8cc.
The earlier generation-feasibility-20260906 packet and its source bindings remain
the pinned adapter/dependency intake. Source-bound manifests retain original
absolute paths as historical custody metadata; copied files are NOT rewritten.
Native runtime binaries and caches are external and represented by their actual
hashes/versions. They are not duplicated in Git or claimed reproducibly rebuilt.
Reexecution would be another run; these records are for inspection/custody.

The manual forced route establishes only output-path qualification.
The full macro route preserves primitive alternatives but adds a singleton
nonterminal that may affect search. Native annotations can arise through
reconstruction. No learned discovery, adaptation benefit, A−B residual, useful
cost crossover, persistent field admission or generalized cognition follows.
The explicit-primitive timeout remains a separate unresolved diagnostic.
