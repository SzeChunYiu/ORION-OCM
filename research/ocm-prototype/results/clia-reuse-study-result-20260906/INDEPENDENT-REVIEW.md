# Reuse v3 — independent evidence and child-import review

**Verdict: no material discrepancy found in the bounded published result.**
Reviewer: hostile_design; read-only review completed 2026-09-06.
Owner #62; acceptance #38/#49; implementation/evidence PR87.
Reviewed publication: https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5557705923
No actor, solver, model, grader or test was executed by this reviewer; no source was edited.

## Exact reviewed custody

Frozen execution source: `1509d23217a43e4024b442f66b242316bc877e55`.
F0 SHA256: `629172c51fa0e6dc1ce6419de3ffe8e347d65b3e8136de4e7a7b66a3b8edd213`.
F1 SHA256: `b890f876d754b82b220fd6fd988b1780c697cf8428cba6cdca02df702f46450b`.
Receipt SHA256: `7954fd7e07dc5d244979d7fc7af69edc6d171d3e1aef200dc43f6878aa52267f`.
Grade SHA256: `a34e53904838959f969174cb39410356631d61f0c634ebd85ebac6c7fe1ba1d9`.
Cleanup SHA256: `c37af0f48ba61746d34243155a16ab8dea1bcc40c1ea7c8f9f48fb9b3032fdbd`.
Raw seal binding: `8204dd4bbd9f14777a5d8b0523c7b983d688a04827a62996ae80f809ebf8e4c8`.
The execution lane's full 322-file seal verification was not repeated in this review.
Raw root: `/home/billy/orion-director-work/20260906/clia-reuse-capture-v3`.
Local receipt, grade and cleanup copies were hashed; selected raw rows/F1 were read on laptop.

## Functional evidence

The receipt records twelve distinct actor stages, each exit zero and without timeout.
Each arm retains 43 assignments: two acquisitions, 36 applications and five syntax observations.
Each has 34 correct authorized values, two expected policy refusals and zero unchecked rows.
Both acquired max3 descriptors bind program SHA256
`3ac00c37400fc26525779a0ba0cf002cad5e3c5a175a5f304dee04464cb0b5fd`.
The five syntax observations are equal within/across arms; this is one repeated retention diagnostic.
It is not five independent language tasks, a new accuracy estimate or a capability-comparability test.
Actual acquisition calls are two syntheses per arm, with two native versus six OCM verifications.
Post-acquisition records contain 34 application and five syntax calls per arm, with zero synthesis.

Both actual withdrawal rows have independently DEAD lower/upper F1 support and no selected value.
They contain no backend invocation events; native explicitly reports `REFUSED_DEAD_SUPPORT`.
OCM's descriptor is exploratory-only, excluded from warranted extraction and composition;
commitment then refuses. Generic `NOT_ADMITTED` alone was not treated as policy evidence.
During withdrawal, 19 audited registration-dependent prior records are DEAD and 17 unaffected
records remain LIVE. These are the actual audited record denominators, not all possible descendants.
Same-ID reinstatement occurs at the end of withdrawal; fresh restore then succeeds without a new action.
Inspected prior record payload hashes remain unchanged; history evidence overlaps neither support bound.
This supports `EXECUTABLE_REUSE_DEVELOPMENT_SUPPORTED` and `PARENT_SUFFICIENT_FUNCTION_ONLY`.
It does not establish OCM-specific learning, local training-data deletion, sparse cognition or superiority.

## Supervisor failure and cost boundary

Retained supervisor-negative SHA256: `fc951500ff4a0bcb14c7ccfc1a3390b15fb26b09f213f4acb873a83a3ad6dff4`.
Retained traceback SHA256: `1c4ae133879a81ef117a8de3d843a92f1a5507619e7cab0a59fe540a35e9ebcb`.
The traceback was preserved retrospectively from tool output, not initially redirected supervisor stderr.
Frozen helper lines120–132 show wait4 reaping precedes the failed `os.waitstatus_to_exitcode` call.
Thus the outer reporting failure follows capture reaping; its missing PID/exit/CPU are not reconstructed.
Cleanup records all 24 actor/native PIDs absent and no exact-root capture/worker/grader argv matches.
Summed actor wall is 4.752680 s native / 21.754922 s OCM; direct wait4 CPU is 4.702995 / 19.247037 s.
These match the published rounded observations. Complete descendant CPU, training and F0 preparation
remain outside the measured total. `CANNOT_CHECK_COST` is preserved separately from finite function.

## Post-seal child-import correction

Reviewed file: `research/ocm-prototype/test_clia_reuse_cold_withdrawal.py` in the study worktree.
Before SHA256: `970df9e44bd0eef3d4f4bea631ca158570f5a4a0433b35544a3bdcf9635df8c8`.
After SHA256: `9438acba18f392ba4dde034e5f8c2ef5588f3cfe9a5dcbe1b467335a43acb4d7`.
The diff adds os/Path, derives repository src + prototype import paths from __file__, and passes
explicit child environment/cwd. The worker body, interpreter choice and lifecycle assertions are unchanged.
Inspected retained control: `clia-reuse-child-import-fix/{control.log,control.xml,completed.json}`
under `/home/billy/orion-director-work/20260906`; ambient PYTHONPATH was removed.
The existing XML reports one pass, zero failures/errors/skips, 1.397 s; final source hash matches above.
**Source review cleared. This test was executed by the implementation lane, not this reviewer.**
The earlier CI failure remains retained separately; it occurred before child runtime construction.
