# Paid decision-region correction — current status

**Independently reviewed; integration into PR158 remains pending.** This is an isolated source correction, not a requalification of the published aggregate results or a runtime-adoption receipt.

The current source reuses PR159's exact represented-rational input foundation while preserving DRD's finite proper-tree min/max semantics. It repairs the maintenance guard and checks the declared three source files plus their loaded module paths. The final successor closes the missing `dev6` module-path check.

- [What changed and what remains](SCOPE.md).
- [Current source](source/research/paid-decision-region-v1/run_shortcircuit.py), [full integration patch](patches/integration.patch), [two-line successor delta](patches/successor.patch).
- [Independent original review](review/REVIEW-01.json) and [accepted blocker closure](review/SUCCESSOR-CLOSURE-02.json).
- [Historical 15-control qualification](qualification/historical-15/QUALIFICATION.json) and [one affected control](qualification/focused/child/RECEIPT.json), with [its process receipt](qualification/focused/PROCESS.json).
- [Exact-copy map](COPY-MANIFEST.json), [complete history archive](RAW.zip) and [every archive member](RAW-MEMBERS.json).

The 15 earlier controls were not rerun. The new control used synthetic cached modules; no real donor, full runner, frozen DEV6 sweep, native corpus, learner or CI was executed. Historical statuses remain unchanged in their original records; this page and the independent closure identify the current state.
