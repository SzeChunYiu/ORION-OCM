# G2.4 ordinary-cut lemma reuse — parent saturation

Research planning only. No manuscript, novelty clearance, or new experimental
result. Does not CHECK G2.4.

This capsule saturates CS / ATP / Metamath **journals and proceedings** that
own ordinary-cut lemma *reuse*, as distinct from library induction already
assimilated in [PARENTS.md](../programme/PARENTS.md) and
[parent-absorption-v1](../parent-absorption-v1/CORE.md).

Machine-readable rows: [LEDGER.json](LEDGER.json).
Fetch/read custody: [SOURCE-READS.json](SOURCE-READS.json).
Gap vs Paper B falsifying panel: [GAP.md](GAP.md).

## Decision

Do not treat the 1-step alias screen as the consumer of the 22
`SCREENED_NEGATIVE_IN_DOMAIN` ordinary `$p` lemmas
([g2-causal-lemma-reuse-v1](../g2-causal-lemma-reuse-v1/CORE.md)).
That screen is Mooney's *limited-use extreme* applied as an eligibility test.
A 1-step-screen negative is not an empty-opportunity finding and is not a
utility measurement.

The next registered experiment **must** be a later-proof *refactoring* consumer
(subtree match+replace) **and** a bounded *2-decision* search with vs without
the extra lemmas. A 1-step conclusion-alias hunt would only rediscover what
the screen already refused.

`PARENT_SUFFICIENT` is the expected first terminal if those two consumers,
charged under Minton's utility formula and equipped with ordinary substitution
plus SInE-class premise selection, reproduce any later benefit. That is not
programme failure. Paper B's residual (revision-aware retention that prices
future verification) is not testable until this consumer exists.

No novelty is claimed. The parents below already own lemma mining, macro use,
utility accounting, ATP-with-vs-without extra lemmas, proof-tree refactoring,
save-value synthesis, cut-introduction, and large-theory premise selection.

## Already assimilated (do not re-open)

| Parent | Where recorded | Role already charged |
|---|---|---|
| DreamCoder, Ellis et al., PLDI 2021 | PARENTS.md #1; P-PROGRAM-LIBRARY | Wake-sleep library + later solving from abstractions |
| Stitch, Bowers et al., POPL 2023 | PARENTS.md #2 | Corpus compression / refactoring donor |
| LILO, Grand et al., ICLR 2024 | PARENTS.md #3 | Neural synthesis + Stitch; external-only |
| Minton, AAAI 1988 EBL / PRODIGY | typed-next-parent; P-MINTON-EBL | Proof compilation into an ordinary theorem |
| Metamath book §§4.1.3–4.1.4 | P-METAMATH-SUBSTITUTION | Ordinary `$p` substitution is the conventional consumer |
| CD Tools pin `42ae1d5` source review | P-CDTOOLS | DAG/save-value + TreeRePair; adapter pending |
| SEPIA 2015 | typed-next-parent option C | Trace-model inference; later than option A |

The 22 lemmas are already natively verified ordinary `$p`
(`NATIVE_ORDINARY_LEMMAS_ADMITTED_NO_HELD_OUT_INVOCATION`). G2.4 remains
`NOT_YET` because no later causal invocation was measured.

## What the 1-step-screen negative is

The syntax-revival negatives are *not aliases of existing conclusions under
one-step matching*. Seven of 22 have zero hypotheses. Held-out scan: 0
alpha-renames of those seven in the first 5,000 post-`pssdif` statements;
`inssdif0` is prefix-closed; a 4-decision 9-wff bank did not invoke any cut.

That is exactly the evaluation that Kaliszyk & Urban, REFACTOR, and Mooney
warn against treating as the usefulness test:

- 1-step alias of a later conclusion = “the learned fact *is* the later theorem.”
- Ordinary reuse = later ATP / search / refactoring *uses* the extra lemma as
  an intermediate, with or without chaining limits.

## Next experiment MUST vs PARENT_SUFFICIENT

### MUST (closes the G2.4 consumer gap; still not Paper B)

