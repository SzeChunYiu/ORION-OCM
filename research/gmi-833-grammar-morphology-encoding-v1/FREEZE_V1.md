# FREEZE_V1 — `gmi-833-grammar-morphology-encoding-v1`

**Frozen before any implementation file exists in this package.** Git order proves it:
this file is committed alone, in its own commit, before `grammar_morphology_encoding_v1.py`,
`independent_oracle_v1.py`, any adapter, any test and any result blob. (#976 CONFIRMED a
POST_HOC_SUSPECT where a freeze postdated its result by 89 minutes; that failure mode is
structurally excluded here.)

## 0. Pins

- `source_main` = `6590cd998cdc7d60333d3c4ec446ae7757788a4b`
- Issue: SzeChunYiu/ORION-OCM **#833**, Section **B. Full corpus scientific audit**
- Claim ceiling:
  `GMI_833_SEARCH_GRAMMAR_TARGET_ENCODING_IDENTIFICATION_AT_REGISTERED_SCOPE`

### 0.1 The EXACT issue row text this tranche may reconcile (verbatim, one row only)

```
- [ ] Identify search grammars that encode the target morphology.
```

**No neighboring row is earned here.** In particular this tranche does not touch, re-open,
re-close, strengthen or weaken: the cost-model row (`Identify cost models that structurally
force the claimed winner.`), the hidden-macro row (`Identify hidden architecture macros or
privileged operators.`), the encoding-sensitivity row (`Identify claims sensitive to
arbitrary encoding choices.`), the search-algorithm row, or any row of Sections A or C–M.

## 1. Parent ownership (full disclosure in `PARENT_LITERATURE_V1.md`)

This row already has prior state on `main`. It is absorbed, not re-discovered:

1. **#891 `gmi-833-g0-cost-privilege-v1`** owns the boundary. Its `BIAS-1` proves, by a
   same-semantic-coverage non-isometric grammar pair, that family-label blindness plus
   equal semantic coverage do **not** imply representation/search neutrality. Terminal
   `NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE`. **This tranche does
   not attempt to overturn it.** It is cited as the boundary, EARNED-BY-COUNTEREXAMPLE, and
   is used as this tranche's mandatory recall anchor (section 6, V1).
2. **#875 / #863 `gmi-833-g0-grammar-bias-v1`** owns finite G0 description/reachability
   bias and the isometric-relabeling-vs-non-isometric-recoding distinction.
3. **#976 `gmi-833-corpus-passes-v2-v1`, `PASS_L49_L50_L53_V1.md` § "L48-SCREEN"** is the
   direct prior state of *this row*: identification-only, box explicitly NOT ticked. It
   established (a) 0 confirmed grammar-target encodings in the 27 A1-denylist hit packages,
   (b) that the ≤138 (refined 109) no-signature packages are where semantic target-encoding
   **"cannot be excluded lexically"**, and (c) `INSTANCE-AJ9-NOSMUGGLING-SCOPE` (RED/HIGH,
   aj-lane) as the one registered grammar-target instance.
4. **`gmi-833-a2-signature-extension-v1`** (ticket `REV-L50-A2-SIGNATURE-PROGRAMME`) owns the
   *semantic-fingerprint* extension of the lexical route: 148 packages, 1,607 primitive
   blocks, all 31 D2 classes mapped to 9 name-blind families, **0 confirmed collisions**.
5. **`gmi-833-no-smuggling-audit-v1`** owns the A1/A2 machinery and the D1/D2 denylists.

**Named residual contribution of this tranche.** Parents (3) and (4) close the *lexical* and
*semantic-fingerprint* routes and jointly report that the structural question — whether a
grammar's own cost geometry makes its declared target cheapest — is out of their reach.
This tranche supplies exactly that second, independent **structural/cost route**, runs it
exactly (integer arithmetic) over the cost-extractable grammar population, adjudicates every
hit individually, and states the screened-not-adjudicated remainder. Nothing in parents
(1)–(5) is reclaimed.

