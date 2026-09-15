# GMI Section-Q parent coverage V2

Status: **REGISTERED-SCOPE COVERAGE SATURATED — ADEQUACY REMAINS CLAIM-SPECIFIC**  
Date: 2026-09-15.  
Authority: issue #602 Section Q; base doctrine `research/parent-absorption-v1/LEDGER.json`; extension `research/parent-absorption-v1/GMI_602_PARENT_EXTENSION_V1.json`.

## 1. Why V2 exists

The original corpus audit (`STAGE_PARENT_COVERAGE_V1.json`) intentionally measured only the then-existing canonical parent ledger. It found:

```text
23 named #602-Q traditions
7  solidly covered
3  suspect: coverage rested only on a promiscuous entry
13 absent
```

That result remains an immutable historical audit. It was correct and useful: it named the gap instead of fabricating citations to make a checklist green.

V2 closes **that named coverage gap** by adding sixteen source-backed records inside the canonical `parent-absorption-v1/` authority family:

```text
13 previously absent traditions
+3 previously suspect traditions with dedicated records
=16 explicit extension records
```

The V2 audit does not infer those records by fuzzy token matching. Every extension row carries one exact `section_q_traditions` value. This avoids accidental coverage such as the token `Levin` matching the author name `Levine`.

## 2. Result

`STAGE_PARENT_COVERAGE_V2.json` now records:

```text
V1 base solid       7
V1 base suspect     3
V1 base absent     13
explicit additions 16
----------------------
registered coverage 23 / 23
uncovered            0
```

Terminal:

`PARENT_COVERAGE_SATURATED_AT_REGISTERED_602_SECTION_Q_SCOPE`

This is **coverage**, not proof that every parent comparison is adequate for every downstream claim. It does not mean `ALL_RELEVANT_PARENTS_KNOWN`; open literature can always supply a stronger or more specific comparator later.

## 3. Added first-refusal records

