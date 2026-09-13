# PR568 learning/memory review

Scope: read-only mathematical review, no execution or source modification.
Reviewed commit: `6e879c5f7c0fa59e8bdded6dcb1b67d16a86d5ac`.
Both paths are under `research/gmi-recursive-theory-closure-v1/`:

| Source | SHA256 |
|---|---|
| FORMAL_LEARNING_MEMORY_THEORY_V1.md | `4b3576e6d0873d0ffc540f56aeeb3d707d2d49c3016759a1071fe271022ac79d` |
| test_learning_memory_v1.py | `0954de6c013b6c1a7c98128ee05e55601f0477ea51a8f556508978732b6e102a` |

Comparison authority: accepted formal unit commit
`1858f7b95e583ad5ca44c85bd1e2e34976093b27`, particularly LEARNING,
MEMORY, REPRESENTATION and COMPOSITION. That unit remains unchanged.

## Verdict

The fixed-class ERM inequality and the intended indistinguishability/forgetting
arguments are valid. The following wording/quantifier repairs are needed for
precise integration. They do not establish a counterexample to the properly
qualified classical theorems. No new empirical or novelty claim is supported.

## R1: one-sided regret versus exact equality (lines74–80)

The displayed definition requires signed average regret to converge exactly
to zero. It is stronger than a one-sided guarantee of performing no worse
asymptotically than the best fixed comparator.

Concrete distinction: two fixed experts suffer alternating losses (0,1) and
(1,0). A causal policy knowing the deterministic alternating schedule chooses
the zero-loss expert each round. At every even T its loss is0 and each fixed
expert's loss is T/2, so sup_h Reg_T(h)/T=-1/2. This violates the displayed
equality despite outperforming every comparator.

Repair: use limsup_T sup_h Reg_T(h)/T<=0, equivalently convergence to zero
of the positive part, with the probability/expectation mode explicitly fixed.
Alternatively retain equality and name it the stronger zero-average-regret
convention; do not infer it from a sublinear upper bound alone. The external
parent [Hazan, Introduction to Online Convex Optimization](https://arxiv.org/abs/1909.05207)
provides upper regret guarantees; the signed-sequence distinction above is
an explicit arithmetic counterexample, not a claim that all literature uses
one terminology.

## R2: complete transcript and terminal-output law (lines191–193)

The proof requires equality of the joint law of everything the terminal
decoder can use, including initial information, actions and revealed private
randomness, or an equivalent common conditional decoder kernel. Equality of
individual observations or their marginal laws is insufficient.

Boundary counterexample: a fair private bit B chooses A=B; world b returns
Z=A xor b. Z is marginally fair in both worlds, but the learner decodes
b=A xor Z perfectly. The complete (A,Z) law differs, so this does not refute
the intended complete-transcript theorem. State that premise directly.

For a claim over all learners/policies, require indistinguishability for each
policy in that class. Indistinguishability only under one nonexploring policy
cannot rule out a different policy that observes the distinguishing action.

The proof's exact success identity1-q silently assumes binary total output.
If abstention/other outputs are allowed, let q_i be the common probability of
terminal output i. Then q_0+q_1<=1 and min(q_0,q_1)<=1/2. This proves the
same conclusion without a binary-output or almost-sure-termination premise.

## R3: fixed class and loss before scoring (lines115–119)

Accept LMT-3 under the standard reading that H and its measurable loss maps
are fixed before the IID evaluation sample, and hhat belongs to H. State this
explicitly to prevent a data-selected-class interpretation of the bound.

Boundary counterexample to that relaxed interpretation: X is uniform[0,1],
Y=0; after observing a finite sample S choose H_S={h_good,h_S}, where h_good=0
everywhere and h_S(x)=0 on S,1 elsewhere. Both have empirical loss0. Choosing
h_S is exact ERM, but its population risk is1 versus comparator risk0 almost
surely, for arbitrary n. Fixed finite cardinality2 alone cannot pay selection.
Fresh independent evaluation or a pre-data simultaneous class bound repairs it.

## R4: the forgetting decoder's complete input (lines236–238)

Accept the collision proof for the same protected continuation and a common
decoder kernel with identical complete input in both cases. Other accessible
registers or newly distinguishing observations cannot be omitted from that
input. This matches1858 MEM1/REP3. If side information reveals the forgotten
bit, forgetting that bit locally does not prevent later exact reconstruction;
the retained-state collision alone then does not identify a decoder collision.

## Accepted remainder and executable evidence boundary

- LMT-1's three distinct evaluation notions are coherent once the regret
  convention is repaired/renamed; no universal implication is asserted.
- LMT-2's fixed evaluation and jointly attainable resource requirement agree
  with1858. Pareto/scalarized improvement are declared orders, not deductions.
- For fixed measurable H, Hoeffding gives2|H| exp(-n epsilon^2/2), so the
  stated ERM sample requirement and approximate-ERM decomposition are correct.
  Vanishing uniform deviation plus optimization error gives objective-value
  convergence in the same stated mode; it does not give parameter convergence.
- LMT-4 correctly separates convergence types; LMT-6 specifies revision duties
  without asserting a general termination/soundness algorithm for cyclic graphs.
- LMT-7's distortion/resource condition is a declared forgetting contract;
  LMT-8 and the falsifiers do not supply additional universal guarantees.
- The four tests check selected finite identities. Their inspected arithmetic
  is correct, but they neither prove the general PAC quantifiers nor test
  full transcript sufficiency or all randomized forgetting decoders.

No tests were run for this review. The264-line theorem source should also be
split when repaired to meet the repository's modular-document convention.