1. **Refactoring consumer (ADOPT from REFACTOR, non-neural).** On held-out
   published proofs after `pssdif`, run subtree match+replace: if a connected
   proof subtree is an instance of one of the 22 ordinary `$p`, replace it by
   a single invocation. Count nodes saved, proofs touched, and whether any
   replacement occurs. This is REFACTOR §4.3 / Table 5's *consumer*, not its
   neural extractor.
2. **2-decision search (ADAPT from Mooney limited-use + ordinary parent).**
   Enlarge the finite bank to the official intermediates of a P1-closed
   held-out target (the 9-wff bank was incomplete, not a residual). Compare
   native search *with* vs *without* the 22 lemmas at `max_decisions ≥ 2`.
   Charge compilation, matching, and failed attempts. One-step conclusion
   matching is a control, not the scored consumer.
3. **Utility ledger (ADOPT Minton 1990 formula).** For each of the 22:
   `Utility = (AvrSavings × ApplicFreq) − AvrMatchCost`.
   Drop or down-weight lemmas with negative estimated utility. Do not retain
   on native-verification alone.

### Would be PARENT_SUFFICIENT (stop; do not invent an OCM residual)

If, after those two consumers and the utility charge, any later benefit is
reproduced by:

- ordinary demonstrated-theorem accumulation (Metamath `$p` parent), and/or
- SInE-class symbolic premise selection over the enlarged library, and/or
- Kaliszyk/Urban with-vs-without extra lemmas on later ATP/search, and/or
- REFACTOR-style mechanical refactoring without a new extractor,

then record `PARENT_SUFFICIENT` and move the question upward (Paper B:
revision-aware *retention* under evidence change, not “can extra lemmas be
used”). Aliases-only, no later invocation, or a parent reproducing the
frontier remains the Paper B refutation.

## Gap parents (this saturation)

### 1. Mooney, IJCAI 1989 — rule *use*, not rule *form*

**Source.** Raymond J. Mooney, “The Effect of Rule Use on the Utility of
Explanation-Based Learning,” IJCAI-89, pp. 725–730.
Full text: `https://ijcai.org/Proceedings/89-1/Papers/116.pdf`
(sha256 `20f36d5d492c…`, 136,962 bytes). Proceedings landing also fetched.

**What it owns.** EGGS is a depth-bounded Horn-clause prover that compiles
proofs into macro-rules. §4 contrasts *full-use* (learned rules chain with
domain rules and each other) against *limited-use* (a learned rule may fire
only if it completely solves the current goal; no backchaining on its
antecedents). Unrestricted chaining degrades performance (depth-4 full-use
2.4× slower than no-learn on controlled Principia problems). Limited-use is
1.4× / 2.0× faster at depth 3 / 4. Search strategy (depth-first vs
breadth-first) changes the sign of learning. Matching antecedents is
NP-complete (citing Minton); proving them is worse.

**Disposition.** **ADAPT** the use-restriction. **REJECT** reading our
1-step-screen negative as “no useful cut.” That screen *is* Mooney's
limited-use extreme used as an *alias filter*. It correctly refuses aliases;
it does not measure later utility under 2-decision or refactoring use.

**Prior information added.** Horn-macro use policy; Principia / blocks-world
full-vs-limited tables; the explicit warning not to generalize utility across
performance elements.

**Remaining question.** Does *limited* 2-step use of the 22 lemmas pay, or
does even that remain negative once match cost is charged?

### 2. Minton, AIJ 1990 — quantitative utility

**Source.** Steven Minton, “Quantitative results concerning the utility of
explanation-based learning,” *Artificial Intelligence* 42(2–3):363–391, 1990.
DOI `10.1016/0004-3702(90)90059-9`. Revised AAAI-88 Best Paper.

**Read status.** DOI landing + OpenAlex + Unpaywall + Semantic Scholar:
**closed**, no OA PDF (`oa_status=closed`, `best_oa_location=null`).
ScienceDirect HTML 403. AAAI-88 CDN URLs served *bundled proceedings*
starting at other papers (Ginsberg; Gelfond/Lifschitz), not an isolated
Minton extract. Formula recovered from primary-quoting secondaries that
cite the 1990 paper by name:

