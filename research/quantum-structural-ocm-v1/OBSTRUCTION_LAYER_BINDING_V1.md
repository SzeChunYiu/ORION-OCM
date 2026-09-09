# FQ-4 obstruction-witness to load-bearing-layer binding table V1

Issue SzeChunYiu/ORION-OCM#216 section 4 (FQ-4, resource-responsibility mapping).
This is the concrete `ResourceResponsibilityMap` instance: every recorded obstruction
on main that names a binding constraint, bound to the layer that controls it, with the
quote that carries the attribution. Machine-readable twin:
`OBSTRUCTION_LAYER_BINDING_V1.json` (28 witnesses, same IDs, full fields).

**This is a descriptive binding of recorded witnesses, not a validated responsibility
map. No row claims that moving its layer would have changed an outcome; only a
`reopen_falsifier` firing would license that, and none has.**

## Summary table

| ID | Layer | Conf. | Obstruction (1 line) |
|---|---|---|---|
| W01 | search | bound | Typed channels can never win reach over the unbounded exact closure (Proposition 3) |
| W02 | search | bound | Rarity-first ordering strictly worse than naive at budget 64 under a rare-channel decoy |
| W03 | verification | bound | TYPE_DECOY world did not discriminate: two banked wins rest on an untested mechanism |
| W04 | cost-charging | bound | Metapath preparation is an uncharged full edge scan, so savings are not net |
| W05 | state-maintenance | bound | Break-even ignores re-paid preparation under structural edit/revocation |
| W06 | cost-charging | bound | Cost of detecting that an edit occurred still uncharged |
| W07 | representation | bound | VSA/kNN ordering converges away from the exact one on near-twins; more capacity worsens it |
| W08 | search | bound | All 30 #203 rows UNKNOWN at REGISTERED_SOFT_WALL_BOUND during grounding |
| W09 | cost-charging | bound | 2,072 steps saved vs 14,155 lookups + checks/admission; no physical payback |
| W10 | cost-charging | bound | Prefix trie removes 130,377 steps at parity; no wall-time or lifetime gain |
| W11 | search | bound | Live learned library uses 1.6363x query slots of primitive search on the tape |
| W12 | cost-charging | bound | Rank-sum reductions are build-time counters, not serving-time speedups |
| W13 | tools-API | bound | All 76 proposal screens stop at unsupported wff syntax/type admission |
| W14 | cost-charging | bound | Grammar repair completes the family at 366 s, over 60/180 s envelopes |
| W15 | state-maintenance | inferred | Repeated parsing across screens consumed the screening budget (repaired) |
| W16 | tools-API | bound | Producer/consumer `train` field boundary failed before acquisition |
| W17 | acquisition | bound | Every candidate had one distinct support; frozen requirement is two |
| W18 | cost-charging | contested | 10x serving-cost deficit with the responsible sub-layer explicitly unattributed |
| W19 | other: custody-binding | bound | Consumer audit omitted root helper probes; lifecycle stopped pre-reconstruction |
| W20 | tools-API | bound | `match_getsteps` misses instances with argument-expanded boundary steps |
| W21 | verification | bound | Four authored cells are not a strategy-selection population |
| W22 | verification | bound | Fresh protected matched lifetimes not run; thesis CANNOT_CHECK |
| W23 | cost-charging | bound | Fixed-point iteration updates every row; an O(k) claim would hide work |
| W24 | other: attribution-discipline | bound | Obstructions in presentation coordinates are satisfiable without progress |
| W25 | verification | bound | Three controls structurally incapable of failing |
| W26 | other: custody-binding | bound | Binding computed over bytes that never entered version control |
| W27 | tools-API | inferred | Controller refused to write on a wrong open-issue assumption |
| W28 | tools-API | inferred | lean4 donor checker admission is CANNOT_CHECK |

## Aggregate

Layer histogram (28): cost-charging 8 · tools-API 5 · search 4 · verification 4 ·
state-maintenance 2 · representation 1 · acquisition 1 · other:custody-binding 2 ·
other:attribution-discipline 1 · retrieval 0 · revision 0 · **model-donor 0**.
Confidence: bound 24 · inferred 3 (W15, W27, W28) · contested 1 (W18).

