# PR154 mathematical and numerical source review

Commit: `9087971dd3a9847149fa8cf844cb13e84a57cacd`. Review scope: named source snapshot only.

Three actionable findings:

1. **P2 — define termination for same-horizon cognition.** The general Bellman
   note permits a zero-cost cognitive cycle without stating a well-founded
   recursion or proper-policy convention.
2. **P2 — certify exact action sets before reporting exact collisions.**
   The implementation uses floating-point values and tolerance-based ties.
   This proves a mismatch with its exactness claim, not a demonstrated wrong
   row in the frozen population.
3. **P2 — remove the obsolete common-safe-action stopping shortcut.**
   The README still prescribes the implication that the newer formal note
   explicitly corrects.

[Actionable findings and by-hand witnesses](THEORY-FINDINGS.md).
[Oracle validity, limitations, and repair specification](THEORY-BOUNDARIES.md).
[Source custody and review metadata](THEORY-REVIEW.json).

The R0B executable DP does decrease its horizon on both arms. The generic
same-horizon issue is not evidence of a loop in that executable.

No study, source module, native verifier, learner, protected corpus, or test
suite was executed. No empirical result, broad novelty, or paper-readiness
verdict is inferred.
