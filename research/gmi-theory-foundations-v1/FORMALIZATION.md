# GMI theory foundations v1 — formalization

## 0. Scope and claim ceiling

This note proves two narrow foundational results needed by #833:

1. a symmetry obstruction to *literal* prior-free unique selection; and
2. a canonical minimal behavioral quotient for deterministic, total, finite-interface
   transition/output systems.

The word **finite-interface** means only that the action and observation/output alphabets
used by the executable checks are finite. The analytic behavioral-quotient theorem below
does not require the carrier state set to be finite unless a cardinality comparison is
invoked. No stochastic, causal, developmental, open-ended, or universal-intelligence
claim is proved here.

A finite executable check is a reconstruction aid and hostile control. It is not a proof
of a universally quantified theorem.

---

## 1. Objects

### Definition 1 (deterministic transition/output system)

A deterministic transition/output system is a tuple

\[
M=(S,A,O,\delta,\lambda),
\]

where \(S\neq\varnothing\) is a state carrier, \(A\neq\varnothing\) is an action/input
alphabet, \(O\neq\varnothing\) is an output alphabet,

\[
\delta:S\times A\to S,\qquad \lambda:S\times A\to O
\]

are total functions. No graph, neural, symbolic, probabilistic, program, or other
architecture is assumed.

For \(w\in A^\*\), define the emitted output word \(B_s(w)\in O^\*\) recursively:

\[
B_s(\epsilon)=\epsilon,\qquad
B_s(av)=\lambda(s,a)\,B_{\delta(s,a)}(v).
\]

### Definition 2 (behavioral specification)

The **behavioral specification** of a state \(s\) is the function

\[
\beta(s):A^\*\to O^\*,\qquad \beta(s)(w)=B_s(w).
\]

A specification is therefore extensional: it says what output trace is produced for
every admissible finite action trace. It does not name an implementation architecture.

### Definition 3 (future-behavior equivalence)

\[
s\sim_B t
\quad\Longleftrightarrow\quad
\forall w\in A^\*:\ B_s(w)=B_t(w).
\]

---

## 2. Symmetry obstruction to literal prior-free unique selection

The result is stated as a group-action theorem because "no prior" is otherwise too vague
to prove anything about.

Let a group \(G\) act on a hypothesis set \(H\) and an evidence space \(X\). A
deterministic selector is \(f:X\to H\). It is **equivariant** when

\[
f(gx)=g f(x)\quad\text{for all }g\in G,x\in X.
\]

For evidence \(x\), its stabilizer is
\(G_x=\{g\in G:g x=x\}\). The hypotheses fixed by every element of the stabilizer are

\[
\operatorname{Fix}_H(G_x)=\{h\in H:\forall g\in G_x,\ gh=h\}.
\]

### Theorem S1 (stabilizer fixed-point necessity)

If an equivariant deterministic selector \(f:X\to H\) is defined at \(x\), then

\[
f(x)\in \operatorname{Fix}_H(G_x).
\]

Hence, if \(\operatorname{Fix}_H(G_x)=\varnothing\), no deterministic equivariant
selector can make a unique selection at \(x\).

**Proof.** Take any \(g\in G_x\). Since \(gx=x\), equivariance gives

\[
f(x)=f(gx)=g f(x).
\]

Thus \(f(x)\) is fixed by every \(g\in G_x\), so it lies in
\(\operatorname{Fix}_H(G_x)\). If that set is empty, such an \(f(x)\) cannot exist. ∎

### Corollary S1.1 (fully symmetric finite hypotheses)

Let \(H\) be finite with \(|H|\ge2\), let \(G=\mathrm{Sym}(H)\) act on \(H\) by
permutation, and suppose evidence \(x\) is invariant under every \(g\in G\). Then no
deterministic \(G\)-equivariant selector \(f\) can uniquely choose an element of \(H\)
at \(x\).

**Proof.** Here \(G_x=G\). No \(h\in H\) is fixed by every permutation: choose
\(h'\ne h\) and the transposition exchanging \(h,h'\). Therefore
\(\operatorname{Fix}_H(G_x)=\varnothing\), and Theorem S1 applies. ∎

### Scientific consequence

"Literally assumption/prior-free unique derivation" is not a coherent universal target
whenever observational evidence leaves a nontrivial relabeling symmetry. A unique
choice must obtain a symmetry breaker from at least one of:

