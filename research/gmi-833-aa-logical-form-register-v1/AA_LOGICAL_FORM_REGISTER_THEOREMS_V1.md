# AA logical-form register — named results (issue #833, section AA)

Status: **FINITE EXACT REGISTER AND REVIEW-QUEUE INSTRUMENT**. Claim ceiling
`LOGICAL_FORM_REGISTER_AND_REVIEW_QUEUE_V1`. Every number below is an `int`
or an exact `Fraction` reproduced by `RESULT_V1.json`; the two routes agree
by canonical-structure equality on every form and by set equality on every
queue. A queued object is a review item, never a refuted claim; an
unqueued object is not thereby sound. No statement here reaches past the
registered set (`309 / 391`).

Population: the census's own enumeration under the rule of `FREEZE_V1.md`
section 4 — 391 named results (346 heading objects, 45 bold-led statements)
in 114 pinned blobs; 266 further `EXPLICIT` theorem-artifact objects are
mention lines and are listed, not registered.

## LF-1 — the logical-form register exists on 309 of 391 named results

**Statement.** Over the 391-object population, FORM_GRAMMAR_V1 (quantifier
prefix as an ordered list of `(Q, var, domain)`; matrix over `->`, `<->`,
`and`, `or`, `not` with atoms carrying a relation class in
`{EQ, LE, GE, OPT, CAUSAL, EXISTS, PRED}`; necessary/sufficient roles as index
paths; a `scope`) registers a closed form for **309** results: **271** by the
machine rules R1–R9 and **38** by hand on the frozen 40-object sample (seed
833; 2 kept `FORM_UNAVAILABLE` with written reasons). **82** results are
`FORM_UNAVAILABLE` (79 `NO_GRAMMAR_RULE`, 1 `EMPTY_STATEMENT`, 2 hand-refused).
Coverage is exactly `309/391`. Trailing remark sentences were dropped on 286
statements and are flagged per object.

**Assumptions.** The pinned census blob `709159c5…` and its `source_blob` /
`source_locator` pointers are the population; the statement region is the
bytes of `FREEZE_V1.md` 4.1; the grammar is the frozen rule list plus
amendment 01 items 1–7; a sentence with no rule is refused, never guessed.

