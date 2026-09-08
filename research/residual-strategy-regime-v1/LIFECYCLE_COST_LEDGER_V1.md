# Four-term lifecycle cost ledger

**Status:** research-only measurement instrument / no policy change / no lifecycle gate
touched / no production behaviour changed / no ML authorization.

`CONVERGENCE_V1.md` item 3 says a reusable cognitive state is worth building only when
expected reuse before invalidation repays build and maintenance and lifecycle cost. That
is a claim with four cost terms in it, and a claim of that shape cannot be settled until
all four are on the same page against the same parent over the same population.

This module is that page.

## 1. The four terms, and why exactly these

Two lanes reached the same decomposition from opposite directions, which is the only
reason to trust it:

| term | paid | this lane | the cognitive-ladder lane |
|---|---|---|---|
| `PREPARATION` | once per epoch | whole-bank grounding, 3.689–3.931 s per cold arm | compiling a verdict table |
| `PER_USE` | once per use | F2 feature acquisition, ~4.09 coefficient visits per query | consulting the table |
| `OCCUPANCY` | per step held | policy table, DP storage | the table's bits, from the same budget as the facts |
| `INVALIDATION` | once per invalidation | reset/drift epochs, `sum_e B_r(max_{i in e} R(q_i))` | recompiling after the version space shrinks |

Neither lane set out to find four terms. Both ended with these four, and neither can
close a net-benefit claim while any of them is missing.

## 2. The one rule

> **A ledger with any uncharged term may report an upper BOUND on net benefit.
> It may never report a net benefit.**

This is enforced rather than advised. `Charge` cannot be constructed empty: it is either
a resource vector or an explicit `uncharged_reason`, never both and never neither, and a
blank reason is refused. `scalar_margin` returns `net_benefit_claimable: False` with the
offending terms named, however large the margin is. `report` terminates at
`INCOMPLETE_LEDGER_BOUND_ONLY`.

The reason for the severity is that an absent cost term is not a small error. It is a
*sign* error, and it is the specific one this programme keeps making. Every real
correction in the cognitive-ladder lane came from billing something previously free:

```text
DEV-2  charged rule USE            DEV-1's carry advantage became PARENT_SUFFICIENT
X1     charged DELIBERATION        E6's transferred mechanism kept its contract, lost its sign
DEV-6  charged the SCAN            DEV-5's 5.1x became 3.4x, and this lane's own proposed fix was refuted
X7     charged the TABLE's storage  eager compilation fell from 13 winning settings to 2
```

Four times, the same shape: something free, then billed, then the conclusion moved.

## 3. Proposition 1 — an incomplete ledger bounds benefit from above

> Let `L` be a ledger in which term `t` is uncharged, and let `L'` be identical except
> that `t` is charged at unit vector `v` with multiplicity `m`. Then for every
> non-negative price vector `p`,
>
> ```text
> margin(L') <= margin(L).
> ```

**Proof.** `total(L') = total(L) + m·v` coordinatewise, because an uncharged term
contributes nothing to the sum and a charged one contributes `m·v`. Resource coordinates
are non-negative by `ResourceVector.__post_init__` and multiplicities are non-negative by
the ledger's own validation, so `m·v >= 0` in every coordinate and
`total(L') >= total(L)` coordinatewise. `value(x) = sum_c p_c x_c` with every `p_c >= 0`
is a monotone linear functional, so `value(total(L')) >= value(total(L))`. Since
`margin = value(parent_cost) - value(total)` and `parent_cost` is unchanged,
`margin(L') <= margin(L)`. ∎

**Corollary (which way an incomplete ledger may be read).** On an incomplete ledger a
*parent* win is sound — charging the missing term can only make it larger. An *object*
win is not a result. The `reading` field says exactly this in words, so the direction
cannot be lost between the receipt and its summary.

`test_charging_a_previously_uncharged_term_never_helps_the_object` checks the proposition
over a hundred random vectors, and would fail if any term were ever credited rather than
charged.

## 4. Coordinates are not collapsed

Comparison inside the ledger is Pareto on the repository's own `ResourceVector`, which
contract §19 requires and which `MULTIOBJECTIVE_COVERAGE_STATE_V1.md` and
`PRICE_OBJECTIVE_CONFLICT_V1.md` in this tranche already rely on. Disagreeing coordinates
produce `INCOMPARABLE_WITHOUT_A_PRICE` rather than an average.

A scalar margin exists, because a decision eventually needs one, but it exists only
against explicitly declared prices for **every** coordinate — a missing price is an error,
not a default of zero — and the prices are published inside the same object as the margin
they produced. Quoting the number away from its prices is then visibly a different claim.

## 5. Right censoring

`right_censored` marks an observation window that ended while the object was still in
use. X8 is the reason the flag exists: it reported the highest price at which an advantage
survived, that price was the top of its own sweep, and reporting it as a boundary rather
than as a bound would have been the study's one real error. A censored ledger's totals are
floors, and the reading says which side that favours.

## 6. The regression fixture

`test_a_free_storage_term_inverts_a_real_published_ordering` encodes the inversion X7
measured. Two arms differ only in how many cells they hold — the whole extension, or only
what was demanded, using X7's measured 16 and ~14. With occupancy uncharged their margins
are **identical**, which is exactly the reading X6 published: the two levers looked like
the same lever. With occupancy charged at two bits a cell they separate.

The fixture reproduces the *mechanism* of that inversion under the ledger's arithmetic. It
does not re-derive X7's winning-setting counts, and it is not offered as independent
confirmation of them.

## 7. What this is for

It is step 3 of a five-step route to the claim that has been stuck at 30–45%: *does OCM as
an architecture provide net benefit?*

That claim is not provable in the form usually stated, because the sign is
population-relative and both lanes have shown it flipping within their own data. The
provable form is a **characterization**: a decidable predicate on a workload such that
total charged cost beats the best charged parent exactly when the predicate holds, plus a
measurement of the mass of the real population on which it holds.

```text
1. fix the theorem shape: characterization, not superiority
2. freeze the scope boundary -- OCM-owned cost vs host-supplied cost
3. this ledger, emitted per episode                       <-- here
4. measure the invalidation-rate distribution on the real workload
5. compose through break_even_uses; report the population mass above it
```

Step 4 is the remaining hard part, and it is a data-collection problem rather than a
theory problem: three of the four terms are measurable from one cold run, and only the
effective reusable horizon before reset, drift or revocation needs longitudinal data.
Step 2 is not optional either — `R0A_CHECKER_CENSUS_V1.md` measured that production
supplies **no** checker callable, so a real share of the architecture's cost lives in
host-supplied components this repository cannot see. Deciding that boundary after the
measurement is how a percentage stays at 30–45% indefinitely.

## 8. What this does not establish

- A ledger is a measurement over one population against one parent. It authorizes nothing,
  changes no policy or lifecycle gate, and a positive margin is a fact about the stated
  population under the stated prices.
- The ledger charges what it is given. It cannot know that a term was measured badly, only
  that it was not measured at all. `PROSPECTIVE_SELECTOR_PROTOCOL_V1.md`'s legality rules
  still govern what may be observed in the first place.
- Nothing here weakens `LEARNED_ROUTER_NOT_AUTHORIZED`. If anything it raises the bar: a
  learned selector must now clear a parent whose costs are all four charged, not a parent
  that was quietly holding some of them for free.
