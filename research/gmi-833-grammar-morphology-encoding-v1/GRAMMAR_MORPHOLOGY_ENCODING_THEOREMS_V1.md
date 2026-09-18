# GME theorems — search grammars that encode the target morphology

Scope object: the frozen `P-COST` population of §4.2 of `FREEZE_V1.md` — 13 grammar
instances mechanically extracted from 4 merged corpus packages (plus one synthetic
clean-control fixture used only for validation and excluded from every denominator,
Amendment A5.2), each with its declared target morphology quoted verbatim from the owning
package. All arithmetic is exact integer
arithmetic; no float appears in any statement or receipt.

Every result below is **at registered scope**. None of them is a statement about all
grammars, all searches, or machine intelligence in general.

---

## GME-1 — the target-exclusive-production criterion is name-blind

**Statement.** For a grammar instance `G` with declared target `t`, define
`dep(Q) = { s : mu_{G\Q}(s) != mu_G(s) }`, where `G\Q` removes every presentation using a
production in `Q`. `Q` is *target-exclusive* iff `dep(Q) = {t}`. Then for every bijective
renaming `pi` of the production vocabulary and of the presentation identities that
preserves semantic class and cost, `dep_G(Q) = dep_{pi G}(pi Q)`, so the Tier-1 verdict is
invariant under renaming.

**Proof.** `mu_G(s)` is the minimum of a multiset of integers indexed by the presentations
of class `s`; `pi` is a bijection preserving class and cost, so it preserves that multiset
and hence every `mu`. `G\Q` is defined by the incidence relation "presentation uses
production", which `pi` transports exactly by construction. Therefore every `mu_{G\Q}(s)`
and every membership test in `dep` is preserved. QED.

**Quantifiers.** For all `G` in `P-COST`, for all renamings, for all `Q`. Nothing is
claimed for grammars outside `P-COST`.

**Falsifier.** A renaming under which the hit set changes. Machine certificate: the R3
battery, 10 relabelings per instance, plus 204 randomized isometry controls (V5),
0 changes.

**Strongest parents.** #891 LABEL-1 (family-label blindness) and ISO-1 (certified
isometry invariance). GME-1 is the production-level analogue; the parent's result is not
reclaimed.

**Forbidden extrapolation.** Name-blindness of the *criterion* is not neutrality of the
*grammar*. #891 BIAS-1 forbids that step and GME-3 reproduces it.

---

## GME-2 — deletion dichotomy: semantics-preserving rise vs coverage loss

**Statement.** For target-exclusive `Q`, exactly one of:
(a) `mu_{G\Q}(t)` is finite and `> mu_G(t)` — `G\Q` is a semantics-preserving re-encoding
of `t` and the target is strictly cheaper in `G`: `TARGET_SPECIFIC_SHORTCUT`; or
(b) `mu_{G\Q}(t) = None` — `t` has no presentation avoiding `Q`, i.e. the target morphology
*is* a production of the grammar: `TARGET_IS_A_PRIMITIVE`.

**Proof.** `mu_{G\Q}(t)` is either `None` or a minimum over a subset of the costs of `t`'s
presentations; a subset minimum is never smaller than the full minimum, and the hit
condition excludes equality. The two branches are exhaustive and disjoint. QED.

**Why the distinction is load-bearing.** Only (a) is a *strict inequality against a
semantically equivalent alternative* in the row's literal wording. In (b) no such
alternative exists inside the grammar at all — the gap is a limit, not a finite number.
The two kinds are never merged in any table of this package.

**Falsifier.** A hit reported as (a) whose `mu_{G\Q}(t)` is `None`, or a sentinel integer
used in place of `None` (hostile H2).

---

## GME-3 — #891's BIAS-1 reproduced over the extractable population

**Statement.** There exist grammar instances in `P-COST` and semantics-preserving cost
remints (R2: exchange of the cost assignment between two equal-size semantic classes,
coverage preserved exactly) under which the selected class changes. In particular the
registered #891 pair is re-found: `GA` selects `ALPHA` and `GB` selects `BETA` at
`w = (1,1)` with identical coverage `{ALPHA, BETA}`.

