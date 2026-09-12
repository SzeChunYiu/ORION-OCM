# GMI Species Phase Laws v1

Status: **FORMAL/QUANTITATIVE HARDENING — MIX OF EXACT IDENTITIES, BOUNDS AND PROSPECTIVE RESPONSE LAWS**

Status date: 2026-09-12.

Purpose:

> Convert qualitative species niches into measurable inequalities, lower bounds and crossover laws. These laws are not universal constants; each is valid only under the stated lifecycle accounting and assumptions.

---

# 1. Burden notation

Let a lifecycle burden vector be

\[
B=(B_{train},B_{data},B_{search},B_{serve},B_{lat},B_{mem},B_{comm},B_{update},B_{verify},B_{human},B_{energy},B_{risk}).
\]

GMI comparisons should remain Pareto/multiobjective whenever possible.

When an ecology explicitly supplies a price vector `pi >= 0`, a registered scalarized burden may be used:

\[
C_\pi(M)=\pi^\top B(M)+L_{sem}(M).
\]

There is no universal `pi`.

---

# 2. RQM residual lower bound

Let predictive state be `S_P` and target semantic state `S_O`.

For predictive fiber `p`, define

\[
m(p)=|\{s_O:P(S_O=s_O,S_P=p)>0\}|.
\]

Any exact residual alphabet `R` permitting reconstruction

\[
S_O=g(S_P,R)
\]

must satisfy

\[
|R|\ge \max_p m(p).
\]

Therefore fixed-length worst-case residual bits obey

\[
B_R^{wc}\ge \lceil\log_2\max_p m(p)\rceil.
\]

For ordinary lossless conditional coding,

\[
E[\ell(R)]\ge H(S_O\mid S_P).
\]

This is an exact information lower bound at finite scope.

---

# 3. RQM lifecycle crossover

Let:

```text
C_core       one-time broad predictor acquisition cost
C_res        residual acquisition cost
u_res        expected number of residual update events
c_res_up     cost per residual update
u_full       full-model update count (normally same event count)
c_full_up    cost per full-model update
N            query count
c_rqm        RQM query cost
c_full       full model query cost
```

Then a necessary accounting comparison is

\[
C_{RQM}=C_{core}+C_{res}+u_{res}c_{res,up}+Nc_{rqm}
\]

versus

\[
C_{FULL}=C_{full,acq}+u_{full}c_{full,up}+Nc_{full}.
\]

RQM is burden-preferred under the registered scalarization when

\[
(C_{full,acq}-C_{core}-C_{res})
+u(c_{full,up}-c_{res,up})
+N(c_{full}-c_{rqm})>0.
\]

The experiment must manipulate residual complexity/volatility independently; otherwise this inequality is bookkeeping rather than an explanatory law.

---

# 4. VRQM speculative/versioned update threshold

For a residual update, let:

```text
p_bad      probability candidate is inadmissible before verification
L_bad      loss if bad candidate is served/adopted
c_iso      isolation/shadow-state burden
c_v        verification burden
c_hist     extra retained-history burden
L_ret      expected retention/rollback loss avoided by retaining incumbent/history
```

A simple one-step versioned-admission crossover is

\[
p_{bad}L_{bad}+L_{ret} > c_{iso}+c_v+c_{hist}.
\]

This does **not** imply persistent history whenever drift is high. `c_hist` and `L_ret` depend on the actual lineage/rollback obligation.

---

# 5. VGSC amortization law

Suppose independent proposals are generated until an admissible proposal occurs with probability `p_a>0` per proposal. Let proposal+verification cost per trial be `c_g+c_v`; after acceptance compile cost is `c_c`; compiled serving cost `c_s`; direct trusted solving cost per use `c_d`; accepted result reused `R` times.

Expected VGSC cost under geometric proposal trials is

\[
E[C_{VGSC}]=\frac{c_g+c_v}{p_a}+c_c+Rc_s.
\]

Direct repeated trusted solving costs

\[
C_D=Rc_d.
\]

Therefore VGSC amortizes when

\[
R>\frac{(c_g+c_v)/p_a+c_c}{c_d-c_s},
\]

assuming `c_d>c_s` and verifier false-adoption risk is negligible or separately charged.

With verifier false-accept probability `alpha`, add expected protected loss `alpha L_f` at the appropriate lifecycle frequency.

---

# 6. IQL intervention rule

Let current protected Bayes/decision risk be `R_t`. For legal intervention `j` with cost `c_j`, define expected post-intervention risk

\[
E[R_{t+1}\mid do(j)].
\]

The one-step value of information is

\[
V(j)=R_t-E[R_{t+1}\mid do(j)].
\]

