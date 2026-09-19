# FREEZE — `gmi-833-aa-logical-form-register-v1` (issue #833, section AA)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed alone, before any executor,
test, receipt, register, theorem note or workflow file of this package exists.
`git log --reverse -- research/gmi-833-aa-logical-form-register-v1/` must show
this file, alone, first. This file is never edited after the first receipt
exists; corrections go into a numbered amendment file.

## 1. Source pin

- `source_main` = `b5193f32db01944774e9527b06e63dec2fac887d`
- issue comment under reconciliation: `5684607872`, anchor
  `### AA. Recursive loophole / logic-gap closure`
- live comment bytes at freeze: 39218 (LF only), fetched 2026-09-19 before
  this file was written.
- frozen census: `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json`
  blob `709159c53c6284366aaf1f05380f5fada8d81a98` (22553 objects,
  `frozen_source_sha` `2fffb14447193cbfbed3224508a077f2d4f5d2dd`).
- the finding this package answers:
  `research/gmi-833-census-registration-pass-v1/DECIDABILITY_V1.json` blob
  `b154d5c2a49902665f3e35462a7ad4ad53122651` — 13 AA rows carry
  `NO_REGISTERED_DISCRIMINATOR` because no register field carries the
  statement's logical form.

## 2. Claim ceiling

`LOGICAL_FORM_REGISTER_AND_REVIEW_QUEUE_V1`

This package builds a **register** (a per-object record of the statement's
logical form, read from the pinned source bytes under an exact grammar) and
runs **metadata predicates** over it. Every predicate emits a **review
queue**, never a verdict: a queued object is an obligation to look, an
unqueued object is not thereby correct. Coverage is reported as
`registered / population` and no claim extends past the registered set.

## 3. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Search for quantifier-order mistakes (`forall/exists` swaps).
    - [ ] Search for converse/inverse fallacies.
    - [ ] Search for necessity-vs-sufficiency confusion.
    - [ ] Search for optimality-vs-selection confusion.
    - [ ] Search for empirical-correlation-to-causal claims.

Row ids as used by `DECIDABILITY_V1.json`: AA16, AA17, AA18, AA20, AA22.

**No neighboring row is earned here.** Explicitly NOT earned, with the
attribution fixed now: AA23 (identifiability), AA28 (encoding equivariance),
AA29 (objective / scalarization form), AA30 (search budget), AA32 (ecology
sample), AA34 (leakage ledger), AA35 (sample size), AA36 (latent structure)
— each needs **experiment metadata** that a logical-form register does not
carry; the lever for them is an experiment-ledger register, not this one.
AA19, AA21, AA31, AA37 are already earned elsewhere and are not re-earned.
AA24–AA27 and AA33 belong to the `assumptions`-ledger discriminators of the
census pass and are not touched. No row of AB, AC or AD is earned.

### 3.1 Closure rule per row (fixed before any number is read)

A targeted row is reconciled to `- [x]` only if ALL hold:

1. its discriminator is **evaluable on >= 1 registered object** of the real
   population (not only on a planted fixture);
2. the discriminator **ran over the whole registered population** and the
   receipt states the evaluable count and the queue;
3. every planted hostile of that row is **detected** with `applicable: true`;
4. the **no-alarm case** on the hand-verified clean set raises 0 alarms;
5. the two routes agree on the row's queue by **set equality**;
6. the null of section 9 is beaten on the pooled agreement statistic, and the
   row's own agreement statistic is reported (a row whose own null is not
   beaten is reported as such in the reconciliation line).

A row failing any clause stays `- [ ]` and is reported NEGATIVE with the
failing clause named. Rows are never closed by narrowing their meaning:
"quantifier-order mistakes" means any permutation of a mixed `forall/exists`
prefix, "converse/inverse" means both `B -> A` and `not A -> not B` for a
stated `A -> B`, "necessity-vs-sufficiency" means any mismatch between the
stated role marking and the warranted direction, "optimality-vs-selection"
means an optimality assertion warranted by a run search, "correlation-to-
causal" means a causal assertion warranted by an observational run.

## 4. Population rule (stated, not cherry-picked)

