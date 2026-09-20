# Constructive synthesis and operational transport V6

This successor follows FREEZE_V6.md. Boolean completeness, structural induction,
compiler verification and simulation are parent mathematics. The result is a
specific constructive synthesis certificate, not architecture-free general AI.

## Syntax, semantics and the certificate theorem

The grammar is t ::= x | y | NAND(t,t). Every leaf and operator costs one:
size(x)=size(y)=1 and size(NAND(a,b))=1+size(a)+size(b).
Its syntax includes every finite tree of arbitrary depth; no maximum depth is
part of the mathematical claim. An executable uses complete binary truth tables:
bit 2*x+y records output on inputs (x,y), so bit order is 00,01,10,11.

For any semantic set S, terminal values X,Y and operation N:S*S->S, interpret
trees recursively. Let m:S->N satisfy m(X)<=1, m(Y)<=1 and, for all a,b in S,
m(N(a,b))<=1+m(a)+m(b). Then m(eval(t))<=size(t) for every tree t.

Proof: each leaf follows from its terminal inequality. For NAND(a,b), the
composition inequality bounds its semantic value by 1+m(eval(a))+m(eval(b));
the two inductive hypotheses bound this by 1+size(a)+size(b). This proves the
claim by structural induction, independently of a search's stopping criterion.

If for every s in S there is a witness t_s with eval(t_s)=s and size(t_s)=m(s),
then m(s) is the exact minimum cost among all finite trees denoting s.
The witness supplies an upper bound. Applying the preceding theorem to any
other tree denoting s supplies the matching lower bound. A finite semantic
quotient can therefore certify minima in an infinite grammar without an
unjustified depth cutoff.

For the binary Boolean instance, S has exactly 16 truth tables. Checking both
terminal inequalities, all 256 ordered composition inequalities, and an
actually evaluated attaining witness for each table instantiates this theorem.
A search reporting 16 entries alone does not do so. Neither the inequality
certificate nor compiler correctness depends on NAND commutativity.

Equality of complete truth tables is a congruence for this operation. Hence
semantic dynamic programming may replace a subtree by another expression with
the same table without changing a larger expression's table. Retaining the
cheapest discovered representative is sound for the declared additive node
cost, but a final global optimum claim still requires the certificate above.
Other costs, grammar operators or evaluation domains need their own proof.

## Stack compiler theorem

The target instructions are PUSH_X, PUSH_Y and NAND. Compile a leaf to its
load, and NAND(a,b) to compile(a); compile(b); NAND. NAND pops the right operand,
then the left operand, and pushes N(left,right). Failure on fewer than two
operands is explicit. There are no other valid executable opcodes.

For every tree t, arbitrary semantic type S and arbitrary initial stack st,
running compile(t) succeeds and leaves eval(t) above the original stack.
Proof: loads establish the leaf cases. For NAND(a,b), induction first yields
eval(a) above st, then eval(b) above eval(a) above st. The final instruction
pops exactly these two values and pushes N(eval(a),eval(b)). Sequential code
execution over appended lists equals successive execution; its proof is
induction on the first instruction list, including the failure case.

Also length(compile(t))=size(t): loads each have length one and appending the
two child compilations plus NAND adds one to their combined lengths.
The Lean representation lists the top first, giving eval(t)::st. Python stores
the bottom first, giving st+(eval(t),). Reversing stack order relates these two
representations; instruction order and operand order agree. Ill-formed encoded
instructions are rejected by the executable parser; Lean's inductive opcode
type excludes them by construction rather than proving a parser theorem.

## Uniform deterministic operational simulation

The following is a paper theorem; it is not established by Boolean compiler
tests. Let source and target machines have deterministic partial successor
functions f:S->?S and g:T->?T. Undefined means actual halting, not timeout or an
unknown evaluation. Fix one effective state encoder E, shared uniformly across
all supported programs and inputs, with these premises for every reachable s:

