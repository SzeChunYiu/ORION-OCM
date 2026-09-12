# GMI novel-domain hypotheses N3 and N10 — executed exact microscopes and reduction verdicts (V1)

Status: **EXECUTED — NO NEW DOMAIN IS CLAIMED.** Both candidates reduce to matched existing-domain parents at scope.
Issue: #422 (Track B). Branch: `claude/gmi-domain-n3-n10`.

Microscopes: `gmi_microscope/dn_sheaf.py` (N3), `gmi_microscope/dn_partialorder.py` (N10).
Receipts: `microscopes/results/STAGE_DN_V26_N3_SHEAF.json` (sha `df29242f74950cdb…`),
`STAGE_DN_V27_N10_PARTIALORDER.json` (sha `581b52489855907d…`),
`STAGE_DN_V28_N10_LAW_LW.json` (sha `eb796f010f241caf…`, the out-of-sample re-run).
Ledger: `REVIVAL_LEDGER_N3_N10.jsonl` — RV-377-050, RV-377-051, RV-377-052. `REVIVAL_LEDGER.jsonl` was not touched.
Tests: `test_gmi_microscope.py::test_dn_sheaf_receipt_cell_reproduces` and `::test_dn_partialorder_receipt_cell_reproduces`
(`python3 -m pytest test_gmi_microscope.py -q -k "sheaf or partialorder"` → 2 passed; full suite 24 passed).

## 0. A source gap that must be read before the numbers

Three documents named as required reading do not exist anywhere on the parent branch
`claude/gmi-d0-d1-research-dnbp8i`: **`GMI_NOVEL_DOMAIN_HYPOTHESES_V1.md`** (the source of the N3 and N10
specifications), **`GMI_NEW_DOMAIN_HARDENING_PROGRAMME_V1.md`** and **`GMI_DOMAIN_DERIVATION_COMPLETENESS_V1.md`**.
Verified by name search over the tree and by content search for `sheaf`, `partial-order intelligence` and
`Relational-Constraint`, which hit only `PARENT_LEDGER_V2.json` and `LITERATURE_LEDGER_V2.md`.

Both hypothesis specifications executed here are therefore **reconstructed** from the task directive's own
enumeration (carrier, native operators, natural complexity coordinate, predicted niche, capability hypothesis, weak
regime, parent attacks, domain discriminator), and tested against the admission contract that **is** present: the
domain criterion of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §2, the domain-novelty criterion §14 (criteria 1–6), and
the executable method of `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` §0 and §2. Every reconstructed element is written into
each receipt's `candidate_spec` field so the reconstruction is auditable against the hypothesis document if it
reappears. **If the reconstruction differs from the intended N3 or N10, the executed numbers stand but the verdicts
must be re-read against the real specification.**

## 1. N3 — Relational-Constraint / Sheaf Intelligence

**Carrier.** A sheaf of local sections over a declared cover: `n-1` local relations `R_i ⊆ d × d` on patches
`P_i = {x_i, x_{i+1}}` of overlap width 1, plus the restriction maps. No global object is stored.

**Law.** GLUE (compose local sections agreeing on an overlap), RESTRICT (restrict to an overlap), CHECK (does a
section extend), PROJECT (read a variable off a glued section). Complexity coordinate: the number of patches `n-1`,
against the global assignment space `d^n` the cover factorizes.

**Obligation** (the one the carrier is for). Given boundary values `x_0 = a`, `x_{n-1} = b`, decide whether a global
section exists and return the canonical (lex-least) one. Development shows only the `d` boundary pairs with `b = 0`,
so `d² − d` evaluation queries are never seen: the obligation is compositional, not memorizable.

**Parent rows** (all charged on the same ecology, same queries, answers compared bit for bit):

| row | domain | strategy |
|---|---|---|
| `SHEAF` | candidate | forward GLUE pass, backward RESTRICT pass, CHECK, PROJECT |
| `TABLE_MAT` | D2 constraint/table memory | **denied the gluing operator**, so it enumerates all `d^n` assignments at init and serves one lookup |
| `PROG_SEARCH` | D4/D5 program search + verifier | lex-first DFS over assignments with an edge verifier |
| `TABLE_SEEN` | D2 plain exemplar memory | stores dev queries, nearest-key fallback (generalization control) |
| `SHEAF_NOGLUE` | negative twin | GLUE removed: sections never composed across an overlap |

