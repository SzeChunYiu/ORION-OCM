# Expert literature lanes — v1 (issue #833, section AC)

11 lanes. For each lane: canonical works to saturate (5–10 entries with citations + one-line
reason-to-saturate), plus the shared parent-literature-check protocol. This file is the index for the
terminology authority's expert lanes; it is a living document updated by the AC re-run before any
manuscript freeze.

Citation status: `VERIFIED` = checked against a live source during tranche build (2026-09-15);
unmarked entries are canonical field anchors entered from field knowledge and MUST be re-checked by the
AC re-run.

## Lane 1 — Theoretical CS / formal languages

| work | citation | why to saturate |
|---|---|---|
| Automata & formal languages | Hopcroft, Motwani & Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. 2006 | state/tape/quotient: the canonical state-carrier vocabulary GMI re-derives |
| Myhill–Nerode | Myhill 1957; Nerode 1958 | future-behavior equivalence IS right-language congruence in the deterministic finite case |
| Trace vs bisimulation spectrum | van Glabbeek, "The linear time — branching time spectrum I", 1990 | GMI equivalence claims must be slotted into the concurrency spectrum |
| Turing completeness/undecidable ceilings | Turing 1936; Hopcroft et al. ch. on undecidability | capability ceilings = computability bounds when the object is a universal function |
| Formal-language expressibility | Chomsky 1956 hierarchy | grammar expressiveness is encoding bias; the DSL-bias anchor |
| Computability of specification spaces | Rice's theorem (H. G. Rice 1953) | sets of computable functions are undecidable — anchors "specification space" claims |
| Complexity classes | Cook 1971 (SAT NP-complete); Arora–Barak 2009 | resource-bounded capability ceilings, comparisons to Karp reductions |

## Lane 2 — Statistical learning / information theory

| work | citation | why to saturate |
|---|---|---|
| Bias necessity | Mitchell, "The need for biases in learning generalizations", 1980 | the canonical inductive-bias definition; anchors "prior-free is ill-posed" |
| VC theory | Vapnik & Chervonenkis 1971; Vapnik 1995 | hypothesis-class capacity; dimension of the search space |
| NFL theorems | Wolpert & Macready, "No free lunch theorems for optimization", 1997 | no universal optimizer — ecologies needed for selection claims |
| MDL/compression | Rissanen 1978; Grünwald 2007 | model selection via description length; strongest parent for "selection" |
| Information capacity | Shannon 1948 | information-theoretic capabilities, capacity bounds |
| Identifiability | Manski, *Partial Identification of Probability Distributions*, 2003 | non-identifiability → abstention semantics |
| Calibration | Dawid, "The well-calibrated Bayesian", 1982 | uncertainty-calibration discipline for confidence sets |
| Random search baseline | Bergstra & Bengio, "Random search for hyper-parameter optimization", JMLR 2012 | the simplest search baseline all discoveries must beat |

## Lane 3 — Optimization / algorithm selection

| work | citation | why to saturate |
|---|---|---|
| Algorithm selection | Rice, "The algorithm selection problem", *Advances in Computers* 15, 1976 | the four-space parent (problem/feature/algorithm/performance + selection mapping) that GMI morphology selection must explicitly parent-subtract |
| Configuration selection | Hutter, Hoos, Leyton-Brown (SMAC), 2011 | hyperparameter/configuration selection is a distinct selection sense |
| Racing & successive halving | Maron & Moore 1994; Jamieson & Talwalkar 2016 (ASHA) | cost-aware candidate elimination — resource-crossover math |
| Multi-objective Pareto | Pareto 1906; Coello et al. 2007 overview | resource vector/directional dominance discipline |
| Landscape/crossover computation | Ruhe, *Algorithm Engineering*, 2010 | control-parameter and regime-map terminology |
| Portfolio selection | Gomes & Selman 2001; SATzilla | algorithm-portfolio selection is the strongest parent for "selection mapping" |

## Lane 4 — Program synthesis