A myopic rational intervention satisfies

\[
V(j)>c_j
\]

under a common registered burden scale.

For target ambiguity functional `A`, a quotient-focused proxy is

\[
IG_O(j)=A(S_O\mid E_t)-E[A(S_O\mid E_{t+1})\mid do(j)].
\]

The empirical GMI claim is that `IG_O` predicts intervention utility better than generic predictive entropy in target-aliased ecologies.

---

# 7. LMHM local-switch threshold

For factor `i`, compare incumbent realization `a` and candidate family `b` over expected remaining horizon `H`.

Let per-unit-horizon burden difference favoring `b` be

\[
\Delta c_i=c_i(a)-c_i(b).
\]

Let local search/switch/verification cost be `C_i^{switch}`.

Local switching is lifecycle-beneficial when

\[
H\Delta c_i>C_i^{switch}.
\]

A global rearchitecture with cost `C_{global}` is dominated by local switching if

\[
C_i^{switch}+Hc_i(b)+H\sum_{j\ne i}c_j
<
C_{global}+H\sum_j c'_j.
\]

The key predictive variable is affected dependency cone, not architecture name.

---

# 8. SCDI compilation threshold

Let universal serving cost per query be `c_u`; specialized compiled serving cost `c_s<c_u`; compile/synchronization burden for a serving context be `C_c`; expected uses before invalidation `R`.

Compilation pays when

\[
R(c_u-c_s)>C_c.
\]

Thus

\[
R^*=\frac{C_c}{c_u-c_s}
\]

is the finite amortization threshold.

Multiple serving contexts should each be evaluated against their own `R_k`, price vector and synchronization cost.

---

# 9. ETMI evidence-authority separation law

For evidence item `e`, let relevance benefit be `V_rel(e)` and expected protected loss from admitting an unauthoritative item be `p_bad(e)L_bad`.

Let authority/provenance checking cost be `c_auth(e)`.

Authority checking is economically justified when

\[
p_{bad}(e)L_{bad}>c_{auth}(e)
\]

for decisions where the item would otherwise be admitted.

Prediction: as `L_bad` or source unreliability rises, the optimal system increasingly separates retrieval relevance from authority admission.

---

# 10. CRWM causal residual lower bound

Let passive predictive state `S_P` and intervention-sufficient target state `S_{do}`.

Any exact causal residual `R_do` satisfying

\[
S_{do}=g(S_P,R_{do})
\]

obeys the same fiber lower bound as RQM:

\[
|R_{do}|\ge \max_p |\{s_{do}:P(s_{do},p)>0\}|,
\]

and average conditional coding burden at least

\[
H(S_{do}\mid S_P).
\]

This quantifies the information passive prediction cannot supply in an observationally aliased causal ecology.

---

# 11. BHI branching threshold

Suppose two live hypotheses `h1,h2` cannot yet be distinguished. Collapsing now incurs expected irreversible wrong-commitment loss `L_commit`; keeping both branches costs `c_branch` per step for `T` steps until expected discriminating evidence.

Branching is favored when

\[
E[L_{commit}\ avoided]>Tc_{branch}.
\]

With branch probabilities `p_i` and action losses `L(a,h_i)`, the exact decision-theoretic value is the difference between minimum expected loss with future branch resolution and the loss under forced present collapse.

Prediction: benefit vanishes as discriminating evidence becomes immediate or commitment becomes reversible.

---

# 12. MTCI consolidation threshold

A reusable item currently lives in fast/ephemeral layer `f`.

Let:

```text
R          expected future reuse count before invalidation
c_f        per-use/reconstruction cost in fast layer
c_s        per-use cost after consolidation in slow layer
C_write    consolidation/write cost
C_int      expected interference/retention cost introduced by consolidation
```

Consolidate when

\[
R(c_f-c_s)>C_{write}+C_{int}.
\]

Therefore

\[
R^*=\frac{C_{write}+C_{int}}{c_f-c_s}.
\]

This predicts consolidation by recurrence/reuse and interference, not wall-clock time alone.

---

# 13. CDTE tool choice law

For tool `t` on obligation `O`, let expected semantic loss be `L_t(O)` and burden vector `B_t(O)`.

Under registered prices `pi`, legal tool selection is

\[
t^*(O)=\arg\min_{t\in\mathcal T_{legal}}\left[L_t(O)+\pi^\top B_t(O)\right]
\]

subject to any hard admissibility constraints.

Changing `pi` with `O` fixed should induce predictable tool-routing transitions.

---

# 14. RAI substrate migration law

Suppose semantic-equivalent realization `a` consumes resource vector `r_a` per use and `b` consumes `r_b`. Current price vector is `pi`; migration cost is `C_{a\to b}`; expected remaining use count `R`.

