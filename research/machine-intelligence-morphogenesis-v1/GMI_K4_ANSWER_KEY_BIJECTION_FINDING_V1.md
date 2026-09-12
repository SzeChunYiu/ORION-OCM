# K4 engine review — the shape inventory is in exact bijection with the answer key

Status: **BLOCKING DEFECT FOR ANY `K4_RECOVERY_GREEN` CLAIM / NOT BLOCKING FOR THE MERGE**
Date: 2026-09-12. Reviewing `gmi/k4-engine-empirical-v4` (33 commits) against `GMI_K4_LOFO_FREEZE_V1.json`.

## What the branch gets right, first

The Codex lane built the thing this lane had flagged as missing, and its own self-audit is unusually honest:

* `GMI_K4_ENGINE_SCOPE_AND_SELF_AUDIT_V2.md` **retires V1 as protected evidence** because its outcomes were seen while
  the harness was still being engineered — and preserves it as development evidence rather than deleting it. That is
  the correct handling and it was volunteered, not extracted.
* It labels its own output `K4_PALETTE_PHASE_EVIDENCE__FULL_GRAMMAR_NATIVE_RECOVERY_PENDING` rather than
  `K4_RECOVERY_GREEN`.
* `gmi_k4_grammar_native.py` states plainly that **`IG-5` remains PENDING because the same author selected all three
  primitive inventories** — correctly citing this lane's own sub-gate rather than claiming it closed.
* The rewritten `hpc/gmi_k4_task.py` **preserves both rules that were enforced in code**: `freeze.pop("name_key")` on
  load, and `except → status=FAILED + traceback` inside a `finally` that still writes the receipt. Verified by reading
  the new file, not assumed from the commit message.
* A one-shot future public beacon implements sub-gate `IG-2` as specified.

## The defect

`gmi_k4_grammar_native.py` builds every candidate from a `StateShape` drawn from a fixed list of **22** shapes.
`Candidate.vector()` then returns

```python
"state_scales_with": self.shape.state_scale,
"serve_scales_with": self.shape.serve_scale,
```

— read **directly off the pre-selected shape token**, not derived from the candidate's structure.

Measured against the freeze:

| check | result |
|---|---|
| `SHAPES` count vs `families` count | **22 vs 22** |
| shape `(state, serve)` pairs exactly matching a family's | **22 of 22** |
| families with no matching shape | **none** |
| shapes matching no family | **0** |
| families uniquely determined by `(state_scale, serve_scale)` alone | **22 of 22** |

The shape inventory is an **exact bijection with the answer key**, and those two axes alone identify the family
outright in every single case.

The remaining eight axes *are* genuinely searched — `routing × sharing × retrieval × iterations × stochastic ×
verifier × authority × locality` = **576** combinations per shape. So the engine does real combinatorial work on 8 of
10 axes and is **handed the 2 that uniquely name the family**.

> A `K4_RECOVERY_GREEN` from this engine therefore means: *the search selected the correct item from a 22-item list,
> one of which is the held-out family's answer, and then resolved 8 further axes out of 576.* That is a 1-in-22
> multiple-choice question with a refinement step. It is not neutral rediscovery.

`StateShape("S13", "n_experts_times_expert_size", "active_expert_size", ("specialist",))` is an expert macro with the
name removed. The register's `C4` requires a grammar with "no convolution, attention, recurrent gate, tree learner,
solver, expert, retriever or adapter macro", where "every compound operator expands to charged primitives". A shape
token that *asserts* its own state and serve scaling does not expand to anything.

**This defect is distinct from the one the branch's own audit names and survives the V3 fix.** The V2 audit names the
shared-palette/price-map defect, which V3 genuinely repairs by giving each grammar its own token inventory and cost
algebra. The bijection is a separate problem and V3 inherits it unchanged.

## Disposition

**Merge the branch.** The apparatus is substantial, additive, honestly self-audited, and preserves both enforced
rules. Nothing in it claims `K4_RECOVERY_GREEN` today.

**But the claim ceiling drops further**, to:

```text
K4_MULTIPLE_CHOICE_PHASE_EVIDENCE__STATE_AND_SERVE_AXES_SUPPLIED_BY_THE_CANDIDATE_SPACE__
NEUTRAL_REDISCOVERY_NOT_DEMONSTRATED
```

A full successor must derive `state_scales_with` and `serve_scales_with` **by measuring the candidate program's
actual retained state and per-query work**, exactly as the `B1` layer's `carrier_of` derives a carrier from a typed
graph rather than from a label. Until then no K4 verdict from this engine bears on `K4_LOFO`.

Recorded as gap **DG-10**.

---

## Addendum — the V3 engine's verdict distribution, and why running it was safe

**Development-time observation, seed 17, cell `w2`, all 22 families × 3 grammars = 66 cells.** Explicitly **not**
protected evidence, for the reason given below.

| verdict | count | share |
|---|---|---|
| `THEORY_RED` | **59** | 89.4% |
| `INCONCLUSIVE_GRAMMAR` | 6 | 9.1% |
| `K4_RECOVERY_GREEN` | 1 | 1.5% |

All 59 REDs give the same reason: *"grammar-native frontier property vector contradicts frozen prediction"*. The 6
inconclusives are *"no admissible positive candidate"* — which is also why the branch's three hostile tests fail with
`KeyError`: they hit that early-return path, which omits `winner_candidate_id` and `world_profile`, so those tests
never reach the substance of their assertions. **The leakage and replay guarantees they exist to establish are
therefore currently UNVERIFIED — not verified-and-broken, but unestablished.**

**Why running this did not burn anything.** The protected V3 successor draws its seed from a **future drand beacon**
that has not been acquired — `GMI_K4_PUBLIC_BEACON_V3.json` does not exist, and the successor freeze still reads
`FROZEN_BEFORE_V3_PUBLIC_BEACON_AND_ANY_V3_PROTECTED_RESULT`. The protected seed therefore does not exist yet and
cannot be contaminated by a development observation at seed 17. **This is sub-gate `IG-2` doing precisely the work it
was specified for**, and it is the reason this review could measure the engine at all without spending the protected
evidence — a contrast with V1, which the branch's own audit had to retire for exactly this.

**How the 89.4% should and should not be read.** It is a large apparent negative against GMI's `K4` predictions and it
must not be reported as one yet, for two reasons stated in advance of any protected run:

1. **`DG-10` applies.** The candidate space hands the search the two axes that name the family. A frontier vector that
   contradicts the prediction in 89% of cells means the *cost model* is selecting a different pre-built shape than the
   predicted one — which is a statement about the lifecycle price map at least as much as about GMI.
2. **The obligations may not discriminate.** 6 cells find no admissible candidate at all, which is the same
   "ecology does not discriminate" failure mode `DG-9` found in the `B1` layer. No best-constant or fixed-function
   null (rules 40, 42) has been run against these obligations.

The honest reading today: **the engine is measuring something, and nobody has yet established that what it measures is
GMI's prediction rather than its own price map.** That question is answerable and is the next work.
