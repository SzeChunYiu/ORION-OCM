# Capability interaction laws — tranche 1

Scope: finite exact microscopes for the first four F3 rows of issue #602. Evidence classes are P1 (formal) and P2 (finite-exact controls). Claim ceiling is **G2**. Nothing here is a G6 morphology-to-capability predictor.

## 1. Memory × planning

Let there be `N` cue classes, observed once before a deterministic plan tree. The final correct terminal action depends injectively on the cue. Between cue and terminal decision the agent has no external memory, only a retained state in a set `M` with `|M| = K`. Let the relevant terminal discriminator occur `H` steps beyond the planning cut, while the planner's declared lookahead is `D`.

**Theorem MP.** Exact success is possible iff `K >= N` and `D >= H`.

*Necessity.* If `K < N`, pigeonhole forces two cue classes into one retained state. Since their required final actions differ, one decoder state cannot be correct for both. If `D < H`, the discriminator is outside the planner's declared reachable horizon, so an exact plan depending on it is outside scope.

*Sufficiency.* With `K >= N`, injectively encode each cue class. With `D >= H`, the planner reaches the terminal discriminator and decodes the remembered cue into its required branch.

The interaction is therefore conjunctive: more planning depth cannot repair a memory collision, and more memory cannot expose a discriminator outside the allowed planning horizon. The minimal negative twin makes the terminal action cue-independent; then the memory condition vanishes.

## 2. Memory × abstraction

Let raw items be `X`. An abstraction `q : X -> C` is **obligation-preserving** when all raw items mapped to one class have identical future obligations. Let the quotient contain `|C|` represented classes.

**Theorem MA.** For an obligation-preserving quotient, the exact retained-state lower and upper bounds coincide at the number of task-distinct quotient classes. If a proposed coarsening merges two obligation-distinct items, it is not a cheaper exact representation; exact success becomes impossible.

*Necessity.* Distinct future obligations must induce distinct retained states, otherwise a shared decoder would be required to emit two incompatible futures.

*Sufficiency.* Retain only the quotient-class identity and decode the common future obligation for that class.

Thus abstraction and memory interact through the quotient index: valid abstraction reduces the number of distinctions memory must preserve, but invalid abstraction destroys solvability rather than buying a free compression gain.

## 3. Search × learned heuristic

For one exact search obligation let plain verified search cost `B0` per query. A learned heuristic changes the verified search cost to `B1 <= B0`, costs `L` once to acquire and retain, and is reused `r` times. All costs are measured in one prospectively frozen additive unit and correctness/verifier power are unchanged.

**Theorem SH.** The retained heuristic is cheaper iff

`r (B0 - B1) > L`.

It ties at equality and loses below it.

*Proof.* Plain search costs `r B0`; heuristic-guided search costs `L + r B1`. Subtraction gives `r(B0-B1)-L`.

The negative twin sets `B1 = B0` with `L > 0`; the heuristic then strictly loses for every reuse count. This is deliberately not a claim that a learned heuristic is always useful: its value is exactly the verified search burden it removes under the frozen accounting.

## 4. Social modeling × communication

Let partner type be compressed into at most `S` social-model states and the received channel contain at most `K` message symbols. The receiver has no other side information. Suppose the correct action may differ across obligation-distinct `(partner type, message)` pairs.

**Theorem SC.** The receiver can condition on at most `S K` social-state/message cells. If the task requires more than `S K` pairwise obligation-distinct cells, exact success is impossible. The bound is tight when the social encoder and message channel preserve all required distinctions and the decoder assigns the correct action to each represented cell.

*Necessity.* The receiver's total observable decision state is a Cartesian product of at most `S` social states and `K` messages, hence has cardinality at most `SK`; pigeonhole applies beyond that count.

*Sufficiency.* For any task with at most `SK` required cells, assign each required distinction injectively to a product cell and decode it to the corresponding action.

The negative twin removes type dependence from the required action; then the social-model factor drops out. Shared side information is a load-bearing exclusion: if present, it can refine the receiver state without consuming either declared factor.

## Parent subtraction

These are not novelty claims. MP is a direct composition of finite-state distinguishability and bounded-horizon planning. MA is quotient/sufficient-statistic compression. SH is amortization applied to verified search reduction. SC is a finite communication/distinguishability product bound. The GMI contribution at this tranche is to register them under one architecture-independent capability contract with explicit negative twins, falsifiers, and exact executable controls.