Migrate when

\[
R\pi^\top(r_a-r_b)>C_{a\to b}.
\]

If price vector changes to `pi'`, the boundary moves accordingly. Irreversibility/hysteresis comes from migration/search state and must be separately charged.

---

# 15. CQI communication lower bound

Let receiver have side information `Z_R`, receive messages `M`, and require exact reconstruction of target state `S_O`:

\[
H(S_O\mid Z_R,M)=0.
\]

Then

\[
H(S_O\mid Z_R)
=I(S_O;M\mid Z_R)
\le H(M\mid Z_R).
\]

Therefore any exact protocol must communicate conditional information at least

\[
H(M\mid Z_R)\ge H(S_O\mid Z_R).
\]

For finite worst-case coding, corresponding conditional distinguishability/cardinality bounds apply.

This gives a non-neural lower bound on genuinely collective sufficient state.

---

# 16. MRQL minimal-resolution law

Let nested quotient levels `S_0,...,S_k` have serving costs

\[
c_0\le c_1\le\cdots\le c_k.
\]

For query `q`, define

\[
i^*(q)=\min\{i:S_i\text{ is sufficient for }q\}.
\]

An oracle quotient ladder has expected serving cost

\[
E[c_{i^*(q)}],
\]

while an always-finest system costs `c_k`.

Maximum possible expected saving is

\[
c_k-E[c_{i^*(q)}].
\]

Real systems must subtract routing/classification overhead and error from choosing insufficient levels.

---

# 17. PCAI local-certification threshold

Let unconstrained adaptive update create expected false-adoption loss `L_u`; frozen certified system incurs expected obsolescence loss `L_f`; local proof-carrying update costs `c_up+c_proof+c_verify` and leaves residual risk `L_p`.

PCAI is preferred when

\[
c_{up}+c_{proof}+c_{verify}+L_p<\min(L_u,L_f)
\]

under a common registered horizon/accounting.

The hypothesis is strongest when verifier dependency cone aligns with update cone.

---

# 18. EPrI semantic precision allocation

For factor `i`, choose precision `b_i` with resource cost `c_i(b_i)` decreasing as precision is reduced and protected distortion `d_i(b_i)` increasing as precision is reduced.

Solve

\[
\min_{b_1,...,b_n}\sum_i c_i(b_i)
\]

subject to

\[
\sum_i d_i(b_i)\le\epsilon.
\]

For differentiable interior solutions, KKT conditions imply

\[
-\frac{c_i'(b_i)}{d_i'(b_i)}=\lambda
\]

for all active factors.

Thus the optimal system equalizes marginal resource saving per marginal semantic distortion, rather than assigning precision solely by layer identity.

---

# 19. APO portfolio maintenance threshold

Let a portfolio add expected niche-specific benefit `G` over the best single solver, while costing maintenance `C_m`, routing `C_r` and additional search/tuning `C_s` over the registered horizon.

Portfolio is justified only if

\[
G>C_m+C_r+C_s.
\]

As ecology becomes homogeneous, `G` should collapse and portfolio diversity become dominated.

---

# 20. SMMS meta-morphogenesis threshold

Let building a self-response/meta-morphogenesis model cost `C_meta`. Across future ecology shifts `e_1,...,e_K`, let adaptation burden saved relative to a strong static search parent be `\Delta C_k`.

Meta-morphogenesis amortizes when

\[
\sum_{k=1}^K E[\Delta C_k]>C_{meta}.
\]

The protected scientific claim requires positive savings on **unseen shift families**, not repeated versions of the meta-training shifts.

---

# 21. Interaction laws

Species mechanisms need not add linearly.

For mechanisms `a,b`, define interaction on outcome `Y` as

\[
\Delta_{ab}
=
Y_{11}-Y_{10}-Y_{01}+Y_{00}.
\]

A composite species requires explicit interaction tests. If `Delta_ab≈0`, the combination may be mere independent composition. Strong species-level claims require recurrent non-additive lifecycle or semantic effects where predicted.

---

# 22. What remains empirical

These inequalities provide thresholds **given measurable terms**. They do not yet solve the difficult quantitative problem of predicting every term from pre-outcome ecology descriptors.

The next level is to learn/test architecture-neutral response laws for:

```text
p_bad
verification error and cost
residual information from observable proxies
expected reuse/invalidation horizons
interference cost
morphology switch cost
causal intervention value
communication sufficiency
semantic distortion vs precision
meta-morphology transfer
```

Those terms enter the quantitative closure registry and are blocking whenever a high-level phase prediction depends on them.
