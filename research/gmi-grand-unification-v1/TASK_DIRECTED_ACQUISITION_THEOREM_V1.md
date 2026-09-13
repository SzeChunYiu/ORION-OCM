# Task-directed acquisition and retention theorem V1

Date: 2026-09-13. Status: finite exact theorem with constructive witnesses.

This module corrects the instrumental reading of EA-5 and composes acquisition
with SC-1 and ACL-3. EA-1--4 remain valid for their declared identification
obligation. Recovering every response profile can cost more than producing
one action that succeeds; the difference persists during experimentation.

## 1. Register and falsifying example

Let nonempty finite `W,A` be worlds and terminal actions, finite `X` be tests,
`O(w,x)` their deterministic outcomes, and nonempty `Gamma(w) subseteq A`
the successful terminal actions. Tests leave the world and terminal obligation
unchanged, are always legally available, and have finite exact nonnegative costs
`c(x)`. Outcomes and history are available throughout acquisition. Policies
must terminate and succeed for every world. Test, output and control tables
are admitted; this theorem measures experiment cost, not their execution cost.

Set `Gamma(w0)={a,b}`, `Gamma(w1)={a,c}` and give the worlds identical test
rows. Their complete action-success response profiles differ, so identifying
that response quotient is impossible. The constant action `a` nevertheless
succeeds without testing. If a unit-cost revealing test is added, quotient
identification costs one while adequate action still costs zero.

Thus EA-5's former equality with *task-sufficient* discovery was false for
relational obligations. Its equality for full protected-response identification
is retained. Experimental indistinguishability is fatal to action only when
it prevents one common successful action, not whenever response profiles differ.

## 2. Exact relational acquisition

For nonempty candidates `S`, put `C(S)=intersection_{w in S} Gamma(w)` and
`S_xy={w in S:O(w,x)=y}`. Let `Split(S)` contain tests having at least two
nonempty outcome cells on `S`. Define, with `min(empty)=infinity`,

`V(S)=0` if `C(S)` is nonempty; otherwise
`V(S)=min_{x in Split(S)} [c(x)+max_{y:S_xy nonempty} V(S_xy)]`.

**TDA-1.** `V(W)` is the attained minimum worst-case test cost of an adequate
adaptive policy, or infinity exactly when none exists.

Proof. If `C(S)` is nonempty, stopping with a common action is optimal because
costs are nonnegative. Otherwise a successful policy must test. A test with
one possible outcome can be deleted: it changes neither candidates, legal
future tests nor terminal obligation. This includes repeated and zero-cost
uninformative tests. After deleting them, every branch strictly reduces `S`.
Its first test costs `c(x)` and every possible child must be solved, which
bounds the policy below by the displayed expression. Conversely select a
minimizing test and minimizing child policies; these finitely many choices
exist by induction on `|S|`. Their concatenation attains that value. Every
reduced path has at most `|W|-1` tests, so no zero-cost cycle or limiting
unattained optimum enters this proof. QED.

**TDA-2.** Let `B` range over classes of identical full test rows. Then
`V(W)<infinity iff C(B) nonempty for every B`.

Proof. Two worlds in `B` give identical outcomes at every adaptively selected
test, by induction on their shared history, so a deterministic policy uses one
terminal action throughout `B`. This proves necessity. Testing all members of
`X` identifies `B`; choose a common action there to prove sufficiency. This is
finite, including `X=empty`. If empty action rows are allowed as intermediate
restrictions, the same proof declares the corresponding instance impossible.
A randomized zero-error policy with worst-case cost over its random choices
cannot improve the minimum: finitely many worlds allow one common random seed
on which all succeed and obey that cost, yielding a deterministic policy. QED.

When the obligation is exact identification, `Gamma(w)={sigma(w)}`, TDA-1
reduces to EA-1. If identifying a richer quotient permits a common action in
each quotient cell, then `V <= eta_sigma`, including infinity. Equality need
not hold. Full-response identification remains scientifically appropriate
when the scientific obligation explicitly demands those responses.

## 3. Cut lower bound and its missing converse

Let `H_Gamma` have hyperedges `B` with `C(B)=empty`. Every successful decision
tree partitions worlds into compatible leaves. Its leaf labels therefore
color `H_Gamma`, so its number of leaves is at least `chi(H_Gamma)`. With unit
cost and at most `b>=2` outcomes per test, depth is at least
`ceil(log_b chi(H_Gamma))`. This concerns depth, not arbitrary weighted cost.
For `b=1`, success is possible exactly when a common action already exists.

The bound can be strict: four worlds require distinct actions and the only
tests ask separately whether the world is `w0`, `w1` or `w2`. A sequence of
three negative answers identifies `w3`, so optimal depth is three, whereas
`ceil(log2 4)=2`. Legal tests restrict which compatible partitions can be
realized. A coloring alone supplies no experimental decision tree.

The three sets `{a,b}`, `{b,c}`, `{a,c}` also retain the higher-order conflict:
all pairs are compatible, but a constant experiment row cannot support any
adequate policy. Pairwise discrimination tests alone miss this obstruction.

