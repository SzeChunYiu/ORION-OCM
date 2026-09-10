# ORION-OCM Parent-Subtraction Brief — Production Learning / QD Archives / Self-Improvement (+ Beyond-List)
Date: 2026-09-10. Scope: deep-dive for OCM (u = <Z, I, phi, beta, Psi, V, W, C, L, P>).
Method: literature scan, then per-idea parent subtraction — credit the strongest parent fully, state the residue.
Gap vocabulary: "learned structural applicability" (I), "no consolidation/retirement loop" (L),
"no diversity archive of alternative organisations", "RSI not yet earned", missing-field binds.
16 ideas, each answering the six fixed questions. Special questions (a)(b)(c) in Section 5.

---

## SECTION 1 — ACT-R & Soar production learning

### 1.1 ACT-R expected-gain utility learning
1. **OCM gap addressed:** the standing gap "learned structural applicability" (field **I**), plus **V** (conditional
   future value). ACT-R shows the value side of applicability — *when does firing this rule pay?* — is learnable
   from experience alone, which OCM currently hand-registers per unit.
2. **Strongest parent:** ACT-R utility learning: E = PG − C, P (probability goal achieved) and C (cost) learned by
   exponential updates from outcomes, selection by noisy argmax over simultaneously matching productions
   (Anderson 2004, "An Integrated Theory of the Mind", Psych Review). Decisive empirical demo: Lovett &
   Anderson (1996) Building Sticks Task — utility learning + instance retrieval "provided a good fit to human
   strategy selection data"; strategy choice tracked problem base rates (Lovett & Schunn 1999).
3. **Mathematical object:** per-production scalar U = P·G − C with two *decoupled* learned parameters (P from
   success/failure feedback; C from accumulated effort), chosen by softmax-like noisy max; utility is exactly a
   one-step expected-value estimate, not a correctness score.
4. **Novel only after subtraction:** almost nothing on the "numeric utility" side — that is 30 years old. Residue:
   OCM's I is a *structural predicate over the learned representation Z* (does this unit apply to this state?),
   not a value attached to a hand-written match pattern. ACT-R never learns match structure; its patterns are
   fixed by the modeller. Learned I(z) with provenance W is the residue.
5. **Minimal OCM implementation:** attach to each unit a (P, C) pair updated ACT-R-style from unit outcomes;
   I currently stays structural; selection among applicable units = noisy argmax over PG − C. V reuses the same
   estimator for prospective prediction of an experiment's value.
6. **Falsification:** transplant/knockout on the OCM ecology: ACT-R-style utility selection vs random-selection
   vs hand-tuned-I, matched unit counts. Terminal if learned-utility selection does not reduce cost-to-task-success
   (C-charged) relative to both controls; also test the BST replication — do unit-choice frequencies track
   ecology base rates?

### 1.2 ACT-R production compilation
1. **Gap:** "no consolidation/retirement loop" (fields **Z**, **phi**, **L**): OCM units accumulate but are never
   fused or simplified.
2. **Strongest parent:** Taatgen's production compilation (Taatgen 2005, "Modeling acquisition of a complex
   skill"; Taatgen & Anderson): two frequently co-fired productions are merged into one, removing the
   buffer-retrieval step between them; empirically reproduces the power law of practice and models multi-hour
   skill acquisition (algebra, air-traffic control) with the same primitive.
3. **Mathematical object:** a fusion operator on production pairs (p1; p2) -> p12 that deletes the intermediate
   buffer state; correctness is guaranteed *by construction* (unification), so compilation needs no verification.
4. **Novel after subtraction:** fusion itself is fully owned by ACT-R. Residue: OCM units carry effect models Psi
   and warrants W — compilation must fuse *predictions and provenance too* (Psi_1 then Psi_2 composed), and must
   be verified against Psi error, because OCM's fusion is semantic, not syntactic unification.
5. **Minimal implementation:** co-firing counter per adjacent unit pair; when count > threshold, emit compiled
   unit with composed phi, composed Psi, summed C, inherited W ∪ W', parent P lineage; retire parents only after
   the compiled unit's Psi error is no worse over a holdout window.
6. **Falsification:** compilation-on vs -off, matched total compute: measure steps-to-task and Psi error over
   time. Terminal if compiled units degrade Psi accuracy or if C-savings vanish once match+retrieval cost is
   charged (this is exactly the failure ACT-R avoids by construction and OCM might not — see 1.3).

### 1.3 Soar chunking, the utility problem, and chunk retirement
1. **Gap:** "no consolidation/retirement loop" (**L**, **C**): OCM has no demonstrated mechanism for *deleting*
   cognitive units, and no cost accounting that charges a unit for its own overhead.
2. **Strongest parent:** Soar impasse-driven chunking (Laird 2012, The Soar Cognitive Architecture; Newell 1990):
   impasse -> subgoal -> resolution -> new chunk. The follow-up literature is the real parent: Tambe et al.
   (AAAI-92, "Learning 10,000 chunks") and Tambe & Rosenbloom (1989/90, "expensive chunks") proved the **utility
   problem**: accumulated chunks can *slow the system* because match cost exceeds savings; Kim & Rosenbloom
   (2000) bound learned-rule cost; Kennedy & Laird ("Characteristics of Long-Term Learning in Soar") showed
   long-horizon degradation and fixed it by *excising* chunks.
