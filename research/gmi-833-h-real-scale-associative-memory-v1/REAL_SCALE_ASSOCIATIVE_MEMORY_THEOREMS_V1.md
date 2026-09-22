# Named results — gmi-833-h-real-scale-associative-memory-v1

Every result below is stated at one registered scope and at no other. No
result here is composed with any certificate of any parent package; `FGS-2`
forbids it and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_H06R` —
row `Associative memory.`; grammar `G_AM`; ecology `F06`, the cue-association
table over the descriptor closure (prefixes of length ≥ 2) of the sha256-bound
source `D = /usr/share/dict/american-english` (104,334 tokens, digest
`9e66281f7e51`), 776,142 descriptors, presented under the registered Knuth
permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit` 679,124, `n_held`
97,018.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

---

## `RSC-AM-1` — a family-blind recovery over the registered readout language identifies the cue-association fan-out readout at `SIGMA_H06R`

**Statement.** The family-blind recovery procedure (fewest exact decision
errors on the rank-score set, ties by charged cost then readout name; the
readout language `R = {C0, C1, LEN<=7..12, ASSOC>=1..3, PREF_VOTE, EXT_VOTE,
MEM_FALLBACK}` closed before any outcome) selects **`ASSOC>=2`** — "does the
cue retrieve a stored association with at least two distinct elements?" —
whose post-hoc structural class is `CUE_ASSOCIATION_FANOUT`. At the rank stage
it makes **8,600 decision errors** on 203,738 rank-score queries against the
fit-majority rule's **91,819**. Fitted at full scale (store = all 679,124 fit
descriptors) and evaluated on the disjoint 97,018 held-out descriptors, it
makes **1,249 decision errors** against the fit-majority rule's **43,775** —
prototype agreement 95,769 / 97,018. The symmetric half-split regeneration
(R09, registered from the start) recovers the same class on both halves:
`ASSOC>=2` at 25,907 errors (store `fit_lo`, score `fit_hi`, majority
152,818) and at 31,249 errors (store `fit_hi`, score `fit_lo`, majority
152,848); the store-size-asymmetric complementary split also recovers
`ASSOC>=2` (69,329 errors vs majority 213,847, store coverage 0.343), a
robustness datum. Both registered nulls fire against the committed
constructions: the label-shuffle null (`random.Random(20260923)`) makes
**48,065** errors, strictly more than the majority rule's 43,775; the
shuffled-association design null (`random.Random(20260924)`), which destroys
exactly the content-to-content adjacency between each cue and the letters
stored after it while keeping the store size, the cue set and the query set
fixed, makes **23,969** errors, more than three times the arm's 1,249. The
membership-with-fallback arm `MEM_FALLBACK` (the sibling's exclusion rule
admits it here because its stored branch reads the STORED association size,
which is two-valued) is **rejected by the winner rule** at every stage —
53,183 rank errors, 18,331 held errors, 109,174 / 112,930 on the two
regeneration halves. The store ladder of the selected readout is monotone
non-increasing in the stored budget: `{1000: 49200, 5000: 41310, 10000:
37421, 30000: 30716, 67912: 25239, 135824: 20226, 271649: 13755, 679124:
1249}`. The scan-vs-vocabulary-index crossover is `m* = 110,799` (the
smallest `m` with `2m > V + 27`, `V = 221,569` distinct stored descriptors,
index cost 221,596). The matched **source-order presentation control fires**:
under the un-permuted contiguous presentation the family readout `ASSOC>=2`
degrades to 51,702 held errors against the majority's 45,231 (it does not
beat the majority rule) and the selected readout (`LEN<=7`, 31,584 errors)
fails the registered F1 margin (31,584 > 22,615 = 45,231 // 2), so the
registered presentation lever is load-bearing and the effect is not an
artifact of the table readout alone. Every quantity is an exact integer
decision count, committed in `REAL_RUNS/scope_SIGMA_H06R.json`, replayed
exactly by route A and re-derived by route B (`independent_oracle_am_v1.py`,
which imports none of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only.
Nothing is claimed about associative memory on any other ecology, source,
presentation, or grammar; in particular no claim about nearest-neighbour /
exemplar memory (`H05`) or about a different association threshold under a
different presentation.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits of the
slice addenda; the readout language `R` and the constant-branch exclusion rule
of the slice addendum, which admits `MEM_FALLBACK` (its stored branch reads
the STORED association size, not a constant); the fit multi-element fraction
exceeds 1/2 (the executor asserts it before enumeration); the winner rule of
the slice addendum; the symmetric half-split R09; the registered null
constructions and seeds; the charged-cost model (`2m` vs `V + 27`) of the
slice addendum.

**Dependencies.** `grammar_am_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 11;
`FREEZE_V1_SLICE_ADDENDUM.md`; `FREEZE_V1_SLICE_ADDENDUM_R2.md`. It depends on
no artifact of any parent package. Receipt: `REAL_RUNS/scope_SIGMA_H06R.json`,
`RESULT_V1.json` row `H06`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count
exceeds half the fit-majority rule's (F1); a label-null that fails to exceed
the fit-majority rule (F2); a design-null that fails to exceed three times the
arm (F3); a non-monotone store ladder; a crossover `m*` at which the scan arm
does not strictly exceed the index arm; a source-order control that clears F1;
any cross-scope gate composition or foreign `sigma`; disagreement between
routes A and B.

**Strongest parents.** Anderson 1972, Willshaw, Buneman & Longuet-Higgins
1969, Hopfield 1982, Kohonen 1972 and Kanerva 1988 for content-addressable
association and the content-at-the-cue interface; Knuth 1997 for the
multiplicative-hash presentation lever; Salton, Wong & Yang 1975 for the
descriptor vocabulary; the in-repository parents in `PARENT_LEDGER.md` for the
ledger shape, the classifier idea, the presentation lever and the custody
chain. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about
`SIGMA_HA`, `SIGMA_H01`..`SIGMA_H05R` or any other scope; any claim that the
neighbourhood votes (`PREF_VOTE` 35,967 / `EXT_VOTE` 61,781 held errors) or
the membership-with-fallback readout (`MEM_FALLBACK` 18,331 held errors) beat
the family readout under the registered presentation — what is recovered is
the cue-association fan-out, content AT the cue, distinct from the sibling's
stored-exemplar membership.

---

## `RSC-AM-2` — the registered presentation lever is load-bearing: the source-order matched control fires

**Statement.** Under the identical ecology, readout language, recovery
procedure and arithmetic slice, but with the descriptor list read in source
(alphabetical) order instead of under the registered Knuth permutation, the
held tail is dominated by long single-element descriptors, the stored table
barely covers it, and the family readout `ASSOC>=2` makes **51,702** held
decision errors against the majority rule's **45,231** (it is *worse* than
the majority rule). The selected readout under the source-order presentation
is `LEN<=7` (31,584 errors), which fails the registered F1 margin (31,584 >
22,615 = 45,231 // 2). The control therefore fires, demonstrating that the
family effect recovered in `RSC-AM-1` is not an artifact of the table readout
alone but requires the registered presentation — the target-independent
permutation that makes the stored table cover the held-out descriptors
uniformly.

**Quantifiers.** This scope only. The control is a matched negative: only the
presentation differs.

**Assumptions.** Same as `RSC-AM-1`, with the presentation key replaced by
the identity (source order).

**Dependencies.** Same as `RSC-AM-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_H06R.json` under `presentation_control` and re-derived
by route B.

**Falsifiers.** A source-order presentation under which the family readout
clears F1, or a selected source-order readout that clears F1, would falsify
the load-bearing claim.

**Strongest parents.** The parents' registered presentation lever
(`gmi-833-h-real-scale-classical-v1` `L1`); the matched-negative-control
doctrine of the Section-H requirement ledger (`R05`); the sibling's
registered matched-presentation control form.
