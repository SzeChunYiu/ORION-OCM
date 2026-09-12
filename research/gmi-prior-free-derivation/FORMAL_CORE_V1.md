# A measure-free, architecture-neutral core for general machine intelligence

## Formal core v1 — OCM consolidation

### Abstract

The target is not to derive a privileged implementation name from logic. The target is to derive representation-invariant constraints on intelligent machines from a minimal declared problem: a causal interaction domain, a cognitive obligation, an admissible ecology, a machine boundary, and physical/resource variables. No probability measure over the ecology and no named architecture family is required by the core construction.

The formalism separates predictive state, control state, physical morphology, and developmental reachability. This separation is necessary. A representation can be predictively minimal without being control-minimal; a behavior can be nondominated without identifying a unique implementation; a physically optimal morphology can be unreachable under a given search process.

The main closure criterion is a bidirectional sandwich. Necessity theorems produce an outer set containing every physically realizable morphology; explicit constructions produce an inner set. If a constructive antichain dominates the entire necessary outer profile region, then the true physical Pareto-profile frontier is certified there. Exact morphology additionally requires a fiber-identification theorem.

---

# 1. Declarations

Let \(\mathcal A\) and \(\mathcal O\) be action and observation spaces and

\[
h_t=(o_0,a_0,o_1,a_1,\ldots,o_t)
\]

a finite interaction history. An environment \(e\) is a causal kernel family

\[
e_t(do_{t+1}\mid h_t,a_t).
\]

The admissible ecology is a nonempty set \(\mathcal E\) of such environments. No probability measure on \(\mathcal E\) is assumed.

A problem declares a machine boundary

\[
\mathfrak B=(\mathcal B_{\rm in},\mathcal B_{\rm out},\mathcal S_{\rm free}).
\]

A clock, retrieval store, plan table, external agent, random seed, tool, or environment label is not free unless declared in \(\mathcal S_{\rm free}\). Moving information across the boundary changes the resource problem.

A cognitive obligation \(\Omega\) determines which future outcomes matter. For quantitative control write

\[
\ell_\Omega(h,e,\kappa;s)\in[0,\infty]
\]

for the loss after root history \(h\), structural environment \(e\), rooted continuation \(\kappa\), and free side information \(s\). Define robust loss

\[
L_\Omega(h,\kappa;s)=\sup_{e\in\mathcal E}\ell_\Omega(h,e,\kappa;s).
\]

Expected loss inside one stochastic environment is permitted. What is absent is a probability law selecting environments from \(\mathcal E\).

The declaration basis is therefore:

- D0: causal interaction domain and system boundary;
- D1: cognitive obligation \(\Omega\);
- D2: admissible ecology \(\mathcal E\);
- D3: physical/resource model \((\Theta,\rho)\) for morphology claims;
- D4: operational probe resolution \(\mathcal Q\);
- D5: development process \((D,B)\) for developmental claims.

Probability priors over environments, neural units, attention, symbolic rules, gradient descent, KSO, program search, and all named architecture families are absent from this basis.

---

# 2. Rooted continuation semantics

After a root history, re-index future time from zero. A rooted suffix before local action \(k\) is \(\sigma_k\), containing only post-root actions and observations. A rooted continuation strategy has the form

\[
\kappa_k(da_k^+\mid \sigma_k,s).
\]

The forgotten pre-root history is not an argument. This prefix-blindness condition is essential: otherwise a nominally common continuation can secretly branch on the very history identity that a compression theorem claims to discard.

Let

\[
\mathsf Q_h(e,\kappa,s)
\]

denote the complete obligation-relevant future response of history \(h\) under \((e,\kappa,s)\).

---

# 3. Canonical predictive residual

Define