**Machine certificate.** 55 admissible remints over the loaded instances, 3 exhibiting a
selection reversal, including `cost_privilege_GA` — the mandatory V1 anchor.

**Status.** This is a **reproduction of the registered boundary**, not a discovery. A
same-coverage cost remint reverses selection for essentially any non-degenerate grammar;
that is exactly what #891 already proved, and it is why R2 is **never** read as evidence of
a leak in this package. Tier-1 is decided by R1 alone.

**Parent.** #891 `NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE`, cited
as the boundary, EARNED-BY-COUNTEREXAMPLE. It is not overturned, weakened or re-derived.

---

## GME-4 — no-alarm: isometries and a clean grammar produce zero flags

**Statement.** (i) For every instance in `P-COST` and every isometric relabeling (semantic
class, cost and leaf-structure preserved), the Tier-1 hit set is unchanged. (ii) The
registered clean control grammar — every class realized over the same vocabulary at the
same costs — produces 0 hits.

**Machine certificate.** V3: 10 relabelings per targeted instance, all invariant;
clean control 0 hits. V5: 204 randomized isometry controls, 0 spurious changes.

**Falsifier.** Any flag on the clean control, or any hit-set change under an isometry.

---

## GME-5 — the identified population (the row's answer)

**Scope.** 13 grammar instances from **4 merged corpus packages**, 11 carrying a declared
target. (This package's own synthetic clean-control fixture is loaded for validation V3/V5
and is excluded from every denominator below — Amendment A5.2.)

**Statement.** The corpus grammars that **encode their declared target morphology** in the
sense of GME-2 are exactly these **7**, and they split into two kinds that are never summed:

### (a) Measured cost gap — 2 instances, only one of them a finite strict rise

