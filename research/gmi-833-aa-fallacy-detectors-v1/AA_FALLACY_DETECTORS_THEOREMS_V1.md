# Named results — `gmi-833-aa-fallacy-detectors-v1` (issue #833, section AA)

Claim ceiling: `VALIDATED_REVIEW_QUEUE_DETECTOR_V1`.

Every result below is an exact statement about explicitly named finite objects
at `source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`: the **22553**
registered scientific objects of `CORPUS_INDEX_V1.json`
(blob `709159c53c6284366aaf1f05380f5fada8d81a98`), the **2362** named results of
the tracked theorem artifacts, the registered grammar fixture of
`gmi-833-g0-grammar-bias-v1` with its exhaustive **24**-member isometric family
and its registered non-isometric pair, constructed fixtures, and 200 seeded
randomizations.

**Every detector emits a review queue, never a verdict.** A queued object is a
requirement to look; an unqueued object is not thereby correct. None of these is
an analytic proof, and none asserts that any queued claim is wrong.

---

## FD-1 — AA19: a universal claim warranted by a search that was run is queued

**Scope.** All 22553 registered objects.

**Statement.** The detector is a **metadata** predicate, deliberately not a text
grep: an object is queued when its registered `quantifier_class` is `UNIVERSAL`
— a statement about everything the class can represent — while its registered
`proof_evidence_mode` is an experiment that was run (`EMPIRICAL_EXPERIMENT` or
`STATISTICAL_EXPERIMENT`), which is a reachability observation. The queue is
**60 records over 57 distinct object ids in 37 source files**. Recall on planted
positives is **6/6**; alarms on the 12 planted clean objects are **0**; and, on
the real corpus, alarms on the whole declared-clean population are **0 of
21548** — **331** universal claims carrying an analytic or mechanized warrant
and **21217** non-universal objects, zero alarms on either. Two independent
routes agree on the queue by **set equality**. The overlap with the `FIN2UNIV`
population AA21 already validated is **1 object**, so the two detectors are
near-disjoint rather than the same predicate renamed.

**Quantifiers.** For every registered object o: o is queued iff
`o.quantifier_class = UNIVERSAL` and `o.proof_evidence_mode ∈
{EMPIRICAL_EXPERIMENT, STATISTICAL_EXPERIMENT}`. Over the frozen corpus only.

**Assumptions.** The registered quantifier class and evidence mode mean what the
parent census says they mean. The predicate fires on **declared metadata**, so a
claim that confuses representability with reachability in prose while declaring
a non-universal quantifier class is outside its scope — and the size of that
blind spot is measured, not waved at: a text-trigger variant would add **14**
more records (hostile H7, 60 → 74).

**Dependencies.** `gmi-833-corpus-census-v1` for the corpus and the fields;
`gmi-833-aa-finite-universal-harness-v1` for the `FIN2UNIV` population the
disjointness is measured against.

**Falsifiers.** One alarm on any declared-clean object, planted or real; a
planted positive missed; a route-B recount whose queue differs by one id; an
overlap with `FIN2UNIV` equal to the queue size, which would mean the two
predicates had collapsed into one.

**Strongest parents.** `gmi-833-global-vs-reachable-morphology-v1` and
`gmi-833-finite-reachability-fractions-v1` **own** the representability /
reachability distinction and its exact fractions; nothing about the distinction
is claimed novel here. Wolpert & Macready, *IEEE TEC* 1(1) 1997,
doi:10.1109/4235.585893, owns the reason a search result is not a statement
about a whole class. The residual is the detector and its validation.

**Forbidden extrapolations.** `QUEUED_CLAIM_IS_FALSE` and
`UNQUEUED_CLAIM_IS_SOUND` are both forbidden. 60 records is a review queue, not
60 errors.

---

## FD-2 — AA31: a same-semantics grammar pair with divergent bias is queued, exactly

**Scope.** The registered grammar fixture of `gmi-833-g0-grammar-bias-v1`, its
exhaustive isometric family, and its registered non-isometric pair.

**Statement.** Two grammars with the same semantics are queued when their
per-semantic-class bias rows differ in any cell, compared as exact `Fraction`
values with **no tolerance**. The parent's own **24** isometric remints — every
relabelling of the fixture's four nodes — raise **0** alarms, matching the
parent's certificate of 24 permutations with 0 invariant failures; this is a
no-alarm case measured on the parent's real construction, not on anything
built here. The parent's registered non-isometric same-semantics pair **is**
queued, with **10 divergent cells across 2 of the 3 semantic classes** (`A` and
`B`; `ROOT` agrees). Exactness is load-bearing and is asserted: `1/3` versus
`333333/1000000` diverges, `2/6` versus `1/3` does not.

**Quantifiers.** For all 24 isometric relabellings, and for the registered pair.

**Assumptions.** Bias rows are keyed by semantic class, so an isometric node
relabelling leaves them invariant by construction — which is exactly why the
family is the right no-alarm population. "Same semantics" is the parent's own
predicate on the two grammars' semantic maps, and it is checked here rather than
assumed.

**Dependencies.** `gmi-833-g0-grammar-bias-v1` for the fixture, the remint
machinery, the isometric certificate and the non-isometric pair. FD-2
instruments that result; it does not re-derive it.

**Falsifiers.** One isometric relabelling that diverges; the registered pair
failing to diverge; a pair queued whose semantic maps differ, which would make
the finding a semantics difference rather than a grammar artifact; any float or
tolerance entering the comparison.

