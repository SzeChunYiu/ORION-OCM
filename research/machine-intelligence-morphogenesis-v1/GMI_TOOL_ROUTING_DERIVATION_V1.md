# Calling out, and what it costs not to be able to check (B20)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/tool_routing_witness.py`.
Receipt: `microscopes/results/STAGE_TOOL_ROUTING_V1.json`.
Executed on `laptop-billy`; 53 assertions, 6.8 s, receipt byte-identical on a
clean-directory re-run. Every number below names the receipt key it comes from.

B10 priced one machine split into blocks under a context tag. B7 priced where to
look inside one input. Neither faced an alternative that is **not part of the
machine**: an outside holder with its own competence set, its own posted price,
and the capacity to be wrong without saying so. Three things follow only from
that, and none of them is B10 or B7 under a new name.

Eight tasks over a sixteen-payload space, exhaustive, exact integers. The cost
primitive is B10's — minimal branching structure, nodes held and tests
traversed. Two conventions carry weight and are stated where they are used: a
caller knows **which** task it ran and **what** answer it was handed but not the
payload, so held cost counts every node while traversal counts only payload
probes; and a holder posts **one** price, so its price is its own worst-case
probing plus a toll. The toll is the only free parameter and is swept 0–4.

## The primitive, re-verified on a path B10 did not have

B10 brute-forced its tree DP against all 256 total three-variable functions.
This ledger introduces **don't-care cells** — queries a machine is never asked —
which is a new code path, and don't-care minimisation is exactly where a
plausible DP silently returns a non-minimal tree. So the DP is checked against
an independent exhaustive enumeration of every decision tree (`primitive_validation`):

| arity | partial functions | carrying don't-cares | mismatches |
|---|---:|---:|---:|
| 2 | 81 | 65 | **0** |
| 3 | 6561 | 6305 | **0** |

The comparison is itself mutation-tested: a node count off by one is rejected.

## Breadth is paid once per call, through worst-case pooling

> **A holder must quote its worst task's price on every task it holds.** Pooling
> an easy capability with a hard one reprices the easy one upward, permanently
> and on every call — not only on the calls that need the hard one.

The `ladder` layout in `holders` is this and nothing else. One task — the
constant obligation, which costs 0 probes to answer — is priced three times,
unchanged, in three different company:

| competence set | worst task | posted price |
|---|---|---:|
| {constant} | constant, 0 probes | **0** |
| {project, constant} | project, 2 probes | **2** |
| {witness-one, project, constant} | witness-one, 3 probes | **3** |

Nothing about the task moved. Its company did.

The cost of overlap is that effect, summed. From `overlap`, at equal coverage of
all eight tasks, comparing a partition against total redundancy:

| layout | covered | fallbacks | prices | summed price |
|---|---:|---:|---|---:|
| partition | 8 | 0 | [4, 2, 4] | **28** |
| specialists | 8 | 1 | [3, 3, 4] | 30 |
| overlap-2 | 8 | 4 | [4, 4, 4] | 32 |
| nested | 8 | 4 | [4, 4, 4] | 32 |
| everyone | 8 | 8 | [4, 4, 4] | **32** |

The 28 is three tasks at 4, two at 2, three at 4 — the middle holder covers only
{project, constant}, whose worst probing is 2, so it can quote 2. The 32 is
eight tasks at 4. **The whole four-unit gap is those two tasks repriced from 2
to 4** by being pooled with parity and popcount, which probe 4. Overlap buys 4
fallbacks (`overlap`, `fallbacks`) and that is what it costs per round.

Under a partition a misjudged competence has nowhere to go at all: 0 fallbacks.

## The posted price cannot express breadth

The obvious statistic — the dearest holder in a layout — does not work here, and
this is a measured limit of the cost model rather than a result.

A posted price is a **maximum** over the holder's tasks, and the maximum is
capped by the payload arity: no task can be worth more than 4 probes when the
payload is 4 bits. So in `overlap`, `broadest_price` is **4 for partition,
overlap-2, nested, gap, specialists and everyone alike**. A holder covering one
third of the tasks and a holder covering all of them post the same number. The
max is blind to breadth by construction.

`price_monotone` measures the same blindness directly: of **107** strictly
nested competence pairs across every layout, **45** have the broader holder
strictly dearer and **0** have it cheaper. Price is monotone in competence but
not strictly so — once two holders are both at the ceiling the maximum can no
longer separate them.

> **That is why the summed price is the right statistic and the posted price is
> not.** The cost of breadth is real and is recoverable; it is simply not
> visible in the number a holder quotes, only in what a round of queries pays.

