# Skills, levels, and why hierarchies are shallow — checklist item 10

Date: 2026-09-13. Status: **DERIVATION + EXACT FINITE WITNESS + PHASE SWEEP**. Closes the gap the
coverage audit recorded as: *"only an atlas row and a cited parent; no derivation of action-sequence →
skill chunking, subgoal formation, or hierarchical planning."*

Nothing new is assumed. Two proved results are joined:

* **PVR-3** (`PROOF_SEARCH_VERIFICATION_REUSE_THEOREM_V1.md`) — with `C` the charged derivation, `S` the
  one-time storage and `U` the per-invocation cost, `fresh = rC` against `retain = C + S + (r−1)U`, so
  retention strictly wins iff `S < (r−1)(C−U)`, i.e. **`r > 1 + S/(C−U)`**, and never when `U ≥ C`.
* **The developmental quotient theorem** — the coarsest response-preserving quotient is the unique
  minimal exact representation.

## 1. The chunking law

A **skill is a retained sub-quotient**, and chunking is PVR-3 applied to it. A recurring action or
reasoning sequence should be compiled into a skill exactly when its demand clears

> **`r > 1 + S / (C − U)`**

and never when invoking it costs as much as deriving it. The quotient theorem supplies *what* to
compile, so the unit of chunking is not a heuristic choice.

## 2. Why levels are self-limiting — the derived consequence

Retaining level 1 **lowers the derivation cost of level 2**, because a higher-level sequence is then
assembled from cheap invocations rather than from primitives. But `C` appears in the denominator of the
threshold: lowering `C` shrinks `(C − U)` and therefore **raises** the recurrence a level-2 chunk must
clear.

**Each level is harder to justify than the one beneath it.** Depth is self-limiting, and the first level
should capture most of the available benefit. That is a prediction, and it is what the sweep shows.

## 3. Exact witness (`gmi_microscope/hierarchy_witness.py`)

Five weighted tasks over primitive actions, complete enumeration of every candidate chunk set.

| scheme | cost | saving |
|---|---:|---:|
| flat, no chunking | 72 | — |
| best one level (`abc`, `abd`, `abe`) | 33 | **39** |
| best two levels (`abcabd`, `abdabc`, `abc`, `abe`) | 31 | 41 |

**The second level adds 2 against the first level's 39.** The short chunks are shared across every task;
the long ones are task-specific and must earn their storage from one context's recurrence alone.

## 4. Phase sweep (`gmi_microscope/hierarchy_phase_sweep.py`)

Storage price `S` against recurrence, exhaustive at every cell:

| `S` \ recurrence | 2 | 4 | 8 | 16 |
|---|---:|---:|---:|---:|
| 1 | 13.5 % | 13.2 % | 15.3 % | 19.5 % |
| 2 | 11.8 % | 12.0 % | 14.6 % | 19.2 % |
| 3 | 12.9 % | 10.6 % | 13.9 % | 18.9 % |
| 6 | 18.2 % | 10.5 % | 11.4 % | 17.9 % |
| 10 | **0.0 %** | 15.4 % | 13.8 % | 19.7 % |

(cells give the second level's gain as a percentage of the first level's)

Three readings:

* **The second level's contribution rises with recurrence** at every storage price — at `S = 1` it goes
  5 → 7 → 13 → 29 in absolute charge as recurrence goes 2 → 16.
* **It is a minority everywhere**, 10–20 % of what the first level delivers, across the entire swept
  range. The prediction in §2 holds.
* **There is a clean boundary**: at `S = 10, r = 2` the second level adds **exactly zero**. Expensive
  storage plus low recurrence makes depth worthless, not merely marginal.

## 5. What this settles, and what it does not

**Settles:** when a sequence becomes a skill (PVR-3's threshold on a quotient), why levels stack at all
(shared sub-sequences serving many contexts), and **why hierarchies are shallow** — each level raises the
bar for the next, which is derived rather than observed.

**Does not settle:** *subgoal* formation. A subgoal is naturally the entry state from which a retained
skill is valid, which connects to item 11's gap, but that identification is not proved here. Nor is
hierarchical *planning* — this is about compiling recurring structure, not about search over futures.

**Load-bearing assumptions:** PVR-3's own — no invalidation or eviction, stable validity, constant
independent costs. Under eviction the threshold rises and shallow depth is reinforced, so the conclusion
is not fragile in that direction; under shared storage between levels it could weaken.

**Falsifier:** a cost regime, inside PVR-3's stated assumptions, where the second level delivers a
*majority* of the total saving. That would break the denominator argument in §2 rather than this
assembly.