| work | citation | why to saturate |
|---|---|---|
| SyGuS | Alur et al., "Syntax-guided synthesis", FMCAD 2013 | DSL/grammar bias is real and acknowledged — the exact anchor AB names |
| Sketching | Solar-Lezama, "Program synthesis by sketching", PhD thesis, 2008 | grammar-restricted SMT search, primitive-set discipline |
| Deductive synthesis | Manna & Waldinger, "A deductive approach to program synthesis", TOPLAS 1980 | constructive proof-as-derivation; parent of "derivation" claims |
| CEGIS | Solar-Lezama et al. 2006; Alur et al. 2013 | verifier-guided search — verification semantics for program discovery |
| Grammar-based GP | Koza 1992 genetic programming | grammar-seeded evolutionary search; the DSL-bias of GP formalized |
| Search strategies over libraries | Gulwani 2011 synthesis survey; Alur et al. "Search-based program synthesis" CACM 2018 | remint/regeneration vocabulary; library learning parent |
| Domain-specific languages | Fowler, *Domain-Specific Languages*, 2010 | DSL as bias carrier; expressiveness-cost tradeoff wording |

## Lane 5 — Neural architectures

| work | citation | why to saturate |
|---|---|---|
| Universal approximation | Cybenko 1989; Hornik 1991 | expressibility is not reachability — the discipline GMI must enforce |
| CNN/RNN/Attention provenance | LeCun et al. 1989/1998; Hochreiter & Schmidhuber 1997; Bahdanau 2015; Vaswani 2017 | named architectures are the "known families" to recover without macros |
| NAS | Zoph & Le 2017; ELM 2018 survey; NAS-bench 2019 | architecture search is a parent selection problem (not a native GMI term) |
| Depth/structure bounds | telgarsky 2016; Eldan & Shamir 2016 | structural capability bounds → capability-ceiling vocabulary |
| Inductive-bias of architectures | LeCun 1989 (local weight sharing); Cohen & Welling 2016 (equivariance) | architecture names = inductive-bias labels; pure "morphology" is derivative |
| Continual/synthetic gradients | Parisi et al. 2019 continual lifelong learning survey | development/continual-learning vocab parent |

## Lane 6 — RL / control

| work | citation | why to saturate |
|---|---|---|
| MDP/task formalism | Bellman 1957; Puterman 1994; Sutton & Barto 1998/2018 | environment/task distributions; operating regimes; reward-resource separation |
| Bandits & regret | Thompson 1933; Lai & Robbins 1985; Auer et al. 2002 | exploration/exploitation selection; regret as resource accounting |
| Model-free vs model-based | Sutton 1990/1991; RL surveys | the task-conditioned law family GMI "derives" |
| Optimal control | Pontryagin 1962; Bellman 1957 | control-theoretic ceilings and reachability |
| Belated credit assignment | Widrow & Hoff 1960; Werbos 1974/1988; Rumelhart et al. 1986 | reverse-mode credit assignment provenance (never "backprop" as discovery) |
| Active inference | Friston 2010-2020 | surprise-minimizing selection parent for perception/action separation |

## Lane 7 — Bayesian / causal inference

| work | citation | why to saturate |
|---|---|---|
| Bayes & updating | Bayes 1763; Jaynes 2003; MacKay 2003 | prior/update canonical senses; "prior-free" impossibility |
| Potential outcomes | Rubin 1974/1976; Holland 1986 | counterfactual control; negative twin parent |
| SCM/interventions | Pearl, *Causality* 2000 / *Causation* 2009; Neapolitan 2004 | causal terms must obey intervention/counterfactual semantics |
| Aleatoric vs epistemic | Kiureghian & Ditlevsen, "Aleatory or epistemic? Does it matter?", Structural Safety 2009 | the canonical split for uncertainty terms |
| Confidence/credible sets & calibration | Neyman 1937; Box 1980; Gelman et al. 2013 | confidence/credible/calibration vocab discipline |
| Partial identification | Manski 2003 | abstention and non-identifiability semantics |

## Lane 8 — Evolutionary computation / ALife

| work | citation | why to saturate |
|---|---|---|
| Evolvability | Wagner & Altenberg, "Complex adaptations and the evolution of evolvability", Evolution 1996 | canonical evolvability = capacity to generate adaptive heritable variation |
| Open-ended evolution | Taylor et al., "Open-ended evolution: perspectives from the OEE workshop in York", Artificial Life 2016 | the OEE definition; "open-ended" must tie here, never mean "large space" |
| Novelty search | Lehman & Stanley, "Exploiting open-endedness to solve problems through the search for novelty", ALIFE XI 2008 | origin of novelty-search; discovery-without-target vocabulary |
| Quality diversity / MAP-Elites | Mouret & Clune, "Illuminating search spaces by mapping elites", 2015; Pugh et al. 2016 survey | behavioral niche descriptors; species-as-occupancy vocabulary |
| GP/EvoCom foundations | Holland 1975; Koza 1992 | evolutionary selection; DSL bias in grammars |
| Neutral/rough fitness landscapes | Kimura 1983; van Nimwegen et al. 1999 | neutral search claims need landscape math, not a "neutral" label |
| Evolvability in ALife | Altenberg 1994; Pigliucci 2008 evolvability volume | quantitative evolvability (upper tail of offspring fitness) |

