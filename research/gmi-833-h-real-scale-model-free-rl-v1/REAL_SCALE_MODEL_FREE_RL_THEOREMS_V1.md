# Named results — gmi-833-h-real-scale-model-free-rl-v1

Every result below is stated at one registered scope and at no other. No result
here is composed with any certificate of any parent package; `FGS-2` forbids it
and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_HMLR` — row
`Model-free RL-like learning.`; grammar `G_ML`; ecology `F_ML`, the experience
table over the descriptor closure of the sha256-bound source
`D = /usr/share/dict/american-english` (104,334 tokens, digest
`9e66281f7e51`), `T = 671,860` experiences (context `w[:k]`, received outcome
`rho(w[k])` for `2 <= k <= len(w) - 1`), presented under the registered Knuth
permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit` 587,877, `n_held`
83,983.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

---

## `RSC-ML-1` — a family-blind recovery over the registered readout language identifies the accumulated-outcome-feedback readout at `SIGMA_HMLR`

**Statement.** The family-blind recovery procedure (fewest exact decision
errors on the rank-score stream, ties by charged cost then arm name; the
readout language `R` of 70 arms closed before any outcome: `C0`, `C1`,
`LEN<=6..12`, `CNT>=1..3`, `ASSOC>=1..3`, `LEN<=L&CNT>=K`,
`LEN<=L&ASSOC>=K` for L = 6..12, K = 1..3, `PREF_VOTE`, `EXT_VOTE`,
`MEM_FALLBACK`, `RECENCY_LAST`, `VOTE>=j/10` for j = 1..9) selects
**`VOTE>=5/10`** — "does the accumulated outcome mass at the query's state
`sigma(q) = (q[:1], q[-1:])` reach half of that state's experience count?" —
whose post-hoc structural class is `REWARD_PROPENSITY_ACCUMULATION`: a stored
value read out by accumulated experienced reward frequency. At the rank stage
it makes **1,303 decision errors** on 176,364 rank-score experiences against
the fallback rule's **56,687** (67 queries read the registered fallback). Fitted
at full scale (store = all 587,877 fit experiences) and evaluated on the
disjoint 83,983 held experiences, it makes **931 decision errors** against the
fallback rule's **27,222** — prototype agreement 83,052 / 83,983 — with 11
queries taking the fallback. The symmetric half-split regeneration (`R09`,
registered from the start, with `fit_lo` 293,938 / `fit_hi` 293,939) recovers
the same class on both halves: `VOTE>=5/10` at **5,457** errors (store
`fit_lo`, score `fit_hi`, fallback rule 94,724) and at **6,923** errors (store
`fit_hi`, score `fit_lo`, fallback rule 94,668). The store-size-asymmetric
complementary split (store = `rank_score` 176,364, score = `rank_fit` 411,513)
also recovers `VOTE>=5/10`, at 10,499 errors against that stream's fallback
rule's 132,705, with the store covering 54,014 of the score stream's 79,684
distinct contexts (0.6779) — recorded as the boundary datum that fixes the
symmetric half-split as the registered `R09`. Both registered nulls fire against
the committed constructions: the label-shuffle null (`random.Random(20260931)`)
makes **36,939** errors, strictly more than the fallback rule's 27,222; the
feedback-shuffle design null (`random.Random(20260932)`), which permutes the
received outcomes across the fit positions while leaving the store size, the
cell structure, the marginal outcome rate, the label and the query set fixed,
makes **27,222** errors — more than three times the arm's 931, and in fact
**exactly** the fallback rule's held error count, so the shuffled masses carry
no held information at all. The **matched negative control fires**: under a
per-experience Bernoulli received outcome with the registered marginal
(`random.Random(20260933 * 7919 + i)`, 322 per mille over the fit store,
realised mass 189,016 of 587,877), **no arm of `R` clears the registered
margin** (bound 13,611): the best accumulated-feedback arm reads 27,215
(`VOTE>=4/10`) against the fallback rule's 27,222, the best arm of all is
`MEM_FALLBACK` at 18,132, and every raw arm is **bit-identical** to its
registered-ecology value (`CNT>=1` 49,503, `ASSOC>=2` 39,241, `LEN<=9` 53,651,
`LEN<=9&CNT>=1` 48,217), because raw arms read stored structure and not
accumulated feedback. The degenerate boundary (`rho' = 0` everywhere) is
recorded for the record: identical raw arms, every value arm collapsing to
exactly 27,222, no arm clearing the margin, and `MEM_FALLBACK` 18,132 again.
The admitted stored-read arms are **rejected by the data** at every stage:
`MEM_FALLBACK` 38,261 rank / 18,132 held / 64,437 primary / 64,524 regen, and
`RECENCY_LAST` 42,446 rank / 21,020 held. The store ladder of the selected
readout is monotone non-increasing in the stored budget: `{1000: 19952,
5000: 10601, 10000: 8062, 30000: 6064, 67912: 4389, 135824: 2905, 271649: 1761,
587877: 931}`. The scan-vs-vocabulary-index crossover is `m* = 79,644` (the
smallest `m` with `2m > V + 27`, `V = 159,259` distinct stored contexts, index
cost 159,286). No **strictly cheaper** arm attains the winner: 61 arms are
strictly cheaper under the registered charged-cost model, the best of them
(`MEM_FALLBACK`, cost 2 per query against the winner's cell-mass cost) reads
18,132 against the winner's 931, and the best non-accumulated-feedback arm of
all reads 18,132, more than nineteen times the winner. The matched
**source-order presentation control fires**: under the un-permuted contiguous
presentation 79,244 of 83,983 held queries take the fallback (the store barely
covers the held tail) and the selected readout's **23,237** errors do **not**
clear the registered `F1` margin (23,237 > 12,276 = 24,552 // 2), so the
registered presentation lever is load-bearing. Finally, the **already-closed
sibling rows' own readouts lose on this package's held stream**: the
stored-exemplar membership readout of `SIGMA_H05R` reads 49,503, the
cue-association fan-out readout of `SIGMA_H06R` reads 39,241, the
length/stored-context conjunction of `SIGMA_H08R` reads 48,217, and all three
are beaten by the accumulated-feedback readout's 931 — the neighbouring rows
are separated by their readouts, not by relabeling. Every quantity is an exact
integer decision count, committed in `REAL_RUNS/scope_SIGMA_HMLR.json` (with
eight replay blocks, three of them scored against substituted cell masses),
replayed exactly by route A and re-derived by route B
(`independent_oracle_ml_v1.py`, which imports none of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only. Nothing
is claimed about model-free learning on any other ecology, source,
presentation, or grammar; in particular no claim about search/frontier
algorithms, planning, dynamic programming, model-based learning, Bayesian
inference, probabilistic graphical models, or any other named family of
Section H.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the reward
set `V = {a, e, i, o, u}` and the state projection `sigma(q) = (q[:1],
q[-1:])`, both registered before any count; the label
`2 * P_full(sigma(q)) >= N_full(sigma(q))` over the whole experience table,
with the registered fallback constant asserted to be `0` for every registered
stream; the registered Knuth presentation key `(i * 2654435761) mod 2**32`; the
arithmetic 7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi`
sub-splits of the slice addenda; the readout language `R` and the
constant-branch exclusion rule of the slice addendum, which eliminates nothing
and admits `MEM_FALLBACK` and `RECENCY_LAST`; the winner rule of the slice
addendum; the symmetric half-split `R09`; the registered null constructions and
seeds; the registered matched negative control construction; the charged-cost
model (`2m` vs `V + 27`, and the per-arm lookup costs of section 5).

**Dependencies.** `grammar_ml_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 11;
`FREEZE_V1_SLICE_ADDENDUM.md`; `FREEZE_V1_SLICE_ADDENDUM_R2.md`. It depends on
no artifact of any parent package. Receipt: `REAL_RUNS/scope_SIGMA_HMLR.json`,
`RESULT_V1.json` row `HMLR`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count exceeds
half the fallback rule's (`F1`); a label-null that fails to exceed the fallback
rule (`F2`); a design-null that fails to exceed three times the arm (`F3`); any
arm of `R` clearing `F1` under the matched negative control (`F4`); a
non-monotone store ladder; a crossover `m*` at which the scan arm does not
strictly exceed the index arm; a source-order control that clears `F1`; a
strictly cheaper arm attaining the winner; any cross-scope gate composition or
foreign `sigma`; disagreement between routes A and B.

**Strongest parents.** Sutton 1988 (temporal-difference value estimation) and
Sutton & Barto 2018 (tabular model-free value estimation) for the mechanism;
Watkins & Dayan 1992 (Q-learning) for model-free control by experienced
outcome; Kemeny & Snell 1960 (finite Markov chains) for the reward-frequency
average; Herrnstein 1961 (matching law) for response propensity tracking
reinforcement frequency; Knuth 1997 for the multiplicative-hash presentation
lever; Salton, Wong & Yang 1975 for the descriptor vocabulary; the
in-repository parents in `PARENT_LEDGER.md` for the ledger shape, the
classifier idea, the presentation lever and the custody chain. None of it is
claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about `SIGMA_H05R`,
`SIGMA_H06R`, `SIGMA_H08R` or any other scope; any claim that the sibling
readouts (`CNT>=1` 49,503, `ASSOC>=2` 39,241, `LEN<=9&CNT>=1` 48,217 held
errors) beat the accumulated-feedback readout under the registered
presentation — what is recovered is accumulated outcome feedback at the
query's state, a stored value updated by experienced reward frequency, and not
any single stored item and not any single dimension of the query.

---

## `RSC-ML-2` — the accumulated-feedback readout's advantage is destroyed by a matched negative control that leaves the raw arms bit-identical

**Statement.** Under the identical ecology, readout language, recovery
procedure, arithmetic slice, fallback constant, held query set and labels, but
with a received outcome that is a per-experience Bernoulli draw from the
registered seed and the registered marginal (`random.Random(20260933 * 7919 +
i)`, 322 per mille) and therefore carries **no information about the outcomes
the stored experiences' own cells received**, no arm of `R` clears the
registered margin: the best accumulated-feedback arm reads **27,215**
(`VOTE>=4/10`) against the fallback rule's 27,222 (bound 13,611), where under
the registered ecology the same family reads **931**. The best arm of all is
`MEM_FALLBACK` at 18,132, which does not clear the margin either. Meanwhile
every raw arm is **bit-identical** to its registered-ecology value:
`CNT>=1` 49,503, `ASSOC>=2` 39,241, `LEN<=9` 53,651, `LEN<=9&CNT>=1` 48,217 —
because a raw arm reads stored structure and not accumulated feedback, so
swapping the received outcomes cannot move it. The degenerate boundary
(`rho' = 0` everywhere) reproduces the raw arms bit-identically again, collapses
every value arm to exactly the fallback rule's 27,222, leaves no arm clearing
the margin, and still reads 18,132 for `MEM_FALLBACK`. The control therefore
demonstrates that the effect recovered in `RSC-ML-1` is carried by the
accumulated outcome feedback itself, not by the table readout.

**Quantifiers.** This scope only. The control is matched in the ecology, the
store, the cell structure, the readout language, the winner rule, the fallback
constant, the held query set and the labels, and in the received-outcome
marginal; only the cell alignment is destroyed.

**Assumptions.** Same as `RSC-ML-1`, with the received outcome replaced by the
registered control construction and the label held fixed at the registered
one.

**Dependencies.** Same as `RSC-ML-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_HMLR.json` under `matched_negative_control` and as the
`control_block` and `zero_block` replay blocks, and are re-derived by route B
from the committed cell masses.

**Falsifiers.** A matched negative control under which any arm of `R` clears
`F1`; a control that moves a raw arm's error count (which would mean the raw
arm was reading accumulated feedback after all); a control whose realised
received-outcome mass falls outside the registered band.

**Strongest parents.** The parents' matched-negative-control doctrine (`R05` of
the Section-H requirement ledger); the siblings' registered design-null and
matched-presentation control forms; the registered-fallback and
admission/rejection patterns of the sibling real-scale packages.