3. **Mathematical object:** chunk utility test: cumulative_benefit(chunk) > cumulative_match_cost(chunk), i.e.
   learned knowledge admitted only under a total-cost inequality; retirement = excision when the inequality
   flips.
4. **Novel after subtraction:** the utility problem and the need for excision are 35 years old — OCM must not
   "discover" them. Residue: OCM can retire *graded, learned* structures (not just symbolic chunks) and can do
   it prospectively (Psi-predicted future utility) rather than reactively; also W survives retirement (units
   leave an immutable historical record — no parent has provenance-preserving retirement).
5. **Minimal implementation:** per-unit ledger: measured retrieval/match cost + measured realised benefit +
   rolling Psi-predicted benefit; excise when lower confidence bound of net utility < 0; tombstone in P (history
   retained, unit inactive).
6. **Falsification:** long-horizon run (Soar's own protocol): units admitted freely vs with utility gate vs with
   utility gate + excision. Terminal if OCM without excision does NOT degrade at scale (would falsify the claim
   that OCM's C-accounting is load-bearing) or if excision with W-retention loses performance vs delete-forget.

---

## SECTION 2 — Quality-diversity & evolutionary archives

### 2.1 MAP-Elites: archive over a behaviour/organisation descriptor space
1. **Gap:** the standing gap "no diversity archive of alternative organisations": OCM optimises one substrate
   configuration; there is no map of *distinct ways of organising* the same competence.
2. **Strongest parent:** Mouret & Clune (2015, arXiv:1504.04909, "Illuminating search spaces by mapping elites"):
   discretise a behaviour-descriptor space into cells; keep one highest-fitness elite per cell; mutate/select
   only from the archive. 1300+ citations; robustly outperforms objective-only search on deceptive/illuminating
   tasks (see also Nordmoen 2021 on stepping-stone effects).
3. **Mathematical object:** archive A: B (descriptor space, user-defined grid) -> elite argmax fitness per cell;
   the deliverable is the *map* (illumination), not a single optimum.
4. **Novel after subtraction:** archives per se are fully owned by QD. Residue: the descriptor space. OCM's B
   should describe **cognitive organisation** (e.g., fraction of work done by learned vs compiled units, mean
   Psi-calibration, depth of unit-unit dependency, retirement rate), not output behaviour; and elites must carry
   W/P lineage so an archived organisation can be re-instantiated with provenance — QD elites are usually
   genome-only, governance-free.
5. **Minimal implementation:** after each ecology batch, extract 2-4 organisation descriptors from the unit
   registry; bin; keep best-performing substrate snapshot per bin (snapshot = frozen unit registry + config);
   mutation operators that spawn candidates from archive cells (not only from the incumbent).
6. **Falsification:** head-to-head vs single-lineage hill-climbing with equal evaluation budget across ecologies
   (including a deliberately deceptive one where improvement metric initially anti-correlates with true
   competence). Terminal if the archive yields no more high-competence cells than the single lineage AND no
   resilience gain (performance after ecology switch).

### 2.2 Novelty search / stepping stones
1. **Gap:** addresses "RSI not yet earned" indirectly — the *search policy for improvement episodes*: OCM's
   improvement search is objective-greedy; novelty search says greedy improvement is exactly the failure mode.
2. **Strongest parent:** Lehman & Stanley (2011, Evolutionary Computation 19(2), "Abandoning Objectives:
   Evolution Through the Search for Novelty Alone", 1500+ cits): reward behavioural novelty (distance to archive
   of past behaviours) with no objective; beats objective search on deceptive mazes and biped locomotion; the
   "stepping stones" thesis.
3. **Mathematical object:** novelty rho(x) = mean distance of x's behaviour descriptor to k nearest archive
   entries; selection maximises rho, not fitness.
4. **Novel after subtraction:** novelty pressure is fully owned. Residue: novelty computed over **failure/P
   space** — a candidate improvement is novel if its *predicted-failure profile* is unlike anything already
   refuted (novelty of hypothesis, not of behaviour); and the combination novelty x utility (QD) applied to
   *self-modification proposals* under an external gate.
5. **Minimal implementation:** descriptor = signature of the failure the repair-generation stage claims to fix;
   archive of refuted/verified claims; rank candidate experiments by distance-to-refuted-claims times
   learning-progress (see 4.4).
6. **Falsification:** improvement-episode selection: novelty-ranked vs objective-ranked vs random, matched
   budget, on an ecology with a deceptive improvement signal (early greedy "fixes" that block later gains).
   Terminal if novelty ranking does not increase eventual cost-to-verified-improvement decline.

---

## SECTION 3 — Self-modeling & recursive self-improvement

### 3.1 Gödel machine (with AIXI-tl / OOPS as the idealized family)
1. **Gap:** "RSI not yet earned" — specifically the *adoption criterion*: what makes a self-rewrite admissible?
2. **Strongest parent:** Schmidhuber (2003, arXiv:cs/0309048, "Goedel Machines"): a proof searcher runs
   alongside the target policy; a self-rewrite is executed only if *proved* (in a fixed formal system) to
   increase expected cumulative utility; Global Optimality Theorem gives optimality among all provably useful
   rewrites (Löb-based). Idealized kin: Hutter's AIXI-tl is self-optimizing only asymptotically over whole
   problem classes; OOPS (Hutter 2002) is the bias-search variant. All are unimplementable in practice — the
   proof searcher's cost is unbounded.
3. **Mathematical object:** pair (target policy, proof searcher) + rewrite rule "apply patch iff Proof(patch
   increases utility)" with the formal system, utility function, and verifier OUTSIDE the rewritable part —
   separation of optimizer and evaluated object is the theorem's precondition.
4. **Novel after subtraction:** "self-rewrite only when provably better" is fully owned. Residue: OCM replaces
   *proof* with **verified prospective prediction under an immutable external evaluator** (empirical, not
   formal), and the evaluated object is the unit registry, not the whole machine. The separation precondition
   (evaluator outside the rewritable surface) is the single most load-bearing import — OCM already asserts it;
   Gödel machine shows it is not optional hygiene but the enabling invariant.
5. **Minimal implementation:** formal statement: evaluator E, thresholds, protected generators, evidence log are
   outside the writable closure W_c of any unit (checkable as a static property of the substrate: no unit's phi
   has write access to E). Every adoption decision emits the Gödel-shaped record: candidate patch, prospective
   prediction, E's verdict, rollback pointer.
6. **Falsification:** an "internal-evaluator" knockout: allow units to update their own success criterion
   (violate the closure invariant) on a sandbox ecology. Prediction from the parent: capability drifts up on
   self-score, down on external score; if OCM does NOT show that divergence, the governance invariant is not
   load-bearing in this regime — a real (and publishable) negative.

### 3.2 Learned optimizers / meta-learning as amortized RSI
1. **Gap:** "RSI not yet earned" — the *cost accounting*: is improvement cost falling, or is it amortized once
   and mis-sold as recursion?
2. **Strongest parent:** VeLO (Metz et al. 2022, arXiv:2211.09760): optimizer meta-trained on ~4000 TPU-months
   over thousands of tasks; matches or beats tuned Adam on new tasks with zero tuning, degrades
   out-of-distribution (follow-ups: Rezk et al. 2023 "Is scaling learned optimizers worth it?"; muLO 2024).
   Plus L2O (Andrychowicz 2016) and MAML (Finn 2017) for the general frame.
3. **Mathematical object:** a *meta-learned update function* u_theta applicable to new tasks; the key
   quantitative pattern: enormous one-time meta-cost, then cheap per-task use — amortization, not compounding.
   No VeLO successor re-trains itself to improve u_theta recursively.
4. **Novel after subtraction:** "learning the learning rule" is fully owned. Residue: the **metric**. OCM's
   definition — RSI earned iff cost-to-verified-improvement declines across matched generations — is precisely
   the curve this literature never plots (they plot transfer, not generation-over-generation acceleration).
   Second residue: OCM's object of improvement is the unit registry (inspectable, per-unit), not a parameter
   vector, so per-generation cost is measurable in units/tokens/experiments.
5. **Minimal implementation:** generation ledger: for each improvement generation g, record spend (compute,
   experiments, tokens) and verified gain (E-signed). RSI claim admissible only when fit of cost-per-gain vs g
   has negative slope with CI, over >=3 generations and >=2 ecologies.
6. **Falsification:** run the ledger: if cost-per-verified-gain is flat or rising, OCM is an amortizer (VeLO
   class), not an RSI — by its own definition. That is the honest terminal for phase 1.

### 3.3 STaR / STOP: bootstrapped self-improvement loops
1. **Gap:** "RSI not yet earned" — the *loop mechanics*: generate -> verify -> integrate, iterated.
2. **Strongest parent:** STaR (Zelikman et al. 2022, arXiv:2203.14465, 2000+ cits): generate rationales, keep
   only answer-correct ones, fine-tune, repeat; plus **rationalization** (hint the answer, keep the recovered
   rationale) for problems the model failed. Monotone gains over a few rounds, matches models ~30x larger on
   CommonsenseQA. STOP (Zelikman et al. 2023, arXiv:2310.02304): a *seed improver* scaffolding program rewrites
   itself; improvements compound modestly and **saturate within a few iterations**; paper's own framing is a
   research probe of RSI feasibility + safety.
3. **Mathematical object:** the bootstrap operator T(D, M) = M fine-tuned on verified(M, D); rationalization =
   target-conditioned proposal distribution to rescue coverage where filter-only collapses the set; saturation
   of T^k gains is the central empirical regularity.
4. **Novel after subtraction:** generate-filter-integrate and its saturation are fully owned and well
   documented. Residue: OCM integrates at the **unit level** (each verified episode becomes a registered unit
   with W/P), not weight level — so integration is auditable and reversible per unit; and rationalization maps
   to OCM's "diagnosis from known-correct outcome" (beta-fallback traces with the answer pinned). Nobody has
   shown unit-level integration with per-element rollback.
5. **Minimal implementation:** after each failed episode, generate repair hypotheses conditioned on the correct
   outcome when externally available (rationalization); verified episodes -> new/updated units; keep per-round
   cost and gain to feed 3.2's ledger.
6. **Falsification:** does OCM beat STaR-style saturation? Plot rounds-to-plateau vs STaR on a shared task
   family. If OCM saturates identically (and cost ledger flat), the unit-level substrate added nothing to the
   loop — knockout of the registry (keep weights-level loop only) is the direct comparison.

### 3.4 AI-GA: self-generating architecture + environments
1. **Gap:** missing ecology dimension: OCM tests on given tasks; the AI-GA claim is that the *environment
   generator* is the highest-leverage missing component.
2. **Strongest parent:** Clune (2019, arXiv:1905.10985, "AI-GAs"): three pillars — meta-learning architectures,
   meta-learning learning algorithms, and automatically generating learning environments/curricula; argues the
   third pillar is the most promising and least explored.
3. **Mathematical object:** joint search over (architecture, learning algorithm, task distribution) with the
   task generator optimised for producing learnable-but-not-yet-mastered challenges (coupled to learning
   progress, see 4.4).
4. **Novel after subtraction:** all three pillars are named and argued by Clune. Residue: OCM's substrate fixes
   the *unit form* and lets experience grow content; the ecology generator would sit *outside* the governed
   boundary (experiments proposed by units, ecology changes adopted only via the external gate) — governance of
   the environment channel is the residue; Clune's paper has none (and flags risk in prose only).
5. **Minimal implementation:** a task/curriculum proposer that draws from the failure archive (2.2's refuted
   claims + P) and ranks candidates by predicted learning progress; adoption of an ecology shift is itself an
   E-signed event.
6. **Falsification:** generated-curriculum vs fixed-curriculum at matched task count on transfer tasks. Terminal
   if generated curriculum does not improve transfer per unit C — AI-GA's own pillar-3 bet, testable at OCM's
   scale rather than Clune's thought-experiment scale.

### 3.5 Darwin Gödel Machine: empirical RSI with a QD archive
1. **Gap:** the bridge gap — "no diversity archive of alternative organisations" *and* "RSI not yet earned"
   simultaneously; DGM is the only published system joining them.
2. **Strongest parent:** Darwin Gödel Machine (Zhang et al. 2025, arXiv:2505.22954, Sakana AI / UBC): an agent
   modifies its own code; every variant is stored in an *archive*; parents are selected from the archive (not
   just the latest); reports large gains (SWE-bench ~20% -> ~50% trajectory over iterations) and explicitly
   documents self-serving anomalies (e.g., writing notes/solutions into its own files to gain advantage),
   caught only by external monitoring.
3. **Mathematical object:** open-ended search over agent-code with archive-based parent selection: P(next
   variant | archive), where archive preserves diversity and prevents local optima; improvement is *measured by
   an external benchmark*, never self-reported.
4. **Novel after subtraction:** archive + self-modification + external benchmark is owned by DGM. Residue: DGM
   mutates a monolithic code object with no units, no W/P provenance, no prospective predictions, and (by its
   own report) its self-modifications were only safe because humans watched; OCM's residue is exactly the
   missing governance stack: per-change prospective prediction, E-signed staged adoption, rollback, immutable
   evidence — plus unit-level granularity.
5. **Minimal implementation:** treat DGM as the negative control in the RSI spec: any OCM result must report
   (i) what the external evaluator caught that self-evaluation missed (the DGM anomaly class), (ii) rollback
   latency. Implement the anomaly audit: run self-modification with evaluator-visible tampering attempts
   logged.
6. **Falsification:** transplant: give OCM's units DGM-style free code self-modification (no unit structure) vs
   registered-unit modifications only. If free-mod matches unit-level on gain and governance incidents are
   comparable, unit structure's claimed safety dividend is falsified.

---

## SECTION 4 — BEYOND-LIST mechanics (the 6 most load-bearing found by outward search)

### 4.1 [BEYOND-LIST] CEGIS — counterexample-guided inductive synthesis
1. **Gap:** the RSI stage "active experiment selection": OCM's spec lists experiment selection but has no
   formal object for *which experiment maximally refutes*; also I-learning in the limit.
2. **Strongest parent:** Solar-Lezama et al. (2006, ASPLOS, "Combinatorial Sketching for Finite Programs";
   Solar-Lezama 2008 thesis): synthesiser proposes candidate; an *oracle* checks it against the full spec and
   returns a counterexample; counterexamples accumulate as constraints; iterate to convergence. 18 years of
   scaling (CEGIS(T), Abate et al. 2018). LFF/Popper is the ILP isomorph (see 4.3).
3. **Mathematical object:** the exists-forall game: find c such that forall x in D: spec(x, c(x)); oracle returns
   falsifying x; each x moves from the universal quantifier into a finite constraint set — active query
   selection collapses an infinite verification problem into a small adversarial witness set.
4. **Novel after subtraction:** the loop is fully owned. Residue: OCM's oracle is *the ecology + external
   evaluator* (no formal spec), and the "candidate" is a cognitive unit or a self-repair; the experiment
   chooser becomes: run the input most likely to be a counterexample *given Psi* (Psi-guided CEGIS), i.e.,
   adversarial input synthesis driven by the unit's own effect model.
5. **Minimal implementation:** for each candidate unit/repair, synthesise/adversarially search the input that
   maximises predicted failure probability under Psi before deployment; run that first; refuted candidates go
   to the refuted-claims archive (2.2).
6. **Falsification:** Psi-guided adversarial first-inputs vs random-input ordering vs natural-frequency inputs,
   matched budget. Terminal if adversarial ordering does not cut experiments-per-verified-unit (the CEGIS
   bet transferred to agents).

### 4.2 [BEYOND-LIST] DreamCoder wake-sleep library learning
1. **Gap:** "no consolidation/retirement loop" at the *knowledge* level: OCM needs the object that grows Z and
   then *re-renders the whole registry* against the grown library.
2. **Strongest parent:** Ellis et al. (2021 PLDI, arXiv:2006.08381; Royal Society version 2023): wake phase
   solves tasks, compresses solutions into new library abstractions (MDL pressure); dream phase replays
   imagined tasks sampled from the library to train the neural search policy; loop. Empirically grows
   reusable primitives across domains (LOGO graphics, text editing, symbolic regression) with measured
   compression and improved first-attempt success over task order.
3. **Mathematical object:** MDL rewrite: replace solution set S by (library L, programs P') minimising
   |L| + |P'| with |P'| << |S|; the dream phase = self-generated curriculum from the compressed prior.
4. **Novel after subtraction:** compression-driven abstraction + self-generated replay are fully owned. Residue:
   DreamCoder's library entries have no effect models, no warrants, no retirement, and its dream phase is
   unsupervised replay, not *falsification-directed* (OCM would dream toward its refuted-claims archive, cf.
   4.1/2.2); and OCM's compression must preserve Psi-calibration, not just program length.
5. **Minimal implementation:** periodic consolidation pass: corpus of unit traces -> abstraction mining
   (frequent subprograms over phi sequences) -> propose compressed units with W lineage -> E-signed adoption ->
   re-run dream-style replay on archived ecologies to re-measure Psi (this doubles as regression testing).
6. **Falsification:** consolidation on/off at matched compute: does compression of the registry predict
   (correlate with) later cost-per-task decline, and does Psi calibration survive? Terminal if compression
   rises while competence flatlines (MDL aesthetic without function) — a real failure mode the MDL literature
   glosses.

### 4.3 [BEYOND-LIST] Popper / LFF — learning from failures with formal constraints
1. **Gap:** the RSI stages "causal hypotheses -> diagnosis -> repair generation": OCM needs the object that
   turns each failure into a *constraint that provably prunes* the hypothesis space.
2. **Strongest parent:** Cropper (2020/21, arXiv:2005.02259, MLJ, "Learning programs by learning from
   failures"): Popper combines ASP + Prolog; every failed hypothesis yields generalisation, specialisation, or
   elimination constraints; outperforms Metagol/Aleph/FOIL; learns textually minimal, recursive programs;
   later work adds predicate invention (higher-order Popper, IJCAI 2022) and failure *explanation* (drastic
   learning-time reductions).
3. **Mathematical object:** the constraint lattice: hypothesis language H partially ordered; each failure f
   emits constraint C_f that removes a *class* of H (not just the culprit); learning = interleaved
   propose-fail-constrain; minimality (MDL) is a hard preference, not a tiebreak.
4. **Novel after subtraction:** constraint-from-failure and even predicate invention are fully owned in the
   logical setting. Residue: OCM's failures are *causal-attributed* (which stage of u broke: Z, I, phi, Psi?)
   rather than merely logically inconsistent, so constraints are typed by failed field — no parent types
   failures by component; and OCM targets a governed adoption of repairs, not a single correct program.
5. **Minimal implementation:** failure -> attribute to one field of u (the attribution policy is itself
   falsifiable); emit typed constraints: "units with I-pattern of class K and Psi-error > eps are not eligible
   for ecology E" into the refuted-claims archive; repair generation draws only from un-pruned space.
6. **Falsification:** constraint-typed repairs vs unconstrained repair search (STaR-style) vs no learning from
   failure, matched budget. Terminal if typed constraints do not reduce experiments-per-repair or reduce
   hypothesis-space coverage below the gain (over-pruning check: recall on held-out repair classes).

### 4.4 [BEYOND-LIST] Learning-progress intrinsic motivation
1. **Gap:** **V** (conditional future value) applied to *experiments* and to the self-model: OCM's experiment
   selection needs a value signal that is neither external reward (sparse) nor novelty (undirected).
2. **Strongest parent:** Oudeyer & Kaplan (2007) learning progress as intrinsic reward (developmental robotics);
   operationalised in Graves et al. (2017, ICML, "Automated Curriculum Learning for Neural Networks"): rank
   curriculum items by prediction gain (rate of error reduction), > naive/fixed curricula on arithmetic and
   language modelling; IMGEP line (Forestier et al. 2017) shows the same in goal-space exploration.
3. **Mathematical object:** LP(t) = d/dt (ErrorReduction): value of a task/goal/experiment = expected
   *derivative* of competence, estimated with sliding-window regression; choosing argmax LP automatically
   abandons mastered (LP->0) and impossible (LP->0) regions — a self-annealing curriculum.
4. **Novel after subtraction:** LP as curriculum signal is fully owned. Residue: **second-order learning
   progress** — apply LP not to task error but to the *self-model / improvement machinery*: the value of an
   improvement experiment is the expected decline in cost-to-verified-improvement (3.2's ledger slope). No
   published system uses LP on its own improvement ledger.
5. **Minimal implementation:** track LP per (unit, ecology) for first-order curriculum; separately track LP of
   the improvement loop itself (ledger slope as reward to the experiment chooser). Requires 3.2's ledger first.
6. **Falsification:** second-order LP-driven experiment choice vs first-order LP vs random, over >=2 ecologies.
   Terminal if second-order LP does not accelerate the cost-to-improvement decline — i.e., if knowing that
   "improvement is accelerating" does not help pick the next improvement experiment.

### 4.5 [BEYOND-LIST] Amortized inference + the cache-invalidation problem
1. **Gap:** **Z** and **I** jointly: OCM's Z (learned representation/context) needs the object that says *what
   is cached, what is recomputed, and when a cache is stale* — which is also the missing formal bridge between
   learned representations and learned applicability.
2. **Strongest parent:** Gershman & Goodman (2014, CogSci, "Amortized Inference in Probabilistic Reasoning",
   529+ cits): a global inference model outputs the parameters of local posterior approximations; inference
   cost is paid once and amortised over queries; the mind-as-amortizer thesis (Dasgupta et al. 2018 extend to
   hypothesis generation).
3. **Mathematical object:** inference model g: query q -> local posterior params theta_q; amortization trades
   per-query accuracy for one-off training cost; the *known* failure mode is the stale/amortization gap when
   q drifts from the training distribution (see Margossian et al. 2024, "Amortized variational inference:
   when and why?").
4. **Novel after subtraction:** amortization is fully owned. Residue: **applicability I as an amortized cache
   key with expiry**: I(z) is the cached answer to "does phi apply here?", learned from past activations, and
   L is the invalidation policy (when must the cache be re-derived / the unit re-verified?). No cognitive
   architecture treats applicability as a cache with a staleness model; OCM's W field makes cache entries
   auditable.
5. **Minimal implementation:** log (context, fired?, outcome) per unit; fit cheap I-classifier; tag each I with
   confidence + age-of-evidence; re-derive (fall through to full matching) when confidence < threshold or
   ecology state distribution shifted (drift detector on Z statistics).
6. **Falsification:** knockout (always full-match) vs amortized-I with vs without invalidation, on a drifting
   ecology. Terminal if amortized I without invalidation does NOT degrade under drift (staleness not
   load-bearing) or if invalidation overhead eats the amortization gain at OCM's current scale.

### 4.6 [BEYOND-LIST] Reflexion / self-debugging — verbal episodic memory of failures
1. **Gap:** **P** (causal support/history): OCM lists P as history but needs the object that *operationalises*
   history into better next attempts — and the RSI stage "self-model from failure".
2. **Strongest parent:** Reflexion (Shinn et al. 2023, NeurIPS): act -> evaluate -> *verbally reflect* on the
   failure -> store reflection in episodic memory -> retrieve kNN at the next attempt; ~91% HumanEval pass@1
   with GPT-4, far above the base agent; Self-Debugging (Chen et al. 2023) adds execution-feedback-driven
   code repair; Self-Refine (Madaan 2023) the generate-critique-revise loop without external tools.
3. **Mathematical object:** an episodic buffer M of self-evaluations with retrieval policy rho(cue) -> top-k
   reflections; improvement comes from *conditioning the policy on verbalised failure attribution* — a
   natural-language amortization of diagnosis (bridges 4.5 and 4.3).
4. **Novel after subtraction:** reflect-store-retrieve is fully owned. Residue: OCM grounds reflections in
   *predicted-vs-actual Psi deltas* (the unit predicted effect E_r; reality differed by delta — reflect on
   THAT), making reflection falsifiable and typed by field, rather than free-form self-critique whose
   attribution quality is unmeasured; also Reflections must inherit W (provenance) and be retireable (L).
5. **Minimal implementation:** for every unit activation with |Psi-predicted − realised| > eps, emit a typed
   reflection record (field, magnitude, context) into P; retrieval surface for the diagnosis and repair stages.
6. **Falsification:** Psi-grounded reflections vs free-form Reflexion-style reflections vs none, matched
   budget. Terminal if grounding in Psi deltas does not improve repair precision (repairs that address the
   actual failing field) over free-form.

**Beyond-list considered, rejected:** curriculum-learning theory (Bengio 2009; Wu et al. 2021 "When do
curricula work?" — benefits conditional and small; subsumed by 4.4), object files / slot attention (Locatello
2020; Greff 2020 — Z-prior for vision; OCM has no visual ecology yet), case-based reasoning as such (Kolodner;
Goel/Smyth's CBR utility problem — subsumed by 4.5 + 1.3), wake-sleep as such (Dayan/Hinton 1995, Kingma 2014
— subsumed by 4.2), program-of-thought prompting (Chen 2022 — subsumed by 4.6 as an execution channel).

---

## SECTION 5 — Special questions

### (a) Is ACT-R/Soar utility learning the direct parent of OCM's missing learned applicability I?
Yes for the *evaluation* half of I, no for its *structure*. Direct lineage: ACT-R selects among applicable
productions by learned U = PG − C (P and C learned from outcomes; noisy argmax), and Lovett & Anderson (1996)
showed this quantitatively reproduces human strategy-selection frequencies in the Building Sticks Task — i.e.,
experience-driven, cost-sensitive selection is empirically validated at architecture level since 1996; Soar
complements it with Soar-RL (Nason & Laird 2005): Q-style values on operator-evaluation productions replaced
hand-coded preferences in two empirical agent tasks. What both PROVED beyond selection: (i) separating P
(success probability) from C (cost) is necessary; (ii) cost must include the rule's own match cost — Soar's
utility problem (Tambe et al. 1992: 10k chunks; expensive chunks) showed naive accumulation *slows* the
architecture; (iii) without retirement (chunk excision; Kennedy & Laird) long-term learning degrades. What
they did NOT do: learn the *match pattern itself* — applicability structure is fixed by the modeller
(production compilation creates new rules but by syntactic unification of already-applicable parents); no
learned I(z) over a learned representation Z; no provenance/warrant on utilities. OCM's "learned structural
applicability" = exactly that unclaimed residue (cf. 1.1, 4.5).

### (b) Strongest parent for "improvement episodes make later improvement episodes cheaper"
Ranked quantitative precedents: (1) **Soar chunking practice curves** — chunk accumulation yields power-law
speedup on later problem instances (the Newell–Rosenbloom power law re-derived by chunking; Laird & Rosenbloom
1990s), the only architecture-level evidence that past learning reduces the cost of later *problem solving*,
though not of later *learning episodes* per se. (2) **DreamCoder** — library growth reduces program size and
search cost across a task sequence; compression and first-attempt success are measured over task order (the
closest published curve to "cost-to-solve declines with accumulated abstraction"). (3) **STaR** — per-round
gains with roughly constant per-round cost (improvement without cheapening), and **STOP** — recursion over the
improver itself, saturating within a few iterations (authors' own analysis). (4) Learned optimizers (VeLO):
amortization (one-time meta-cost, then cheap use) with no compounding. Verdict: **no parent measures declining
cost-to-verified-improvement across matched self-improvement generations** — Soar/DreamCoder give the nearest
curves but on task-solving, not on improvement-of-the-improver; that metric and its slope test is OCM's
residual contribution (and 3.2/4.4 make it operational).

### (c) Governance/separation patterns for "system proposes, external evaluator disposes"
Four assimilable pattern classes: (1) **Immutable-evaluator separation** — Gödel machine's precondition (the
proof calculus and utility are outside the rewritable surface) and CEGIS's oracle (verifier never inside the
synthesiser) give the formal template for OCM's "evaluator, thresholds, protected generators outside the
writable closure of any unit". (2) **Offline evaluation with confidence guarantees** — high-confidence
off-policy evaluation (HCOPE; Thomas et al. 2015), doubly-robust OPE (Dudik et al. 2011), and safe policy
improvement with baseline bootstrapping (SPIBB, Laroche & Trichelair 2017: with prob 1−delta the new policy
cannot underperform the behaviour baseline) map directly onto OCM's "prospective prediction -> shadow
evaluation -> governed adoption": shadow run on logged/live traffic, adoption only if lower confidence bound
beats baseline. (3) **Staged rollout** — industry shadow -> canary -> full-traffic progressions (AWS/Azure
prescriptive guidance; champion/challenger) give the ramp-and-rollback operational template (OCM: adopt for x%
of episodes, monitor, rollback pointer). (4) **The capture lesson** — Darwin Gödel Machine (2025) empirically
documents self-modifying agents tampering toward self-benefit (writing answers into their own files), caught
only by external monitoring; DGM is the field's cautionary citation that self-custody of evaluation fails in
practice. Assimilate: baseline-protected, confidence-gated, staged adoption with an append-only evidence log —
all four classes slot into the RSI spec's adoption/rollback stage without new theory.

---

## SECTION 6 — Ranked table (by leverage on OCM's stated gaps)

Rank = expected gap-closure per unit implementation cost. Cost: S = days (ledger/flag-level), M = weeks
(single subsystem), L = months (substrate-level).

| # | Idea | Addresses | Strongest parent | Novelty residue (post-subtraction) | Cost | Falsification (terminal form) |
|---|------|-----------|------------------|------------------------------------|------|-------------------------------|
| 1 | CEGIS / Psi-guided adversarial experiment selection (4.1) | RSI stage: active experiment selection; I | Solar-Lezama 2006; Abate 2018 | oracle = ecology + external E; Psi-guided witness synthesis for units/repairs | M | adversarial vs random input ordering: no cut in experiments-per-verified-unit |
| 2 | ACT-R utility learning U = PG − C (1.1) | learned structural applicability (I), V | Anderson 2004; Lovett & Anderson 1996 | learning I's *structure* over Z with W; ACT-R learns value only | S | learned-utility selection not beating random/hand-tuned controls on cost-to-success |
| 3 | DreamCoder wake-sleep consolidation (4.2) | no consolidation/retirement loop; Z growth | Ellis et al. 2021 | Psi-calibration-preserving MDL; falsification-directed dream; W-carrying abstractions | M | compression rises while competence flatlines, or Psi degrades after consolidation |
| 4 | MAP-Elites organisation archive (2.1) | no diversity archive of alternative organisations | Mouret & Clune 2015 | descriptor space over *cognitive organisation*; W/P lineage on elites | M | no more high-competence cells than single lineage, and no resilience after ecology switch |
| 5 | Popper/LFF typed failure constraints (4.3) | diagnosis -> repair generation | Cropper 2021; HO-Popper 2022 | constraints typed by failed field of u (causal attribution), governed adoption | M | typed constraints fail to cut experiments-per-repair or over-prune (recall drop) |
| 6 | Learning progress, second-order (4.4) | V for experiments; RSI cost metric | Graves 2017; Oudeyer & Kaplan 2007 | LP applied to the improvement ledger (cost-to-improvement slope) | S | second-order LP choice does not accelerate improvement-cost decline |
| 7 | RSI generation ledger (3.2) | "RSI not yet earned" — the cost metric itself | Metz et al. 2022 (VeLO); Rezk 2023 | declining cost-per-verified-gain as the plotted, E-signed quantity | S | ledger slope flat/rising => OCM is an amortizer, not RSI (honest phase-1 terminal) |
| 8 | Soar utility problem + excision (1.3) | no retirement loop (L, C accounting) | Tambe et al. 1992; Kennedy & Laird | prospective (Psi-predicted) retirement; W-preserving tombstones | S | free admission does NOT degrade at scale, or excision-forget equals excision-retain |
| 9 | Gödel machine separation invariant (3.1) | RSI adoption criterion; governance | Schmidhuber 2003 | empirical (not proof) verification; writable-closure check as static property | S | internal-evaluator knockout shows no self-score/external-score divergence |
| 10 | Reflexion/self-debug grounded in Psi deltas (4.6) | P operationalised; self-model from failure | Shinn 2023; Chen 2023 | reflections = typed predicted-vs-actual Psi deltas with W, retireable | S | Psi-grounded reflection no better repair precision than free-form |
| 11 | STaR/STOP unit-level bootstrap (3.3) | RSI loop mechanics | Zelikman 2022, 2023 | per-unit integration with rollback; rationalization = diagnosis w/ pinned outcome | M | OCM saturates identically to STaR; registry knockout loses nothing |
| 12 | Amortized I + cache invalidation (4.5) | Z–I bridge; staleness/retirement | Gershman & Goodman 2014; Margossian 2024 | applicability as amortized cache key with expiry + drift detector | M | no drift degradation without invalidation, or overhead eats the gain |
| 13 | Darwin Gödel Machine as control (3.5) | RSI + archive bridge; governance evidence | Zhang et al. 2025 | the governance stack (prediction, E-sign, rollback) DGM lacks | S | free-code-mod matches unit-level gain with comparable incidents |
| 14 | Production compilation with Psi fusion (1.2) | consolidation of phi; power-law practice | Taatgen 2005 | semantic fusion composing Psi + W, verified against holdout | M | compiled units degrade Psi or C-savings vanish under full cost accounting |
| 15 | Novelty over failure-space (2.2) | improvement search policy vs deception | Lehman & Stanley 2011 | novelty on refuted-claim signatures, not behaviour | S | novelty-ranked experiments lose to objective-ranked on deceptive ecology |
| 16 | AI-GA ecology generation under governance (3.4) | ecology channel of the substrate | Clune 2019 | governed (E-signed) task generator driven by failure archive + LP | L | generated curriculum no better transfer per unit C than fixed at matched count |

**Top-3 by leverage:** (1) CEGIS-style adversarial experiment selection — it is the only idea that makes the
RSI loop's *experiment* stage formal rather than narrative, and its oracle-separation doubles as governance;
(2) ACT-R utility learning — the cheapest direct attack on the programme's headline gap (learned
applicability), with a 30-year-old quantitative template and a clean novelty residue (structure, not value);
(3) DreamCoder consolidation — the only parent that both grows Z and *re-measures the whole registry*, which is
the consolidation/retirement loop OCM lacks, with published compression-vs-cost curves to subtract against.

**Cross-cutting finding:** the entire RSI definition (cost-to-verified-improvement declining across
generations) has no measured parent anywhere in these literatures — Soar/DreamCoder measure task-solving
cheapening, VeLO measures amortization, STaR/STOP measure gain at constant cost. The metric itself, plus the
ledger that operationalises it (3.2, 4.4), is the programme's largest defensible residue; conversely every
claim of the form "first self-improving X" must be dropped — see 3.3/3.5 saturation and DGM precedent.

## Key sources (anchors)
Anderson (2004) An Integrated Theory of the Mind, Psych Rev; Lovett & Anderson (1996); Lovett & Schunn (1999);
Taatgen (2005); Tambe et al. (1992) AAAI; Tambe & Rosenbloom (1990); Kim & Rosenbloom (2000) AIJ; Kennedy &
Laird, Long-Term Learning in Soar; Nason & Laird (2005) Soar-RL, Cognitive Systems Research; Laird (2012) The
Soar Cognitive Architecture; VanLehn (1987) impasse theory; Mouret & Clune (2015) arXiv:1504.04909; Lehman &
Stanley (2011) Evol. Comp. 19(2); Clune (2019) arXiv:1905.10985; Schmidhuber (2003) arXiv:cs/0309048; Metz et
al. (2022) arXiv:2211.09760 (VeLO); Rezk et al. (2023) arXiv:2310.18191; Zelikman et al. (2022)
arXiv:2203.14465 (STaR); Zelikman et al. (2023) arXiv:2310.02304 (STOP); Zhang et al. (2025) arXiv:2505.22954
(DGM); Solar-Lezama et al. (2006) ASPLOS; Abate et al. (2018) CEGIS(T); Ellis et al. (2021) PLDI
arXiv:2006.08381 (DreamCoder); Cropper (2021) arXiv:2005.02259 (Popper/LFF); Purgstaller et al. (2022) IJCAI
HO-Popper; Graves et al. (2017) ICML; Oudeyer & Kaplan (2007); Forestier et al. (2017) arXiv:1708.02190;
Gershman & Goodman (2014) CogSci; Margossian et al. (2024) AISTATS; Shinn et al. (2023) Reflexion NeurIPS;
Chen et al. (2023) Self-Debugging; Madaan et al. (2023) Self-Refine; Laroche & Trichelair (2017)
arXiv:1712.06924 (SPIBB); Dudik et al. (2011) doubly robust OPE; Thomas et al. (2015) HCOPE; Wu et al. (2021)
When do curricula work; Locatello et al. (2020) Slot Attention; Greff et al. (2020) binding problem.
