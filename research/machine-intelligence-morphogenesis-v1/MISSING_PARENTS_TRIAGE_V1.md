# Missing-parents triage V1 (from the GMI-D0 primary-source depth pass)

Source: `PARENT_LEDGER_V2.json:missing_parents_reported` (70 items flagged by the family workers
while reading primary sources). Triage classes:

- **LB** — load-bearing for a registered Track-B row (GMI-T…) or rung; must be absorbed at ≥
  `PARTIAL_TEXT_READ` before `PARENT_COVERAGE_SATURATED_AT_GMI_V1_SCOPE` can be computed.
- **DR** — depth refinement of an already-absorbed parent; absorb opportunistically; does not block.
- **IR** — already in the repo (HST/HSG/Codex ledgers) at adequate depth; cross-reference only.

The class is a judgement recorded here so the next worker can contest it; nothing is dropped.

| item (family) | class | why / which row |
|---|---|---|
| Neary & Woods 2006, small universal TMs with polynomial-time simulation (P0) | **LB** | GMI-T1/B1: a *small* universal basis need not pay exponential simulation overhead — bounds `K_sim` for minimal bases; changes what "minimal" can cost |
| Gurevich 2000 ASM thesis; Dershowitz–Gurevich 2008; Boker & Dershowitz 2006 "Comparing computational power" (P0) | **LB** | GMI-T2/T3: the step-for-step behavioural-equivalence and "simulation up to representation" notions are the natural parents of `≈_{E,ε,K}` and `≡_K`; must be cited in DEFINITIONS_V2 §4 |
| Cook & Reckhow 1973; Slot & van Emde Boas 1984; Hartmanis–Stearns / Hennie–Stearns (P0) | DR | fine overhead catalogue behind the invariance thesis; GMI-T0 needs only finiteness of `K_sim` |
| Levin 1984 Kt / randomness conservation (P0) | DR | where Levin search is actually written; GMI-T8 cites Hutter 2002 already |
| Bennett 1988 logical depth; Solomonoff 1989 conceptual jump size (P0) | **LB** | GMI-T12: the only classical *developmental cost* laws (depth of a structure = compute to reach it from a short description); parents for `B_morph,g` |
| Blum 1971; McCreight–Meyer union; Borodin gap; Meyer–Fischer (P0) | DR | abstract complexity refinements of Blum speedup (GMI-T9 already parent-anchored) |
| Krajíček–Pudlák 1989 optimal proof systems; Chen–Flum 2010 (P0) | DR | verification-contract-relative optimality; relevant to the `ver` coordinate later |
| Rice–Shapiro; KLS; Hoyrup–Rojas "information carried by programs" (P0) | DR | GMI-T11 impossibility already trivial; these sharpen it |
| Board & Pitt 1990 reverse Occam; Ehrenfeucht et al. 1989 lower bound (P0) | DR | Occam family; P9B covers PAC/VC |
| Barron–Cover 1991; Rissanen 1983/1996; Wallace–Boulton MML (P0) | DR | MDL consistency; not load-bearing for a GMI row |
| Igel & Toussaint 2004; Auger & Teytaud 2010; Whitley & Rowe 2008; Wolpert & Macready 2005 (P0) | **LB** | GMI-T9: NFL's exact domain (permutation closure; continuous "free lunches") decides *where* NFL is silent — i.e. where phase laws may exist; must be stated precisely |
| Lattimore & Hutter 2011/2013 asymptotic optimality; Orseau/Ring delusion box; Sunehag–Hutter optimism (P1) | DR | universal-agent optimality refinements; GMI residual beyond P1 already located (bounded optimality) |
| Hernández-Orallo C-test / anytime test; Legg & Veness 2013 (P1) | DR | intelligence-measure family; not a morphology parent |
| Horvitz 1987; Zilberstein & Russell 1991/1996 anytime composition (P1) | **LB** | GMI-T10: composition of performance profiles is the parent for composing per-coordinate costs across composites (cost algebra of combinators, D2-§1.2) |
| Lieder & Griffiths 2020; Callaway et al. 2018 (P1) | IR | Codex PARENT_EXPANSION_V2 §D; META_SELECTION_PARENT_UPDATE_V1 |
| Ortega & Braun 2013; Genewein et al. 2015 information-theoretic bounded rationality (P1) | **LB** | GMI-T10: free-energy/KL form of bounded-rational selection is the direct parent of Codex's idealized KL phase theorem (GMI-V4-06); cite to avoid re-deriving it |
| Gigerenzer ecological rationality (P1) | DR | morphology–ecology matching in the empirical literature; qualitative |
| Aslanides, Leike & Hutter 2017 AIXIjs (P1) | DR | implementations |
| Hochreiter, Younger, Conwell 2001 (P4) | DR | first gradient-trained meta-RNN; history |
| Santoro 2016; Mishra 2018 SNAIL; Munkhdalai 2017 (P4) | DR | black-box meta-learners |
| **Chalmers 1990 "The evolution of learning"** (P4) | **LB** | B5 blind recovery: evolution rediscovers the delta rule in a fraction of runs — the earliest *blind recovery of a learning law* datum; must be in the ledger before any B5 protocol is designed |
| Oh et al. 2020 discovering RL algorithms; Kirsch et al. 2019 MetaGenRL (P4) | **LB** | GMI-T12/B3: learned update laws that generalize across environments; direct parents of "learning law as developmental product" |
| Metz et al. 2019/2020 learned-optimizer pathologies (P4) | DR | already partly in P4.LEARNED_OPTIMIZERS |
| **Mikulik et al. 2020 "Meta-trained agents implement Bayes-optimal agents"; Ortega et al. 2019; Müller et al. 2022 PFNs** (P4) | **LB** | GMI-T6/T12 and B3: a neural (M4) substrate under meta-training converges to the Bayes (M3) update law — an existing cross-paradigm learning-law *convergence* datum; kills any naive "Bayes law needs a probabilistic basis" claim (H-STOCHASTIC-DEGENERACY reading) |
| **Chan et al. 2022 data-distributional properties drive emergent ICL; Garg et al. 2022** (P4) | **LB** | GMI-T10/ECOLOGY_AXES: named ecology axes (burstiness, Zipfian class distribution, dynamic meaning) that switch a substrate between memorization (M5-like) and in-context learning — a *published phase law with axes*; register as parent for the `task_diversity` / distribution-structure axes |
| Raghu et al. 2020 rapid learning or feature reuse (P4) | DR | what MAML develops |
| Grant et al. 2018 hierarchical Bayes view of MAML; Franceschi 2018 (P4) | DR | learning-law correspondence M4↔M3 at the meta level |
| Schlag–Irie–Schmidhuber 2021 fast weight programmers; Irie 2022 (P4) | DR | self-referential weights; in P2 history |
| Miconi 2018/2019; Randazzo 2020 MPLP; Gregor 2020 (P4) | IR | Codex PARENT_EXPANSION_V2 §E |
| Zenke 2017; Rusu 2016; Lopez-Paz 2017; McClelland 1995 CLS (P4) | DR | continual-learning family; `drift` axis parents |
| Maurer et al. 2016; PAC-Bayes meta-bounds (P4) | IR | HST ledger |
| Wingate, Stuhlmüller, Goodman 2011 transformational compilation (P6) | **LB** | GMI-T6/Stage D: the actual *compiler* from a probabilistic program to an inference engine with reported overhead — a D1 instance for M3 |
| Ścibior et al. 2018; Lew et al. 2020 trace types; Borgström et al. 2016 (P6) | DR | semantics/soundness; GMI-T6 finite scope does not need them |
| Freer & Roy 2012; Ackerman–Freer–Roy 2017 disintegration (P6) | DR | refinements of the conditioning limit |
| **Cooper 1990; Dagum & Luby 1993** (P6) | **LB** | ECOLOGY_AXES / GMI-T10: NP-hardness of exact and approximate inference is the *complexity* limit of M3 inside the computable region — a resource axis (treewidth) on which M3 loses to M4/M5 |
| Gershman & Goodman 2014 amortized inference; Hinton et al. 1995 wake-sleep (P6) | IR | P6.AMORTIZED_INFERENCE_HYBRID |
| Griffiths, Vul, Sanborn 2012; Vul et al. 2014 "one and done" (P6) | DR | resource-rational sampling |
| Saad et al. 2019 Bayesian synthesis of probabilistic programs; Ellis 2022 (P6) | DR | M3/M2 hybrid; P5 covers program synthesis |
| Rezende et al. 2014 (P6) | DR | VAE co-discovery |
| Braithwaite, Hedges, Smithe 2023 compositional Bayesian inference (P7) | DR | canonical statement of Bayesian lenses; P7.BAYESIAN_LENSES has Smithe 2020 full text |
| **Gavranović 2022 space-time tradeoffs of lenses and optics** (P7) | **LB** | GMI-T5/P7.RESOURCE_SILENCE: the one categorical-cybernetics paper that charges resources (space/time of lens composition) — decides whether the "categorical works charge nothing" claim in THEOREM_REGISTRY_CANONICAL_377 GMI-T5 is exactly right |
| Hedges 2019 open learners→open games; Fong & Johnson 2019 lenses and learners; Dalrymple 2019 dioptics (P7) | DR | Learn/Lens/Game embeddings |
| Sprunger & Katsumata 2019 delayed trace; CHAD; Alvarez-Picallo et al. 2021 (P7) | DR | RNN/AD inside categorical settings |
| Dudzik et al. 2024 asynchronous alignment; **Xu et al. 2019 "What can neural networks reason about?"** (P7) | **LB** (Xu) | GMI-T10/T4: algorithmic-alignment sample-complexity theorem is the only *resource* result in the neural↔DP bridge; a phase-law parent (architecture aligned to algorithm ⇒ lower sample complexity) |
| de Moor 1994; Bird & de Moor 1997 algebra of programming (P7) | DR | programmatic morphology's own algebra |
| Smithe 2022 open dynamical systems as Poly coalgebras; Myers categorical systems theory (P7) | DR | Poly parents in Codex PARENT_EXPANSION_V2 §A |
| Bolt, Hedges, Zahn 2019 Bayesian open games (P7) | DR | — |
| Egri-Nagy & Nehaniv 2013; Maler 2010 Krohn–Rhodes (P7) | IR | #145/HSG semigroup rows |
| Cho & Jacobs 2019; Fritz 2020 (P7) | IR | Codex PARENT_EXPANSION_V2 §B |

## Load-bearing set to absorb before any saturation computation (12 items)

Neary & Woods 2006 · Gurevich/Boker–Dershowitz · Bennett 1988 + Solomonoff 1989 · NFL domain
refinements (Igel–Toussaint; Auger–Teytaud; Whitley–Rowe) · Zilberstein–Russell anytime composition ·
Ortega–Braun / Genewein bounded rationality · **Chalmers 1990** · Oh et al. 2020 / MetaGenRL ·
**Mikulik et al. 2020 (+ Ortega 2019, PFNs)** · **Chan et al. 2022 (+ Garg 2022)** · Wingate et al.
2011 · Cooper 1990 / Dagum–Luby 1993 · Gavranović 2022 · Xu et al. 2019.

These are assigned to the follow-up depth worker together with the still-uncovered #377 families
(P2 at proof depth; P3 beyond AutoML-Zero; P5 beyond DreamCoder; P8 beyond Sigma/Hyperon).
