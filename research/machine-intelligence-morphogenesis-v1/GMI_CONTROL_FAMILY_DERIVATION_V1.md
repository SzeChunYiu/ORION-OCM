# Control: policy, value, model and option as one holding decision (B18)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/control_family_witness.py`.
Receipt: `microscopes/results/STAGE_CONTROL_FAMILY_V1.json`.
Derived by a parallel worker. Witness and receipt md5 **independently
reproduced** on `laptop-billy` before this document was written; 71 assertions;
exit 0, `all assertions held`.

## Policy memory is the quotient, and it is coarser than belief

Enumerated over machines, not argued:

| world | optimal | machines seen | minimal `m` | attain it |
|---|---:|---:|---:|---:|
| cue **hidden** at the junction | 2 | 65 552 | **2** | 4 096 |
| cue **visible** at the junction | 2 | 32 | **1** | 8 |

Belief classes on the same world: **3**. Memory classes needed to *act*: **2**.

> The pre-cue history — belief `(1/2, 1/2)` — merges with a post-cue class. A
> controller needs the quotient that its **actions** induce, which is coarser
> than the one its **beliefs** induce. Carrying the belief partition would be
> carrying a distinction nothing acts on.

## Value is retained state, and myopia is not a bug

Same graph, same reward multiset, only the order permuted:

| world | `V(0..4)` | optimal | myopic | regret |
|---|---|---:|---:|---:|
| big exit **late** | 9,10,11,12,10 | 9 | **0** | **9** |
| big exit **first** | 12,7,8,9,10 | 12 | **12** | **0** |

A myopic controller is exactly right in one and maximally wrong in the other,
with nothing changed but the arrangement.

## A reward signal is not always sufficient

| task | count vector | state-only | state + step |
|---|---|---:|---:|
| do `a` then `b` | (1,1) | **0 / 75** | 27 / 243 |
| do `a` twice | (2,0) | 30 / 75 | 27 / 243 |

> **No additive reward on state alone induces "do `a` then `b`"** — the two
> tasks have equal count vectors, so any state-additive reward scores them
> identically. The impossibility is a proof; the grid only confirms it. Adding
> the step index repairs it, and that repair is existential.

## The trichotomy is one crossover, twice

| `r` | plan always | compile all | cache | cheapest |
|---:|---:|---:|---:|---|
| 1 | **6** | 176 | 7 | plan |
| 25 | **150** | 200 | 175 | plan |
| **31** | 186 | 206 | **181** | **cache** |
| 200 | 1200 | 375 | **350** | cache |

Planning gives way to caching at **r = 31**, and to the whole compiled table
only at **r = 36**. **Compile-all never wins.**

Model-based against model-free flips at `r = 5` with one goal and `r = 17` with
64 or 256 — a model amortises across *goals*, so more goals move the flip
later, not sooner. Policy against value table crosses at 18 evaluation queries.

## Coverage, and when an experience batch pays

| batch | covers π | estimate | error |
|---|---|---|---:|
| covering | yes | 7/2 | **0** |
| one pair missing | **no** | 3/2 | **2** |
| missing pair added | yes | 7/2 | 0 |

Off-policy reuse is PVR-3 with the batch as retained state: at `W=1, C=2, U=2`
it **never** pays; at `W≥2` it pays from `r = 4` and then `r = 2`.

## Exploration, over 32 768 enumerated machines

Minimum total regret **2**, attained by **512** machines; the best
constant-arm machine scores **8**. Those 512 minimizers show only **2** distinct
behaviours on worlds whose arms differ, and 8 on the tied ones — so the
enumeration is not rewarding arbitrary variety.

**The twin is the control**: announce the payoffs and minimum regret drops to
**0**, while a machine that still pulls both arms where they *differ* scores 2.

> Exploration is not a virtue of the machine. It is the price of not being told,
> and it goes to zero exactly when the telling happens.

## Options pay by recurrence, not by structure

| task set | option | occurrences | flat | hierarchical | margin |
|---|---|---:|---:|---:|---:|
| recurring | XYZ | 4 | 22 | **17** | **+5** |
| no recurrence | AB | 1 | **22** | 23 | **−1** |

Break-even at 2 uses. Same machinery, opposite verdict, decided by recurrence.

## Neutral recovery: three shapes, none of them named

A candidate is `m` memory classes, a class-update table, an action table, and a
**subset of its own keys it holds as rows**; unheld keys are recomputed per
visit. Nothing names a policy, value, model, plan or option.

| `r` | keys held | reads as |
|---:|---|---|
| 1 | **0/6** | **a planner** |
| 2–3 | **2/6** | **partial compilation** |
| 5+ | **6/6** | **a compiled policy** |

> A controller is not chosen from a menu of families. Hold a decision when
> PVR-3 says its own visit count earns the row, and recompute it otherwise.

**The intermediate regime appears at every row price tested and never in the
matched twin** where corridor observations are distinct and every key is visited
exactly once. Partial holding is not a tuning artefact — it is what *uneven
visitation* buys.

This fills the gap `GMI_SEARCH_FRONTIER_DERIVATION_V1.md` explicitly left open:
it listed partial compilation as legal in the ledger and did not evaluate it.

## Scope, as the witness states it

- §3's impossibility is a proof; the grid confirms it, and the repair is
  existential rather than general.
- §4 charges a planning query at exhaustive depth-2 expansion and a row at 1.
  Other prices move the crossovers; **the shape, and caching's dominance over
  whole-table compilation, do not**.
- §5's off-policy estimator substitutes 0 off support. Another default changes
  the size of the error, not its existence.
- §6 has deterministic payoffs, so one pull identifies an arm exactly. Noisy
  payoffs would add a statistical term this exact method cannot carry.
- §7 prices one option; nested and overlapping options are legal and unsearched.
- **§8 conditions its subset enumeration on machines that are already optimal,
  so it prices *what to hold*, not *what to do*.**

**Falsifier.** Exhibit a control world where holding every decision beats
holding the frequently-visited ones at every reuse count under uneven
visitation; or a task that is not a function of state visitation counts and is
still the unique optimum of some additive reward on that state.