Lever-layer analysis against the FNA model (FNA-1 → hostile v2 → FNA-1c → FNA-1d:
the lever applied is the lever the obstruction's own layer names):

| Lever disposition | Count | Witnesses |
|---|---:|---|
| Same-layer lever applied | 9 | W02, W03, W04, W05, W13, W15, W16, W19, W27 |
| Cross-layer lever, recorded reason | 2 | W09 (cost obstruction; acquisition lever named for payback), W17 (acquisition obstruction; representation lever, criterion fixed to isolate) |
| Mechanism succeeded, obstruction layer unmoved | 3 | W10, W11, W14 |
| No lever recorded (open) | 3 | W06, W12, W18 |
| Lever proposed/deferred | 4 | W20, W21, W22, W28 |
| Guard or rule applied, no experiment | 4 | W23, W24, W25, W26 |
| None applicable (structural/contract) | 3 | W01, W07, W08 |

**Match/mismatch result.** Of the 11 applied levers, 9 stayed in the obstruction's own
layer; the 2 cross-layer cases each carry a recorded reason (payback economics,
variable isolation). The 3 mismatches are all the same shape and are the FQ-4 warning
instantiated on main: an internal-coordinate improvement with no whole-task gain —
W10 (130,377 steps removed, wall unchanged), W11 (library live, slots 1.6363x),
W14 (0 still-UNSUPPORTED, deadlines breached). All three terminate at cost-charging.

## Findings

1. **model-donor count is zero.** No recorded obstruction on main attributes to a
   model/neural component in the loop. The nearest mechanism, FNA-2's projection,
   records "no training set, no objective, no fitted parameter, no gradient" and
   binds to representation. The layer the donor programme is named after is the one
   layer the failure record never needed.
2. **cost-charging is the modal layer (8/28)** and the terminal layer of all three
   internal-coordinate traps. The binding constraint between internal wins and
   whole-task gains is dominated by cost accounting — and only one cost-charging
   obstruction (W04) was ever closed by a lever.
3. **The FNA chain is a four-link same-layer discipline already on main**
   (W02→W03→W04→W05): each capsule's named-next-thing sat in the obstruction's own
   layer, and each lever moved the terminal. FQ-4's rule formalizes what that chain
   did informally.
4. **W18 is an unresolved FQ-4 question living inside a capsule**: the ASSAY
   explicitly refuses to pick a lever before attribution ("attribute ... before
   optimizing source validation, support lookup, state hashing or ledger
   persistence"). It is the table's only contested row.
5. **Two candidate sources do not exist.** `g1-hostile-pi-v1` and
   `l1-meaning-graph-bound-v1` were searched by basename across the whole tree at
   b801a03 and are absent; nearest existing objects are `research/g1-vessel-freeze-v1`
   (mined: W28) and `tests/m3/test_meaning_graph.py` (a test, not an obstruction
   record). The table can only be as real as the paths it cites.

## Method

Witnesses were mined by reading the result capsules on main at base b801a03
(`git diff --stat b801a03` confirms the worktree is clean against it) and extracting
every sentence that (a) names a binding constraint, bottleneck, uncharged term or
CANNOT_CHECK reason, and (b) carries attribution evidence in its own text. Each
witness was then bound to a layer by the recorded evidence alone — never by
mechanism sympathy: W10's mechanism is representation but its obstruction is
cost-charging, and the table keeps them apart.

Capsules mined: functional-neural-absorption-v1 (W01–W07),
programme-execution-20260909 (W08–W10, W27), architecture-benefit-own-state-v1 (W11),
g2-cost-parity-repair-v1 (W12), ordinary-cut-opportunity-result-v1 (W13),
ordinary-cut-syntax-revival-v1 (W14), ordinary-cut-screening-cache-result-v1 (W15),
math-language-learning-v1 (W16–W18), native-typed-lifecycle-attempt-v1 (W19, with
its revival in native-typed-consumer-revival-v1), ordinary-lemma-consumer-source-review-v1
(W20), residual-strategy-regime-v1 (W21), machine-epistemics-lifetime-v1 (W22–W23),
orion-machine/OCM_FAILURE_LEDGER.md (W24–W26), g1-vessel-freeze-v1 (W28).

Verification performed this session, mechanically: the JSON parses; witness IDs are
unique; every witness carries all nine required fields; every layer is in the
declared vocabulary; the aggregate histograms recomputed from the rows match;
each `quoted_obstruction` fragment (split on `...` joins, fragments ≥25 chars) was
matched verbatim — whitespace- and quote-normalized only — against its cited file,
decoding JSON sources to their string values; every cited line range carries at
least one distinctive token of its quote. Result: 28/28 clean.

## Boundary notes

1. Descriptive binding, not a validated responsibility map; no causal claim without
   reopen evidence. `bound` grades attribution quality of recorded evidence, not
   causal sufficiency of the layer.
2. `other-named:custody-binding` and `other-named:attribution-discipline` extend the
   issue's ten-layer vocabulary because four real obstructions (W19, W24, W25, W26)
   do not fit it; forcing them into verification or state-maintenance would have
   blurred the histogram.
3. Witnesses W24–W27 are scoped `programme-attribution`/`programme-custody`: they
   bind the programme's own record-keeping, not task cognition, and are kept
   separate by the `scope` field in the JSON.
4. The table binds single-obstruction witnesses; capsules recording multi-term cost
   chains (FNA-1c/1d) appear as multiple rows because each uncharged term was
   separately named and separately paid.
5. Line numbers cite files as they stand at b801a03; any later edit to a source
   capsule can shift them without changing the quote's verbatim status.
6. The `reopen_falsifier` fields are conditions, not results; none has fired, and
   firing one is the only licensed way to convert this table from descriptive to
   causal.
