# Probability-prior-free information and robust decision V7

Read [FREEZE_V7.md](FREEZE_V7.md). This repair establishes a positive
information-order theorem and its converse under explicit decision assumptions.
It specializes established parent decision theory; no novelty is claimed for
Blackwell comparison, minimax or the value-of-information principle.

## 1. Declared model and full-profile transport

Let W and A be nonempty sets of worlds and actions. A deterministic signal
f:W->S is observed before choosing an action. Its admissible policies are
**all** maps pi:S->A, unless a restriction is stated separately. Fix the same
loss L:W x A->R for every compared signal. World, action, signal, loss and
policy semantics are supplied assumptions. No probability distribution over W
is needed. Loss minimization itself is an objective choice.

Say fine f1 refines coarse f0 when f1(u)=f1(v) implies f0(u)=f0(v).
On realized fine labels there is consequently a well-defined map h with
f0=h composed with f1: set h(f1(w))=f0(w). Equal fine labels make this assignment
unambiguous. Choose any w0 in W to set h=f0(w0) on unrealized labels.
This is a set-theoretic construction; infinite spaces need not provide a
computable h, or a measurable one if measurable policies are required.

**T1: exact profile inclusion.** For every coarse policy pi0 define
pi1=pi0 composed with h. Then pi1(f1(w))=pi0(f0(w)) for every w; hence their
complete loss profiles agree. Therefore every attainable coarse loss profile
is attainable under fine information. In particular, for any pointwise bound
b:W->R, coarse attainability of L(w,pi0(f0(w)))<=b(w) implies fine attainability.
Proof is substitution, world by world. No averaging or scalarization is used.
This statement is valid for arbitrary W and for any ordered loss domain.

The operational condition with restricted policy classes Pi0,Pi1 is
pi0 composed with h in Pi1 for every pi0 in Pi0. It must be checked, not
inferred from more signal labels. Resource-constrained policies additionally
require an implementation and charged cost for the decoding map h.
Classical choice in the general proof is not an efficient decoding algorithm.

## 2. Finite minimax value and exact block formula

Now assume W,A finite and nonempty, with finite real losses. Discard unrealized
signal labels; this changes no profile and leaves a finite policy space. Define

V(f,L) = min_pi max_{w in W} L(w,pi(f(w))).

Both extrema exist. Let P_f be the nonempty fibers of f. Then

V(f,L) = max_{B in P_f} min_{a in A} max_{w in B} L(w,a).       (1)

Proof: every policy assigns one action per fiber, and its worst loss in that
fiber is at least the fiber's minimum over actions. Thus its global worst loss
is at least the right side. Conversely choose a minimizing action independently
for each fiber, which is allowed because all maps are admissible. The resulting
policy attains the right side. QED.

**T2: minimax monotonicity.** If f1 refines f0, then V(f1,L)<=V(f0,L).
Transport a minimizing coarse policy with T1 and compare against the minimum
over all fine policies. Equality is allowed; extra distinctions need not help
the particular task. Equation (1) also proves the bound independently.
For infinite sets one can instead use infimum/supremum with declared
extended-real conventions; neither attained minima nor (1) follows unchanged
without the necessary choice, approximation and existence conditions.

## 3. Complete characterization by binary decision problems

**T3.** For deterministic signals on finite nonempty W, these are equivalent:

1. f1 refines f0.
2. For every two-action loss L:W x {0,1}->{0,1},
   V(f1,L)<=V(f0,L).
3. Every binary target solvable perfectly from f0 is solvable perfectly from f1.

The forward implication follows from T1/T2. Conversely, failure of refinement
supplies u,v with f1(u)=f1(v), f0(u)!=f0(v). Define the binary target
t(w)=1 if f0(w)=f0(u), and t(w)=0 otherwise; let
L(w,a)=0 if a=t(w), and 1 otherwise.
The coarse rule testing whether its signal equals f0(u) has loss zero everywhere.
Any fine rule chooses the same action at u and v, whose required targets differ,
so it incurs loss one in at least one of them. All losses are at most one;
therefore V(f0,L)=0 and V(f1,L)=1. This contradicts either 2 or 3. QED.

The zero-threshold characterization and separating witness also hold on arbitrary
nonempty W as set-theoretic statements: the displayed coarse rule exists and
every fine rule fails at one of two specified worlds. Neither an enumeration of
W nor a distribution is used. The theorem characterizes deterministic information
partitions, not the entire stochastic Blackwell order or a unique task objective.

