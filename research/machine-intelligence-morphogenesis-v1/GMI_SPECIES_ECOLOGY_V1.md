# Machine-species ecology: what the corpus already proves, and what it does not

Date: 2026-09-14. Addresses checklist section **G**, boxes 7–16.
Evidence: `microscopes/results/STAGE_R10_INVASION_V1.json`, produced by `gmi_microscope/invasion.py`.
Companion: `GMI_SPECIES_ALGEBRA_V1.md` (boxes 1–6).

Section G's second half asks for ecology: niche occupancy, coexistence, competitive exclusion, symbiosis,
resource partitioning, abundance, transitions under repricing, invasion, extinction, and multi-species
microscopes. **Before building an ecology, I checked whether the corpus already had one. It does**, and it is
better than a fresh stub would have been — so this document reports what that result closes, guards it, and
names precisely what it leaves open.

## 1  The existing result

`invasion.py` runs two carriers **developing in the same ecology out of one shared charged budget**, with
occupancy decided by competition rather than by two independent scores placed side by side. That distinction
is the whole point, and it is tested rather than assumed.

* **8 carriers**, all ordered pairs, **3 declared budget pools** (20 000 / 60 000 / 200 000) → **192 cells**
* Registered prediction: *"occupancy under a shared budget is not a function of the solo scores: at least one
  ordered pair must disagree"* — **holds**
* **65 of 192 cells** disagree with solo scoring — 20 on the diagonal, **45 off-diagonal**
* Verdict: `COMPETITION_REORDERS_OCCUPANCY`

The off-diagonal count matters: disagreement confined to the diagonal would only mean a carrier behaves
differently against a copy of itself, which is not a statement about invasion at all. A pin now enforces that.

## 2  What it closes

**Box 14, invasion** — the outcome taxonomy is measured per ordered pair, not asserted.

**Box 9, competitive exclusion** and **box 8, coexistence** — both are measured, and the finding is that
**exclusion is the rule and coexistence the exception**:

| pool | COEXIST | INVADER_REPLACES | RESIDENT_HOLDS |
|---|---:|---:|---:|
| 20 000 | **6** | 29 | 29 |
| 60 000 | **2** | 26 | 36 |
| 200 000 | **2** | 28 | 34 |

Coexistence never exceeds **6 of 64** (9.4%) in any pool. A pin fails if coexistence ever becomes the
majority outcome, or if either exclusion direction stops occurring — a competition where the invader always
wins, or never wins, would not discriminate.

**Box 15, extinction/displacement** — `INVADER_REPLACES` *is* displacement, measured in 26–29 of 64 cells per
pool.

**Box 7, niche occupancy** — partially. Occupancy is what the competition decides, and it is shown not to be
recoverable from solo scores. What is *not* here is a notion of niche independent of the pairwise contest.

## 3  An observation I am deliberately not turning into a law

Coexistence is highest at the smallest pool (6, then 2, then 2). It is tempting to read *"larger budgets
suppress coexistence"*, and I am not claiming it: three pools, a change of four cells, and the last two are
flat rather than continuing to fall. More importantly the receipt's own `claim_ceiling` says the allocation
rule **is a modelling choice and a different rule can reorder outcomes**. A trend read off three points under
one allocation rule is not a law, and the corpus has enough real laws that it does not need a weak one.

What *is* solid is the level rather than the trend: coexistence is rare everywhere.

## 4  The invariance control

`remint_invariance`: reminting either competitor changed **no** reported quantity across **12** competitions
checked. That is a real control — it establishes the outcome depends on organization rather than on a
competitor's identity or name — and it was previously unguarded. It is now pinned.

## 5  What this does NOT close, stated plainly

| box | status |
|---|---|
| 10 symbiosis | **closed, negatively** — see §5c |
| 11 resource partitioning | **closed** — see §5e; spending more *anti*-predicts winning |
| 12 abundance from ecology | **closed** — see §5e; abundance is stable under repricing |
| 13 morphology transitions under repricing | **closed** — see §5d; repricing is NON-monotone |
| 16 multi-species ecologies | **open** — this is strictly **pairwise**; three or more competitors are untested |

Box 16 is the load-bearing gap. Every result above is a two-body contest, and pairwise exclusion does not
determine multi-species outcomes — rock-paper-scissors cycles are the standard counterexample, and nothing
here rules one out. **Claiming section G's ecology closed on pairwise evidence would be wrong**, and the
distinction is exactly the one boxes 8–9 versus box 16 are drawing.

## 5b  Box 16 decided: a frozen prediction that FAILED, and a better finding underneath