| #602-Q tradition | dedicated V2 parent record | anchor parents | parent-owned content / GMI residual |
|---|---|---|---|
| Universal computation / lambda / register machines | `P-GMI-UNIVERSAL-COMPUTATION` | Turing 1937, DOI `10.1112/plms/s2-42.1.230`; Minsky 1967 | computable representability/simulation; residual is resource-bounded morphology/development prediction |
| AIXI / universal intelligence | `P-GMI-AIXI-UNIVERSAL-INTELLIGENCE` | Hutter 2005, DOI `10.1007/b138233`; Legg–Hutter 2007, DOI `10.1007/s11023-007-9079-x` | ideal universal-agent objective/measure; residual is realizable resource-bounded selection under frozen normative scope |
| MAML / learned optimizers / meta-RL | `P-GMI-META-LEARNING` | Finn–Abbeel–Levine 2017 PMLR 70; RL²; Learning to reinforcement learn | faster future adaptation / learned update state; residual is full-lineage burden prediction and harmful-transfer/reset law |
| Categorical / compositional learning theory | `P-GMI-CATEGORICAL-COMPOSITIONAL` | Shiebler–Gavranovic–Wilson 2021; Gavranovic et al. ICML 2024; Coecke–Sadrzadeh–Clark 2010 | formal composition/architecture language; residual requires necessity/resource separation, not recoding |
| ACT-R / Soar / NARS / OpenCog | `P-GMI-COGNITIVE-ARCHITECTURES` | Anderson et al. ACT-R 2004; Laird Soar 2012; Wang NARS 2006; OpenCogPrime AAAI 2011 | integrated cognitive mechanisms; residual is architecture-neutral pre-outcome derivation/prediction |
| RL / HRL / model-based planning | `P-GMI-RL-HRL-PLANNING` | Puterman; Kaelbling–Littman–Cassandra; Sutton–Precup–Singh options DOI `10.1016/S0004-3702(99)00052-1` | control, belief planning, temporal abstraction; residual is full-lifecycle phase selection |
| Active inference / predictive processing | `P-GMI-ACTIVE-INFERENCE` | Friston 2010 DOI `10.1038/nrn2787`; Parr–Pezzulo–Friston 2022; Levine 2018 control-as-inference | generative inference/action and epistemic/pragmatic value; residual is priced parent-family selection |
| Memory systems / CLS / continual learning | `P-GMI-CLS-CONTINUAL` | McClelland–McNaughton–O'Reilly 1995 DOI `10.1037/0033-295X.102.3.419`; Kirkpatrick et al. 2017 DOI `10.1073/pnas.1611835114` | consolidation, stability/plasticity, replay/regularization; residual is common resource/update frontier |
| MoE / modular continual learning | `P-GMI-MOE-MODULAR` | Jacobs et al. 1991 DOI `10.1162/neco.1991.3.1.79`; Shazeer et al. 2017 | modular specialization and learned sparse routing; residual is heterogeneity-to-specialization phase under full routing cost |
| Hyperdimensional / vector-symbolic computing | `P-GMI-HDC-VSA` | Plate HRR 1995 DOI `10.1109/72.377968`; Kanerva HDC | binding/bundling/permutation/cleanup; new-domain residual only after bounded reduction/lifecycle separation |
| Neural cellular automata / morphogenetic computation | `P-GMI-NCA-MORPHOGENESIS` | Mordvintsev et al. 2020 DOI `10.23915/distill.00023`; cellular/local dynamical systems | learned local growth/regeneration and local update dynamics; residual only after local-domain reductions fail |
| Evolutionary / open-ended ALife | `P-GMI-OPEN-ENDED-ALIFE` | Taylor et al. OEE 2016 DOI `10.1162/ARTL_a_00210`; Lehman–Stanley novelty search DOI `10.1162/EVCO_a_00025` | open-ended/novelty evolutionary mechanisms and criteria; residual is predictive useful-descendant/search-burden law |
| Analog / physical / quantum computation | `P-GMI-PHYSICAL-QUANTUM` | Mead 1990 DOI `10.1109/5.58356`; reservoir computing DOI `10.1016/j.cosrev.2009.03.005`; Nielsen–Chuang; Biamonte et al. DOI `10.1038/nature23474` | substrate/reservoir/quantum computation; residual requires end-to-end prep/I-O/calibration/error-correction separation |
| Levin / OOPS / PowerPlay / Gödel machines | `P-GMI-LEVIN-OOPS-POWERPLAY` | OOPS DOI `10.1023/B:MACH.0000015880.99707.b2`; PowerPlay DOI `10.3389/fpsyg.2013.00313`; Levin search | bias-optimal/universal/incremental search and solver reuse; residual is pre-search phenotype prediction + bias/encoding robustness |
| AutoML-Zero / NAS / NEAT / evolutionary computation | `P-GMI-AUTOML-NAS-NEAT` | NEAT DOI `10.1162/106365602320169811`; AutoML-Zero PMLR 119 | architecture/algorithm discovery by search; residual is prediction before search, not rediscovery after search |
| Bayesian inference / probabilistic programming / BPL | `P-GMI-BAYES-PPL-BPL` | Church PMLR R6; Lake–Salakhutdinov–Tenenbaum DOI `10.1126/science.aab3050`; Bayesian decision theory | posterior/generative-program/program-induction mechanisms; residual is resource phase against alternative sufficient states |

The seven V1-solid traditions remain owned by the original ledger: Solomonoff/MDL, NFL/metareasoning, DreamCoder/Stitch/program synthesis, causal inference, RAG/database/indexing, neuro-symbolic/TMS/proof systems, and GNN/message-passing/constraint/factor-graph parents.

## 4. What V2 does and does not close

V2 closes the *Section-Q registration question*:

> Is there an explicit strongest-parent record for every parent tradition that #602 itself demands?

Answer: **yes, 23/23 at the registered list.**

It does not answer the stronger question:

> Is the parent comparison for every individual GMI theorem, experiment, morphology and new-domain candidate adequate at its exact scope?

That remains claim-specific. A stronger newly discovered parent can still force `PARENT_SUFFICIENT`, narrow a residual, or reopen a comparison. The parent ledger is therefore a living first-refusal mechanism, not an ontological completeness theorem.

## 5. Falsifiers / reopen conditions

Reopen registered-scope Q coverage if any of the following occurs:

- a named #602-Q tradition loses its explicit ledger entry;
- an extension record lacks a source, parent-owned statement, disposition or residual question;
- one extension record is made to cover several unrelated traditions merely through token overlap;
- a cited parent is shown not to support the mechanism attributed to it;
- #602 adds another required parent tradition without a corresponding parent-absorption record.

Do **not** reopen merely because a stronger paper is found: update the matched parent and residual instead. Coverage is allowed to improve in adequacy without pretending the literature has a final boundary.
