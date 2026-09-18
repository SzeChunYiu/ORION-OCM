# PARENT_OWNERSHIP — GMI #833 Section I update-law regimes

Read this before the theorem note. Every result there is stated after
subtracting what is listed here. Assimilation-first: the parents are absorbed,
then the residual is named. Nothing below is claimed as this tranche's
contribution.

---

## 1. In-corpus parents

### #1014 — `research/gmi-833-update-law-space-v1` (direct parent)

Owns:

- **IL-1**, the admissible update-law space `A_k` over the #837 realization
  contract: laws map `(realization, registered history, budget)` to
  `(distribution over successor realizations, charge)`; admissibility `A1`-`A4`
  is decidable at finite scope in at most
  `|R| |HIST| |Bgrid| (|R| + 2|coords| + 1)` exact rational operations per law
  per grade; `A_star` is closed under rational convex mixture (IL-1.2) and under
  composition (IL-1.3); `A_1` is NOT composition-closed
  (EARNED-BY-COUNTEREXAMPLE); `(A_star, o)` is a two-sided monoid on kernels
  with only subassociative worst-case charging (IL-1.4); the name-freedom
  certificate (IL-1.5).
- **IL-2 / IL-2a / IL-3 / IL-3b / IL-23**, the acquisition-cost crossover:
  every verified-selection evaluative-only law costs exactly `(d+1)/(m+1)`
  probes under the successor-relabeling orbit, so the evaluative and directional
  regimes partition the registered price/ecology space at
  `rho* = mean_i (d_i+1)/(m_i+1)`.
- **IL-4**, credit assignment recovered from graph and resource structure.

This tranche **defines no new space**. Every signature below is a subset of
`A_k`, every regime is a region of the same registered price space, and the
mixture-hull argument used for selector soundness is IL-1.2's, cited as such.
The one place this tranche strengthens a parent result is stated as a
strengthening, not as an independent discovery: `UL-1` observes that `A1`-`A4`
is a **pointwise** conjunction, so `A_k` is closed under arbitrary pointwise
selection — of which IL-1.2's rational mixture is the distributional special
case. The proof is one line over the parent's own definition.

### #870 — `research/gmi-833-update-law-nfl-v1`

Owns the no-free-lunch boundary: under uniform completion every update law
scores identically, and for any two predictively distinct laws there exist
ecologies preferring each; therefore a useful preference between update laws
**requires stated ecological, informational and resource assumptions**. This is
why every row here is of the form *which stated assumption class favours which
external signature*, and why no unconditional preference is asserted anywhere.

### #897 — `research/gmi-833-g0-grammar-growth-v1`

Owns grammar growth `G_t -> G_(t+1)` (GRW-1), recursive library formation and
primitive invention (INV-1/REC-1), the lifecycle threshold `H_eff * Delta > K`
(THR-1), the held-out reuse benefit (HLD-1) and its null (NULL-1). The
`program/library learning` row is closed here **by reconciliation to #897**, as
the freeze pre-committed. The residual claimed here is only the *placement*: the
same inequality restated in this tranche's price coordinates as the condition
under which the re-invocation refinement of a description-emitting law is
favoured inside `A_k`. **No novelty is claimed for the invention result, the
grammar growth, or the held-out reuse benefit**, and this tranche does not
re-run them.

### #848 / #874 and the governed-self-change package

Own governed self-change and its authority contract. The `self-modification`
row here is a **cost and reachability** statement inside `A_k` and carries no
governance content: nothing here licenses a law that promotes or signs off on
itself, and `SELF_MODIFICATION_GOVERNANCE_SETTLED` is a forbidden promotion.

### #903 — `research/gmi-833-real-transition-receipts-v1`

Owns the real-system protocol this tranche would have had to follow to close
`Test on realistic learning systems`. That row is **left open**; see `CORE.md`.

### `research/gmi-833-capability-interaction-partition-v1` (#1011)

Owns the correction of `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1`, whose
DEF-2 was a taxonomy asserted as a partition when one class was a strict
sub-case of another. That correction is the reason the compatibility matrix
here is reported **as a matrix** and the word partition is applied only to the
argmin-cell decomposition, which is a partition by construction.

### `research/gmi-833-theory-baseline-v1/BASELINE_V1.md`

Owns assertions A1-A14, the claim ceiling discipline and the forbidden-promotion
vocabulary. Adopted unchanged.

---

## 2. Literature parents

Each result below is a parent of one of the seven signatures. None of them is
restated as a finding here; what is claimed is the exact finite crossover inside
a registered architecture-neutral law space, which none of them states.