Section 5 called box 16 the load-bearing gap and cited rock-paper-scissors cycles as the *reason* pairwise
data cannot settle multi-species outcomes. That was a borrowed warning. It is now a measured question about
this corpus's own data — and the answer is not the one I predicted.

**The prediction, frozen at `ed21bdf6` in a commit with no measuring code**: at least one intransitive triple
exists among the 8 R10 carriers. The reasoning was that R10's upheld finding — occupancy is not a function of
the solo scores — means a scalar ranking already loses information, so the pairwise relation is probably not
an order either. The receipt recorded that this is an **inference, not an implication**, and that it could
fail.

**It failed.** Among triples whose three pairs are all decided: **0 of 76 are cyclic.** Where the two readings
of the matrix agree, dominance is **acyclic**.

That zero is not vacuous, and the witness enforces it: a triple only counts once all three of its pairs are
*decided*, because an undecided pair cannot participate in a cycle. 76 triples were fully decided across the
three pools and none was cyclic. A pin fails if the decided count ever collapses, since the acyclicity finding
rests entirely on cycles having been possible.

### What the data says instead: an order effect

Reading the matrix two ways — *A succeeded as an invader against B* and *A repelled B as a resident* — should
be the same fact. **In 36 of 168 ordered pairs, they disagree.**

So "A beats B" is not one fact. **Who was there first changes the outcome.** That is a priority effect, and it
answers box 16 more decisively than intransitivity would have: a pairwise table recording only *who beats
whom* cannot determine a multi-species outcome when arrival order matters — transitive or not.

**Box 16 is therefore necessary, for order dependence rather than for the intransitivity I predicted.** The
prediction was wrong about the mechanism and right about the conclusion, which is exactly the case freezing
exists to expose rather than smooth over. A pin keeps the verdict recorded as `FALSIFIED`.

The disagreement is also *partial* — 36 of 168, not all of them — and that matters: universal disagreement
would mean the matrix is simply inconsistent, whereas partial disagreement is a property of the competition.
Both bounds are pinned.

## 5c  Box 10: symbiosis does not occur, and the zero is backed by a control

**COEXIST is not symbiosis.** Coexisting means both survived; symbiosis means both did *better together than
alone*. That distinction was what left box 10 open — and it turned out to be measurable from data already on
disk, since R10 carries `capability_invader` / `capability_resident` for all 192 cells and a solo baseline
per carrier per pool.

**Criterion, frozen at `080a86ae`** before any measuring code existed: a pair is **symbiotic** iff both
capabilities in competition strictly exceed the same carriers' solo capabilities; **mutually harmful** iff
both are strictly lower; anything else is one-sided.

Two predictions were frozen, not one:

* **P1** — symbiosis never occurs. **Holds: 0 of 168 pairs.**
* **P2** — mutual harm does occur. **Holds: 38 of 168 pairs.**

**P2 exists because P1 alone would be unfalsifiable-looking.** "Nothing was found" is also what a broken
measurement reports. The adjudicator *asserts* that mutual harm is non-zero, so if the comparison ever stops
detecting joint effects the result fails loudly instead of returning a clean-looking zero. That assertion is
the reason the zero can be believed.

| outcome | pairs |
|---|---:|
| symbiotic (both above solo) | **0** |
| mutually harmful (both below solo) | **38** |
| one-sided | 123 |
| both unchanged | 7 |

**Reading**: two carriers sharing one charged pool never both end above their solo capability, while 38 pairs
both end below it. Sharing a fixed budget is not a cooperative interaction in this ecology. Box 10's
criterion is satisfiable in principle and has **no positive instance** in this corpus — a negative result,
reported as one.

### An orientation check that had to come first

The cell keys are `pool<P>|<a>|<b>`, and which of `a`, `b` is the resident decides the **sign of every
comparison**. Rather than assume it, the adjudicator checks both readings against the invasion matrix:
`pool|resident|invader` agrees on **192 of 192** cells, the reverse on 54. A pin fails if that ever drops
below 192, because a misread orientation would invert the entire result silently while still looking clean.

## 5d  Box 13: repricing is non-monotone — the second frozen prediction to fail

R10 ran the same 8 carriers at three budget pools, which *is* the repricing box 13 names. Reading a winner
per pool gives each ordered pair a **winner sequence** of length 3; a pair **oscillates** if that sequence is
`X, Y, X` — reversing as the budget grows, then reversing back.

**Frozen at `f0c7cd29`**, before any measuring code existed:

