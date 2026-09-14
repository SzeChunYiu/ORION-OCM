# GMI #602 parent-atlas amendments and hostile-proof corrections V1

Status: **NORMATIVE AMENDMENT TO `GMI_602_PARENT_ATLAS_AND_FORMAL_CLOSURE_V1.md`**  
Date: 2026-09-14.  
Rule: where this file narrows an assumption or claim in the V1 spine, **this file controls**. It adds parent-first coverage and does not raise the empirical claim ceiling.

## 0. Why this amendment exists

A second adversarial pass found two different kinds of gap:

1. important mature parent families were only implicit in the first-refusal atlas; and
2. several formal statements needed sharper boundary conditions to avoid silently proving more than their assumptions warrant.

The corrections below are deliberately conservative. They shrink claims rather than rescue them by stronger wording.

---

# 1. Parent-first additions for whole-GMI coverage

These rows are additive to §3 of the V1 spine and to the specialist `PARENT_LEDGER_V2.json`.

| GMI pressure/object | strongest parent work | parent-owned result/mechanism | exact GMI residual after subtraction |
|---|---|---|---|
| predictive/minimal dynamical state | predictive-state representations (PSRs); causal-state/computational-mechanics constructions; stochastic bisimulation and MDP state abstraction; minimal realization/Hankel-rank methods | future-prediction sufficient state, predictive rank/minimality, behavior-preserving state aggregation | obligation-specific quotient plus **resource/development** cost of realizing one sufficient state rather than another |
| statistical sufficiency / compressed representation | Fisher–Neyman sufficiency; Blackwell sufficiency; information bottleneck and rate-distortion-style representation theory | when a statistic retains all information needed for a declared inferential/decision target; information–compression tradeoffs | cross-morphology lifecycle price of a target-sufficient representation; no novelty from merely rediscovering sufficiency |
| PAC / VC / distribution-free generalization | Valiant-style learnability; Vapnik–Chervonenkis uniform convergence; Rademacher/covering-number descendants; PAC-Bayes | hypothesis-class/sample-complexity and generalization bounds under explicit distribution/loss/prior assumptions | registered ecology-to-hypothesis/representation frontier **after** those statistical assumptions are fixed |
| minimax statistical lower bounds | Le Cam two-point/multiple testing, Fano, Assouad, local asymptotic/minimax machinery | information-theoretic lower bounds on estimation/testing/sample complexity | turn a GMI obligation into a matched lower bound only after mapping it to the parent's statistical experiment |
| online learning / regret | prediction-with-expert-advice, online convex learning, adversarial/stochastic regret theory | sequential performance relative to comparator classes | developmental/resource law only if it predicts which comparator/update regime is selected under full lifecycle costs |
| multi-armed/contextual bandits | Lai–Robbins lower bounds; UCB/finite-time analyses; contextual-bandit descendants | exploration–exploitation regret lower/upper bounds under declared feedback model | no new “curiosity/exploration mechanism” unless residual remains after matched bandit parent subtraction |
| generic active learning / query complexity | membership/query learning, disagreement/query strategies, active-learning theory | label/query-complexity reductions from selective information acquisition | price the query/verifier channel jointly with compute/state; active querying itself is parent-owned |
| streaming / cell-probe / external-memory lower bounds | streaming lower bounds (e.g. frequency moments); cell-probe/data-structure lower bounds; communication reductions; I/O/external-memory models | space/query/update/I/O lower bounds for online data access and indexing | architecture-independent lifecycle phase only after the GMI task is reduced to the matched data-access problem |
| algorithmic information / universal agents | Kolmogorov–Chaitin complexity; Solomonoff prediction; Hutter AIXI; Legg–Hutter universal-intelligence measure | description-length priors, universal sequence prediction/agent ideals, simplicity-weighted environment aggregation under their definitions | no morphology/development theorem follows without computability/resource/ecology restrictions and a frozen normative reward/task measure |
| observability / controllability / system identification | classical realization theory, observability/controllability, subspace/system-ID methods | what latent dynamical state is reconstructible/control-relevant from an observation/action channel | GMI residual is the priced choice among predictive, belief, recurrent or external-memory realizations under the same obligation |

## 1.1 Consequences for #602

The following claims are now explicitly blocked unless these parents receive first refusal:

- “minimal intelligent state” -> compare Nerode **and** PSR/causal-state/bisimulation/statistical-sufficiency parents;
- “sample-efficient intelligence” -> compare VC/PAC/PAC-Bayes/minimax parents;
- “adaptive exploration” -> compare online/bandit/active-learning parents;
- “memory/retrieval lower bound” -> compare streaming/cell-probe/communication/I/O parents;
- “universal intelligence” -> compare algorithmic-information/AIXI/Legg–Hutter parents and state their incomputability/resource/normative limits;
- “dynamical latent state” -> compare realization/observability/system-identification parents.

