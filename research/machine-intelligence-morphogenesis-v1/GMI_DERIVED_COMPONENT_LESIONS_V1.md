# Lesioning derived cognitive components — checklist item 29

Date: 2026-09-14 (revised). Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/lesion_witness.py`.
Receipt: `microscopes/results/STAGE_COMPONENT_LESIONS_V1.json`.
Verified in CI by `test_gmi_derivation_witness_reproduction.py`.

Closes the gap the coverage audit recorded as: *"the corpus ablates its own
search basis and information channels, not derived cognitive components — there
is no 'remove memory / attention / planning → predicted deficit' family."*

**Revision note.** The first version of this document reported measurements
with no backing witness — nothing could re-derive its numbers. This revision
supplies the witness, which reproduces the procedural figure exactly, corrects
two figures that were not reproducible, adds the two components the item names
that were missing (planning and retrieval), and withdraws an overclaim about
the dissociation. Details in the last section.

## The six components

Each is derived elsewhere in this corpus, so each can be removed and its
deficit **computed from the law that derived it**, then measured by re-running
the same enumeration with the component disabled.

| component | what it is | the law that fixes its deficit |
|---|---|---|
| procedural | chunking | PVR-3 reuse threshold |
| semantic | consolidation | CSR-1 retention width |
| episodic | replay side channel | CSR-1 capacity shortfall |
| working | within-event state | serving requires it at all |
| planning | optimal segmentation | the value-aware stopping rule |
| retrieval | indexed lookup | the `U` term of PVR-3 |

Intact baseline on the registered task set: serving costs **29** with the
optimal chunk set `{abcab, abdabc, abeabc}`, against **72** with no chunks.

## Predictions and measurements

| lesion | derived prediction | measured | match |
|---|---|---|---|
| **procedural** | serving reverts to flat, 72 | 72, ratio **2.4828**, **+148.3 %** | ✅ |
| **retrieval** | `U` rises from 1 to `\|K\|`=3, giving 53 | 53, **+24** serving | ✅ |
| **planning** | greedy costs 4 where optimal costs 2 | 4, deficit **2** | ✅ |
| **semantic** | naive width 5 bits against consolidated 2 | 2 → 5 bits, **+150 %** | ✅ |
| **episodic** | `N_t − capacity` = 8 distinctions lost | **8 of 16**, 50 % | ✅ |
| **working** | no multi-step task serveable | **0 of 5**, total not graded | ✅ |

Predictions are arithmetic consequences of the laws, computed in the same run
before the measurements. They are **derived, not prospective**: agreement
confirms internal consistency, it does not supply independent evidence.

## Every lesion is conditional

A lesion that hurts in every setting says nothing about when the component is
needed. All six are checked in more than one regime, and the witness aborts if
any turns out to be unconditional.

**Semantic.** Consolidation saves nothing when nothing is redundant:

| regime | consolidated | naive | extra |
|---|---:|---:|---:|
| A_independent | 4 | 4 | **+0** |
| B_redundant | 2 | 5 | +3 |
| C_mixed | 3 | 6 | +3 |

**Episodic.** Distinctions are lost exactly when capacity is exceeded:

| regime | final `N` | capacity | lost |
|---|---:|---:|---:|
| A_independent | 16 | 8 | 8 (50 %) |
| B_redundant | 4 | 8 | **0** |
| C_mixed | 8 | 4 | 4 (50 %) |

**Planning.** This is the sharpest of the three. On the registered task set the
planning lesion costs **exactly nothing** — greedy longest-match is already
optimal, because the optimal chunks do not interfere. Build a chunk set where
a long early match blocks a better covering (`abcdefgh` with
`{abcde, ab, cdefgh}`) and greedy costs 4 against an optimal 2.

> **Lookahead earns its cost only when actions interfere with each other.**
> Where they do not, a planning module is pure overhead — and the deficit from
> removing it is zero, not small.

That is the same shape as the rest of the corpus: machinery pays only under a
stated condition, never generically.

## Three deficit shapes

Removing procedural memory costs **+43 serving and zero retention**; removing
semantic memory costs **+3 bits of retention and zero serving**. That is a
double dissociation, and here it is *derived* rather than observed: the two
lesions load on orthogonal ledger coordinates because different conditions
produced them — PVR-3's reuse threshold for one, CSR-1's retention width for
the other. This independently strengthens the partition in
`GMI_MEMORY_REGIME_PARTITION_V1.md`, which had argued distinctness from four
different growth laws.

The episodic and working lesions differ in *shape* again. Episodic loss is
**graded**, set by the gap between `N_t` and capacity. Working loss is
**total**: within-event state is not a store that can be made smaller, so
without it no multi-step event is serveable at all.

## Scope, stated plainly

**The double dissociation is a two-component claim, not a four-component one.**
Retrieval also moves the serving coordinate (+24), so *three* deficits land on
one axis. Three deficits on one coordinate are not three systems. Only the
procedural/semantic pair dissociates; retrieval and planning are distinguished
from procedural by their **mechanism**, not by an orthogonal coordinate. The
witness records which lesions share a coordinate so this cannot be overstated.

**These are derived components inside this accounting**, not biological
structures. No claim here predicts any neuropsychological finding; items 25–28
remain the other lane's, and a comparison would need a biological half this
corpus does not have.

**Falsifier.** Lesioning one derived component moves the ledger coordinate
assigned to another — a procedural lesion that changes retention width, or a
semantic lesion that changes serving cost. Either would show the components are
not separately realised. The witness asserts the double dissociation directly,
so this falsifier is checked on every CI run.

## What this revision corrected

| figure | first version | now | status |
|---|---|---|---|
| procedural ratio | 29 → 72, **2.483** | 29 → 72, **2.4828** | **confirmed**, and now reproducible |
| semantic width | 3 → 12 bits, +300 % | 2 → 5 bits (B), 3 → 6 (C), +150 % | **corrected** — 12 matches no regime |
| episodic loss | 4 of 8, 50 % | 4 of 8 in regime C; 8 of 16 in regime A | **confirmed**, regime now named |
| working | unserveable | 0 of 5 tasks | unchanged |
| planning | *absent* | deficit 0 or 2 by regime | **added** |
| retrieval | *absent* | +24 serving | **added** |
| dissociation | "a derived double dissociation" | two components, not four | **narrowed** |

The procedural figure was right all along; it simply had no witness behind it.
The semantic figure was not reproducible from any registered regime and has
been replaced by the computed one.
