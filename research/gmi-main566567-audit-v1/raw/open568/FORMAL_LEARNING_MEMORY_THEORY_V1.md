# Formal learning and memory theory V1 — LMT-1–8

Status: **DEFINITIONAL CORE + CONDITIONAL THEOREMS**  
Date: 2026-09-13

This capsule gives GMI explicit meanings for learning, knowledge change, improvement, convergence, forgetting, revision and failure. It uses the minimal declaration

\[
\mathcal G=(\mathcal I,\mathcal E,\mathcal O,\mathcal R,\mathcal D)
\]

from `MINIMAL_AXIOM_FREEZE_V1.md` and does not replace the exact semantic-state, reuse/invalidation or representation experiments already on main.

The definitions deliberately separate three traditions that are often conflated: statistical/PAC learning, online regret, and belief/semantic identification. PAC-style finite-sample guarantees trace to Valiant and statistical learning theory; online regret to the prediction-with-expert-advice/online-learning literature; logical revision to AGM-style belief revision. GMI's role here is to place them under one declared causal/resource/development interface, not to claim those parent results as new.

## 1. Learning state

At development time `t`, write the machine state as

\[
X_t=(W_t,K_t,\Gamma_t).
\]

- `W_t` — **working state**: transient state needed to continue the current computation or interaction;
- `K_t` — **retained epistemic state**: parameters, hypotheses, rules, indexes, sufficient statistics, representations or other retained objects used on later tasks;
- `Gamma_t` — **provenance/dependency state**: evidence identifiers, assumptions, scopes, version/source bindings and dependency edges supporting retained claims.

A development update is an admitted causal map

\[
X_{t+1}=U_t(X_t,Z_t,\xi_t),\qquad U_t\in\mathcal D,
\]

where `Z_t` is newly available evidence/feedback and `xi_t` is admitted private randomness available at the declared decision time. Its acquisition, computation, storage and update costs are charged by `R`.

A state change is not automatically learning.

## 2. LMT-1 — what is learned

Fix an evaluation environment/law `P in E`, a protected future interface, and a predictor/policy/decoder `a(K)` induced by retained state. Let the obligation provide a bounded loss `ell in [0,1]` for this theorem; other obligations require their own integrability/order conditions.

Define future risk

\[
R_P(K)=\mathbb E_P[\ell(a(K),Z^{future})].
\]

For comparator family `H`, let

\[
R_P^*=\inf_{h\in H}R_P(h).
\]

The following are different valid learning statements.

### Statistical/PAC learning

After `n` observations, `K_n` **(epsilon,delta)-learns H in risk** when

\[
P\bigl(R_P(K_n)\le R_P^*+\epsilon\bigr)\ge1-\delta.
\]

The sampling assumptions defining that probability are part of the claim.

### Online learning

For actions `a_t` and revealed losses `ell_t`, regret against comparator `h` is

\[
Reg_T(h)=\sum_{t=1}^T \ell_t(a_t)-\sum_{t=1}^T\ell_t(h).
\]

The process **learns in the no-regret sense** against `H` when

\[
\sup_{h\in H}Reg_T(h)/T\to0
\]

with the declared mode of convergence/sign convention. This does not imply parameter identification.

### Semantic/parameter identification

Let `q(P)` be a protected identifiable target (semantic state, causal parameter, support, representation class, etc.). An estimator `qhat_t(K_t)` is consistent when

\[
qhat_t\to q(P)
\]

in the declared topology/mode. Identification requires that observational/interventional distributions admitted by the interface actually distinguish the target.

None of these three definitions implies the other two without additional premises.

## 3. LMT-2 — improvement

A state transition `K -> K'` is an **evaluation improvement** for `P` if

