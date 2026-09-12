# GMI Stage B2 — Transformer / LLM microfeature phase atlas, EXECUTED (V1)

Status: **EXECUTED AT TIER S — SYNTHETIC EXACT MICROSCOPES AT LAPTOP SCOPE. NOT EVIDENCE ABOUT ANY TRAINED NEURAL
NETWORK.**

Status date: 2026-09-12. Issue #422. Lane ledger: `REVIVAL_LEDGER_B2.jsonl` (reserved id range `RV-377-090` onward,
protocol rule 30). Branch `claude/gmi-stage-b2-atlas`.

Ten rows of stage B2 (`GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md` section 9) were executed as exact charged microscopes
with deterministic receipts under the freeze-before-run protocol: **B2.1, B2.2, B2.4, B2.5, B2.6, B2.7, B2.8, B2.9,
B2.10 and B2.11**. Rows B2.3 and B2.12 were already executed in a parallel lane (`RV-377-056`, `RV-377-055`); the other
eight rows of the stage are untouched by this lane.

**126 of 138 frozen clauses HOLD.** Twelve fail. Every failing clause is scored verbatim, none is deleted or softened,
and the failures are where most of the content is: three of them corrected a claim this programme was carrying.

---

## 0. What this atlas is not

```text
It is NOT evidence about any trained neural network.
It is NOT a measurement of optimization, of training dynamics or of gradient transport: no learning is
    run anywhere in these ten rows, and the two protocol endpoints that ask for it (B2.8's "optimization
    success" and B2.10's "optimization stability") are DECLARED NOT EXECUTED in their receipts rather than
    proxied by a forward quantity with a suggestive name.
It is NOT a ranking of architectures. B2 output is a phase atlas, as the protocol says, not one winner.
A count of configurations here is NEVER a count of species and never a count of forms (protocol rule 29).
```

Every row is a `SYNTHETIC_EXACT_MICROSCOPE__LAPTOP_SCOPE__NOT_EMPIRICAL_NEURAL_EVIDENCE`. Where a row also contains a
closed-form identity, that part carries the separate kind `MATH_IMPLEMENTATION_CHECK__NOT_EMPIRICAL_NEURAL_EVIDENCE`
and the receipt states in terms that it is not evidence for the measured part (rows B2.6 and B2.10).

## 1. The instrument, and the rules it carries

All ten rows run on `gmi_microscope/b2_common.py`, which carries five protocol rules as executable helpers rather than
as prose, so a receipt either calls them or visibly does not.

| rule | how it is carried | where it bit |
|---|---|---|
| **17** | every receipt states the frontier rule its clauses are evaluated under | all ten |
| **19** | every capability is the **parent-maximal** reader of the state the arm carries, never a fitted one; every opponent is built adversarially | B2.8's scale-controlled opponent overturned the row; B2.4's arbitrary content-based scorer; B2.1's best-function-of-the-bag |
| **21** *(as narrowed by `RV-377-073`)* | `charged_serve_audit`: no admissible row may serve state **written during development** without a charged operation; a constant-answer row legitimately costs nothing | all ten; the work order quoted the ORIGINAL wording, which the gap ledger records as `FALSIFIED_AND_REPLACED` — see §4 |
| **22** | `constant_control`: a hindsight-optimal **constant-answer** row in every cell, and clauses evaluated only where it fails | B2.6 had to move to a threshold declared *relative* to the control after an absolute one VOIDED a cell |
| **24** | `gate_claim`: every gate claim enumerates the **representations of the carrier's state** the alphabet admits and tests the strongest at the gated setting | B2.6 and B2.8 both turned on it; without it B2.8 would have reported a depth gate that is not there |
| **28 / DG-2** | `frontier_set`: every crossover computed **first** in exact rationals, one shared grid built to reach 4× the largest, `max(grid) >= 2*max(crossover)` asserted per context, and the **per-row cost coordinates** carried in the receipt | all ten; graded SAFE by `grid_audit.py` |
| **29** | `census`: no count travels without its (alphabet, servability filter, ecology) triple | B2.1, B2.4, B2.7, B2.11 |

Arithmetic is exact throughout: `fractions.Fraction` where the quantity is combinatorial or rational, and the
**registered 8-bit fixed-point universe** of `gmi_microscope/core.py` (`TOTAL_BITS = 8`, `FRAC_BITS = 4`, with its
saturation and its declared `MUL` rounding) where the quantity is an activation — rows B2.7, B2.8, B2.9 and B2.10.
There is **no randomness anywhere in stage B2** and no tolerance anywhere except in two explicitly labelled float
checks. Charged costs in the 8-bit rows are **metered on `core.Machine` under basis `B0`**, not counted by hand.