This is pinned in CI as an equality (`everyone["broadest_price"] ==
part["broadest_price"]`), so if the saturation ever stops holding the pin fails
rather than quietly changing what the section means.

## Whether the advantage expires — heterogeneity does not overturn B10

B10 found that a storage bargain paid in per-query work has a finite life. Two
things could break that here, so they are varied one at a time (`expiry_factorial`,
70 worlds each). "Expires" means the monolith is asymptotically optimal, ties
included — a tie is not an advantage.

| price | own cost | never expires | |
|---|---|---:|---|
| derived | interfering | **14 / 70** | this world |
| derived | isolated | **0** | |
| flat | interfering | 12 / 70 | |
| flat | isolated | **0** | B10's regime |

> **Interference is necessary.** With a task's probing made independent of what
> else is held, every storage advantage expires under *both* price regimes.
> Restore interference and 14 worlds survive: holding one more capability
> deepens the probing of everything already held, so a caller that absorbs
> everything pays for that on every query forever.

This is B10's own finding — conditioning costs computation rather than saving it
— read from outside the machine, where the same cost is what keeps an outside
holder permanently worth calling.

> **Heterogeneous prices are neither necessary nor sufficient.** They carry 2
> worlds on their own (14 against 12, `expiry_attribution.price_effect`) and
> none at all without interference. They move *which* capability is given up
> first, not whether any is.

Across `expiry`, 56 of 70 worlds expire and 14 do not, and `toll_threshold` puts
the first expiring toll at **1 in all 14 layout-weighting rows** — the threshold
is a property of the held machine, not of who is outside. Absorption is a
staircase rather than a switch (`staircase`: 68 multi-step worlds, up to 8
steps), and in **1** world it is not even nested: a task absorbed at a low round
count is handed back at a higher one.

## What it costs not to be able to check

A holder asked outside its competence returns a wrong answer, not an error. To
stay correct a caller must hold a competence map or a checker. Both are retained
structure, and B10 and B7 never had to buy either. From `verification`:

| task | obligation | solve probes | check probes | |
|---|---|---:|---:|---|
| witness-one | relational | 3 | **1** | cheaper |
| witness-zero | relational | 3 | **1** | cheaper |
| parity | functional | 4 | 4 | equal |
| majority | functional | 4 | 4 | equal |
| popcount | functional | 4 | 4 | equal |
| and-or | functional | 4 | 4 | equal |
| project | functional | 2 | 2 | equal |
| constant | functional | 0 | 0 | equal |

> **Checking is cheaper than computing exactly when the obligation is
> relational.** Where more than one answer is acceptable, a checker tests the
> answer it was handed. Where exactly one is, the checker must pin down the same
> answer the solver would have produced, and probes *exactly* as much —
> verification buys nothing at all.

The equality on the functional side is asserted as equality, not as "not
cheaper", so a single task drifting off it aborts the run. The verifier-gated
admission lifecycle is licensed by **multiple acceptable answers**, not by
outsourcing.

## Knowing who to ask is not what kills calling out

The expected result was that a competence map eventually costs more than the
capability it spares you holding. It does not, and the negative is carried by a
control rather than by an absence.

With competence declared per task the map is a function of three bits the caller
already knows, so it costs storage and no probes at all: `postures` reports it
cheaper than the capability in **28 of 28** worlds that obtain anything. That
margin is *forced by the construction* — such a map is capped at 15 nodes
against savings of 22 to 100 — so it is a baseline, not evidence.

The evidence is the twin. Let competence be **earned** instead of declared: each
holder gets a probe budget, answers with the commonest value in each class it
can tell apart, and is competent on the instances it actually gets right, which
have no reason to respect task boundaries (`fine_competence`):

| budget | covered instances | map nodes | map probes | hold(covered) |
|---:|---:|---:|---:|---:|
| 0 | 70 | 1 | 0 | 7 |
| 1 | 93 | 27 | 3 | 45 |
| 2 | 113 | 39 | 4 | 79 |
| 3 | 112 | 27 | 4 | 77 |
| 4 | 126 | 1 | 0 | 109 |

The map never collapses. Nor does it under an adversarial search over competence
**regions** — parity classes, single bits, density, task halves — where 0 of
**66** pairs collapse and the dearest map anywhere costs 31 nodes against a
capability of 77 (`collapse_search`).

The collapse is nonetheless real: `collapse_control` keeps the competence
boundary and makes the capability trivial, and the map costs **31 nodes against
a capability of 1**. The detector fires. So the negative is a fact about this
world, not about the code.

