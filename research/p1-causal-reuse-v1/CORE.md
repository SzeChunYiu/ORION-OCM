# P1 tiny causal reuse (G2 macro + OS-process restart)

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) remaining **P1**
boxes:

```text
admit scoped learned method
restart
fresh task
actual use witness
measurable benefit
method-removal ablation
strongest persistent parent
```

Pinned production source: `src/ocm/learning/methods.py` blob
`50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`. No `src/` edits.

## Mechanism

This capsule is a **tiny end-to-end** over the existing G2 MACRO-token serving
in `research/g2-macro-operator-v1/` plus an **OS-process restart**.

`research/g2-process-restart-v1` is **not** on the remaining-gates base, so the
spawn is implemented here: `subprocess.run` of `python3 -B` on this file. The
child constructs a **new** `OCMRuntime` on the parent's persisted ledger, reloads
the live scoped macro, and solves a **fresh** polynomial task.

`G2.admit_macro` still reconstructs `OCMRuntime` in-process after `persist()`.
That reconstruction is recorded on the **same PID** and is **not** the P1 restart
witness. The restart witness is `child_pid != parent_pid` (and
`child_ppid == parent_pid`).

## Frozen small partition

| stratum | N | programs |
|---|---:|---|
| train | 2 | `(inc, square, inc)`, `(inc, square, double)` |
| admission holdout | 2 | `(inc, square, dec)`, `(inc, square, square)` |
| fresh test | 2 | `(inc, square, inc, inc)`, `(inc, square, double, dec)` |

The length-2 fragment `(inc, square)` is mined from training only (`support ≥ 2`)
and admitted only if it strictly reduces aggregate G2 enumeration attempts on
the admission holdout. Fresh fingerprints are disjoint from train and admission.
Budget: `slots=1000`, `max_length=4`.

## What this may CHECK

The seven remaining P1 boxes, **only if** every criterion in `RESULT.json` holds.

It does **not** close G2.4 (corpus experience, separated proof families, length-8
ecology). It does **not** emit unscoped `CAUSAL_METHOD_REUSE_SUPPORTED`. Ordinary
atomic JSON library persist is the executed strongest persistent parent; OCM live
is required to match it (no extra architecture residual on this microscope).

## Terminals

```text
P1_CAUSAL_REUSE_SUPPORTED_AT_POLYNOMIAL_MICROSCOPE
MACRO_TOURNAMENT_SELECTS_NO_METHOD
NO_OS_PROCESS_RESTART
NO_ACTUAL_MACRO_USE
NO_MEASURABLE_BENEFIT
CANNOT_CHECK_METHOD_REMOVAL_ABLATION
CANNOT_CHECK_ORDINARY_PARENT_PARITY
P1_CAUSAL_REUSE_INCOMPLETE
```

## Run

```sh
python3 -B -m unittest discover -s research/p1-causal-reuse-v1 -p 'test_*.py' -v
python3 -B research/p1-causal-reuse-v1/experiment.py --out research/p1-causal-reuse-v1/RESULT.json
```