- additional evidence;
- a representation convention;
- an architecture/operator restriction;
- a search or tie-breaking rule;
- an ecological/resource restriction; or
- an evaluation/scalarization rule.

This is a necessity statement, not a claim that every declared prior is justified.

### Definition 4 (architecture-prior-free within a declared ledger)

For #833, a derivation is called **architecture-prior-free within ledger \(L\)** iff:

1. its admissible carrier and behavioral specification do not preselect a named
   implementation family (neural, graph, symbolic, transformer, cellular, etc.);
2. renaming architecture labels alone cannot alter admissibility, proof validity, or
   score;
3. every non-evidential restriction used to make selection, inference, search, or
   evaluation determinate is recorded in \(L\) under a prior category; and
4. the claim is invalidated if an undeclared architecture restriction is necessary to
   reproduce the result.

This definition intentionally does **not** mean "prior-free". Theorem S1 explains why
the latter is generally impossible as a unique-selection requirement under unresolved
symmetry.

---

## 3. Deterministic behavioral quotient

### Theorem B1 (equivalence and one-step stability)

\(\sim_B\) is an equivalence relation. Moreover, if \(s\sim_B t\), then for every
\(a\in A\),

\[
\lambda(s,a)=\lambda(t,a)
\quad\text{and}\quad
\delta(s,a)\sim_B\delta(t,a).
\]

**Proof.** Reflexivity, symmetry, and transitivity follow pointwise from equality in
\(O^\*\). For one-step stability, use the one-letter word \(a\) to obtain equality of
\(\lambda(s,a)\) and \(\lambda(t,a)\). For arbitrary \(v\in A^\*\),

\[
B_s(av)=\lambda(s,a)B_{\delta(s,a)}(v),\qquad
B_t(av)=\lambda(t,a)B_{\delta(t,a)}(v).
\]

The first symbols are already equal, and the full words are equal because \(s\sim_B t\);
therefore the suffixes are equal for every \(v\), proving
\(\delta(s,a)\sim_B\delta(t,a)\). ∎

### Theorem B2 (well-defined quotient)

Let \(\bar S=S/{\sim_B}\). Define

\[
\bar\delta([s],a)=[\delta(s,a)],
\qquad
\bar\lambda([s],a)=\lambda(s,a).
\]

Then \(\bar M=(\bar S,A,O,\bar\delta,\bar\lambda)\) is well-defined and has exactly the
same future behavior as \(M\) under the quotient map \(q(s)=[s]\).

**Proof.** If \([s]=[t]\), Theorem B1 gives both equal immediate outputs and equivalent
successors, so neither definition depends on the representative. Induction on
\(|w|\) then gives \(B_{[s]}(w)=B_s(w)\) for every \(w\). ∎

### Definition 5 (exact deterministic abstraction)

An exact deterministic abstraction of \(M\) is
\(N=(Q,A,O,\delta_Q,\lambda_Q)\) with a map \(f:S\to Q\) satisfying, for all \(s,a\),

\[
f(\delta(s,a))=\delta_Q(f(s),a),
\qquad
\lambda(s,a)=\lambda_Q(f(s),a).
\]

Only the used image \(f(S)\) matters for state-count comparisons.

### Theorem B3 (minimality)

For every exact deterministic abstraction \(f:S\to Q\),

\[
f(s)=f(t)\Longrightarrow s\sim_B t.
\]

Consequently each fiber of \(f\) is contained in one \(\sim_B\)-class. If the number of
behavioral classes is finite, then

\[
|f(S)|\ge |S/{\sim_B}|.
\]

The quotient of Theorem B2 attains equality, hence is state-minimal among exact
deterministic abstractions.

**Proof.** Suppose \(f(s)=f(t)\). By induction on a word \(w\), the homomorphism equations
force the two abstract executions to occupy the same abstract state before each action
and to emit the same output symbol at every step. Thus \(B_s(w)=B_t(w)\) for every
\(w\), so \(s\sim_B t\). Therefore different behavioral classes cannot be merged by
\(f\). The finite cardinality inequality follows, and the quotient realizes one state
per class. ∎

### Corollary B3.1 (uniqueness up to isomorphism at the minimum)

Any exact deterministic abstraction with exactly one used state per behavioral class is
isomorphic, on its used image, to \(\bar M\).

