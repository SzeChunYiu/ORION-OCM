# Behavioral state: quotient, sufficiency and its missing premises

Status: proved conditional representation theorems for the classical AX1–AX4
specialization. A behavioral representation is not automatically executable,
learnable, finite, or a model of an unobserved physical state.

## REP1: constructive deterministic residual quotient

Let \(A,Y\) be nonempty alphabets and let \(F:A^*\to Y^*\) be a total
length-preserving causal behavior: \(F(\epsilon)=\epsilon\), and \(F(u)\)
is a prefix of \(F(uv)\). Here \(Y\) contains all protected per-step outputs.
For a prefix \(u\), define its residual \(R_u:A^*\to Y^*\) by
\(F(uw)=F(u)R_u(w)\), and set \(u\sim v\iff R_u=R_v\).
The comparison retains the entire future behavior, not just a current answer.

**Theorem.** The classes \(Q=A^*/{\sim}\), root \([\epsilon]\), and maps
\[
\lambda([u],a)=R_u(a),\qquad \delta([u],a)=[ua]
\]
define a deterministic Mealy machine realizing exactly \(F\). It has the
fewest reachable states of any deterministic Mealy realization of \(F\).

**Proof of congruence.** If \(R_u=R_v\), their one-symbol outputs agree.
Causality gives
\(R_u(aw)=R_u(a)R_{ua}(w)\) and
\(R_v(aw)=R_v(a)R_{va}(w)\). Cancel the equal first output to obtain
\(R_{ua}(w)=R_{va}(w)\) for every \(w\); hence \(ua\sim va\).
Both maps are therefore well-defined. Induction on input length shows that
after \(u\) the state is \([u]\) and the emitted word is \(F(u)\).

**Proof of minimality.** Let another deterministic realization reach state
\(s(u)\) after \(u\). If \(s(u)=s(v)\), its deterministic continuation
from that state agrees on every word, so \(R_u=R_v\). Consequently
\(s(u)\mapsto[u]\) is a well-defined surjection from its reachable states
onto \(Q\). Thus no realization has fewer states. If its state map identifies
exactly equivalent histories, that surjection is a rooted output/transition
isomorphism. Minimality is in this machine/interface class, not in bytes,
circuit gates, inference cost, or hardware volume.

For partial legal inputs, the residual must also record its continuation
domain; add a protected illegal-input symbol and absorbing state to reduce
to the total case. Erasing legality can falsely merge states. A terminal
obligation that depends on elapsed time or past rewards requires those
coordinates in the protected interface/state before this result applies.

**Finite-index consequence.** \(F\) has a finite deterministic realization
iff the number of residual classes is finite. The reverse implication is the
construction; the forward implication is the surjection. This is existence,
not an algorithm for deciding equality of arbitrary residual functions.
[STATE-DISCOVERY](STATE-DISCOVERY.md) supplies one finite exact acquisition
procedure under a known state bound, stable outputs and paid resets.

## REP2: finite tests cannot silently replace continuation equivalence

Define \(u\sim_Lv\) by equality on words of length at most \(L\).
Then \(u\sim_Lv\) implies only \(ua\sim_{L-1}va\), not
\(ua\sim_Lva\). For every \(L\ge1\), compare an all-zero self-loop state
to a chain with \(L\) zero-output transitions followed by a one-output
transition. Their first \(L\) outputs agree; after one common input their
successors differ within \(L\) inputs. Quotienting by finite-horizon tests
therefore need not define a stationary recursive machine. An explicit
remaining-horizon coordinate repairs finite-horizon recursion; a justified
finite-state bound can instead supply a complete distinguishing set.

## REP3: stochastic state requires a controlled kernel homomorphism

