# Named results — `gmi-833-aa-finite-universal-harness-v1` (issue #833, section AA)

Claim ceiling: `REGISTERED_DETECTOR_VALIDATED_V1`.

Every result below is an exact statement about explicitly named finite objects:
the 1140 records of
`research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json`
(blob `61006b756721c748f8dcc797c755abd25cc42956`), the 22553 scientific objects
of `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
(blob `709159c53c6284366aaf1f05380f5fada8d81a98`), and 22 declared synthetic
validation objects — all at
`source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`.

These are computer-assisted exhaustive checks over declared finite domains.
**None is an analytic proof of an unbounded universal statement**, and none
asserts that any flagged GMI claim is actually wrong. The `FIN2UNIV` predicate
fires on *declared metadata* — a registered quantifier class and a registered
evidence mode — never on the mathematics of the claim.

---

## FU-1 — the registered `FIN2UNIV` population is exactly what the predicate licenses

**Scope.** The `GAP-FIN2UNIV-*` subpopulation of the 1140 frozen gap records,
and the 22553 frozen scientific objects.

**Statement.** Two materially independent routes produce the same population.
Route A reads the registered gaps out of the frozen gap graph. Route B never
opens the gap graph: it recovers the firing condition and the gap-id
construction from the parent census *source text*
(`corpus_census_v1.py`, blob `e35f1ae92ea9d140675e01750252dca0a36d2b6e`) and
re-derives the population from the object corpus. The two gap-id sets and the
two `claim_id` sets are **identical by set equality** (symmetric difference 0),
at **283 records**, **269 distinct gap ids**, **269 distinct claim ids**, drawn
from **182 distinct source files**, split **by evidence mode** between
`COMPUTER_ASSISTED_EXHAUSTIVE` and `FINITE_EXECUTABLE_CERTIFICATE`.

**Quantifiers.** For every object o in the 22553: o is flagged iff
`o.quantifier_class = UNIVERSAL` and
`o.proof_evidence_mode ∈ {COMPUTER_ASSISTED_EXHAUSTIVE, FINITE_EXECUTABLE_CERTIFICATE}`.
Universally quantified over the frozen corpus only.

**Assumptions.** The two frozen blobs are the ones pinned above. The census
source states its own rule in the form route B parses; if it does not, route B
raises instead of agreeing by coincidence. `object_id` is the identity the
census hashes.

**Dependencies.** `gmi-833-corpus-census-v1` for the corpus, the predicate and
the gap population; `gmi-833-aa-gap-object-v1` for the `OPEN_GAP` schema whose
non-empty-cell property FU-2 re-checks on this subpopulation. No dependency on
any GMI theorem.

**Falsifiers.** A non-zero symmetric difference between the two routes' gap-id
sets; a `claim_id` in the gap graph with no corresponding firing object; a
census source whose stated rule differs from the one route B recovers.

**Strongest parents.** `gmi-833-corpus-census-v1` **owns** the predicate and
its output; nothing about the predicate is claimed novel here. The
analytic-proof / computer-assisted-check line the predicate encodes is Hales,
"Formal proof", *Notices of the AMS* 55(11) 2008. The residual is the
independent re-derivation and the set-equality comparison.

**Forbidden extrapolations.** Agreement of two routes on a population says
nothing about whether the flagged claims are wrong. `FIN2UNIV_CLAIMS_ARE_FALSE`
and `CORPUS_FREE_OF_OVEREXTRAPOLATION` are both forbidden.

---

## FU-2 — the registered population carries a duplicate-record defect

**Scope.** The same `GAP-FIN2UNIV-*` subpopulation.

**Statement.** The gap graph carries **283 `FIN2UNIV` records** but only
**269 distinct gap ids** — **14 records are duplicates of an id already
present**. The cause is structural and is visible in the parent source: the
census emits one gap per *object row* inside `for obj in objects`, while the
gap id is a function of `object_id` alone, and 14 object rows share an
`object_id` with an earlier firing row. Separately, all five required
`OPEN_GAP` text cells are non-empty on all 283 records (**0** empty cells), and
the five non-identifying columns each carry exactly **one** value
(`CRITICAL`, `MATERIAL`, `OPEN`, `HOSTILE_VERIFICATION`, `T833-B1-AA`) — the
zero-information grading `gmi-833-aa-gap-object-v1` AAG-2 measured over the
whole graph reproduces on this subpopulation.

**Quantifiers.** Over the 283 records and the five named columns.

**Assumptions.** A gap "identity" is its `id` field. Two records sharing an
`id` are the same gap counted twice, not two gaps.

**Dependencies.** FU-1 (the population); `gmi-833-aa-gap-object-v1` AAG-1 for
the nine-field schema and AAG-2 for the zero-information column finding.

**Falsifiers.** A recount showing 283 distinct ids; a documented reason the
census intends per-row rather than per-object emission; any empty required
cell.

**Strongest parents.** `gmi-833-corpus-census-v1` owns the emission. This is a
**disclosure against the parent**, not a repair: the defect is reported and the
population is left as registered.

**Forbidden extrapolations.** 14 duplicates is a counting defect in the gap
ledger, not evidence that any claim is duplicated, and not a licence to
renumber the registered population.

---

## FU-3 — the detector has total recall on planted positives and zero alarms on declared-clean input

**Scope.** 8 planted positive objects and 14 declared-clean objects, all
synthetic, all of shapes fixed in `FREEZE_V1.md` §4 before any number was read.

**Statement.** Recall **8/8**. False alarms **0/14** on the constructed clean
set — and, more importantly, **0 alarms on 21548 real objects** of the frozen
corpus that the predicate must leave alone: **331** `UNIVERSAL` claims carrying
an analytic or mechanized warrant and **21217** non-`UNIVERSAL` objects, zero
alarms on either. A constructed no-alarm set measures the author's imagination;
this one measures the corpus. The clean classes are
(i) `UNIVERSAL` with `ANALYTIC_DEDUCTIVE` or `MECHANIZED_PROOF` — a universal
claim with an analytic warrant is exactly what the predicate must *not* flag —
and (ii) every non-`UNIVERSAL` quantifier class paired with each finite
evidence mode. The no-alarm case is **falsifiable, not vacuous**: widening the
evidence-mode set to include the analytic modes raises alarms on the same clean
set, and the test asserts that it does.

**Quantifiers.** Over all 22 synthetic objects, and over all 21548 real
non-target objects.

**Assumptions.** The declared-clean classes are genuinely clean *for this
predicate*: a universal claim with an analytic proof is out of the predicate's
target class by construction. This is a definitional boundary, not an empirical
finding.

**Dependencies.** FU-1 for the predicate under test. Independent of the corpus.

**Falsifiers.** A single alarm on any declared-clean object, constructed or
real; a planted positive the predicate misses; a widening perturbation that
raises no alarm (which would show the clean set vacuous).

**Strongest parents.** Standard detector validation practice (recall /
false-alarm on labelled controls). Nothing methodological is claimed novel; the
residual is that the parent census registered this detector's output and never
ran either test.

**Forbidden extrapolations.** `DETECTOR_IS_COMPLETE` is forbidden. Recall is
measured against positives of the declared metadata shape only. A claim that
overextrapolates in prose while declaring a non-universal quantifier class is
**outside** this predicate's scope — see FU-4's hostile H6, which measures
exactly how large that blind spot is.

---

## FU-4 — six hostiles move their own quantity, and 0/200 randomized nulls reproduce the population

**Scope.** Six declared perturbations and 200 seeded randomizations
(seed `8332021`) over the real 22553-object field distribution.

**Statement.** Every hostile is detected and each moves the quantity it was
built to move: dropping one registered gap moves distinct ids **269 → 268**;
widening the evidence modes to analytic moves clean alarms **0 → 1**; dropping
the quantifier conjunct moves clean alarms **0 → 12**; truncating the gap-id
hash to 11 hex digits changes a fixed object's id; narrowing to one evidence
mode moves recall **8 → 4**; and replacing the declared quantifier class by a
prose grep for universal wording moves flagged records **283 → 351**, i.e.
**+68 alarms** the registered detector does not raise. The null shuffles the
two predicate fields independently across all 22553 objects: over 200 trials it
reproduces the true flagged set **0** times, with flagged-set sizes ranging
**282–389** (exact mean **8677/25**) and a maximum overlap with the true
269-element set of **15** (exact mean overlap **1259/200**).

**Quantifiers.** Over the six hostiles and all 200 trials.

**Assumptions.** The null preserves each field's marginal distribution and
destroys their joint — which is the right null for a conjunctive predicate over
two declared fields. The seed is pinned; the study is reproducible bit for bit.

**Dependencies.** FU-1 (population), FU-3 (clean and positive sets).

**Falsifiers.** A hostile whose quantity does not move; a null trial
reproducing the true set; a null whose flagged sets are empty (which would make
the comparison vacuous).

**Strongest parents.** Permutation-null practice in applied statistics; nothing
novel claimed. The +68 figure is this package's own measurement.

**Forbidden extrapolations.** The 68 extra prose-variant alarms are **not** 68
additional real fallacies: they are the size of the disagreement between a
metadata predicate and a text predicate. Which of the two is right on any given
object is undetermined here, and AA16–AA20 and AA22–AA37 remain open.
