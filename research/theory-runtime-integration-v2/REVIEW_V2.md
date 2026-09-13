# Integration V2 source and obligation review

Date: 2026-09-13. Coordinator code/contract review; no independent external
reviewer or scientific replication is claimed.

V1's reopening is correct: a full source inventory was part of its eligibility
contract. Replacing only its terminal or refreshing its old receipt would hide
the changed implementation. V2 uses a new directory and a new current-runtime
anchor while keeping the exact ORION-V2 theory and M1–M4 mappings.

## Semantic mapping and dependency review

`learning/methods.py`, `science/finite_identification.py` and
`evaluation/method_learning_eval.py` are Git-blob-identical to the V1 runtime.
The theory still supplies the finite grammar/slot statement, polynomial
normalization and nonzero-polynomial counterexample argument, distinct-task
fragment learning with independent support obligations, and finite noiseless
version-space identification. No new source theorem is inferred from this
engineering update.

M1 and M2 call the same `solve`, `normal_form`, `execute`, `verify_solution` and
task-fingerprint implementations. The finite checks exercise all registered
short programs and targets, fair primitive fallback, empty budgets, and a
candidate that fits two samples but fails polynomial identity. M4 calls the same
frozen prediction table and minimax query logic, compares the actual selected
query and every survivor set to the separate theory checker, and reopens every
single-observation constraint. The proof assumes deterministic accurate
observations and an in-class truth; simulations do not validate those assumptions.

M3 depends on runtime construction, evidence/object admission, ledger persistence,
state reconstruction, revocation and liveness. These dependencies were changed
even though the learning module was not. Runtime changes include current-state
callback/commitment guards, indexed extraction/operator navigation and explicit
accounting; store changes include ledger event and storage support; KSO changes
include exact warrant and navigation structures. The packet binds the complete
current source, imports a private source copy, reruns the actual persistent
generator path and retains a source-hash inventory of loaded modules. Importing
a solve/navigation module is not evidence that every new solver path was exercised.

The separate lifetime, self-model intake, language/frontend, semantic comparator
and evaluation changes are conservatively bound too. The V2 checks do not
promote their programme statuses. `lifetime/machine.py` now distinguishes the
legacy comparator and checks adoption predecessor history; `selfmodel/intake.py`
contains additional open obligations. These changes supply no M1–M4 authority
merely because they appear in a source inventory. `RUNTIME_DELTA_V2.json` is the
complete 44-file change register, not a claim of full behavioral coverage.

## Recursive defect found during revalidation

V1 checked revocation of only the first training support. M3's contract says
every essential training proof and holdout-comparison support must disable reuse.
V2 adds three separate temporary-runtime executions, one for each of the two
training supports and one for holdout validation. Each must load the generator
after restart before revocation, reject loading after revocation and another
restart, retain the generator object, and preserve the exact prior event-hash
prefix. This tests the missing conjunctive-support cases without changing runtime
code or converting the two authored holdouts into population evidence.

## Custody and comparison review

The new checker retains V1's actual Git-object resolution, canonical paths,
working-byte checks, explicit row revocation and private source copies. It adds
loaded-module source checks and exact whole-payload deterministic comparison.
Manifest parsing rejects duplicate keys and non-finite numbers. The comparison
preserves scalar types, so `true`, `1` and `1.0` cannot silently substitute.
The checker, binding tests, manifest, README, this review, delta register and V2
workflow are themselves hashed in every result. The replay does not hash itself;
its legitimacy still depends on reviewed publication and the trusted host.

The V2 workflow fails on drift, missing evidence, revoked support or replay
disagreement. The historical V1 workflow's warning behavior is preserved only
for its historical contract. New V2 engineering support cannot silently survive
a later runtime change. No adoption or scientific authority field is broadened.
