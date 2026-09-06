# PR87 packed-chart failure — exact-source audit

**Terminal: TEST_HARNESS_IMPORT_FAILURE.** One failed / 204 passed in the existing CI log.
The failing child did not reach runtime construction or the withdrawal/replay assertions.
No missing main integration explains this failure; no new runtime regression is established by it.

- Run34017850883, job101444761266: [exact job](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34017850883/job/101444761266).
- Reported PR head: `1509d23217a43e4024b442f66b242316bc877e55`.
- Actually executed merge: `2f1e5d625884972a1144ad9e0a3c504d06bd9f42`.
- Its first parent is current main `55bb3176484a7355ca103cbcda5efcb24ebd78f1`; second parent is that PR head.
- Log lines118–121 bind the executed merge; lines265–304 contain the complete failure and test totals.

## Cause and exact boundaries

`research/ocm-prototype/test_clia_reuse_cold_withdrawal.py:89–90` launches
`sys.executable -c WORKER` without an explicit import path or working directory.
The child's import at file line19 raises `ModuleNotFoundError: clia_reuse_study_common`;
its `OCMRuntime(...)` call at line25 has not executed.
The test's own parent imports succeed under pytest's collection path handling, which is
not propagated into the new interpreter's `sys.path`.

The helper exists at the expected path in both PR head and executed merge, with identical
blob `65501dccb233c06e0f56e2b3d570234c875c974e` and SHA256
`b3bb9c455f2e26e40334034cae1a9d74807acea01aba0c5dad45a132cbdae34d`.
The failing test is likewise identical in both commits, blob
`f133bcf358f9b74ffa6073caa9960abaf934059e` and SHA256
`970df9e44bd0eef3d4f4bea631ca158570f5a4a0433b35544a3bdcf9635df8c8`.

The workflow runs pytest from the checkout root and supplies only `OCM_G1_DEV_PATH`
(lines30–39); `scripts/m0_install_dev.sh` installs the project editable.
`pyproject.toml:22–24` packages only `src/ocm*` and `src/orion_v2*`, not prototype modules.
Thus installation of the core package does not make the prototype helper importable.
The workflow and packaging files are identical across head, merge and current main.

## Small repair after the v3 seal

Owner: learning_domains. Preserve the existing failed log and frozen v3 source.
Make this subprocess test self-contained by passing an explicit environment with paths
derived from the test's own `__file__` for repository `src` and `research/ocm-prototype`
(or an equivalent explicit local bootstrap); keep the current interpreter and assertions.
Do not fix this solely by broadening a laptop shell's ambient PYTHONPATH.
Qualify once with inherited PYTHONPATH absent, then run the scoped CI-equivalent suite on
laptop after the active experiment closes. Parent independently reviews the patch.
This is a fixture portability correction, not a policy normalization or replay relaxation.

## Custody

The exact downloaded log is retained unchanged as `job-101444761266.log`:
29,772 bytes, SHA256 `c48bda9c4659cd41809c412476c5e21134fac7b33390892d8add2b2640b4d3eb`.
`source-context.json` binds commits/trees; source copies and raw SHA inventory accompany it.
The audit used GitHub log/metadata plus `/usr/bin/git` object reads only. No source/env
changes, repository imports, tests, study calls or reruns were performed.
