# G2.4 OS-process restart (not in-process reconstruction)

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G2.4 checkbox
**“machine process restarts”**. Owner of the defect: PR [#192](https://github.com/SzeChunYiu/ORION-OCM/pull/192)
(`research/g2-macro-operator-v1/`), which called `OCMRuntime(root)` again in the
**same** Python interpreter after `persist()` and treated that as restart.

That is object reconstruction. It does not earn G2.4/002.

## Mechanism change

This capsule **spawns a separate OS process** (`subprocess.run` of `python3 -B`
on this file). The child:

1. constructs a **new** `OCMRuntime` on the parent’s persisted ledger root;
2. reloads the live generator with `methods.load_generator`;
3. solves a **held-out** polynomial task that was not used in training or
   admission validation.

The restart witness is `child_pid != parent_pid` (and `child_ppid == parent_pid`).
An in-process `OCMRuntime(root)` control is recorded on the **same** PID and is
explicitly **not** the G2.4/002 witness.

## Frozen small partition

Pinned production source: `src/ocm/learning/methods.py` blob
`50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`. No `src/` edits.

| stratum | N | programs |
|---|---:|---|
| train | 2 | `(inc, square, inc)`, `(inc, square, double)` |
| admission holdout | 2 | `(inc, square, dec)`, `(inc, square, square)` |
| fresh test | 2 | `(inc, square, inc, inc)`, `(inc, square, double, dec)` |

Admission holdout is required by `admit_generator`. Fresh fingerprints are
disjoint from train and admission. Budget: `slots=1000`, `max_length=4`.

## What this may CHECK

**G2.4/002 machine process restarts** — only if the OS-process criteria hold.

It does **not** emit `CAUSAL_METHOD_REUSE_SUPPORTED`. It does **not** close the
rest of G2.4 (corpus experience, separated proof families, #192 length-8
ecology). Retrieval / answer-cache / ablation are measured **at this
microscope** so the restart box is not a vacuous persist.

## Terminals

```text
OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED
NO_OS_PROCESS_RESTART
IN_PROCESS_RECONSTRUCTION_ONLY
HELD_OUT_SOLVE_FAILED
```

## Run

```sh
python3 -B -m unittest discover -s research/g2-process-restart-v1 -p 'test_*.py' -v
python3 -B research/g2-process-restart-v1/experiment.py --out research/g2-process-restart-v1/RESULT.json
```