A GMI result survives only when the matched parent theorem has been instantiated and a nonempty residual remains in morphology selection, lifecycle resource law, reachability, development, cross-domain composition, or prospectively verified transfer.

## 1.2 Anchor literature for these added rows

This is a first-refusal anchor list, not an exhaustive bibliography:

- V. N. Vapnik and A. Ya. Chervonenkis, “On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities,” *Theory of Probability and Its Applications* 16(2), 1971, DOI `10.1137/1116025`.
- M. L. Littman, R. S. Sutton and S. Singh, “Predictive Representations of State,” *NeurIPS 14*, 2001.
- R. Givan, T. Dean and M. Greig, “Equivalence notions and model minimization in Markov decision processes,” *Artificial Intelligence* 147, 2003, DOI `10.1016/S0004-3702(02)00376-4`.
- J. P. Crutchfield and K. Young, “Inferring Statistical Complexity,” *Physical Review Letters* 63, 1989, DOI `10.1103/PhysRevLett.63.105`.
- N. Alon, Y. Matias and M. Szegedy, “The Space Complexity of Approximating the Frequency Moments,” *JCSS* 58(1), 1999, DOI `10.1006/jcss.1997.1545`.
- B. Yu, “Assouad, Fano, and Le Cam,” in *Festschrift for Lucien Le Cam*, 1997, DOI `10.1007/978-1-4612-1880-7_29`.
- T. L. Lai and H. Robbins, “Asymptotically efficient adaptive allocation rules,” *Advances in Applied Mathematics* 6(1), 1985, DOI `10.1016/0196-8858(85)90002-8`.
- P. Auer, N. Cesa-Bianchi and P. Fischer, “Finite-time Analysis of the Multiarmed Bandit Problem,” *Machine Learning* 47, 2002, DOI `10.1023/A:1013689704352`.
- A. N. Kolmogorov, “Three approaches to the definition of the concept quantity of information,” *Problems of Information Transmission* 1(1), 1965.
- G. J. Chaitin, “On the Length of Programs for Computing Finite Binary Sequences,” *JACM* 13(4), 1966, DOI `10.1145/321356.321363`.
- M. Hutter, *Universal Artificial Intelligence: Sequential Decisions Based on Algorithmic Probability*, Springer, 2005, DOI `10.1007/b138233`.

---

# 2. Hostile-proof corrections to the formal spine

## C602-05 — corrected lifecycle reuse theorem boundary

T602-05's compact condition `HΔ>K` is exact only under the stated additive stationary-horizon model:

1. the retained mechanism is acquired once before the `H` counted uses;
2. per-use charged saving `Δ` is stable across those uses;
3. `K` already includes every acquisition/build/maintenance/revision charge that is not separately time-indexed;
4. there is no discounting or time-varying resource price hidden outside `w`;
5. the baseline and retained mechanisms remain obligation-equivalent for those uses.

Under time-varying savings `Δ_t` and overheads `K_t`, the exact criterion is instead

\[
\sum_{t=1}^{H}\Delta_t > \sum_t K_t.
\]

With discount factor `γ_t` fixed prospectively, compare `Σ γ_t Δ_t` against the correspondingly discounted overhead. Thus `HΔ>K` is a corollary, not the universal lifecycle law.

**Claim effect:** narrows T602-05; no empirical status changes.

## C602-13 — species relation requires identity/composition closure

Let `K` denote a **compiler-bound class**, not merely one fixed numerical cap, and assume:

- identity simulators belong to `K`;
- composition of two `K`-admissible simulators remains in `K` (or in a prospectively declared closure `K*` used consistently for the relation);
- protected capability/development preservation is transitive under composition.

Then `<=_K` is reflexive and transitive, hence a preorder. Mutual reachability

\[
M_1\equiv_K M_2 \iff M_1\le_K M_2\land M_2\le_K M_1
\]

is an equivalence relation.

If a fixed overhead cap is not composition-closed, the relation must be indexed by accumulated overhead or replaced by its explicitly declared transitive closure. A species theorem may not invoke transitivity otherwise.

**Claim effect:** supplies the missing proof/assumption boundary for T602-13.

## C602-14 — finite domain closure needs a finite admitted candidate set

The first sentence of T602-14 is replaced by the following stronger statement:

> If the **admitted candidate set is finite**, the registered world/input test set is finite, every resource/equivalence predicate used by the closure procedure is decidable on those candidates, and the registered reduction set is finite/decidable, then exhaustive registered-scope domain closure is decidable.

