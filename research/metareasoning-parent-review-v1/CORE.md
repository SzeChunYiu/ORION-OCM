# Metareasoning parents: source review and engineering decisions

This capsule turns primary-source reading into a bounded engineering plan.
It contains no new experiment, measured performance result or novelty verdict.

Start with [the mechanism mapping](OCM-METAREASONING-DONORS.md): paid computation,
proper termination and reusable investment already have substantial conventional
foundations. OCM should reuse them under their actual assumptions.

[The source review](review/THEORY-REVIEW-CORE.md) covers twelve named files at
ORION-OCM commit `9087971dd3a9847149fa8cf844cb13e84a57cacd` in PR154.
It identifies a general termination assumption gap, an exactness certification gap,
and contradictory stopping guidance. The numerical gap is not a demonstrated wrong
answer on the frozen population. The executable two-arm recurrence decreases its
horizon; the general note's termination gap does not establish a runtime loop.

The review is historical and specific to that snapshot. Later PR154 additions
require separate review; this capsule does not qualify the current whole PR.

## Decisions and open work

1. Keep the finite two-arm decision process as a conventional comparison model.
2. Give broader cognitive recursion a finite allowance, decreasing rank or an
   explicitly justified proper-policy contract before execution.
3. Implement the [scaled-integer certificate specification](review/THEORY-BOUNDARIES.md)
   in a separately registered qualification. Check exact action sets, ties and
   collision counts; retain existing floating-point outputs as historical results.
4. Replace the common-safe-action shortcut with the paid-cognition comparison.
   [The findings](review/THEORY-FINDINGS.md) give concrete mathematical witnesses.
5. For unknown-horizon reuse, qualify a ski-rental reduction or disclose an adapted
   baseline. Revocation and query-dependent costs need their own treatment.

These are open implementation/review tasks, not completed fixes to PR154.
No frozen corpus, study, source module, native verifier or learner was run here.
No neural mechanism is proposed for OCM. Useful performance and lifetime claims
still require matched implemented parents and measurements.

## Evidence

- [Fetched source identities](FETCHED-SOURCES.json) bind the named GitHub snapshot.
- [Independent source review](review/THEORY-REVIEW.json) records scope and findings.
- [Independent literature review](review/THEORY-LITERATURE-REVIEW.json) records corrections.
- [Later-head boundary](review/THEORY-HEAD-BOUNDARY-ADDENDUM.md) limits applicability.
- `FILES.json` binds this published capsule. Linked primary sources retain their
  original authority; local notes are interpretations, not substitute evidence.
