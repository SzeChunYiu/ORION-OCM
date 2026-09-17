# E9 theorems — exec-cost rank revival

All statements are at the registered scope of FREEZE_E1.md (frozen v1/v2
grammar, enumerator, count metric, EXEC-B per-op model, κ=1, K charged in
count-symbols as frozen in v2). Every identity below is additionally
machine-checked by the receipt (`affine_checks`, `checks`, hostiles) and the
independent oracle.

## T-E1 (dispatch decomposition)

For a macro library L with acyclic dependency order m_1..m_d and any integer
ρ ≥ 0, define `opcost_ρ(m) = ρ + Σ_{s ∈ body(m)} opcost_ρ(s)` with base
opcost 1 (the frozen EXEC-B model), and the dispatch count
`D(m) = 1 + Σ_{macro s ∈ body(m)} D(s)`, `D(base) = 0`. Then for every macro
and every ρ:

```text
opcost_ρ(m) = |Expand(m)| + ρ · D(m)
```

**Proof.** Induction on the admission order. A flat body (all base symbols)
has opcost ρ + |body| = |Expand| + ρ·1. If body(m) contains macros m_{i}
(i < k), then by the inductive hypothesis
opcost_ρ(m) = ρ + Σ_i (|Expand(m_i)| + ρ·D(m_i)) + #base(m)
= |Expand(m)| + ρ·(1 + Σ_i D(m_i)) = |Expand(m)| + ρ·D(m), since expansion is
additive over the body and every base symbol contributes 1. ∎

**Corollary (affinity in ρ).** For every program p and target suite,
`exec_ρ(p) = exec_0(p) + ρ · Σ_s D(s)`, so every exec burden, and hence every
exec Net, is an exact affine function of ρ. This licenses the closed-form
break-even `ρ† = ceil(−Net(0)/Net(1)−Net(0))` with two-point verification
(receipt `inv_breakeven_exact` fields; brute-scan agreement asserted by test).

## T-E2 (flattening invariance and the exact exchange law)

Let L be a library, L̂ its flattening (each body replaced by its full base
expansion, names/order/cardinality unchanged), and more generally let two
members of NFAM(L) differ only in the flat/nested choice of bodies.

1. **Count-invariance.** For every target w, the canonical enumerator visits
   under L and L̂ the same sequence of description lengths, and the first-hit
   program under L̂ is the symbol-wise image of the first-hit program under L
   (their step-wise expansions coincide because the alphabets, canonical
   order, and per-symbol expansions are identical). Hence
   `B_{G0∪L}(w) = B_{G0∪L̂}(w)` for every w, and
   `Net_count(L̂) − Net_count(L) = K(L̂) − K(L) =: ΔK`.
2. **Exchange law.** By T-E1 the per-symbol exec cost differs only through
   dispatch: for a symbol m, `opcost_ρ^L̂(m) − opcost_ρ^L(m) = −ρ(D_L(m)−1)`
   whenever the corresponding rung flattens m's body (else 0). Summing over
   every visited program and every symbol occurrence, with
   `V_m = Σ_{visited p} #m-occurrences in p`:
   `Net_exec(L̂, ρ) − Net_exec(L, ρ) = −ρ Σ_m (D_L(m)−1)·V_m + ΔK =: −ρ·ΔD·V + ΔK`.
   The K-charges are ρ-independent by the frozen accounting.

The receipt asserts this identity exactly for every same-macro-set pair in
NFAM(L_inv) on v1ref/c3/c4/c5 at ρ ∈ {1,2,4} (all pairs exact), and HEXR-2
shows a single ±1 opcost perturbation is detected by the identity (tamper
evidence). ∎

**Consequence (flatten dominance, rung ladder).** Un-nesting one level
strictly improves the exec net iff `ρ·ΔD·V > ΔK`, and strictly worsens the
count net by exactly ΔK. On every battery corpus at ρ ∈ {1,2,4} the
inequality holds at every rung (the ladder is monotone), so the exec-argmin
rung is the full flattening and the count-argmin rung is the nested end
(min-K) — the "library instance adapting to the cost model".

## T-E3 (exec-MDL degeneracy)

Under EXEC-B accounting, the exact analogue of the v1 charged corpus
compression gain for admitting candidate u (occurrences o, over the current
alphabet) with the definition charged as exec(body)+κ is

```text
gain_execMDL(u) = −ρ·o(u) − exec_ρ(u) − κ
```

