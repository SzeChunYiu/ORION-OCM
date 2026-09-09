# GS Reuse Audit (#221 sec 2a) — reuse-first, self-build only the OCM residual

Created 2026-09-09 (GS-R0 prerequisite). Measurement + install probes are
reproducible: `hpc/measure_vectorizable.py`, `hpc/env_probe.py` (run on the
scoring host, never the Mac).

## 1. Installability (probed live, 2026-09-09)

| Host | Python | Verdict |
|---|---|---|
| LUNARC login (`lunarc`, module Python) | 3.11.5 | PyPI reachable from login; `pip install --user` works; Apptainer present; user-site shared with compute nodes (home FS) |
| billy-laptop | 3.8.10 | internet; sklearn 1.3.2, optuna 4.5.0 preinstalled; ribs installs only as 0.7.1 (no ProximityArchive) |
| billy-old | 3.14.4 | not reachable in the audit window (DNS from laptop); not load-bearing |

| Package | LUNARC user-site | billy-laptop | Role |
|---|---|---|---|
| pyribs (`ribs`) | **0.12.0 OK** | 0.7.1 (no ProximityArchive) | QD archives / novelty admission |
| scikit-learn | **1.9.0 OK** | 1.3.2 OK | surrogate heads |
| DEAP | **1.4 OK** | absent | GA/speciation toolbox |
| Optuna | **5.0.0 OK** | 4.5.0 | scalar BO |
| nevergrad | **BLOCKED** (home disk quota, `.local` at 3.7G) | absent | scalar optimizers |
| HpBandSter (BOHB) | **BLOCKED** (same quota) | absent | multi-fidelity daemons |
| QDax | not installed (CPU lane) | absent | GPU-vectorized QD — GPU lane asset |

Staging for compute nodes: user-site on the home FS is visible from compute
nodes, so login-node `pip install --user` suffices; no Apptainer needed for
R1. (`~/.cache/pip` was 3.8G and has been cleared.)

## 2. Component -> mature tool -> decision

| GS component | Mature parent | Decision |
|---|---|---|
| Novelty archive admission | pyribs `ProximityArchive` (k-NN novelty, threshold, capacity) | **INTEGRATED** — `search/novelty_viability.py:RibsNoveltyArchive` wraps it (k=15, static threshold 0.0, capacity=4096, seed pinned); builtin fallback kept, WHICH impl runs is pinned by `GRAND_SEARCH_R1_FREEZE.json` from `hpc/env_probe.py` on the scoring host. Documented delta: cap-overflow REJECTS vs builtin's evict-least-novel. |
| Surrogate heads (GSA5 allocation ranking) | scikit-learn `HistGradientBoosting` | **INTEGRATED** — `search/surrogate_allocate.py` impl="sklearn" (library defaults; `random_state` is the only knob). Stump/kNN ensemble stays as fallback; impl pinned by freeze. Surrogate still ranks promotions ONLY, never an OCM component (#71). |
| Multi-fidelity promotion (T0->T1->T2, eta=3, insurance) | HpBandSter/BOHB | **NOT INTEGRATED** — uninstallable (quota) AND architecturally hostile: BOHB needs a nameserver+worker daemon topology, while the campaign is frozen sbatch array tasks under a sha-chained manifest. The frozen SH loop is ~70 OCM-specific lines binding OUR tier evaluators; retained. Revisit only if R2 needs asynchronous budget reallocation. |
| Emitter/mutation loop | pyribs Scheduler + emitters | **NOT INTEGRATED in R1** — the parent mutation/crossover loop drives OCM-specific genome mutators (`morphology/mutations.py`); pyribs emitters would change the frozen arm algorithms. Flagged for R2 (ImprovementEmitter over the novelty measure space is a natural swap). |
| Scalar optimizers | Optuna, nevergrad | **REJECTED BY DESIGN** — the GS contract forbids scalar quality optimization (viability gates + novelty driver only). Installability is recorded, use is not. |
| DEAP toolbox | DEAP | **NOT INTEGRATED** — mutate/crossover are OCM genome-specific; DEAP would be ceremony, not reuse. |
| GPU-vectorized eval | QDax/JAX | **DEFERRED to the GPU lane** (separate worker; firehose evaluator). CPU R1 stays exact. |
| AutoML-Zero philosophy | Real et al. 2020 | **ADHERED TO as design principle** (primitive -> program genome -> mutate -> evaluate); no library to install — it justifies the genome/compiler residual below. |

## 3. Self-built residual (OCM-specific, correctly ours)

morphology genome+compiler, immutable-constitution C integration binding,
exact evaluator + tier definitions (T0/T1/T2), persistent developmental
lineage hooks, resource ledger (COST_MODEL_V1), held-out T3 battery
(`evaluation/t3_ecology.py`), failure memory (`search/failure_memory.py`),
freeze/sha-chain tooling (`hpc/freeze_gs.py`), campaign driver + hourly
checkpoints + adaptive-batch ledger (`hpc/submit_gs.py`,
`hpc/checkpoint_gs.py`).

## 4. Operator bottleneck: vectorizable fraction of T0

`results/REUSE_VECTORIZE_MEASUREMENT.json` — 300 candidates, seed 7,
billy-laptop, fresh-batch profile (see memoization note):

- exact T0: **0.151 ms/candidate** (viable 0.111, non-viable 0.098);
  viability in-sample 28/300 = 9.3%.
- pipeline split (named top-level cumulative): **compile/objects 37.4%,
  digest/canonicalize 28.8%, micro-world stepping (run_lifetime) 33.8%**.
- cheap proxy (genome features + novelty descriptors): **0.010 ms/cand
  (6.7% of exact)**; numpy-batched 0.018 ms/cand at N=300 (batch overhead
  dominates at this size — vectorization pays only at 10k+ batches).

Reading: only the ~34% micro-world-stepping share is a genuine
arrayification target; compile (branchy object construction) and
digest (canonical-JSON sha256) are inherently sequential/branchy.
A GPU proxy can therefore pre-screen at best ~1/3 of eval cost — and for
SCORED evaluations a proxy is forbidden anyway (exactness is the point of
the tiers). Conclusion for the GS-R1 CPU lane: vectorization is NOT the
bottleneck at 0.15 ms/cand (144M-candidate sweep ≈ 6 CPU-hours total);
the GPU lane's firehose matters only if T0 semantics are to be relaxed.

**Memoization finding**: `evaluate_genome` memoizes by genotype digest —
repeat candidates cost ~0 after first eval. This speeds mutated-parent
sampling in search arms (real compute saved, honestly charged) and is
recorded because it changes any future throughput model.

## 5. Consequences for R1

1. Freeze now REQUIRES `GS_ENV_PROBE.json` from the scoring host and pins
   `novelty_archive_impl` / `surrogate_impl` (no ambient behavior).
2. Smoke gate exercises the pinned impls on LUNARC before production.
3. The hand-rolled archive/surrogate survive only as frozen fallbacks.

## 6. Worker O host installability matrix (GPU lane probes, 2026-09-09)

Recorded verbatim from the GPU/laptop lane (#239). Probe divergence with
section 1, kept honestly, NOT adjudicated here: this matrix observes pyribs
0.0.2-resolution on billy-laptop where section 1 observed 0.7.1, and "not in
modules" on LUNARC where section 1's user-site install (login, module Python
3.11.5) holds 0.12.0. The campaign ground truth is `GS_ENV_PROBE.json` from
the scoring host (cosmos3, Python 3.11.5, ribs 0.12.0, sklearn 1.9.0), which
the freeze pins; neither laptop observation ever ran a scored evaluation.

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
