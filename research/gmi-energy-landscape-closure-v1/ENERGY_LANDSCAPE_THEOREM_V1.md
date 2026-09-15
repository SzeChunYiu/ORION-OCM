# Finite energy-landscape reduction and phase theorem v1

## Scope

This result concerns finite, explicitly encodable energy landscapes with a
computable strict-relaxation law. It closes the four energy-landscape tasks in
Issue #602 at that scope. It makes no claim about analog physical relaxation,
quantum dynamics, unbounded precision, or unmatched hardware prices.

## Definition

Let \(X\) be a finite nonempty state set, \(E:X\to L\) an energy into a
totally ordered set, \(N(x)\subseteq X\) a declared neighborhood, and
\(\prec\) a fixed tie order. The carrier is

\[
S_E=(X,E,N,\prec,x).
\]

Its native operator is strict relaxation

\[
R(x)=
\begin{cases}
\prec\!\operatorname{-first}\arg\min\{E(y):y\in N(x),E(y)<E(x)\},
 &\text{if that set is nonempty},\\
x,&\text{otherwise}.
\end{cases}
\]

An update may replace \(E\), \(N\), or their finite parameterization (for
example Hebbian updates to a coupling field); those mutable objects remain part
of the sufficient state and their update cost is charged.

## Theorem EL-1 — exact reduction to D6 and local optimization

Every finite energy system above compiles exactly to D6 by setting the D6
transition law \(F=R\) and its current state to \(x\). For every initial
state and horizon \(t\),

\[
F^t(x)=R^t(x).
\]

The same object is a discrete local-optimization instance: objective \(E\),
proposal relation \(N\), deterministic selection \((E,\prec)\), and stopping
condition “no strict improvement.”

**Proof.** The compiler copies \(x,E,N,\prec\) and implements exactly the
displayed case split. One-step equality is definitional; induction gives equality
for all \(t\). Copying a symbolic transition representation has constant
wrapper overhead (E1); compiling an explicit finite transition table takes
\(O(|X|+\sum_x|N(x)|)\) evaluations and space (E2). The optimization
identification is the same tuple under standard objective/proposal/selection
names. ∎

The converse is false. A D6 two-cycle \(a\mapsto b\mapsto a\), \(a\ne b\),
would require both \(E(b)<E(a)\) and \(E(a)<E(b)\). Thus strict relaxation is
a proper D6/optimization subclass, not a new domain.

## Theorem EL-2 — termination, basin, and burden

Each changed relaxation step strictly lowers energy. Therefore no state can
repeat and every trajectory reaches a fixed point in at most \(|X|-1\) changed
steps; more sharply, at most \(|E(X)|-1\). The basin of fixed point \(a\) is

\[
B(a)=\{x\in X:\exists t<|E(X)|,R^t(x)=a\}.
\]

If at most \(d\) neighbors are inspected per step, an energy evaluation costs
\(c_E\), comparison/tie handling costs \(c_C\), and selection costs \(c_S\),
then a query has the explicit upper bound

\[
B_{serve}\le (|E(X)|-1)\,[d(c_E+c_C)+c_S].
\]

State description, energy/neighborhood construction, update, precision, failed
starts, and verification remain separate lifecycle coordinates. For independent
restart basin mass \(p>0\), the existing BR-1 law adds expected restart factor
\(1/p\), or \(\lceil\log\delta/\log(1-p)\rceil\) starts for miss
probability at most \(\delta\).

**Proof.** Strict descent makes the visited energy values a strictly decreasing
finite sequence. Multiplying its maximum number of changes by the declared
per-step work gives the bound. The basin statement is the preimage of a fixed
point under this terminating map. The restart law follows from independent
failure probability \((1-p)^r\). ∎

## Theorem EL-3 — corrected exact phase boundary

In the committed \(N=32,P=4\), one-bit-noise, wide-integer receipt, Hopfield
relaxation and the nearest-exemplar parent are both capability 1 and have the
same answer signature. Their native-price coordinates are

| realization | description | serve/query |
|---|---:|---:|
| energy relaxation | 1984 bits | 3 native operations |
| exemplar parent | 128 bits | 4 native operations |

At reuse horizon \(H\), their lifecycle costs are \(1984+3H\) and
\(128+4H\). Hence

\[
H^*=1856;
\quad H<1856:\text{parent};\quad
H=1856:\text{tie};\quad H>1856:\text{energy relaxation}.
\]

The separate description-compression crossover is \(P^*=124\) patterns at
\(N=32\), while the executed capacity gate lies between \(P=4\) and \(P=8\).
Thus compression is unavailable in the capability-feasible cells at this scope;
the surviving phase is the high-reuse native-price corner at the capacity edge.

This corrects the original frozen clause that overlooked the three actual
descent sweeps and truncated its grid at \(H=1024\). It is a negative result
for domain novelty but a positive, exact phase-law result. The committed receipt,
its correction, and every tiny landscape through four states are validated by
the executable certificate.
