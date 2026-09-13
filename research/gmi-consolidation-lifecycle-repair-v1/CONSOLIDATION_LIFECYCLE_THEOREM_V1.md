# Consolidation with preservation and lifetime charges — CLR-1–4

Status: exact finite parent specialization and correction; not a new
automata minimization or amortization method. All sets below are finite and
nonempty; transitions are deterministic, total and explicitly supplied.

## 1. Parent scope before the mechanism

[CSR-1–5](raw/parents/CONTINUAL_SEMANTIC_RETENTION_THEOREM_V1.md) already
proves exact retained-response width, replay's joint-channel requirement and
update-induced forgetting. The
[developmental quotient parent](raw/parents/DEVELOPMENTAL_QUOTIENT_THEOREM_V1.md)
instead minimizes all admitted future traces. Its own teaching example
separates these two equivalences. Classical
[finite-state minimization](https://courses.cs.cornell.edu/cs4120/2023sp/notes/leximpl/index.html)
supplies the future-distinguishability argument. We adapt that argument to
finite outputs and an observable current label, not a new theorem.

[PVR-2–4](raw/parents/PROOF_SEARCH_VERIFICATION_REUSE_THEOREM_V1.md) already
requires certified transport and paid setup/reuse.
[CRI-1–3](raw/parents/CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md) supplies
stronger acquisition/repair/abandon policy comparisons under its stated graph.
The [aggregate method](https://www.cs.cornell.edu/courses/cs3110/2014sp/lectures/22/amortized-analysis.html)
charges the entire operation sequence. CLR-4 is a direct finite application,
not an optimizer or an improvement on those parents.

## 2. CLR-1 — fixed retention is a state-width question

Fix histories H and binary obligations Q_1,...,Q_t. Write
Sigma_t(h)=(Q_1(h),...,Q_t(h)), N_t=|Sigma_t(H)|.
With only a freely designable persistent symbol and the query identity at
the decoder, the exact minimum is N_t symbols or ceil(log2 N_t) fixed bits.

Distinct signatures cannot collide; assigning each signature its own symbol
attains the bound. Appending obligations refines the partition, so N cannot
decrease. Equal successive N means the new answer is a function of the old
signature, at this fixed history/obligation scope. It means no extra
retained width, not free computation, updating, construction or storage work.

The original binary fixture compares one bit per task without sharing:
A independent: N=2,4,8,16; B redundant: N=2,4,4,4,4;
C mixed: N=2,4,4,4,8,8. Final savings are exactly0,3,3 bits.
For nonbinary tasks the separate-storage comparator must change accordingly.
These are semantic encodings; arbitrary physical implementability is absent.

## 3. CLR-2 — constructive preservation for every admitted future event

Supply S, event set A, current label q:S→Y, transition d:S×A→S
and emitted label o:S×A→O. Events include all admitted teaching/query actions.
Only the declared observable projection q/o is preserved; internal details
outside it are irrelevant. This exact preservation criterion is sufficient
for those obligations, not necessary for every adequate implementation under
an error tolerance, relational answer choice or deliberate lossy forgetting.
All S are possible starting states; otherwise restrict to the declared
closed reachable subset. Protected resource receipts may be components of
q/o if exact equality of those receipts is required.

An encoding e:S→Z admits a stepwise exact quotient whose state stays e(s)
if and only if, whenever e(s)=e(t), for every a:
q(s)=q(t), o(s,a)=o(t,a), and e(d(s,a))=e(d(t,a)).

Necessity: a deterministic quotient sees the same encoded state/action and
must emit the same labels and next encoded state. Sufficiency: define each
quotient label and transition from any representative; the conditions make
them well-defined. Encode the actual initial state, then induction on word
length proves equality of all current labels, emitted labels and encoded
successors for every finite word. Construction/verification costs are real
work when this finite table method is actually used by an agent.

The weakest equivalence preserving all such future label traces is obtained
by repeatedly refining q-classes with (emitted label, successor class).
At a fixed point it satisfies the displayed criterion. Any trace-preserving
encoding refines every iteration by induction, so the resulting quotient is
minimal, up to renaming, for this supplied register and all possible starts.
An implementation may retain extra, observationally redundant states.
Unknown dynamics or an incomplete event alphabet do not satisfy coverage.

### Decisive future-teach control

States0,1 both currently answer0; states2,3 answer1. Query is a self-loop
emitting the current answer. Teach emits the same acknowledgement everywhere,
but sends0→2,1→1,2→2,3→3. Thus current width is2, future width is3:
teach/query returns1 from0 and0 from1. Merging0/1 fails the criterion.
The valid quotient {0},{1},{2,3} preserves every word, and supplies a
constructive revival without claiming the smaller static code was adequate.

This is precisely the distinction already present in the developmental
parent. Merely identifying its quotient size with N_t is invalid.

## 4. CLR-3 — sufficient capacity versus a preserving actual update

For one fixed retained signature q:S→Y, after a deterministic update U
with no other surviving information, exact retention from U(s) is possible
iff U(s)=U(t) implies q(s)=q(t). Define the decoder on each U-fiber.
Four available memory states do not help an update that sends all four
distinct retained classes to0. Identity preserves all four, and any
permutation plus its inverse decoder is an explicit preserving update.

This is CSR's existing irreversible-merge/injective-preservation result;
capacity is a possibility claim, not a guarantee about every update.
For continued development, additionally discharge CLR-2 for the full future
event register. A successful current decoder alone is insufficient.

Replay supplies a joint symbol (Z,R); exact retention requires that its
fibers refine q, hence |Z||R|>=N. Product size alone suffices only when
those channels are jointly designable, not for fixed colliding channels.
Raw data D by itself must have at least N distinguishable values if it is
the only exact information source. Cheaper storage in another substrate
requires its own meter, not a claim of fewer states under the same meter.

## 5. CLR-4 — a sufficient paid-benefit certificate

Compare two actual feasible, equally adequate implementations on the SAME
declared initial contexts and workload words. Their final states need not
share representations. Prove semantic preservation (e.g. CLR-2) separately
from quantitative work; if costs are required equal in the semantic trace,
a strict cost improvement is excluded by that chosen equivalence.

For every admitted workload w of length H, let full charged totals be
J_R=A_R+sum_i c_R,i+T_R and J_C=A_C+sum_i c_C,i+T_C.
These nonnegative scalar charges include every acquisition, minimization,
conversion, decoder, failed attempt, control, update, retrieval/replay,
holding, input movement and terminal operation actually used. Common past
charges cancel only if they really are identical. Conversion must preserve
the supplied state; an abstract encoding is not an already executed converter.

If uniformly A_C-A_R+T_C-T_R<=a and c_R,i-c_C,i>=d_i,
then J_C-J_R<=a-sum_i d_i. Thus sum_i d_i>a certifies strict benefit.
Sum the inequalities to prove it; no probability or independence is needed.
Exact known totals give an iff comparison J_C<J_R for these two policies.
Upper bounds for C below lower bounds for R give a sound interval certificate.
This is not a family optimum; a third feasible policy may dominate both.

A declared finite arithmetic example uses a redundant5-bit answer vector
versus its2-bit sufficient code. Conversion/check/setup cost7. Each serving
round charges raw query1+holding5 versus compact decode2+holding2.
A paid holding interval follows each query, including the final one; terminal
charges are0. For H=3: raw18, compact19 (loss1); H=4:24 versus23 (gain1).
At equal per-round costs, positive conversion cost never becomes free.
All are authored operation prices, not measured native timings or energies.
The converter and decoder are executed in the finite witness on all16 histories.

No optimal forgetting decision follows without the value/error objective
and the legal continuation graph. All-channel width insufficiency forbids
exact retention; choosing which obligations to relinquish is a new policy
problem. Existing CRI is the stronger matched parent when its graph applies.
