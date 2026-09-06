# Contract and executable handoff

## Scope and reuse classification

- Z3 parsing, substitution and simplification: ADAPT, fixed application mechanism.
- Existing CLIA grammar gate and Z3 universal checker: ADOPT, checker/tool.
- Existing production registry, replay and SV.solve: ADOPT, mechanism under study.
- NativeLibrary: ordinary persistent library comparator with the same descriptor,
  application engine, pointwise checker, host cache and support powers.
- max3/guard2 public specifications: exposed development tasks, not protected tasks.

## Data and host boundary

`clia_reuse_descriptor.create(task, candidate, support, history=...)` accepts only
these two existing public tasks, checks the explicit grammar, and runs the existing
universal checker. It stores canonical program/spec data, exact checker/evaluator
source digests, Z3 version, both support bounds and the real check receipt.
`program_sha256` binds mathematical code and task. Descriptor IDs also bind receipts
and support; independent acquisitions can have different descriptor IDs/timings.

`CompiledProgram` uses the fixed Z3 parser/substituter/simplifier. No code object is
serialized. `check_value` separately reparses canonical data and checks the claimed
exact integer against P(tuple). It binds typed arguments, descriptor and program ID.
Its use of the same Z3 engine is explicit; external public-spec scoring remains needed.
Universal correctness alone cannot certify an arbitrary returned value.

Only the host explicitly binds callable implementations after restart. Loading,
auditing or applying a request cannot repair withdrawn authority. Importing an
external native descriptor reruns universal verification; normal rebinding does not.
Source changes invalidate the bound checker prior and require explicit reacquisition.

## API

- OCM acquisition: `clia_reuse_vessel.adopt(runtime, admitted_proof_atom, history=[...])`.
  This requires a live SPECIFICATION_VERIFIED_PROGRAM proof and expands its actual
  evidence warrant to assumption support. It performs no synthesis.
- OCM host: `bind(runtime, descriptor_id)`; then `query(runtime, request)`.
- Native: `NativeLibrary(root).acquire(task, candidate, support, history=[...])`,
  `bind(descriptor_id)`, `apply(request)`; `install` is the checked import route.
- Application request: exactly `kind='clia_apply'`, `program_id`, `arguments` (three
  exact Python integers within the inherited grammar's 4096-bit operational bound).
- OCM `audit(runtime)` and native `audit()` enumerate descriptors and previous
  application answers with current LIVE/DEAD/UNKNOWN support and binding state.
- Revision uses actual assumption IDs: runtime/native `revoke([...])` and
  `reinstate([...])`; the OCM caller persists revision events explicitly.

The OCM wrapper delegates syntax/synthesis to the existing G1 query/admission path
through its optional catalogue-builder hook. Application uses the same production
SV.solve and a fixed pointwise admission gate. Every offered operator ID is reported;
backend visits are separate. Non-applicable visits, rejected checks and global SV
work remain chargeable. Native has all tools available and may dispatch efficiently.

## Support and observation limits

Descriptors and new answers retain the real per-function query-registration support
AND shared CLIA prior. Query withdrawal can distinguish max3 from guard2. Shared
CLIA withdrawal is intentionally global to both. No local training-point deletion
or learned lexical revision is claimed. The pre-existing CLIA support atom is not
retroactively relabelled as search-only evidence.

History-only IDs must be separate known OCM assumptions and disjoint from BOTH
support bounds. A native two-bound DNF implementation mirrors LIVE/DEAD/UNKNOWN and
alternate-support semantics; one surviving OR support remains live. Stored answer
liveness is assessed with current revocations, without mutating history.

## Actual controls and retained diagnostics

Final command: `PYTHONPATH=<worktree>/src <g1-env>/bin/python -m pytest -q`
followed by the four test paths in `raw/combined-final-command.json`.

- `before`: missing implementation collection error, before the adapter existed.
- `audit-before`: three red controls for boolean tuple aliasing and missing audit APIs.
- `history-bound-before`: real lower-only support/history overlap accepted; repaired
  by checking both bounds during create and validate, with clean separate-history control.
- `combined-reviewed`: two failed assertions incorrectly equated offered catalogue
  with backend visits; corrected to the actual production SV input filtering rule.
- `combined-final`: 55 pass, zero failures/errors/skips; source unchanged during run.

Earlier unbound red logs are development history, not final-source scientific tests.
Unit applications exposed `[41,-7,12]`, `[17,-9,0]`, `[0,0,0]`, `[-17,9,0]`;
malformed requests and all test files are public/exposed too. Two archived real donor
candidates are verified/compiled without applying tuples. The prospective panel
must exclude exposed valid tuples and retain its independent custody record.

## Requirements before the prospective study

1. Merge the selected current main, freeze all runtime/donor/source dependencies and
   model/data hashes, tuple/phase order, outer resources and external grader before acquisition.
2. Independently acquire once per arm with identical public input and tool access;
   record actual synthesis/check calls. Freeze program/support/alias mappings before
   applying tuples. Require identical canonical program hashes or report
   CANNOT_CHECK_IDENTICAL_DONOR_BINDING without selecting replacements.
3. Include new tuples, actual syntax retention and withdrawal/restoration phases.
   Enumerate affected descendants and unaffected answers, including incomplete rows.
4. Meter acquisition, host rebind, application, checker and outer process-tree CPU,
   wall, replay, state and archive bytes. Native counters are LIBRARY_ONLY;
   synthesis_calls_in_library=0 does not meter external acquisition. OCM dispatch
   counters distinguish availability from actual backend calls; they are not CPU totals.
5. The external grader independently checks public specification semantics and
   wrong-value controls; compare values/trees, not timing-bearing output JSON.

This adapter is a single-writer development implementation, not an atomic concurrent
library service. Its controls establish a runnable bounded mechanism, not scientific
promotion, lifelong learning, local model influence deletion or parent superiority.
