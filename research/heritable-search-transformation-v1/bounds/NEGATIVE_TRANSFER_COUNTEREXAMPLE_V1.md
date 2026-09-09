# HST Negative-Transfer Counterexample V1 (lane D, D6 — HST-T09 hostile)

Issue #233 §11 bullet: "learned bias trained on unrelated tasks causing negative
transfer" — the nearest-false-generalization witness for `HST_TRANSFER_BOUND_V1.md`.
Minimal two-ecology finite world, **exact by enumeration (no simulation)**; every
number is a rational computed by hand and machine-verified in `check_bound_v1.py`
part (b) with `fractions.Fraction` arithmetic.

## 1. The world W- (two ecologies, anti-correlated structure)

```text
Candidates:      X = {a, b}                      (N = 2)
Kernels:         Q_a = δ_a,  Q_b = δ_b           (K = 2 point-mass proposal kernels)
Flat prior:      Q_0 = ½ Q_a + ½ Q_b  = Unif(X)  (the do-nothing bias)
Tasks/ecologies: τ_A with admissible set A_{τ_A} = {a}
                 τ_B with admissible set A_{τ_B} = {b}      (disjoint / anti-correlated)
Loss (frozen):   ℓ(Q,τ) = 1 − Q(A_τ) ∈ [0,1]     (admission-failure probability)
Train ecology:   D_train = δ_{τ_A}   (m tasks, all τ_A)
Test ecology:    D_test  = δ_{τ_B}   (the unseen ecology)
Learning rule:   ρ = ERM over the mixture simplex on the training sample
```

ERM here: empirical risk of mixture `ρ` on m copies of `τ_A` is `ρ_b` (loss of `Q_a`
is 0, of `Q_b` is 1, linear in ρ), minimized at the pure vertex `ρ = δ_{Q_a}` — the
rule learns "propose only a". Ties impossible: the two empirical losses differ.

## 2. Exact numbers (Fractions, no floats)

| quantity | learned `Q_ρ = δ_a` | flat prior `Q_0` |
|---|---|---|
| `E_{D_train}[ℓ]` (train risk) | **0** | ½ |
| `E_{D_test}[ℓ]` (test risk, ecology τ_B) | **1** | ½ |
| test excess vs flat prior | **+1 − ½ = +½** | — |

**Negative transfer, exactly:** the learned bias has expected admission-failure
probability `1` on the test ecology vs `1/2` for the bias that ignored all experience
— the inherited structure `H` (here: the learned pure kernel) **doubles** the
probability-of-failure burden. In burden terms: flat prior admits within 2 proposals
in expectation (`1/Q_0(A_{τ_B}) = 2`); the learned bias proposes `a` forever and never
admits (`1/Q_ρ(A_{τ_B}) = ∞`; truncated loss form caps at 1). Every value above is a
dyadic rational; part (b) of the checker recomputes them as `Fraction(1,1)`,
`Fraction(1,2)` and asserts equality.

**Minimality:** with one candidate, one task, or one kernel there is nothing to
mis-learn (the mixture space is a point or the loss is constant); two candidates,
two tasks, two kernels is the smallest world in which a learning rule can place full
mass on a wrong structure. `m` is irrelevant (any m ≥ 1 gives the same ERM output),
so this is not a small-sample artifact.

## 3. Why this does not contradict Theorem T09-B (the pairing)

The bound's premise is that train and test tasks are drawn from the **same** D. On
`D_train` the theorem holds trivially and is verified exactly in the checker: for
every m ≥ 1 and every δ-grid point, the exact sample-space violation probability is 0
(the empirical loss is 0 and `E_D[ℓ(Q_ρ)] = 0`, so the inequality `0 ≤ 0 + ε` never
fails). The failure is **entirely** at the removed assumption `D_test = D_train`:

- remove "same ecology" → this counterexample (+½ excess, Sec. 2);
- keep it → Theorem T09-B (bound on D-excess burden).

That is the whole content of the registry's "No theorem over arbitrary future
domains" clause, made numerical. It is also the exact formal shadow of #151's
"related/unrelated/harmful transfer" measurement axis: "unrelated" is
`D_test ⊥ D_train` (here: disjoint admissible sets), and the harm is bounded by the
loss range (`+½` of the maximal `+1` on this world) — nothing smaller is provable
without relatedness assumptions, because this world exists.

## 4. Claim ceiling (binding)

This witness licenses exactly: *"bias learned under one registered ecology can be
strictly worse than the flat prior on a different ecology, by up to the full loss
range; no PAC-Bayes/Baxter-family statement constrains out-of-ecology transfer."*
It does NOT license: "learning usually harms transfer" (here harm is an artifact of
anti-correlation; under `D_test = D_train` the bound controls excess), nor any
quantitative claim about real #217/#221 lineages — detecting regime change and gating
adoption of inherited bias is the empirical (P4) programme of #151/#149 (`C`-level
adoption gates), not a theorem.