\[
R_P(K')<R_P(K).
\]

For an environment class, one may instead require worst-case, Bayes, distributionally robust or vector improvement, but that choice must be declared in `O/E`.

If resources matter, there are two valid forms:

1. **Pareto improvement:** no protected risk/resource coordinate worsens and at least one improves;
2. **scalarized improvement:** a preregistered scalar functional `J(R_P(K),rho(K))` decreases.

A lower training loss, a larger parameter change, or a new representation is not by itself an improvement theorem. Componentwise minima from different unattainable states may not be combined.

## 4. LMT-3 — a known finite learner derived as a specialization

Assume:

1. `H` is finite and nonempty;
2. examples `Z_1,...,Z_n` are iid from `P`;
3. every loss `ell(h,Z)` lies in `[0,1]`;
4. `D` admits empirical-risk minimization (ERM), returning `hhat` whose empirical risk is minimal in `H`;
5. the computation/storage cost of evaluating and retaining `H` is charged by `R`.

For `epsilon,delta in (0,1)`, if

\[
n\ge \frac{2}{\epsilon^2}\log\frac{2|H|}{\delta},
\]

then

\[
P(R_P(hhat)\le R_P^*+\epsilon)\ge1-\delta.
\]

Proof. Hoeffding plus a union bound gives, with probability at least `1-delta`,

\[
\sup_{h\in H}|\widehat R_n(h)-R_P(h)|\le\epsilon/2.
\]

On this event, for an optimal comparator `h*`,

\[
R_P(hhat)\le\widehat R(hhat)+\epsilon/2
\le\widehat R(h^*)+\epsilon/2
\le R_P(h^*)+\epsilon.
\]

QED.

This is a standard finite-class PAC/ERM result, not a new GMI learner. The derivation demonstrates the intended discipline: a known learner appears only after the sampling law, hypothesis family, loss, admitted update and resource costs are supplied.

### Approximate optimization form

If the development process returns an `eta_n`-approximate ERM,

\[
\widehat R(hhat_n)\le\inf_{h\in H}\widehat R(h)+\eta_n,
\]

then on the same uniform-convergence event

\[
R(hhat_n)-R^*\le2\sup_h|\widehat R(h)-R(h)|+\eta_n.
\]

Thus risk consistency follows when the uniform deviation and optimization error both vanish. This identifies exactly where statistical and optimization assumptions enter.

## 5. LMT-4 — convergence is claim-specific

GMI recognizes at least four distinct convergence claims.

- **risk consistency:** `R_P(K_t)->R_P^*`;
- **no regret:** average regret tends to zero;
- **semantic/parameter consistency:** an identifiable protected target converges;
- **state convergence:** `K_t` itself converges in a declared metric.

State convergence is neither necessary nor sufficient for risk convergence. Multiple parameter states can implement the same protected response; conversely a convergent but misspecified state can retain positive excess risk.

A convergence theorem must disclose the premises it uses, commonly including some subset of:

- stationarity/iid/ergodicity or an explicit adversarial online protocol;
- identifiability;
- adequate hypothesis/realization class;
- exploration or support coverage;
- capacity control/uniform convergence or a valid posterior/concentration mechanism;
- optimization error control;
- stable resource availability;
- a fixed target or an explicit drift budget.

## 6. LMT-5 — impossibility without identifiability

> **Two-world indistinguishability theorem.** Suppose environments `P0,P1 in E` induce exactly the same distribution over every observation available to the learner under its admitted development policy, but the unique obligation-optimal terminal outputs are `0` in `P0` and `1` in `P1`. Then no learner can have success probability strictly greater than `1/2` in both worlds.

Proof. Because the complete learner-visible histories have the same law, the distribution of its terminal output is the same in both worlds. Let `q` be its probability of outputting `1`. Success is `1-q` in `P0` and `q` in `P1`; their minimum is at most `1/2`. QED.

Consequences:

- observationally indistinguishable causal models cannot be uniquely learned without added interventions/assumptions;
- a policy that never explores an action cannot generally identify its unobserved consequence;
- omitted support outcomes can block a sure-safety claim;
- unrestricted drift can make a static target undefined.

The correct repair is to strengthen the interface/data assumptions, weaken the target to an identifiable equivalence class, or retain uncertainty—not to declare convergence from repeated updates.

## 7. LMT-6 — retained memory, revision and conflict

A retained claim is stored as a record

\[
c=(statement,scope,status,evidence,parents,cost).
\]

`Gamma_t` is a directed dependency graph over such records. A valid revision operation must:

1. preserve source/evidence identity needed for the protected audit contract;
2. distinguish retraction from replacement;
3. invalidate or reopen every descendant whose proof requires a revoked parent, unless an independent surviving support path exists;
4. charge repair/rebuild/reverification work;
5. preserve incompatible live claims as an explicit conflict/uncertainty state until a declared rule resolves them.

A later observation does not get to overwrite an earlier contradictory record merely by recency. Bayesian conditioning, likelihood/e-process updates, AGM-style revision, truth-maintenance and domain-specific repair are different admissible specializations with different premises.

This extends the repo's existing certified-reuse/invalidation discipline from proof artifacts to the generic learning-memory layer.

## 8. LMT-7 — forgetting is lossy compression with a protected distortion contract

Let `F` map retained states to compressed/forgotten states, `K' = F(K)`. Define the protected continuation-response pseudometric `d_Q` already used by Grand GMI, or another declared risk distortion metric.

Forgetting is **epsilon-safe** on set `S` only if

\[
\sup_{K\in S}d_Q(K,F(K))\le\epsilon
\]

and the relevant resource ledger improves enough for the selected objective/frontier.

> **Exact no-free-forgetting lemma.** If `F(K_1)=F(K_2)` but there exists an admitted future continuation for which `K_1` and `K_2` require different unique obligation-correct responses, then no common decoder from the forgotten state can be exact for both.

Proof. The decoder receives the same forgotten state in both cases and therefore produces the same response distribution. It cannot equal two different unique required responses. QED.

Thus forgetting is safe only relative to a declared resolution/task/horizon/ecology. This mirrors the exact semantic quotient: collapsing distinctions that later matter is not lossless memory compression.

## 9. LMT-8 — failure taxonomy

The following are distinct failure modes and must not be reported under one generic label:

| Failure | Formal symptom | Typical repair |
|---|---|---|
| non-identifiability | two admitted worlds have same learner-visible law but different targets | interventions, assumptions, equivalence-class target |
| misspecification | `R_P^*` inside admitted `H` remains above desired risk | enlarge/change realization family |
| estimation error | empirical/posterior uncertainty remains large | more/better data, valid concentration |
| optimization error | chosen state far from best admitted empirical/objective state | better search/optimization or weaker guarantee |
| exploration failure | relevant consequences never become observable | active exploration with charged risk/cost |
| drift | no fixed target/law satisfies the theorem's premise | dynamic comparator/drift budget/change detection |
| catastrophic forgetting | protected old-task risk increases after updates | replay/regularization/modularity or accept declared trade-off |
| invalid revision | revoked evidence still supports descendants | provenance repair/invalidation |
| resource exhaustion | valid update/certificate cannot be executed within `R` | cheaper representation/update or weaker objective |

A theory that merely records state changes cannot distinguish these mechanisms and therefore has not yet supplied a learning theorem.

## 10. Boundaries and falsifiers

The finite ERM theorem is falsified by any finite `H`, iid `[0,1]` loss process and exact ERM satisfying the sample-size condition for which the stated PAC probability fails. The indistinguishability theorem is falsified by a learner observing identically distributed histories in the two declared worlds yet exceeding `1/2` success in both without additional information. The forgetting lemma is falsified by an exact common decoder after a collision of two states requiring distinct unique outputs.

This capsule does not claim that iid ERM is universally appropriate, that retained propositions are the only form of knowledge, or that every useful learner converges. It provides the vocabulary and sufficient conditions needed to make such claims testable.
