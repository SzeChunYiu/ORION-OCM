# CORE — `gmi-833-mtg-groupoid-hom-v1` (issue #833, programme comment 5687604615)

**Rows.** Three rows of the programme comment (indices 0, 8, 10 of `research/gmi-833-mtg-map-v1/MTG_ROWS_V1.json`):
the relabeling action on derivation records (MTG-1), the exact composition laws for error, uncertainty,
resources, intervention contracts and developmental tier (MTG-2), and isomorphic transform sets under
equivalent source/target presentations (MTG-2).

**Claim ceiling.** `GMI_833_MTG_REGISTERED_RELABELING_ACTION_ON_DERIVATION_RECORDS_AND_TYPED_HOM_COMPOSITION_AT_REGISTERED_FINITE_SCOPE`

| result | statement | numbers |
|---|---|---|
| GRP-1 | `Sym(X)×Sym(T)` acts on derivation records; the action groupoid is a groupoid | 720 compatibility, 60 inverse, 1728 associativity checks, orbit 12 |
| GRP-2 | fingerprint, recomputed observations, Pareto-minimal membership and forward-ball membership commute with the action | 60/60, 4 classes, 6/6 hostiles, null 0/200 |
| GRP-3 | the first-hit search statistic is not invariant (boundary) | `M2` → `M4` after one swap |
| HOM-1 | typed composition laws; identities, associativity; every declared field sound after composition | 96 identities, 32 triples, 576 pairs: ε-bound 576/576, tier 576/576, contract 576/576; equality fails 20 / 64 |
| HOM-2 | eleven fail-closed branches incl. `EVIDENCE_LOSS` | 11/11 applicable and detected |
| HOM-3 | conjugation is a field-preserving bijection of Hom sets | 576/576 bijections, 1728/1728 maps |

**What was corrected.** The first run used a fraction-of-cells defect and refuted its own composition laws
(subadditivity 574/576, tier minimum 566/576). Attribution: a cell fraction is not carried along a
collapsing state map. Lever: max-form defect over the label-graded metric, under which label-preserving
maps are 1-Lipschitz. Outcome: all composition laws sound, 576/576, with an analytic proof in the theorem
note. The refuted object is re-derived by the test module on every run.

**Two routes.** `groupoid_hom_v1.py` (permutation-minimum canonical form, action applied to the population,
Hom by `itertools.product`) and `independent_oracle_v1.py` (breadth-first canonical form, explicit orbit
enumeration with its own interpreter, Hom by base-3 index arithmetic; imports nothing from route A).
20 shared quantities compared.

**Reproduce (laptop or CI, never the Mac mini).**

```
python3 -I -B  research/gmi-833-mtg-groupoid-hom-v1/groupoid_hom_v1.py
python3 -I -B  research/gmi-833-mtg-groupoid-hom-v1/independent_oracle_v1.py
python3 -I -B  research/gmi-833-mtg-groupoid-hom-v1/test_groupoid_hom_v1.py
python3 -I -O -B research/gmi-833-mtg-groupoid-hom-v1/test_groupoid_hom_v1.py
```

Receipts are byte-identical between the two modes (`RESULT_V1.json` md5 `b1181c885401e0e368efc4dd160ad098`).

**Not claimed.** Universal grammar neutrality, search-prior or reachability invariance, developmental
equivalence, Hom-set isomorphism beyond registered relabelings, complete GMI.