- Langley, *The Computational Gauntlet of Human-Like Learning* (2023 slides),
  section “Quantitative Results on Utility of EBL,” quoting Minton 1990:
  **`Utility = (AvrSavings × ApplicFreq) − AvrMatchCost`**
  where `AvrSavings` is average time saved when the rule applies (search
  eliminated), `ApplicFreq` is the probability the rule applies when tested,
  `AvrMatchCost` is average match cost. Initial estimate from the training
  example; empirical validation; discard remaining negative-utility rules.
- Marks, *Machine Learning* 1991 / “Information filtering,” quoting Minton
  1988a/b: operational `Utility = avg-time-without − avg-time-with`, and
  retention filter `(Mean Time Saving × Probability of Application) − Mean
  Match Costs`.

Architecture-net-benefit-v1 had only the publisher/AAAI *abstract*. The
**exact formula** is now charged.

**Disposition.** **ADOPT** the formula as the retention test for the 22
lemmas. **ADAPT** units to native decision-count / action-attempts / compile
cost (do not add bytes to seconds). **REJECT** retaining on verification
alone.

**Applied to the 22.** Under the 1-step conclusion consumer, measured
`ApplicFreq ≈ 0` (0/5000 alpha, 0 invocations on `inssdif0`). Then
`Utility ≈ −AvrMatchCost < 0` unless a different consumer raises frequency.
That is the quantitative reading of the 1-step-screen negative.

**Prior information added.** Closed-access status of AIJ 1990; formula
quotation trail; implication that match cost of 22 extra `$p` must be
charged on every later search layer.

**Remaining question.** After refactoring + 2-decision, is any lemma's
utility positive on held-out families, estimated from *training-only*
information?

### 3. Kaliszyk & Urban — lemma mining; ATP with vs without

**Sources (journal and proceedings).**

- CICM 2013 / LNAI 7961: “Lemma Mining over HOL Light,” arXiv 1310.2797.
  Full PDF+HTML read (214,241 / 167,056 bytes).
- JSC 69:109–128, 2015 (online 2014): “Learning-assisted theorem proving
  with millions of lemmas,” DOI `10.1016/j.jsc.2014.09.032`, CC-BY.
  PMC HTML full text read (`PMC4599631`, 263,070 bytes). Elsevier PDF 403;
  PMC PDF object 404. OpenAlex `is_oa=true`.

**What it owns.** Mine unnamed HOL Light / Flyspeck inference-graph lemmas;
rank by `D` (dependency mass), `U` (downstream use), size, PageRank,
epcllemma. **Evaluation is ATP success on later / original theorems with vs
without the extra lemmas**, under cheating / almost-honest / fully-honest
proof-graph restrictions — *not* 1-step alias of conclusions. CICM: +~5%
absolute on core HOL Light in non-cheating settings; `Q2` 46.2% at 512
premises in fully-honest. JSC Flyspeck almost-honest: 14-best lemma methods
37.6%, combined with older HOL(y)Hammer methods 44.2% (21.4% relative
improvement over the older 14). Adding *all* lemmas eventually weakens
performance (Table 11) — a utility/swamping result.

**Disposition.** **ADOPT** the with-vs-without later-proving consumer and the
honest/cheating distinction (do not score a lemma using theorems proved
after it). **ADAPT** to native search / mmverify, not HOL(y)Hammer.
**REJECT** k-NN / learning-based relevance filtering in the OCM arm
([NO_NEURAL_CONTRACT](../programme/NO_NEURAL_CONTRACT.md)). **REJECT**
calling 1-step alias “lemma mining evaluation.”

**Prior information added.** Exact evaluation protocol; HOL Light / Flyspeck
counts; the warning that too many extra lemmas hurt.

**Remaining question.** With-vs-without the 22 on a held-out native family,
after SInE-class selection — does anything remain once the ordinary `$p`
parent is equally equipped?

### 4. REFACTOR, ICLR 2024 / arXiv 2402.17032

**Source.** Jin et al., “REFACTOR: Learning to Extract Theorems from Proofs.”
arXiv HTML+PDF and ICLR proceedings PDF all fetched and read
(arXiv PDF sha256 `a423fcbf2436…`).

