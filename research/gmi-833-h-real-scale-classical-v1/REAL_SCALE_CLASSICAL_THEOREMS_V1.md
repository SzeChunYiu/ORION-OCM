# Real-scale classical Section-H derivation — named results V1

All statements are about this package's four registered scopes
`SIGMA_H01`–`SIGMA_H04` (`FREEZE_V1.md` Section 3) at `source_main`
`91c6d2876ba80c517a186e28fce3bdbe4e3fc218`. Exact numbers are in
`RESULT_V1.json`; every one is reproducible from the committed receipts by
`python3 -I -B real_scale_classical_v1.py`.

---

## RSC-1 — the single-scope closure rule

**Statement.** A Section-H named-family row is closed by this package only if
all eleven requirement certificates for that row carry one and the same scope
identifier, that identifier is one of `SIGMA_H01..SIGMA_H04`, and no certificate
is imported from any other scope. The checker enumerates the eleven
certificates per row, refuses a row whose certificates carry more than one
`sigma`, and refuses any certificate carrying `SIGMA_4F`.

**Quantifiers.** For every row `r` in the four, for every gate `g` in `R01..R11`.

**Assumptions.** The scope tuple of PR #997 `FGS-2`: `(family row, grammar,
ecology, budget, freeze, protected interface)`.

**Why it is the rule.** `FGS-2` proves that certificates at scopes `sigma_j` do
not compose into eligibility at a target `sigma*` unless every `sigma_j =
sigma*` or a transport theorem is registered. `gmi-833-h-family-requirement-ledger-v1`
`HRL-1` lists `CROSS_SCOPE_GATE_COMPOSITION` among its forbidden
extrapolations. `gmi-833-h-neutral-four-family-v1` holds ten of the eleven
coordinates for these same four rows at `SIGMA_4F`, a finite `Z3` scope; adding
a real-scale eleventh certificate at a different scope and declaring the
conjunction is exactly the forbidden move. This package therefore imports none
of those ten and earns eleven at each of its own scopes.

**Falsifiers.** A closed row whose gate list contains two distinct `sigma`
values; a closed row citing a `SIGMA_4F` artifact as gate evidence; a transport
theorem from `SIGMA_4F` to any of these scopes (which would make the composition
legitimate and this rule unnecessarily strict).

**Strongest parents.** PR #997 `FGS-2`; PR #1023 `HRL-1`.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`,
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`.

---

## RSC-2 — the real-scale instantiation

**Statement.** At each of the four scopes the registered real-scale conditions
of `FREEZE_V1.md` Section 7 hold: every input value is read from `D1`, `D2` or
`D3` and verified by sha256 at run time; `n_fit >= 100,000` and
`n_held >= 20,000`; at least two arms are fitted at that scale under one slice
rule and one rationalisation; every claimed number is computed on rows no arm
was fitted on, in exact arithmetic; and the charged cost model is evaluated at
the real index-set size.

**Quantifiers.** For every scope, for every claimed number.

**Assumptions.** The `D1`–`D3` digests of `FREEZE_V1.md` Section 4; the slice
rule of `FREEZE_V2_ADDENDUM.md` Section 4; the rationalisation denominator
`10^9`, and for the `SIGMA_H04` landmark arm the registered dyadic kernel
rounding at `2^30`, which is disclosed rather than silent.

**Falsifiers.** A claimed number reproducible from fewer than 100,000 real
fitted rows; a byte used that no Section-4 digest covers; a held-out row that an
arm was fitted on; a float surviving into any claim.

**Scope.** This is real-scale **at this definition**. It is not frontier scale,
not a statement about data outside `D1`–`D3`, and not a statement about
ecologies other than `E_H01`–`E_H04`.

**Forbidden extrapolations.** `REAL_SCALE_VALIDATION_COMPLETE`,
`FRONTIER_SCALE_VALIDATION`.

---

## RSC-3 — blind recovery of four structural classes at real scale

**Statement.** One grammar — `grammar_v2`, 12,614 candidate pairs, one digest,
unchanged between scopes and verified identical before and after every search —
selects, without receiving any family name, family identifier or
family-specific candidate list, a program whose post-hoc structural class is the
class predicted from the ecology specification alone, at each scope where the
row closes. The class is attached after selection by a classifier that reads the
expression tree and nothing else, and it is confirmed by an independently
implemented classifier in `independent_oracle_v1.py` that uses symbolic second
differences on a different grid.

**Quantifiers.** For each closed row; the open rows are named with their
recovered class and their single-stage attribution.

**Assumptions.** The search procedure of `FREEZE_V1_ECOLOGY_ADDENDUM.md` A8 as
amended by `FREEZE_V1_SEARCH_AMENDMENT.md` and `FREEZE_V2_ADDENDUM.md` L1–L4;
the ecology definitions of A1–A4; the loss at each scope being that scope's own
already-frozen protected interface.

**Falsifiers.** A selection that differs from the predicted class; a grammar
digest that differs between two scopes; a family string reaching the generator;
a negative twin at which the same class is selected; a remint slice at which a
different class is selected; the two routes disagreeing on the class.

**What the independent route covers, exactly.** `independent_oracle_v1.py`
imports no module of this package — enforced by an `ast` import scan and a
`sys.modules` assertion, not by a comment — and re-derives, with its own
`(num, den)` rational arithmetic, its own parser, its own evaluator and its own
optimiser: the grammar's cardinality (by closed-form recursion rather than by
enumeration), the structural classification of every winner, the exact held-out
arithmetic on the committed real verification slices, and the charged-cost
crossovers. It re-derives the **selection** by re-ranking the committed survivor
set — the top 8 of the frozen screen — on 200 committed real search-slice rows
under its own exact-rational coordinate descent, and must agree on the winner's
structural class. **It does not re-run the full 12,614-pair enumeration on the
full search slice**, because it has no access to `D1`–`D3`; the independent
re-derivation of the selection is therefore of the decisive comparison among the
survivors, not of the screen that produced them. A second float optimiser inside
stage 1 (`route B`) is recorded as a diagnostic only, including where it
disagrees; `FREEZE_V1.md` Section 9 names the source-separated oracle as the
`R10` route and that is what the gate reads.

**Strongest parent.** `gmi-833-h-neutral-four-family-v1`, which owns this
construction at finite scope. **No certificate of it is counted here.**

**Forbidden extrapolations.** `ALL_KNOWN_FORM_RECOVERY`,
`UNIVERSAL_GRAMMAR_NEUTRALITY`, `NAMED_FAMILY_ROW_CLOSED_OUTSIDE_THE_FOUR`.

---

## RSC-4 — exhaustive minimality lower bound

**Statement.** For each selected program, no expression of the frozen grammar
with strictly fewer nodes realises the selected body denotation or the selected
head denotation on the registered probe grid. This is established by exhaustive
enumeration of all 116 body expressions of at most 3 nodes and all 8,155 head
expressions of at most 5 nodes, and by comparing denotations, not syntax.

**Quantifiers.** For every selected program, over the whole frozen grammar.

**Assumptions.** The probe grid of `grammar_v1.PROBE_1D`; equality of
denotation on that grid as the identity criterion.

**Falsifiers.** A smaller expression with the same denotation on the grid; a
pair of expressions the grid fails to separate that a larger grid would.

**Forbidden extrapolations.** This bounds description length **inside `G_R` on
the probe grid**. It is not a bound over all programs, all grammars, or all
representations, and it says nothing about statistical sample complexity.

---

## RSC-5 — charged-cost crossover at real scale

**Statement.** Under the uniform cost model of
`FREEZE_V1_ECOLOGY_ADDENDUM.md` A5, each scope reports the exact integer
crossover `m*`: the smallest index-set size at which the sign-quantised lookup
table costs strictly more than the selected compact composed program at that
same size. `m*` is verified to be the smallest by exhaustive ascent, and the
checker rejects a claimed `m*` for which `m*-1` already crosses. `SIGMA_H04`
additionally reports `q*`, the smallest landmark count whose charged cost
exceeds the affine arm's while its exact held-out squared error is still lower,
and `q_b*`, the kernel-trick crossover against the explicit degree-two basis.

**Quantifiers.** For each scope; exactly, in integers.

**Assumptions.** One charged unit per evaluated grammar operation and per stored
rational; the sign quantiser as the registered tabulation.

**Falsifiers.** A crossover that is not the smallest; a cost model under which
the ordering reverses (the model is registered, not derived, and a different
registered model is a different claim).

---

## RSC-6 — the boundaries the first pass exposed

**Statement.** Three of the four V1 structural predictions failed, each for one
identifiable reason, and each reason is a property of the registered procedure
rather than of the family:

1. **A head node budget of 4 excludes parameterised state.** A `G_R` expression
   over three distinct leaves needs `2n-1 = 5` nodes, so no expression using
   `S`, `STATE` and `BIAS` together exists at budget 4, and no leaky
   accumulator, decayed register or counter-with-forgetting is in the search
   space at all. A grammar that cannot express a family's mechanism cannot
   recover it, and the failure is a budget fact, not evidence about automata.
2. **A time-ordered sliding-window ecology is not a regression ecology.** At
   `SIGMA_H02` under time order the blind search preferred `ADD(S,STATE)` — an
   integrator, i.e. an infinite-impulse-response linear filter — over the affine
   score, because real audio carries exploitable temporal autocorrelation
   beyond the 32-lag window. That is a true fact about the ecology. A row about
   regression presupposes exchangeable observations; a sliding-window
   presentation does not supply them.
3. **Squared error is the identity-link criterion.** Minimising squared error
   cannot express a preference for a link function, so no link can be recovered
   under it, whatever the response. Recovering a link requires searching under
   the ecology's own criterion — here the absolute closeness that
   `FREEZE_V1_ECOLOGY_ADDENDUM.md` A3 had already frozen as that scope's
   protected interface.

**Scope.** These are statements about this package's procedure at these scopes.
They are not claims that the finite parent's `SIGMA_4F` results are wrong — at
that scope they stand — and they are not claims about the families themselves.

**Consequence.** Each is a constraint on **method**, and each named its own
removal; the removals are the levers of `FREEZE_V2_ADDENDUM.md` Section 3. None
of them is a `BLOCKED_STRUCTURAL` obstruction, which is consistent with PR
#1023 `HRL-4`.

**Falsifiers.** A head budget of 4 under which a parameterised state update is
expressible; an exchangeable presentation at `SIGMA_H02` under which the search
still prefers a stateful head; a squared-error search that recovers a link.

---

## What none of these results says

No result here licenses `INDEPENDENT_TEAM_REPLICATION`, `M5`, `EV4` or `EV5`.
Both routes, both hosts and both interpreter modes are intra-package;
intra-package agreement is not independent replication, and the corpus has zero
`M5` instances. No result here closes, touches or bears on any of the other 39
named-family rows of Section H, on the aggregate Section-H rows, or on any other
section of Issue #833.