1. If f(s)=s', a specified finite positive block length k(s)>=1 satisfies
   g repeated k(s) times from E(s) equals E(s'), with every intermediate
   transition defined.
2. If f(s) is undefined, g(E(s)) is undefined.
3. Observations at designated block boundaries decode to source observations;
   intermediate target observations are silent or erased by the declared trace
   projection. The encoder and simulation procedure use no noncomputable oracle.

Then every n-step source prefix lifts to a target prefix of length
K_n=sum_{i<n}k(s_i), with the same boundary observations. If the source halts
after n steps, that target prefix halts at E(s_n). If the source never halts,
all its lifted prefixes exist and K_n>=n, so the target cannot halt after
finitely many steps. Thus halting is both preserved and reflected for target
runs started at encoded source states.

Proof of prefix transport: induction on n concatenates the next supplied
block. Determinism makes these prefixes agree with the single target run.
The terminal premise gives preservation. For reflection, a nonhalting source
would supply target prefixes longer than any supposed finite halting time,
a contradiction. Finite positive progress is essential: zero-step stuttering
cannot establish divergence preservation, and a divergent interpreter block
cannot establish transport of the next source step.

No global bound on k is required for this qualitative theorem. A quantitative
claim such as K_n<=B*n additionally needs a uniform k(s)<=B. Encoding,
initialization, output decoding and lifecycle overhead must also be counted.
This theorem supplies neither a computable decision procedure for source
halting nor an efficient universal interpreter.

For nondeterministic machines, an existential matching target path for each
source transition proves only forward inclusion of projected source traces.
The target may have additional choices and outcomes. Equality of attainable
outcomes needs a reverse path-lifting condition for every admitted target run,
compatible starts/acceptance/evaluation, and prevention of unaccounted internal
divergence. Action/control policies and observations must also be transported
before any control-equivalence conclusion is available.

Finite coded digital algorithms can use this theorem after establishing an
effective operational simulation for their actual instructions. Arbitrary exact
real constants, unrestricted real-number oracles and undecidable exact tests
are not automatically covered. Computable reals require a specified effective
representation and supported operations; approximations require error
transport. A representation theorem does not select a useful architecture,
prove it discoverable under a particular search, or transfer its learning
performance without corresponding premises.

## Robust comparison with lifecycle cost intervals

Suppose each candidate i has true quality q_i and total relevant cost c_i with
q_i in [Q_i-d_i,Q_i+d_i], c_i in [l_i,u_i], d_i>=0 and l_i<=u_i.
Let lambda>=0 and score_i=q_i-lambda*c_i. If candidate w satisfies

Q_w-d_w-lambda*u_w > Q_j+d_j-lambda*l_j for every j != w,

then w is the unique score maximizer for every realization within these
intervals. Proof: the left expression lower-bounds score_w; each right
expression upper-bounds score_j. The strict comparison composes these bounds.
This is a sufficient robust certificate. Failure to certify is UNKNOWN for
that comparison, not evidence that no candidate is truly best.

The intervals must jointly cover all relevant acquisition, synthesis, training,
inference, storage, evaluation and transfer costs in a common declared unit,
with amortization and workload explicit. Numerical intervals do not establish
their own coverage. Negative lambda, omitted costs or comparisons outside the
registered domain require a different theorem. Point-estimate winners and
ties are not promoted to a certified unique robust winner.

## Formal boundary

SimulationV6.lean proves run_append, compile_correct, compile_size,
certificate_lower_bound, exact_minimality and explicit stack-underflow facts.
The semantic type and operation are generic; complete Boolean-table instance
coverage and attained witnesses are independently executable obligations.
The general operational simulation and interval theorem above are paper proofs.
The finite compiler instance does not mechanize a universal machine theorem.

Declared inputs, grammar, Boolean semantics, equality oracle, node costs and
search order remain assumptions. All 222 original requirements retain their
identities; these local constructive results do not close the full R0-R17
programme or explain and derive every known machine intelligence family.
