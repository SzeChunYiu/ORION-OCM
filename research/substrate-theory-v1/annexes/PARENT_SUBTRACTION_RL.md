# ORION-OCM Field Brief: RL / Control / Memory — Parent-Subtracted Import Candidates

Scope: 6 fields, 19 candidate imports. Each bound to a numbered OCM finding (M1B =
library useful only when served through applicability; M2-P1 = history induces a
genuine search prior, stored answers worth zero, shuffled history worse than none;
DEV-CAL-3/4 = acquisition-charging amortisation corrected, ledger recovered positive;
NEG-I = standing negative: learned applicability I missing) or a slot of
u = <Z, I, phi, beta, Psi, V, W, C, L, P>. Parent subtraction is brutal by design.

---

## Field 1: Options / Affordances / Hierarchical RL

Closest existing OCM relative: the I and beta slots themselves (oracle-or-absent) plus
the veto gate's "which generator where" decision — OCM already rediscovered that
applicability is load-bearing (M1B); what it lacks is machinery that LEARNS it.

### 1.1 Options framework (semi-MDP temporal abstraction)

1. Addresses: NEG-I; formalizes M1B — value lives in the initiation decision, not
   fragment content (option-internal policy quality is secondary to option selection
   in the semi-MDP Bellman equation, exactly M1B's integration-secondary finding).
2. Strongest parent: Sutton, Precup, Singh, "Between MDPs and semi-MDPs" (AIJ 1999):
   option = <I, pi, beta>, initiation predicate, termination function, planning over
   options at semi-MDP timescales.
3. Object to assimilate: option triple typed onto u: I as measure over Z (contexts,
   not raw states), beta as stopping time WITH a fallback branch (OCM's semantic,
   absent in options — keep it); semi-MDP backup Q(s,o)=E[r + gamma^k max Q(s',o')],
   k the random option duration. Claim: u is an option whose option-set is mined and
   priced.
4. Novel after subtraction: triples, termination, semi-MDP math are the parent's.
   Residue: (a) options are free, OCM options carry C + amortised charges, so I =
   "where does this pay back amortised cost", not "where executable"; (b) option
   inventory is mined. Economic wrapper on a 1999 formalism.
5. Minimal implementation: type the registry so I: Z->[0,1] and beta: Z->[0,1] are
   explicit learned objects; serve by option-level value backup instead of oracle I.
   Consumes existing serving logs. Bookkeeping only, a few hundred lines.
6. Falsification: degenerate-I (I=1 everywhere) + learned backup vs M1B oracle config;
   fixed-beta knockout to separate selection from timing effects. Terminal: ecology
   accuracy vs parent. If degenerate-I matches oracle, the formalization adds nothing.

### 1.2 Option-critic (end-to-end learned initiation/termination)

1. Addresses: NEG-I precisely — canonical proof that I and beta are learnable by
   gradients inside the policy.
2. Strongest parent: Bacon, Harb, Precup, "The Option-Critic Architecture" (AAAI
   2017): termination gradient theorem, intra-option policy gradient, policy over
   options.
3. Object to assimilate: dJ/dtheta_beta = E[delta_t grad log beta(s)]; initiation as
   softmax over units conditioned on Z with gradient from downstream return.
4. Novel after subtraction: option-critic learns I from task reward; OCM has no dense
   reward — I must be supervised by the LEDGER (amortised return of serving events).
   Residue: initiation trained on economic signal = substituting the critic target.
   Gradient theorems are the parent's; thin but high-value delta.
5. Minimal implementation: learned router head p(unit|Z) over the library, trained on
   logged serving outcomes with target = realised amortised value (data exists post
   DEV-CAL-3/4). One head + ledger join. Highest value-per-line in this brief.
6. Falsification: random-init vs ledger-trained vs oracle I, library frozen. If
   ledger-trained routing does not beat RANDOM, the ledger cannot supervise I and
   NEG-I is a supervision-availability failure — locating the defect in Z instead.

### 1.3 Affordances as dynamics-gated availability

1. Addresses: NEG-I plus Psi — availability is a property of the system-environment
   pair (what the fragment does to the future), coupling I to an effect model.
2. Strongest parent: Khetarpal, Ryzhov, Tachet des Combes, Faust, Precup, "What can
   I do here? A Theory of Affordances in RL" (ICML 2020, arXiv:2006.15085); Gibson
   (1979) for origin.
3. Object to assimilate: affordance = actions whose state-conditioned effect
   distribution is distinguishable from a null kernel; transposed: fragment f
   affords in z iff P(future|z, serve f) distinguishable from P(future|z, no serve).
   I becomes a per-context hypothesis test, falsifiable, not a classifier output.
4. Novel after subtraction: parent assumes given action set, known dynamics. Residue:
   "actions" are mined fragments with capital cost; null = free behavior. Residue =
   effect-size-gated router against a do-nothing baseline.
5. Minimal implementation: two-sample tests (served vs unserved outcomes) per
   (unit, context-bucket) from existing logs -> affordance table. Pure statistics,
   no training loop; a first learned I with no gradients.
6. Falsification: transplant I learned on one formal language to a held-out language:
   if transfer does not beat the parent (oracle or 1.2 in-ecology router),
   applicability is ecology-specific memorization, killing the "I is a law of the
   ecology" hypothesis.

### 1.4 Feudal RL / MAXQ (manager sets goals; value decomposes)

1. Addresses: NEG-I from above — the missing router IS a manager whose action space
   is the library; MAXQ supplies the attribution needed for composed (multi-fragment)
   trajectories once routing is learned.
2. Strongest parent: Dayan & Hinton, "Feudal RL" (NeurIPS 1993); Vezhnevets et al.,
   FeUdal Networks (ICML 2017) for differentiable manager-direction subgoals;
   Dietterich, "MAXQ" (JAIR 2000) for decomposed value.
3. Object to assimilate: MAXQ projected decomposition Q(i,s)=V(i,s)+C(a|s) giving
   per-node marginal attribution; FuN manager emitting latent directions every k
   steps, workers rewarded for moving along them.
4. Novel after subtraction: parents fix or end-to-end-train the hierarchy; MAXQ
   assumes a GIVEN hierarchy. OCM mines it (support-rank) and prices it. Residue: a
   mined, priced hierarchy where the manager's choice set is the charged inventory —
   the wrapper again; attribution math is MAXQ's.
5. Minimal implementation: attribution half only — instrument serving trajectories
   with the completion-function split so each unit gets MARGINAL not total credit;
   upgrades the ledger's charge basis. Moderate bookkeeping.
6. Falsification: on 2+-fragment tasks, marginal-credit vs total-credit ledger as
   1.2's training signal: if router quality is equal, decomposition is decorative —
   a cheap null to run before building any manager.

---

## Field 2: Predictive-State Representations / Successor Features / World Models

Closest existing OCM relative: support-rank mining is crude frequency-based
sufficient-statistic extraction; the veto gate's "library recovers all motifs" is a
generative-coverage criterion — proto-predictive-state ideas with no predictive model
ever placed in the loop.

### 2.1 Predictive state representations

1. Addresses: Psi (absent from the loop) and Z — PSR says the right context
   representation is the sufficient vector of future test predictions; OCM's Z is a
   mined fragment label, not a predictive statistic.
2. Strongest parent: Littman, Sutton, Singh, "Predictive Representations of State"
   (NeurIPS 2001); Boots, Singh, Gordon, spectral PSR (2011); Boots & Gordon,
   "Predictive State TD Learning" (NeurIPS 2010).
3. Object to assimilate: any system has a linear PSR of dimension = rank of the
   test-History matrix; state b_t = P(tests|history), rank-one updates per step.
   Invariant: Z = minimal test set whose predictions suffice for all tests.
   Transposition: the library IS a test set; Z(z) = predicted effect of serving each
   fragment.
4. Novel after subtraction: sufficiency machinery, spectral learning, linear dynamics
   are the parent's. Residue: PSR tests are generic probes; OCM's are mined, priced
   units — test acquisition priced in C. "Library-as-state with priced tests" — thin.
5. Minimal implementation: fixed battery of observable probes per ecology (outcome,
   next-token stats, cost-to-completion); regress each on context features from logs;
   Z := predicted-probe vector. Gives Psi a first instantiation with no generative
   model. Low, log-based.
6. Falsification: router (1.2) fed with PSR-Z vs fragment-identity-Z, plus a
   shuffled-probe control (must reproduce M2-P1's shuffled-worse signature). If PSR-Z
   does not improve learned I, applicability is not a function of predictable
   futures — wrong substrate for NEG-I.

### 2.2 Successor features / generalized policy improvement

1. Addresses: V slot — no per-unit conditional value object exists; M1B's
   which-fragment-helps-where is exactly a (context, fragment) successor matrix.
2. Strongest parent: Barreto et al., "Successor Features for Transfer in RL" (ICML
   2017) + GPI; ancestor Dayan, successor representations (NeurIPS 1993).
3. Object to assimilate: Q(s,a) = psi(s,a)^T w, psi = discounted feature occupancy;
   task change = w change only. Transposed: psi_f(z) = expected context-type
   occupancy after serving f; new ecology target = new w; serving value = psi^T w
   with C_f charged into w (cost as a negative reward feature — the cleanest ledger
   integration available).
4. Novel after subtraction: transfer math and composition guarantees are the
   parent's; SF assumes fixed features. Residue: features = mined fragments,
   acquisition cost as explicit negative reward channel making amortisation
   first-class in w. Most natural formal home for the DEV-CAL-3/4 ledger — but the
   residue is the charge semantics, not math.
5. Minimal implementation: tabular Monte-Carlo psi_f(z) from serving logs; regress w
   per ecology target on realised amortised return; serve greedily. Tabular, logs
   only; independently yields a learned router (non-gradient twin of 1.2).
6. Falsification: transplant: estimate (psi, w) on one authored regime, apply to a
   perturbed regime with w-refit only (SF's transfer promise). If psi must be
   re-mined per regime to recover performance, the successor object is unstable
   across OCM ecologies and transfer is void. Terminal: amortised-return gap.

### 2.3 Latent world models, Dreamer line (RSSM + imagination planning)

1. Addresses: Psi at full strength; beta's fallback (terminate when prediction
   confidence collapses); and the veto gate — Dreamer's reconstruction/return
   criteria are the industrial standard for "is this learned model trustworthy
   enough to act through"; motif-coverage is a special case.
2. Strongest parent: Hafner et al., PlaNet (2019), Dreamer (2020), DreamerV2 (2021),
   DreamerV3 "Mastering diverse domains through world models" (Nature 2023).
3. Object to assimilate: RSSM prior/posterior with KL balance; decision rule
   "act entirely against the model"; beta definable as a function of
   posterior-prior divergence (fallback when the effect model stops tracking
   reality).
4. Novel after subtraction: brutal — Dreamer is monolithic (one model, no
   applicability, no economics) and mixture-of-experts world models already exist;
   "many small models + routing" is not novel either. Residue ONLY: per-unit
   admission priced by C with the veto gate replacing uniform trust. Weak at
   mechanism level; useful as trust-gating vocabulary.
5. Minimal implementation: import just divergence-triggered beta: small
   next-context predictor per admitted generator (Psi-lite from 2.1 probes), beta=1
   when error exceeds a calibrated threshold -> fallback path. Low complexity.
6. Falsification: corrupt per-unit predictors deliberately; verify beta's fallback
   fires and protects performance (vs oracle-beta parent). If performance under
   corrupted Psi equals performance with no Psi at all, the effect model is
   epiphenomenal and Psi can be deferred — a useful cheap negative.

---

## Field 3: Adaptive Control / Persistent Excitation / System Identification

Closest existing OCM relative: the per-acquisition charge with amortisation across
targets is an un-theorised value-of-information accountant — adaptive control
(excitation, dual control, concurrent learning) supplies the theory it lacks.

### 3.1 Persistent excitation as convergence condition for learned I

1. Addresses: NEG-I with a possible ROOT CAUSE — learned I may fail because the
   training stream is rank-deficient in context coverage, so no estimator could
   identify applicability. Also binds L (plasticity = retained identifiability).
2. Strongest parent: Narendra & Annaswamy, "Stable Adaptive Systems" (1989): PE iff
   integral_t^{t+T} phi phi^T >= alpha I; parameter convergence iff PE. Unification:
   Annaswamy et al., Annual Review of Control 2023 (10.1146/annurev-control-062922-
   090153).
3. Object to assimilate: excitation matrix G = sum_t z_t z_t^T of the context stream;
   rank(G) = number of directions in which I is identifiable. Converts "learned I is
   missing" from method gap to measurable data property — compute rank(G) per
   ecology before blaming the learner.
4. Novel after subtraction: PE is a 60-year-old condition, not a mechanism; applying
   it to an applicability predicate is routine. Residue: PRICED excitation —
   deliberately probe low-eigenvalue context directions and charge the probe to C as
   investment. The pricing wrapper is ours.
5. Minimal implementation: diagnostic only — context-covariance spectrum over logs
   per ecology; correlate rank with where learned-I failed. One script. Cheapest
   diagnostic in the brief; run FIRST.
6. Falsification: enrich context distribution to provably full rank (uniform over
   contexts), retry 1.2 router: if I still fails, PE is exonerated — failure is
   representational (Z-level); if I succeeds, NEG-I collapses to a sampling-policy
   fix. Either terminal is a result.

### 3.2 Dual control / Bayes-adaptive probing

1. Addresses: DEV-CAL-3/4 directly — acquisition charging is an empirical
   rediscovery of dual control's tradeoff: actions must exploit estimates AND excite
   the system. OCM's amortisation is a hand-rolled value-of-information calc.
2. Strongest parent: Feldbaum, dual control (1960-61); Duff, Bayes-adaptive MDPs
   (2002) as the computable idealization.
3. Object to assimilate: certainty-equivalence (act on point estimates — OCM today)
   vs dual control (actions valued by posterior including information gain); the
   probing value E[value|action] - E[value|no action] includes belief sharpening.
4. Novel after subtraction: brutal — dual/Bayes-adaptive control is intractable;
   every practical system approximates, and OCM's ledger is such an approximation,
   not a novel one. Residue: amortisation-across-targets (one probe informs MANY
   downstream targets) — multi-target amortisation of information is the only
   OCM-shaped piece.
5. Minimal implementation: formalise, don't build: write the acquisition decision as
   expected-amortised-VOI over logged acquisitions and audit DEV-CAL-3/4 semantics
   against the decomposition — documentation-level, exposes residual charging errors.
6. Falsification: withhold ledger-booked high-VOI acquisitions and replay: if
   downstream performance is unchanged, the VOI proxy is decorative and acquisition
   order could be random — direct audit of the recovered-positive mechanism.

### 3.3 Concurrent learning (excitation from recorded data)

1. Addresses: M2-P1 with a mechanism — recorded history is an excitation reservoir;
   stored answers are rank-1 (no new directions, zero value); shuffled history
   destroys the (state, effect) pairing while keeping marginals = actively misleading
   identification, hence WORSE than none. Tightest theory-experiment fit here.
2. Strongest parent: Chowdhary et al., concurrent learning (2010-14): SVD-based
   accumulation over RECORDED data replaces PE-by-probing; plus experience replay
   strengthening the excitation condition (J. Guidance 2022, 10.2514/1.G008162).
3. Object to assimilate: Gram matrix G = sum tau tau^T over a SELECTED memory (keep
   samples that grow min singular value — the "stack"); invariant: memory is
   valuable exactly when it raises excitation rank. Gives P (causal support) a
   principled retention criterion.
4. Novel after subtraction: stack update, SVD trigger, convergence proofs are the
   parent's. Residue: applying it at FRAGMENT level — memory entries are (context,
   fragment, effect) and the excitation accumulated is identifiability of
   per-fragment applicability. Converts M2-P1 from finding into mechanism; modest
   but real.
5. Minimal implementation: concurrent-learning memory stack over serving logs:
   admit (z, f, outcome) iff it grows min-singular-value of the design matrix; train
   1.2's router on the stack. A data-selection filter in front of existing training.
6. Falsification: train router on (a) full log, (b) CL-selected stack, (c) equal-n
   shuffled log. M2-P1 predicts (c)<(a); CL predicts (b)>=(a) with less data. If
   (b) does not beat (a), the M2-P1 prior is not an excitation phenomenon —
   falsifying this import's core claim on OCM's own ecologies.

---

## Field 4: Causal Inference for Intervention Discovery

Closest existing OCM relative: W and P are named-but-empty causal machinery; the veto
gate is an intervention-free goodness criterion — no do-operator anywhere in the loop.

### 4.1 Interventional semantics (do-calculus, interventional equivalence)

1. Addresses: W and P — no formal language for what a serving event IS: serving is
   do(f) on the task-solving process; M2-P1's shuffle harm is a destroyed-pairing/
   confounding phenomenon that interventional semantics makes statable.
2. Strongest parent: Pearl, "Causality" (2009); Hauser & Buhlmann, interventional
   Markov equivalence / GIES (JRSS-B 2012) — which interventions identify which edges.
3. Object to assimilate: serving f in z samples P(outcome|do(serve f), z); W records
   which registry entries are interventional vs observational; the interventional
   equivalence class defines what OCM can learn from its log composition (mostly
   self-selected servings = confounded).
4. Novel after subtraction: a notation act, not a contribution. Residue: ~none at
   math level; only that interventions are PRICED (each do(f) carries C), making
   identifiability-vs-budget explicit. Vocabulary import.
5. Minimal implementation: tag ledger entries observational/interventional + serving
   propensity. Schema change that makes confoundedness of I-learning data auditable.
   Trivial code, high diagnostic value for NEG-I.
6. Falsification: propensity-stratified M1B reanalysis: if the serving benefit
   persists only in high-propensity strata and vanishes under forced-random servings,
   M1B is confounded by selection — a devastating, cheap audit to run before trusting
   any router.

### 4.2 Causal bandits / budgeted active intervention design

1. Addresses: C + NEG-I jointly — which fragment to acquire, and where to probe
   applicability, are intervention-budget problems; acquisition is currently by
   support-rank (frequency heuristic) with no value-of-intervention logic.
2. Strongest parent: Lattimore et al., causal bandits (2016); Zhang/Bareinboim,
   active optimal intervention design (arXiv:2209.04744); budgeted structure
   learning (DODO 2025); "partial structure suffices for no-regret" (2024).
3. Object to assimilate: arm value depends only on the ancestor subgraph of the
   reward (2024 result). Transposed: value of acquiring f depends only on the
   sub-ecology of contexts f could serve — the whole ecology need not be modelled
   to price an acquisition.
4. Novel after subtraction: parents assume known graph, known variables. OCM's arms
   are mined fragments (variables invented by the miner); the "graph" is
   context-fragment-effect support in P. Residue: arm-creation pricing on top of
   causal bandits. Real but narrow.
5. Minimal implementation: replace support-rank ordering with ancestor-subgraph
   value estimate: per candidate fragment, estimate servable sub-ecology from mining
   stats + expected amortised return there; acquire greedily by value-per-charge.
6. Falsification: greedy-value vs support-rank vs random acquisition at equal
   capital, terminal = amortised-return-per-capital. If greedy-value does not
   dominate support-rank, the miner's frequency order is already near-optimal and C
   adds nothing to acquisition — falsifying the economic wrapper itself.

### 4.3 Invariance-based discovery (ICP): applicability as invariant usefulness

1. Addresses: NEG-I with a second estimator: I = contexts where a fragment's
   usefulness is INVARIANT across ecology perturbations — causal fragments work
   wherever their cause operates; spurious correlations break under shift.
2. Strongest parent: Peters, Buhlmann, Meinshausen, "Invariant Causal Prediction"
   (JRSS-B 2016); IRM (Arjovsky et al. 2019) as the representation cousin.
3. Object to assimilate: a predictor invariant across environments uses only causal
   parents of the target. OCM's authored-history regimes are literally the required
   perturbation set — OCM already builds the ICP data structure without knowing it.
4. Novel after subtraction: ICP targets a LABEL; OCM's target is utility —
   "invariant utility" has no causal guarantee (stable spuriousness possible).
   Honest residue: an estimator whose guarantee degrades exactly as utility is
   non-causal; OCM's contribution would be measuring that degradation. Thin as
   theory; valuable as a second gradient-free router.
5. Minimal implementation: partition serving logs by authored regime; per fragment,
   test effect-stability across regimes per context bucket; I_f = stable set. Same
   log statistics as 1.3 — affordance and invariance tables in one pass.
6. Falsification: disagreement analysis: if invariance-I and affordance-I (1.3)
   agree, both measure the same object, either suffices; if not, transplant both
   into a regime-shifted ecology — whichever survives measures the causal quantity;
   the other is falsified as memorization.

---

## Field 5: Complementary Learning Systems / Replay / Consolidation

Closest existing OCM relative: the two-population structure exists implicitly — fast
mined fragments (hippocampal) vs slow veto-admitted generator (neocortical) — but no
replay or consolidation loop connects them; the gate checks once at admission.

### 5.1 CLS dual-store architecture

1. Addresses: L and the missing consolidation loop; explains WHY the veto gate works
   — isolating rapid fragment acquisition from the generator prevents interference
   (CLS's central computational argument).
2. Strongest parent: McClelland, McNaughton, O'Reilly (Psychological Review 1995);
   Kumaran, Hassabis, McClelland (TiCS 2016) for the deep-learning statement.
3. Object to assimilate: the interleaved-learning requirement — neocortical
   (generator) learning must be slow and INTERLEAVED over stored episodes to avoid
   catastrophic interference; the consolidation-rate ratio between stores is the
   anti-forgetting control variable.
4. Novel after subtraction: a 30-year-old architectural hypothesis with thousands of
   instantiations. Residue: the consolidation decision is PRICED — only fragments
   whose amortisation justifies interleaved retraining get consolidated. CLS says
   "interleave everything"; OCM can only afford what pays.
5. Minimal implementation: retrain the generator interleaved over the fragment
   buffer (uniform mixture) instead of fit-once-at-veto, with replay cost booked in
   C. Touches training schedule + ledger only.
6. Falsification: sweep interleaving ratio (sequential -> fully interleaved) at fixed
   capital: if generator quality and downstream return are flat in the ratio, the
   predicted interference is absent in OCM's regime (discrete fragments may not
   interfere) and 5.1 is falsified AS IMPORTED.

### 5.2 Prioritized memory access (Schaul / Mattar-Daw)

1. Addresses: M2-P1's search prior — Mattar & Daw formalize replay scheduling by
   expected gain = need x chance-of-use, including the prediction that replay value
   is realised through CHANGED DECISIONS, not content recitation (M1B: retrieval
   timing null, content secondary — the same dissociation).
2. Strongest parent: Schaul et al., prioritized experience replay (ICLR 2016);
   Mattar & Daw, Nature Neuroscience 2018.
3. Object to assimilate: G(z) = need(z) x chance-of-use(z) as retrieval score;
   need = value of knowing the state, chance = trajectory proximity.
4. Novel after subtraction: Mattar-Daw fully covers M2-P1 (prior, zero-value stored
   answers, harmful shuffle breaking the gain estimate). Residue after brutal
   subtraction: the fragment-library instantiation — retrieve WHICH UNIT to serve,
   scored by amortised-return gain. Theory theirs; OCM adds a domain instance.
5. Minimal implementation: rank units per context by need x chance (need = value at
   stake from ledger; chance = applicability posterior from 1.2/1.3), serve top-rank.
   Scoring layer over already-computed objects.
6. Falsification: need-only and chance-only knockouts: if either factor alone matches
   full gain, the product adds nothing; if full gain fails to beat random serving on
   M1B-null ecologies, the instantiation is void. M1B already half-falsifies this
   import — real chance of a cheap negative.

### 5.3 Generative replay / distillation (DGR line)

1. Addresses: the consolidation mechanism — the veto gate is the ACCEPTANCE TEST of
   a generative-replay consolidation that is never run; nothing maintains old
   fragment coverage as the library grows.
2. Strongest parent: Shin et al., "Continual learning with deep generative replay"
   (NeurIPS 2017); van de Ven et al. (2020) unifying replay types.
3. Object to assimilate: pseudo-rehearsal — the generator samples synthetic
   instances of past fragments; consolidated model trains on new + generated-old
   mixture, maintaining coverage without storing raw history (which M2-P1 shows is
   dangerous: stored answers worth zero; the generator is the safe compression).
4. Novel after subtraction: DGR preserves old-task performance in a monolithic
   model — standard mechanism. Residue: WHICH past content to generate is priced —
   replay budget allocated by amortised value, dropping non-paying fragments.
5. Minimal implementation: per mining batch, retrain generator on a ledger-weighted
   mixture (weight = fragment amortised return), then verify the veto gate still
   passes; coverage should fall exactly where return was negative.
6. Falsification: drop the lowest-amortisation quartile from replay: generator motif
   recovery must hold on retained, fall on dropped; downstream return vs full-replay
   parent. If return does not drop while dropped motifs degrade, the library carried
   dead weight and C-charged retention wins; if it drops, amortisation undercounts
   future value and DEV-CAL is incomplete.

---

## Field 6: Continual Learning & Plasticity Loss

Closest existing OCM relative: L is named with no mechanism; support-rank mining
(count desc, length desc) is itself a plasticity risk — the library accretes toward
training-ecology frequencies with no retirement, recycling, or protection.

### 6.1 Importance-weighted consolidation (EWC / SI)

1. Addresses: L + admitted-generator stability — mining batches must not degrade an
   admitted generator; EWC is the standard protection mechanism.
2. Strongest parent: Kirkpatrick et al., EWC (PNAS 2017); Zenke et al., synaptic
   intelligence (ICML 2017).
3. Object to assimilate: Fisher penalty loss + sum_i F_i (theta_i - theta_i*)^2
   anchoring parameters to values that mattered for motif recovery; SI's online
   importance accumulator as the cheap version.
4. Novel after subtraction: EWC/SI protect a single network on a task stream —
   parent's wholly. OCM's split population (protected generator vs free library)
   already sidesteps interference (that is 5.1's point). Residue ~zero unless
   generators share parameters. Verdict: import only for a shared generator.
5. Minimal implementation: none now; if a shared-parameter generator appears, an SI
   accumulator over training batches. Flag, don't build.
6. Falsification: pre-registered null: verify EWC anchor = plain interleaved replay
   for generator stability — confirming the architecture externalizes what EWC
   internalizes; file PARENT_SUFFICIENT.

### 6.2 Replay-with-constraints (A-GEM / DER++)

1. Addresses: the operational consolidation loop — A-GEM's episodic constraint is
   exactly "consolidate new fragments without violating old motif coverage": a SOFT
   veto gate during training instead of a binary check after it.
2. Strongest parent: Chaudhry et al., A-GEM (ICLR 2019); Buzzega et al., DER++
   (NeurIPS 2020).
3. Object to assimilate: gradient projection g := g - <g,g_mem>/||g_mem||^2 g_mem
   when a step would increase loss on the memory buffer; transposed: generator
   updates must not increase reconstruction error on the retained-fragment buffer.
4. Novel after subtraction: general continual-learning plumbing, parent's. Residue:
   buffer membership economics — which fragments enter the anchor buffer is a
   capital decision, vs parents' uniform/recency sampling. Shared with 5.3.
5. Minimal implementation: A-GEM projection around generator training over a
   ledger-weighted fragment buffer. Small code, moderate compute.
6. Falsification: constraint on/off at fixed buffer and capital: if motif recovery
   is equal (interleaving suffices), the constraint is redundant — parent-sufficient,
   keep only the sampler.

### 6.3 Plasticity maintenance (continual backprop / dormant neurons / resets)

1. Addresses: L as ACTIVE mechanism — deepest resonance in this brief: continual
   backprop's utility-weighted reinitialization IS capital recycling. The ledger
   already computes per-unit amortised return; the missing half is a retirement
   policy that recycles capacity into new mining. Latent risk: support-rank mining
   accretes monotonically, so library capacity silently saturates toward the
   training ecology (library-level plasticity loss).
2. Strongest parent: Dohare, Hernandez-Garcia, Rahman, Lan, Sutton, Mahmood, "Loss
   of plasticity in deep continual learning" (Nature 632:768-774, 2024) — continual
   backprop reinitializes least-useful units by utility; Sokar et al., dormant
   neuron phenomenon / ReDo (ICML 2023); Nikishin et al., primacy bias / resets
   (ICML 2022).
3. Object to assimilate: utility u_i = discounted running average of contribution,
   retirement threshold and recycle rate as control knobs; empirical law: without
   recycling, learnability decays to shallow-network level on long sequences.
   Transposed: u_i := amortised return (already computed post DEV-CAL); retire the
   bottom tail, refund booked C to the acquisition budget.
4. Novel after subtraction: continual backprop recycles weights INSIDE one network;
   OCM recycles REGISTERED UNITS in a market with a capital-refund loop (retired
   capital returns to the acquisition pool, feeding 4.2). Refund loop + priced
   retirement are genuinely OCM-shaped — strongest candidate for residue beyond the
   wrapper: the ledger turns a per-weight heuristic into a per-unit market with
   conserved capital.
5. Minimal implementation: retirement sweep every K batches: retire units below
   amortisation threshold over window, refund booked C to the acquisition pool.
   Registry job + ledger transfer; no model changes.
6. Falsification: long target sequences at fixed total capital: recycling-market
   (retire+refund+greedy reacquire) vs accretion-only (current OCM) vs
   random-replacement churn. If accretion-only matches, the library never saturates
   and L is unnecessary (structurally informative); if random churn matches utility
   recycling, amortisation adds nothing over churn — falsifying the economic claim
   where it matters most.

---

## Ranked table (leverage = impact on NEG-I / M2-P1 + economics coherence, per unit cost)

| # | Idea | Addresses | Strongest parent | Novelty residue | Cost | Falsification |
|---|------|-----------|------------------|-----------------|------|---------------|
| 1 | 1.2 Ledger-supervised learned initiation | NEG-I | Bacon/Harb/Precup 2017 | I trained on amortised-return signal | Low | Ledger vs random router, frozen library |
| 2 | 3.3 Concurrent-learning memory stack | M2-P1 + NEG-I | Chowdhary CL; J.Guidance 2022 | Excitation-rank retention for P | Low | Stack vs full log vs shuffle |
| 3 | 6.3 Capital recycling | L, library saturation | Dohare et al. Nature 2024 | Conserved-capital retire+refund market | Low | Recycling vs accretion vs churn |
| 4 | 3.1 Excitation-spectrum diagnostic | NEG-I root cause | Narendra & Annaswamy 1989 | None (diagnostic) | Trivial | Full-rank enrichment retry |
| 5 | 2.2 Successor features w/ cost channel | V, DEV-CAL | Barreto 2017; Dayan 1993 | Cost as negative reward feature in w | Low | psi fixed, w-refit regime shift |
| 6 | 1.3 Affordance table | NEG-I + Psi | Khetarpal ICML 2020 | Effect-size-gated I vs null | Low | Cross-ecology I transplant |
| 7 | 4.3 Invariance I (ICP) | NEG-I, 2nd estimator | Peters 2016 | Invariant-utility (weak guarantee) | Low | Disagreement vs 1.3 under shift |
| 8 | 5.3 Ledger-weighted generative replay | Consolidation + gate | Shin NeurIPS 2017 | C-charged retention policy | Moderate | Drop low-return quartile |
| 9 | 5.2 Prioritized memory access | M2-P1 formalization | Mattar & Daw 2018 | Library instantiation only | Low | Need x chance vs factors; M1B risk |
| 10 | 4.1 Interventional logging + audit | W, P; M1B validity | Pearl 2009 | None (audit) | Trivial | Propensity-stratified M1B |
| 11 | 4.2 Value-per-charge acquisition | C, replaces support-rank | Lattimore 2016; DODO 2025 | Arm-creation pricing | Moderate | Greedy vs rank vs random, fixed C |
| 12 | 1.1 Options typing + semi-MDP backup | I, beta first-class | Sutton/Precup/Singh 1999 | Amortised-cost initiation | Low-med | Degenerate-I, fixed-beta knockouts |
| 13 | 2.1 PSR probe-vector Z | Z, Psi | Littman 2001; Boots 2010 | Priced test inventory | Low | PSR-Z vs fragment-Z router input |
| 14 | 2.3 Divergence-triggered beta | beta, Psi trust | Hafner DreamerV3 2023 | Economic admission only | Low | Corrupted-Psi fallback test |
| 15 | 5.1 Interleaved consolidation | L, rate control | McClelland 1995 | Priced consolidation filter | Moderate | Interleaving-ratio sweep flatness |
| 16 | 1.4 MAXQ marginal attribution | Ledger charge basis | Dietterich 2000; FuN 2017 | Mined priced hierarchy | Moderate | Marginal vs total credit |
| 17 | 3.2 Dual-control VOI formalization | DEV-CAL semantics | Feldbaum; Duff 2002 | Multi-target info amortisation | Docs | Withheld high-VOI acquisitions |
| 18 | 6.2 A-GEM over fragment buffer | Generator stability | Chaudhry 2019; Buzzega 2020 | Ledger-selected anchor buffer | Low | Constraint on/off |
| 19 | 6.1 EWC/SI anchors | Generator stability | Kirkpatrick 2017; Zenke 2017 | None; architecture externalizes | Skip | Pre-registered PARENT_SUFFICIENT null |

Run order: 3.1 + 4.1 first (trivial, gate everything); then the router trio
1.2 / 1.3 / 4.3 — three estimators of one object on the same logs (dynamics-gated,
invariance-gated, ledger-gradient); 3.3 as the data filter; 6.3 and 2.2 as the
economics formalizations; consolidation (5.x) once a router exists to consolidate for.

Cross-cutting honesty: after parent subtraction, Fields 1-2 mostly reduce to the OCM
economic wrapper (charged initiation, amortised value, priced tests). The two imports
whose residue EXCEEDS the wrapper: 3.3 (concurrent-learning retention as a
memory-selection law grounded in M2-P1's shuffle signature) and 6.3 (retire-and-refund
capital conservation, upgrading a per-weight heuristic into a per-unit market).