11 cells (`n ∈ {4,6,8,10}` dense, `n ∈ {4,6,8}` sparse, `n = 6 d = 4`, and a declared **late-failure** family
`n ∈ {6,8,10}` with the final patch restricted to one allowed pair), 2 columns (`B0` linear-scan store, `B0i`
indexed store). θ = 0.85. Runtime 2.4 s.

### Executed numbers (column B0)

| cell | SHEAF cap | parents cap | desc SHEAF / TABLE_MAT | compile TABLE_MAT | exec/q SHEAF / TABLE_MAT / PROG_SEARCH | H\* SHEAF→TABLE_MAT |
|---|---|---|---|---|---|---|
| n4_d3_dense | 1.0 | 1.0 / 1.0 | 39 / 81 | 252 | 140.89 / 5.0 / 7.33 | 2.16 |
| n6_d3_dense | 1.0 | 1.0 / 1.0 | 75 / 117 | 3 654 | 229.00 / 5.0 / 13.67 | 16.50 |
| n8_d3_dense | 1.0 | 1.0 / 1.0 | 105 / 153 | 45 936 | 318.33 / 5.0 / 19.00 | 146.76 |
| n10_d3_dense | 1.0 | 1.0 / 1.0 | 153 / 189 | 531 450 | 407.67 / 5.0 / 26.33 | 1 319.92 |
| n6_d3_late | 1.0 | 1.0 / 1.0 | 75 / 117 | 3 654 | 223.78 / 5.0 / 87.67 | 16.89 |
| n8_d3_late | 1.0 | 1.0 / 1.0 | 105 / 153 | 45 936 | 310.44 / 5.0 / **703.00** | 150.55 |
| n10_d3_late | 1.0 | 1.0 / 1.0 | 153 / 189 | 531 450 | 397.11 / 5.0 / **5 949.00** | 1 355.45 |

`TABLE_SEEN` peaks at 0.7778 and `SHEAF_NOGLUE` at 0.2222 — both inadmissible in all 11 cells.

### Exact developmental equality

**`SHEAF` and `TABLE_MAT` return identical answer signatures in 22 of 22 cell–column pairs, and `SHEAF` and
`PROG_SEARCH` in 22 of 22.** Every answer, including the infeasible boundaries. The candidate produces no answer that
a D2 table memory or a D4/D5 program search cannot produce.

### Crossover and the cost structure

- Description: `desc(SHEAF) = (n−1)d² + 2(n−1)⌈log₂n⌉` and `desc(TABLE_MAT) = d²(1 + n⌈log₂d⌉)` exactly; the ratio is
  2.077 / 1.560 / 1.457 / 1.235 at `d = 3, n = 4/6/8/10` and **decreases** in `n`.
- Construction: `compile_ops(TABLE_MAT) = dⁿ(n−1) + d²` exactly, `native_compile_ops = dⁿ` exactly; zero for the
  candidate and the search parent.
- Serve: the candidate's is **exactly affine** in the patch count (increment 86.6667 charged ops per two added
  variables at `d = 3`, identical in both columns); the search parent's is **geometric** in the late-failure regime
  (ratios 8.019 and 8.462) and **below** the candidate's in every dense and sparse cell.
- `H*(SHEAF → TABLE_MAT)` = 16.89 → 150.55 → 1355.45 in the late family, growing by a factor converging to `d² = 9`
  **from below** (7.63 and 7.74 at the `n4→n6` step; 8.74–9.00 at every later step).
- Frontier (DG-2 compliant — every grid is built from the analytic crossovers and its largest point exceeds every
  crossover it reports, to `H = 49 827`): `n10_d3_late` reduced price is `SHEAF` alone at `H = 1 … 1024` and
  `TABLE_MAT` alone from `H = 1357`; `n8_d3_late` native price is `SHEAF` to `H = 202`, `TABLE_MAT` from `H = 406`.

