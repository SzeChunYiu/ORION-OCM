# Named results — gmi-833-h-real-scale-decision-trees-v1

Every result below is stated at one registered scope and at no other. No
result here is composed with any certificate of any parent package; `FGS-2`
forbids it and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_H08R` —
row `Decision trees/rule systems.`; grammar `G_DT`; ecology `F08`, the
stored-context rule table over the descriptor closure (prefixes of length ≥ 2)
of the sha256-bound source `D = /usr/share/dict/american-english` (104,334
tokens, digest `9e66281f7e51`), 776,142 descriptors, presented under the
registered Knuth permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit`
679,124, `n_held` 97,018.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

---

## `RSC-DT-1` — a family-blind recovery over the registered readout language identifies the threshold-conjunction readout at `SIGMA_H08R`

**Statement.** The family-blind recovery procedure (fewest exact decision
errors on the rank-score set, ties by charged cost then readout name; the
readout language `R` of 60 arms closed before any outcome: `C0`, `C1`,
`LEN<=6..12`, `CNT>=1..3`, `ASSOC>=1..3`, `LEN<=L&CNT>=j`, `LEN<=L&ASSOC>=j`
for L = 6..12, j = 1..3, `PREF_VOTE`, `EXT_VOTE`, `MEM_FALLBACK`) selects
**`LEN<=9&CNT>=1`** — "is the query short (length at most 9) AND present in
the stored rule table?" — whose post-hoc structural class is
`THRESHOLD_CONJUNCTION`: a decision rule that tests a conjunction of a
length threshold and a stored-context membership condition. At the rank stage
it makes **11,947 decision errors** on 203,738 rank-score queries against the
fit-majority rule's **42,936**. Fitted at full scale (store = all 679,124 fit
descriptors) and evaluated on the disjoint 97,018 held-out descriptors, it
makes **1,391 decision errors** against the fit-majority rule's **20,446** —
prototype agreement 95,627 / 97,018. The symmetric half-split regeneration
(R09, registered from the start) recovers the same class on both halves:
`LEN<=9&ASSOC>=1` at 23,239 errors (store `fit_lo`, score `fit_hi`, majority
71,453) and at 29,226 errors (store `fit_hi`, score `fit_lo`, majority
71,725); the exact conjunct the winner rule picks varies slightly between
halves (membership on the rank/held stages, association on the two halves),
and the recovered structural class `THRESHOLD_CONJUNCTION` is identical —
which is the registered R09 gate. The store-size-asymmetric complementary
split (store = `rank_score` 203,738, score = `rank_fit` 475,386) degenerates
toward the length threshold (`LEN<=9` at 51,146 errors vs majority 100,242;
the family readout `LEN<=9&CNT>=1` at 83,495) because the store covers only
63.7% of the score set's descriptors (302,857 / 475,386) — recorded as the
boundary datum that fixes the symmetric half-split as the registered R09. Both
registered nulls fire against the committed constructions: the label-shuffle
null (`random.Random(20260926)`) makes **33,079** errors, strictly more than
the majority rule's 20,446; the membership-shuffle design null
(`random.Random(20260927)`), which destroys only the membership alignment
between stored descriptors and the stored table while keeping the store size,
the length structure and the query set fixed, makes **9,358** errors, more
than three times the arm's 1,391. The membership-with-fallback arm
`MEM_FALLBACK` (admitted because its stored branch reads the STORED label of
the query, two-valued over the store) is **rejected by the winner rule** at
every stage — 34,750 rank errors, 15,759 held errors, 59,873 / 60,056 on the
two regeneration halves. The store ladder of the selected readout is monotone
non-increasing in the stored budget: `{1000: 67348, 5000: 56488, 10000:
51064, 30000: 40557, 67912: 31103, 135824: 22904, 271649: 11946, 679124:
1391}`. The scan-vs-vocabulary-index crossover is `m* = 110,799` (the
smallest `m` with `2m > V + 27`, `V = 221,569` distinct stored descriptors,
index cost 221,596). The matched **source-order presentation control fires**:
under the un-permuted contiguous presentation the family readout
`LEN<=9&CNT>=1` degrades to 75,318 held errors against the majority's 21,571
(it does not beat the majority rule at all) and the selected readout
(`LEN<=9`, 12,319 errors) fails the registered F1 margin (12,319 > 10,785 =
21,571 // 2), so the registered presentation lever is load-bearing and the
effect is not an artifact of the table readout alone. Every quantity is an
exact integer decision count, committed in `REAL_RUNS/scope_SIGMA_H08R.json`,
replayed exactly by route A and re-derived by route B
(`independent_oracle_dt_v1.py`, which imports none of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only.
Nothing is claimed about decision trees / rule systems on any other ecology,
source, presentation, or grammar; in particular no claim about nearest-
neighbour / exemplar memory (`H05`), about associative memory (`H06`), or
about a different conjunction threshold under a different presentation.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits of the
slice addenda; the readout language `R` and the constant-branch exclusion rule
of the slice addendum, which admits `MEM_FALLBACK` (its stored branch reads
the STORED label of the query, not a constant); the fit positive fraction
exceeds 1/2 (the executor asserts it before enumeration, 535,946 / 679,124 =
0.789); the winner rule of the slice addendum; the symmetric half-split R09;
the registered null constructions and seeds; the charged-cost model (`2m` vs
`V + 27`) of the slice addendum.

**Dependencies.** `grammar_dt_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 11;
`FREEZE_V1_SLICE_ADDENDUM.md`; `FREEZE_V1_SLICE_ADDENDUM_R2.md`. It depends on
no artifact of any parent package. Receipt: `REAL_RUNS/scope_SIGMA_H08R.json`,
`RESULT_V1.json` row `H08`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count
exceeds half the fit-majority rule's (F1); a label-null that fails to exceed
the fit-majority rule (F2); a design-null that fails to exceed three times the
arm (F3); a non-monotone store ladder; a crossover `m*` at which the scan arm
does not strictly exceed the index arm; a source-order control that clears F1;
any cross-scope gate composition or foreign `sigma`; disagreement between
routes A and B.

**Strongest parents.** Quinlan 1986/1993 (ID3/C4.5 threshold tests), Breiman,
Friedman, Olshen & Stone 1984 (CART binary threshold partitioning), Hunt,
Marin & Stone 1966 (CLS), Mitchell 1982 (version spaces over conjunctive
hypotheses) and Bruner, Goodnow & Austin 1956 (conjunctive concepts) for the
decision-rule / threshold-conjunction mechanism; Knuth 1997 for the
multiplicative-hash presentation lever; Salton, Wong & Yang 1975 for the
descriptor vocabulary; the in-repository parents in `PARENT_LEDGER.md` for the
ledger shape, the classifier idea, the presentation lever and the custody
chain. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about
`SIGMA_HA`, `SIGMA_H01`..`SIGMA_H06R` or any other scope; any claim that the
bare membership readout (`CNT>=1` 6,078 held errors), the bare association
readout (`ASSOC>=2` 27,900 held errors), the neighbourhood votes (`PREF_VOTE`
20,069 / `EXT_VOTE` 76,876 held errors) or the membership-with-fallback
readout (`MEM_FALLBACK` 15,759 held errors) beat the family readout under the
registered presentation — what is recovered is the threshold conjunction,
a decision rule over stored context, distinct from the siblings'
stored-exemplar membership and cue-association fan-out.

---

## `RSC-DT-2` — the registered presentation lever is load-bearing: the source-order matched control fires

**Statement.** Under the identical ecology, readout language, recovery
procedure and arithmetic slice, but with the descriptor list read in source
(alphabetical) order instead of under the registered Knuth permutation, the
held tail is dominated by long unique descriptors, the stored rule table
barely covers it, and the family readout `LEN<=9&CNT>=1` makes **75,318** held
decision errors against the majority rule's **21,571** (it is *worse* than
the majority rule). The selected readout under the source-order presentation
is `LEN<=9` (12,319 errors), which fails the registered F1 margin (12,319 >
10,785 = 21,571 // 2). The control therefore fires, demonstrating that the
family effect recovered in `RSC-DT-1` is not an artifact of the table readout
alone but requires the registered presentation — the target-independent
permutation that makes the stored rule table cover the held-out descriptors
uniformly.

**Quantifiers.** This scope only. The control is a matched negative: only the
presentation differs.

**Assumptions.** Same as `RSC-DT-1`, with the presentation key replaced by
the identity (source order).

**Dependencies.** Same as `RSC-DT-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_H08R.json` under `presentation_control` and re-derived
by route B.

**Falsifiers.** A source-order presentation under which the family readout
clears F1, or a selected source-order readout that clears F1, would falsify
the load-bearing claim.

**Strongest parents.** The parents' registered presentation lever
(`gmi-833-h-real-scale-classical-v1` `L1`); the matched-negative-control
doctrine of the Section-H requirement ledger (`R05`); the siblings' registered
matched-presentation control form.