## 2. Definitions (frozen)

A **search grammar instance** `G` is a finite tuple of *presentations*. Each presentation `p`
carries:
- `leaves(p)` — the finite multiset of **productions** (atomic vocabulary symbols) occurring
  in `p`'s registered serialization;
- `L(p) ∈ ℤ≥0` — the grammar's own registered integer description/search cost;
- `sem(p)` — the grammar's own registered semantic class of `p`.

`P(G) = ⋃_p leaves(p)` is the **production vocabulary**.
`mu_G(s) = min{ L(p) : sem(p) = s }`, and `mu_G(s) = None` when no presentation realizes `s`.
`argmin(G) = { s : mu_G(s) = min_{s'} mu_G(s') }` (ties are kept as a set; never name-broken).

The **declared target morphology** `t(G)` is the semantic class the owning package declares,
**verbatim and file:line-cited, in its own frozen documents**. It is never inferred. A
grammar instance with no such declaration is disposed `NO_DECLARED_TARGET`.

### 2.1 Operational criterion for "encodes the target morphology"

`G` encodes `t` when `G`'s own production set makes `t` reachable at strictly lower
description/search cost than a semantics-preserving alternative — i.e. the answer is
smuggled into the primitive basis.

For a production `q ∈ P(G)` define the **deletion re-encoding**
`G\q = { p ∈ G : q ∉ leaves(p) }`, and
`dep(q) = { s : mu_{G\q}(s) ≠ mu_G(s) }` (a class *depends* on `q`).

`q` is **target-exclusive** iff `dep(q) = { t }`. This is computed from the cost table, not
from names: the criterion is **name-blind**.

- **Tier-1 `ENCODES`** — ∃ target-exclusive `q` with `mu_{G\q}(t) > mu_G(t)` or
  `mu_{G\q}(t) = None`. Sub-kinds:
  - `TARGET_IS_A_PRIMITIVE` — `mu_{G\q}(t) = None`: the target morphology *is* a production
    of the grammar and nothing else needs it. (Strongest form; an infinite cost gap.)
  - `TARGET_SPECIFIC_SHORTCUT` — finite and strictly greater: `q` is a shortcut only `t` uses.
- **Tier-2 `DECISIVE_SELECTION_FLIP`** — additionally `argmin(G) = {t}` and
  `argmin(G\q) ≠ {t}` (or, under R2, `argmin(G') ≠ {t}`). Orthogonal marker; the
  confirmed-leak trigger.

Tier-1 is the row's population and the headline. Tier-2 is the strictly stronger subset.
**Reporting Tier-2 alone would close the row by narrowing its stated meaning and is forbidden.**

`mu = None` is represented by Python `None` with an explicit branch — never by a large
sentinel integer.

## 3. Registered re-encoding generator set R (frozen)

- **R1 `PRODUCTION_DELETION`** — `G\q` for every `q ∈ P(G)`. Semantics-preserving on every
  class that retains coverage; classes that lose coverage are handled by the `None` branch.
- **R2 `NON_ISOMETRIC_REMINT`** — for every ordered pair of distinct semantic classes
  `(s1, s2)` with `|s1| = |s2|`, exchange the cost values along the id-sorted bijection
  `s1 ↔ s2`. Semantic coverage is preserved exactly; the class→cost attachment is not. This
  is #891's BIAS-1 mechanism generalized, and is the generator that must re-find `GA/GB`.
- **R3 `ISOMETRIC_RELABEL`** — bijections of presentation identities preserving semantic
  class, `L`, and `leaves`-multiset structure. **Must yield zero flags.** This is the
  no-alarm control, taken from the corpus's own anchor (#891 ships 6 label permutations and
  720 name-isometries with 0 failures).

R1, R2, R3 are three distinct generators. They are **not** the "two independent routes" of
the closure standard (§7 below) and do not substitute for them.