### Verdict

Criteria 1 and 2 of §14 hold by construction. **Criterion 3 FAILS at every patch count tested** — two matched
parents reproduce every answer exactly. Criterion 4 **is** satisfied in the declared late-failure regime from `n = 8`:
the candidate is the only admissible row whose description *and* serve are both linear in the patch count, the table
parent being exponential in construction and the search parent geometric in serve. The candidate is the **intermediate
compile point of D2 × D4/D5** — eager materialization, lazy search, and the polynomial compromise between them.

**Claim level: `REDUCED_TO_PARENT`** (D2 constraint/table memory and D4/D5 program search, jointly).

RV-377-050: **7 of 8 clauses hold.** Clause 6's growth-band half failed — an asymptotic ratio (`d² = 9`) was asserted
at the smallest patch count in the grid, where the description terms are still a sixth of the crossover numerator.
Opens gap **DG-3**: an asymptotic growth band may only be asserted over the coordinate range in which it was calibrated.

## 2. N10 — Event-Causal / Partial-Order Intelligence

**Carrier.** A causal poset of `n` events held as one `w`-component vector clock per event. The served state is the
happens-before order, **not** the observed sequence.

**Law.** EXTEND (append an event over its predecessors), JOIN (componentwise least upper bound of the predecessors'
clocks), COMPARE (happens-before), CONCURRENT? (incomparability). Complexity coordinate: the **width** `w`.

**Obligation.** For every ordered pair of events decide happens-before / happens-after / **concurrent**, invariantly
under the interleaving in which the events were observed. Each cell is run under **two declared linear extensions of
the same poset**, so interleaving invariance is measured, not assumed.

**Parent rows.** `PAIRTABLE` (D2 table memory: denied the join, so it materializes the full `n × n` transitive closure
by a charged Floyd–Warshall pass, then serves lookups), `SEQ_MEM` (D2 sequence/exemplar memory: the observed
interleaving as positions), `PROG_SEARCH` (D4/D5: edge list + a charged causal-path search per query), and the negative
twin `POSET_NOJOIN` (the JOIN removed, so causality never crosses a cross-chain edge).

