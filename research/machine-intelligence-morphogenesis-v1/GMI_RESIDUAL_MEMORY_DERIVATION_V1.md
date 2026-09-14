# Residual memory: what an absorbing machine still keeps outside (B12)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/residual_memory_witness.py`.
Receipt: `microscopes/results/STAGE_RESIDUAL_MEMORY_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

Every number names the receipt key it came from. The only numbers that are not
keys are the prices, declared as constants in the witness (`ABSORB=4`,
`WRITE=1`, `LOOKUP=3`, `PROBE=1`, `EVAL=1`, `RESEARCH=4`, `INDEX_BUILD=2`);
everything derived from them is a key.

B11 asked whether to hold knowledge as a table or as a rule, from nothing. This
asks the question one step later. A machine has **already absorbed most of the
body parametrically**, and only the part it could not absorb is in dispute — the
**residual**.

World (`world`): 16 inputs of 4 bits, a **three-valued** response, 23 rules. The
third value is load-bearing: under a binary response every residual admits one
correction, §1's quotient is trivially a single class, and its twin cannot be
built. The class is deliberately not closed under `(a+b) mod 3` — 529 ordered
pairs collapse to `two_term_images` = 196 distinct functions, only
`one_term_images` = 21 of them single terms. A closed class absorbs every
residual and nothing is ever stored.

## 1. The residual quotient

The store must tell residual inputs apart only up to the **response each
demands**. Key `quotient`:

| obligation | rule | coverage | residual | payload classes | collapses |
|---|---|---:|---:|---:|---|
| `absorbed` | `sum_mod3` | 16 | 0 | 0 | no |
| `residual_collapse` | `sum_mod3` | 13 | 3 | **1** | **yes** |
| `residual_distinct` | `sum_mod3` | 13 | 3 | **3** | **no** |
| `residual_reducible` | `cap2` | 15 | 1 | 1 | no |
| `smooth_residual` | `one_if>=2` | 11 | 5 | 1 | yes |
| `incompressible` | `one_if>=1` | 10 | 6 | 2 | yes |

The middle two are a **matched twin**, found by search subject to both members
being irreducible: same rule, same three perturbed inputs
(`world.twin_positions` = `0000`, `0001`, `0010`), same residual 3. They differ
only in what those three demand — one response (`world.collapse_value` = 2) or
three (`world.distinct_values` = `[1,0,2]`).

> **A residual store is a key set plus one response per class, not one response
> per item.** The keys never collapse; the payload does.

When the payload collapses to one class the store is a constant on a set — a
rule term wearing a store's clothes. Whether the class can *say* that set is §2.

## 2. Irreducibility: forced, or waste

This contrast is the result. Search the class exhaustively for a one- or
two-term expression under `(a+b) mod 3`; the search is tie-break-free, so it
does not inherit whichever rule the coverage search picked. Key
`irreducibility`:

| obligation | one term | two terms | hybrid (rule+store) | verdict |
|---|---|---|---:|---|
| `absorbed` | `sum_mod3` | — | 5 | no residual |
| `residual_collapse` | none | **none** | 12 | **STORE IS FORCED** |
| `residual_distinct` | none | **none** | 12 | **STORE IS FORCED** |
| `residual_reducible` | none | `two_if>=3+sum_mod3` = 9 | 10 | **STORE IS WASTE** |
| `smooth_residual` | none | `one_if>=2+one_if>=3` = 8 | 13 | **STORE IS WASTE** |
| `incompressible` | none | **none** | 14 | **STORE IS FORCED** |

`residual_reducible` pays 9 for a second term against 10 for rule-plus-store,
`smooth_residual` 8 against 13 — neither needs a store. The twins and
`incompressible` have no two-term expression, so for them it is forced.

> **Provision an external store only after the composition search fails.** A
> residual the class can express is not a residual — it is a description the
> machine has not finished writing.

**Positive control.** The same search that returns `none` for three obligations
finds genuine two-term expressions for two others, so its negatives are evidence
rather than an empty candidate space.

## 3. External store versus full absorption

Installing one item costs 4 in the description against 1 in the store; serving
one query costs 1 for the description against 2 plus 3 on a hit. The store wins
iff `(ABSORB-WRITE)*k > N*(PROBE + f*LOOKUP)`. Key `external_vs_absorbed`:

| obligation | `k` | `f` | `N*` | N=1 | N=64 |
|---|---:|---:|---:|---|---|
| `absorbed` | 0 | 0 | 0 | absorb | absorb |
| `residual_collapse` / `residual_distinct` | 3 | 3/16 | 144/25 | store | absorb |
| `residual_reducible` | 1 | 1/16 | 48/19 | store | absorb |
| `smooth_residual` | 5 | 5/16 | 240/31 | store | absorb |
| `incompressible` | 6 | 3/8 | 144/17 | store | absorb |

> **Not B11's threshold, and it runs the other way.** B11 asks how often one item
> must *recur* before keeping beats recomputing, and more reuse favours the
> store. This asks how many queries a *fixed* residual serves, and more queries
> favour **absorption** — the store pays per query, the description pays once.

### 3b. Frequency, separated from size

`f = k/M` above is the residual's *measure*; that is not a frequency, and
conflating the two would make this box a restatement of §3. Let each residual
input be `w` times as likely to be asked, so `f = w*k/(w*k + (M-k))` is free of
`k`. Probing first pays iff `PROBE < (1-f)*LOOKUP`, i.e. `f < 2/3`. Key
`frequency` (12 cells; four shown):

| `k` | `w` | `f` | gated serve | ungated | probe pays |
|---:|---:|---:|---:|---:|---|
| 10 | 1/8 | 5/29 | 73/29 | 4 | yes |
| 10 | 8 | 40/43 | 206/43 | 4 | **no** |
| 3 | 8 | 24/37 | 146/37 | 4 | yes |
| 6 | 8 | 24/29 | 130/29 | 4 | **no** |

Key `probe_separation`: the verdict flips on **frequency alone** at
`flips_at_fixed_k` = `[6, 10]` and on **size alone** at `flips_at_fixed_w` =
`['8']`. Neither variable is a proxy for the other — a large residual asked
rarely and a small one asked constantly are different machines, and both are in
the table.

**Not over-read.** Key `frequency_obligations`: all six obligations sit on the
paying side (`f` from 0 to 3/8, all below 2/3). The non-paying regime is
exhibited by the sweep, not by any obligation in this world. The threshold is
*located*, not straddled by the examples.

### 3c. The index cost law

Arranging the store costs 2 per item and cuts a hit to 1, so it pays iff
`N*f*(k-1) > INDEX_BUILD*k`, with `f` the query-weighted frequency. Key
`index_law` (12 cells; four shown):

| `k` | `w` | `f` | N=8 | N=64 | N=512 |
|---:|---:|---:|---|---|---|
| 1 | 8 | 8/23 | no | no | **no** |
| 3 | 1/8 | 3/107 | no | no | yes |
| 3 | 8 | 24/37 | **yes** | yes | yes |
| 10 | 1/8 | 5/29 | no | yes | yes |

Key `index_separation_fixed_k` = `[3]`: at N=64 the verdict flips on frequency
alone. A one-item store is never worth arranging at any volume or frequency —
that is the `(k-1)` factor, not a price. At N=8 a large rarely-asked store
(`k=10, w=1/8`) and a small constantly-asked one (`k=3, w=8`) fall on opposite
sides, which is the separation the law needs.

## 4. The update law under changing knowledge

Key `repair`, on `residual_distinct`:

| change lands | store repair | description repair | cheaper |
|---|---:|---:|---|
| inside the residual | 1 | 4 | store |
| in the covered region | 1 | **24** | store |

> **A store's repair cost does not depend on where the change landed; a
> description's does.** Editing an entry is 1 either way; a change in the region
> the *rule* covers invalidates the rule and costs 24 to re-derive.

### 4b. CORRECTED against the obvious expectation

The expectation was that patching must eventually force re-derivation, since
each patch grows the residual and raises `f`. Key `drift`:

| `d` | `k_d` | `f_d` | serve gap | fresh rule | re-derive | `N*` |
|---:|---:|---:|---:|---|---:|---:|
| 0 | 3 | 3/16 | 25/16 | `sum_mod3` | 20 | 64/5 |
| 2 | 5 | 5/16 | 31/16 | `sum_mod3` | 28 | 448/31 |
| 4 | 7 | 7/16 | 37/16 | `one_if>=4` | 35 | 560/37 |
| 5 | 8 | 1/2 | 5/2 | `one_if>=4` | 39 | 78/5 |
| 6 | 9 | 9/16 | 43/16 | `one_if>=4` | 39 | **624/43** |

**The break-even volume does not fall as the store grows.** It ends higher than
it began (64/5 → 624/43) **and is not monotone** — it peaks at 78/5 at `d=5`
then dips, because the best fresh rule changes from `sum_mod3` to `one_if>=4` at
`d=4`, after which the re-derivation cost goes flat (39 → 39) while the serve
gap keeps climbing.

> Accumulated change degrades the thing you would re-derive **into** as much as
> it degrades the patched machine. "Patch until it is too messy, then retrain"
> is **false** here: the mess is in the world, not in the store.

Key `drift_winners`: at every drift level N=4 selects `patch` and N=16/64/256
select `re-derive`. **Re-derivation is chosen by query volume, not by drift.**

### 4c. PVR-3 with the twist

B11 keeps an item iff `S < (r-1)(C-U)`. Under change, reuse is capped by the
item's **lifetime** `L` — reuses after the knowledge moved are served wrong —
giving `S < (min(r,L)-1)(C-U)`. Key `pvr3_lifetime`: **7 of 18** rows change
verdict, every one from keep to discard, all at `L=1` or at `L=2` with gap
`C-U = 1`.

Revalidation is no escape: checking an entry against the world on every use
costs what recomputing costs, so `U` rises to `C`, and B11 says nothing is worth
keeping at `U >= C` at any recurrence. **A residual store is viable only where
change announces itself; polling dissolves it.**

Key `staleness`: unmaintained, after 1/3/5 changes the store errs 1/3/5 and the
description errs 1/3/5 — identical. Neither is self-correcting; the store's
whole advantage is that its errors are **addressable one at a time**.

## 5. Caches, closeness-keyed stores, adapters

**Eviction soundness** is the line between a cache and a store. Matched twin,
key `eviction` — same 3 entries, same prices, differing only in whether a
correct rule covers what they hold: over covered inputs, 0 errors held and
**0 after eviction**; over residual inputs, 0 held and **3 after eviction**.

> **A cache is a holding whose miss is survivable** — not a policy choice but a
> property of coverage. Cached answers are recomputable, so eviction costs time;
> a residual holding covers what the description cannot produce, so eviction
> costs correctness.

**Exact versus closest key.** Key `closest_key`: `smooth_residual` needs 1 key
for 5 residual inputs and `residual_collapse` 1 for 3, while `residual_distinct`
needs all 3. *Positive control*: the identical capped subset search that yields
no saving on `residual_distinct` yields 1-for-5 on `smooth_residual`, so the
negative is about roughness, not about a search that finds nothing.

**Who attains the minimum.** 48 cells over (obligation, `N`, recompute price
`C`, changes `d`), correctness first then cost. Ties are reported as ties: two
holdings answering identically at identical cost are one machine under two
names, and letting a sort order choose would manufacture a verdict. Keys
`comparison_tally` / `comparison_outright`:

| holding | attains min | outright |
|---|---:|---:|
| `absorb_all` | 26 | 26 |
| `store_by_closeness` | 22 | 12 |
| `store_residual` | 10 | **0** |
| `cache_only` | 1 | **0** |

Key `comparison_cells`: 10 of 48 cells are ties, all 48 served with zero errors.
**`store_residual` never wins outright here** — all ten of its cells tie with
`store_by_closeness`. Exact- and closeness-keyed residual stores are
cost-indistinguishable except where a strict subset exists, where closeness
strictly wins. The residual store's *strict* selection lives in §6, not here.

## 6. Neutral recovery

Key `neutral_vocabulary` records the whole candidate vocabulary — `nothing`,
`the_misses`, `half_the_misses`, `everything`, `same_input`, `closest_input`,
`the_description`, `the_side_list`, `test_first`, `described` — and the banned
substrings `retriev`, `rag`, `index`, `database`, `adapter`, `cache`, `memor`,
with `hits` = `[]` asserted at run time. Two disciplines cost the claim rather
than help it: candidates that *realize* the same machine are collapsed before
scoring (369–379 survive per cell), and remaining ties break **against** the
external holding, so every external selection is strict.

Key `neutral_shapes`: 11 distinct machines over 48 cells.

| selected machine | cells | what it is |
|---|---:|---|
| `-\|the_misses\|same_input\|the_description\|t0` | 11 | memorise everything internally |
| `sum_mod3\|nothing\|same_input\|the_description\|t0` | 7 | no holding — description is exact |
| `sum_mod3\|the_misses\|same_input\|the_side_list\|t1` | 5 | **a residual store** |
| `one_if>=2\|half_the_misses\|closest_input\|the_side_list\|t1` | 5 | a closeness-keyed store |
| `-\|the_misses\|same_input\|the_side_list\|t0` | 4 | a full external table |
| *(6 further shapes)* | 16 | |

Key `neutral_split`: external holdings selected in 20 cells, 14 under change;
internal in 21 cells, only 8 under change. Key `neutral_closest_cells` = 5, and
all five are `smooth_residual` — closeness keying is selected exactly where §5
showed the metric is aligned, and nowhere else.

> Told nothing but mechanisms and prices, the search selects **no holding** when
> the description is exact, an **internal** holding when the residual is small
> and stable and volume is high, and an **external holding keyed on the same
> input, consulted only after a test**, when the knowledge changes. That last
> shape is a residual store, and the search reached it without the word.

## Honest negatives

**`comparison_never_wins` = `[]`.** Every holding attains the minimum somewhere,
so nothing is dead in this price regime — but "attains" includes ties. Two of
the four (`store_residual`, `cache_only`) attain it *only* in ties, and
`cache_only`'s single cell is on `absorbed`, where there is no residual to fail
on. The empty list is weaker than it looks.

**`drift_flips_at_volume` = `[]`.** At no tested volume does accumulated drift
change the patch/re-derive decision. The witness records this and deliberately
does **not** assert on it. A price regime where drift *does* flip the decision
is the more interesting finding and the one intuition expects; gating on its
absence would freeze a negative into a tripwire, so a future discovery would
surface as a regression rather than as a result.

**Three `STORE IS FORCED` verdicts mean *not expressible in two terms*,** not
not expressible. A three-term expression is untested.

## Scope

- 16 inputs of 4 bits, three-valued response, 23-rule class. The third value is
  required for §1 to have content at all.
- The class is deliberately not closed under `(a+b) mod 3`, checked at run time.
- §2's composition search is exhaustive over **one and two** terms only.
- The closest-key subset search is capped at 8 and reports `none <= 8` rather
  than claiming impossibility, following B11.
- §5 and §6 **price** change; they do not re-score correctness after it. §4c's
  staleness table is the only place unmaintained error is counted.
- `incompressible` is one fixed pseudo-random table, not a sample over tables.
  It witnesses that the class has gaps, not how many.
- Query weighting in §3b/3c is a uniform `w` over the whole residual; skew
  *within* the residual is untested.
- Every price is a modelling choice. The **orderings and thresholds** are the
  result; the magnitudes are not. `LOOKUP > PROBE` is the one relation §3b
  needs, and it is stated rather than discovered.

**Falsifier.** Exhibit a residual the class can express where an external store
is still cheaper than a second term; or a holding whose repair cost depends on
where the change landed; or a world where accumulated drift makes re-derivation
more attractive at fixed query volume; or a closeness-keyed holding that covers
a rough residual with a strict subset.
