# Three mechanisms and the engineering choice

These are design options, not reproduced algorithms or benchmark claims.

| Option | Acquired object and consumer | Extra requirement | Decision |
|---|---|---|---|
| A. Explanation-based proof compilation into an ordinary theorem | A machine-selected subproof boundary becomes a native `$p`; ordinary typed substitution/search uses it | Exact projection, alias/subsumption screening, full native admission | **Implement first**: reuses the existing theorem representation |
| B. Explanation-based search-control learning | Explicit conditions prefer an existing assertion or binding during search | Traces must retain alternatives and failures, plus an architectural explanation model | Next if selection, rather than missing reusable subproofs, is the measured failure stage |
| C. SEPIA-style trace-model inference | A finite automaton proposes sequences of existing proof actions, executed by the native prover | Typed arguments, goal transitions, state merging and charged failed paths | Later if profitable composition requires control flow that theorem boundaries cannot express |

## Primary donor for A/B: Minton, 1988

Sections 2 and 4 describe explanation-based generalization using a supplied
domain theory and operationality criterion. PRODIGY learns search-control
conditions from traces; explanation construction uses an architectural theory,
and utility includes applicability checking as well as saved search. Rules can
be removed when later use does not pay.
[AAAI primary paper](https://cdn.aaai.org/AAAI/1988/AAAI88-100.pdf).

A is an adaptation of proof compilation, not a reproduction of PRODIGY.
Its initial operationality criterion is a bounded native proof cut. B is closer
to PRODIGY's control-rule object, but success-only proof traces cannot silently
supply explanations of failed search alternatives. Neither source establishes
that the proposed OCM task pool contains useful cuts or preferences.

## Native interface for A: Metamath

The book's sections 4.1.3–4.1.4 define proved assertions, ordered mandatory
hypotheses, simultaneous substitution and distinct-variable obligations.
A new derived theorem needs a checked proof under its actual context; its future
instances use the ordinary assertion mechanism.
[Book, displayed edition 2019-06-02](https://us.metamath.org/downloads/metamath.pdf).

Use the existing ordinary-parent contract in full. The earlier six atomic
renamings do not qualify composite or repeated substitutions. Before evaluation,
qualify the selected theorem's actual substitution/type/DV domain and prove
normalization back to the original library. Do not substitute a custom macro
executor for this missing qualification.

## Primary donor for C: SEPIA, 2015

Sections 2–3 describe MINT state merging over Coq tactic traces, with parameters
and guards. The inferred model may permit unseen sequences; proof search actually
executes the proposed tactics and arguments in Coq. The source also preserves
semicolon behavior across generated subgoals.
[Primary paper, v1](https://arxiv.org/pdf/1505.07987v1).

A Metamath adaptation must preserve corresponding typed goal and premise
dependencies. A model path is a proposal, not a proof. This is additional
machinery, so first establish whether ordinary theorem acquisition suffices.

## Why A is the smallest decisive next step

No new semantic object is needed: a typed cut is turned into an ordinary
assertion contract and proof. The learner selects reusable structure from
experience; the existing prover supplies applicability and warrant. If whole
training-theorem accumulation is equally useful, adopt that simpler mechanism.
All-alias limits new-theorem acquisition here; it does not rule out learned
selection/applicability utility. Keep current empty eligibility. Search telemetry
can support a separately registered EBL/control-selection diagnosis, without
endless cut-size expansion. Allocations and revival branches remain proposed.