| grammar instance | production set | kind | mu(t) before -> after | indicator margin | Tier-2 flip |
|---|---|---|---|---|---|
| `grammar_growth_G2` (#897) | `m2` (R1a) | TARGET_SPECIFIC_SHORTCUT | 2 -> 3 | 0 | no |
| `grammar_growth_G2` (#897) | `{m1, m2}` (R1b full unfold) | TARGET_SPECIFIC_SHORTCUT | **2 -> 5** | 0 | **yes** (REUSE_POSITIVE -> UNRELATED_CONTROL) |
| `cross_grammar_routing_B` | `branches` | TARGET_IS_A_PRIMITIVE | 3 -> none | 1 | no |

`grammar_growth_G2` is the **only** case in the corpus where a genuine semantics-preserving
re-encoding exists and is strictly dearer. The deleted set is not a class indicator: the
base-only encoding of every reuse-positive word uses neither `m1` nor `m2`, so the target
stays reachable and the 2 -> 5 rise is a real cost measurement over 181 target presentations.
Unfolding the invented composite layer changes the minimum of the target class and of no
other class, and moves the selected class. Disposition
`ENCODES_COST_MEASURED__DISCLOSED_CHARGED`: the package charges `K_total = 6` at
`kappa = 1`, preserves an H- negative control, and beats a 0/200 randomized-admission null.

`cross_grammar_routing_B` passes the A5 indicator test **on a margin of one**: `branches`
also appears in a single `FIXED_READ` presentation (the all-equal-leaves candidate, which
`classify()` sends to the other class), so the production does not mark the target class
exactly. Its `mu` gap is still a coverage loss rather than a finite number. The margin is
published on the hit so the thinness is visible rather than hidden behind a verdict.

### (b) Production is the class label — 5 instances (indicator margin 0)

| grammar instance | production | n target presentations |
|---|---|---|
| `cross_grammar_local_A` | `shared` | 1 |
| `cross_grammar_local_B` | `shared` | 1 |
| `cross_grammar_state_B` | `not_s` | 4 |
| `cross_grammar_storage_A` | `rows` | 2 |
| `cross_grammar_storage_B` | `leaves` | 2 |

For these, `gmi-cross-grammar-four-family-v1`'s own post-run `classify()` assigns the
phenotype **by reading the production symbol** (`SHARED_LOCAL_UPDATE if raw[...] ==
"shared"`, `"not_s" in raw`, `raw[0] in {"rows","leaves"}`), so
`sem(p)` is a function of `leaves(p)` and target-exclusivity follows from the classifier's
definition. The name-blind `indicator(Q, t)` test of Amendment A5 separates them: every
target presentation uses `Q` and no other class's does.

**These are still encodings** — indeed the strongest form of "the answer is in the primitive
basis": the morphology taxonomy *is* the grammar's vocabulary, so the target is reachable
only through a production nothing else uses. But **no cost gap is measured**, and this
package never reports one for them. Disposition
`ENCODES_CLASS_INDICATOR__DISCLOSED_CHARGED`: the package discloses the design (two
independently structured grammars, candidate spaces not in one-to-one correspondence, no
shared evaluator) and controls it with matched negative twin ecologies (8/8 positive/twin
flips).

### The rest of the corpus population

**`ENCODES_UNDISCLOSED` = 0.** No confirmed leak.

**Zero corpus grammars came out `NEUTRAL_AT_REGISTERED_SCOPE`.** The only NEUTRAL row is the
synthetic fixture, which is exactly what it is there to be.

**Screened, not cleared** (§4.3): 3 instances `NO_PRODUCTION_STRUCTURE`
(`cost_privilege_GA`, `cost_privilege_GB`, `cross_grammar_state_A`), 1
`NUMERIC_PARAMETER_SPACE` (`cross_grammar_routing_A`), 2 `NO_DECLARED_TARGET`
(`cost_privilege_REGISTERED`, `grammar_bias_G0_slice`). These are **not** clean verdicts;
the R1 production route simply does not reach them.

**Detector power is proven, not assumed** (V1-V5): the #891 anchor is re-found, planted
target-specific shortcuts in real corpus grammars are caught 11/11, the clean control and
204 randomized isometry controls raise 0 alarms, and all seven hostile detector variants —
including H7, a variant omitting the A5 indicator test — are detected. H7 is a live check,
not a formality: it passes precisely because the population really does contain both kinds.

**Forbidden extrapolation.** This is an identification over an extractable population. It is
NOT a claim that no other corpus grammar encodes its target; the cost route reaches only
grammars whose `(presentations, cost, semantic class, declared target)` tuple is
mechanically recoverable, and 4 of the 11 targeted instances are not reached by R1 at all.

---

## GME-6 — the lexical route reproduces its parents at 0 confirmed

**Statement.** Over `P-LEX` — 158 packages (authority-self-skip: this package) that are
definition-anchored and carry grammar/DSL vocabulary, 1,923 extracted blocks — the lexical
detector over the corpus's own D1 denylist and 31-key D2 mapping raises **37 hits in 9
packages, all 37 adjudicated individually with written reasons, 0 CONFIRMED**.

False-positive classes, all named and reproduced rather than silenced:

| class | n | cause |
|---|---|---|
| `PARENT_LITERATURE_ATLAS` | 19 | `GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md`, self-declared "MICROFEATURE ATLAS ... NOT NEURAL EVIDENCE"; TF-* rows are parent comparison targets, not productions |
| `AUDIT_RECORD_ECHO` | 10 | the corpus's own anti-smuggling / audit / registry machinery recording the banned token (the registered #976 denylist-owner class) |
| `SUBSTRING_COLLISION` | 5 | `gru` matched inside `congruence`; the token is not a segment of the identifier |
| `PROSE_NEGATION` | 3 | the token sits inside an explicit prohibition |

The sharpest instance, read and quoted: `machine-intelligence-morphogenesis-v1/gmi_k4_freeze.py:146-148`
defines `GRAMMARS["G1_TENSOR_GRAPH"]` and ends its definition with
*"No convolution, attention, gate, expert, retriever or adapter macro."* — the flagged token
is the corpus's own prohibition inside a grammar declaration.

**Status.** Reproduction, as pre-registered (PRED-5). #976's L48-SCREEN and the merged A2
signature extension (148 packages, 1,607 blocks, 0 confirmed collisions) already owned this
route; GME-6 re-derives it on the grammar-restricted population and adds two previously
unrecorded false-positive classes (`SUBSTRING_COLLISION`, `PARENT_LITERATURE_ATLAS`).

---

## Detector agreement (freeze §7a)

D-LEX and D-COST are materially independent and **disagree completely**: the two packages
D-COST identifies (`gmi-cross-grammar-four-family-v1`, `gmi-833-g0-grammar-growth-v1`) are
flagged by D-LEX **not at all**, and the 9 packages D-LEX flags are all refuted. This is the
point of running two routes: the encodings that exist in this corpus carry perfectly neutral
production names (`shared`, `rows`, `leaves`, `branches`, `not_s`, `m1`, `m2`) and are
invisible to every lexical and semantic-fingerprint screen. The parents' own conclusion —
that semantic target-encoding "cannot be excluded lexically" — is confirmed constructively.

---

## Registered open instance, carried forward

`INSTANCE-AJ9-NOSMUGGLING-SCOPE` (RED / HIGH, aj-lane) is **not closed here**. Its gap is
governance of task provenance and primitive-basis provenance in the AJ9 blind-recovery
contract — a contract-coverage defect, not a cost-geometry property of an extractable
grammar object. It is outside the mechanical reach of both routes of this pass and is
recorded as such in `RESULT_V1.json.registered_open_instance`.

## Claim ceiling

`GMI_833_SEARCH_GRAMMAR_TARGET_ENCODING_IDENTIFICATION_AT_REGISTERED_SCOPE`

This establishes no unbiased grammar, no universal representation invariance, no search
neutrality, no architecture-prior-free grammar, and no statement that "no grammar encodes
its target". The full forbidden-promotion list is in `MANIFEST_V1.json` and is asserted by
the test battery.

---

## Pre-registered prediction outcomes (including the two that deviated)

The freeze registered five falsifiable predictions and a set of both-direction anchors
before any detector existed. All outcomes, deviations included:

| id | prediction | outcome |
|---|---|---|
| PRED-1 | #891 `GA/GB` re-found as a selection reversal under R2 | **held** — `GA` selects `ALPHA`, `GB` selects `BETA`, coverage equal, 1 reversal on `GA` |
| PRED-2 | `gmi-833-g0-grammar-bias-v1` disposes `NO_DECLARED_TARGET` | **held** (the rule is not rigged: a package that measures bias declares no target) |
| PRED-3 | R3 yields 0 flags on every `P-COST` grammar | **held** — 12 instances x 10 relabelings + 204 randomized controls, 0 changes |
| PRED-4 | routing `from_input` (A) **and** `branches` (B) are `TARGET_IS_A_PRIMITIVE` | **partially deviated** — `cross_grammar_routing_B` held; `cross_grammar_routing_A` did **not**, because its exact-candidate set has only one string atom, so `|P(G)| >= 2` fails and Amendment A1 dispositions it `SCREENED_NOT_ADJUDICATED:NUMERIC_PARAMETER_SPACE`. The substantive reading of PRED-4 is untested for grammar A, not refuted |
| PRED-5 | D-LEX returns 0 confirmed over `P-LEX` | **held** — 37/37 adjudicated, 0 confirmed |

**Anchor deviation.** Amendment A1 predicted `cross_grammar_state_A` would land in
`NUMERIC_PARAMETER_SPACE`. It landed in `NO_PRODUCTION_STRUCTURE` instead: its exact
candidates are pure integer tables with **zero** string atoms rather than one. Both are
registered `R1_NOT_APPLICABLE` reasons and both are screened-not-cleared, so the disposition
is unaffected; the anchor's wording was simply wrong about which of the two applies, and is
recorded here rather than quietly corrected.

Both deviations point the same way: the R1 production route reaches only grammars with a
named production vocabulary, and two of the four cross-grammar A-side instances do not have
one. That is a coverage limit of this pass, filed as `REV-B48-COST-ROUTE-COVERAGE`, not a
clean verdict on those grammars.

**Amendment A5's own anchor also deviated, in the interesting direction.** A5 predicted all
six cross-grammar hits would be `PRODUCTION_IS_CLASS_INDICATOR`. Five are, at margin 0.
`cross_grammar_routing_B` is not: `branches` also occurs in one `FIXED_READ` presentation
(the all-equal-leaves candidate), so it does not mark the target class exactly and the
incidence test returns `COST_MEASURED` on a margin of 1. The test was frozen before the run
and decided the case against the amendment's own expectation; the margin is published on the
hit rather than rounded away.
