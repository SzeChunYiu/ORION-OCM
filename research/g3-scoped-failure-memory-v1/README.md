# G3.2 — scoped failure memory

**Status:** research-only / no production change / no ML / no routing change.

Converts #165's `G3.2` from unmeasured. #193 closed G3.1 and named this as the next
obligation.

## The design decision that is the experiment

`g2-macro-operator-v1` enumerates `product(tokens, repeat=depth)` and **skips over-length
words at no cost**. Discarding an infeasible branch for free is exactly what a failure
memory is supposed to buy, so in that accounting a nogood store can only ever look
worthless. This study uses a **prefix-extending BFS**, where extending a prefix is the
charged unit — what a real search pays, and what a nogood store actually saves.

The population matters just as much. Every task is **unreachable at budget 5 and reachable
at budget 6**. That is the G3.2 distinction made concrete: unreachable-at-a-budget is a
*scoped method failure*, not task impossibility, and the budget change is the regime change
under which a sound memory must reopen.

## Result

```text
FAILURE_MEMORY_NOT_USEFUL          (under the declared prices)
scope_is_load_bearing: TRUE        (independently, by falsifier)
```

| arm | extensions | lookups | maint | bits | solved | sound |
|---|---:|---:|---:|---:|---:|:--:|
| `NO_MEMORY` | 216,777 | 0 | 0 | 0 | 24/48 | ✓ |
| `NOGOOD` (unscoped) | **69,568** | 262,080 | 4,096 | 65,536 | **0/48** | ✗ |
| `SCOPED_NOGOOD` | 122,569 | 216,777 | 4,096 | 0 | 24/48 | ✓ |

Pareto: **`INCOMPARABLE_WITHOUT_A_PRICE`**. Coordinates are not summed — bits are not
extensions, and adding them is the post-hoc scalarization #165 forbids.

### Two independent findings, both retained

**1. Scope is load-bearing, and it is shown by a falsifier rather than asserted.** The
unscoped store cuts extensions by 68% and then solves **0 of 48** — it is not merely worse,
it is *unsound*. It carries budget-5 nogoods across the regime change, blocks the length-6
solutions, and loses every task. The scoped store reopens and solves exactly what the
memoryless arm solves. That is the difference between "this method failed here" and "this
task is impossible", demonstrated.

Note the storage column: the scoped store ends at **0 bits** precisely *because* it
correctly discarded stale nogoods, while the unscoped store holds 65,536 bits of entries
that are actively harmful.

**2. The memory does not pay at this ecology.** It trades **94,208 extensions saved** for
**216,777 extra lookups** — one store probe per candidate against a 43% extension saving.

```text
break-even lookup price   0.416
```

Scoped failure memory pays **iff one store probe costs less than 0.416 of one prefix
extension**. That is a number a real system can check against its own data structure before
adopting a nogood store — more useful than a verdict at one arbitrary price. No storage
price rescues it; storage is not the deciding coordinate.

**The negative does not say scope is unnecessary.** Both findings are independent and both
are retained; a test asserts the terminal reason says so.

## Two errors this study made first

Recorded because a study that only reports its final state hides how it got there.

1. **A vacuous negative.** The first population used reachable tasks at a generous budget.
   BFS returns as soon as it finds a solution, so it never reached the bound, recorded
   **zero** nogoods, and returned `FAILURE_MEMORY_NOT_USEFUL` from a run in which no failure
   had occurred. There is now a `CANNOT_CHECK_NO_FAILURE_WAS_EVER_RECORDED` terminal so such
   a run cannot be reported as a negative result, and a test that fires it.
2. **The wrong soundness definition.** "Every row solved" called the *correct* arm defective,
   because at budget 5 every task is genuinely unreachable. Soundness is now defined against
   the memoryless arm: an arm is sound iff it solves exactly what searching without memory
   solves.

## Boundary

Same-domain polynomial ecology, one grammar, two budgets, 24 tasks over 48 task-budget rows. `NOGOOD` is the classic
TMS/CEGAR parent and it is the arm that wins on gross search — this study does not claim a
new mechanism, it prices one and tests whether *scope* earns its place. CBR and full TMS
justification maintenance are not implemented and are not claimed as parents here.