## 4. Populations (frozen)

### 4.1 `P-LEX` — lexical/definitional route, corpus-wide

Enumerated by the merged, validated `gmi-833-a2-signature-extension-v1` extractor
(`primitive_defining_files`, `extract_blocks`, `VOCAB_RE`, `DEFSTRUCT_RE`), imported and
blob-pinned, never re-implemented (reuse-first). `P-LEX` = every package under `research/`
that is def-anchored **and** whose vocabulary hit includes a *grammar/DSL* token (this row is
about search grammars, not every primitive table).

Detector **D-LEX**: a production name or definition body that is specific to one target
family, using the corpus's **own** registered lexicons — the D1 denylist
(`transformer, self_attention, conv2d, lstm_gate, rag_retriever`, A1-normalized) and the
31-key `D2_MAPPING` — plus each package's own declared family tokens.

**Known false-positive class that MUST be reproduced and excluded by written reason, not by
silence:** the denylist owners themselves. #976 found 12 of 27 A1 hits were the corpus's own
anti-smuggling machinery (`BANNED_MI_PRIMITIVES`, `FORBIDDEN_FAMILY_TOKENS`,
`FORBIDDEN_MACROS`, `forbidden_symbol_substrings`) and 14 were prose citations / registry
bookkeeping.

D-LEX is expected to be a **reproduction** pass, not a discovery pass; parents (3) and (4)
already closed it at 0 confirmed. All discovery power is in D-COST.

### 4.2 `P-COST` — structural/cost route, exact

A package is **cost-extractable** iff (a) it is in `P-LEX`, (b) a finite
`(presentation_id, leaves, L, sem)` table is mechanically recoverable from its own committed
module by a registered adapter in `adapters_v1.py` — each adapter carrying a file:line
citation to the grammar it reads — and (c) it declares a target morphology per §2.

**Pre-registered anchors, both directions, verified before the corpus run:**

| package | required |
|---|---|
| `gmi-cross-grammar-four-family-v1` | IN |
| `gmi-833-g0-cost-privilege-v1` | IN |
| `gmi-833-g0-grammar-growth-v1` | IN |
| `gmi-833-g0-grammar-bias-v1` | IN |
| `gmi-833-corpus-census-v1` | OUT |
| `gmi-833-depgraph-adjudication-v1` | OUT |
| `gmi-833-theory-baseline-v1` | OUT |
| `gmi-833-terminology-migration-v1` | OUT |
| `ocm-prototype` | OUT |
| `programme` | OUT |