* **P1** — no pair oscillates. **FALSIFIED.**
* **P2** — at least one pair changes winner. **Holds.**

| | pairs |
|---|---:|
| ordered pairs | 56 |
| constant across all three pools | 49 |
| changed at least once | 7 |
| **oscillating (`X, Y, X`)** | **2** |

Both oscillations have `gradient_net_h4` as the invader: it wins at 20 000, loses at 60 000, and wins again at
200 000. With n = 2 that is an observation about two pairs, **not** a claim that this carrier is special —
stated here so a reader does not upgrade it.

**What it means.** Repricing does **not** have a single direction. A transition made as the budget grows can
be undone by growing it further, so **morphology transitions cannot be extrapolated from endpoints**: knowing
the outcome at the smallest and largest pool does not determine the middle. Box 13 is closed with a negative
structural answer rather than the predictable one-way law I expected.

The texture is worth keeping: 49 of 56 pairs are completely budget-invariant, and among the 7 that change,
3 move the resident's way and **0** move the invader's. So the system is *mostly* directional — the
non-monotonicity is real but confined, and the confinement is what a reader needs in order not to over-read
either way.

**The control fired, which is why the falsification is trustworthy.** P2 exists because "no oscillation" is
also what a repricing that changes nothing would report. 7 pairs do change, so the measurement was detecting
budget effects when it found the oscillations. Pins assert that changing pairs stay non-zero, that constant
pairs stay non-zero, and that not every changing pair oscillates.

**Caveat carried from the R10 receipt**: the allocation rule is a modelling choice and a different rule can
reorder outcomes. This is a property of this ecology under that rule.

## 5e  Boxes 11 and 12: spending does not win, and abundance is stable

Both frozen at `9f71a640` before any measuring code existed. One prediction failed, one held.

### Box 11 — resource partitioning: **P1 falsified, and informatively**

I predicted the winner draws more of the shared pool, reasoning that winning means developing further and
development is what charge buys. The measurement says the opposite:

| over 162 decided contests | count |
|---|---:|
| **loser** drew more charge | **110** |
| winner drew more charge | 52 |
| equal | 0 |

**Drawing more of the shared pool anti-predicts winning**, roughly two to one. In hindsight the mechanism is
plain — a competitor that burns charge inefficiently exhausts the budget and fails, so what wins is
*efficiency of expenditure*, not expenditure. But I had it backwards in advance, and the prediction is
recorded as failed rather than reinterpreted after the fact.

The control mattered here too, in the opposite direction from usual: a pin asserts the winner draws more in
**at least some** contests (52 of 162). "The winner never draws more" would be a far stronger claim than what
was measured, and it should not be able to pass silently.

### Box 12 — abundance: **P3 holds**

Win counts per carrier per pool:

| carrier | 20 000 | 60 000 | 200 000 |
|---|---:|---:|---:|
| **hamming_knn_k3** | **14** | **14** | **14** |
| soft_retrieval | 12 | 12 | 12 |
| exemplar_table | 8 | 8 | 8 |
| gradient_net_h4 | 7 | 6 | 8 |
| gradient_net_h2 | 6 | 6 | 6 |
| particles_p4 | 4 | 3 | 5 |
| compiled_search | 1 | 4 | 1 |
| program_search | 0 | 2 | 1 |

The same carrier tops every pool, and **four of the eight have identical win counts at every budget**.
Abundance is predictable from the ecology and stable under repricing — even though box 13 showed repricing is
non-monotone and two pairs oscillate.

That combination is the useful part: **the pairwise outcomes move while the aggregate does not.** The four
carriers that do vary — `compiled_search`, `gradient_net_h4`, `particles_p4`, `program_search` — are exactly
where the budget bites, and a pin asserts that both the invariant and the varying sets stay non-empty, so
neither "nothing moves" nor "everything moves" can creep in.

**Caveat carried from R10**: the allocation rule is a modelling choice and a different rule can reorder
outcomes. Box 11's result in particular is a statement about competition under *this* allocation rule.

## 6  A gap in the guarding, now fixed

This result — a registered prediction, 192 cells, an invariance control — had **no CI pin of any kind**. It
could have drifted silently. Three pins now assert the prediction still holds, that disagreement is neither
zero nor total and occurs off-diagonal, that coexistence stays the exception with both exclusion directions
occurring, and that remint invariance holds.

Reproduction is **not** wired: `invasion.py` is not a single-file witness and does not run under the
temp-directory harness. The pins guard the claims, not the derivation of the receipt. That is weaker than the
corpus's other guards and is recorded here rather than glossed.
