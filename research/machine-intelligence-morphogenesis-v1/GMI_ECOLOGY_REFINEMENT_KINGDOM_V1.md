# GMI ecology refinement — the `F` axis of GMI-DA7, executed against every exact-equality certificate (V1)

Status: **EXECUTED EXACT AT SCOPE.** Record `RV-377-070` (`REVIVAL_LEDGER_FAXIS.jsonl`, frozen before the run in its
own FREEZE commit). Receipt `microscopes/results/STAGE_F_AXIS_REFINEMENT_V1.json`,
`receipt_sha256 = 3cba9000c58d1e633edaa00a6f2d8bd5cff51c6636b7b68e980229b310c6ee9b` (reproduces exactly on re-execution).
Module `gmi_microscope/refine_f.py`. Issue #422. Companion: `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §10 (`GMI-DA7`),
which registers this experiment as the `F` axis and names this document.

**Terminal:**

```
F_REFINEMENT_SPLITS_10_OF_14_EQUALITY_CERTIFICATES__3_SURVIVE_THE_KNOWN_GATES
```

---

## 1. What was under test

`GMI-DA7` part 3 proves that `K(A, d, p, F)` is **monotone in the ecology family `F`**: refining `F` can only SPLIT
classes, never merge them, because `R_{E,J}` equality over a larger index set is a strictly stronger condition. The
corollary the programme owed itself is uncomfortable: an exact-equality certificate is **not** evidence that a
candidate carrier and its parent are the same machine. It is evidence that **`F` never asked them to differ**. The
registered family — 5 ecologies × 6 interventions (`gmi_microscope/ecology.py`) — was designed to test capability, not
to separate carriers.

This document is the hostile attempt to break every one of those certificates.

## 2. The certificates, recomputed from the committed receipts

The prose count of **eight** is a count of **candidates**, and it is correct. Recomputing equality cell by cell from
the committed receipts (`refine_f.enumerate_certificates`, replayed by
`test_f_axis_certificate_enumeration_replays_the_committed_receipts`) gives the finer structure the prose does not
state: **17 certificate rows across 13 receipts**, which deduplicate — N10 is certified in two receipts against two
parents, N11 in two receipts against one — to **14 distinct (candidate row, parent row) pairs over 8 candidates**.
Two candidates that reduced, DC2 and DC3, have no exact-equality certificate at all (they are dominated, not
identical), and F4 has none; that is exactly the prose's "eight of eleven".

| pair | candidate | parent | domain candidate | receipt | cells certified | instrument |
|---|---|---|---|---|---|---|
| P1 | `VSA` | `STORE_MAT` | DC1 hyperdimensional / VSA | `STAGE_DC_V24_DC1_VSA` | 7 | registered 8-bit |
| P2 | `QPROJ` | `BAYES_ORDERED` | DC7 quantum cognition | `STAGE_DC_V31_DC7_QUANTUM` | 6 | declared `wide` |
| P3 | `QPROJ` | `TABLE` | DC7 quantum cognition | `STAGE_DC_V31_DC7_QUANTUM` | 6 | declared `wide` |
| P4 | `PHASE` | `PHASE_STORE_MAT` | DC9 oscillatory / phase | `STAGE_DC_V32_DC9_PHASE` | 66 | registered 8-bit |
| P5 | `SHEAF` | `TABLE_MAT` | N3 relational-constraint / sheaf | `STAGE_DN_V26_N3_SHEAF` | 22 | registered 8-bit |
| P6 | `SHEAF` | `PROG_SEARCH` | N3 relational-constraint / sheaf | `STAGE_DN_V26_N3_SHEAF` | 22 | registered 8-bit |
| P7 | `POSET` | `PAIRTABLE` | N10 event-causal / partial order | `STAGE_DN_V27` + `STAGE_DN_V28_N10_LAW_LW` | 32 | declared `wide` |
| P8 | `POSET` | `PROG_SEARCH` | N10 event-causal / partial order | `STAGE_DN_V27` + `STAGE_DN_V28_N10_LAW_LW` | 32 | declared `wide` |
| P9 | `AUTOCAT_EAGER` | `SEARCH_DERIV` | N8 constructive / autocatalytic | `STAGE_DN_V28_N8_AUTOCATALYTIC` | 6 | registered 8-bit |
| P10 | `AUTOCAT_EAGER` | `TABLE_FULL` | N8 constructive / autocatalytic | `STAGE_DN_V28_N8_AUTOCATALYTIC` | 6 | registered 8-bit |
| P11 | `OBSTRUCT` | `DENSE_RREF` | N11 invariant / obstruction | `STAGE_DN_V29` + `STAGE_DN_V30_..._R2` | 10 | registered 8-bit |
| P12 | `SCDI` | `AUTH_INTERP` | F6 self-compiling developmental | `STAGE_E1_V36_F6_SCDI` | 16 | registered 8-bit |
| P13 | `SCDI` | `UNIVERSAL` | F6 self-compiling developmental | `STAGE_E1_V36_F6_SCDI` | 16 | registered 8-bit |
| P14 | `SCDI` | `AUTH_TABLE` | F6 self-compiling developmental | `STAGE_E1_V36_F6_SCDI` | 16 | registered 8-bit |