`gmi_microscope/b2_audit.py` runs `gmi_microscope/grid_audit.py` over every receipt of this lane before it is
committed; the verdicts are in `microscopes/results/STAGE_B2_DG2_AUDIT_V1.json`.

---

## 2. The ten rows

### B2.1 tokenizer granularity — `RV-377-090`, 17 of 18, receipt `STAGE_B2_01_TOKENIZER_V1.json` (`2b61c875…`)

**Measured.** Three declared morphologies (semantic units of length 1, 2 and 3 symbols), 512 enumerated strings each,
nine tokenizer rows (a BPE merge ladder at k = 0…24 plus a declared unit-aligned arm), two worlds (original and
reminted). Capability is the hindsight-optimal function of the token multiset — the parent-maximal bag reader.

**Numbers.** Minimal exact vocabulary size 8, 16, 16 entries. Character-level capability 1, 3/8, 3/8. At the **same**
V = 16 the unit-aligned tokenizer is exact and linearly realizable on both multi-symbol morphologies while the
frequency-learned one is neither (127/128 and 15/16, linear system inconsistent). Frequency-learned merge tables that
contain **every** unit as a merge are still unit-aligned on as little as 147/256 of the corpus, because merges apply
greedily left to right and a cross-boundary occurrence is consumed first. Linear sample efficiency along the ladder:
8, 10, 28, 64, 64, 89, 121, 169 labelled examples. The cost-optimal exact vocabulary moves 8 → 32 entries between
H = 1 and H = 1024, and differs across morphologies and price vectors.

**C17 FAILS as frozen and as predicted:** the coarsest frequency-learned row co-occupies frontier cells with the
unit-aligned row on the digram morphology.

**Claim level** `EMPIRICALLY_SUPPORTED_AT_TIER_S`. **Ceiling:** three declared synthetic corpora, one BPE rule, one
reader class, four price vectors; "no universal optimum" is a statement about *these* morphologies and *these* prices.
**Registry:** `TF-001`, `TF-002` moved (claim NARROWED from size to alignment); `TF-003`, `TF-004` deliberately not.

### B2.2 positional necessity and geometry — `RV-377-091`, 11 of 13, receipt `STAGE_B2_02_POSITION_V1.json` (`f39fa551…`)

**Measured.** Four obligations × seven lengths × eleven declared position representations, all 2^n histories
enumerated. TM-1 is *measured* here, not re-proved: the parent-maximal permutation-invariant encoder (the full token
multiset) is exact on the invariant obligation at every length and inexact on all three order-dependent ones.

**Three resolution thresholds, separately measured.** A cyclic code of period P is exact exactly while n ≤ P. A
saturating relative code of reach R serves a distance-d obligation **iff R ≥ d + 1** — reaching the obligation's own
distance is not enough. A bounded absolute table with P codes and one out-of-range bucket resolves **P + 1** positions.

**C6 FAILS and the refined form is exact.** The frozen threshold was n ≤ P; the measured one is n ≤ P + 1, because a
**singleton out-of-range bucket is itself a position code**. Any capacity threshold stated on the code count alone is
off by one. **C7b FAILS at exactly the predicted place**, a boundary effect at the shortest length.

**The extrapolation law is a price dichotomy, not a ranking:** exactly two of eleven representations are exact on
every task at every length, and they pay in different currencies — a description linear in the largest served length,
or a serve cost quadratic in the length (20 against 55 charged ops per query at n = 10).

**Registry:** `TF-005` (CORRECTED), `TF-007`, `TF-008` moved; `TF-006` and `TF-044` deliberately not.

### B2.4 head factorization — `RV-377-092`, 14 of 14 GREEN, receipt `STAGE_B2_04_HEADS_V1.json` (`9918bf1c…`)

**Measured.** 144 cells: four feature representations × six relation sets × three sequence lengths × two edge budgets.
A head is one **content-based** routing factor — an arbitrary score function of the (query feature, source feature)
pair, which is the parent-maximal content-based scorer — and realizability is decided exactly by topological sort on a
finite constraint graph.

**Numbers.** The minimal exact head count is **identical at k = 4, 6 and 8 in every one of the 144 cells**: sequence
length moves it nowhere. It equals the counting bound ⌈multiplicity / budget⌉ in every servable cell under every
representation, including one whose score cannot see the query's content. A relation declared twice costs nothing.
Under an absolute-position representation the ladder is 1, 2, 3, 4 heads at budget 1 and 1, 1, 2, 2 at budget 2.

