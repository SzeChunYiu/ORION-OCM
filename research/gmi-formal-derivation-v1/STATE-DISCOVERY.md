# Acquiring state and support instead of assuming them supplied

Status: constructive exact bounded-state learning and conditional statistical
support recovery. These discharge particular state/support premises; neither
claims to learn an arbitrary world's true state from unrestricted experience.

## SD1: a finite experiment set identifies an unknown transducer

Assume a total deterministic Mealy machine with unknown transition/output
tables, at most \(m\ge1\) reachable states, finite nonempty input alphabet
\(A\) and output alphabet \(Y\). Its initial state can be restored by an
admitted reset. Each executed word returns its exact output word. The known
bound, truthful interface, stable machine and reset behavior are substantive
premises; the learner is not given the transition table or state identities.

**Distinguishing lemma.** Two rooted machines with \(n_1,n_2\) states either
agree on all words or differ on a word of length at most \(n_1n_2\).
**Proof.** Choose a shortest word whose last step first exposes different
outputs. Before its successive symbols the pair of current states cannot
repeat: deleting the loop between two identical state pairs would preserve
the differing last output and produce a shorter witness. There are at most
\(n_1n_2\) state pairs, so the word length is at most that number.

**Sharper distinguishing lemma.** The bound improves to \(n_1+n_2-1\).
Take the disjoint union of both state sets, with \(N=n_1+n_2\), and let
\(R_k\) identify states agreeing on all output words of length at most \(k\).
\(R_0\) is universal. Define \(R_{k+1}\) by equal next outputs on every
input and \(R_k\)-equivalent successors. This proves the word interpretation
by induction. If a refinement is strict it increases the number of blocks;
if it is unchanged, its recursive definition makes every later refinement
unchanged. Starting at one block, there can be at most \(N-1\) strict
refinements. Thus \(R_{N-1}\) is stable and identifies exactly full future
equivalence. Any inequivalent roots differ by depth at most \(N-1\).

**Algorithm.** Set \(D=2m-1\). Reset and query every word of length exactly
\(D\). Its output prefixes supply all shorter queries: each shorter input
has an extension to length \(D\) because the alphabet is nonempty.
Enumerate labeled rooted Mealy machines in increasing state count up to \(m\);
stop at the first candidate matching every returned word, then minimize it by
continuation equivalence as in REPRESENTATION. This uses one candidate table
at a time. If a matching machine had fewer reachable states, its trimmed
rooted copy would occur earlier in the enumeration.

**Theorem.** The retained machine is behaviorally equivalent to the unknown
machine from corresponding roots on all finite and infinite input streams,
and its reachable residual
state is a sufficient recursive state for that protected input/output law.
**Proof.** A labeled copy of the target is in the finite enumeration, so the
consistent set is nonempty. If a retained candidate differed from the target,
the sharper lemma would supply a disagreement of length at most \(2m-1\),
already queried directly or as a prefix, a contradiction. Equality of every finite output prefix yields
equality of the deterministic infinite stream. Continuation minimization
preserves all words and gives the residual state construction. The acquired
table depends on observations and is used to compute later outputs; it is
executable learned structure, not a text description of a hidden state.

This known bounded exact-learning construction uses a different interface from
L* and its membership/equivalence-query model. It needs no equivalence-query oracle because a state bound gives
an exhaustive finite conformance set. It may be very expensive.
Writing \(a=|A|,b=|Y|\), the query count is
\(Q=a^{2m-1}\), executed input/output symbols
\(S=(2m-1)a^{2m-1}\), and a labeled candidate bound is
\(N=\sum_{n=1}^m n(nb)^{na}\). Brute-force candidate comparison executes at
most \(NS\) candidate transitions, beyond \(Q\) real resets and \(S\)
real queried transitions. Before deployment, restore the physical target's root
with one additional paid reset (\(Q+1\) total), or transport the learned state
by replaying the known final query word and charge that work. An untracked
post-acquisition target state is not the common initial state used by the proof.
Store the transcript and one candidate table, then
charge enumeration, minimization, counters, symbol storage and final deployment.
These logical counts do not stand in for measured hardware costs.