Two certificates in that table are at the **declared wide instrument**, because that is the instrument at which they
were taken: DC7's rows differ in every 8-bit cell (`GMI-DA5`), and N10's `POSET` equals its relational parents only
under the wide instrument, the 8-bit one gating it at chain length 12. Running them anywhere else would not be a test
of the certificate on record.

The word "certificate" here counts **configurations of the certificate table**. It is not a species count and it is
not a machine count: 14 pairs arise from 8 candidate carriers and 11 parent rows.

## 3. The refined family

Five new interventions and two new obligations, none of them in the registered `F`
(`gmi_microscope/refine_f.py`; every demand's target pair and rationale is in the module docstring):

| demand | what it asks | designed to separate |
|---|---|---|
| `OVERFLOW` | each row's state size held **fixed** at the value it was certified at while the load is raised past it — depth 1→2, `Q`→cross-pair family, boundary→interior-pinned family, late events, `L`→`L+4`, `m`→`2m`, a fifth serving regime | every eager/materialising parent from its lazy/algebraic candidate. **This is where `GMI-DA4`'s capacity gate lives.** |
| `NOISY_CUE` | `k = 1, 2, 3` bit flips in the cue | exact-key retrieval from similarity-based retrieval |
| `COMPOSITIONAL_UNSEEN` | a combination never taught but implied by the taught set, at **unbounded** capacity | model-carriers from data-carriers |
| `ABSTAIN_OBLIGATION` | the served answer becomes `(answer, abstain-flag)`; a row abstains **iff its own law cannot determine an answer** from its retained state at its certified capacity and budget; scored by `B_risk = λ·wrong_served + (λ/16)·abstentions`, `λ = 16` (gap G4, `vm.lifecycle_vector`, records RV-377-032/036/037/038) | graded-score carriers from exact-key-miss carriers |
| `REVOKE_THEN_REQUERY` | `m = 3, 4, 5`, strictly above the registered `double_revoke` (`m = 2`) | carriers whose state folded the revoked item in from carriers that hold the data |
| `INTERIOR_PIN` | pin an interior variable and requery — justified from `SHEAF`'s declared native operator RESTRICT | P5, P6 |
| `LATE_EXTEND` | append events/moves after development closes — justified from `POSET`'s EXTEND and `OBSTRUCT`'s DERIVE | P7, P8, P11 |

`ABSTAIN_GRADED` (abstain on a declared margin rule rather than on forced indeterminacy) is executed and reported but
**does not decide a verdict**, because a margin rule can deny a row a confidence measure its law actually affords and
protocol rule 19 forbids taking a separation verdict against a diminished opponent. It split no pair.

### 3a. Parent-maximality (protocol rule 19, gap DG-5), and what it cost this record

Every parent was given, before any verdict:

* **its best eviction policy** — every `OVERFLOW` demand is run under all three declared policies (`FIFO`, `LRU`,
  `LFU_TAUGHT`) and the policy **minimising disagreement with the candidate** decides. This is not decorative: under
  `LRU` the N8 table parent reproduces the candidate's answers exactly past the capacity edge, which is why P10
  survives;
* **its best cue-matching rule** — exact-key lookup plus the nearest-retained-key fallback in its own metric;
* **its best abstention rule** — the forced-only form above, at its **certified** capacity and **certified** budget.

Applying rule 19 honestly **removed three splits this record had already measured**, and each removal is recorded
because each was a defect of the instrument rather than a property of a carrier:

1. `PAIRTABLE` was first run storing only the reachable pairs, so a zero answer was indistinguishable from a missing
   key and it abstained on 170 of 240 cells. Its **declared** description (`dn_partialorder.PairTable.desc_bits`) is
   `n²` — the full matrix, zeros included — so a maximal `PAIRTABLE` materialises the zeros and a zero is a positive
   statement of concurrency. The P7 `ABSTAIN_OBLIGATION` split vanished.
2. `SEARCH_DERIV` was first run at a node budget of 64 rather than its certified `NODE_BUDGET = 400000`. The P9
   `ABSTAIN_OBLIGATION` split vanished.
3. `TABLE_MAT` was first denied re-materialisation of the enlarged pinned key space. The P5/P6 `ABSTAIN_OBLIGATION`
   splits vanished, and P6 became EQUAL under the whole refined family.

**Plain dominance is excluded for all fourteen pairs by construction**, and this is worth stating once rather than
testing fourteen times: a row that were "simply worse everywhere" could not have produced an exact-equality
certificate on the registered family in the first place. Every pair here is bit-identical on every registered cell,
so neither member dominates the other there, and no refined split can be attributed to dominance.

## 4. The executed decision, pair by pair

Registered verdict is EXACT DEVELOPMENTAL EQUALITY for all fourteen, by definition of the table in §2.

| pair | refined cells | refined verdict | demands that split | first split — `(ecology, intervention, query)` and both answers |
|---|---|---|---|---|
| P1 `VSA`/`STORE_MAT` | 252 | **SPLIT** | `OVERFLOW` (18/48) | `E_rolefill[D64_d1_k3\|depth2_past_capacity]`, `capacity=32\|evict=FIFO`, `rec0\|path23` → candidate `1`, parent `null` |
| P2 `QPROJ`/`BAYES_ORDERED` | 576 | **SPLIT** | `OVERFLOW` (86/160), `COMPOSITIONAL_UNSEEN` (86/96), `ABSTAIN_OBLIGATION` (96/128) | `E_order[n1_Q4\|cross_pair_family_past_capacity\|wide]`, `capacity=24\|evict=FIFO`, `pair(0,1)\|outcome0` → candidate `0`, parent `290` |
| P3 `QPROJ`/`TABLE` | 576 | **SPLIT** | `OVERFLOW` (86/160), `COMPOSITIONAL_UNSEEN` (86/96), `ABSTAIN_OBLIGATION` (96/128) | `E_order[n1_Q4\|cross_pair_family_past_capacity\|wide]`, `capacity=32\|evict=FIFO`, `pair(0,1)\|outcome0` → candidate `0`, parent `512` |
| P4 `PHASE`/`PHASE_STORE_MAT` | 252 | **SPLIT** | `OVERFLOW` (18/48) | `E_bindsync[D64_d1_k3_Q4_P32\|depth2_past_capacity\|fx8]`, `capacity=32\|evict=FIFO`, `rec0\|path23` → candidate `1`, parent `null` |
| P5 `SHEAF`/`TABLE_MAT` | 333 | **SPLIT** | `OVERFLOW` (72/117) | `E_glue[n6_d3_dense\|pinned_family_past_capacity]`, `capacity=9\|evict=FIFO`, `boundary(0,0)\|pin=x1=1` → candidate `[0,1,0,0,1,0]`, parent `[0,0,0,0,1,0]` |
| P6 `SHEAF`/`PROG_SEARCH` | 333 | **SURVIVES** | — | — |
| P7 `POSET`/`PAIRTABLE` | 2 558 | **SPLIT** | `OVERFLOW` (132/582) | `E_causal[w4_L4\|late_events_past_capacity\|wide]`, `capacity_candidate=64\|capacity_parent=35\|evict=FIFO`, `pair(0,16)` → candidate `null`, parent `1` |
| P8 `POSET`/`PROG_SEARCH` | 2 558 | **SPLIT** | `OVERFLOW` (102/582) | `E_causal[w4_L4\|late_events_past_capacity\|wide]`, `capacity_candidate=64\|capacity_parent=16\|evict=FIFO`, `pair(0,16)` → candidate `null`, parent `0` |
| P9 `AUTOCAT_EAGER`/`SEARCH_DERIV` | 92 | **SPLIT** | `OVERFLOW` (2/16) | `E_construct[L10\|L_past_capacity]`, `capacity=26\|evict=FIFO`, `artifact0101010111001` → candidate `0`, parent `1` |
| P10 `AUTOCAT_EAGER`/`TABLE_FULL` | 92 | **SURVIVES** | — | — |
| P11 `OBSTRUCT`/`DENSE_RREF` | 280 | **SPLIT** | `OVERFLOW` (16/32) | `E_obstruct[m10_d2_k10\|m_past_capacity]`, `capacity_bits_candidate=20\|capacity_bits_parent=80\|evict=FIFO`, `delta0` → candidate `1`, parent `0` |
| P12 `SCDI`/`AUTH_INTERP` | 936 | **SURVIVES** | — | — |
| P13 `SCDI`/`UNIVERSAL` | 936 | **SPLIT** | `OVERFLOW` (24/216), `COMPOSITIONAL_UNSEEN` (24/24), `ABSTAIN_OBLIGATION` (24/120), `REVOKE_THEN_REQUERY` (72/288) | `E_factored[G=4\|fifth_regime_past_capacity\|B0]`, `capacity=384\|evict=FIFO`, `regimeE\|x=255\|scope(0,1)` → candidate `1`, parent `null` |
| P14 `SCDI`/`AUTH_TABLE` | 936 | **SURVIVES** | — | — |

**10 of 14 split. 4 survive.** Every surviving pair is now certified over a family between 15× and 59× the size of
the registered family that certified it (P6 15.1×, P10 15.3×, P12 and P14 58.5×), which is what makes a survival a
strictly stronger reduction than the one on record rather than the same one restated.

`NOISY_CUE` split **no pair anywhere** at the instrument each certificate was taken at, at `k = 1, 2, 3`. For the two
algebraic pairs that is the sharpest result in the table: the lazy/eager identity
`Hamming(cue ⊕ role, f) = Hamming(cue, role ⊕ f)` and its phase analogue are claimed for *every* cue, and corrupted
cues do not break them.

## 5. Classifying the splits — the part that decides whether the programme learns anything

A split is evidence of domain novelty only if none of the already-proved gates explains it.

### 5a. Explained by `GMI-DA4` (capacity): ten of ten `OVERFLOW` splits

Every `OVERFLOW` split in the table is **absent at or below the parent's declared capacity edge and present past it**
(clause 7, HOLDS; the per-load counts are in the receipt's `gate_classification[*].by_load`). These are **capacity
refinements of the reduction bound, not kingdoms.** What each one adds to the record is a measured edge:

* P1/P4: the materialising parent holds `R·F = 32` bound vectors; at depth 2 the obligation needs `R²·F = 128` while
  the candidate's codebook stays at `R + F = 12`. This is `GMI-DA3` (`H*(d) ~ R^d/d`) showing up as an answer
  difference rather than as a cost ratio, and it is why criterion 3 needs a declared depth bound (gap DG-3).
* P5: the boundary-keyed table holds `d² = 9` entries; the interior-pinned family has `d²·(n−2)·d = 108` keys and the
  sheaf's local sections are unchanged.
* P7/P8: three late events cost the vector clock `w = 4` components each and the transitive-closure table `2n + 1`
  entries each.
* P9: **the split runs the other way.** Past the artifact cap the candidate's closure is the thing that overflows and
  the search parent, whose state is the seed set and the rule, is unaffected and correct. A capacity gate is not
  automatically a gate on the parent.
* P11: at `m = 24` the invariant basis needs `d·m' = 48` bits against its certified 20 and the coefficient basis
  `(m'−d)·m' = 528` against its certified 80; both truncate, and they truncate differently.
* P13-at-`OVERFLOW`: the fifth serving regime does not fit the certified serving table.

### 5b. Explained by `GMI-DA5` (precision): none — but the instrument adds splits rather than removing them

No split reverses at the other instrument (clause 9, HOLDS). The verdict for all five precision-sensitive pairs is
SPLIT at both instruments and no splitting demand disappears. What the 8-bit instrument does is **add** splits that
the wide instrument does not show: P2 additionally splits under `NOISY_CUE` at `fx8`, and P3 under `NOISY_CUE` and
`REVOKE_THEN_REQUERY`. That is `GMI-DA5` behaving exactly as proved — admissibility, and now response identity, is a
function of the instrument — and it means the `F` and `p` axes compose rather than compete.

### 5c. Explained by `GMI-DA6` (reliability): none

No refined demand takes a seed. Every ecology, perturbation, eviction order and revocation set is a declared
deterministic construction, so the declared reliability is `q = 1` by construction and no table here is a `q = 0.5`
table (clause 10, HOLDS; protocol rule 16).

### 5d. Explained by plain dominance: none, by construction

See §3a.

### 5e. **The three splits no known gate explains**

| pair | demand | cells | what differs |
|---|---|---|---|
| **P2** `QPROJ` vs `BAYES_ORDERED` | `COMPOSITIONAL_UNSEEN`, unbounded capacity, registered `Q` | 86 / 96 | the joint of question A of registered pair *i* with question B of registered pair *j*, `i ≠ j`. `QPROJ` composes it from ONE shared state and two stored projector angles at **zero extra description**. `BAYES_ORDERED` holds six parameters per registered pair and has no cross-pair conditional; its strongest available statement is the independence composition of pair *i*'s A-marginal with pair *j*'s B-marginal. First cell: `pair(0,1)|outcome0` → `0` against `290` (4096ths). |
| **P3** `QPROJ` vs `TABLE` | `COMPOSITIONAL_UNSEEN`, unbounded capacity, registered `Q` | 86 / 96 | same demand; the table holds 8`Q` registered numbers and no cross-pair entry. Its best cue-matching fallback is the same outcome index of pair *i*. First cell: `pair(0,1)|outcome0` → `0` against `512`. Materialising the cross-pair family costs the table 8`Q²` numbers against the candidate's unchanged 2`Q` angles. |
| **P13** `SCDI` vs `UNIVERSAL` | `COMPOSITIONAL_UNSEEN` (24/24), `REVOKE_THEN_REQUERY` at `m = 3, 4, 5` (72/288), `ABSTAIN_OBLIGATION` (24/120), all at unbounded capacity and the registered `G` | up to 120 | `UNIVERSAL` compiles one universal serving table and **releases the authority state**. A fifth serving regime over the same latent factors, never labelled in development, is served by `SCDI` by interpretation and cannot be served by `UNIVERSAL` at any description budget: there is nothing left to recompile from. The same mechanism splits it when development events are withdrawn and the remaining ones must be re-derived. |

### 5f. The honest reading of those three, including the part that does not favour the candidate

The `ABSTAIN_OBLIGATION` scoring (gap G4's lifecycle terms, `λ = 16`) makes the DC7 result sharper and less
flattering than "the candidate generalises":

* **P2/P3**: over the 128 scored cells the parent serves **0 wrong answers and abstains 96 times** — `B_risk = 96`.
  The candidate serves **24 wrong answers and never abstains** — `B_risk = 384`, four times the parent's. `QPROJ`'s
  cross-pair composition is its model's extrapolation, and the registered within-pair table **does not identify it**:
  the grid fit is exact within pairs (`max_err = 0`) yet a different angle pair reproducing the same within-pair table
  yields a different cross-pair joint. So the split is real and capacity-free, but it is a difference of
  **commitment**, not of correctness: one carrier commits off the registered family and is sometimes wrong, the other
  declines. Disclosed caveat: the cross-pair ground truth is generated by the declared projective model, which is the
  candidate's own model class — which is exactly why the verdict rests on the served answers DIFFERING and never on
  which row is right.
* **P13**: here the direction is unambiguous. The candidate's `B_risk` is 0 and the parent's is 24 (24 forced
  abstentions, 0 wrong). Retaining the authority state buys answers the released-authority row cannot produce at any
  budget.

### 5g. What each would need to become a kingdom claim

Criteria 3–6 of `GMI_STRUCTURAL_DOMAINS_KINGDOMS_V1.md` §14, applied to the three:

| criterion | P2/P3 (`QPROJ` vs the D3/D2 parents) | P13 (`SCDI` vs `UNIVERSAL`) |
|---|---|---|
| **3** no bounded semantics-preserving reduction over the registered family | **NOT MET, and the gap is quantified.** The reduction exists: materialising the cross-pair family costs the table 8`Q²` numbers and the ordered-Bayes row 6`Q²`, against 2`Q` angles. That is **polynomial**, so by §9 of the algebra it is one more crossover law of the L4 family, not a kingdom. Needed: a family in which the parent's materialisation is **unbounded in a declared parameter** while the candidate's is not — the depth axis of `GMI-DA3` is the template. | **NOT MET as stated, and it is the more interesting failure.** `UNIVERSAL` cannot reduce at ANY budget, because what it lacks is not capacity but **retention**. Needed: a statement of the bounded-reduction relation that prices the authority state, since `≼_B` as written in §1 bounds burden by state size and says nothing about what the compiled realisation is allowed to discard. Until that is written, P13 is a defect in the criterion, not a kingdom. |
| **4** an ecology where the frontier changes | **REGISTERED, NOT EXECUTED.** This record makes no frontier claim (§6). Needed: the cross-pair family run through the reuse-horizon grid with the `Q²` materialisation charged, extended past every crossover it reports (DG-2). | **REGISTERED, NOT EXECUTED.** Same: the fifth-regime family on the price-switch grid of RV-377-064, with `K*` recomputed. |
| **5** neutral biosphere recovery from low-level primitives | **NOT ATTEMPTED.** Needed: the B1 recovery harness recovering a projective carrier over the typed IR alphabet. | **NOT ATTEMPTED.** Needed: recovery of a machine that keeps an authority state and compiles disposable realisations from it. |
| **6** recurrence under remint and independent search encodings | **NOT ATTEMPTED.** | **NOT ATTEMPTED.** |

So: **three candidate class separations, zero kingdom claims.** None of the three clears criterion 3, and none of
criteria 4–6 has been executed for any of them.

## 6. Claim levels and the claim ceiling

| claim | level |
|---|---|
| the certificate table (17 rows / 14 pairs / 8 candidates) recomputed from the committed receipts | `PROVED_AT_SCOPE` (replayed cell by cell in `test_gmi_microscope.py`) |
| 10 of 14 certificates split under the declared refined family; 4 survive | `EXECUTED_EXACT_AT_SCOPE` |
| every `OVERFLOW` split is a `GMI-DA4` capacity refinement, absent at the capacity edge | `PROVED_AT_SCOPE` for the executed loads |
| no split is attributable to `GMI-DA5`, `GMI-DA6`, or plain dominance | `PROVED_AT_SCOPE` (dominance by construction; precision by the two-instrument column; reliability by determinism) |
| P2, P3, P13 carry a split no known gate explains | `EXECUTED_EXACT_AT_SCOPE`, claim level **`CANDIDATE_CLASS_SEPARATION`** |
| any of the three is a kingdom | **NOT CLAIMED.** criterion 3 fails for all three; criteria 4–6 unexecuted |
| the four surviving certificates are stronger reductions than the ones on record | `EXECUTED_EXACT_AT_SCOPE` over 15–59× the registered cell count |

**Claim ceiling.** This is exact response equality over **one declared refinement of `F`**, at the instrument each
certificate was taken at, against a parent given its best eviction policy, its best cue-matching rule and a
forced-only abstention rule. A SPLIT says the two rows **serve different answers** on a demand the registered family
never posed; it does not say either row is right, and §5f reports the lifecycle risk of both where they differ. A
SURVIVAL says the certificate held over a family 15–59× larger, not that the carriers are the same machine —
`GMI-DA7` part 3 guarantees only that further refinement can split **more** pairs, never fewer, so no survival here
is final. The refined demands are declared text, and a different declared abstention rule, a different eviction
policy set or a different load axis would move the table; §3a records three splits that parent-maximality removed,
which is the measure of how much the declared text matters. No frontier claim, no reuse-horizon grid and no
admissibility claim is made anywhere in this record.

## 7. Consequences for the theory

1. **`GMI-DA7` part 3 is now executed, not only proved.** Refining `F` split 10 of 14 exact-equality certificates.
   The programme's statement that eight candidates reduced "by exact developmental equality" must from here be read
   as *equal on the registered 5 × 6 family*, and the receipt says by how much that is weaker than it sounded.
2. **A new gap, `DG-6`: `≼_B` does not price retention.** P13 splits because `UNIVERSAL` released the authority
   state, and the bounded-reduction definition of `GMI_DOMAIN_ALGEBRA_EXECUTED_V1.md` §1 bounds lifecycle burden by
   state size while saying nothing about what a compiled realisation may discard. A compiler that throws the
   developmental state away satisfies the definition and then cannot answer a demand outside the family it was
   compiled for. Closure: amend the definition to quantify over a declared closure of future obligations, then
   re-adjudicate every certificate whose parent is a compiled-and-released row.
3. **Protocol rule 19 has teeth and should be executed, not asserted.** Three measured splits disappeared when the
   parent was actually given its best policy (§3a). `DG-5`'s closure procedure — an adversarial parent-construction
   step run *before* the verdict — is now demonstrated to change verdicts, not merely to be prudent.
4. **`GMI-DA3`'s depth axis and the `F` axis are the same statement seen twice.** P1 and P4 split at depth 2 for
   exactly the reason `H*(d) ~ R^d/d` is unbounded. Refining `F` with a capacity-held `OVERFLOW` demand converts a
   cost-ratio statement into an answer-difference statement, which is the stronger of the two.
5. **The `p` axis composes with the `F` axis.** At `fx8` the DC7 pairs split under two further demands (§5b). A
   refinement of `F` can expose a precision gate that neither axis alone reports.

## 8. Adjudication of the frozen prediction

`RV-377-070` froze twelve numbered clauses before the run. **Nine hold, three fail.** Nothing is deleted or softened;
the failures are in `REVIVAL_LEDGER_FAXIS.jsonl` and in the receipt's `clause_adjudication`, verbatim.

| clause | verdict | observed |
|---|---|---|
| 1 — exactly 12 split, 2 survive (P12, P14) | **FAILS** | 10 split; survivors P6, P10, P12, P14 |
| 2 — the per-pair table and first-splitting demand | **FAILS** | 11 of 14 entries correct. Wrong: P6 (predicted SPLIT at `ABSTAIN_OBLIGATION`, observed SURVIVES), P8 (predicted first at `ABSTAIN_OBLIGATION`, observed first at `OVERFLOW`), P10 (predicted SPLIT at `OVERFLOW`, observed SURVIVES) |
| 3 — `NOISY_CUE` splits neither algebraic pair | **HOLDS** | 0 of 72 differing for P1 and for P4 |
| 4 — `COMPOSITIONAL_UNSEEN` splits both DC7 pairs inside budget | **HOLDS** | 86/96 each, unbounded capacity, registered `Q` |
| 5 — `COMPOSITIONAL_UNSEEN` splits P13 inside budget | **HOLDS** | 24/24, unbounded capacity, registered `G` |
| 6 — `REVOKE_THEN_REQUERY` splits P13 and not P1, P4, P7 | **HOLDS** | P13 72; P1, P4, P7 all 0 |
| 7 — every `OVERFLOW` split is past the capacity edge and absent at it | **HOLDS** | all ten, 0 differing at every at-capacity load |
| 8 — 9 capacity-gated / 2 budget-dominance / 3 surviving | **FAILS** | 10 capacity-gated, 0 budget-dominance, 3 surviving. The surviving count and the identity of the three (P2, P3, P13) are right; the other two numbers are wrong, and the reason is the rule-19 correction of §3a, which converted the two predicted budget-dominance splits into no split at all |
| 9 — no split reverses at the other instrument | **HOLDS** | no verdict reverses, no splitting demand disappears; `fx8` adds `NOISY_CUE` for P2 and `NOISY_CUE`, `REVOKE_THEN_REQUERY` for P3 |
| 10 — no reliability gate | **HOLDS** | no refined demand takes a seed |
| 11 — survivors certified over ≥ 10× the registered cells | **HOLDS** | P6 15.14×, P10 15.33×, P12 58.5×, P14 58.5× |
| 12 — the receipt is deterministic | **HOLDS** | the whole experiment re-executed in-process and across processes to the identical `receipt_sha256` |

The three failures share one cause and it is worth naming: **the frozen predictions were made before protocol rule 19
was applied to the abstention rule.** Predicting P6 and P8 to split at `ABSTAIN_OBLIGATION` and P10 to split at
`OVERFLOW` assumed parents that were, respectively, denied their certified search budget, denied the full declared
description of their closure table, and denied their best eviction policy. Every one of those splits was measured and
then correctly withdrawn. The frozen count of 3 surviving splits — the number the experiment was actually for —
was right, and so was the identity of the three.
