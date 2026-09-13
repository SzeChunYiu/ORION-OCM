# Controlled acquisition information-state theorem V1

Status: **FINITE DETERMINISTIC ROBUST THEOREM; POMDP / ACTIVE-EXPERIMENT PARENT ACKNOWLEDGED**  
Date: 2026-09-13  
Base: `main@f66219161315d42ea919d8de1ef75a7e304bb0b1`

This closes Q1 of the recursive scientific queue at a finite deterministic, zero-error/robust scope. It corrects any acquisition recurrence that tracks only a candidate-world set when experiments can change physical state, consume capabilities, or alter which experiments/actions remain legal.

## 1. Controlled acquisition problem

Let:

- `W` be a finite static latent-world set;
- `S` a finite physical/control state set;
- `T` a finite experiment/control set;
- `O` a finite observation set;
- `L_t(w,s)` say whether experiment `t` is legal at pair `(w,s)`;
- `O_t(w,s)` be the deterministic observation when legal;
- `F_t(w,s)` be the next physical state;
- `A_Omega(w,s)` be the nonempty set of terminal actions that satisfy the declared obligation at `(w,s)`;
- `c(t)>=0` be a scalar experiment cost.

The world is not required to change, but the physical state may. A history contains chosen experiments and returned observations. Define the exact controlled information state

`I(h) subset W x S`

as the set of all current `(w,s)` pairs reachable from an admitted initial pair and consistent with the complete action/observation history.

Register a nonempty initial pair set and retain only nonempty compatible
successor sets. Beliefs in this theorem are therefore nonempty.

A terminal action is robustly adequate exactly when

`A(I) = intersection_{(w,s) in I} A_Omega(w,s)`

is nonempty.

This is deliberately weaker than full world identification.

## 2. CA-1 — pair-state sufficiency theorem

Assume future experiment legality, transition, observation, experiment cost and terminal-success relation depend on history only through the current hidden pair `(w,s)` and the chosen experiment/action. Then two histories inducing the same controlled information state `I` have the same set of feasible future experiment trees and the same robust terminal possibilities.

Therefore `I(h)` is a sufficient information state for finite-horizon robust acquisition.

**Proof.** For any chosen legal experiment `t`, every possible next observation and next pair is determined pairwise by `O_t,F_t`. Hence the successor information state

`I_{t,o} = {(w,F_t(w,s)) : (w,s) in I, L_t(w,s), O_t(w,s)=o}`

depends only on `I,t,o`. The robust legality condition likewise depends only on whether `L_t` holds for every pair in `I`; terminal adequacy depends only on `A(I)`. Induction on remaining horizon gives equality of all future feasible policy trees and values. QED.

## 3. CA-2 — exact robust Bellman recursion

For remaining experiment horizon `H`, let `V_H(I)` be minimum worst-case future experiment cost. Define

`V_H(I)=0` if `A(I)` is nonempty,

`V_0(I)=+infinity` otherwise, and for `H>0`

`V_H(I) = min_t [ c(t) + max_{o:I_{t,o} nonempty} V_{H-1}(I_{t,o}) ]`,

where the minimum ranges only over experiments legal for **every** pair in `I`.

Under CA-1's hypotheses this recursion equals optimization over arbitrary history-dependent experiment policies.

The committed checker compares this recursion with a separate explicit history-tree recursion for all `5^8 = 390,625` two-world/two-state/two-test kernels at horizon two. Each `(test,world,state)` entry is either illegal or one of four `(observation,next-state)` outcomes. The obligation is exact world action. There are zero mismatches.

## 4. CA-3 — world-support-only recursion is unsound

Take worlds `{0,1}` and states `{fresh,burned}`. An informative experiment is legal only in `fresh` and reveals the world in one step. A destructive experiment emits no information and moves either world to `burned`. No informative experiment is legal in `burned`.

Before destruction:

`I_fresh={(0,fresh),(1,fresh)}` and `V(I_fresh)=1`.

After destruction:

`I_burned={(0,burned),(1,burned)}` and `V(I_burned)=+infinity`.

Yet both project to the identical candidate-world set `{0,1}`.

Therefore no recurrence whose entire state is only the surviving world set can be sound for general state-changing acquisition.