**Proof.** Map \([s]\mapsto f(s)\). B3 makes this injective when the state counts are
equal; surjectivity onto \(f(S)\) is immediate. The defining homomorphism equations
preserve transitions and outputs. ∎

---

## 4. Relation to Myhill–Nerode

For a DFA \(D=(S,A,\delta,s_0,F)\), define state right-language equivalence

\[
s\sim_L t
\Longleftrightarrow
\forall w\in A^\*:
[\delta^\*(s,w)\in F]=[\delta^\*(t,w)\in F].
\]

For words \(u,v\), the classical Nerode relation is

\[
u\equiv_L v
\Longleftrightarrow
\forall w\in A^\*:\ [uw\in L]=[vw\in L].
\]

If \(s_u=\delta^\*(s_0,u)\), then directly

\[
u\equiv_L v\Longleftrightarrow s_u\sim_L s_v.
\]

Thus, on reachable states, the same "indistinguishable by every future experiment"
construction specializes to the classical minimal-DFA quotient. The present Mealy
theorem is not advertised as a new Myhill–Nerode theorem; it is the transition/output
analogue required to make #833's architecture-neutral behavioral state precise.

---

## 5. Relation to bisimulation and the nondeterministic boundary

Write the deterministic Mealy transition as
\(s\xrightarrow{a/o}\delta(s,a)\) where \(o=\lambda(s,a)\).
In a deterministic total machine, \(\sim_B\) is exactly the largest relation that
matches every \(a/o\)-transition on both sides: Theorem B1 gives the forward
bisimulation condition, and induction over paths gives the converse.

This equivalence fails for nondeterministic systems if behavior is weakened to **trace
sets**.

### Counterexample N1 (trace equivalence does not imply bisimulation)

Consider two finite labeled transition systems:

- \(p_0\xrightarrow{a}p_1\), and
  \(p_1\xrightarrow{b}\bot,\ p_1\xrightarrow{c}\bot\);
- \(q_0\xrightarrow{a}q_b,\ q_0\xrightarrow{a}q_c\),
  \(q_b\xrightarrow{b}\bot,\ q_c\xrightarrow{c}\bot\).

Both initial states have exactly the finite traces
\(\{\epsilon,a,ab,ac\}\). They are not strongly bisimilar. Any match for
\(p_0\xrightarrow{a}p_1\) must relate \(p_1\) to either \(q_b\) or \(q_c\).
The former cannot match the \(c\)-transition of \(p_1\); the latter cannot match its
\(b\)-transition. ∎

Therefore B1–B3 may not be exported to nondeterministic trace semantics without a new
theorem and a stronger behavioral object.

---

## 6. Predictive-state boundary

The deterministic quotient groups states by equality of all action-contingent future
output traces. That is structurally related to predictive-state ideas, but the
stochastic extension is intentionally open.

- Predictive State Representations represent controlled stochastic state using
  predictions of action-conditional tests.
- Computational mechanics groups histories that induce the same conditional
  distribution over futures and proves predictive minimality/uniqueness results under
  its own process assumptions.

Neither literature result licenses replacing the deterministic equality used above by an
unspecified stochastic criterion. #833 therefore records the controlled stochastic
behavioral quotient, measurability, approximate equivalence, and finite-sample
identifiability as separate open gaps.

---

## 7. References used to set boundaries

- T. M. Mitchell, *The Need for Biases in Learning Generalizations*, Rutgers
  CBM-TR-117 (1980). https://www.cs.cmu.edu/~tom/pubs/NeedForBias_1980.pdf
- J. R. Rice, *The Algorithm Selection Problem*, Advances in Computers 15 (1976),
  pp. 65–118. https://doi.org/10.1016/S0065-2458(08)60520-3
- R. Alur et al., *Syntax-Guided Synthesis*, FMCAD (2013).
  https://doi.org/10.1109/FMCAD.2013.6679385
- M. L. Littman, R. S. Sutton, S. Singh, *Predictive Representations of State*,
  NeurIPS 14 (2001/2002 proceedings).
  https://proceedings.neurips.cc/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html
- C. R. Shalizi, J. P. Crutchfield, *Computational Mechanics: Pattern and Prediction,
  Structure and Simplicity*, Journal of Statistical Physics 104 (2001), 817–879.
  https://arxiv.org/abs/cond-mat/9907176