which is strictly negative for every candidate of every corpus at every
ρ ≥ 1 (asserted on all six G0 pools). **Proof.** Rewriting one occurrence of
u to the new symbol m replaces exec cost `exec_ρ(u)` by
`opcost_ρ(m) = ρ + exec_ρ(u)`, i.e. adds ρ per occurrence; the definition is
executed once, costing `exec_ρ(u) + κ`. Total change:
`o·ρ + exec_ρ(u) + κ > 0`. ∎

Hence the exec-accounting corpus-MDL invention problem has the empty library
as its unique optimum: the exec benefit of a library is entirely
enumeration-horizon-side (hit-length shortening), never corpus-exec-side.
This is why the correct revival instrument is the post-invention rung
refinement (EXR-7), not a re-derived invention rule.

## T-E4 (charge-class forcing; the rung-2 negative)

Within the frozen charge class
Φ ∈ {count, exec, max, sum, countdisp} (freeze §2), on each battery corpus
the greedy first admission is forced:

- v1ref: `o(ab)·(2−1) = 11 > o(abab)·(4−1) − (Φ(abab) − Φ(ab))` because every
  Φ in the class satisfies `Φ(abab) ≥ Φ(ab) + 2` (each charge component is
  nondecreasing in the body's symbol count and exec cost, and abab's exceed
  ab's by 2 in both) — so gain(ab) > gain(abab) strictly.
- trap1: bcbc (savings 12 vs abab's 6 with Φ(bcbc) − Φ(abab) = 0 for all
  base-body charges... in particular gain(bcbc) ≥ gain(abab) with equality
  only for Φ_sum, where the tie-break expand-word order prefers 'bc' over
  'bcbc' — either way a trap body is admitted first).
- trap3: abc (savings 12 vs 6; forced).

After the forced first admission, the corpus rewrite destroys the reusable
mass that the both-metric-optimal witness needs (trap1: 'bcbc' consumes the
bcbc-programs; v1ref: 'ab' consumes the literal 'abab' occurrences — the
#978 trap3 admission-order externality), so the witness bodies are no longer
candidates and no sequential continuation reaches them. Machine check: the
five paths on all six corpora are computed in the receipt; none yields a
library with 0/200 strictly-better under both metrics at its own cardinality
on all six corpora (the count charge yields the recursive library, which
loses 19/200 under exec on v1ref; the exec/max charges stop at {ab} on v1ref,
which is both-rank-1 only at a shrunk cardinality with a 42,385-op worse
count net — refusing depth is not repair). ∎

## T-E5 (both-metric rank-1 witness; the rung-1 negative)

The exec-argimal library on every battery corpus is FLAT, not recursive:

- On v1ref the full frozen space (47 libraries) has exec-argmin
  {ab, abab} (net −396,644 at ρ=1, and at ρ ∈ {2,4}); the count-argmin is the
  recursive INV-1 library (−48,739); the frontier is exactly the two net
  points. By T-E2 any recursive library is exec-dominated by its flattening
  whenever ρ·ΔD·V > ΔK — which holds at every rung on every battery corpus
  (the hit programs themselves contain the deep macros, so V_m ≥ 1 per level
  and the enumerated volume dominates the ΔK offsets). The strongest rung-1
  claim ("recursive libraries optimal under both accountings") is therefore
  FALSE, earned-by-counterexample, and the correct strongest claim is the
  ladder: the flat rung is rank-1 under BOTH metrics (0/200 strictly better
  on each) on every battery corpus, with ties exactly the identity draws
  where the witness is pool-drawable (v1ref 19, trap1 4, trap3 16) and
  strict margins where it is not (c4/c5: the W·c·W bodies are not corpus
  subwords). The witness extends the exec break-even from 164 to 314 on
  v1ref (5→53 on trap1, 1→41 on trap3). ∎

## Scope notes

- Rank-1 statements are ensemble-relative to the frozen NULL-3 (200 seeds,
  equal cardinality, frozen hash); optimality statements are relative to the
  frozen spaces (full on v1ref/trap1/trap3; top-T closure on c3;
  NFAM-chain-only on c4/c5 — no closure claim is made there).
- The v1ref strict-domination impossibility: under exec at ρ=1 no library in
  the full space strictly dominates all nulls (0 strictly better AND 0 ties),
  because the exec-argmin lies inside the null pool; ties are intrinsic to
  the metric, reported exactly.
- trap1/trap3 extend the #978 admission-order-trap finding to exec
  symmetrically (52/49 resp. 33/33 nulls beat the compression arm under
  count/exec); the both-metric argmin exists there and is unreachable by
  every charge-class rule (T-E4).