\[
h\equiv_{\rm pred}h'
\iff
\mathsf Q_h=\mathsf Q_{h'}.
\]

Let

\[
S_{\rm pred}=\mathcal H/\!\equiv_{\rm pred}.
\]

A deterministic statistic \(\phi:\mathcal H\to Z\) is response-sufficient if the full response profile can be reconstructed from \(\phi(h)\).

## Theorem 3.1 — coarsest exact predictive statistic

Every deterministic response-sufficient statistic refines the predictive quotient. Equivalently, on reachable codes there is a map \(r\) such that

\[
q_{\rm pred}=r\circ\phi.
\]

### Proof

If \(\phi(h)=\phi(h')\), response sufficiency forces identical reconstructed response profiles for all admitted \((e,\kappa,s)\). Hence \(h\equiv_{\rm pred}h'\). Therefore every fiber of \(\phi\) lies inside one predictive-equivalence class. \(\square\)

Thus a canonical predictive state exists up to reachable-state relabeling. It is not a neuron, token, symbolic rule, KSO, or parameter tensor. It is an obligation-relative future-response distinction.

This theorem does **not** imply that every successful controller must preserve every predictive distinction.

---

# 4. Control compatibility is a different problem

For tolerance \(\varepsilon\), define the feasible rooted plans

\[
\Gamma^{\rm plan}_\varepsilon(h;s)
=
\{\kappa:L_\Omega(h,\kappa;s)\le\varepsilon\}.
\]

A set \(B\) of histories is plan-compatible when

\[
\bigcap_{h\in B}\Gamma^{\rm plan}_\varepsilon(h;s)\ne\varnothing.
\]

Compatibility need not be transitive. For instance

\[
\Gamma(h_1)=\{a,b\},\quad
\Gamma(h_2)=\{b,c\},\quad
\Gamma(h_3)=\{a,c\}
\]

are pairwise compatible but not jointly compatible. General control therefore need not admit a unique coarsest quotient. The canonical object is the feasibility/conflict structure; a controller is one realization of it.

---

# 5. Three deterministic control complexities

Assume a finite Markov residual specification \(V\), finite action alphabet, and deterministic controller class.

Let \(A_\varepsilon(v)\) be the admissible current actions at residual state \(v\).

### 5.1 Repeated action disclosure

A block is action-compatible if

\[
\bigcap_{v\in B}A_\varepsilon(v)\ne\varnothing.
\]

Let \(\chi^{\rm det}_{\rm act}(\varepsilon)\) be the chromatic number of the resulting conflict hypergraph. It is the minimum message alphabet when an external encoder may inspect the true residual state again at every step and only needs to identify a valid current action.

### 5.2 One-time plan selection

Let \(\chi^{\rm det}_{\rm plan}(\varepsilon;s)\) be the chromatic number of deterministic rooted-plan conflict. It is the minimum root-label alphabet when a one-time encoder selects a complete deterministic rooted plan. Decoder-side memory needed to execute that plan is not charged by the label count.

### 5.3 Autonomous dynamic state

Let \(N^{*,\rm det}_{\rm dyn}(\varepsilon)\) be the minimum reachable internal-state count of a clock-free autonomous deterministic controller receiving only the declared observation stream and side information after initialization.

For finite incompletely specified machines, this is a compatible closed-cover problem: cover members must admit a common output/action and their implied successor sets must be contained in cover members.

## Theorem 5.1 — deterministic hierarchy

Under aligned residual, tolerance, observation, side-information, and boundary semantics,

\[
\boxed{
\chi^{\rm det}_{\rm act}
\le
\chi^{\rm det}_{\rm plan}
\le
N^{*,\rm det}_{\rm dyn}.
}
\]

### Proof

A common deterministic plan has a common first action, so every plan-compatible block is action-compatible. This yields the first inequality.

For the second, fix any autonomous deterministic controller with \(N\) reachable states. For each controller state, collect the residual situations that can coexist with it. Starting from that internal state, the controller induces one deterministic rooted strategy on all future suffixes; hence each such residual set is plan-compatible. These at most \(N\) sets cover the reachable residual situations, so a plan coloring with at most \(N\) colors exists. Minimize over controllers. \(\square\)

Both inequalities can be strict. The finite witnesses are registered in the hostile-check suite.

### Boundary

The unrestricted randomized analogue is OPEN. Randomization must be typed and charged consistently across first-action kernels, rooted-plan feasibility, retained private randomness, and autonomous state accounting. A deterministic theorem must not be silently promoted to randomized controllers.

---

# 6. Zero-error causal-cut lower bound

Consider a complete causal cut carrying transcript \(Y\) from a root-history side to a downstream deterministic plan selector. All other downstream side information is declared in \(s\).

Under a pathwise zero-error contract, whenever transcript value \(y\) can occur after history \(h\), the plan selected from \((y,s)\) must be valid from \(h\). Therefore all histories sharing the same transcript symbol form a plan-compatible block.

For a finite transcript alphabet,

\[
\boxed{|\mathcal Y|\ge\chi^{\rm det}_{\rm plan}(\varepsilon;s).}
\]

The naive statement “a stochastic channel with \(|Y|\) symbols carries at most \(\log_2|Y|\) bits by pigeonhole reasoning” is not a substitute for this theorem. Average-error or Shannon-style claims require their own probability/source assumptions.

---

# 7. Prior-free decision order

Let \(\Psi_\theta(M)\) collect every registered obligation and resource coordinate of machine \(M\) under substrate condition \(\theta\). Define

\[
N\preceq_\theta M
\iff
\Psi_\theta(N)_\lambda\le\Psi_\theta(M)_\lambda
\quad\forall\lambda.
\]

Strict dominance additionally requires inequality on at least one coordinate. The prior-free frontier is the nondominated set.

No probability measure over \(\mathcal E\) is used.

A scalar selector \(\Phi\) is guaranteed not to select a dominated point only when it is strictly monotone for the declared coordinatewise order. Expected-risk Bayes objectives can fail this property for pointwise dominance when strict improvement occurs only on a prior-null environment. Priors are therefore optional selectors, not the definition of the order.

In a nonempty compact finite-dimensional profile image, a Pareto point exists by minimizing any strictly positive weighted sum. In unrestricted infinite spaces the nondominated set may be empty without an existence condition.

---

# 8. Operational morphology and non-leakage

Let \(\mathcal Q\) be the declared family of behavioral, causal-cut, physical, and resource probes relevant to the claim. Define

\[
M\simeq_{\mathcal Q}N
\iff
q(M)=q(N)\quad\forall q\in\mathcal Q.
\]

The operational morphology class is

\[
\chi_{\mathcal Q}(M)=[M]_{\simeq_{\mathcal Q}}.
\]

A machine-dependent premise \(F\) is architecture-neutral at this resolution only if it factors through the quotient:

\[
F=\bar F\circ\chi_{\mathcal Q}.
\]

Hence a representation-invariant theory cannot derive implementation syntax below its declared probe resolution. Resource measurements may distinguish physically different realizations, but the measurement rule itself must be operational rather than label-dependent.

This blocks hidden architecture priors such as “attention is cheap” or “neural programs are searched first” unless those assumptions are explicitly part of the substrate or development model.

---

# 9. Necessity–construction sandwich

Let

\[
\mathfrak X^{\rm phys}_\theta
\]

be the unknown set of operational morphology classes physically realizable at substrate condition \(\theta\).

Let \(\mathfrak X^{\rm nec}_\theta\) be the set satisfying every proved necessary condition, and \(\mathfrak X^{\rm con}_\theta\) the classes with explicit verified constructions. Soundness gives

\[
\boxed{
\mathfrak X^{\rm con}_\theta
\subseteq
\mathfrak X^{\rm phys}_\theta
\subseteq
\mathfrak X^{\rm nec}_\theta.
}
\]

Defining \(\mathfrak X^{\rm phys}_\theta\) or writing down its Pareto frontier is not a derivation. Closure requires the inner and outer arguments to meet.

## Theorem 9.1 — Pareto-profile closure

Let \(Y^\bullet_\theta=\Psi_\theta(\mathfrak X^\bullet_\theta)\). Suppose a set \(F_\theta\subseteq Y^{\rm con}_\theta\) satisfies:

1. no two distinct profiles in \(F_\theta\) strictly dominate one another;
2. for every \(y\in Y^{\rm nec}_\theta\), some \(f\in F_\theta\) obeys \(f\le y\).

Then

\[
\boxed{
\operatorname{Pareto}(Y^{\rm phys}_\theta)=F_\theta
}
\]

up to equality of objective profiles.

### Proof

Every \(f\in F_\theta\) is physically achievable. If some physical profile strictly dominated \(f\), outer domination would provide another \(f'\in F_\theta\) no worse than that dominator and hence strictly better than \(f\), contradicting the antichain property. Conversely, if \(y\) is physically Pareto-optimal, outer domination supplies an achievable \(f\le y\); Pareto optimality forces equality of profiles. \(\square\)

This is the formal bidirectional-vise criterion: derive lower bounds from above, constructions from below, and close the frontier only where they meet.

---

# 10. Performance closure is not morphology identity

For a frontier profile \(f\), consider all necessary morphologies mapping to it. If several operationally distinct classes share the same optimal profile, the theory has a tie/phase-coexistence region rather than a unique morphology.

Therefore full morphology closure requires two theorems:

\[
\text{profile-frontier closure}
\quad+\quad
\text{frontier-fiber identification}.
\]

Named architecture syntax below \(\mathcal Q\)-resolution is not identifiable and must not be inferred from performance optimality.

---

# 11. Resource-conditioned phase law

A genuine phase diagram is a set of certificates of the form

\[
\theta\in R_i
\Longrightarrow
\operatorname{Pareto}(Y^{\rm phys}_\theta)=F_i(\theta),
\]

with morphology-fiber statements where required. Hardware constants may remain external measured parameters; the theory can still be complete conditionally over \(\theta\) if the relevant regions and transitions are proved.

---

# 12. Architecture-independent channel laws

A simple example illustrates the intended level of theory. In one stochastic environment, suppose a decisive fair hidden bit is located uniformly among \(L\) positions. A primary channel resolves it on an event whose probability is at most \(r/L\), and after a miss the machine's remaining view contains no information about the bit. Then

\[
\operatorname{Acc}\le\frac12+\frac{r}{2L}.
\]

If a secondary rescue channel reveals a primary miss with conditional probability at most \(p\), and after both channels fail the remaining view is still independent of the bit, then

\[
\operatorname{Acc}
\le
1-\frac{(1-r/L)(1-p)}2.
\]

These are conditional channel laws. The randomness belongs to the declared structural environment; it is not a Bayesian prior over architecture hypotheses or environment classes.

---

# 13. Developmental reachability

Let \(D\) be a development/search process and \(B\) a budget. Define the reachable morphology set \(\mathcal R_B\).

Two frontiers must be separated:

\[
\mathcal G_B
=\mathcal F_{\rm global}\cap\mathcal R_B
\]

and

\[
\mathcal F_B
=\operatorname{Pareto}(\mathfrak X^{\rm phys}_\theta\cap\mathcal R_B).
\]

The first is the reachable part of the global frontier; the second is the best frontier among reachable machines. They need not coincide, and the first can be empty while the second is nonempty.

A syntax-level development kernel can reintroduce an architecture prior. Let \(q_\mathcal Q\) be the operational quotient. Architecture-neutral developmental claims require quotient compatibility:

\[
M\simeq_\mathcal Q N
\Longrightarrow
(q_\mathcal Q)_\#D(\cdot\mid M)
=(q_\mathcal Q)_\#D(\cdot\mid N).
\]

If this fails, reachability is search-prior-sensitive. Universal-program search does not remove the issue automatically because coding/reference-machine choices can alter active-agent behavior.

---

# 14. Representation coverage, recovery, prediction

Every implemented classical causal interactive machine can be represented as a causal transducer by taking its complete retained physical configuration as raw state. Quotienting by \(\simeq_\mathcal Q\) gives an operational morphology class. This establishes broad **representation coverage**.

Coverage is not recovery.

A valid recovery test freezes the problem, resource model, probe vocabulary, and derivation protocol without using the held-out architecture label, derives a region, and only then reveals the held-out form.

A valid prospective prediction is stronger: derive and freeze a nonempty morphology region before any inhabitant is known, then subsequently construct or discover an inhabitant.

The principal architecture-neutral reduction coordinates are:

- persistence timescale;
- access geometry;
- update geometry;
- routing topology;
- counterfactual/simulation structure;
- composition boundaries;
- resource-response vector;
- approximation contract.

Transformers, recurrent/SSM systems, graph/message-passing machines, external-memory and retrieval systems, symbolic/probabilistic/program-search systems, world-model planners, evolutionary systems, tool agents, multi-agent systems, and neuromorphic implementations can all be described in these operational terms. That is coverage only. It does not show that their regions were predicted without historical exposure.

Genuinely quantum external input/output remains outside the present classical interface and requires a quantum-instrument extension.

---

# 15. OCM consequences

The present Language KSO, Method KSO, Wisdom KSO, field/subject/domain organization, symbolic grammar, controller structures, and retrieval mechanisms are candidate implementations, not primitives of cognition.

An OCM architecture-benefit claim should therefore be formulated as:

1. freeze \((\Omega,\mathcal E,\mathfrak B,\Theta,\rho,\mathcal Q)\);
2. derive necessary residual/control/channel/resource constraints;
3. construct OCM and matched alternatives under the same boundary;
4. compare complete resource/performance profiles;
5. identify the nondominated profile frontier;
6. claim morphology only if the frontier fiber is operationally identified;
7. keep developmental reachability separate from static optimality.

A result that merely says the current OCM architecture performed well on its authored search trajectory is not a zero-architecture-prior morphology theorem.

---

# 16. Current closure ledger

Closed or theorem-backed within the stated domains:

- measure-free pointwise/robust decision order;
- canonical exact predictive residual;
- generic control non-quotient result;
- finite deterministic action/plan/dynamic-state hierarchy;
- finite deterministic closed-cover controller specialization;
- zero-error deterministic cut coloring bound;
- architecture non-leakage criterion;
- necessity/construction Pareto-profile closure theorem;
- broad classical representation coverage.

Open:

- general randomized-controller hierarchy/closed-cover analogue;
- time-held-out architecture recovery under a frozen vocabulary;
- preregistered prospective unknown-form prediction;
- nontrivial substrate-specific morphology frontier closure for OCM;
- general developmental/search closure;
- quantum external-interface extension.

No stronger terminal should be reported until the corresponding open obligation is discharged by a registered proof, construction, or prospective test.

---

# 17. Donor boundary

The programme absorbs rather than renames prior results. Relevant donors include Blackwell comparison of experiments; zero-error graph/chromatic communication results; predictive-state representations and causal-state ideas; incompletely specified finite-state-machine closed-cover minimization; No-Free-Lunch boundaries; information bottleneck/rate-distortion as distribution-conditioned specializations; bounded-rationality information-cost formalisms; and universal-agent work showing reference-machine sensitivity.

The candidate GMI contribution is the cross-layer chain

\[
\text{obligation/ecology residuals}
\to
\text{control information}
\to
\text{causal-cut bounds}
\to
\text{resource outer constraints}
\leftrightarrow
\text{explicit constructions}
\to
\text{certified morphology phases}
\to
\text{prospective machine-form prediction},
\]

with each arrow carrying its own proof and evidence status.
