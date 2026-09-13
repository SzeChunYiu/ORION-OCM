# Developmental life-cycle correction

Audit: 2026-09-13, source base `5622ac45d0261e8fe0a92f4209b1bb782ce43732`.

## Reproduced gap: GMI-AUDIT-DRS-01

DRS-1/3 selects a deployment/development resource frontier. The former checker
and section 10 instead discarded development cost after testing reachability.
At budget 3 it selected the program endpoint alone; its actual charged profile
`(1,1,3)` is incomparable with the neural profile `(2,2,2)`.

The default checker now retains development cost. Budget 3 yields two families,
and budget 10 yields three. The old family flips remain reproducible only under
an explicitly named `deployment_only` objective. This is a correction to the
mathematical example, not evidence that a physical architecture improved.

For any path records with the same endpoint, the deployment profile is fixed.
A lower scalar development cost weakly improves every life-cycle coordinate and
strictly improves the final coordinate. Thus all positive-cost cycles can be
removed before frontier selection; zero-cost cycles add histories but cannot
improve the endpoint/resource frontier. The finite witness now enumerates simple
path representatives and states that it does not enumerate every path history.
For vector costs, retain nondominated labels rather than an invented coordinatewise
minimum. Existential reachability is also distinguished from a single controller's
ability to find a successful path across unknown ecologies.

## Verification and authority

The initial six-method regression run had five failed subcases and two errors
against the old checker. The corrected eleven-method suite covers the budget-3 and
budget-10 tradeoffs, explicit deployment projection, starting conditions, equal-cost
distinct mechanisms, a cheaper alternative path, zero-cost cycles, malformed
budgets/costs, and full current-receipt replay.

Independent review strengthened DRS-2: under a fixed graph/profile declaration,
an expanded cap on the charged development coordinates cannot eliminate an old
life-cycle frontier point. Any supposed new dominator already met the smaller
budget. The new test checks frontier persistence across budgets 0 through 11.

Run:

```sh
python -m unittest discover -s research/gmi-grand-unification-v1 -p test_grand_gmi_developmental_lifecycle_v2.py -v
python research/gmi-grand-unification-v1/grand_gmi_developmental_reachability_checks_v1.py
```

`GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json` is the corrected authority.
The unchanged `GRAND_GMI_DEVELOPMENTAL_REACHABILITY_RECEIPT_V1.json` is historical
deployment-only evidence and does not support a life-cycle family flip.

This closes the identified accounting inconsistency and the finite witness's
cycle-termination defect under a complete memoryless graph and nonnegative
integral scalar costs. Empirical cost measurement, development-policy acquisition,
and unrestricted reachability remain separate obligations.