**Strongest parents.** `gmi-833-g0-grammar-bias-v1` **owns** the
grammar-induced-bias finding outright and none of it is claimed here. Alur et
al., "Syntax-guided synthesis", FMCAD 2013, doi:10.1109/FMCAD.2013.6679385,
owns grammar-restricted search as a concept. The residual is turning a frozen
result into a reusable exact divergence test with a measured no-alarm family.

**Forbidden extrapolations.** `GRAMMAR_BIAS_ELIMINATED` and
`ALL_GRAMMARS_EQUIVALENT` are forbidden. A queue of one registered pair is a
detector validated on the one pair the corpus registers, not a survey of the
repository's grammars.

---

## FD-3 — AA37: a new-form claim carrying no parent-reduction ledger is queued

**Scope.** The 2362 named results of the tracked theorem artifacts, plus three
constructed fixtures.

**Statement.** Tier 1 is precise: a named result is a new-form claim when its
text uses the declared novelty vocabulary — the six novelty-ladder levels of
`gmi-833-ab-residual-definitions-v1` plus the crosswalk's `unseen form`,
`novel intelligence`, `novel mechanism`, `new computational class`,
`predicted morphology`, `held-out architecture`, and AA37's own `new-form`,
under a declared hyphen/space normalization — and it is queued when it emits
**no strongest-parent ledger**. **18** results trigger tier 1, **8** of them
carry a result identifier, **5** are cleared by a parent ledger and **3** are
queued. The no-alarm population is real and large: **2344** named results do not
trigger and none is queued. This tranche's own theorem notes are a **live
cleared negative** — **1** triggers tier 1 and **0** are queued. On constructed
fixtures, recall is **1/1** and clearing is **1/1**, and an off-topic result
triggers **0** times. Tier 2, a bare `novel`/`new`/`first` grep, triggers
**233** identified results — an inflation of **225** over tier 1 — and is
reported for exactly that reason and never used to queue.

**Quantifiers.** Over all 2362 named results and all three fixtures.

**Assumptions.** Emitting a strongest-parent ledger is evidence that a parent
reduction was *recorded*, never that the reduction is correct — the ledger gate
this reuses checks emission, not contents. Every tier-1 term has a declared
source (AA37's own row, the novelty ladder, or the frozen crosswalk) and the
guard asserts it term by term.

**Dependencies.** `gmi-833-aa-ledger-gate-v1` for the named-result and ledger
predicates; `gmi-833-ab-residual-definitions-v1` for the six ladder levels;
`gmi-833-tranche-ab-ac-lit` for the crosswalk's new-form vocabulary.

**Falsifiers.** A queued result that does emit a parent ledger; a cleared result
that does not; a tier-1 term with no declared source; an off-topic fixture that
triggers; this tranche's own notes appearing in the queue.

**Strongest parents.** `gmi-833-parent-equivalence-v1` owns parent equivalence
as an operation and `gmi-833-aa-ledger-gate-v1` owns the ledger predicate. Rice,
*Advances in Computers* 15 (1976), doi:10.1016/S0065-2458(08)60520-3, is the
standing parent a selection-style new-form claim must be reduced against. The
residual is the binding of a novelty trigger to a ledger requirement.

**Forbidden extrapolations.** `PARENT_REDUCTION_COMPLETE`,
`ALL_PARENTS_EXHAUSTED` and `NOVELTY_ESTABLISHED` are forbidden. The three
queued results are three notes to check, and the small tier-1 population is
itself the finding: the corpus rarely states a new-form claim in the sanctioned
vocabulary at all.

---

## FD-4 — every text-trigger variant is measured and published, never used to queue

**Scope.** The three detectors and their text variants, on the real corpora.

**Statement.** Each detector's loose variant is run once, only to publish the
size of the gap between what it sees and what the detector queues. For AA19 the
text variant adds **14** records (60 → 74); for AA37 the bare grep triggers
**233** identified results against tier 1's **8**, an inflation of **225**. For
AA31 no text variant exists: the comparison is arithmetic. Seven hostiles are
detected and each moves its own quantity, including the two that show what
loosening the AA19 predicate costs on the **real** corpus — dropping the
quantifier conjunct moves real clean alarms **0 → 1027**, and widening to
analytic warrants moves them **0 → 331**. The null shuffles AA19's two predicate
fields independently across all 22553 objects: over 200 seeded trials it
reproduces the true queue **0** times, with flagged-set sizes **46–86** (exact
mean **2607/40**) and a maximum overlap with the true 57-element queue of **2**
(exact mean **13/40**).

**Quantifiers.** Over the seven hostiles and all 200 trials.

**Assumptions.** The null preserves each field's marginal and destroys their
joint, which is the right null for a conjunctive two-field predicate. The seed
is pinned and the study is reproducible bit for bit.

**Dependencies.** FD-1 and FD-3 for the populations the variants are measured
against.

**Falsifiers.** A hostile whose quantity does not move; a null trial
reproducing the true queue; an inflation figure of zero, which would mean the
text variant and the detector agree and the published gap is vacuous.

**Strongest parents.** `gmi-833-aa-finite-universal-harness-v1` established the
metadata-versus-text measurement for AA21 (a prose variant there inflated 283 →
351); this result carries the same instrument to two more rows. Permutation-null
practice in applied statistics is standard and is not claimed novel.

**Forbidden extrapolations.** An inflation figure bounds the disagreement
between two predicates. It does **not** say which of them is right on any given
object, and it is not a count of missed fallacies.
