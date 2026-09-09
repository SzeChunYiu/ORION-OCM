# REUSE_AUDIT — GS R1 (worker O rows: host installability)

Coordinator instruction 2026-09-09: "mature tool not installable on any
real host" is a first-class audit row, and it justifies the in-repo
`search/` implementations as the reuse route (reuse-first means reusing
what CAN run, not violating the rule by importing what cannot).
Worker N's full audit (zoo/gs-round1) merges with this file; the rows
below are verified on the actual hosts this campaign runs on.

## Host installability matrix (all probed 2026-09-09, not asserted)

| tool | billy-laptop (py3.8.10, pip 25.0.1) | billy-old (py3.14.4, pip needs --break-system-packages) | LUNARC (module bio-suite-py3.12-torch, py3.12.11) | verdict |
|---|---|---|---|---|
| pyribs | resolves to 0.0.2 only (pre-history, useless) | resolves to 0.0.2 only (useless) | not in modules | NOT INSTALLABLE anywhere real — in-repo archive search is the reuse route |
| qdax (needs jax[cuda12]) | — | — | jax absent from modules; `pip install --user jax[cuda12] qdax` dies on home disk quota (nvidia cu12 wheel set >> quota; no writable project staging path) | BLOCKED on the only GPU host |
| jax | untested (CPU wheel irrelevant to lane) | untested | ABSENT + pip-staging BLOCKED (quota) | BLOCKED |
| torch | — | — | 2.7.1+cu12.9 PREINSTALLED, VERIFIED on A40 (job 3587172, cg05, matmul+cuda probe) | the GPU engine |
| deap | 1.4.3 installs OK | 1.4.4 installs OK | — | installable if an arm needs GA primitives |
| optuna | NOT resolvable on 3.8 | 5.0.0 installs OK | — | py3.14-only |
| numpy | 1.24.3 present | 2.5.3 installed this session | 2.2.6 | universal |
| scikit-learn | — | — | 1.7.0 | surrogate members run on LUNARC |
| cupy | — | — | 13.4.1 present (import verified on login; device use untested) | spare engine |

## Consequence for GS-R1 arms

1. QD library reuse is IMPOSSIBLE on every host of this campaign
   (pyribs dead-resolution on laptops, jax/QDax quota-blocked on LUNARC).
   The frozen arms therefore legitimately use the in-repo `search/`
   implementations + this lane's torch-backed batched evaluator
   (`gpu/t0_tape.py`); that is the reuse-compliant choice, not a dodge.
2. The verified GPU stack is torch 2.7.1+cu12.9 on A40 — the tape uses it
   as a column-array backend only (elementwise fp64, bit-identical to the
   CPU path), NOT as a learned component (#71 untouched).
3. Laptops: billy-laptop = py3.8.10/numpy 1.24.3 (12 workers),
   billy-old = py3.14.4/numpy 2.5.3 (11 workers). Both pass the full
   lane test suite (13/13) — compatibility window 3.8.10..3.14.4 held.