**Servability is entirely the representation's**, and the blocking mechanism is exhibited per cell: a content-only
representation gives a required and a non-required source the same feature pair; a relative-offset representation makes
one offset class required at one query and forbidden at another. **Relative and absolute representations are
INCOMPARABLE** — each serves a relation the other cannot.

**Ceiling:** the arbitrary content-based score makes every head count an **upper bound** on a rank-bounded head's
requirement, never a lower one. The disclosed calibration that *did* bound the rank found zero realizers at any length.
**Registry:** `TF-016`, `TF-017` moved; `TF-011` not (moved by B2.5 instead), `TF-010` already at tier S.

### B2.5 MHA → GQA → MQA — `RV-377-093`, 13 of 13 GREEN, receipt `STAGE_B2_05_KVSHARING_V1.json` (`4756775c…`)

**Measured.** 90 cells, 960 frontier contexts. Every partition of the query heads and every stored key/value subset is
enumerated and the hindsight optimum taken, so a reported quality loss is a loss **no grouping could have avoided**.

**TM-7 confirmed and RELOCATED.** Adequacy under sharing is a **stored WIDTH** property, not a map-identity one: on the
three-kind portfolio the minimal exact H_kv falls 3 → 1 as the stored key cap goes 1 → 3, so MQA becomes exact on a
heterogeneous portfolio by widening the shared key alone. At the tightest cap the minimal exact H_kv equals the
measured KV relation heterogeneity exactly (1, 2, 3, 4), and MQA scores 1, 1/2, 1/2, 1/4 of query heads.

**Against a formula this programme was carrying: cache is NOT proportional to H_kv** once per-group widths are
measured. On the four-kind portfolio at width caps (2, 2) and n = 16 the caches at H_kv = 1, 2, 3, 4 are **192, 448,
448 and 512** elements — merging four groups into two saves 64 of 512, and three into two saves nothing. TMT-13's
`2 L n d H_kv` is the equal-width special case.

Sequence length moves the minimal ratio nowhere in any of the 90 cells. At zero memory price every exact and feasible
ratio **ties**, so the whole MHA/GQA/MQA question is created by the memory price.

**Registry:** `TF-018` (RELOCATED), `TF-011` moved; `TF-047` keeps `PROVED_AT_SCOPE` and records the equal-width
condition; `TF-048` deliberately not moved.

### B2.6 softmax entropy/temperature — `RV-377-094`, 14 of 14 GREEN, receipt `STAGE_B2_06_SOFTMAX_V1.json` (`3f822d71…`)

**Two kinds of result, labelled separately.** C1 is a `MATH_IMPLEMENTATION_CHECK` of the TM-3 variational identity for
the **dyadic** kernel (float64, declared tolerance 1e-9, worst grid gap 0.0) and is explicitly not evidence for the
thirteen measured clauses, which are exact rationals with no tolerance.

**The response law.** The optimal temperature at full materialization moves **0 → 2 → 4 → ∞** as ambiguity goes
1 → 2 → 4 → 8.

**The rule-24 gate, which is the sharpest result here.** At **one** word width — the registered 8 bits — the
**log-domain** weight recovers the exact optimum at all four ambiguity levels and the **linear** weight does not,
returning 0, 2, 1, ∞ and missing at ambiguity 4 by two grid steps. That is `RV-377-075`'s invariant reproduced at a
second, independent point of the atlas and on a different kind of quantity.

**Two further laws the protocol text does not contain.** The value of routing over a hindsight-optimal constant
collapses with ambiguity — 1.000, 0.543, 0.296, **0.034** of the control's own error — and **ambiguity forces
materialization**, the cheapest adequate top-κ rising 1, 1, 2, 8. The regime where routing is worth its cost is the
low-ambiguity regime, and it is cheapest there.

**Registry:** `TF-013`, `TF-038` moved; `TF-012` and `TF-037` deliberately not.

### B2.7 MLP width/gating — `RV-377-095`, 15 of 15 GREEN, receipt `STAGE_B2_07_MLP_V1.json` (`eda0ddfb…`)

**Measured** in the registered 8-bit universe, with each arm's realizable class **enumerated in full** at each width.

**The separation the row asks for is exact:** charged routing is **2 operations per query for every arm at every
width**, so every difference is the local transform and nothing else.