**What it owns.** Metamath proof trees. Extraction = node-level classification
of a *connected subtree* that is a valid theorem. **Consumer:** expand human
proofs by inlining, then *refactor* later proofs by subtree match+replace;
16 new theorems from set.mm, 14,092 / 27,220 theorems refactored, ~400k
nodes saved, mean use 733.5 after refactoring. A prover trained on the
refactored library proves 75 more test theorems (neural; external-only).

**Disposition.** **REJECT** the neural extractor under NO_NEURAL_CONTRACT
(same class as the 2023 lemma-repo `model.py` already rejected in
P-CDTOOLS). **ADOPT** the refactoring consumer as the missing G2.4
*usefulness* test for already-admitted ordinary `$p`. A symbolic compressor
(Stitch / CD Tools / Vyskočil) may propose cuts; REFACTOR's match+replace
says whether later human proofs actually contain them.

**Prior information added.** Exact Metamath consumer; set.mm refactor
counts; extraction ≠ 1-step conclusion identity.

**Remaining question.** Do any of the 22 appear as replaceable subtrees in
held-out set.mm proofs after `pssdif`?

### 5. Wernhard — proof structures and save-value synthesis

**Sources.**

- Wernhard & Bibel, “Investigations into Proof Structures,” *JAR* 68(24),
  2024. DOI `10.1007/s10817-024-09711-8`. arXiv 2304.12827 PDF full text
  (1,523,935 bytes). HTML 404 (no ar5iv build). Springer landing fetched.
- Wernhard & Zombori, “Exploring Metamath Proof Structures,” arXiv
  2505.12305. HTML+PDF full text. Knowledge base = grammar compressing
  proof terms; TreeRePair; human+machine lemmas for large subsets of
  set.mm.
- Wernhard, “Generating theorems by proof structures,” arXiv 2602.15511.
  HTML+PDF full text. Save-value / combinator lemmas on a 1,374-theorem
  POI fragment; **lemmas improve prover solution rates**.

**Disposition.** **ADAPT** — already P-CDTOOLS. Do not build another miner.
**ADOPT** save-value as a *proposal* ranking, not a warrant. The 2026 paper's
consumer is again later proving with vs without generated lemmas.

**Prior information added.** JAR 2024 structure-as-term account; 2026
explicit “lemmas significantly improve solution rates” (later-ATP, not
1-step).

**Remaining question.** After exact re-expansion and native admission, does
save-value pick cuts that beat the 22 already-admitted training cuts on the
refactoring / 2-decision consumers?

### 6. Adjacent invention / sharing parents

| Parent | Read | Disposition |
|---|---|---|
| Vyskočil, Stanovský, Urban, LPAR-16 2010, LNCS 6355. Author PDF `komprese.pdf` (305,623 bytes). Substitution-tree definition invention; ~8,000 TPTP proofs; compression of *terms*, not later solving. | full-text | **ADAPT** as a proposal heuristic. **REJECT** as a G2.4 consumer. Compression ≠ causal later use. |
| Gauthier & Kaliszyk, LPAR-20 2015 / arXiv 1509.03527. HOL4↔HOL Light knowledge sharing; HOL(y)Hammer 30%→40% on HOL Light with HOL4 advice. | full-text | **REJECT** neural/statistical advice for OCM. **ADAPT** “extra foreign lemmas help later ATP” as a consumer *shape*. |
| Gauthier & Kaliszyk, CPP 2015 / arXiv 1509.03534. HOL4 premise selection + Metis reconstruction. | full-text | **REJECT** learned selector. Ordinary SInE is the symbolic parent. |
| Gauthier, Kaliszyk, Urban, CICM WiP 2016, CEUR 1785/W23. Statistical conjecturing. | full-text | **REJECT** under NO_NEURAL_CONTRACT. |
| Hetzl, Leitsch, Weller, LPAR-18 2012, LNCS 7180. Author PDF. Cut-introduction from Herbrand-sequent compressions; inverse cut-elimination; ATP-output lemmas. | full-text | **ADAPT** as FO lemma-invention parent. **LEAVE OPEN** on Metamath traces (no Herbrand sequent). Evaluation is proof length, not later search. |
| Hetzl et al., “Algorithmic Introduction of Quantified Cuts,” arXiv 1401.4330. Journal-length inversion of Gentzen; exponential compression. | full-text | Same as 2012; **ADAPT** theory, not native mechanism. |
| Fikes, Hart, Nilsson, “Learning and Executing Generalized Robot Plans,” *AIJ* 3:251–288, 1972. DOI landing closed; Nilsson-hosted PDF full text (`learningexecuting.pdf`, 2,410,065 bytes). MACROPS from triangle tables; later STRIPS planning uses them as operators (whole or subsequence); Problem 5 unsolvable without MACROPS. | full-text (author copy) | **ADOPT** as the historical macro-operator parent. Multi-step later planning, not 1-step alias. Utility not yet quantitative (Minton). |