**Counterexample and repair.** Without a known state bound, any finite queried
set has maximum length \(L\). With at least two output symbols, a one-state
all-zero machine and a chain that
first emits one after \(L+1\) symbols agree on all acquired data. No exact
finite stopping certificate covers both. Supplying the state bound restores
SD1; alternatively certify only a finite horizon or a probabilistic obligation.
Unreliable resets similarly invalidate the fixed-root experiments; include the
reset state in the model and prove a valid control protocol before applying SD1.

## SD2: finite support recovery with a known positive-mass floor

For a born row with a complete declared outcome alphabet of integer size
\(b\ge1\) containing its true support, suppose
each next visited outcome has the same conditional distribution \(p\) given
the full global past. Visits are chosen predictably before outcomes. At birth,
the complete alphabet, \(b\), \(0<p_{\min}\le1\), and \(\alpha\) are fixed
measurably from the birth history. Each coordinate of the fixed row law
is either zero or at least \(p_{\min}\). The allocation satisfies \(0<\alpha<1\)
before scored observations; other rows and the visit schedule may be dependent.
Set
\[
n_0=\left\lceil\frac{\log(b/\alpha)}{p_{\min}}\right\rceil.
\]
After \(n_0\) attained visits, declare the observed outcome set to be support.

**Theorem.** The event "this declaration occurs and is incorrect" has
probability at most \(\alpha\), conditional on the birth history.
**Proof.** Zero-probability outcomes are observed with probability zero over
countably many visits. For a positive coordinate \(y\), define
\(M_t=(1-p_y)^{-N_t}1_{\{y\text{ never seen in this row by }t\}}\)
when \(p_y<1\), where \(N_t\) is the attained visit count after birth.
Given the full past, its expected factor at a visit is
\((1-p_y)/(1-p_y)=1\), and a skipped visit leaves it unchanged.
It is a nonnegative martingale starting at one. Stop at the \(n_0\)-th visit
and a finite global horizon; Fatou's lemma on increasing horizons yields
\(\Pr(N\text{ reaches }n_0,\ y\text{ unseen})\le(1-p_y)^{n_0}\).
The \(p_y=1\) case has zero missing probability after one visit.
Union bound over coordinates gives
\(b(1-p_{\min})^{n_0}\le b e^{-n_0p_{\min}}\le\alpha\).
This does not condition completed samples on the event that they exist.

With predictable row births and \(\sum_j\alpha_j\le\delta\) pathwise,
the conditional-birth argument in ADAPTIVE gives simultaneous support
correctness for all declarations with probability at least \(1-\delta\).
Rows never sampled sufficiently produce no support certificate.
Knowing support does not identify a hidden sufficient state, physical law or
correct reset interface. Those are distinct premises.

**Why the mass floor matters for alphabets with at least two symbols.**
Compare a point mass at zero to a Bernoulli
row with arbitrarily small positive \(\epsilon\). Under the latter, \(n\)
observations are all zero with probability \((1-\epsilon)^n\), arbitrarily
close to one. Thus a finite all-zero record cannot uniformly certify exact
zero support over this unrestricted class. A known mass floor, a structural
zero proof or a tolerance-based rare-event claim is an explicit repair.

## SD3: formal bridge to a learned architecture

SD1 supplies learned recursive behavior. REALIZATIONS then compiles that table
to an exact symbolic controller, Boolean circuit or finite neural embedding
under each declared operation/encoding contract. CMP1 preserves its behavior
when composed through the same interfaces; AX4 carries the compiled resource
charges. A finite fully charged candidate register can then be selected under
a declared objective, using exact decidable scores or effective outward bounds
and a positive optimization tolerance as in L3. This is a constructive implication with its
acquisition stage paid, not merely a table presumed to have appeared for free.

SD2 supplies a support certificate only in its stated stochastic class. Combining
it with separate state and row-law certificates requires allocating one shared
error allowance or summing their distinct allowances through CMP2. It does not
upgrade probabilistic support recovery into pathwise sure safety.

## Parents

SD1 uses exact query learning and finite-machine conformance testing:
[Angluin (1987)](https://homepages.math.uic.edu/~lreyzin/papers/angluin87.pdf) and
[Chow (1978)](https://archiv.infsec.ethz.ch/intranet_secured/r/1/chow-testingFSMs.pdf).
Its brute-force bounded-class learner is an explicit simple specialization,
not their efficient algorithms. SD2 uses conditional product/supermartingale
and union-bound mechanisms; the mass-floor sample law is not a new GMI rate.