**Width buys breakpoints** — minimal rectified width 1 and 2 for one- and two-breakpoint targets, with the enumerated
class growing 43 → 873 → 10 819 → 465 179 functions. **Gating buys the product** — no rectified sum of width up to 4
reaches the bilinear target (12/25, 3/5, 18/25, 21/25 and still climbing) while the gated arm reaches it at width 2.
**And the gate is bought, not free:** 18 charged local-transform operations per query against 10 at width 1, 36 against
20 at width 2. That answers `TF-025`'s standing demand for a matched-cost control in the same units as the benefit.

**The negative result:** content-conditioned transport (`x if y > 0 else 0`) is reached by **no** declared arm at any
declared width, ceilings 17/25, 21/25, 22/25 — although `SEL` is a primitive of the registered universe. An arm
ladder's expressive reach is a property of the ladder, not of the universe it is built in.

**Ceiling:** one coefficient alphabet, one 25-point grid, widths capped at 4 and 2; every "does not reach" is an exact
bound **at those widths over that alphabet** and never an impossibility proof. **Registry:** `TF-022`, `TF-023`,
`TF-025` moved; `TF-024` deliberately not.

### B2.8 residual connection — `RV-377-096`, 13 of 13 GREEN, receipt `STAGE_B2_08_RESIDUAL_V1.json` (`a321e1c4…`)

**Measured** over all 256 representable states at every setting, five depths × five gains × three perturbations.

**The protocol's own negative control behaves:** at depth 1 and unit gain the plain and residual arms differ by 1/128.
What happens deep is the opposite of what the row expects.

**At unit gain the skip is strictly HARMFUL at every declared depth** — the plain path holds capability 1 and 254
distinct states at all five depths while the residual path falls 127/128, 3/4, 9/16, 129/256, 1/2. And the
parent-maximal opponent rule 24 requires of a depth gate — a plain path with per-layer scale control and **no skip** —
beats the residual arm at depth 16 at **every one of the five declared gains**, and is depth-invariant in the
contractive regime. The residual arm at depth 16 occupies **no** frontier cell at any price.

**The two failure modes are different and measurably so.** In the contractive regime the plain path collapses
129 → 65 → 17 → 2 → 1 distinct states with saturated fraction exactly 0 and a perturbation response of exactly 0 LSBs
(underflow); the residual path ends with over half its states pinned at a rail (saturation). In this universe **the
skip is a scale amplifier of gain 1 + g, not an identity path**.

**A depth claim and a precision claim fail the same way.** `RV-377-075` showed a precision gate is a claim about a
representation; this shows the same for a depth gate. Without the scale-controlled arm this row would have reported a
depth gate that is not there.

**Declared NOT executed:** optimization success, and gradient transport — the argument the parent literature actually
makes. `TF-026`'s claim is **SPLIT** accordingly. **Registry:** `TF-026`, `TF-027` moved; `TF-031` not.

### B2.9 normalization — `RV-377-097`, 10 of 14, receipt `STAGE_B2_09_NORM_V1.json` (`58245aca…`)

**Measured.** Six arms × five depths × four drifts × three precisions, every representable state of every width
enumerated (256, 4 096, 65 536). Precision is a declared **family** whose (8, 4) member *is* `core.py`'s arithmetic,
asserted at import so the registered universe cannot be quietly replaced by a wider one.

**The mediator test is what the row asks for, and it is answerable.**

The naive candidate — the distinct-final-state **count** — **fails both readings**: over 120 pooled rows it takes 31
values, three of which carry more than one capability (largest spread **31/128**), and it is not even monotone (33
distinct states scores 251/256 while 65 scores 191/256). **Which** distinctions survive decides the obligation; **how
many** does not. *(C1, C2 FAIL.)*

The obligation-aware candidate — the fraction of obligation-distinct input pairs the stack does not merge, frozen with
its outcome unknown — **screens off the architecture label completely**: 25 values, largest within-bucket capability
spread **exactly 0**. But capability is **not monotone** in it: it is a **sufficient statistic and not a ranking**.
*(C14 HOLDS, C13 FAILS.)*

**C7 FAILS with its violations named:** widening the precision *lowers* capability for `RMS_BATCH` at unit drift and
depth 1 (1 → 509/512) and for `MAXABS_BATCH` at drift 2 and depth 2 (195/256 → 3087/4096 → 49215/65536), because the
obligation's class boundaries and the batch-estimated scales are both grid-relative.

**C5 licenses every attribution above:** the negative twin with identical arithmetic and a data-independent scale
reproduces the unnormalized arm **exactly** at unit drift, so a normalizer's effect is its data dependence.

