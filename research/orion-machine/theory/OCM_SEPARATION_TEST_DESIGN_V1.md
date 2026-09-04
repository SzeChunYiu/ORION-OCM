# Separation claim — registered-test design and pre-run audit

**Claim under test (directive, #194 comment 5539487737):** OCM "learns how to accomplish tasks, not
merely approximates outputs from large-scale exposure."
**Claim status: `NOT_ESTABLISHED`.** **Test status: `NOT_FROZEN` — pre-run audit
`FAILED_REACHABILITY_AND_COMPARATOR_MATCHING`.** Nothing was run. No arm exists.

Date: 2026-09-04 · Umbrella: #194 · Execution master: #197 · Machine-readable twin:
`OCM_SEPARATION_TEST_DESIGN_V1.json`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** This document designs the test the directive
requires, audits it *before* any run for reachability (both verdicts attainable), comparator
matching, and the root failure ledger's retained classes, and records why the audit fails. A test
that would have been frozen with an unreachable verdict is the ledger's
`STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE`; recording that here is the guard doing its job.

## 1. The claim as a falsifiable statement

Let `T` be a task family on the substrate (`reference/ocm_reference_semantics.py`), `π` the
*procedure-learner* arm (the substrate: acquires procedures with warrant through the channels,
composes them, revises under revocation), and `α` a *large-exposure approximator* arm (a learner
that fits an input→output map from many exposures and carries no warrant store). The directive's
claim is a separation:

> there exists a registered `(T, endpoint, budget)` such that `π` passes and `α` cannot pass, with
> `α` **budget- and information-matched** to `π`.

Endpoint candidates, in order of how much of the directive they test:

- **E1 (lifecycle):** after `k` transcripts and a hidden revocation `R` drawn from the admitted
  family `Γ`, emit the exact liveness signature of the acquired procedures (retain / retract /
  abstain per record), with no false retain and no false retract.
- **E2 (held-out composition):** emit the behaviour of a reminted composition of acquired
  procedures never shown as a whole.
- **E3 (channel):** acquire a procedure from a *single* instruction or demonstration and pass E2.

## 2. Reachability audit — can both verdicts occur?

| verdict | arm | reachable? | reason |
|---|---|---|---|
| PASS | `π` on E1 | **yes** | S3 of the substrate: with experimentation (closure) certificates, the live set after any `R ∈ Γ` is exact — 2,688/2,688 at n=4 |
| PASS | `π` on E2 | **yes** | S2: composition is exact by construction |
| FAIL | `α` on E1, exposure **unbounded** | **no** | the map from a complete transcript to the liveness signature is a finite function on a finite domain; an approximator with unbounded exposure to `(transcript, R) → signature` pairs represents it. The FAIL verdict is unreachable by construction: `STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE` (unfailable direction) |
| FAIL | `α` on E1, exposure **matched** to `π`'s `k` transcripts, **interface matched** (α also reads certificates and may call `V`) | **not established** | at equal information the fibre criterion (lane #200 Thm B) binds both arms equally: whatever is constant on the fibre is answerable by either; whatever is not is unanswerable by either. A separation would need a *computational* or *sample* lower bound against α at matched information — the programme has only cardinality bounds (LI-1, RCL-1c), which bind `π` too. Repository precedent: ME-X6 V2, a **learned capacity-matched untyped comparator tied** the typed mechanism 1,400/1,400 (#263) |
| FAIL | `α` on E1, interface **unmatched** (α gets endpoints only, `π` gets certificates) | yes — but it measures the channel, not the learner | this is lane #200's `I0 < I3`, already `PARENT_OWNED` (closed-world assumption), and the comparator is `HANDICAPPED_COMPARATOR` |
| FAIL | `α` on E3 (one demonstration) | not established | one demonstration under-determines the procedure for *any* learner unless the description budget is smaller than the information in the trace; then both arms identify it (version space of one point). A separation needs a registered prior/budget asymmetry — which is the information mismatch again |

**Result.** The PASS verdict is reachable for `π`. The FAIL verdict for `α` is reachable only in
the unmatched form, where it is not the directive's claim, or is unreachable / not established in
the matched form. **Reachability: FAILED.**

## 3. Comparator-matching audit

"Large-exposure approximator" and "procedure-learner" differ, once information is matched, in one
of two ways — and each is a registered failure class:

1. **Interface asymmetry** (α cannot read certificates / call `V`; π can): then the test measures
   the observation channel. `HANDICAPPED_COMPARATOR`. And it is parent-owned: the closed-world
   parent already says absence of a positive is not a negative.
2. **Interface parity** (α reads the same certificates and may call the same `V`): then a
   sufficiently capable α *is* a procedure learner — verifier-guided synthesis (CEGIS) is a
   function approximator with a checker in the loop. The two arms dispatch to the same information
   and the same oracle; the contrast collapses to how the arm is *labelled*. `VACUOUS_CONTRAST`.

There is a third reading in which the claim is a **resource frontier**, not a pass/fail: at matched
information, `π` reaches E1 with `k` transcripts and a warrant store of `H_0(L|B)` bits, while α
needs `k'` exposures and `c` parameters. That is a legitimate registered study, but it is lane
#202's kind of object — a trade-off, reported as a trade — and its lower-bound side is exactly the
non-cardinality bound the programme does not have. **Comparator matching: FAILED** for the claim
as a separation; **re-scoped** as a frontier study it is designable but has no theorem to
pre-register a margin from.

## 4. Failure-ledger audit

The brief named "the ledger's 16 failure classes"; the root `FAILURE_LEDGER.md` at `main`
`2dd2c67` carries **26** retained classes (control: the three correction rows are excluded). All 26
were read against the design; the ones that bind are listed, the rest are recorded as
not-applicable with the reason.

| class | binds? | how |
|---|---|---|
| `STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE` | **yes** | the unbounded-exposure FAIL verdict cannot occur (§2) |
| `HANDICAPPED_COMPARATOR` | **yes** | the only reachable FAIL is the interface-asymmetric one (§3.1) |
| `VACUOUS_CONTRAST` | **yes** | interface parity makes the arms the same learner (§3.2) |
| `DONOR_PRODUCT_TIE` | **yes** | expected outcome under parity; precedent ME-X6 V2 tie 1,400/1,400 |
| `NONIDENTIFIABLE` | yes | at matched information the distinction "learned a procedure" vs "approximated the map" is not identifiable from endpoint behaviour on a finite domain |
| `FORECLOSED_FAILURE_MODE` | yes | with closure certificates supplied, "did I have warrant?" is never a judgment for either arm — the failure the endpoint measures cannot occur (cf. ME-F1 G0e) |
| `AUTHORITY_LAUNDERING` | guarded | the design authorises no training or protected run; a pass would still not establish the directive's claim without the theorem in §3 |
| `PREMATURE_IMPLEMENTATION` | guarded | nothing implemented; recorded here so no arm is built before the audit passes |
| `TERMINAL_OVERSTATES_ITS_PROCEDURE` | guarded | terminal wording is `NOT_FROZEN`, not "refuted" — nothing was run |
| `DEGENERATE_PROBE_STATISTIC` | would bind | exact-signature accuracy has no dynamic range under parity (both 1.0) |
| `UNGATED_CONTROL_VERDICT`, `UNGUARDED_DEPENDENT_CHECK`, `CHECK_THAT_RUNS_AND_CANNOT_FIRE`, `CHECKER_STAGED_ON_THE_WRONG_SUBSTRATE`, `UNPINNED_SUBSTRATE_CONDITION`, `SILENT_MODEL_SUBSTITUTION`, `MANDATE_EXPLORATION_COLLAPSE`, `NONREPRODUCIBLE_FROZEN_ARTIFACT`, `REGISTERED_SCOPE_DIVERGENCE`, `RENDERED_SURFACE_SUBSTITUTED_FOR_THE_FACT`, `REPAIR_DOCUMENTED_NOT_LANDED` | n/a | run-time and custody classes; no run, no arm, no served model, no frozen artifact exists |
| `COVERAGE_GAP`, `REPO_COLLISION`, `DONOR_RECONSTRUCTION_FAILURE`, `FALSE_STRUCTURAL_ANALOGY`, `CENSORED_ROUTE` | n/a | literature-search classes; the parents in §3 are named, none reconstructed here beyond the lane records |

## 5. What a freezable test would need

1. a **registered non-rectangular natural class** (lane #200 §8) on which a *non-cardinality*
   lower bound separates learners at equal information — the same missing object that blocks RCL-C;
2. **bounded, matched exposure** `k` for both arms and **matched interface** (both read certificates,
   both may call `V`), with the approximator defined as a *capacity-matched untyped learner of the
   same interface* (the ME-X6 V2 construction), not as an external large model;
3. a **pre-registered margin** derived from the bound in (1), so a tie is a registered outcome, not
   a surprise;
4. planted controls: a `π` that launders (admits without `V`) must fail E1; an α given closure
   certificates must pass E1 (the no-alarm case proving the endpoint is not foreclosed against α);
5. the endpoint's dynamic range established on the substrate before freezing (both arms' verdicts
   observed to vary across the registered instances).

Until (1) exists, items (2)–(5) have nothing to derive a margin from and the test cannot be
frozen without violating the ledger's guards. **Terminal: `NOT_FROZEN__AUDIT_FAILED`.**

## 6. Non-consequences

Nothing here shows the directive's claim is false — the audit shows it is *not yet testable as a
separation*. No training, protected evaluation, natural-language competence, quantum or
superiority claim is authorised. No checkbox in #197 is closed.