| signature | strongest parents |
|---|---|
| exact conditional weighting (`SIG-W`) | Bayes (1763); de Finetti, *La prévision*, Ann. Inst. Henri Poincaré 7:1-68 (1937); Savage, *The Foundations of Statistics* (1954); Robbins, *An empirical Bayes approach to statistics* (1956) |
| stored-instance retrieval (`SIG-X`) | Cover & Hart, *Nearest neighbor pattern classification*, IEEE Trans. Inform. Theory 13(1):21-27 (1967), doi:10.1109/TIT.1967.1053964; Aha, Kibler & Albert, *Instance-based learning algorithms*, Machine Learning 6:37-66 (1991), doi:10.1007/BF00153759; Stanfill & Waltz, CACM 29(12):1213-1228 (1986), doi:10.1145/7902.7906 |
| production compression (`SIG-R`) | Rissanen, *Modeling by shortest data description*, Automatica 14(5):465-471 (1978), doi:10.1016/0005-1098(78)90005-5; Michalski (1983); Quinlan, *Induction of decision trees*, Machine Learning 1:81-106 (1986), doi:10.1007/BF00116251; Blumer, Ehrenfeucht, Haussler & Warmuth, *Occam's razor*, Inform. Process. Lett. 24(6):377-380 (1987), doi:10.1016/0020-0190(87)90114-1 |
| reuse-indexed construction (`SIG-L`) | Solomonoff (1964); Wolfe & Goodman (2014); Dechter, Malmaud, Adams & Tenenbaum, *Bootstrap learning via modular concept discovery*, IJCAI (2013); Ellis et al., *DreamCoder*, PLDI (2021), doi:10.1145/3453483.3454080 — **and #897, which owns the in-corpus result** |
| breadth selection (`SIG-P`) | Holland, *Adaptation in Natural and Artificial Systems* (1975); Rechenberg (1973); Schwefel (1977); Droste, Jansen & Wegener, *On the analysis of the (1+1) evolutionary algorithm*, Theoret. Comput. Sci. 276(1-2):51-81 (2002), doi:10.1016/S0304-3975(01)00182-7; Jansen, De Jong & Wegener, *On the choice of the offspring population size*, Evol. Comput. 13(4):413-440 (2005), doi:10.1162/106365605774666921 |
| cross-episode indexing (`SIG-T`) | Schmidhuber (1987); Thrun & Pratt, *Learning to Learn* (1998), doi:10.1007/978-1-4615-5529-2; Baxter, *A model of inductive bias learning*, JAIR 12:149-198 (2000), doi:10.1613/jair.731; Maurer, Pontil & Romera-Paredes, JMLR 17(81):1-32 (2016) |
| successor-set change (`SIG-S`) | Schmidhuber, *Evolutionary principles in self-referential learning* (1987); Schmidhuber, *Gödel machines* (2003), arXiv:cs/0309048; Lenat, *EURISKO*, Artificial Intelligence 21(1-2):61-98 (1983), doi:10.1016/S0004-3702(83)80005-8 |
| why any selection needs assumptions | Wolpert & Macready, *No free lunch theorems for optimization*, IEEE Trans. Evol. Comput. 1(1):67-82 (1997), doi:10.1109/4235.585893; Mitchell, *The need for biases in learning generalizations* (1980); Schaffer, ICML (1994) |

**What is explicitly NOT claimed novel here:** that exact conditioning is
optimal under a correct prior; that stored instances generalize; that shorter
descriptions generalize; that reusable sub-programs amortize; that populations
escape local optima; that related tasks transfer; that self-reference is
expressible; or any statement about which of these is best in general. All of
these are parent results, several of them decades old, and the parents own them.

---

## 3. The named residual of this tranche

1. **Seven external structural signatures** on laws in `A_k`, each a predicate
   on the law's charged trace and emitted predictor, none of which names a
   mechanism. The definitions are in the theorem note; the lexical and
   structural screens that check the non-naming are in the receipt.
2. **Seven exact rational dominance thresholds** in registered ecology
   invariants, each with its matched converse, of which five are UNCONDITIONAL:
   `alpha_gain <= 0` kills `SIG-W` at every positive price; never-retrieved
   instances are strictly wasteful; a unimodal score landscape makes every extra
   carried member strictly wasteful; `r = 0` makes the cross-episode rule
   behaviourally identical to the base rule and strictly dearer; and — the
   sharpest — pointwise-selection closure makes the conditions favouring
   successor-set change **EMPTY** inside any closed comparison class.
3. **The honest joint structure**: an exact 21-pair compatibility matrix showing
   the seven predicates do NOT separate law space, reported as a matrix; and,
   separately, the argmin-cell partition of the positive price cone, which is a
   partition by construction and is proved unconditionally.
4. **A prospective selector** whose decision table is in the freeze commit and
   whose census is in a later commit, with soundness scoped to the registered
   representatives and their rational mixture hull (the hull extension is
   IL-1.2's, cited).
5. **A blind structural enumeration** whose objective is only the charge, whose
   grammar carries no family token, and whose argmin's signature is computed
   after the fact.

Everything else in this package is machinery, screens, or parent mathematics
re-derived only to check that the declared cost model does not contradict a
parent bound.