Terminal: `WORLD_SUPPORT_ALONE_INSUFFICIENT_FOR_CONTROLLED_ACQUISITION`.

## 5. CA-4 — information can be replaced by control

State-changing acquisition is not merely passive sensing.

Construct a two-world problem in state `s0` where world 0 accepts only action `a0` and world 1 only `a1`. An uninformative legal transformation maps both hidden pairs to state `s1`, where both worlds accept common action `a*`.

The world support remains `{0,1}` before and after the transformation. No uncertainty was removed. Nevertheless the obligation changes from incompatible to compatible and the exact acquisition/control value is one step.

Thus a Grand-GMI acquisition law must allow two ways to reduce semantic difficulty:

1. **epistemic:** observations separate hidden possibilities;
2. **interventional:** control transforms the possibilities into a region with a common adequate action.

This is the controlled analogue of task-directed stopping and makes explicit why information gathering and control cannot be globally separated.

## 6. CA-5 — path-dependent resources must be state variables

If future legality or the claim itself depends on a remaining budget, accumulated damage, time, workspace, energy reserve, query quota or another path-dependent resource, `I` alone is insufficient unless that variable is already part of `S`.

The smallest witness uses one informative cost-1 experiment. The identical pair set is solvable with remaining budget 1 and infeasible with remaining budget 0. Hence the sufficient controlled state is more generally

`J(h) = (I(h), r(h))`

for every charged/path-dependent resource coordinate `r` that affects future feasibility or value.

This identifies which charged resource variables must enter the state. It does
not itself optimize controller storage, transient workspace or implementation
cost: Q2 remains open. The CA-5 checker now executes both pair and history recursions at the
remaining unit-cost horizons; it does not synthesize a physical controller.

## 7. Relation to Grand GMI

The previous noninvasive acquisition recurrence is the special case with fixed `s`, history-independent test legality and no path resource omitted from state.

The correction makes acquisition a proper controlled causal process and aligns it with the master tuple's process theory, obligation and resource coordinates. The same state principle also applies to destructive measurements, active diagnosis, test-time interventions, experiment design and self-modification.

The complementary [CRA-1--3](CONTROLLED_RELATIONAL_ACQUISITION_THEOREM_V1.md)
uses complete configurations, including the pair above when appropriate. It
adds empty terminal relations for irrecoverable states, least-fixed-point
synthesis of all finite terminating policies, rank bounds and protective
control. Both use the same established strong-planning parent; their finite
censuses are different checks of related formulations.

## 8. Stochastic boundary

This theorem is finite deterministic and robust/zero-error. Under stochastic transitions or observations, a support set is generally insufficient for expected-risk optimization. The classical parent is the POMDP belief-state construction: a belief distribution is a sufficient statistic for history under the Markov model. Prior-free Grand GMI with multiple admitted stochastic ecologies may require a common-decoder family/set of controlled beliefs or another sufficient statistical object. That broader stochastic statement is not claimed here.

## 9. Parent subtraction / novelty boundary

This is **not** claimed as invention of belief-state planning or stateful experimental design.

Parents include:

- POMDP theory: belief states are sufficient statistics for action-observation histories in controlled partially observed Markov processes;
- controlled sensing / active sensing;
- Equivalence Class Determination and Decision Region Determination: acquisition may terminate once the remaining hypotheses imply the same decision region rather than identifying the full hypothesis.

The GMI contribution at this layer is the precise repair of its own task-directed acquisition object: set-valued obligation compatibility, state-changing interventions, robust common legality, charged path resources, and integration with the semantic-cut / morphology theory. Under the novelty ledger this is parent-assisted synthesis, not a priority claim.

## 10. Executable evidence

`grand_gmi_controlled_acquisition_checks_v1.py` exhaustively compares CA-2 to explicit history policies and pins the CA-3/CA-4/CA-5 counterexamples. `GRAND_GMI_CONTROLLED_ACQUISITION_RECEIPT_V2.json` records the exact integrated
output, including the replay terminal field. Upstream PR #539 recaptured its
V1 file in place. The original pre-terminal V1 bytes are preserved separately in
`replay_receipts_v1/GRAND_GMI_CONTROLLED_ACQUISITION_PRE_CAPSULE_V1.json`;
the inventory identifies both histories. CA-5 values are now computed from
policies instead of supplied in a constant table.