## Lane 9 — Cognitive science / neuroscience

| work | citation | why to saturate |
|---|---|---|
| Working memory | Baddeley & Hitch 1974 | GMI "working memory" must match the construct or state divergence |
| Episodic/semantic memory | Tulving 1972/1983 | memory taxonomy discipline |
| Metacognition | Flavell 1979; Nelson & Narens 1990 | metacognition = monitoring/control of one's own cognition |
| Theory of mind | Premack & Woodruff 1978; Baron-Cohen et al. 1985 | ToM operational criteria |
| Attention as selection | Broadbent 1958; Kahneman 1973 | attention-as-resource-rational-selection parent |
| Cognitive architecture | Newell 1990, *Unified Theories of Cognition* | UTC claims are the nearest strong parent for "unified intelligence theory" |
| Imitation/teaching/culture | Tomasello 1999; Whiten et al. 1999 | cultural-accumulation parent for teaching/culture terms |

## Lane 10 — Formal methods

| work | citation | why to saturate |
|---|---|---|
| Formal specification | Hierons et al. 2009 (ACM Computing Surveys); Gaudel 1994; van Lamsweerde 2000 | the definition of formal specification as mathematical description of intended behavior |
| Verification vs testing | Harel 1992 "Biting the Silver Bullet"; Wikipedia/class. formal-verification literature | executable-spec gap; verification asks whether an implementation satisfies the spec |
| Model checking | Clarke, Emerson & Sistla 1986 | exhaustive finite checking is verification on a bounded surface, not proof of universal |
| Hoare logic | Hoare 1969 | axiomatic semantics; state-precondition vocabulary |
| Refinement | Morgan 1990, *Programming from Specifications*; Abrial 1996 | spec→implementation refinement; correct-by-construction |
| Proof assistants / formal proof | Hales, "Formal proof", Notices AMS 2008; capture/coq-lean-isabelle | computer-assisted proof needs a certificate + checker; never "proof" for enumeration |
| Conformance/certification | standard conformance-testing literature | distinguishing formal verification, empirical validation, testing, certification |

## Lane 11 — Philosophy of science

| work | citation | why to saturate |
|---|---|---|
| Falsifiability | Popper, *The Logic of Scientific Discovery*, 1935/1959 | scoped claims need falsifiers; bare "closed" is not scientific |
| Confirmation & underdetermination | Hempel 1965; Quine 1951 | observation underdetermination — claims need stated scope and abstention |
| Causality & counterfactuals | Lewis 1973; Pearl 2000 | causal language registered against counterfactual semantics |
| Theory-ladenness / terms as theory | Kuhn 1962; Feyerabend 1962 | terminology IS theoretical commitment — the AB thesis itself |
| Novelty & discovery | Lakatos 1978 research programmes | what counts as novel empirical content vs footnote to parent programme |
| Emergence | Kim 1999; Butterfield & Isham 2001 | "emergence" claims need micro/macro distinction or are vacuous |
| Explanation & reduction | Nagel 1961; Salt 1977 | theory-reduction parent for "synthesis" claims |

## Parent-literature check protocol (per idea, before naming)

For every core GMI construct: (1) map the construct onto each of the 11 lanes' canonical terms; (2)
choose the earliest/strongest known parent (listing the parent each time); (3) if an established term
coincides with the object, adopt the field's primary term (AC box: "Prefer canonical field terminology
when definitions coincide"); (4) if terminology differs across fields, record the cross-field synonyms
and choose one primary paper term; (5) state whether the GMI contribution relative to that parent is a
theorem, a synthesis, a generalization, a new selection law, a new empirical result, or only
terminology — and log the row into `WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md`; (6) re-run the search before
every manuscript freeze (AC box: "Re-run literature search before manuscript freeze").
