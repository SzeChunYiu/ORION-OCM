# GMI empirical closure programme — status against the A–K brief

Date: 2026-09-12. Base: `main` at `291045db`, merged with the executable lane. Freeze witnessed at `d9aa44aa`.
Branch: `claude/gmi-lunarc-empirical-closure`.

**This document does not flip any terminal.** Both remain `FALSE`:
`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE`,
`NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE`.
No RED is deleted, weakened or rewritten. The V1 real-transfer RED and the earlier grammar-bias and developmental
falsifications stand untouched.

## 0. Two facts that determine everything below

**LUNARC is not reachable from the container running this work.** No SSH keys, no slurm client, all login hosts
unreachable, egress proxied to GitHub only. Verified, not assumed. Execution therefore goes through the owner's
machine; a bridge session (`session_01XCJ3pULKAxYqL2hfdNURGy`, Remote Control, connected) has been tasked with
reconnaissance and will report by committing `LUNARC_ENV_PROBE_V1.json` to this branch. **Array sizing is deliberately
left unrendered until that probe lands** — `hpc/gmi_k4_array.sbatch` carries `__ACCOUNT__`, `__PARTITION__`,
`__WALLTIME__`, `__MEM__`, `__ARRAY__` placeholders and is *intended to fail* if submitted unrendered, so the sizing
comes from the measured environment rather than a guess.

**`main` never contained the executable machinery.** The GMI work on `main` is documents and standalone scripts; the
charged `Machine`, ecologies, zoo, morphology IR and search live on the `claude/gmi-d0-d1-research-dnbp8i` lane and
were never merged. They are merged here — cleanly, only four files differed — so the empirical programme has a meter
to charge with. Anyone reading `main` alone would conclude, wrongly, that no instrument exists.

## 1. Delivered in this session

| item | status |
|---|---|
| `GMI_INDEPENDENCE_GATE_DECOMPOSITION_V1.md` | **done, pushed** — refines `EF-2`; 3 of 5 sub-gates close with no external author |
| `GMI_K4_LOFO_FREEZE_V1.json` (+ generator) | **done, pushed and witnessed at `d9aa44aa`** — 22 families, 10 axes, 3 grammars, zero vector collisions |
| `hpc/gmi_k4_array.sbatch`, `hpc/gmi_k4_task.py` | **done** — part-J discipline enforced in code |
| LUNARC reconnaissance | **dispatched** to the bridge session; awaiting `LUNARC_ENV_PROBE_V1.json` |
| `gmi_k4_search.py` (the three grammars) | **NOT BUILT** — see §3 |

### The independence workaround, in one line

The gate is not atomic. `IG-1` generator discretion closes by **exhaustion** (a constant map is independent of
everything); `IG-2` seed discretion closes by **future public entropy**; `IG-3` predictor leakage closes by
**third-party-witnessed commit order** — the git forge is an external process and supplies exactly the tamper-evident
ordering the gate needs. What remains is `IG-4` meter **bucketing** and `IG-5` grammar **primitive selection**, which
genuinely require an external author and are marked `PENDING`. That residue is strictly smaller than the gate the
register has been treating as blocking, and the difference is what unblocks C5-shaped work.

## 2. What the freeze commits us to

264 array tasks: 22 families × 3 grammars × 4 width cells. Per family the freeze fixes an implementation-invariant
property vector over ten axes, the obligation the family is the cheapest answer to, a quantitative phase prediction, a
negative twin and a kill condition. The search is handed **an obligation and a grammar, never a name**; `name_key` is
stripped by the runner before anything touches it.

Known-control recovery (`CTL_IDENTITY`, `CTL_CONSTANT`, `CTL_LOOKUP`, `CTL_AFFINE`) and the coverage bound (1e6 scored
candidates or exhaustion) are frozen **in advance**, because the brief's rule — a failure may not be blamed on search
unless the controls were preregistered and fail — is only meaningful if they were not chosen after a disappointing
run.

## 3. What is NOT built, stated plainly

`gmi_k4_search.py` — the three grammars, the obligation generators, property-vector measurement and the verdict
logic — **is not implemented.** It is the scientific core of part A and it is a substantial engineering job: three
genuinely independent primitive systems (tensor dataflow, register program, finite-state message passing), each with a
charged meter over nine cost channels, plus 22 obligation generators.

**The honest consequence: no K4 verdict exists for any family, and none may be reported.** The freeze is real and
witnessed; the benchmark it describes has not been run. Reporting the freeze as if it were evidence would be exactly
the failure mode this programme exists to prevent.

Parts **B** (K5 held-family prediction), **C** (neural developmental regime), **D** (routing/MoE), **E** (generative
lifecycle curves), **F** (control and exploration), **G** (continual development) and **H** (fresh real transfer) are
**not started**. Part **H** additionally needs pinned real workloads that this container cannot fetch — its egress
reaches GitHub only.

## 4. Sequencing that follows from the above

1. Probe lands → render the sbatch against measured partitions/limits → pilot array at tiny budget → confirm the
   receipt discipline end to end (including a deliberately failing task, to prove failures are receipted).
2. Build `gmi_k4_search.py` grammar by grammar. One grammar end to end is worth more than three half-built: a cell
   whose grammar is unimplemented must report `INCONCLUSIVE_GRAMMAR` **by construction and say so**, never a silent
   pass.
3. Only then freeze the protected configuration and launch the untouched protected array.
4. Parts B–G follow the same freeze-then-run discipline. Part H waits on real workload snapshots.

## 5. Terminal, as strong as the evidence actually supports

```text
LUNARC_EXECUTION_PATH_ESTABLISHED_VIA_BRIDGE          = PENDING_PROBE
INDEPENDENCE_GATE_DECOMPOSED_AND_PARTIALLY_CLOSED     = TRUE   (IG-1, IG-2, IG-3)
INDEPENDENT_METER_BUCKETING_AND_PRIMITIVES            = PENDING_INDEPENDENT_EVIDENCE
K4_LOFO_PREDICTION_FROZEN_AND_WITNESSED               = TRUE   (d9aa44aa)
K4_LOFO_EXECUTED                                      = FALSE
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_SCOPE       = FALSE
NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_SCOPE    = FALSE
```

The one genuinely new closure is the independence decomposition. Everything else delivered here is apparatus, and
apparatus is not evidence.
