# Risk, regret and fixed-class learning — LMT-1 / LMT-3

## LMT-1: risk and one-sided online regret

Fix a population law \(P\), measurable loss \(\ell\in[0,1]\), a protected
future interface, and a decoder \(a(K)\) with all additional information
declared. Write \(R_P(K)=E_P[\ell(a(K),Z)]\) and
\(R_P^*=\inf_{h\in H}R_P(h)\). PAC risk learning means
\(\Pr(R_P(K_n)\le R_P^*+\varepsilon)\ge1-\delta\), under the stated sampling
law. Target identification is instead \(\hat q_t\to q(P)\) in a stated mode;
it requires the admitted experiment to identify \(q(P)\).

For online losses and a nonempty fixed comparator family H, define
\[
r_T=\sup_{h\in H}\{\sum_{t\le T}\ell_t(a_t)-\sum_{t\le T}\ell_t(h)\}.
\]
For a realized sequence the one-sided no-regret criterion is
\[
\limsup_T r_T/T\le0
\quad\Longleftrightarrow\quad (r_T)_+/T\longrightarrow0.
\]
The equivalence follows by applying the definition of limsup to every positive
tolerance. Specify which admitted sequences/laws and convergence mode the
algorithm's guarantee covers. An expected signed-regret statement
\(\limsup E[r_T]/T\le0\) is separate; cancellation does not justify replacing
it with convergence of \(E[(r_T)_+]/T\).

**Countermodel to mandatory signed-zero convergence.** Let two fixed actions
be the comparators. On odd rounds their losses are \((0,1)\), and on even
rounds \((1,0)\). A learner using the known round parity chooses the zero-loss
action before feedback. Thus \(r_T=-\lfloor T/2\rfloor\), so \(r_T/T\to-1/2\)
while its positive part is zero. This verifies a sequence-scoped distinction;
it does not certify that this particular policy has low regret on other
adversarial sequences. A conventional nonnegative worst-case regret upper
bound can converge to zero after normalization even when realized regret is
negative.

## LMT-3: fixed-class proper finite ERM

Before the scored sample is seen, fix a finite nonempty hypothesis register
\(H\), measurable maps \(z\mapsto\ell(h,z)\in[0,1]\), and a population law
\(P\). Draw \(Z_1,\ldots,Z_n\) iid from \(P\). An admitted measurable learner
returns a **proper** \(\hat h\in H\) with
\[
\widehat R_n(\hat h)\le\min_{h\in H}\widehat R_n(h)+\eta_n,\qquad\eta_n\ge0.
\]
A fixed finite tie rule supplies measurability for exact ERM. Randomized
selection may use the same bound if every returned member satisfies the
displayed condition. Charge proposal, evaluation, storage and selection work.

For \(d>0\), Hoeffding on each fixed loss function and a finite union bound give
\[
\Pr(\sup_{h\in H}|\widehat R_n(h)-R_P(h)|>d)
 \le 2|H|e^{-2nd^2}.
\]
On the complementary event, choose a population minimizer \(h^*\in H\).
Finiteness guarantees its existence, and properness permits both uniform
bounds:
\[
R_P(\hat h)\le\widehat R_n(\hat h)+d
\le\widehat R_n(h^*)+\eta_n+d
\le R_P(h^*)+\eta_n+2d.
\]
Thus with \(d=\varepsilon/2\) and
\(n\ge 2\varepsilon^{-2}\log(2|H|/\delta)\),
the excess risk is at most \(\varepsilon+\eta_n\) with probability
\(1-\delta\). Exact ERM has \(\eta_n=0\).
For a fixed class, uniform convergence and \(\eta_n\to0\) give proper risk
consistency in the same mode; nonnegative excess risk supplies the lower bound.

## Why two omitted premises are load-bearing

Let \(X\) be uniform on 96 inputs and every true label be zero. At sample
size \(n=24\), define \(h_S(x)=0\) on observed inputs and 1 elsewhere.
The sample-dependent register \(H_S=\{h_{\rm good}\equiv0,h_S\}\) has size2,
and both members have zero training loss. A proper ERM tie rule may return
\(h_S\). Every sample has at most24 distinct inputs, hence
\(R(h_S)\ge72/96=3/4\), whereas \(R^*_{H_S}=0\).

Take \(\varepsilon=\delta=1/2\). The stated size-only sufficient condition is
satisfied: \(2\varepsilon^{-2}\log(2|H_S|/\delta)=8\log8<24\).
(The series for \(e^3\) already exceeds8 in its first three terms.)
Nevertheless failure has probability1. The class was chosen using the same
data to which the fixed-function Hoeffding bound was being applied.
Uniform[0,1] with any finite sample makes the same memorizer's risk exactly1;
the finite construction already suffices.

For a distinct properness failure, keep the pre-data register
\(H=\{h_{\rm good}\}\) but output the same \(h_S\notin H\). Its empirical
risk still equals the minimum over \(H\), yet its population risk is at
least3/4. An empirical inequality alone does not replace class membership.

**Constructive repairs.** Use a fixed containing class and charge its actual
complexity, or first choose a measurable finite class and loss from separate
pilot information \(C\), then obtain a fresh scored sample iid from \(P\)
conditional on \(C\). Conditional on every admitted \(C\), the fixed-class
proof applies to a proper learner, using that class's size and a sample count
chosen before the scored sample. Integrating the conditional bound preserves
the stated error allocation. Sample reuse without this conditional sampling
contract needs a different simultaneous/stability argument.

## Matched parent

This is the fixed-class agnostic PAC/ERM mechanism of
[Shalev-Shwartz and Ben-David, §§2.3 and4.2, Corollary4.6](https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf).
Their §21 supplies the online comparator framework; its worst-case convention
must be distinguished from realized signed regret. No new concentration or
online-learning rate is claimed.
