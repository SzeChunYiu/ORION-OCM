# Empirical frontier identification theorem — EFI-1--4

Date: 2026-09-13. Status: exact finite-register mathematics; conditional measurement bridge.
This module repairs the inference from uncertain resource intervals to family
coexistence. It complements EMPIRICAL_RESOURCE_IDENTIFICATION_THEOREM_V1.md:
scalar resource bounds alone do not identify a vector Pareto frontier.

## 1. Primary parents and the precise adaptation

[Hladik, ODS 2017, slides 5--9](https://kam.mff.cuni.cz/~hladik/doc/2017-conf-PssEffIntMolp-talk.pdf)
defines possible efficiency in some realization and necessary efficiency in
every realization. These quantifiers are the direct parent. Its linear
coefficient model couples candidate profiles; its specialized theorems cannot
be transplanted to arbitrary joint measurement uncertainty.
[Bokrantz and Fredriksson, 2017, sections 1 and 4](https://arxiv.org/html/1308.4616v5)
instead study set-valued robust efficiency and warn against replacing coupled
uncertainty by independently adverse coordinates. That optimization criterion
is not synonymous with necessary scenario-wise frontier membership here.
[VIM3, 2.47](https://jcgm.bipm.org/vim/en/2.47.html) requires a specified measurand
for measurement compatibility and explicitly accounts for correlation.
The adaptation is an exact finite-candidate identification algorithm and a
GMI instrument-transport contract, not a new general Pareto-optimization claim.

## 2. Joint worlds, membership and family support

Register finite nonempty candidate universe I and dimension d>=1; all
coordinates are minimized finite real costs. Admissibility, adequacy and
developmental reachability are fixed throughout this register. The claimed
universe is exactly I; wider claims require a separate coverage proof.
Let W be a nonempty set of jointly feasible measurement worlds. World w
assigns every i a vector x_i(w). Write x prec y when x<=y coordinatewise and
at least one coordinate is strictly smaller. Equal profiles retain every tie.

Define F(w)={i: no j!=i has x_j(w) prec x_i(w)},
P=union_w F(w), N=intersection_w F(w), and Q={F(w):w in W}.
For a fixed family map f, use S={ {f(i):i in F}:F in Q }.

**EFI-1.** P and N are exactly possible and necessary membership, respectively.
The exact candidate frontier is identified iff P=N, equivalently |Q|=1.
The exact family support is identified iff |S|=1, a weaker condition.

Proof. The union and intersection express the existential and universal
quantifiers. If equal, every intermediate F(w) equals them; the converse is
immediate. Applying f can identify distinct candidate sets. Each world has a
finite nonempty candidate register and hence a nonempty frontier. Q and S
are therefore nonempty. QED.

Finite W is solved exactly by enumerating its worlds, computing F in each,
and accumulating Q, P, N and S. In general the union of possible families
does not assert simultaneous coexistence. Even necessary family presence
need not provide a necessary individual: two same-family candidates with
scalar worlds (0,1) and (1,0) always supply that family, but N is empty.

## 3. Fully rectangular intervals and the correlation boundary

Suppose W_box is the FULL product of closed intervals [L_ik,U_ik], with
finite endpoints and L_ik<=U_ik, independently across candidates AND
coordinates. This is a feasibility assumption, not a probability model.

**EFI-2.** For this full rectangle, exactly
P_box={i: no j!=i has U_j prec L_i},
N_box={i: no j!=i has L_j prec U_i}.

Proof. For possible membership, set i to L_i and all rivals to their U_j.
This simultaneously favorable world is feasible. If a rival dominates i
there, that rival dominates i in every world, including the strict
coordinate; otherwise this world witnesses membership. For necessary
membership, set i to U_i and all rivals to their L_j. A dominator witnesses
failure. If none dominates there, no rival can dominate in any world:
any such strict comparison would imply L_j prec U_i. QED.

If the true nonempty joint W is merely contained in W_box, the safe
conclusions are N_box subseteq N_W and P_W subseteq P_box; equality need
not hold. In scalar worlds (i,j,k)=(1,0,2) or (1,2,0), i never survives,
although its marginal-box favorable world (1,2,2) makes it survive.
Here every world has a dominator, but no fixed rival dominates in all
worlds. Known correlations must be retained or overapproximation declared.
Finite correlated W admits EFI-1 directly. Arbitrary continuous correlated
constraints require their own exact feasibility oracle; no solver is implied.

**Forced-survivor corollary.** If one coordinate k obeys
U_ik < L_jk for every rival j, then i is necessary for every nonempty W
inside those bounds. A rival cannot meet the required <= in coordinate k.
Other-coordinate costs and timing cannot overturn this conclusion.
This proves survival, not domination of the other candidates.

## 4. Constructive exact frontier patterns for continuous rectangles

Individual membership corners do not identify every possible full frontier.
For scalar intervals A=[0,2], B=[1,3], every endpoint world has one winner;
the interior equality A=B=3/2 has frontier {A,B}. Endpoint-world enumeration
therefore misses a possible coexistence pattern.

**EFI-3.** All Q and S for a full finite rectangle can be computed by
enumerating feasible ordered partitions separately in each coordinate.
An ordered partition B_1,...,B_r assigns equal coordinate values within
each nonempty block and strictly increasing values between blocks.
For each block put l_b=max_{i in B_b} L_ik and u_b=min_{i in B_b} U_ik.
This partition is feasible iff
l_b<=u_b for every b, and l_p<u_q for every p<q.

Proof of feasibility. Necessity follows from l_p<=t_p<t_q<=u_q.
For one block choose t_1=l_1. Otherwise choose
delta=(1/2) min_{p<q} (u_q-l_p)/(q-p)>0, and
t_q=max_{p<=q} [l_p+(q-p)delta].
Then t_q>=l_q and t_q<=u_q: the p=q term uses l_q<=u_q;
every earlier term is strictly below u_q by the delta choice.
Also t_(q+1)>=t_q+delta. Assign t_b to every member of block b.
This constructs a feasible representative, rational for rational endpoints.

There are finitely many ordered partitions. Each coordinate assignment
induces exactly one; the construction realizes each feasible one.
Rectangular feasibility allows any combination of coordinate representatives.
All strict dominance relations depend only on these coordinate orders.
Their product therefore realizes exactly every possible frontier pattern;
mapping each frontier through f supplies every family-support pattern. QED.

The algorithm is finite and can be expensive; it is not a scalable claim for
unbounded architecture spaces. Exact rational comparisons avoid tolerance
changing ties. Arbitrary real endpoints require exact comparison/arithmetic
access; the implementation accepts integers and rational numbers only.

## 5. Cross-instrument transport and testable predictions

**EFI-4.** Suppose two instruments admit a candidate bijection b preserving
family, task adequacy and developmental admissibility, and a world bijection
h preserving the registered joint feasibility model. Suppose, for every
world and candidate pair, strict Pareto dominance holds in instrument 1
iff it holds between their images in instrument 2. Then b(F_1(w))=F_2(h(w));
possible/necessary membership and all family-support patterns transport.

Proof. The bijection carries exactly every competing dominator and its
absence. Taking unions, intersections and family images proves the claim.
A sufficient profile condition is x_2(b(i),h(w))=T(x_1(i,w)), where T is a
common separable map T(x)_k=t_k(x_k), each t_k strictly increasing.
Positive affine changes of units satisfy it. Merely increasing mixed-coordinate
maps need not reflect dominance: T(x,y)=(2x+y,x+2y) takes incomparable
(0,3),(1,0) to (3,6),(2,1), where the second dominates the first. Candidate-dependent rescaling, dropping cost
coordinates, changed acquisition charges, missing competitors and different
uncertainty support do not generally satisfy the premise. QED.

Native wall/process time and virtual-machine instruction counts are different
measurands unless a justified mapping establishes the stated relations.
Disagreement can expose changed premises, uncertainty or model error; it is
not automatically a GMI contradiction. Conversely interval underidentification
is not measured coexistence. Observed repetition envelopes carry no confidence
level or population coverage guarantee without an additional sampling model.

For the frozen parity candidates with exact opcode costs 88,136,312,472,
the 88-opcode XOR candidate necessarily survives every timing realization.
A neural-only frontier is therefore impossible under this three-coordinate
register and cannot serve as its prospective timing falsifier. Neural
coexistence remains testable: it requires a timing advantage sufficient to
avoid domination in at least one other coordinate, judged with EFI-1--3.
An actual falsifier must be feasible under the frozen apparatus assumptions.

## 6. Evidence, chronology and remaining empirical work

The companion checker compares endpoint membership and ordered partitions
with independent direct world enumeration, including ties, correlations,
unknown coexistence, forced survival and transport-breaking controls.
GRAND_GMI_EMPIRICAL_FRONTIER_IDENTIFICATION_RECEIPT_V1.json records the finite
censuses. They verify implementation; EFI-1--4 supply the mathematical proofs.
No measured timing, neural advantage or whole-lifecycle gain is asserted.

PR530_SCIENTIFIC_REVIEW_88729748_V1.md pins the motivating PR and remaining
B6 scoring repairs, including exact chronology. A registration after data
exist may be outcome-blind if supported independently; it is not pre-data
merely because its author had not inspected an artifact. An authenticated
earlier specification or a fresh future run is needed for that designation.
Fixing the inference does not retroactively change frozen measurements.