Let \(H,A,Y\) be standard Borel history, action and output spaces, with
measurable history extension \(h,a,y\mapsto hay\), and a supplied controlled
kernel \(P(dy\mid h,a)\). Here \(h\) is the complete actual observed global
history, including context registers and information available to the action
selector; it does not reveal the unobserved world state. The kernel describes
an admitted controlled action, not an observational conditional from a policy.
Let \(T:H\to S\) be measurable, with \(S\) standard Borel. Augment \(T\)
with every external register \(Z\) used by the policy or protected obligation.
Include their joint updates in \(T(hay)\), expanding \(Y\) to record update
outcomes if necessary. Legal actions must factor through \(T(h)\), or be
restricted to those legal at every history represented by that same state.
Suppose there is a measurable kernel \(K(dy,ds'\mid s,a)\) satisfying
\[
\int 1_B(y,T(hay))P(dy\mid h,a)
=K(B\mid T(h),a)                                      \tag{SH}
\]
for every measurable \(B\subseteq Y\times S\) and every admitted \(h,a\).
An almost-sure version is adequate only under a stated common reference law
covering the policies in the conclusion; a different policy may visit a
previously null history. Countably generated sigma-fields let equality of
kernels be checked on a determining class with a common exceptional set.

**Theorem.** Conditional on that complete observed history and chosen action,
the next
output/state pair has kernel \(K(\cdot\mid T(h),a)\). Thus any measurable
common policy based on the augmented retained state has the same protected
path law in the reduced process, given the same initial **joint** law of
state and external registers. **Proof:** (SH) is the one-step conditional distribution
identity. Successive integration proves equality of every finite path law;
the countable path-extension argument of CMP1 proves the infinite-path claim.
Substitution inside a larger context additionally requires CMP1's actual
conditional context/interface kernels to agree. A component-local marginal
kernel is not a substitute for this joint observed-history contract.

Two exact countercontrols show why. Let a context know a fair bit \(Z\),
choose \(A=Z\), and receive \(Y=Z\). A component-local constant state with
marginal fair-output kernel predicts \(\Pr(Y=A)=1/2\), versus the actual 1:
it fails (SH) conditional on the complete history containing \(Z\). Separately,
take the exact kernel \(Y=S\). An initial coupling \(S=Z\) and independent
fair \(S,Z\) have equal individual marginals but yield equality probabilities
1 and \(1/2\) under \(A=Z\). Matching only the marginal law of \(S\)
therefore fails even when the transition kernel itself is correct.

For an executable deterministic state update, sufficient explicit premises are
\[
P(dy\mid h,a)=Q(dy\mid T(h),a),\quad
T(hay)=U(T(h),a,y)\quad P(\cdot\mid h,a)\text{-a.e.},
\]
with measurable \(Q,U\). These imply (SH) with
\(K(dy,ds'\mid s,a)=Q(dy\mid s,a)\delta_{U(s,a,y)}(ds')\).
In the general (SH) case, standard Borel disintegration supplies a conditional
kernel for \(s'\) given \((s,a,y)\) for a specified joint law; an actual
implementation additionally needs a uniformly parameterized executable sampler.
Neither regular conditional probabilities nor quotients supply that algorithm.

## REP4: an explicit predictive construction and its scope

For finite \(A,Y\), supplied controlled kernels on all finite histories
define \(p_h(v\mid u)\), the probability of output word \(v\) under the
fixed action word \(u\) after history \(h\), by successive multiplication.
The countable profile \(T(h)=(p_h(v\mid u))_{|v|=|u|}\) is measurable.
The next-output law is its one-step coordinate. Whenever \(p_h(y\mid a)>0\),
\[
p_{hay}(v\mid u)=\frac{p_h(yv\mid au)}{p_h(y\mid a)}.       \tag{PU}
\]
This identity follows by factoring the first controlled output probability.
Hence equal complete profiles have equal updated profiles for each
positive-probability observation; zero-probability updates may be assigned an
arbitrary common profile. The coordinatewise ratio is a measurable recursive
update. There are countably many finite histories, so their actual profile set
is a countable Borel subset of the cube \([0,1]^{\mathbb N}\). Use that
ambient cube as state space, the ratio update on actual profiles, and a fixed
actual profile as fallback elsewhere and at zero-probability observations.
Coordinatewise updates and this case distinction are measurable; neither a
measurable quotient assumption nor executable profile-membership test is implied.
This realizes REP3, although evaluating and storing infinitely many test
predictions is generally not an executable finite-memory operation.

Equality under one observed policy does not suffice: two environments always
output zero for action \(a\), while action \(b\) outputs zero in one and
one in the other. A policy using only \(a\) makes their observed laws equal,
but changing to \(b\) distinguishes them immediately. Supplying controlled
laws or an identified intervention model repairs the missing premise. Even
controlled predictive equivalence concerns the declared interface: it need not
identify internal hidden states or physical mechanisms.

## Parents and exact contribution

REP1 is a residual-transducer form of classical continuation minimization;
finite experiment representations are developed by
[Rivest and Schapire (1994)](https://people.csail.mit.edu/rivest/pubs/RS94a.pdf).
REP4 adapts controlled test-prediction states from
[Littman, Sutton and Singh (2001)](https://proceedings.neurips.cc/paper/2001/file/1e4d36177d71bbb3558e43af9577d70e-Paper.pdf).
Their finite linear representation conclusion uses structural/rank premises;
AX1–AX4 do not provide finite rank. The contribution here is an explicit
GMI premise-to-construction bridge and its failure witnesses, not a claim to
have newly invented state minimization or predictive state representations.
