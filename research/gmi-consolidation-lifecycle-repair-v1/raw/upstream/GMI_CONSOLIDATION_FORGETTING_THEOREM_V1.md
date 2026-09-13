# Consolidation versus forgetting, derived — checklist item 7

Date: 2026-09-13. Status: **DERIVATION + EXACT FINITE WITNESS**. Closes the gap the coverage audit
recorded as: *"replay appears once, as an unexplained remedy for catastrophic forgetting; no
consolidation-vs-forgetting condition anywhere."*

Nothing new is assumed. The condition is read off `CONTINUAL_SEMANTIC_RETENTION_THEOREM_V1.md` (CSR-1)
and `DEVELOPMENTAL_QUOTIENT_THEOREM_V1.md`, which were already proved and never connected.

## 1. The lever already in CSR-1

For retained obligations `Ω_1…Ω_t`, histories fall into retention-equivalence classes
`h ≡_t h' ⟺ Σ_t(h) = Σ_t(h')`, and CSR-1 fixes the minimum persistent memory **exactly**:

> `M*_t = N_t` states, i.e. `s*_t = ⌈log₂ N_t⌉` bits, with `N_{t+1} ≥ N_t`.

and its two boundary readings:

* `N_{t+1} = N_t` — the new obligation is **already a function of the retained semantic state**, so it
  costs **zero** additional capacity;
* `N_{t+1} > N_t` — genuinely new distinctions, and any fixed memory with fewer than `N_{t+1}` states
  **must fail some obligation unless another side channel carries the missing distinction.**

That last clause is where replay lives, and naming it is the whole derivation: **replay is the side
channel.** Raw experience re-derives a distinction at evaluation time instead of holding it persistently.

## 2. The three-way condition

Let `C` be the machine's persistent capacity in states, and let `D` be the experience that generates the
distinctions.

| regime | condition | what the machine should do |
|---|---|---|
| **consolidate** | `N_t ≤ C` and naive per-task storage `t > ⌈log₂ N_t⌉` | compress to the quotient; the saving is exactly `t − ⌈log₂ N_t⌉` bits, and it is **free** whenever `N` stopped growing |
| **replay** | `N_t > C` but `D` is cheaper to hold than `N_t` states, and recomputation is affordable | keep raw experience, re-derive the distinction on demand |
| **forget** | `N_t > C` and replay's charged cost exceeds the retained obligations' value | merge equivalence classes; CSR-1 says exactly which distinctions are lost |

The quotient theorem supplies the consolidation *target*: the coarsest response-preserving quotient is the
minimal exact representation, so "compress to the quotient" is not a heuristic — it is the unique minimum,
and `N_t` is its size.

## 3. Exact finite witness

`gmi_microscope/consolidation_witness.py`, receipt `STAGE_CONSOLIDATION_WITNESS_V1.json`. Complete
enumeration over `|H| = 16` histories; every quantity computed, none estimated.

| regime | tasks | `N_T` | min bits | naive bits | **saving** | forgetting forced? |
|---|---|---:|---:|---:|---:|---|
| **A independent** | 4 independent bits | 16 | 4 | 4 | **0** | yes, at task 4 (capacity 3 bits) |
| **B redundant** | 2 independent, then XOR, negation, OR of them | 4 | 2 | 5 | **3** | no |
| **C mixed** | 2 independent, 2 derived, 1 new, 1 derived | 8 | 3 | 6 | **3** | yes, at task 5 (capacity 2 bits) |

Read directly:

* **A shows consolidation cannot always help.** Every task adds distinctions, `N_t` doubles, and the
  minimum equals the naive cost at every step. Compression saves nothing because there is nothing
  redundant. Forgetting is then forced by capacity alone.
* **B shows when consolidation is free.** After task 2 the retained width stops growing: tasks 3, 4 and 5
  each add **zero** new distinctions because each is a function of the first two. Naive storage grows to
  5 bits while the exact minimum stays at 2. The 3-bit saving is not an approximation.
* **C shows the two interleaving.** A saving of 3 bits accumulates, and forgetting is *still* forced at
  task 5, because one genuinely new obligation pushes `N` past a 2-bit capacity that the earlier
  redundancy had been hiding.

## 4. What this does and does not settle

**Settles:** when consolidation pays and by exactly how much; when it is free; when forgetting is forced;
and what replay is *for* — it is the side channel CSR-1 already required but never named.

**Does not settle:** replay *dynamics* — how much to replay, in what order, and at what schedule. That is
a policy question over the charged meter, not a capacity question, and it is the natural next step.
Also untouched: the working/episodic/semantic/procedural partition (item 6), which this does not address.

**Load-bearing assumption:** exact retention. CSR-1's `M*_t = N_t` is the minimum for answering *every*
retained obligation exactly. Under approximate retention the minimum drops and the three-way condition
relaxes into a rate-distortion trade-off that this document does not derive.

**Falsifier:** exhibit a task sequence with `N_{t+1} = N_t` where exact retention nevertheless requires
more than `⌈log₂ N_t⌉` bits, or a capacity `C ≥ N_t` where exact retention still fails. Either would break
CSR-1 rather than this assembly.
