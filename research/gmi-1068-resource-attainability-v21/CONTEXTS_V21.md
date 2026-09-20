# V21 contextual images, resource response and capability

Read THEORY_V21 first. These proofs use actual V15 Context with independent
admission P and evaluator domain E, evaluator nu:{h // E h}→W and declared order.

## U2.1 — actual selected and unrestricted finite-history images

Take raw histories H=S×List A. Write start(h),word(h), and let selection Q_x(h)
imply start(h)=x; additional selection restrictions are allowed. Physical success
means weighted execution W(start(h),word(h)) is some(t,c). Define admission
L_x(h)=P(h) and Q_x(h) and physical success. The budget admission L_x^b adds c≤b.
Determinism gives a unique c, so this definition is unambiguous.

Keep the SAME Context E,nu and value order. The attainable image is
A_x={v | exists h, L_x(h) and exists he:E(h), nu(h,he)=v}.
Define A_x^b with L_x^b. Proof irrelevance makes evaluation independent of the
chosen proof he. For all histories from x choose Q_x(h):=start(h)=x.
A finite selected list uses membership as Q_x; repeated history/value occurrences
do not create new image values. This is exactly V20 Attained with its actual
P-and-E restricted valueMap. Actual history identity remains available to nu.

Observation with admission L_x^b has three exact cases: not L_x^b is illegal;
L_x^b and not E is undefined; L_x^b and E returns nu(h,he). Resource failure
therefore changes admission, not E. An ambient evaluation at an illegal history
remains part of the Context but contributes no attainable value. An observation
label None in V8 is distinct from missing transitions and from evaluator failure.

For nested selections Q⊆Q', every image witness under Q is the identical witness
under Q'; hence A_Q⊆A_Q'. For b≤b', transitivity gives L_x^b⊆L_x^b', and thus
A_x^b⊆A_x^b'⊆A_x. U1.2 proves these restrictions describe actual V8 executions,
not merely sets assigned numeric labels. Fixed E,nu,P and physical dynamics are
essential to this argument; changing evaluators requires separate transport.

## U2.2 — all finite lengths and all finite allowances

Let A_{x,n} restrict Q_x by word length≤n. Then A_x=union_n A_{x,n}:
subset follows by dropping a length bound; converse takes n=length(word(h))
from the actual witness. The same law holds with a fixed resource restriction.
Similarly A_x=union_b A_x^b: each witness has a finite Nat cost c and belongs
to A_x^c; reverse inclusion was just proved. No uniform bound is asserted.
These are unions of actual finite witnesses, not limits, closures or omega traces.
A finite-state machine can still have infinitely many finite histories and values.

## U3.1 — joint attained information and two resource meanings

Define J_x(c,v) iff there is h satisfying P,Q_x,E, with actual weighted cost c
and actual evaluated value v. Then
v in A_x^b iff exists c≤b, J_x(c,v).
Both directions unpack the SAME history witness; U1.2 ties it to resource
execution. Also v in A_x iff exists c,J_x(c,v). Thus J retains the association
between resources and outcomes, which two separate marginal sets can lose.

A declared coordinate map rho:W→R gives the different resource response rho[A_x].
Construct the actual Context with domain E and evaluator rho∘nu; its target
preorder is explicitly supplied. Its attainable image is exactly rho[A_x], since
each side has the same witness h and equality rho(nu(h))=r. No monotonicity is
needed for this image identity. Order-preserving pruning would need V20's guard.
Neither rho nor actual execution costs can be recovered from a bare value set.
Joint cost/value lifting explains when resource restrictions can be expressed
as a projection of a restricted joint image; it does not identify all resources
with coordinates already present in the original Context.

## U3.2 — declared capability and least attained Nat target cost

For any declared target G⊆W, define capability at b as existence of an actual
selected admitted physically successful finite history, E-defined, cost≤b,
whose evaluated value lies in G. By U3.1 this is equivalent to
A_x^b intersect G nonempty, or exists c≤b,v, J_x(c,v) and G(v).
No upward-closedness of G is needed: this is exact image membership/inclusion,
not frontier pruning. Impossibility is the negation of that existential witness.
This last equivalence alone does not identify any intervention or causal barrier.

Let C_G={c:Nat | exists v,J_x(c,v) and G(v)}. Define threshold(G)=None when
C_G is empty; otherwise some(min C_G). Nat well-ordering provides this least
element. Its membership supplies a v AND an actual history realizing it.
For finite c0, threshold(G)=some(c0) iff c0 belongs to C_G and c0≤every c in C_G.
Proof: the forward implication is the minimum definition. For the reverse,
minimum membership and the assumed two lower bounds give equality by antisymmetry.
Thus capability(b,G) iff exists c0,threshold(G)=some(c0) and c0≤b.
Forward: choose a witnessed c≤b and the least element c0≤c. Reverse: use the
history attaining c0, which remains feasible at b by U1.2. threshold=None iff
no unrestricted finite target witness exists. This construction is possibly
noncomputable and assumes no finite-state sufficient observer or shortest solver.
For the singleton target {v}, let D(v) be this threshold. Then v in A_x^b iff
D(v)=some(c) for some c≤b, so D exactly determines every A_x^b. Conversely,
D(v) is None if v never appears, otherwise the first Nat index at which v appears.
Thus D is recoverable from the entire labelled filtration. This is relative to
the declared value labels and Nat index, not an absolute encoding minimum.
The complete J is sufficient but not necessary or recoverable: J={(0,v)} and
J'={(0,v),(1,v)} have the same D and all the same A_b. More expensive duplicate
witnesses are invisible to this observer. Failure of separate marginals does not
establish that every detail of the full joint relation must be retained.

## U2.3 — exact historical image bridge and closure scope

Original R3 Attain(Reach,f)(v) means exists h,Reach(h) and f(h)=some(v).
Take Reach=L_x (or L_x^b) and f=valueMap P k from V20's actual partial Context.
Because L already includes P, the original witness equation is equivalent to
exists h,L(h),E(h),nu(h)=v, hence to the actual image above. Alternatively use
Reach=Q_x and valueMap L_x k. Both factorizations preserve actual histories.
For a general Scenario sc, the kernel uses Reach=sc.admission and the ambient
map valueMap True sc.context; the identical witness equivalence holds without
repeating admission in that map. The same witnesses transport original attain_mono; original maximal_is_attainable
and impossible_means_no_target retain their exact modest statements.
Freshly replay those original declarations and register the actual bridge;
reusing their names without their old source is insufficient for R3-010.
No barriers, context-family regime switches or legacy abbreviations are resolved
by these image and minimum-cost theorems.
