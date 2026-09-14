# CAR-1–4: a sufficient acquisition-and-mediation certificate

## 1. CAR-1 — separate success, capital, and acquisition advantage
Fix a deterministic admitted machine, complete initial state, observation
interface, verifier, finite task register, search policies and nonnegative
additive event prices. A result is solved only if a returned executable program
passes the declared verifier; exhausted search is not a successful acquisition.
Every success and failed candidate remains in the trace.

Let H be a state actually obtained from prior experience; let RESET have the
same machine and current task data but start with an empty library. A separate
matched gate arm disables prior entries as search instructions while the common
admission checker retains the same backing-state/newness access.
Acquisition of a new m must end with m stored and independently verified.
Require m's declared response distinct from the initially available primitives
and stored entries; this excludes direct recall of the target program.

A sufficient *local K1-use* certificate compares identical post-acquisition states
under enabled-m, disabled-m, sham and restored-m gates. Gates preserve typing and
all other causal state. On a distinct later obligation, enabled-m reaches a
verified solution earlier/cheaper, its trace actually executes m before success,
and sham/restored repeat enabled behavior. Such an exact intervention identifies
m's contribution for this machine, task and policy. It is not a claim that all
future tasks need m, that no other solver is better, or that historical
observations alone identify causal effects.

If both H and RESET acquire such a new m under the same task/verifier and
B_H(acquisition+verification+admission) < B_RESET(...), the point-mass experiment
satisfies the original *conditional new-capital acquisition* inequality.
Proof: the intervention supplies the missing later-use premise; verified storage
supplies acquisition; the observed exact inequality is its deterministic
expectation. The historical population protocol remains a separate obligation.

## 2. CAR-2 — candidate rank does not imply the certificate
For alphabet A, length-first search, first solved length L and one-based rank r
within that level, candidate cost is exactly
  sum(|A|^l for 1 <= l < L) + r.
Counting preceding levels and the successful prefix proves the equality.
A shorter word can still be found later after alphabet growth; an equally long
word can be found earlier when retained macros change the first-hit order.

The original primitives are inc, dec, double, square. Retain orig's two exact
functions but rename p1=(inc,double) to a; retain p2=(dec,square).
For target 2x+1 on probes0..3 both minimal nonempty lengths are2.
RESET's first hit (double,inc) is candidate11; H's (a,dec) is candidate8.
Thus description shortening is not a general necessary condition for acceleration.
This does not change the four frozen names/caps or their reported1,707 cases.
Nor does a first-hit rank gain prove m was retained or ever useful later.

## 3. CAR-3 — holding and history can reverse a conditional advantage
Write F for paid history construction, A_H/A_0 for current capital acquisition,
and U_H/U_0 for a fixed future workload including admission/holding/retrieval.
The lifecycle advantage from empty state is exactly
  (A_0+U_0) - (F+A_H+U_H).
Conditional acquisition advantage A_H<A_0 is insufficient if F or future costs
exceed the savings. This is additive accounting, not a new amortization law.
All costs of a sampled diagnostic experiment must also be reported; they do
not disappear because they are excluded from a conditional estimand.

## 4. CAR-4 — positive construction and inherited-parent boundary
The protocol searches x+2 from {double,inc}, stores its discovered primitive
body as h, searches x+4 with/without h and stores the returned flattened m.
The later target x+5 differs from both acquisitions. The executable assay,
including legal gates and all primitive descendants, decides its exact costs.

A same-library library-priority parent is generated independently by recursive
word traversal. Its candidate schedule matches the length/product schedule by
induction on word length: both visit every ordered tuple once in lexicographic
order. Equal event semantics then give equal solutions and costs.
Consequently an earned local mediation/acquisition positive is parent-sufficient.
The construction does not upgrade #323, establish broad K2, recover a prospective
registration, prove optimality over arbitrary solvers, or show physical savings.
