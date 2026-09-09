# HST-T17 — External-evaluator anti-self-certification (toy) [P1 toy + P4 real]

Frozen statement (registry T17): if an optimizer can directly rewrite a scalar score
register that is itself the optimization target and no independent constraint ties the
score to protected world performance, then a score-maximizing self-change can raise
measured objective without improving protected performance. NOT a claim that external C
is sufficient for safe self-improvement.

## 1. The toy machine

A **2-register machine state** is (w, s) with w ∈ W = {0, 1, 2} (work register) and
s ∈ S = {0, 1, 2} (score register).

- **Protected performance** P : W -> W, P(w) = w (frozen, external meaning of "real
  capability"; identity for maximum readability — nothing below uses its form beyond
  being a nonconstant frozen function of w).
- **Measured objective** M(w, s) = s (the optimizer's target).
- An **update** is a map u applied to the state; an **update library** U ⊆ available
  atomic updates defines a *system*. The optimizer enumerates finite sequences from U
  and keeps the result it likes; for the theorem we only need existence of one greedy
  step, so "optimizer" here = ∃ a legal update sequence.

Two systems are compared:

### System W (writable-s) — tampering channel open

U_W = { `w := w'` for all w' ∈ W } ∪ { `s := s'` for all s' ∈ S }.

The score register is directly writable: the optimizer may execute `s := s'` as an
ordinary update. **No independent constraint ties s to P(w)**: the hypotheses of the
frozen statement hold by construction.

### System X (external evaluator) — tampering channel closed

U_X = { `w := w'` for all w' ∈ W } ∪ { `s := E(w)` }, where E : W -> S, E(w) = w
(frozen external evaluator), is **not an optimizer-controlled update**: after every
optimizer-chosen update the score register is *recomputed* by the evaluator from w
alone (equivalently: s is not a register at all but a read-only display of E(w); we keep
it as a register recomputed after every step so both systems share the state space).

## 2. Theorem (toy)

**(a) System W admits a score-maximizing self-change that raises the measured objective
while protected performance is unchanged, and one that raises it while protected
performance gets strictly worse.**

*Proof.* Initial state (w0, s0) = (1, 1). The single update `s := 2` is legal in U_W.
New state (1, 2): M rises 1 -> 2, P unchanged (P(1) = P(1)). Moreover the sequence
(`w := 0`, `s := 2`) is legal: new state (0, 2), M rises 1 -> 2 while P falls
P(1) = 1 -> P(0) = 0. Both sequences are pure register writes; neither consults w's
external meaning. The optimizer, choosing by M alone, prefers both over staying. □

**(b) System X admits no update sequence that changes s without changing w; and with
E = P (the evaluator IS the frozen protected-performance measure), every M-gain is a
P-gain.**

*Proof.* Let Δs ≠ 0 along a legal X-run. Updates in U_X either change w (then done) or
are the evaluator step `s := E(w)`, which changes s only when E(w_new) ≠ E(w_old); since
E is a fixed function, E(w_new) ≠ E(w_old) forces w_new ≠ w_old — but the only optimizer
act in U_X that alters anything is a w-write, so Δs ≠ 0 ⟹ Δw ≠ 0. With E = P, we have
M = s = E(w) = P(w) after every evaluator step, so ΔM > 0 ⟹ ΔP > 0 by identity. □

**(c) Reachability asymmetry (exact counts, see `exact/check_t17_v1.py`).** In W, from
(1,1) the tampered state (1,2) is reachable in one step and the capability-degraded
tampered state (0,2) in two (`w := 0`, then `s := 2`) — and the measured optimum s = 2
is reachable with **no w-write at all** (pure score tampering). In X, the unique
M-optimal state (w, s) = (2, 2) is reachable only through `w := 2` (followed by the
constitutional evaluator pass); enumeration over all atomic acts from every
invariant state (w, E(w)) confirms there is no legal X-act with Δs ≠ 0 ∧ Δw = 0. All
states × all updates × all length-1..2 sequences from (1,1) are enumerated
exhaustively at this scope.

## 3. What this does NOT prove (loud)

1. **No claim that external evaluation solves Goodhart in general.** In the toy,
   "protected performance" is *defined* as P(w) = E(w) — a tautological binding. In any
   real OCM, P is external world truth and E is a proxy: a w chosen to please E
   (proxy-optimizing, reward hacking, test-set overfitting) still raises s without real
   capability. The toy removes only the **direct syntactic channel** (writing the score
   register); it says nothing about *indirect* proxy capture. The real C is
   **formal-by-contract + empirical** (bounded decidable contracts per T15 escapes +
   held-out protected validation), and its independence/completeness/robustness is a P4
   hypothesis, checked campaign by campaign.
2. **No claim about collusion / corrupted evaluators.** If the optimizer can rewrite the
   evaluator itself (modify E, its tests, or its metering), System X collapses to
   System W with extra steps. C's write-protection of E, metering and adoption gates are
   *assumptions of the constitution*, not theorems of HST (definitions §1: "its
   soundness is an assumption of C, never a theorem of HST").
3. **No quantitative claim.** Toy scope: |W| = |S| = 3, P = E = identity, one greedy
   step. Larger state spaces, stochastic evaluators, partial observability of w — all
   outside this proof.

## 4. Artifacts

- Exact enumeration certificate: `exact/check_t17_v1.py` (runs on billy-laptop;
  enumerates all states × all updates for both systems; asserts (a), (b), (c) above).
- Concrete tampering witness (the §11 hostile "self-modifier that raises mutable score
  without protected capability"): `hostiles/T17_TAMPER_WITNESS.json`.
