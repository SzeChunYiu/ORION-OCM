# Combined main integration: PR87 + PR89

**133 focused, 1,006 full and 205 scoped N1/G1 tests passed.**
All 12 current engineering wrappers and archived V5 custody verified.
Owner: #38 / #62 / #72. Classification: INFRASTRUCTURE.
Authority: ENGINEERING_REGRESSION_ONLY; no scientific promotion or actor rerun.

## Exact change and receipt

Normal merge of main `504c320e6a8c9fa8a2e593ded0b4846ce073021b`
into PR87 parent `7c02ffa0bca54b92be0e8bf92906147b7e7b754b`.
The only textual conflict was the current engineering selector. All source merged
cleanly, retaining the concurrent N1 changes plus the independently reviewed runtime
quarantine/proposal replay fixes and their regression tests.

Neither parent receipt covers this combined inventory. The existing recorder ran
both unchanged gate recipes once and selected a new immutable record only after success:

- Source: `c7cdd3a10a8274083e870c3ee9394b83d5bc49800743bee0928410e8da353963`, 310 files.
- Receipt: `1b9114d87fd76a49a78ad25905e7d982638c722e6f8cbc7acced9d21128ad97e`.
- [Immutable run](../runs/c7cdd3a10a8274083e870c3ee9394b83d5bc49800743bee0928410e8da353963/fbabc44446644c4b/RECEIPT.json).
- [Conflict/source diagnosis](raw/conflict-diagnosis.json).
- [Executed wrapper, research and preservation verification](raw/verification.json).

## Preservation and scope

All 248 prior PR87 and 242 main provenance blobs, except the replaceable selector,
remain byte-identical. All sealed files in the three original study attempts
(213 / 320 / 322) and the previous portable result packet still match their hashes.
The executed study remains bound to `1509d23217a43e4024b442f66b242316bc877e55`.
[Post-capture actor-source changes](raw/actor-source-integration.json) are recorded
separately; current integration does not rewrite F0, raw outputs, grades or claims.

## Verification and operating cost

The fixed engineering recorder used the existing receipt-env: 34.446 s focused,
229.511 s full, 264.532 s outer wall. The scoped research suite used existing g1-env,
with ambient PYTHONPATH removed and the custody-bound EWT development input.
It passed in 32.794 s outer wall with zero skipped, failed or errored cases.
Host-only hosted tests and archived results remain excluded as in current CI.

The [exact verification script](raw/qualify.py), launch records, stdout/stderr and
JUnit are retained. It assumes the recorded laptop paths; no environment changed.
Per-gate reaped-child CPU is reported only in its recorded scope. Complete process-tree
CPU, energy and development/setup work are unmeasured; no efficiency claim follows.
Future source edits require a new actual run under the [existing protocol](../README.md).

The [whitespace check](raw/whitespace-check.json) records one inherited EOF blank
line in the concurrent N1 note. That note remains exact main bytes; integration
paths pass the check. No functional or qualification failure occurred.
