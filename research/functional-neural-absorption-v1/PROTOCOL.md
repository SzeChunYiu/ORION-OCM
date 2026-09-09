# FNA-1 protocol — frozen before execution

**Issue #214, work package FNA-1. Base `dff3acadb78dfef161d122d00f20ebb30ab8bb51`.**
**Evidence class E1 / L1.** One planted world, one population, one author. Not E3.

## Why this is not the FNA-1 #214 originally described

#214 proposes a ladder R0–R7 and gives non-neural mechanisms first refusal against
attention. Phase A found R0, R1, R2 and R4 **already implemented on main**, exact, with a
17-coordinate resource vector that charges index build separately from query work.
Rebuilding them would compare against a strawman — the hand-authored-prior risk §6 names.

Phase B found that §3's table **mis-attributes** the typed-channel idea. The literature
reads multi-head as an ensemble of kernel estimators whose function is **variance reduction
through decorrelation** (2605.20271), with many heads inactive (2504.03889). An exact
closure has **no estimator variance**, so that function has no obligation to discharge here.
Typed channels belong to heterogeneous information networks and metapath retrieval
(2605.30966, 2510.15552).

So FNA-1 tests the **typed-channel** mechanism against its **real** parent, on main's own
closure, and does not implement or claim anything about attention.

## Questions, frozen

- **Q1 (unbounded).** Can channel-restricted retrieval reach task-decisive state the
  undifferentiated exact closure misses?
- **Q2 (bounded).** Under a truncation budget, does channel order change what is found, and
  can a **non-oracle** ordering policy recover a decisive item a naive order misses?

## Registered prediction, before execution

**Q1 will be negative and structurally so.** Proposition 3 (stated in `experiment.py`
before any run): `gated_closure` admits a head only via an edge whose tails are reached and
whose warrant is live, so removing edges can only remove admissions. Every channel subset is
therefore a subset of the full closure, for *any* channel policy. Reach cannot be won.

**Q2 is where the mechanism can earn something**, because a binding budget makes expansion
order decide what fits.

## Arms

Unbounded, all on production code: `R0_DENSE`, `R1_INDEXED` (+ real work counters),
`R5_CHANNEL_<t>` per channel, `R5_COMMON_CHANNELS_ONLY`, `R5_UNION_ALL_CHANNELS`.

Bounded, at budgets 4/8/16/32/64/128: `BOUNDED_NAIVE`, `BOUNDED_RARITY_FIRST`,
`ORACLE_DECISIVE_CHANNEL_FIRST`.

**`BOUNDED_RARITY_FIRST` is the only candidate policy.** It orders channels by edge-type
count — a property of the space, **not of the task or its answer** — and is the same
selectivity heuristic `runtime/operator_index.py` applies to operator inputs. Any positive
is therefore owned by the classical IR parent.

**The ORACLE arm is an upper bound, labelled ORACLE in code and output, and is never
reported as a result.**

## Planted world

Seed; `n=60` distractors fanned out on the common channels `SUPPORT`/`DEPENDENCE` plus
second-hop chains that consume budget; **one decisive atom on the rare channel
`SCALE_CHANGE`** (1 edge against 100). This is §4's "one rare decisive item" with
"misleading similar items". It is adversarial to a naive expansion order, **not** to the
parent mechanism.

## Mandatory harness validation

The bounded closure is research-side code mirroring `gated_closure`. At an unbinding budget
it **must** reproduce the production closure exactly. If it does not, the run returns
`CANNOT_CHECK_BOUNDED_HARNESS_DISAGREES_WITH_PRODUCTION_CLOSURE` and no bounded number is
interpretable. If any channel arm exceeds the full closure, Proposition 3 is violated,
which is impossible, so the run returns
`CANNOT_CHECK_PROPOSITION_3_VIOLATED_HARNESS_DEFECT`.

## Stop rule and terminals

Registered #214 §7 terminals only. No result licenses `TRANSFORMER_REPLACED`,
`LLM_EQUIVALENT`, `AGI` or `GENERAL_SUPERIORITY`. The allocation and budgets are not to be
revised to rescue an exposed result.

## Declared limitations, before seeing outcomes

No neural arm is run; R3/R6/R7 remain absent, so `APPROXIMATE_RETRIEVAL_NOT_SAFE` stays
untestable. No lifetime economics: acquisition, maintenance and revocation costs are not
amortised. A decisive item on a **common** channel would reverse the rarity policy's
advantage; that hostile is named here and is **not** run in this tranche.