## 4. Exact acquisition-to-retention bridge

Now erase every acquisition observation before the terminal decision. The
only remaining world-dependent carrier is one classical persistent message
`z in {1,...,m}`; terminal output is `d(z)`, with no side information, timing
signal or later tests. Acquisition may use admitted transient workspace.
Its workspace, controller, encoding and terminal-action costs remain separate
coordinates in the complete physical profile; `m` measures this later cut only.

For an action subset `D subseteq A`, run TDA-1 with successful sets
`Gamma_D(w)=Gamma(w) intersect D` and write its value as `V_D`.

**TDA-3.** Fix a finite nonnegative allowance `q` and an integer `m>=1`.
Infinity denotes impossibility and is never an admitted resource allowance.
An adequate policy with worst-case experiment cost at most `q` and
at most `m` retained symbols exists iff

`min_{D subseteq A, |D|<=m} V_D(W) <= q`.

Proof. An `m`-symbol decoder can emit only actions in `D=im(d)`, with
`|D|<=m`. Every world must therefore reach an acquisition leaf whose output
belongs to `Gamma_D(w)`. TDA-1 bounds its acquisition cost below by `V_D`.
Conversely an optimal `D`-restricted tree has a successful action in `D` at
each leaf. Encode that action's index, retain it and decode it after erasure.
This realizes both bounds under the stated admitted-table contract. QED.

Equivalently, for a fixed acquisition tree with world cell `L` at each leaf,
apply SC-1 to leaf action sets `C(L)`. Their conflict-hypergraph chromatic
number is its minimum retained alphabet. A leaf with empty `C(L)` makes the
tree inadequate. Optimizing the tree and this cut jointly yields the full
attained finite experiment/retention frontier. Independently minimizing test
cost and memory need not produce a jointly achievable pair.

## 5. A strict acquisition/retention frontier

Take six worlds `(i,b)`, `i in {0,1,2}`, `b in {0,1}`, actions
`{a0,a1,a2,d0,d1}` and `Gamma(i,b)={ai,db}`. Every test costs one:

| Test | Outcome in world `(i,b)` |
|---|---|
| `q` | `i` |
| `r_j`, for each `j=0,1,2` | `1` iff `i=j` and `b=1`, otherwise `0` |

Only `q` permits a one-test adequate policy: after `q=i`, the two possible
worlds have common action `ai`. Hence every such policy needs three retained
symbols. Each `r_j=0` cell contains both `b` values at two different indices,
whose four action sets have empty intersection; no `r_j` alone suffices.

After `q=i`, ask `r_i` and emit `db`. Two tests now need only two retained
symbols. One symbol is impossible regardless of testing because all six action
sets have empty intersection. Zero tests are likewise impossible. Therefore
all adequate points are weakly dominated by one of the two attained points,
and the exact frontier is `{(1,3),(2,2)}` in `(test depth, retained symbols)`.
The pair of separate minima `(1,2)` is infeasible. Stopping at the first
compatible leaf can sacrifice a later memory improvement.

## 6. Strongest parents and applicability

[Javdani et al., AISTATS 2014, sections 2--3](https://publications.ri.cmu.edu/storage/publications/pub_files/2014/4/javdani14hec_extended.pdf)
already formulate overlapping decision regions and hyperedge removal for
successful decisions. Their expected-cost greedy guarantees use their stated
Bayesian/adaptive-submodularity conditions. They are not transported to this
worst-case recurrence without a separate proof.
[Chen et al., UAI 2017, section 2](https://www.auai.org/uai2017/proceedings/papers/83.pdf)
explicitly register both expected and worst-case decision-region cost. The
mapping is exact: their successful region `R_a` is `{w:a in Gamma(w)}`, and
`S subseteq R_a` is equivalent to `a in C(S)`. Relational acquisition,
hypergraph compatibility and Bellman optimization are established parents.

The contribution here is repair and composition within GMI: transport the
existing SC-1 adequacy distinction through experimentation and then through a
separately declared retention cut. No novelty is claimed for those parents.

State-changing, unsafe or availability-changing tests require a controlled
state/history register; `S` alone need not be sufficient. Stochastic errors,
unknown outcome tables, deployment cost, bounded acquisition workspace and
physical realization require additional models. This module does not discharge
those obligations or establish universal completion.

## 7. Finite falsification

`grand_gmi_task_directed_acquisition_checks_v1.py` compares the recurrence with
complete bounded policy tables executed world by world, including zero and
unequal test costs. It checks full test-row compatibility independently and
compares the memory bridge against actual distinct decoder actions: 87,808
acquisition instances and 263,424 retained-capacity comparisons all agree. The
six-world frontier and the unidentifiable-but-actionable, triple-conflict and
restricted-test witnesses remain explicit controls. The frozen receipt is
`GRAND_GMI_TASK_DIRECTED_ACQUISITION_RECEIPT_V1.json`; finite agreement is
regression evidence for the proofs above, not an unrestricted solver.
