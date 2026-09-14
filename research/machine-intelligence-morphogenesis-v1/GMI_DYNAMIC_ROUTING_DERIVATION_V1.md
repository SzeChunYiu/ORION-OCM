# Dynamic routing, derived in the ecology item 5 asked for (B7)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/dynamic_routing_witness.py`.
Receipt: `microscopes/results/STAGE_DYNAMIC_ROUTING_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

The corpus records attention as an open gap and says exactly why.
`GMI_NEUTRAL_EMERGENCE_SELECTION_V1.md`: item 5 predicts attention from
*"limited computation plus excessive possible information"*, and the registered
ecologies present sixteen inputs over sixteen events — so there is no
information overload, the antecedent is not satisfied, and the absence of
attention is *predicted by the item* rather than counting against it. It closes:
**"Testing item 5 requires an ecology where the input space exceeds the compute
budget, which the construction does not provide."**

This supplies that ecology.

## The conjunction, and both ways of breaking it

Six places, three values each — 729 configurations. A machine with a read budget
below 6 cannot see the whole input.

| obligation | budget | fixed reads suffice | dynamic reads suffice |
|---|---:|---|---|
| content-dependent | **2** | **NONE** | **yes** |
| content-dependent | 6 | `[0,1,2,3]` | yes |
| content-independent | 2 | `[3]` | — |

> **Dynamic routing is forced by a conjunction.** Lift the budget and it is
> unnecessary; make the target's place fixed and it is unnecessary. Item 5's
> antecedent has two halves and needs both.

Each twin is a separate assertion, so losing either one aborts the run.

## Where the boundary sits

| budget | 1 | **2** | **3** | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| fixed suffices | no | **no** | **no** | `[0,1,2,3]` | yes | yes |
| dynamic suffices | no | **yes** | **yes** | yes | yes | yes |

Dynamic routing answers at a budget of **2**. No fixed policy answers below **4**.

> Between those two numbers is the regime where routing is **not an
> optimisation but the only machine that works at all** — bought with reads, and
> worth buying exactly where the budget is too small for a fixed policy and
> large enough to follow a pointer.

## Position must be distinguishable, or a pointer means nothing

Strip position — let the machine see the **multiset** of values it read rather
than which place each came from, everything else unchanged:

| | with position | without position |
|---|---|---|
| content-dependent solvable | **yes** | **no** |

> A pointer is only a pointer if places can be told apart. **Dynamic routing
> presupposes positional distinction; it does not supply it.**

The witness asserts both halves — if an unordered bag sufficed, the obligation
would not be order-sensitive and the section would be vacuous.

## Neutral recovery

A candidate has exactly two fields: how many places it may read, and whether the
**second read may depend on the first**. No `ATTENTION`, `QKV`, `SOFTMAX`,
`TRANSFORMER`, head, query or key appears in the candidate space.

| obligation | budget | cheapest shape | reads as |
|---|---:|---|---|
| content-dependent | 2 | read 1, then 1 chosen by it | **a content-routed reader** |
| content-dependent | 6 | read 1, then 1 chosen by it | a content-routed reader |
| content-independent | 2 | read 1 fixed place | **a fixed reader** |

A second read whose address comes from the first *is* a routing machine, and it
was selected by cost from a two-field description that never names one.

## The negative ecology

Content-independent target, tight budget — both machines work, so the question
is price:

| machine | reads | cost |
|---|---|---:|
| fixed reader | `[3]` | **1** |
| content-routed reader | 1, then 1 chosen | **3** |

> Where which place matters is fixed, a content-routed reader **pays for a
> choice it never uses**. Routing is not a better way to read; it is the price
> of not knowing in advance where to look.

## Scope

- Six places, three values, one pointer at place 0 naming one target. Sparse
  versus full attention over *many* simultaneous targets is not modelled — this
  derives the condition for routing at all, not the sparsity pattern within it.
- The dynamic machine is two reads: pointer, then pointee. Multi-hop routing and
  multiple parallel heads are legal in this ledger and are not evaluated, so
  **B7's sparse/local regime and phase-boundary boxes are not claimed here**.
- Cost charges one unit per read plus one for the choosing. The *orderings* are
  the result; the constant moves the negative ecology's margin, not its sign.
- *A first version enumerated fixed read sets of size exactly `budget` rather
  than up to it, reporting a six-place read where one place sufficed. That
  inflated every fixed reader's cost. Caught by reading the output rather than
  by an assertion — the assertions all passed.*

**Falsifier.** Exhibit a fixed read policy answering the content-dependent
obligation at budget 2 or 3; or an unordered-bag machine answering it at all; or
a content-independent ecology where a content-routed reader is cheaper.
