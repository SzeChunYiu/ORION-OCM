# Distribution-free robust decision repair — #1068, round G

Baseline branch head: 71f59be1253c15a8b7622c0c0b0443369a9a6050.
Round G merges only after round F and reconciliation against main.
No successor implementation or test outcome exists at this freeze commit.

## Positive theory to establish and falsify

Declare worlds W, actions A, deterministic observations f, a loss L and
admissible decision rules. No probability distribution over W is supplied.

If f1 refines f0 (equal fine signals imply equal coarse signals), construct the
coarse rule from the fine signal and prove preservation of its complete loss
profile. Infer inclusion of robustly attainable thresholds. Under finite
nonempty W,A and all deterministic policies, infer minimax monotonicity.

Prove the converse characterization using all binary-action, binary-loss
decision problems: universal weak minimax improvement forces signal refinement.
A merged pair of worlds with different coarse labels must yield a separating
decision problem. State domain/nonemptiness/attainment assumptions explicitly.

For a constant observation cost c>=0, derive the exact improve/tie/worsen
conditions comparing V(f1)+c with V(f0). Test changes of action availability,
policy class, loss table, world model and randomization as boundaries; do not
import stochastic Blackwell claims from a deterministic signal theorem.

## Executable evidence frozen before implementation

Exhaust all 729 three-world/two-action loss tables with entries in {0,1,2}
and all five partitions of the three worlds. Compare complete policy enumeration
against independent blockwise max-min calculation. For all ordered partition
pairs, compare refinement against universal weak dominance across the table set.
Construct and execute a binary-loss witness for every nonrefinement pair.
For refinements, transport each coarse policy and compare its pointwise profile.

Check relabelings, positive rescaling/offsets, paid-information crossover/ties,
restricted-action and restricted-policy controls, changed worlds/losses,
deterministic-versus-randomized binary matching, malformed inputs and mutated
certificates. No empirical generalization or full-information learning from
samples is inferred from this exact finite reconstruction.

## Formality and authority

Use primary decision-theoretic sources; these are standard parent-owned
information-order/minimax ideas applied to the GMI assumptions ledger.
Kernel-check feasible policy-transport and converse statements in Lean 4.19.0;
separate any remaining paper proof from executable finite evidence.

World set, actions, observations, loss, policy class and resource costs remain
external assumptions. A result without a probability prior does not remove
those premises or decide all machine intelligence. Preserve original atoms,
earlier frozen bytes, UNKNOWN and all stale scientific dependencies.
Independent internal hostile review, normal/optimized replay and exact-head CI
must pass. Retain this freeze by ancestry-preserving merge.