**Two declared precision instruments** with identical charged op sequences (the `dc_energy.Arith` pattern, used here
because a causal counter is exactly what consumes arithmetic range): `fx8` (the registered 8-bit fixed point; one
causal step = `FX_ONE`, so a counter saturates past 7 steps) and `wide` (gap G5's wide-integer instrument).

8 cells (`w ∈ {1,2,4,8}`, `L ∈ {4,8,12}`, `n = 8…48`), 2 columns, 2 instruments, 2 interleavings = 320 charged runs,
13.8 s. Plus an **out-of-sample** 8-cell re-run (RV-377-052) at widths 3, 6, 12 and `L = 6`, 19.4 s.

### Executed numbers (column B0, wide instrument)

| cell | n | conc/total | POSET | PAIRTABLE | SEQ_MEM | PROG_SEARCH | twin | desc POSET/PAIRTABLE | exec/q POSET/PAIRTABLE/PROG |
|---|---|---|---|---|---|---|---|---|---|
| w1_L8 | 8 | 0/56 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 32 / 64 | 1.50 / 28.50 / 4.00 |
| w2_L4 | 8 | 22/56 | 1.0 | 1.0 | 0.6071 | 1.0 | 0.8214 | 48 / 64 | 2.80 / 23.98 / 3.14 |
| w2_L8 | 16 | 76/240 | 1.0 | 1.0 | 0.6833 | 1.0 | 0.7833 | 128 / 256 | 2.78 / 108.31 / 7.39 |
| w4_L4 | 16 | 170/240 | 1.0 | 1.0 | 0.2917 | 1.0 | 0.9083 | 192 / 256 | 4.80 / 59.94 / 3.93 |
| w4_L8 | 32 | 502/992 | 1.0 | 1.0 | 0.4940 | 1.0 | 0.7319 | 512 / 1024 | 4.81 / 369.23 / 12.56 |
| w8_L4 | 32 | 812/992 | 1.0 | 1.0 | 0.1815 | 1.0 | 0.9153 | 768 / 1024 | 8.09 / 163.76 / 5.24 |
| w2_L12 | 24 | 108/552 | 1.0 | 1.0 | 0.8043 | 1.0 | 0.6739 | 192 / 576 | 2.67 / 265.84 / 13.76 |
| w4_L12 | 48 | 896/2256 | 1.0 | 1.0 | 0.6028 | 1.0 | 0.6312 | 768 / 2304 | 4.62 / 950.37 / 22.23 |

### Exact developmental equality, and the two separations that are *not* cost

- **`POSET` == `PAIRTABLE` and `POSET` == `PROG_SEARCH` on every answer, 16 of 16 cell–column pairs under the wide
  instrument** (and 16 of 16 again in the out-of-sample re-run). The candidate produces no answer an eager closure
  table or a lazy path search cannot produce.
- **Capability ceiling against the sequence parent.** `capability(SEQ_MEM, wide) = n_ordered_pairs / n_queries`
  **exactly** in all 8 cells (and all 8 out-of-sample cells) — a total order has no incomparable pairs, so the
  sequence carrier can never answer CONCURRENT. This is a *representational*, not a cost, separation, and it makes
  `SEQ_MEM` inadmissible at every width > 1.
- **Interleaving invariance (the domain discriminator).** `POSET`, `PAIRTABLE` and `PROG_SEARCH` are invariant in
  96 of 96 combinations; `SEQ_MEM` is non-invariant in 28 of 28 width > 1 combinations, and invariant at width 1
  where the poset has exactly one linear extension.
- **Precision gate.** A counter-based row is gated exactly when the range of the counter **it actually uses** exceeds
  8 — `L` for the vector clock, `n = wL` for the sequence position. So the vector clock is **less precision-hungry
  than the sequence carrier by exactly the factor `w`**: it decomposes one global counter of range `n` into `w`
  counters of range `L`. At `L = 12` the registered 8-bit universe degrades the candidate (0.9638, 0.9641) and
  **breaks the reduction**: `POSET == PAIRTABLE` fails under `fx8` in both `L = 12` cells. Proved out of sample,
  80 of 80 checks, on a grid built to separate the two thresholds. Gap **G5 closed** for this microscope.
- **Weak regime confirmed.** At `w1_L8` the poset has exactly 1 linear extension and 0 concurrent pairs; all five rows
  are capability 1.0 and **all five answer signatures are identical** — candidate, all three parents *and* the
  negative twin are one machine. The carrier carries no information beyond the sequence carrier at width 1.

### Cost structure and what the re-freeze overturned

`desc(PAIRTABLE)/desc(POSET) = L/⌈log₂(L+1)⌉` exactly (1.333 at `L = 4`, 2.0 at `L = 8`, 3.0 at `L = 12`), independent
of width. `exec_per_query(POSET) ≤ 2w + 1` in every cell.

RV-377-051's clause 6 failed, and diagnosing it produced a law — *the candidate's serve beats the search parent's iff
`L > w`* — consistent with all 8 cells. Rather than record it post hoc, it was **frozen as RV-377-052 and tested on 8
out-of-sample cells at widths 3, 6, 12 and `L = 6`, five satisfying `L > w` and three not.** The result:

- **The serve law is FALSIFIED** (28 of 32 checks). At `w6_L6`, where `L = w` and the strict law predicts the
  candidate loses, the candidate **wins** (6.3468 vs 10.0183). Over all 16 executed cells the mechanism survives and
  the closed form does not: the candidate's serve is a function of **width alone** (at fixed `w` it varies by ≤ 6.2 %
  across every tested chain length, and `|serve − w| ≤ 1` for `w ≥ 2`), while the search parent's grows in **both**
  coordinates. The boundary is a **surface in `(w, L)`**, not an inequality. `L ≥ 6 or w ≤ 2` fits 16 of 16 (against
  15 of 16 for `L > w`) but is **registered, not claimed** — its `L` threshold is set by the grid's coarsest spacing
  and a cell at `L = 5` would refine it.
