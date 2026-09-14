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
| 10 symbiosis | **open** — nothing measures mutual benefit; the taxonomy has no cooperative outcome |
| 11 resource partitioning | **open** — the pool is shared but partitioning is never measured |
| 12 abundance from ecology | **open** — no frequency prediction exists |
| 13 morphology transitions under repricing | **open** — pools vary, but no morphology is tracked across them |
| 16 multi-species ecologies | **open** — this is strictly **pairwise**; three or more competitors are untested |

Box 16 is the load-bearing gap. Every result above is a two-body contest, and pairwise exclusion does not
determine multi-species outcomes — rock-paper-scissors cycles are the standard counterexample, and nothing
here rules one out. **Claiming section G's ecology closed on pairwise evidence would be wrong**, and the
distinction is exactly the one boxes 8–9 versus box 16 are drawing.

## 6  A gap in the guarding, now fixed

This result — a registered prediction, 192 cells, an invariance control — had **no CI pin of any kind**. It
could have drifted silently. Three pins now assert the prediction still holds, that disagreement is neither
zero nor total and occurs off-diagonal, that coexistence stays the exception with both exclusion directions
occurring, and that remint invariance holds.

Reproduction is **not** wired: `invasion.py` is not a single-file witness and does not run under the
temp-directory harness. The pins guard the claims, not the derivation of the receipt. That is weaker than the
corpus's other guards and is recorded here rather than glossed.
