# HST Transfer Bound V1 (lane D, D6 — HST-T09)

Row: `HST-T09` (P3), statement frozen in `HST_THEOREM_REGISTRY_V1.json`. Nothing below
edits the statement. Notation follows `HST_DEFINITIONS_V1.md` (Σ_t, Q_t, E_t, B_t).

**Honesty preamble.** Every mathematical step below is parent-owned (McAllester 1999;
Langford–Seeger 2002; Maurer 2004; Topsøe 2007; survey Alquier 2021, arXiv:2102.07152;
Baxter JAIR 2000 for the bias-learning framing). Lane D's contribution is exactly what
the registry's `ocm_residual` field assigns: the instantiation of the bound at the OCM
finite morphology/operator-bias class (#221 zoo census), the explicit-numbers table,
the vacuity range at zoo scope, and the paired hostile
(`NEGATIVE_TRANSFER_COUNTEREXAMPLE_V1.md`). No new learning theory is claimed.

---

## 1. The finite HST bias class (definitions, frozen-compatible)

**Candidate space.** `X` finite, `|X| = N`. OCM instance: the #221 feasible-genotype
census universe `N = 28,584` (`FREEZE_V1_AMEND_4.json`/`AMEND_5`, run
`zoo-census-gate-ceiling`, receipt `6ce5ceff38a0de5c`).

**Operator-bias kernels.** A *bias* is a choice of proposal kernel over `X`
(definition §1: `Q_t(·|L_t,H_t,E_t,R_t)`). We take a **finite kernel family**
`Q_1,…,Q_K`, each a fixed proposal distribution; OCM instance: one uniform-over-cell
kernel per census archive cell — `K = 83` (D3d@10 occupied cells), with `K = 50` (D2d)
and `K = 64` (CVTD niches) as sibling readings. The *learned bias* is a mixture

```text
Q_ρ = Σ_{k=1..K} ρ_k Q_k,   ρ ∈ Δ_K   (a "Gibbs-posterior-style" mixture)
```

with information budget `ρ_budget = KL(Q_ρ ‖ Q_0)` against the flat kernel prior
`Q_0 = Unif{1..K}` (index-space uniformity; as a candidate distribution this is the
do-nothing bias that ignores experience). "Flat prior" never means a new universal
prior over arbitrary futures — it is the frozen uniform over the same K kernels.

**Ecology.** Task space `T = {τ_1,…,τ_T}` finite with ecology distribution `D ∈ Δ(T)`
(the "registered ecology" of definitions §4/§5; P3 rows need an explicit sampling rule
— this is it). Tasks `τ_1,…,τ_m` are drawn i.i.d. from `D`.

**Per-task loss (burden/quality form, [0,1]-bounded).** For task `τ` with frozen
admissible set `A_τ ⊆ X` (the frozen `Adm` predicate of the registration — OCM
instance: `dev_score ≥ bar`, `bar = 0.224507`, the #221 amend-5 census-median quality
gate),

```text
ℓ(Q, τ) = 1 − Q(A_τ) = P_{x~Q}[x is inadmissible for τ]
```

the probability that a proposal from `Q` fails the admission predicate — the natural
[0,1] scalarization of search burden (see §5 for what this choice does and does not
license: the *unnormalized* expected-proposals-to-first-admission `1/Q(A_τ)` is
unbounded and no PAC-Bayes bound in this file applies to it).

`E_D[ℓ(Q,τ)] = Σ_τ D(τ) ℓ(Q,τ)` is the **D-excess burden** quantity the bound controls
(relative to whatever empirical value it is compared against; absolute burden is
`E_D[ℓ]` itself since the loss already sits in [0,1]).

---

## 2. The bound (Theorem T09-B)

> **Theorem T09-B (parent: PAC-Bayes, McAllester/Langford–Seeger/Maurer form).**
> Fix a finite kernel family `{Q_k}`, a prior `Q_0` over kernels chosen **before**
> seeing `τ_1..τ_m`, and `δ ∈ (0,1)`. Draw `τ_1,…,τ_m ~ D` i.i.d. Let `ρ = ρ(τ_1..τ_m)`
> be **any** data-dependent mixture (any learning rule, including ERM, Gibbs posteriors,
> arbitrary adaptive selection). Then with probability ≥ `1 − δ` over the sample,
> simultaneously for the chosen `Q_ρ`:
>
> ```text
> E_{τ~D}[ℓ(Q_ρ,τ)]  ≤  (1/m) Σ_{i=1..m} ℓ(Q_ρ,τ_i)  +  sqrt( (KL(Q_ρ‖Q_0) + ln(2√m/δ)) / (2m) ).
> ```

This is the standard PAC-Bayes bound exactly as stated in the task route; every
constant is explicit (`2√m`, `δ`, the `1/2` from Pinsker, `1/(2m)`).

## 3. Derivation with per-step parent attribution

**Step 1 (fixed-kernel concentration, parent: Maurer 2004 Lemma 1 / Topsøe 2007).**
For a fixed kernel `Q` with `p = E_D[ℓ(Q,τ)]` and empirical `ℓ̂ = (1/m)Σ_i ℓ(Q,τ_i)`,
Bernoulli-KL `KL(ℓ̂‖p) = ℓ̂ ln(ℓ̂/p) + (1−ℓ̂) ln((1−ℓ̂)/(1−p))` satisfies

```text
E_S exp( m · KL(ℓ̂(S) ‖ p) )  ≤  2√m .
```

This replaces the cruder Hoeffding route (McAllester 1999 originally charged
`2·KL + ln(2√m/δ)`); the factor-2 saving is parent-owned, not ours. (Machine-checked
numerically in `check_bound_v1.py` part (c) by exact binomial enumeration.)

**Step 2 (change of measure, parent: Donsker–Varadhan variational formula, as used by
Langford–Seeger 2002 / McAllester 2003).** Let `ξ(S,k) = exp(m·KL(ℓ̂(k,S) ‖ p(k)))`
where `ℓ̂(k,S)` is the empirical loss of kernel `Q_k` and `p(k)` its D-risk. For any
data-dependent `ρ = ρ(S)`, the variational representation of KL gives, for every S,

```text
m·KL(ℓ̂(Q_ρ,S) ‖ p(Q_ρ)) − KL(ρ‖ρ_0)  ≤  ln Σ_k ρ_0(k) ξ(S,k)        (DV inequality)
```

with `ρ_0 = Unif{1..K}` the prior index distribution (`KL(Q_ρ‖Q_0) = KL(ρ‖ρ_0)` since
the kernel mixture map is a Markov kernel and KL contracts under it: KL(Q_ρ‖Q_0) ≤
KL(ρ‖ρ_0); we charge the larger right side, so the bound holds a fortiori).

**Step 3 (Fubini + Markov, parent: standard).** Taking expectations over S and using
that `ρ_0` is data-free (Fubini), then Step 1:

```text
E_S Σ_k ρ_0(k) ξ(S,k) = Σ_k ρ_0(k) E_S ξ(S,k)  ≤  2√m .
```

Markov's inequality on the nonnegative r.v. `Σ_k ρ_0(k) ξ(S,k)`: with probability
≥ 1 − δ, `ln Σ_k ρ_0(k) ξ(S,k) ≤ ln(2√m/δ)`. Combined with Step 2, with probability
≥ 1 − δ, **for the chosen ρ** (indeed simultaneously for all ρ):

```text
m · KL( ℓ̂(Q_ρ) ‖ E_D ℓ(Q_ρ) )  ≤  KL(ρ‖ρ_0) + ln(2√m/δ) .          (KL form)
```

**Step 4 (Pinsker inversion, parent: Bretagnolle–Huber / Pinsker).** For Bernoulli
KL, `p − ℓ̂ ≤ sqrt( KL(ℓ̂‖p) / 2 )`. Dividing by m and substituting the KL form gives
Theorem T09-B. ∎ (all steps parent-owned; the assembly is textbook — Alquier 2021
Thm 2.4-style route.)

**Self-contained remark.** Setting `ρ = ρ_0` (no learning) recovers a plain
concentration statement for the flat bias, and the theorem holds *uniformly over the
learning rule*, which is why "any heritable search transformation that outputs a
mixture" is covered without further assumptions on U.

---

## 4. OCM specialization (the registry's `ocm_residual`)

**S1 (finite-kernel KL collapses to log K).** With `Q_0 = Unif{1..K}` over kernel
indices, `KL(Q_ρ‖Q_0) = Σ_k ρ_k ln(ρ_k K) = ln K + Σ_k ρ_k ln ρ_k ≤ ln K`, with
equality iff `ρ` is pure (`ρ = δ_k`). The ERM posterior over the mixture simplex is
pure (the empirical risk `Σ_k ρ_k ℓ̂_k` is linear in ρ, minimized at a vertex), so the
adversarial case `KL = ln K` is *attained*, not merely an upper bound:

```text
ε(m) := sqrt( (ln K + ln(2√m/δ)) / (2m) )     [worst-case slack, δ = 0.05, K = 83]
ln K = 4.4188  (K = 83 D3d cells)   ·   sibling readings: ln 50 = 3.9120, ln 64 = 4.1589
candidate-space corner: a point-mass kernel on one genotype costs ln N = 10.2606 (N = 28,584)
```

**S2 (numbers table).** `δ = 0.05`, `K = 83`, worst case `ρ = ln K`; the bound
licenses: *true D-ecology risk of the learned bias ≤ its training-ecology empirical
risk + ε(m)*. Column ρ=lnN is the same table for the most concentrated bias allowed by
the candidate census (`KL = ln 28584`).

| m (tasks seen) | ε(m), ρ=lnK=4.4188 | ε(m), ρ=lnN=10.2606 | reading |
|---|---|---|---|
| 12 | 0.6242 | 0.7956 | **zoo T2 ecology scale (LIFETIME_ECOLOGY_V2, 12 epochs / amend-5 array = 12 tasks): NEAR-VACUOUS** — a 0.62 additive guarantee on a [0,1] loss pins almost nothing (2.78× the bar) |
| 104 | 0.22393 | 0.27969 | **crossover m\* = 104: first m with ε(m) ≤ 0.224507 (the admission bar itself)**; below m\* the guarantee is coarser than the zoo's own quality predicate |
| 564 | 0.09998 | 0.12319 | **crossover m\* = 564: first m with ε(m) ≤ 0.1** at the pure-kernel budget |

Machine-verified in `check_bound_v1.py` part (d); crossovers by grid search over m.

**S3 (vacuity range, honest status).** At the zoo's actual scope the bound is
`BOUND_DERIVED_VACUOUS_AT_SCOPE`: ε(12) = 0.62 vs a quality gate at 0.2245 — the
guaranteed slack is 2.78× the quantity the zoo calls "admissible". The bound first
becomes comparable to the zoo's own admission bar at m = 104 tasks and reaches
0.1-slack at m = 564 tasks, both far beyond any single amend-5 array (12 tasks). This
is a property of the parent bound at this KL budget, not a defect to be tuned away:
the lever that moves it is a *smaller* information budget (learning rules with
ρ ≪ ln K, e.g. heavily tempered posteriors) or more tasks — a #151/PR-scale design
choice, P4, not derivable here.

**S4 (what Baxter owns in the framing).** Baxter JAIR 2000 proves bias-learning rates
for environments of related tasks with a *controlled family* of hypothesis spaces; our
finite-kernel family is exactly his finite-`|H|` specialization, his "bias learned on
sufficiently many tasks generalizes" is our ecology-D statement, and his controlled-
family assumption is our registered finite `{Q_k}`. Nothing here extends his model to
arbitrary domains.

---

## 5. What the bound licenses and does NOT license (claim ceiling)

Licenses, at scope, all four jointly:
1. The guarantee is **only about the registered ecology D** (i.i.d. task resampling
   from the same finite D). It bounds D-distribution generalization of a learned
   mixture vs its own empirical risk.
2. It is **uniform over learning rules** — no assumption on U, the heritable update.
3. It holds **simultaneously for all mixtures** (KL form), so post-hoc selection among
   biases is covered at the price of the selected bias's KL.
4. Constants are explicit and each step is parent-attributed (§3).

Does NOT license (each is a removed assumption, not a caveat):
- **Out-of-ecology transfer**: nothing for `D' ≠ D`. Harmful transfer on an unseen
  ecology is NOT ruled out and in fact occurs — see
  `NEGATIVE_TRANSFER_COUNTEREXAMPLE_V1.md` (exact +0.5 excess burden vs the flat
  prior). The bound and the counterexample are consistent: the bound holds on D_train,
  the failure is on D_test.
- **Unbounded burden**: the geometric proposals-to-first-admission burden `1/Q(A_τ)`
  is unbounded; no statement here covers it (truncation would be a new theorem, not
  this one).
- **Any "experience helps" claim**: ε(m) only *limits deterioration*; a bound of the
  same family upper-bounds excess burden, it does not certify improvement. "Learned
  bias reduces future burden on real systems" remains P4 (#151/#217 continued-vs-reset
  experiments).
- **Ecology drift**: D fixed; regime change invalidates the i.i.d. premise entirely
  (this is the T14-adjacent honest limit).
- **Verifier soundness**: `Adm` is assumed correctly evaluated (`V_t`, definition §1 —
  soundness is an assumption of C, never a theorem of HST).

Status: `BOUND_DERIVED` (parent-sufficient mathematics, OCM-specialized, vacuity range
reported). Terminal vocabulary per FREEZE: this row supports
`HST_TRANSFER_BOUNDS_SUPPORTED_AT_REGISTERED_DISTRIBUTION` — and only at it.