## 4. Paid information

Charge a constant c>=0 in the same scalar loss units for acquiring and processing
f1, with baseline f0 cost set to zero (or absorb a common baseline charge).
The optimized charged value is V(f1,L)+c, since c is independent of world and
policy. Write Delta=V(f0,L)-V(f1,L), nonnegative under refinement. Then:

- information strictly improves the charged value iff c<Delta;
- it ties iff c=Delta;
- it worsens iff c>Delta.

Subtract V(f1,L) to prove all three. Zero-cost information weakly improves and
strictly improves only when Delta>0. World-dependent or policy-dependent charges
must remain inside the objective; adding their maximum to the uncharged value
is generally only a bound. Vector resources do not become this scalar charge
without an explicit aggregation choice. Charges must include the relevant
acquisition, decoding, action and validation costs before practical deployment.

## 5. Randomization is a different policy class, not a world prior

For W=A={0,1}, constant signal, and matching loss 1[a!=w], every deterministic
policy has worst loss 1. A randomized policy outputs 1 with probability p.
Its expected losses at worlds 0 and 1 are p and 1-p, so worst expected loss
is max(p,1-p)>=1/2, attained at p=1/2. Full revelation permits zero loss.
The fair coin is the agent's randomization distribution, not a belief or prior
over worlds. Hence the paid-information improvement is 1 for deterministic
policies but 1/2 for randomized policies in this same example.

This randomized guarantee assumes the adversary chooses a world without seeing
the realized random action. If it can choose the opposite world after seeing
that action, loss is 1 on every play: sup_w E_coin differs from
E_coin sup_w. With fixed deterministic policies the world may be worst for the
known policy, but must remain consistent with the signal already observed.

A further boundary: a constant signal can be stochastically garbled into an
independent fair coin. A deterministic function of that coin supplies randomized
actions with worst expected matching loss 1/2, whereas a deterministic function
of the constant signal has value 1. Thus a stochastic-garbling simulation needs
closure under randomized decision rules. Deterministic refinement uses an actual
function h; we do not substitute a stochastic channel for h in T1.

## 6. Falsifiers and validity conditions

- A noisier channel or a larger label alphabet is not a refinement witness.
  Check every same-fine pair and explicitly construct h.
- Removing actions or constraining fine policies can prevent the transported
  policy. Compare identical action sets and policy classes, or prove closure.
- Changing the loss table between experiments changes the decision problem;
  information ordering alone then supplies no value comparison.
- Omitting a possible world restricts the guarantee to the declared W.
  Finite reconstruction does not learn or validate that world model from data.
- Signal labels must be opaque identifiers. Arbitrary bijective relabeling
  should transport the policy and preserve every loss profile.
- Sequential control, observation interventions and adversarially changing
  worlds require an explicit causal/timing model. Static minimax does not prove
  dynamic consistency for an arbitrary multiple-prior process.
- Wrong charges or free decoding can reverse the paid comparison. Test
  zero cost, a strict improvement, equality and strictly excessive cost.

## 7. Evidence levels and programme placement

InformationOrderV7.lean imports Std and proves arbitrary-world profile transport,
natural-number threshold inclusion, an attained/minimal minimax implication,
the exact binary zero-threshold converse, and the integer cost crossover.
It uses classical choice for off-image signal handling. It does not prove a
computable infinite decoder. Finite real-valued extrema and (1), the resulting
full real-valued minimax characterization, and the continuous randomized
calculation above are complete paper proofs, not additional kernel declarations.

The finite experiment exhausts the frozen 729 loss tables and five partitions.
Its separate policy-enumeration and blockwise routes test the same exact
mathematical problem. Binary counterexamples must actually run; refinement
transport must preserve whole profiles. These finite results do not replace
the arbitrary-set proof or establish empirical generalization.

This locally advances GMI2-R9-002/008 and GMI2-R10-001/002/005; it supplies a
decision meaning for conditional attainability without a probability prior.
Worlds, objectives, observations, action and policy availability remain assumed.
Original atoms, historical receipts and unresolved dependencies retain their
authority boundaries. Full R0-R17 or all-family machine-intelligence closure
is not earned by this repair. Parent attribution is in PARENTS_V7.json.