**Ceiling, load-bearing:** the state is one-dimensional, so the arms named `CENTER_SCALE` and `RMS` are gauge choices
on a scalar and are **not** the vector operations of those names. **Registry:** `TF-028`, `TF-029` moved (RESTATED);
`TF-031`, `TF-075` not.

### B2.10 pre/post norm — `RV-377-098`, 8 of 11, receipt `STAGE_B2_10_PRENORM_V1.json` (`03924a02…`)

**Two kinds, labelled separately.** C1 is a `MATH_IMPLEMENTATION_CHECK` of the closed forms `(1 + αg/s)^L` and
`((1 + αg)/s)^L` in exact rationals with no quantization; the rest is the quantized measurement.

**"Pre-norm is more stable at depth" is FALSE at the matched scale.** When `s = 1 + αg` the post-norm stack's per-layer
derivative is exactly 1 — an exact isometry — and it scores **251/256** at depth 16 against pre-norm's **1/2**. At
mismatched scales the order reverses: at scale 4 pre-norm scores 7/8, 167/256, 17/32 against post-norm's 1/4
everywhere. **The placement is not the variable; the ratio of the normalizer's scale to the residual accumulation is**,
and what pre-norm buys is *insensitivity* to that ratio, not superiority at it. *(C2, C6 FAIL.)*

**The instrument checks itself:** at unit scale the two placements are literally the same arithmetic and C3 confirms
they are indistinguishable at every depth and residual magnitude. C8 meters them to the **same** charged cost at every
depth, so nothing in the comparison is a cost difference in disguise.

**C7 FAILS and in doing so replicates `RV-377-097`'s C13 in a second ecology:** the obligation-aware mediator is a
sufficient statistic and not an ordered one.

**Declared NOT executed:** optimization stability, the endpoint the row names. **Registry:** `TF-030` moved, with the
bare placement claim recorded as falsified at scope.

### B2.11 context vs recurrence vs retrieval — `RV-377-099`, 11 of 13, receipt `STAGE_B2_11_MEMORY_V1.json` (`37c6b923…`)

**Measured.** Four declared key-value ecologies with mutable facts, every history enumerated; four mechanism families.

**The three mechanisms are priced by three INDEPENDENT properties of the obligation.** Myhill–Nerode class counts
9, 9, 25, 27; minimal exact recurrent widths 4, 4, 5, 5 bits; maximum required depths 3, 4, 3, 3 events; minimal exact
windows 4, 5, 4, 4. Lengthening the history at a **fixed** automaton raises the window's price and leaves the recurrent
state's untouched — that pair is the separation. The class count is **verified** by exhibiting a separating suffix for
every pair of states, not asserted.

**C1 fails by exactly one**, and it is the second time this lane found a boundary slot being part of the capacity: a
window must span the required depth **plus the query event**, as `RV-377-091`'s out-of-range bucket was itself a code.

**C8 is the negative result.** No declared price vector reverses the order: the compressed recurrent state occupies the
frontier **alone** in every ecology at every price, cheapest on description (4–5 bits against 16–20 and 8–12) and on
serve (1 charged operation against 4–5 and 3–4) at once. TM-8's substitutability is realized — every ecology is
servable by at least three of the four families — but its "different burdens" produce a **dominance**, not a frontier.

**The retrieval arm's burden is INVALIDATION**, not retrieval: the negative twin with identical machinery and identical
charged cost scores 47/54, 43/54, 92/125, 683/729 and fails exactly on the overwritten histories.

**Ceiling:** the recurrent arm is an exact automaton state, so its minimal width is a **lower bound** on what a learned
recurrent state would need. **Registry:** `TF-044`, `TF-045`, `TF-046` moved; `TF-047`, `TF-049` not.

---

## 3. The twelve failed clauses, and what each bought

