# What main already supplies for #214 FNA-1

**Base: `dff3acadb78dfef161d122d00f20ebb30ab8bb51` (#207 integration). Verified, not assumed.**

## The Phase A finding

The FNA-1 protocol in #214 proposes a parent ladder R0–R7 and gives non-neural mechanisms
first refusal against attention. Auditing current main first — before designing anything —
**most of the lower ladder is already implemented, already exact, and already instrumented.**

| rung | #214 description | status on main | implementation |
|---|---|---|---|
| **R0** | full/global exact scan | **EXISTS** | `kso/extraction.py` — `reacting_subgraph`, plus `pcst_exact_bounded` (enumerates all optima, reports ties) |
| **R1** | exact typed/indexed retrieval | **EXISTS** | `runtime/operator_index.py` posts each operator under its **rarest required input**; `kso/extraction_index.py` builds incident/outgoing posting indexes |
| **R2** | exact local graph/frontier traversal | **EXISTS** | `kso/extraction_indexed.py` — warm sparse-support reaction, avoids global liveness/pending preparation |
| **R3** | ordinary kNN / kernel retrieval | **ABSENT** | — |
| **R4** | local diffusion / associative retrieval | **EXISTS (shaped)** | `kso/navigation_sparse.py` — sparse adjacency power iteration, `O(|incidences|)`/step, with an exact rational residual bound |
| **R5** | typed multi-channel retrieval | **ABSENT** | the multi-head analogue is not built |
| **R6** | VSA/HDC approximate proposal | **ABSENT** | — |
| **R7** | neural/soft-attention reference | **ABSENT** | — |

Two things follow immediately.

**1. FNA-1 must not rebuild R0/R1/R2/R4.** Re-implementing them would manufacture a
favourable comparison against a strawman, and #214 §6 names exactly that risk ("a
hand-authored symbolic replacement can hide more prior information than a learned model").
The existing implementations are the parents, and they get first refusal *as they stand*.

**2. `operator_index.py` is already the textbook non-neural parent for attention's core
obligation.** Query-conditioned content-addressed selection, implemented as an inverted
index with a rarest-term anchor — the classic IR selectivity optimisation. Its docstring is
explicit that it is "a physical view of an immutable supplied catalogue, not another
operator authority or learned policy", and final warrant checks stay in `compose_stage`.
That is precisely the separation #214 §3 asks for: retrieval proposes, exact machinery
decides.

## The resource contract X4 requires already exists

`IndexedExtractionWork` charges 17 coordinates:

```
incident_postings_examined      distinct_edges_examined      objective_evaluations
index_probes                    outgoing_postings_examined   atom_warrant_checks
edge_warrant_checks             incidence_memberships_examined
distinct_atoms_examined         seed_entries_examined        dense_seed_entries_examined
closure_expansions              candidate_evaluations        total_objects
total_relations                 cold_incident_index_build    cold_build_work
```

Critically, `ExtractionIndex` records **`build_work` separately from query work**, and
"passing this object to a query does not charge that construction again." Index validity is
object-bound: a structurally replaced space requires fresh preparation even when IDs are
unchanged.

**So "no free preprocessing" is already enforced in code, not merely required on paper.**
This is the single biggest saving for FNA-1: the hostile test #214 asks for — *"index
construction dominates all query savings"* — is measurable today against these counters
without building any new accounting.

## What this means for the FNA-1 protocol

The genuinely unmeasured question is **not** "can a non-neural mechanism do
query-conditioned retrieval" — main already does, exactly, with revocation semantics intact
and full cost accounting. The unmeasured questions are narrower and sharper:

1. **Does the existing exact ladder discharge attention's functional obligation, or only its
   mechanical shape?** Attention aggregates *weighted* over all keys; R1/R2 select a
   candidate set and hand it to exact machinery. Where those differ in outcome is the
   residual, and it is unmeasured.
2. **R5 (multi-channel/multi-head) is absent.** #214's table asks for semantic / causal /
   temporal / failure / provenance / goal channels. Main has one relation surface.
3. **R3 and R6 are absent**, so approximate proposal has never been priced against the
   exact parents on a common information surface.
4. **`APPROXIMATE_RETRIEVAL_NOT_SAFE` is currently untestable** — nothing approximate exists
   to be unsafe.

## Hostile framing to carry into Phase C/D (X5)

- The exact parents already win on safety by construction. A study that "shows" this has
  measured nothing. The interesting result is a **capability** gap, not a safety gap.
- `pcst_greedy` already reports `approximation="GREEDY_PRIZE_DENSITY"` on every result, so
  approximation is disclosed rather than hidden. Any new approximate rung must meet that
  bar or it is not comparable.
- Main's retrieval is over an **immutable supplied catalogue**. Attention operates over
  learned content. A comparison that ignores where the catalogue came from would credit OCM
  with supplied prior information — the #214 §6 accounting risk.

## Explicit non-consequences

This map claims **no** result. It establishes what exists so FNA-1 does not re-derive it,
and it names four absences that make the ladder incomplete. No terminal is earned here, no
#165 box is affected, #71 stays `LEARNED_ROUTER_NOT_YET_AUTHORIZED`, and production `src/`
is unmodified by this branch.