**Dependencies.** `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
(population and pointers); `research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py`
(theorem-artifact rule, block-label emission predicate).

**Falsifiers.** A registered form whose canonical structure differs between
route A and route B (0 of 391 differ); a `FORM_UNAVAILABLE` object whose
conclusion sentence matches a rule of section 5; a hand entry whose key is
not in the seeded sample; a population count other than 391 from the frozen
rule; a snapshot that is not byte-identical to a fresh `git cat-file` read.

**Strongest parents.** Attempto Controlled English (Fuchs, Kaljurand & Kuhn
2008, DOI 10.1007/978-3-540-85658-0_3) and Montague (1970,
DOI 10.1111/j.1755-2567.1970.tb00434.x) own controlled-language-to-logic
parsing; Prawitz (1965) owns the hypothesis/conclusion discipline. Nothing
about parsing is claimed novel; the residual is the register on this
population with a stated coverage.

**Scope.** The 391 named results of the census population; nothing is said
about the 22162 other census objects or about the 82 unavailable results.

**Forbidden extrapolations.** `FORM_REGISTER_COMPLETE`,
`GRAMMAR_IS_COMPLETE`, `PARSER_IS_SOUND`, `EXTRAPOLATE_BEYOND_REGISTERED_SET`.

## LF-2 — AA16 quantifier-order discriminator, evaluable on 4 real results

**Statement.** Among registered forms, **5** carry a mixed `forall/exists`
prefix (AA16-applicable; 5 swapped-prefix forms generated); **4** carry a
warrant naming the established outermost quantifier (KF-4, ID-3 from their
proof/construction; QS-1, LLS-3 from inline argument; CC-T2 refused —
`NO_WARRANT_BYTES`). Stated and warranted order agree on **4/4**; the queue
is **empty**. Hostiles: a planted prefix swap into each evaluable form is
queued **4/4** (H1); a planted warrant flip is queued **4/4** (H2). Own null:
**0/200** shuffled draws reach the true agreement.

**Assumptions.** A hand warrant records the order the proof establishes;
the proof-first cue is read only when the conclusion sentence's own prefix
is mixed (amendment item 10).

**Dependencies.** LF-1; `HAND_REGISTER_V1.json` (warrants, content-anchored).

**Falsifiers.** A mixed-prefix registered form not in the applicable set; a
planted swap not queued; an agreeing object whose proof, read again, fixes
the witness before the universally quantified variable.

**Strongest parents.** `gmi-833-aa-fallacy-detectors-v1` FD-1 owns the
metadata-not-grep review-queue shape; classical quantifier-shift analysis
owns the fallacy.

**Scope.** 4 evaluable of 5 applicable of 309 registered.

**Forbidden extrapolations.** `NO_QUANTIFIER_SWAP_IN_CORPUS`,
`UNQUEUED_CLAIM_IS_SOUND`, any statement about the 300 non-mixed forms.

## LF-3 — AA17 converse/inverse discriminator, evaluable on 11 real results

**Statement.** **95** registered conditionals carry no role vocabulary
(AA17-applicable); **11** have an aligned warrant (opening assumption of a
proof block, or a hand-read assumption anchored to the antecedent's content).
Verdicts: direct or contrapositive proofs agree **11/11**; the queue is
**empty**. Hostiles: swapping the sides of each agreeing form is queued as
`CONVERSE` **11/11** (H3); negating both sides is queued as `INVERSE`
**11/11** (H4). A first-sentence lexical fallback tried before the receipt
produced 6/6 false converse alarms and was discarded (amendment item 8). Own
null: **0/200**.

**Assumptions.** Alignment by content-token overlap with a strict majority;
ties are not evaluable (5 hand warrants whose assumed side is pure `<MATH>`
are `UNALIGNED`).

**Dependencies.** LF-1; the AA17/AA18 partition by role vocabulary
(asserted disjoint).

**Falsifiers.** A direct proof aligned with the consequent (a false converse
alarm) on the hand-verified clean set — 0 of 57; a planted converse not queued.

**Strongest parents.** FD-1 (shape); the classical converse/inverse fallacy
taxonomy owns the definitions.

**Scope.** 11 evaluable of 95 applicable.

**Forbidden extrapolations.** `NO_CONVERSE_FALLACY_IN_CORPUS`,
`WARRANT_IS_A_PROOF_CHECK`.

## LF-4 — AA18 necessity-vs-sufficiency discriminator, evaluable on 10, queue 1

**Statement.** **57** registered forms are role-marked conditionals or
biconditionals (AA18-applicable); **10** carry an aligned warrant. **9**
agree; **1** is queued: `DL-3` (`… with equality iff q(z|x)=p(z|x) a.e.`)
whose proof block establishes the identity and argues neither direction of
the equality case — the reader had marked it `QUEUE_EXPECTED` before the
run, so real-data recall is **1/1**. Hostiles: promoting each agreeing `->`
to `<->` with a one-direction warrant is queued `IFF_ONE_DIRECTION` **12/12**
(H5); swapping the necessary and sufficient sides is queued `ROLE_SWAP`
**12/12** (H6). Own null: **0/200**.

**Assumptions.** Second-direction markers (`conversely`, `only if`, `exactly
when`, `iff`, …) or a hand `two_directions` flag decide whether an `iff` is
warranted both ways.

**Dependencies.** LF-1, LF-3 (shared alignment).

**Falsifiers.** A role-marked form in both AA17 and AA18 (0); a two-direction
proof queued as one-direction on the clean set (0 of 57).

**Strongest parents.** FD-1 (shape); the necessary/sufficient-condition
taxonomy owns the definitions.

**Scope.** 10 evaluable of 57 applicable.

**Forbidden extrapolations.** `QUEUED_CLAIM_IS_FALSE` (DL-3 is a review item
to cite the equality case, not a refutation), `NO_CONFUSION_REMAINS`.

## LF-5 — AA20 optimality-vs-run-search discriminator, evaluable on 31

**Statement.** **34** registered forms carry an `OPT` atom; **31** have a
known, non-protocol evidence mode. All 31 are warranted analytically, by a
mechanized proof, by exhaustive computer assistance or by a finite executable
certificate; **0** are warranted by a run search, so the queue is **empty**.
Hostiles: flipping each clean evidence mode to `EMPIRICAL_EXPERIMENT` is
queued **31/31** (H7); re-classing a run-warranted `PRED` atom as `OPT` is
queued **2/2** (H8). Own null: **25/200** shuffled draws reach the true
count — the row's own null is **not** beaten and is reported as such; the
pooled null is.

**Assumptions.** The census `proof_evidence_mode` label is the warrant;
`PROTOCOL_ONLY` and `UNKNOWN` are not evaluable.

**Dependencies.** LF-1; `CORPUS_INDEX_V1.json` evidence labels.

**Falsifiers.** An `OPT` atom with a run-search warrant not queued; the
count of OPT atoms differing between routes (0).

**Strongest parents.** FD-1 owns the `quantifier_class × evidence_mode`
predicate shape this row copies to `atom_class × evidence_mode`.

**Scope.** 31 evaluable of 34 applicable.

**Forbidden extrapolations.** `ALL_OPTIMALITY_CLAIMS_WARRANTED`,
`OWN_NULL_BEATEN` for this row.

## LF-6 — AA22 correlation-to-causal discriminator, evaluable on 5

**Statement.** **5** registered forms carry a `CAUSAL` atom (EA-5, EA-6,
DC-7, CL-5, EM-2); all 5 have a known evidence mode and none is a
observational run without an interventional marker, so the queue is
**empty**. Hostile H9 flips each to `STATISTICAL_EXPERIMENT` (removing the
interventional marker on the 4 that carry one) and is queued **5/5**. Own
null: **72/200** — not beaten, reported as such.

**Assumptions.** Interventional markers `do(`, `intervention`, `intervene`,
`randomi[sz]ed` in the atom text license a causal reading of a run.

**Dependencies.** LF-1.

**Falsifiers.** A `CAUSAL` atom warranted by an observational run not queued.

**Strongest parents.** FD-1 (shape); Pearl's interventional calculus owns
the observational/interventional distinction (not re-derived here).

**Scope.** 5 evaluable of 5 applicable.

**Forbidden extrapolations.** `NO_CAUSAL_OVERREACH_IN_CORPUS`,
`OWN_NULL_BEATEN` for this row.

## LF-7 — validation: two routes, a real clean set, a null that moves

**Statement.** Route B (a hand-written scanner, no regular expression, no
import from route A) agrees with route A on **391/391** forms by canonical
structure and on all five queues, evaluable sets and applicable sets by set
equality. The hand-verified clean set of **57** objects raises **0** alarms
across all five discriminators. The pooled agreement statistic is **60**;
over **200** shuffles of the warrant column across the whole registered
population the maximum is **38**, the exact mean `6633/200`, and **0/200**
reach 60. Dropping the warrant conjunct (H11, measured only) would queue
5 / 95 / 57 / 34 / 5 objects against the true 0 / 0 / 1 / 0 / 0. Grammar
hostiles H10 (5/5) and H12 (1/1) pass.

**Assumptions.** Canonical-structure equality of amendment item 17.

**Dependencies.** LF-1..LF-6.

**Falsifiers.** Any route disagreement; any clean-set alarm; a shuffle
reaching the true statistic.

**Strongest parents.** `gmi-833-census-registration-pass-v1` CRP-1..5 own
the two-route / set-equality discipline copied here.

**Scope.** The registered set at this package's tip.

**Forbidden extrapolations.** `DETECTOR_IS_SOUND`, `DETECTOR_IS_COMPLETE`.