Any in-sweep refinement of a population rule is logged **explicitly with anchors** (the
#976 138→109 precedent), never applied silently.

### 4.3 SCREENED-NOT-ADJUDICATED policy

Every package in `P-LEX \ P-COST` is reported with a **named reason**, counted, and never
conflated with "checked and fine". Registered reasons:
`COST_OBJECT_NOT_MECHANICALLY_RECOVERABLE`, `NO_DECLARED_TARGET`, `NO_FINITE_PRESENTATION_SET`.
"Could not check" and "checked and clean" are distinct dispositions with distinct fields.

## 5. Adjudication disposition vocabulary (frozen BEFORE any hit is seen)

Per `(G, t)` pair, exactly one primary disposition:

- `NEUTRAL_AT_REGISTERED_SCOPE` — no target-exclusive production; no R1/R2 re-encoding raises `mu(t)`.
- `ENCODES_DISCLOSED_CHARGED` — Tier-1 hit that the owning package itself declares AND
  charges (registered cost accounting, matched negative control, or an independently
  structured replica grammar). Identified, not a defect.
- `ENCODES_UNDISCLOSED` — Tier-1 hit with no such declaration. **CONFIRMED LEAK**; triggers
  the §8 revival obligation.
- `LOAD_BEARING_SHARED_PRIMITIVE` — deletion makes `t` unreachable but `dep(q) ⊋ {t}`:
  `q` serves other classes too, so it is not target-specific. Excluded false-positive class.
- `NO_DECLARED_TARGET` — screened, see §4.3.
- `SCREEN_FALSE_POSITIVE:<named subclass>` — D-LEX hit refuted by reading; the subclass name
  is recorded (e.g. `DENYLIST_OWNER`, `PROSE_CITATION`, `REGISTRY_BOOKKEEPING`).
- `SCREENED_NOT_ADJUDICATED:<named reason>`.

Orthogonal marker: `DECISIVE_SELECTION_FLIP` (Tier-2).

No disposition may be invented after seeing a hit. If the data demands one, it is added as a
numbered **Amendment** appended to this file in its own commit, before the run that uses it.

## 6. Validation bar — NOTHING is reported before all of these pass

- **V1 ANCHOR (blocking).** The #891 `GA/GB` object must be re-found: under **R2**, at
  `w = (1,1)` with `ALPHA=(1,1), BETA=(3,2)` in `GA`, the selected class must flip
  `ALPHA → BETA`, i.e. `DECISIVE_SELECTION_FLIP`. **If the detector does not re-find this
  instance, the detector is broken and no corpus finding may be emitted.**
- **V2 RECALL (planted, on REAL corpus grammars).** Target-specific shortcut productions are
  planted into real corpus grammar tables (the G0 126-presentation slice; the cross-grammar
  A/B tables). D-COST must catch every plant.
- **V3 NO-ALARM.** (a) R3 isometric relabelings of every `P-COST` grammar → 0 flags;
  (b) a registered clean/neutral grammar → 0 flags.
- **V4 HOSTILES.** Deliberately broken detector variants must be flagged by the test battery:
  name-based (not dep-based) exclusivity; sentinel-integer `mu` instead of `None`;
  `dep(q) ⊇ {t}` instead of `= {t}`; argmin singleton-by-name tie-break; R3 mutated into a
  non-isometry.
- **V5 NULL.** A randomized control of ≥200 re-encodings drawn from the isometry group must
  produce 0 Tier-1 flags.

## 7. Two materially independent implementation routes

`grammar_morphology_encoding_v1.py` (executor, writes `RESULT_V1.json`) and
`independent_oracle_v1.py`, which recomputes `mu`, `dep`, `argmin`, the tiers and the
per-pair dispositions from the frozen grammar dumps **without importing the executor**. The
two receipts must agree field-for-field. (#976 filed 75/91 packages as single-route; this
package must not join them.)

Three distinct "two-route" axes are kept separate and all three are required:
(a) detectors D-LEX ⊥ D-COST, with an agreement/disagreement table;
(b) re-encoding generators R1/R2/R3;
(c) implementation routes executor ⊥ oracle.

## 8. Positivity mandate / revival obligation

- **0 confirmed leaks is a POSITIVE result only if V1–V5 all pass.** An empty result from an
  unvalidated detector is a defect, not a closure.
- For every `ENCODES_UNDISCLOSED`: construct the neutral re-encoding that removes the
  target-specific production, re-run the affected result under it, and report either
  *repaired-and-re-verified* or a precise defect **with a concrete revival ticket carrying
  the exact repair path**. Silent dropping is forbidden.
- Pre-registered, falsifiable predictions (failure of any is reported, not hidden):
  - **PRED-1** `gmi-833-g0-cost-privilege-v1` re-found as Tier-2 under R2 (= V1).
  - **PRED-2** `gmi-833-g0-grammar-bias-v1` disposes `NO_DECLARED_TARGET` (it measures bias;
    it recovers no family). This prediction exists to show the target rule is not rigged.
  - **PRED-3** R3 yields 0 flags on every `P-COST` grammar.
  - **PRED-4** In `gmi-cross-grammar-four-family-v1`, the routing family's `from_input`
    (grammar A) and `branches` (grammar B) are target-exclusive productions whose deletion
    makes `INPUT_INDEXED_ROUTING` unreachable → `TARGET_IS_A_PRIMITIVE`, Tier-1.
  - **PRED-5** D-LEX returns 0 CONFIRMED over `P-LEX`, reproducing the denylist-owner
    false-positive class.

## 9. Arithmetic and environment

Exact integers / `fractions.Fraction` only. **No float appears in any claim.** stdlib only;
`python3 -I -B` and `python3 -I -O -B` clean. Target `python3` 3.8.10 (laptop-billy): no
match statements, no runtime `X | Y` unions, no dict `|` merge; `from __future__ import
annotations` is used for annotations. All sweeps run on laptop-billy; the Mac runs git/gh
only. Every number in the reconciliation line is read out of the committed `RESULT_V1.json`,
never from a shell pipeline's printed count.

## 10. Forbidden promotions (carried verbatim from #891, plus this row's own)

```
G0_UNBIASED
NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY
REPRESENTATION_INVARIANT_COST_UNIVERSALLY
SEARCH_NEUTRALITY_PROVED
ARCHITECTURE_PRIOR_FREE_GRAMMAR
ALL_SCALARIZATIONS_AGREE
COMPLETE_GMI
GRAMMAR_NEUTRALITY_PROVED
NO_GRAMMAR_ENCODES_TARGET_UNIVERSALLY
CORPUS_WIDE_COST_ROUTE_COMPLETE
```

The row asks to **identify**, not to prove neutrality. A 0-confirmed-leak outcome is written
as "identified population, adjudicated, with proven detector power", never as "no grammar
encodes its target".

---

## Amendment A1 — production vocabulary is the STRING-valued atom set

*Committed before the adapters, the executor, the oracle and any run. Reason for the
amendment rather than a silent change: §5 requires it, and the #976 138→109 precedent
requires in-sweep refinements to be logged with anchors.*

§2 defined `leaves(p)` as "the finite multiset of productions (atomic vocabulary symbols)
occurring in `p`'s registered serialization". Applied literally to this corpus's
table-enumerating grammars, that admits **integers** as productions (a state-count `2`, a
weight `-1`). Deleting an integer is a *range restriction*, not a semantics-preserving
re-encoding of a production set, and it would manufacture vacuous `TARGET_IS_A_PRIMITIVE`
hits (e.g. "the recurrent-state class needs state-count ≥ 2").

**A1 (frozen).** `P(G)` = the **string-valued** atomic symbols of the grammar's own
serialization — its *named* productions. Numeric atoms are parameters, not productions.

Consequences, all reported explicitly rather than hidden:

- A grammar whose vocabulary is purely numeric is dispositioned
  `R1_NOT_APPLICABLE:NUMERIC_PARAMETER_SPACE` at the R1 layer and remains fully in scope
  for **R2** and **R3**. It is *not* silently dropped, and `R1_NOT_APPLICABLE` is a
  distinct field from "checked and clean".
- A grammar whose presentations carry no production structure at all (a bare cost table,
  e.g. #891's registered 6-presentation object) is dispositioned
  `R1_NOT_APPLICABLE:NO_PRODUCTION_STRUCTURE`; adapters for such grammars MUST emit
  `leaves = ()` and MUST NOT emit the presentation identity as a pseudo-production.
  Emitting presentation identities as productions would make every singleton class a
  trivial Tier-1 hit; the test battery contains this as **hostile H6**.
- `n_presentations_using(q)` and `n_target_presentations` are recorded on every Tier-1 hit
  so a reader can judge how thin the witness is.
- A production qualifies only when `|P(G)| >= 2`.

**A1 anchors, verified before the corpus run:** in `gmi-cross-grammar-four-family-v1`, the
`local`, `routing` and `storage` grammars must retain a non-empty string vocabulary
(`shared/site/triple/configuration`, `from_input/read/branches`,
`weighted/rows/expression/leaves`), while the `state` grammar A (pure integer tables) must
land in `R1_NOT_APPLICABLE:NUMERIC_PARAMETER_SPACE` and the `state` grammar B (string
expressions `zero/one/s/not_s`) must stay in R1 scope.

---

## Amendment A2 — R1 covers the FULL macro unfold, not only single deletions

*Committed before the adapters, the executor, the oracle and any run.*

§3 defined **R1 `PRODUCTION_DELETION`** as `G\q` for every single production `q`. That is too
narrow for library-growth grammars, where the semantics-preserving alternative named by the
row ("a semantics-preserving re-encoding into base productions") deletes the whole composite
layer at once: with `m1 -> a b` and `m2 -> m1 m1`, deleting `m1` alone leaves `m2`-encodings
intact, so a single-deletion-only R1 would systematically MISS the very class of encoding the
row is about. A detector that misses its headline class is broken, so the generator is
widened before it is run, not after it returns nothing.

**A2 (frozen).** R1 is the union of two sub-generators, both reported separately:

- **R1a `SINGLE_PRODUCTION_DELETION`** — `G\q`, one `q` at a time (as originally frozen).
- **R1b `FULL_MACRO_UNFOLD`** — `G\Q` where `Q` is the grammar's whole **composite**
  production set (productions carrying a registered expansion into other productions).
  `dep(Q)` is computed for the set exactly as `dep(q)` is for a single production, and
  `Q` is **target-exclusive** iff `dep(Q) = {t}`.

A Tier-1 hit records which sub-generator produced it (`via: R1a | R1b | R2`). `Q = ∅` yields
`R1_NOT_APPLICABLE:NO_COMPOSITE_PRODUCTIONS`, again a distinct field from "checked and clean".

**A2 anchor, verified before the corpus run:** `gmi-833-g0-grammar-growth-v1` has
`Q = {m1, m2}` and must be reachable by R1b. Whether it flags, and at which tier, is left to
the run — the amendment fixes the generator, never the outcome.

---

## Amendment A3 — presentation set for multi-ecology grammars; two hit markers

*Committed before the executor, the oracle and any run. The adapters exist at this point
only as a loader that prints instance shapes; no detector, no `mu`, no hit, no result blob.*

**A3.1 — union of the package's own registered ecologies.** For a package that searches ONE
grammar under SEVERAL registered ecologies (a positive ecology and its matched negative
twin), the presentation set of the grammar instance is the union of the candidates that are
exact for **each** registered ecology, deduplicated by candidate, each classified by the
package's own post-run classifier.

Reason: restricting to the positive ecology alone collapses several corpus grammars to a
single semantic class, where "strictly lower cost than a semantically equivalent
alternative" has no alternative to compare against and target-exclusivity is vacuous. The
union is the grammar's own registered morphology-vs-morphology cost geometry — the object
#891's BIAS-1 is about — and it is what makes the row's question answerable at all. The
union is taken over the package's OWN registered ecologies only; no ecology is invented.

**A3.2 — two mandatory markers on every Tier-1 hit** (recorded fields, never silent):

- `UNIQUE_REALIZATION` — the target class has exactly one presentation. The cost comparison
  is then a limit (coverage loss), not a finite strict inequality.
- `SINGLE_CLASS_INSTANCE` — the instance has exactly one semantic class, so exclusivity is
  vacuous. Such a hit is NOT counted in the confirmed population; it is reported under
  `SCREENED_NOT_ADJUDICATED:VACUOUS_EXCLUSIVITY_SINGLE_CLASS`.

`TARGET_IS_A_PRIMITIVE` (coverage lost) and `TARGET_SPECIFIC_SHORTCUT` (coverage retained,
finite strict rise) stay distinct in every table. Only the latter is a strict-inequality
witness in the row's literal wording; the former is reported as the limit case, labelled.