The population is the census's own enumeration; nothing is re-enumerated.

    P = { o in CORPUS_INDEX_V1.scientific_objects :
          o.id_kind == "EXPLICIT"
          and o.source_path ends with ".md"
          and basename(o.source_path) matches /THEOREM/i        (ledger-gate theorem-artifact rule)
          and ( o.statement starts with "## "                     (heading object of a named result)
                or o.statement matches
                   ^\*\*(Theorem|Lemma|Proposition|Corollary|Law|Claim|[A-Z][A-Z0-9]*-[A-Z0-9.]+)\b ) }
    deduplicated by (source_path, object_id), keeping the smallest locator.

Computed at freeze time by this rule against the pinned census: **391**
distinct named results (346 heading objects + 45 bold-led statements) in
**114** pinned blobs. Vendored `raw/` copies are members like any other and
are flagged `vendored: true`, never dropped. The 266 remaining `EXPLICIT`
theorem-artifact objects are mention lines (a result cited inside another
result's body) and are not statements; they are counted and listed as
`NOT_A_STATEMENT_LINE`, not silently omitted.

### 4.1 Statement bytes

For a heading object the statement region is the pinned blob (`source_blob`)
from the line after `source_locator` up to the first of: the next `## `
heading, the first `### ` heading, the first block-leading bold label
(`**Proof.**`, `**Falsifiers.**`, …) other than a statement label, or a
`# ` heading. For a bold-led object it is the text after the bold label on
that line, continued to the same stops. Fenced code and `$$`/`\[ \]` display
math are replaced by the single token `<MATH>`. `Status: …` lead lines are
dropped. The statement is snapshotted with its blob sha into
`STATEMENT_SNAPSHOT_V1.json`; the executor re-reads the blobs through
`git cat-file` when the repository is reachable and asserts the snapshot is
byte-identical, and degrades to a distinct `BLOBS_UNREACHABLE` state
(never a pass) when it is not.

### 4.2 What is parsed

Only the **hypothesis chain and the conclusion sentence** of the statement
region: leading sentences opening with `Let | Suppose | Assume | Fix |
Consider | Given | Under | Whenever | For (every|all|each|any)` are
hypotheses; the first sentence that is not a hypothesis is the conclusion;
everything after the conclusion sentence is trailing remark, dropped and
flagged `trailing_dropped`. A statement that never reaches a conclusion
sentence is `FORM_UNAVAILABLE / NO_CONCLUSION_SENTENCE`.

## 5. The grammar (FORM_GRAMMAR_V1), declared before any statement is read

    form            := { prefix, matrix, roles, scope }
    prefix          := [ (Q, var, domain) ... ]      ordered, outermost first
    Q               := forall | exists
    matrix          := expr
    expr            := atom | ["not", expr] | ["and", expr, expr] | ["or", expr, expr]
                     | ["->", expr, expr] | ["<->", expr, expr]
    atom            := ["atom", text, rel]           text = normalized clause
    rel             := EQ | LE | GE | OPT | CAUSAL | EXISTS | PRED
    roles           := null | { sufficient: path, necessary: path }
                       (for "->": sufficient = left, necessary = right;
                        for "<->": both sides carry both roles;
                        paths are index lists into the matrix)
    scope           := the finite object family the statement ranges over:
                       the outermost quantifier's domain phrase if any, else
                       the hypothesis chain's declared family, else "UNSCOPED"

Sentence rules, tried in this order on the conclusion sentence (hypotheses
`H1..Hk` are folded as `(H1 and … and Hk) -> C` when k >= 1; a `Let V be D`
hypothesis contributes `(forall, V, D)` to the prefix instead of a conjunct):

    R1  IFF        "X iff Y" | "X if and only if Y" | "X exactly when Y"
                   | "X is necessary and sufficient for Y"        -> ["<->", X, Y]
    R2  IF-THEN    "If X, then Y" | "If X, Y" | "If X then Y" | "Whenever X, Y"
                   | "When X, Y" | "Y if X" | "Y whenever X" | "X implies Y"
                   | "Y provided (that) X"                        -> ["->", X, Y]
    R3  ONLY-IF    "X only if Y"                                  -> ["->", X, Y]
    R4  UNLESS     "Y unless X"                                   -> ["->", ["not", X], Y]
    R5  NECESSARY  "X is necessary for Y" | "Y requires X" | "Y needs X"
                                                                  -> ["->", Y, X]
    R6  SUFFICIENT "X is sufficient for Y" | "X suffices for Y"    -> ["->", X, Y]
                   "It suffices that X" | "It is sufficient that X"
                                                                  -> ["->", X, GOAL]  GOAL = heading title atom
    R7  FORALL     "For every|all|each|any V (in|of|with D)?, S"   -> prefix += (forall, V, D); parse S
                   "Every V S" | "Any V S" | "No V S" (-> forall V, ["not", S])
    R8  EXISTS     "There exist(s) V (such that|with|for which) S" -> prefix += (exists, V, D); parse S
                   "S for some V"                                 -> prefix += (exists, V, -)
    R9  ATOMIC     a sentence with no connective but a relational cue:
                   EQ  ("is exactly", "equals", "is precisely", "=")
                   LE  ("at most", "no more than", "<=", "\le", "bounded above by")
                   GE  ("at least", "no fewer than", ">=", "\ge", "bounded below by")
                   OPT ("optimal", "optimum", "minimal", "minimum", "maximal",
                        "maximum", "argmin", "argmax", "minimizer", "maximizer", "best")
                   CAUSAL ("causes", "caused by", "causal", "do(", "intervention", "intervene")
                   EXISTS ("exists", "there is a", "attained")
                   the first cue in the sentence fixes `rel`     -> ["atom", text, rel]
    R10 no rule matched                                          -> FORM_UNAVAILABLE / NO_GRAMMAR_RULE

Inside X and Y, `and` / `or` at clause level split into ["and"/"or", …]
and a leading `not` / `no` / `never` / `fails to` wraps ["not", …]. Every
atom also carries the rel class assigned by the R9 cue list (PRED when none),
so OPT / CAUSAL atoms are visible wherever they sit in the matrix. Nothing
outside this list is a rule; a statement the list does not fit is
`FORM_UNAVAILABLE`, never guessed.

### 5.1 Hand registration

A random sample of **40** objects drawn from the `FORM_UNAVAILABLE` set
(sorted by `(source_path, object_id)`, drawn by a 64-bit LCG
`x <- 6364136223846793005*x + 1442695040888963407 mod 2^64`, seed **833**,
index `= (x >> 33) mod remaining`, without replacement) is read by hand and
registered `REGISTERED_HAND` with a form in the same grammar, or kept
`FORM_UNAVAILABLE` with a written reason when the statement has no closed
logical form (e.g. a remark, a definition, a derivation fragment). The hand
set is also the **hand-verified clean set** of the no-alarm case: for each
hand-registered object the warrant of section 6 is read from the proof /
executor and registered by hand too. The hand set is drawn once; it is
never re-drawn to change a result.

## 6. The warrant register (what the evidence establishes)

Each object also gets a `warrant` record, read from bytes **outside** the
statement region of the same pinned blob, so the discriminators compare two
independently registered columns:

- `proof_opening`: the first sentence of the `**Proof.**` / `**Proof
  sketch.**` block, the `### Proof` subsection, or an inline `Proof.`
  sentence; parsed with R7/R8 for its first quantifier cue
  (`fix | let … be arbitrary | for each | given any | for every` = forall-first;
  `take | choose | construct | exhibit | there is | consider the` =
  exists-first) and with the hypothesis rule for its opening assumption
  literal (`suppose | assume | let | given X` -> literal X with polarity).
- `falsifier`: the `**Falsifiers.**` / `**Counterexample.**` block text.
- `evidence_mode`: the census `proof_evidence_mode` label, copied.
- `quantifier_class`: the census label, copied **for measurement only** —
  it is a regex over the same statement text and is not used as a warrant.
- `WARRANT_UNAVAILABLE` when none of the above exists.

Alignment of a warrant literal with a side of the matrix is by content-token
overlap (lower-cased alphanumeric tokens of length >= 3, stop-words removed;
`<MATH>` tokens ignored): the side with the strictly larger overlap is the
aligned side; ties are `UNALIGNED` and not evaluable.

## 7. The five discriminators (metadata predicates over the register)

    AA16  applicable: prefix contains both forall and exists.
          For each such object generate every non-identity permutation of the
          prefix (the swapped forms). evaluable: proof_opening has a first
          quantifier cue, or a hand warrant names the established order.
          QUEUE when the stated outermost quantifier differs from the
          warranted outermost quantifier.
    AA17  applicable: matrix top is "->" and the statement carries NO role
          vocabulary (necessary, sufficient, suffices, requires, needs,
          only if, iff, if and only if).
          evaluable: an aligned proof_opening literal or an aligned falsifier.
          QUEUE CONVERSE when the warrant assumes the consequent (aligned
          with the right side); QUEUE INVERSE when the warrant assumes the
          negation of the antecedent or the falsifier negates the antecedent
          rather than the consequent.
    AA18  applicable: matrix top is "->" or "<->" and the statement carries
          role vocabulary (the complementary class of AA17), or the matrix
          top is "<->".
          evaluable: as AA17.
          QUEUE IFF_ONE_DIRECTION when the stated matrix is "<->" and the
          warrant establishes one direction only (no second-direction marker
          `conversely | only if | for the converse | the other direction`);
          QUEUE ROLE_SWAP when the stated necessary side is the side the
          warrant assumes (a sufficiency proof for a necessity claim) or
          vice versa.
    AA20  applicable: some atom has rel OPT.
          evaluable: evidence_mode != UNKNOWN.
          QUEUE when evidence_mode is EMPIRICAL_EXPERIMENT or
          STATISTICAL_EXPERIMENT (an optimality assertion warranted by a run
          search). Declared clean: OPT atoms with ANALYTIC_DEDUCTIVE,
          MECHANIZED_PROOF, COMPUTER_ASSISTED_EXHAUSTIVE or
          FINITE_EXECUTABLE_CERTIFICATE warrant; PROTOCOL_ONLY is NOT
          evaluable (no run took place).
    AA22  applicable: some atom has rel CAUSAL.
          evaluable: evidence_mode != UNKNOWN.
          QUEUE when evidence_mode is EMPIRICAL_EXPERIMENT or
          STATISTICAL_EXPERIMENT and the atom text carries no interventional
          marker (`do(`, `intervention`, `intervene`, `randomi[sz]ed`).

AA17 and AA18 partition the conditional forms by the presence of role
vocabulary, so no object is double-counted between them; the partition is
asserted.

## 8. Hostiles (each carries `applicable`; a vacuous hostile FAILS the run)

    H1  AA16 prefix swap planted into a copy of every applicable-and-evaluable
        real form; each copy must be queued (recall n/n).
    H2  AA16 warrant swap (statement kept, warrant order flipped); queued.
    H3  AA17 converse planted (sides swapped) into every evaluable "->" form; queued.
    H4  AA17 inverse planted (both sides negated); queued.
    H5  AA18 promotion "->" to "<->" with a one-direction warrant; queued.
    H6  AA18 role swap (necessary/sufficient vocabulary flipped); queued.
    H7  AA20 evidence flip: OPT atom, ANALYTIC -> EMPIRICAL; queued.
    H8  AA20 atom flip: an EMPIRICAL-warranted PRED atom re-classed OPT; queued.
    H9  AA22 evidence flip on a CAUSAL atom; queued.
    H10 grammar hostile: a planted "If X, then Y" must parse to ["->", X, Y]
        and "Y if X" to the same form; "X iff Y" to "<->"; "X is necessary
        for Y" to ["->", Y, X]. A parser that gets any of these wrong fails.
    H11 loosening hostile (measured, never adopted): dropping the warrant
        conjunct — every applicable object queued — reports the inflation.
    H12 a statement with no cue ("This is the positive result.") must be
        FORM_UNAVAILABLE, never an atom.

No-alarm case: the hand-verified clean set (section 5.1) raises 0 alarms on
every discriminator; a single alarm on it fails the package.

## 9. Null

Warrants are shuffled across the evaluable objects (200 draws, LCG of 5.1,
seed 2026, indices from bits >> 33). The statistic is the pooled number of
**agreeing** (stated, warranted) pairs over all five discriminators. The true
register must exceed every one of the 200 draws (0/200 reach it); the
per-row statistics and the maximum shuffled value are reported. If the
pooled null is not beaten the package reports it and closes no row.

## 10. Two routes

- Route A `logical_form_register_v1.py`: extraction, regex sentence rules,
  register writer, discriminators, hostiles, null.
- Route B `independent_form_oracle_v1.py`: imports nothing from A; reads
  `STATEMENT_SNAPSHOT_V1.json`, re-tokenizes with a hand-written token
  scanner (no `re` on the sentence body), re-derives prefix, matrix and rel
  classes, recomputes every discriminator from its own parse, and must agree
  with A by **equality on every registered form and every queue**. Any
  disagreement is listed in the receipt as `ROUTE_DISAGREEMENT` and the
  package does not close the affected row.

## 11. Forbidden promotions

- `AA_FALLACY_SWEEP_COMPLETE`, `ALL_FALLACIES_DETECTED`,
  `CORPUS_FREE_OF_FALLACY`, `NO_CONFUSION_REMAINS`.
- `QUEUED_CLAIM_IS_FALSE`, `UNQUEUED_CLAIM_IS_SOUND`.
- `FORM_REGISTER_COMPLETE`, `ALL_NAMED_RESULTS_REGISTERED`,
  `GRAMMAR_IS_COMPLETE`, `PARSER_IS_SOUND`.
- `EXTRAPOLATE_BEYOND_REGISTERED_SET`: no statement about the
  `FORM_UNAVAILABLE` objects or about the 22162 census objects outside P.
- `WARRANT_IS_A_PROOF_CHECK`: alignment by token overlap is a pointer, not a
  verification of the proof.
- `ROWS_AA23_AA28_AA29_AA30_AA32_AA34_AA35_AA36_EARNED`.
- `RECURSION_EXHAUSTED`, `ANALYTIC_PROOF`.

## 12. Parent ownership (declared before implementation)

- `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json` blob
  `709159c53c6284366aaf1f05380f5fada8d81a98` — owns the population, every
  `source_blob` / `source_locator` pointer and the `proof_evidence_mode` and
  `quantifier_class` labels copied here.
- `research/gmi-833-census-registration-pass-v1/DECIDABILITY_V1.json` blob
  `b154d5c2a49902665f3e35462a7ad4ad53122651` — owns the finding (13 rows
  without a registered discriminator) and the row ids.
- `research/gmi-833-aa-fallacy-detectors-v1/RESULT_V1.json` blob
  `ed4045e835ea7b980bb3b04ced00132e4130e830` — owns the review-queue
  claim shape and the metadata-not-grep discipline (FD-1) this package copies.
- `research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py` blob
  `c11fc4a52304f0b827bf59ae3046dac2e0afb514` — owns the theorem-artifact
  rule (`THEOREM` in the basename) and the block-leading bold-label
  emission predicate reused for `**Proof.**` / `**Falsifiers.**`.
- External parents (entered from field knowledge, CITE-TF, not checked
  against a live source; AC05 is not earned): Montague, R., "Universal
  Grammar", Theoria 36 (1970), DOI 10.1111/j.1755-2567.1970.tb00434.x —
  formal-grammar reading of natural-language statements; Prawitz, D.,
  *Natural Deduction* (1965) — hypothesis/conclusion discipline for the
  hypothesis-chain folding; Sowa, J. F., *Conceptual Structures* (1984) —
  controlled natural language to logical form; Fuchs, N. E., Kaljurand, K.
  & Kuhn, T., "Attempto Controlled English for Knowledge Representation",
  Reasoning Web 2008, DOI 10.1007/978-3-540-85658-0_3 — the controlled-
  English-to-logic pipeline whose sentence patterns R1–R9 resemble.
  Nothing about controlled natural language, natural deduction or
  formal-grammar parsing is claimed novel here.

**Residual contribution of this tranche:** a logical-form column on the
census population with a stated coverage figure, a warrant column read from
bytes outside the statement, and the five row discriminators as predicates
over those two columns with detected hostiles, a hand-verified no-alarm set
and a shuffled-warrant null.

## 13. Decision rules for the report

- Coverage is `registered / 391` with MACHINE / HAND / FORM_UNAVAILABLE
  broken out by reason; the CORE states it in its first table.
- A row is POSITIVE only under 3.1; otherwise NEGATIVE with the failing
  clause as attribution and the lever named (warrant sparsity -> proof-
  opening registration; grammar miss -> add a rule in v2 under a new freeze;
  route disagreement -> fix and re-run before any closure).
- `s6_instruction_followed: true` unless a clause of this freeze had to be
  overridden, in which case the receipt records `false` and
  `audit_shape_disclosed: POST_HOC_SUSPECT`.
