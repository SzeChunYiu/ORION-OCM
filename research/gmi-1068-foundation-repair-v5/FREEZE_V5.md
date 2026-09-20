# Foundation repair freeze — #1068, round E

Baseline: ebff2f3ea4e4c1adbcb591b1c68bffe34deb25cd.
This commit contains protocol only, before successor implementations or results.
#1068 is the control plane; #833 and frozen V1–V4 evidence remain historical.

## Questions and falsifiers

1. R1 admissibility: determine the exact conditions under which admissible
   processes form a subcategory. Test failures of identity inclusion and
   composition closure, including bounded resource constraints. State a typed
   state/resource lifting construction with its explicit assumptions; do not
   infer arbitrary physical admissibility from an ordinary category.
2. R2 aggregation: test the universal assertion that a scalar across contexts
   requires weights or a measure. Compare worst-case, best-case, weighted and
   Pareto comparisons on complete finite profiles. Prove the precise distinction
   between a declared aggregation functional and expectation under a measure.
3. Preserve parent ownership and show how the corrected premises affect all
   registered dependent rounds. No primitive-count or prior-free completeness
   claim is earned by this repair.

## Evidence committed to before implementation

- General paper proofs with exact hypotheses and counterexamples.
- Admission-free Lean 4.19.0 for feasible central logical statements; explicitly
  separate kernel statements from paper-only extensions.
- Exact finite enumeration and an independently implemented oracle.
- Hostile tests for missing identity, nonclosed composition, falsely forced
  weighting, illegal resource joins and stale dependency promotion.
- Bind source/receipt hashes and record every original R0–R17 atomic ID unchanged.
- Independent internal hostile review and CI on the exact proposed head.
- Merge using ancestry-preserving merge so this freeze precedes implementation.

## Authority and remaining work

The result may correct R1/R2 and support local obligations. It cannot establish
complete R0–R17 closure, a unique foundation, zero inductive bias, recovery of
all intelligence families or real-scale validation. New defects are followed
through the reverse dependency cone. UNKNOWN and CANNOT_CHECK remain valid.