A common sufficient construction is:

```text
finite primitive/combinator alphabet
+ a finite maximum description length or bounded composition depth
  (or a strictly positive minimum charged construction cost under a finite construction budget)
+ finite parameter domains where parameters are enumerated by the closure claim
=> finitely many admitted candidate descriptions.
```

A finite grammar alphabet plus a resource cap **alone** is not sufficient when arbitrarily deep zero-cost/reusable syntax remains legal. Candidate-set finiteness must be proved or directly registered.

The universal negative part of T602-14 remains: unrestricted semantic domain completeness over arbitrary programs is blocked in general by standard computability/semantic-equivalence undecidability.

**Claim effect:** fixes an over-broad decidability antecedent; J's finite closure must now carry a candidate-finiteness certificate.

## C602-17b — exact transcript-cell definition for active causal identification

For admitted causal-model class `Θ` and a fixed adaptive intervention policy `π`, each terminal transcript `t` induces the consistency cell

\[
C_\pi(t)=\{\theta\in\Theta: P_\theta^\pi(T=t)>0\}.
\]

There exists an exact decoder from terminal transcript to causal target `I(θ)` **iff** `I` is constant on every reachable nonempty cell `C_π(t)`.

**Proof.** If an exact decoder exists, two models in one cell can produce the same terminal transcript and therefore must have the same decoded target. Conversely, if `I` is constant on each reachable cell, define the decoder on transcript `t` as that common value. ∎

This statement is about identifiability under the fixed policy/support. Optimizing `π` for intervention count, cost, regret or information remains active causal learning/experimental-design parent territory.

**Claim effect:** makes T602-17b's cell language exact and supplies its converse proof.

## C602-20 — extrapolation counterexample scope

T602-20's polynomial perturbation proof assumes:

- finitely many **distinct real-valued** observed inputs `x_1,...,x_n`; and
- an unrestricted candidate function class rich enough to contain `f(x)+a∏_i(x-x_i)` for nonzero `a` (or any equivalent pair of functions agreeing on the finite sample and differing outside it).

Under those conditions, finite observations do not identify a unique out-of-range law.

The theorem does **not** apply when the registered input domain is finite and all inputs have been exhaustively observed, or when a prospectively fixed function class has a uniqueness theorem from the sampled design. In those cases the relevant parent identification/generalization theorem controls.

**Claim effect:** narrows T602-20 to the unrestricted extrapolation claim it is intended to refute.

---

# 3. Gap-ledger consequences of the added parents/corrections

## B/F — capability and known-family laws

Any claimed state/sample/memory lower bound now routes through the strongest applicable member of:

```text
Nerode / communication / information
PSR / causal-state / bisimulation
VC/PAC/PAC-Bayes / minimax
streaming / cell-probe / external-memory
```

before a GMI residual is declared.

## C/E/H — learning and development

Learning-law/reachability rows must distinguish:

```text
iid generalization (PAC/VC/PAC-Bayes)
sequential comparator regret (online learning)
partial-feedback exploration (bandits)
selective label/query acquisition (active learning)
neutral grammar/search reachability (GMI-specific experimental obligation)
```

These are not interchangeable evidence classes.

## G/J/K — species, domains and unseen forms

- species quotienting uses C602-13's composition-closed compiler relation;
- finite domain closure carries C602-14 candidate-finiteness proof;
- “novel state representation” is first compared to PSR/causal-state/bisimulation/minimal-realization parents;
- “universal agent/intelligence” is first compared to algorithmic-information/AIXI/Legg–Hutter parents, including computability and normative-measure assumptions.

## M/U — statistics and extrapolation

- capability/generalization claims use the appropriate PAC/VC/PAC-Bayes/minimax parent rather than generic Hoeffding by default;
- adaptive sequential claims use online/bandit/sequential-validity theory as appropriate;
- out-of-range laws use C602-20 and a prospectively frozen model class.

---

# 4. Revised formal closure statement

After this amendment, the permissible formal terminal is:

`FORMAL_PARENT_SUBTRACTION_AND_RESIDUAL_DERIVATION_CLOSED_AT_REGISTERED_V1_SCOPE_SUBJECT_TO_HOSTILE_REVIEW`

It means only that the generic formal gaps have a theorem, parent reduction, or impossibility boundary at the registered scope. It does **not** mean the A–V empirical dependency conjunction is green.

Still forbidden:

- `ALL_RELEVANT_PARENTS_KNOWN`
- `UNIVERSAL_GMI_COMPLETE`
- `COMPLETE_GMI_EMPIRICAL_CLOSURE_AT_REGISTERED_SCOPE`

until their respective requirements are actually satisfiable and, where empirical, observed.
