# Resolution matrix and assimilation decisions

Scope: the four bound blobs at `c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`.
Historical finding IDs refer to the earlier 9087971d source review.

| Finding | Successor status | Remaining boundary |
|---|---|---|
| T1: same-h cognition lacks termination selection | Resolved for Theorem 9 / finite_meta_dp | At most k actions, mandatory stop; no proof of unbounded SSP or the old same-h recurrence. |
| T2: approximate “exact” action/regret claims | Partly improved, unresolved | Direct argmin equality and correct whole-fiber theorem; F2/F3 remain and old selector is unchanged. |
| T3: common-safe action implies economic stop | Explicitly corrected in Theorem 2 and test 81–94 | Older README remains textually unchanged; align the public entry point. |

The V2 opening supersedes only the earlier loose quotient wording in tied-action
settings. It does not explicitly retire all older stopping recurrences or README
rules. The comparison metadata shows the original reviewed source files untouched;
their historical findings therefore persist textually. Later, unreviewed additions
may supply further qualifications; this receipt does not decide their sufficiency.

## Adopt now as established mathematical structure

1. **Decision regions:** whole-fiber common actions avoid both nontransitivity and
   pairwise-overlap traps. Safety feasibility and economic stopping are distinct.
2. **Finite metareasoning:** use the k-indexed recurrence with mandatory stopping.
   Zero-cost loops remain bounded. Charge policy construction, storage, evaluation,
   update and replay as Theorem 9's accounting paragraph requires.
3. **Exact lifecycle abstraction:** equal immediate contracts plus equal successor
   block laws is the appropriate finite parent; its implementation needs F2 fixed.
   A scalar objective must be separately registered when contracts also contain
   outputs, authority fields or multiple resource coordinates.
4. **Bayes feature comparison:** Theorem 4 compares a frozen observation map with
   full state under one fixed distribution, action set and cost model. It proves
   neither minimax adequacy nor out-of-distribution sufficiency. If protected
   legality varies by state, constrain each feature policy to actions legal
   throughout its possible-state fiber; the current cost-only API does not do so.

## Keep these reductions conditional

**Properness:** the finite proof needs no unbounded stopping theorem. Removing k
reopens T1. Previously read Hay assumptions (bounded utilities and fixed positive
computation cost) are stronger than merely nonnegative costs; Bertsekas properness
requires both finite expected termination and finite cost, with the selected
value/uniqueness theorem's additional hypotheses. Do not silently transfer either
result to unrestricted zero-cost cognitive loops.

**Investment:** Theorem 15 openly assumes fixed demand law, additive forward
setup increments, no frontier change while answering, and iid demand conditional
on lifetime. Preserve predictable investment before the current demand is seen.
Its `b_f+H*r_f` benchmark is the expected-slope, fixed-duration offline comparator.
It is not the offline oracle that sees and adapts to every realized future target.
Ordered nondominated slopes alone do not transfer every continuous-time multislope
competitive ratio to a discrete-demand implementation. Specify the chosen parent,
its admissible schedules, time convention, initialization, and comparator first.
The earlier Lotker §2–3 read supports those boundaries; this review does not certify
any newer fixed-frontier, unknown-lifetime or Pareto-frontier implementation.

**Mechanical learning:** adopt ordinary finite/explicit selection if a payable
residual survives. [Literature 300–304](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/LITERATURE_SYNTHESIS_V1.md#L300)
calls an MLP an implementation candidate; under the operator's OCM constraint,
any neural selector belongs only in an external comparator arm. Correct that
future-facing sentence before assimilation into the OCM engineering plan.

**Negative outcomes:** the formal note's line 750 is suitable for closing one
registered test, not terminating the learning programme. Use a concrete failure
attribution and separately registered revival, with no tuning to protected outcomes.