> Naming a correct holder is **itself a relational obligation** — any correct one
> will do — and that slack is the same slack that makes checking cheap above.
> One property buys both.

> What survives is sharper than what was expected: a caller is never priced out
> of **knowing** who to ask. It is priced out of **checking**, and only for
> functional obligations. Verification, not selection, is the cost B10 and B7
> never had to pay.

## Neutral recovery

A candidate assigns each task to a source: *computed from structure held here*,
or *obtained from outside holder i at its posted price*. No `tool`, `solver`,
`router`, `routing`, `route`, `hybrid`, `dispatch`, `expert` or `gate` appears in
the candidate descriptors, and the gate is mutation-tested — adding one
mislabelled source makes it fire.

From `recovery`, over 70 worlds: a mixture wins **40**, a single held machine
wins **30**. The obvious answer — obtain everything the cheapest holder covers —
is optimal in **0 of 70**. Neither shape could have been written down without
the search, and neither wins everywhere.

`brute_force` confirms the decomposition the search relies on, in an
**overlapping** world where tasks genuinely have a choice of holder: all **1296**
legal assignments enumerated at 8 rounds, cost **253**, identical to the
decomposed answer. Under a partition this check would have been vacuous.

## The selection rule, and where it breaks

The rule is: send each obtained task to the cheapest holder *believed*
competent. Overstate one holder's competence by one task and ask whether the
rule changes its mind — a misjudgement nobody acts on is not a failure. Control:
the same sweep under a rule that ignores price and takes the first believed-
competent holder.

Where two holders post the same lowest price the tie is broken by index, so the
two rules pick the same holder and cannot be separated. The comparison is
therefore read on worlds with a **strictly** cheapest holder
(`misjudgement_totals_untied`; `misjudgement_totals` holds the unrestricted sweep):

| prices | rule | overstatements | consequential | onto the preferred holder |
|---|---|---:|---:|---:|
| all | cheapest | 890 | 680 | 360 |
| all | first | 890 | 670 | 330 |
| **no tie** | **cheapest** | 340 | 270 | **130** |
| **no tie** | first | 340 | 260 | 100 |

Removing the confound widens the gap rather than closing it: 130 of 270 against
100 of 260 (`misjudgement_separation.untied_worlds`, 33800 against 27000 as an
exact cross-product).

> **A price-minimising rule concentrates errors on the holder it prefers.**
> Errors follow the selection rule, so the holder a rule prefers is the holder
> whose competence must be judged most carefully — and by the section above,
> that judgement can only be made cheaply by checking where the obligation is
> relational.

## Composition, or a distinct domain

B20 asks whether hybridisation is composition or its own thing. The ledger
answers both ways at once, from `composition`: the **obtained** side is a plain
sum over tasks, each at one posted price, and is composition. The **held** side
is not — holding all eight capabilities costs **109** nodes against **120** held
separately, with 4008 disjoint pairs sharing structure and a largest single
saving of 29 (`sharing`).

> A mixture is a composition on the outside and not one on the inside.

## Scope

- Eight tasks over sixteen payloads, three outside holders, seven competence
  layouts, five tolls, two weightings: 70 worlds, exhaustive, exact integers.
  No sampling and no floating point in any reported number.
- **The posted price saturates at the payload arity.** Every conclusion about
  the cost of breadth is read from the summed price, never from the maximum.
  Widening the payload would move where the ceiling sits; it would not change
  that a maximum is a ceiling statistic.
- **Two conventions, not results.** Index bits are free at query time and
  payload bits are probed; a holder posts one price. Both are stated at the
  point of use and both move margins.
- **Competence is per task in the main search**, and instance-level competence
  appears only in the verification twin. A ledger where the assignment itself is
  made per instance is legal here and is not evaluated.
- **No price is ever attached to a wrong answer.** Exposure is reported as exact
  counts of consequential misjudgements, never converted into cost, so no
  error-rate parameter enters the accounting.
- **Failure-aware fallback is derived as availability and price only.** The
  fallback counts in `overlap` and the misjudgement counts above say what a
  fallback costs and when one exists; no recovery protocol is modelled.
- **The 28/28 baseline in `postures` is forced by construction** and is reported
  as a baseline. The load-bearing result there is the earned-competence twin,
  the 66-pair search, and the control that fires.

**Falsifier.** Exhibit a functional obligation that is strictly cheaper to check
than to solve; or a competence configuration over these eight tasks where naming
a correct holder costs more than answering; or an ecology with flat prices and
non-interfering held structure in which a storage advantage never expires; or a
holder that posts a cheaper price than one whose competence it strictly
contains.