### 7. SInE / premise selection — ordinary consumer of extra lemmas

**Source.** Hoder & Voronkov, “Sine Qua Non for Large Theory Reasoning,”
CADE-23, LNCS 6803:299–314, 2011. DOI
`10.1007/978-3-642-22438-6_23`. Author-copy PDF served from
`tqft.net` (fetched as 344,208-byte PDF). Trigger relation: rare symbols
trigger axioms; iterate from the goal; tolerance / depth parameters.
CASC-LTB winner family.

**Disposition.** **ADOPT** as the ordinary *selection* parent once the
library grows by 22 (or thousands of) extra `$p`. Dumping every extra
lemma into every later search is the swamping Minton/JSC already measured.
**REJECT** MaLARea / k-NN / HOL(y)Hammer predictors in the OCM arm.
**ADAPT** symbol-trigger SInE (or exact premise/conclusion indexes already
in P-INDEXING) as the equally equipped parent.

**Prior information added.** Trigger definition; large-theory fact that
most axioms are irrelevant to a given goal.

**Remaining question.** After SInE (or exact indexes) select among
prefix+22, does 2-decision search still differ from prefix-only?

## Disposition summary

| ID | Parent | Disposition | Consumer they own |
|---|---|---|---|
| G24-MOONEY | Mooney IJCAI 1989 | ADAPT | Limited vs unrestricted *use* of macros |
| G24-MINTON1990 | Minton AIJ 1990 | ADOPT formula | `savings×freq − match` retention |
| G24-KU2013 | Kaliszyk & Urban CICM 2013 | ADAPT eval | ATP later thms ± extra lemmas |
| G24-KU2015 | Kaliszyk & Urban JSC 2015 | ADAPT eval; REJECT learner | Same, Flyspeck-scale; swamping |
| G24-REFACTOR | Jin et al. ICLR 2024 | REJECT extractor; ADOPT consumer | Subtree match+replace |
| G24-WB2024 | Wernhard & Bibel JAR 2024 | ADAPT | Structure-as-term / lemma generation |
| G24-WZ2025 | Wernhard & Zombori 2505.12305 | ADAPT | Metamath grammar compression |
| G24-W2026 | Wernhard 2602.15511 | ADAPT | Save-value synthesis; later ATP |
| G24-VSU2010 | Vyskočil et al. LPAR 2010 | ADAPT propose / REJECT consume | Proof-term compression |
| G24-GK2015A | Gauthier & Kaliszyk LPAR 2015 | REJECT neural; ADAPT shape | Cross-library later ATP |
| G24-GK2015B | Gauthier & Kaliszyk CPP 2015 | REJECT | Learned HOL4 selection |
| G24-GKU2016 | Gauthier et al. CICM 2016 | REJECT | Statistical conjecturing |
| G24-HETZL2012 | Hetzl et al. LPAR 2012 / 1401.4330 | ADAPT / LEAVE OPEN native | Cut-introduction |
| G24-FHN1972 | Fikes, Hart, Nilsson AIJ 1972 | ADOPT | MACROPS as later operators |
| G24-SINE | Hoder & Voronkov CADE 2011 | ADOPT | Symbolic premise selection |

## Non-claims

- No G2.4 checkbox. No causal reuse. No Paper B residual.
- No new miner, neural extractor, or hammer.
- AIJ 1990 full text was not obtained; the formula is charged from
  closed-access metadata plus primary-quoting secondaries named above.
- Local `raw/` bytes are fetch cache, not a redistributed corpus.
- Source verification here does not prove no nearer 2026 parent exists
  after the exact consumer is fixed (PARENTS.md measurement discipline).
