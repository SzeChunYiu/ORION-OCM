# Qualified behavior and measured controls

The [accepted closure](review/CLOSURE-02.json) reports no remaining structural
source/control blocker. It accepts the original source assessment together with
one separately observed missing case; no combined nine-case rerun occurred.

The original eight methods cover composite argument holes; noninjective and
consistent repeated-variable substitutions; essential/binding refusals; floating
contract order; logical assertion roots and malformed traces; explicit unsupported
scope; one selected shared occurrence; and identity/path/size refusals.
Their test03 still used one essential slot. It did not establish distinct equal-
statement slots, despite the original qualification prose. See [original review](review/REVIEW.json).

The new [affected control](source/check_slots.py) uses two distinct slots with the
same statement and different proof derivations. Retained [inputs](records/affected-slot/INPUTS.json)
and [outputs](records/affected-slot/CONTROLS.json) bind floating arguments [7,8,9]
and essential arguments [15,23]. The independently authored 20-label replacement
preserves order; swapped saved arguments [23,15] are refused. Both production
modules, three validators, fixture helper and authored fixture remain byte-identical.
Only the control entry/filename/count changes in [the qualifier delta](patches/QUALIFIER.diff).

| Recorded run | Methods | Child PID | Child wall s | Qualifier window s | Peak RSS KiB |
|---|---:|---:|---:|---:|---:|
| Original | 8 | 2446363 | 0.069849079 | 0.374776516 | 56,228 |
| Affected successor | 1 | 2467304 | 0.039121325 | 0.326433211 | 56,568 |

Both children were reaped at exit 0. Original user/system CPU was 0.061700 /
0.007712 s; successor 0.034929 / 0.003881 s. Each child window is nested in its
qualifier window. Qualifier timing includes pinning/readback and excludes initial
interpreter imports and final receipt serialization; authoring/review is not zero.
These are authored-control costs, not serving benchmarks or lifetime accounting.

For each retained run, 2,012 source/runtime pins and 82 file-backed module names
reconcile with the accepted review. The successor retains exact authored inputs,
full observations and five source snapshots. No original suite, native verifier,
retained-proof/corpus/parser or learner execution was added by this correction.

All adapter outcomes retain native_acceptance=false. Caller-supplied authority
identifiers and the fixture's historical NATIVE_VERIFIED marker provide no fresh
native acceptance or current evidence-registry liveness. [Interface limits](INTERFACE.md)
and a separately qualified [caller](NEXT.md) remain essential.