- **The precision-gate law HOLDS**, 80 of 80 out of sample.
- **The negative-twin attribution law HOLDS**, 16 of 16 out of sample: `capability(POSET_NOJOIN, wide) =
  (n_concurrent_pairs + w·L·(L−1)) / n_queries` exactly — removing the JOIN costs exactly the cross-chain ordered
  pairs. It also correctly predicts the two cells in which the **crippled twin is admissible** (`w6_L4` 0.9275,
  `w12_L4` 0.9459): at short chains and large width most pairs really are concurrent, so a row carrying none of the
  candidate's information clears θ by answering CONCURRENT. **Twin inadmissibility is therefore not a valid
  operator-attribution test on its own** — gap **DG-4**.

### Verdict

Criteria 1 and 2 hold by construction. **Criterion 3 FAILS under the wide instrument at every width** — two matched
parents reproduce every answer exactly, with overhead polynomial in the state size (`n²` description and `n³`
construction for the table parent; `n + m` serve for the search parent). Criterion 4 **is** satisfied against the
sequence/exemplar parent at every width > 1, by a hard capability ceiling and by non-invariance; it is **not**
satisfied against the table or search parents, which differ from the candidate in cost only — and against the search
parent only inside a surface in `(w, L)`.

**Claim level: `REDUCED_TO_PARENT`** (D2 transitive-closure table memory and D4/D5 causal-path search), with an
executed capability separation from the D2 sequence/exemplar parent and an executed precision gate that breaks the
reduction in the registered 8-bit universe at `L = 12`.

## 3. Summary

| | N3 sheaf | N10 partial order |
|---|---|---|
| carrier | sheaf of local sections over a cover | causal poset as vector clocks |
| law | GLUE / RESTRICT / CHECK / PROJECT | EXTEND / JOIN / COMPARE / CONCURRENT? |
| coordinate | patch count `n−1` | width `w` |
| matched parents | D2 table memory, D4/D5 program search, D2 exemplar | D2 closure table, D2 sequence memory, D4/D5 path search |
| exact developmental equality with a parent | **YES**, 22/22 with *both* | **YES**, 16/16 with *both* relational parents |
| negative twin | inadmissible in all 11 cells | differs from the candidate everywhere at width > 1; *admissible* in 2 cells |
| crossover | `H*` 16.89 → 150.55 → 1355.45, growing → `d²` per two patches | boundary is a surface in `(w, L)`; `desc` ratio `L/⌈log₂(L+1)⌉` |
| criterion 3 | **fails** | **fails** (wide); *broken by precision* at `L = 12` |
| criterion 4 | satisfied in the late-failure regime from `n = 8` | satisfied vs the sequence parent at every width > 1 |
| **claim level** | **`REDUCED_TO_PARENT`** | **`REDUCED_TO_PARENT`** |

Both candidates are compile phases of existing domains under law L4, joining DC1 (lazy) and DC3 (eager) from
RV-377-044/045: N3 is the *intermediate* compile point of D2 × D4/D5, N10 the *compressed* compile point of D2's
transitive closure. The programme-level prediction of `GMI_DOMAIN_CANDIDATES_DC1_DC9_V1.md` §4 — that no candidate
survives criterion 3 at the exact layer — **is upheld for both.**

Gaps: **G5 closed** for the N10 microscope (both instruments executed with identical charged op sequences).
**DG-2 closed** for both microscopes (frontier statements checked only on grids built from the analytic crossovers).
**DG-3 opened** (an asymptotic growth band must name its calibrated range). **DG-4 opened** (the negative-twin
protocol must be base-rate corrected: an admissible twin is not evidence against an operator's necessity, and an
inadmissible twin is not proof of it).

Untested, and therefore open: criteria 5 and 6 of §14 (neutral biosphere recovery from low-level primitives, and
recurrence under remint and independent search encodings) for both candidates; a second declared relation family /
poset seed for either microscope (the obvious G2-style replication, so any law here could still be an artefact of
LCG seeds 41 and 53); and a cell at `L = 5` to refine N10's registered serve boundary.
