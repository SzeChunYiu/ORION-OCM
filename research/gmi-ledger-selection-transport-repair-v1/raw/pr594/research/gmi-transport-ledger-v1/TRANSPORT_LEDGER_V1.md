# Transport ledger: what survives scale-up and what does not

Status: **SPLIT RESULT, BOTH HALVES NOW EXACT: LOWER BOUNDS TRANSPORT UNCONDITIONALLY; ORDERINGS TRANSPORT IFF A TWO-SIDED CERTIFICATE EXISTS**
Date: 2026-09-13

Ledger item 9 asks whether the exact finite laws survive at realistic scale.
Asked that way the question has no single answer, because the two halves of a
capability claim behave differently. This unit separates them.

## 1. TL-1 — lower-bound transport is an order argument, and scale is irrelevant to it

`CLB-1` requires exactly two premises: an allocation `q_M` in the relaxed set
`F`, and sound accounting `a(q_M) <= c(M)`. Then

    L = inf_F a  <=  a(q_M)  <=  c(M).

The theorem states that this "needs neither finite cardinality, compactness,
measurability nor computability". The executable model confirms the consequence
that matters for scaling: the transported bound is unchanged across allocation
sets of size 1, 2, 5, 50, 500 and 5000, and is identical for a two-element set
and a two-hundred-element set containing it. **Size is never consulted.**

So a lower bound proved on a small exact model is not invalidated by scale. It
was never a statement about scale.

## 2. TL-2 — both premises are load-bearing

- Unsound accounting (`a(q_M) > c(M)`) returns `UNSOUND_ACCOUNTING` and
  establishes no bound.
- Absent membership returns `NO_MEMBERSHIP`.
- A declared membership contradicted by the set raises rather than defaulting.
- Inexact (float) values are refused; all arithmetic is exact rational.

Under-accounting is the sound direction (CLB-4); over-accounting is not.

## 3. TL-3 — orderings and exclusions do not transport

This is the half that fails, and it is the honest answer to "do the laws
survive at scale".

A transported lower bound `L` constrains every machine from below and therefore
orders none of them. Two machines both strictly above `L` can appear in either
order with `L` unchanged. `CLB-1` says the same in words: a family-relative
bound is not an unconditional global exclusion, and "competitive exclusion also
needs an actual retained comparator at the same task, valuation and joint
feasibility scope".

Consequently a competitive claim measured at small scale — *this family beats
that one* — carries no force at a larger scale without a comparator retained
**at that scale**. Only the one-sided bound travels.

## 4. TL-6 — exclusions transport under a two-sided certificate

TL-3 is a statement about *one-sided* evidence, not an impossibility. The
registered `DCR` separation rule already supplies the positive condition and is
reused here verbatim: a comparison is certified iff the candidate's upper bound
is finite and strictly below the comparator's lower bound.

    candidate = [a_lo, a_hi],  comparator = [b_lo, b_hi]
    CERTIFIED_STRICTLY_LOWER  iff  a_hi is finite and a_hi < b_lo
    UNVERIFIABLE              otherwise

Because the criterion is an order comparison it is scale-free in the same sense
as TL-1: the same certificate holds after multiplying the whole problem by 1,
10, 1,000 or 10^6. So a competitive exclusion **does** transport, provided a
finite upper bound on the candidate is retained.

TL-3 is exactly the degenerate case of this rule with `a_hi = None`: holding
only lower bounds, no pair of machines is ever ordered. Overlapping intervals
and touching intervals (`a_hi = b_lo`) return `UNVERIFIABLE` rather than false,
and malformed or inexact intervals are refused.

The practical reading: measuring a lower bound at small scale buys nothing for
exclusion. Retaining a finite upper bound on the candidate buys everything, and
is what a comparator "at that scale" actually supplies.

## 5. TL-7 — the certificate is necessary as well as sufficient

TL-6 gives a sufficient condition. The characterisation is exact, and both
directions are proved:

    A certified strictly cheaper  <=>  a_hi is finite and a_hi < b_lo

**Sufficiency** is the order chain. **Necessity** is constructive: whenever
`a_hi` is absent or `a_hi >= b_lo`, explicit completions realise the opposite
order or a tie. For `A=[1,4]`, `B=[3,9]` the witnesses are `a=1,b=9` and
`a=4,b=3`; at the boundary `a_hi = b_lo` the witness is the tie `a=b=3`. An
exhaustive check over a rational grid of interval pairs finds **zero**
disagreements between the rule and "every completion has `a < b`".

So the two-sided certificate is not a convenience. It is exactly the
information content required, and no rule on one-sided data can do better.

### The mirror certificate, which TL-6 omitted

TL-6 tested only the candidate direction. The symmetric certificate is equally
valid: `b_hi < a_lo` certifies the **comparator** strictly cheaper. `compare`
implements both and returns one of `CERTIFIED_STRICTLY_LOWER`,
`CERTIFIED_STRICTLY_HIGHER` or `UNVERIFIABLE`. On `A=[10,∞)`, `B=[1,4]` the
mirror certificate applies while TL-6 alone reported `UNVERIFIABLE`. That was a
gap in TL-6, and it is recorded rather than silently corrected.

## 6. TL-4 — the physical gap is separate from the mathematical one

CLB-1's accounting premise may be proved for a mathematical model. A physical
application "additionally needs justified calibration/error bounds connecting
that model to its instance", and a field named `measured_resource_contract`
"neither proves the inequality nor is a logical prerequisite to every abstract
proof". Declaring a contract is not discharging it.

## 7. TL-5 — where the repository already places itself

The phenomenology atlas records three tiers: exact/tight sectors; results
"structurally explained but quantitatively open at modern scale" — naming
attention routing geometry, large-model feature learning, optimization
dynamics, continual learning, broad OOD generalization, tool ecosystems,
multi-agent systems and empirical scaling exponents; and an empirical
application programme requiring measured resources and independent replication.

This ledger does not move any result between tiers. It states why the first
tier's lower bounds are already scale-free, and why nothing in the second tier
becomes closed by proving more exact finite theorems.

## 8. Scope and falsifiers

Not claimed: that any specific registered bound has its accounting premise
discharged for a physical machine; that transport implies tightness; that an
exact finite result predicts a measured constant. The atlas's own warning is
adopted: the programme "should not convert unmeasured constants into theorems".

Falsified if a transported bound is shown to depend on allocation-set size, if
a shared lower bound is shown to determine an ordering, or if either premise is
shown to be dispensable.