| row | clause | verdict | what it bought |
|---|---|---|---|
| B2.1 | C17 occupancy of the unit-aligned row | FAILS as predicted | the coarsest frequency-learned row does hold frontier cells; the alignment claim is about exactness, not occupancy |
| B2.2 | C6 out-of-range threshold `n ≤ P` | **FAILS, refined form exact** | a singleton saturating bucket **is** a code; the threshold is `n ≤ P + 1` |
| B2.2 | C7b relative reach at `R = d` | FAILS at the shortest length | a boundary effect, not the resolution law |
| B2.9 | C1 strong mediator (count) | FAILS | the architecture label carries information a signal count does not; spread 31/128 |
| B2.9 | C2 weak mediator (count) | FAILS | capability is not even monotone in a signal count |
| B2.9 | C13 refined mediator monotone | **FAILS, outcome unknown at freeze** | the obligation-aware mediator is a sufficient statistic and **not a ranking** |
| B2.9 | C7 precision monotonicity | FAILS | more bits can lower capability, in three named places |
| B2.10 | C2 pre-norm dominance | FAILS | "pre-norm is more stable" is false at the matched scale |
| B2.10 | C6 post-norm monotone in residual magnitude | FAILS | post-norm peaks at the matched point |
| B2.10 | C7 mediator ordering | FAILS | replicates B2.9's C13 in a second ecology |
| B2.11 | C1 window = depth | FAILS by one | the query event occupies a window slot |
| B2.11 | C8 no universal winner | FAILS | there is a **dominance**: the recurrent state occupies every frontier cell at every price |

## 4. Defects found in the programme's existing records

1. **`RV-377-056` (row B2.3) is not auditable by the DG-2 instrument.** `STAGE_B2_03_ROUTING_V1.json` reports a
   frontier only **nested** inside its cells, with no top-level per-row cost coordinates. `grid_audit.py`'s corpus scan
   matches **top-level** keys only, so that receipt was never graded by the DG-2 corpus audit of `RV-377-068` and is
   not gradeable by that instrument now. Protocol rule 28 is satisfied *in substance* there (the per-arm costs are
   printed per cell) and unsatisfied *in form*. Recorded as `UNAUDITABLE_BY_INSTRUMENT` in
   `microscopes/results/STAGE_B2_DG2_AUDIT_V1.json`. No number in `RV-377-056` is in question.

2. **The work order for this lane quoted the superseded wording of protocol rule 21.** It asks for the assertion "no
   admissible row has zero execution cost per query". `GMI_GAP_LEDGER_EXECUTED_V1.md` §5 records that wording as
   `FALSIFIED_AND_REPLACED` by `RV-377-073`: a machine serving a **constant** legitimately costs nothing to run, and
   rule 22 *requires* exactly such a row in every cell. The two rules as written are in direct conflict. Every receipt
   here therefore asserts the **narrowed** rule — no admissible row may serve state *written during development*
   without a charged operation — reports each row's charged serve cost, and reports separately that every zero-cost row
   is a constant-answer row. This is a deviation from the work order, taken deliberately and recorded here.

3. **`TMT-13`'s cache formula is equal-width-conditional.** `2 L n d H_kv` is exact only where every KV group stores
   the same width `d`. With per-group widths measured, the cache is `L n Σ_g (key width + value width)` and is **not**
   proportional to `H_kv` — measured at 192, 448, 448, 512 elements for `H_kv` = 1, 2, 3, 4 in `RV-377-093`. The check
   `X-TMT13` is untouched; it verifies the formula under its own hypothesis.

## 5. Where the receipts are

| artefact | path |
|---|---|
| shared charged instrument | `gmi_microscope/b2_common.py` |
| shared depth stack (B2.8, B2.9, B2.10) | `gmi_microscope/b2_depth.py` |
| row modules | `gmi_microscope/b2_tokenizer.py`, `b2_position.py`, `b2_heads.py`, `b2_kvshare.py`, `b2_softmax.py`, `b2_mlp.py`, `b2_residual.py`, `b2_norm.py`, `b2_prenorm.py`, `b2_memory.py` |
| DG-2 audit driver | `gmi_microscope/b2_audit.py` → `microscopes/results/STAGE_B2_DG2_AUDIT_V1.json` |
| frozen-then-adjudicated records | `REVIVAL_LEDGER_B2.jsonl` (`RV-377-090` … `RV-377-099`) |
| replay tests | `test_gmi_microscope.py`, one per executed row plus the audit |

## 6. Claim boundary

This atlas supports:

```text
ten stage-B2 rows executed as exact charged microscopes, frozen before the run, with deterministic
    receipts and 126 of 138 clauses holding and every failure scored verbatim;
twenty-two registry entries moved to EMPIRICALLY_SUPPORTED_AT_TIER_S, several with the claim
    narrowed, relocated, split or corrected rather than confirmed;
three defects found in the programme's existing records.
```

It does **not** support:

```text
that any of these features is explained;
that any LLM behaviour is predicted by any of these numbers;
that any of it is evidence about a trained neural network;
that the eight rows this lane did not execute (B2.13 through B2.20) have been touched at all.
```
