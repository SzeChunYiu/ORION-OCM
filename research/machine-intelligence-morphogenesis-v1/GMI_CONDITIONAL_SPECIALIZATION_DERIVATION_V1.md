# Conditional specialization: a condition, not a recovery (B10)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/conditional_specialization_witness.py`.
Receipt: `microscopes/results/STAGE_CONDITIONAL_SPECIALIZATION_V1.json`.
Derived by a parallel worker. Witness and receipt md5 **independently
reproduced** on `laptop-billy` before this document was written; 65 assertions;
the confound guard was forced and confirmed to fire.

60 worlds (15 set-partitions × 4 rule catalogues), exhaustive. One cost
primitive — minimal decision-tree nodes held plus path traversed —
**brute-force verified against exhaustive tree enumeration on all 256
three-variable functions, 0 mismatches.**

## What is *not* the law

The surplus decomposes as `net = B − A`, where `A` is the label map held minus
what the undivided rule already spends separating contexts inside its own tree,
and `B` is what the undivided rule spends on obligation bodies minus what the
split spends.

> **"Pays iff `B > A`" is an identity, asserted only as a consistency check.**
> It is not a finding and is not written up as one.

## Necessary, not sufficient

| label map | worlds | of which pay |
|---|---:|---:|
| tag-collapsible | 32 | **0** |
| non-collapsible | 28 | **11** |

So 17 non-collapsible worlds still do not pay.

> Interleaving makes the surplus *possible*; the price of the obligations makes
> it *real*.

## The mechanism is not the expected one

Of the 11 paying worlds: **7** pay because holding the separation explicitly is
cheaper than what the undivided rule spends separating inside its own tree
(`A < 0`); only **6** because of duplicated rule bodies (`B > 0`); 2 both.

> "The tree must duplicate the rule" is **not** the larger mechanism here. The
> undivided rule's real handicap is that it must *interleave* separating the
> context with computing the obligation, while the split holds that separation
> once, compactly.

A one-way implication holds with no exceptions: **non-collapsible ⇒ duplicates
(28/28)**. Collapsibility merely *permits* avoiding duplication — 6 collapsible
worlds duplicate anyway, because the tree tests a payload bit first and
separates late.

*The worker had asserted duplication would coincide with collapsibility. The
gate fired; the story was dropped and replaced with the measured cross-tab.*

## Conditioning costs computation — it does not save it

| measure | result |
|---|---|
| worst-case traversal | ties in **58/60**; in the 2 exceptions the **undivided** rule traverses less |
| expected traversal | split **never** cheaper; strictly worse in **28/60** |

A branching machine is already conditional per query. Committing to a block
before reading the payload strictly *raises* expected tests. 28 worlds have a
shared leaf — obligations that already agree — which no split can have.

> This **refutes** the compute argument for conditional specialization in this
> accounting rather than leaving it unaddressed.

## The advantage expires

Because the split buys storage and pays in per-query work, its verdict has a
finite life: `r* = net_held / (E[tests]_split − E[tests]_one_rule)`.

Measured `r*` across paying worlds: **20, 32, 32, 32, 32, 40, 72**. Four never
expire (gap 0); **7 change hands between r = 8 and r = 512.**

> Conditional specialization is a **storage bargain paid for in per-query
> work** — PVR-3 again, with the split on the retention side.

## Neutral recovery

Candidates are `(how you split the context set, which rule per block)`; the
one-block machine and the one-rule-over-tag-and-payload machine are both
members. **11 of 60** recover a split — 7/15 under the dear catalogue, 3/15
mixed, 1/15 cheapest, **0/15 cheap**.

The anti-rig gates matter here: the winner must equal the priced cost floor, and
**the world's own obligation split won 11 and lost 49** — a chooser handed the
answer would win all 60.

*A mutation test showed the recovery gate initially **accepted** a chooser that
returned the answer it was handed. Real defect, fixed with the cost-floor and
cross-check gates.*

## What is not closed

**Latent context.** The tag is *given*. Inferring which obligation is active
from the payload alone is not modelled, and this cost model charges **structure
held**, not **information available**, so it *cannot* test it. That is precisely
the antecedent of the corpus's open attention gap.

> Nothing here recovers routing in general. It derives a **condition**.

**The `GATE` measurement at 0.37× is consistent with this, not in tension.**
Registered ecologies sit at `m = 1`, tag-collapsible, or cheap obligations — and
this accounting calls conditioning overhead in all three.

**Trees only.** A machine that could rejoin paths would get the reuse saving
with no label map at all, and the result vanishes. The restriction is
load-bearing and named rather than buried.

**The "active parameters" compute argument** needs a flat machine that reads all
of itself per query. Not priced here, so nothing supports a compute claim.

## Scope

- Box 4 charges `C = S` — re-deriving costs what holding costs. An assumption,
  not a result; the thresholds depend on it.
- Inter-block movement cost is **not** modelled.
- **Convention dependence, stated rather than hidden**: charging tests-only
  instead of tests-and-leaves flips **9 of 60** verdicts. All 9 sit within one
  node of a tie and all move the same way. The gate was weakened from "no
  flips" to "no *clear* verdict flips, max flipped margin 1". **Near-ties must
  not be read as results.**
- Load balance is PVR-3 per block with load as the recurrence count; uniform 4/4
  and skewed 1/4 are clear in every catalogue (`C−U` spans 2..12), so the
  reading is not a price artefact.

## The failure that mattered most

A first version swept only **arrangement** over **one** catalogue and produced a
clean biconditional — "pays iff not tag-collapsible" — holding in all 15 worlds.

**It is false.** It was a property of that catalogue being expensive. Sweeping
the catalogue produced **17 counterexamples**. Arrangement and obligation price
were confounded. The witness now asserts `len(CATALOGUES) > 1` with that
mistake named in the message, and forcing a single catalogue makes the run abort.

**Falsifier.** Exhibit a tag-collapsible world that pays; or a paying world
where the split is cheaper on expected traversal; or a recovery where the
world's own obligation split wins in all 60.
