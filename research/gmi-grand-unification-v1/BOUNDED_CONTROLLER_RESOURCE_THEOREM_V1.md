# Bounded controller state and represented resources — BCR-1–4

Date: 2026-09-13. Status: exact finite synthesis and scoped resource separation.

## 1. Strongest parents and the remaining GMI bridge

[Meuleau et al. (UAI 1999), §§2.2–2.3](https://www.cassandra.org/arc/papers/uai99.pdf)
defines action-labelled finite policy nodes, observation-labelled edges, and the
controller × physical-state product. We specialize to deterministic execution
and require legal, successful finite termination instead of discounted reward.
[Hu and De Giacomo (ICAPS 2013), pp.110–112](https://www.diag.uniroma1.it/degiacom/papers/2013/ICAPS13.pdf)
gives bounded synthesis, repeated product-configuration rejection, and a sound,
complete search. Our Moore action-first timing differs from their Mealy timing.
[Gerstacker, Klein and Finkbeiner (2018), §§1–2](https://finkbeiner.groups.cispa.de/publications/FKG18.pdf)
distinguishes finite-state graph size from represented program syntax size.

These mechanisms are inherited. The bridge is a finite, explicit implementation
register for [CRA](CONTROLLED_RELATIONAL_ACQUISITION_THEOREM_V1.md): feasibility
of a belief policy does not certify its controller state, stored program, or
model input costs. [TDA](TASK_DIRECTED_ACQUISITION_THEOREM_V1.md)'s retained-action
cut also does not charge all those objects. No new bounded-synthesis result or
lower bound over all programming languages or physical machines is claimed.

## 2. Exact plant, controller and representation registers

Let S be a finite nonempty set of complete configurations, ∅≠I⊆S the admitted
initial states, U finite controls, O nonempty observations, and A nonempty
terminal actions. T:S×U⇀S×O is deterministic; undefined means illegal.
Γ(s)⊆A lists successful terminal actions and may be empty. Complete state must
include obligation-relevant history flags; Γ is fixed for each complete state.

A j-node Moore controller, j≥1, has labelled nodes {0,...,j−1}, initially 0.
Each row is either terminal a∈A or control u∈U with total successor map δ:O→[j].
At (s,q), a terminal row halts successfully iff a∈Γ(s); otherwise it fails.
A control row requires T(s,u)=(s′,o) and moves to (s′,δ(o)); illegality fails.
The node includes the instruction pointer and terminal locations. No initial
world oracle, external clock, cached observation, or additional mutable memory
is admitted. Environment-goal attainment does not automatically stop execution.

Fix n=|S|, u=|U|, o=|O|, a=|A| and public dimension/alphabet registers. Put
b_j=ceil(log2 j), k=ceil(log2(a+u)). Encode each controller row with a k-bit
opcode and o fields of b_j successor bits, padding terminal successors with
zeros. Reject invalid labels and nonzero terminal padding. Then exact payload

    B_C(j)=j(k+o·b_j),        live node storage=b_j.

All allocated rows, including unreachable ones, are charged. This is a specific
injective binary representation, not an optimal compression theorem.

Encode each physical (s,u) entry as 0=illegal or 1+o·s′+observation_index.
Append n·a success-mask bits and n initial-membership bits. Exact model payload

    B_M=n·u·ceil(log2(no+1))+n·a+n.

This is synthesis/verification input. Deployment need not retain it; retaining
it requires an additional online resident-model charge. Fixed dimension headers,
interpreter and interface implementations are outside these payload formulas.

## 3. BCR-1 — exact verification by product execution

A fixed controller succeeds for every s∈I iff every run reaches a successful
terminal before any illegal action, wrong terminal or repeated pair (s,q).
For n physical states and j nodes, a successful run uses at most n·j−1 controls.

**Proof.** From a nonterminal pair the legal next pair is uniquely determined.
A repeated pair repeats its whole deterministic future forever. Conversely,
a run that neither halts nor fails has to repeat among n·j pairs. A successful
run cannot repeat and includes its terminal pair, leaving at most n·j−1 control
steps. Universal success requires this property separately for every initial
state. Tracking only controller-node repetition would discard physical progress.
This is strong finite termination; fairness and probability-one are not premises.

## 4. BCR-2 — exact bounded synthesis and achievable profiles

There are exactly (a+u·j^o)^j labelled j-node controllers. Enumerating j=1,...,r
for finite integer r≥1 and applying BCR-1 decides feasibility with at most r
nodes and constructs every admitted successful controller. Terminal rows have
a choices; each control row has u·j^o choices; all rows are chosen independently.
The same row must be used across all physical states and initial runs.

For a successful controller with worst run length t, use the exact table-machine
profile ρ(C)=(b_j,B_C,B_M,t,2t+1). The final coordinate counts one opcode read
per visited node and one successor-field read per executed control. Controls
have unit abstract action cost. Operations are atomic table accesses, not CPU
instructions. Empty-width constant fields still have a read operation.

Enumerate complete profiles and retain those meeting finite nonnegative integer
coordinate ceilings. Do not independently minimize coordinates and assume their
combination attainable. Every surviving profile has its concrete controller.
The finite nonempty set has an attained Pareto frontier, as in
[MSC-2](CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md); an empty set establishes
only infeasibility within this register. Infinity is never a feasible allowance.

The receipt separately records development work: candidates evaluated, initial
runs, distinct product-pair inspections and physical-transition lookups. These
are exact operation categories for the specified exhaustive search, not total
wall time or total instructions; parsing, allocation and serialization are not
included. Full search work is paid once for the returned register, not hidden in
a per-deployment action count. A concrete implementation must add its actual
headers/interpreter/interface bytes, transient storage, remaining development
work and platform costs before claiming end-to-end physical feasibility.

## 5. BCR-3 — zero retained-action bits, positive controller/program cost

Blind chain: S={s0,s1,s2}, I={s0}, U={tick}, O={blank}, A={stop}.
T(s0,tick)=(s1,blank), T(s1,tick)=(s2,blank); tick is illegal at s2.
Γ(s2)={stop}; Γ(s0)=Γ(s1)=∅. CRA's belief policy tick,tick,stop succeeds.
A retained-action cut immediately before the terminal choice needs one symbol
(stop), hence zero information bits; readiness/control state is not supplied by
this cut measure. Nevertheless a successful controller needs at least three nodes.

**Proof and revival.** Every successful run has exactly two ticks then stop.
Under a single observation the controller-node sequence is independent of the
physical state. If a node repeats before its terminal, its future repeats, so
it never reaches that terminal. Thus all three visited nodes must differ. Three
nodes q0=tick→q1, q1=tick→q2, q2=stop suffice. This yields ρ=(2,9,12,2,5).
The actual payloads are controller `101110000` and model `101100001001` under
the public ordering s0,s1,s2; stop=0,tick=1. An 8-bit program-payload ceiling
rejects every successful controller with j≤3 even when its live 2-bit register
is available. Thus stored program and live-state allowances are both enforced.

A blind length-L chain analogously needs exactly L+1 Moore nodes despite zero
terminal-action bits. L=2 is the smallest such chain exceeding two nodes.
This is not a claim of minimality over other controller or stopping conventions.

## 6. BCR-4 — feedback revival and hidden-state consistency controls

Change only the final tick's observation to done. A two-node controller now
works: q0=tick with δ(blank)=q0, δ(done)=q1; q1=stop. Its profile is
(1,6,15,2,5). Physical progress makes repeating q0 harmless: (s,q0) differs.
The larger observation alphabet and model payload are charged; the apparatus
has changed. This is a positive control against rejecting every controller loop.

For a hidden-state negative, use S={s0,s1}, I=S, tick:s0→s1 and tick illegal
at s1, with only stop at s1 successful. Any initial row is either stop, failing
s0, or tick, illegal at s1. Thus no controller of any size succeeds. Each known
initial state separately has a controller. Allowing rows to depend on hidden
physical state therefore produces a false positive; product-state verification
does not authorize fully observed product-state action selection.

## 7. Decisive executable witness

`grand_gmi_bounded_controller_model_v1.py` implements actual binary encodings,
controller enumeration and forward product traces. The separate checker uses
backward reachability from successful terminals over the full fixed-controller
product graph, without forward traces, repetition tests or an imposed horizon.

The exhaustive oracle covers every two-state, one-control, one-observation,
one-terminal-action plant: 9 partial transition tables ×4 success masks ×3
nonempty initial sets =108 models. For each, all 2 one-node and 9 two-node
controllers give 1,188 comparisons: 210 succeed and 978 fail; both oracles agree.
Actual controller/model payloads round-trip in all cases. Blind synthesis checks
all 11 controllers through two nodes (none succeed), then all 75 through three
(two succeed). The latter inspects 176 distinct product pairs across initial
runs and performs 145 physical-transition lookups; these are development costs.

Twelve focused tests include exact code bytes, every resource coordinate, blind
lengths 1–3, feedback revival, hidden-state consistency, all failure modes,
malformed labels, empty initial sets and nonfinite allowances. The receipt is
`GRAND_GMI_BOUNDED_CONTROLLER_RECEIPT_V1.json`. This finite register does not
close stochastic control, arbitrary code representation or empirical deployment.
